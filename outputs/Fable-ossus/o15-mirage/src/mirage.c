// Ossus O15 mirage (Claude, 18 Oct 2026): a d3d9.dll proxy that chains DXVK and bends the scene behind the Ossus
// ghostfire lightsaber blade like heat haze. See ../DESIGN.md.
//
// The client's graphics plugin (gl07_r.dll) imports only Direct3DCreate9 from d3d9.dll. This DLL takes that name,
// loads the real d3d9 (dxvk_d3d9.dll beside it, else the system one) and patches a few slots of the device vtable.
// A draw is a ghostfire blade draw when the bound pixel program is a lightsaber blade program (blade_ids.h) and its
// texture factor c3 is dark (brightest channel 0.17 or less, the O14 shader's own rule). Before each such draw:
//   1. replay it into a screen-sized mask (our pixel program, the game's vertices, viewport and depth test),
//   2. copy the scene drawn so far,
//   3. redraw that copy through the mask, bent by scrolling noise (one screen quad; texcoords are screen positions).
// Then the game's state goes back and the blade draws on top as usual. Every other call passes straight through.

#define CINTERFACE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "blade_ids.h"
#include "mask_ps.h"   // g_mask_ps_code (fxc /Fh from mask_ps.hlsl)
#include "haze_ps.h"   // g_haze_ps_code (fxc /Fh from haze_ps.hlsl)

// ---- settings (mirage.ini beside the DLL, section [mirage]; MIRAGE_INI overrides the path) ----

static struct {
	int enabled;          // 0: load DXVK and hook nothing
	int toggle_key;       // virtual key that switches the mirage on and off in game (0: none)
	int toggle_mods;      // 1 Ctrl, 2 Shift, 4 Alt
	int max_per_frame;    // mirage passes per frame at most (each is two screen-sized passes)
	int log_shaders;      // 1: log the id of every pixel program the game creates
	int allow_native;     // 1: hook the system d3d9 too (no DXVK); the haze pass drew nothing there (DESIGN.md)
	int debug_view;       // 1: paint the mask red (green/blue: the two noise layers) instead of bending; 2: everywhere
	float strength;       // bend at full mask, pixels
	float spread;         // mask widening, pixels
	float speed;          // noise scroll per second (screen heights / tiles)
	float chroma;         // colour split along the bend, 0-1
	float mask_gain;      // blade texture to mask
	float noise_tiles;    // noise tiles per screen height
	float max_bright;     // c3 brightest channel at or below this = ghostfire
	unsigned int extra_ids[8];
	int extra_count;
} cfg;

static char g_dir[MAX_PATH];
static FILE *g_log;
static int g_log_lines;

static void logf_(const char *fmt, ...)
{
	va_list ap;
	SYSTEMTIME st;
	if (!g_log || g_log_lines >= 4000)
		return;
	GetLocalTime(&st);
	fprintf(g_log, "%d:%02d:%02d.%03d %s  ", st.wHour % 12 ? st.wHour % 12 : 12, st.wMinute, st.wSecond,
	        st.wMilliseconds, st.wHour < 12 ? "AM" : "PM");
	va_start(ap, fmt);
	vfprintf(g_log, fmt, ap);
	va_end(ap);
	fputc('\n', g_log);
	if (++g_log_lines == 4000)
		fputs("(log full)\n", g_log);
	fflush(g_log);
}

static const char *ini_str(const char *ini, const char *key, const char *def, char *buf, int size)
{
	GetPrivateProfileStringA("mirage", key, def, buf, size, ini);
	return buf;
}

static int ini_int(const char *ini, const char *key, int def)
{
	char buf[64], d[32];
	sprintf(d, "%d", def);
	return (int)strtol(ini_str(ini, key, d, buf, sizeof buf), NULL, 0);
}

static float ini_float(const char *ini, const char *key, float def)
{
	char buf[64], d[32];
	sprintf(d, "%g", def);
	return (float)atof(ini_str(ini, key, d, buf, sizeof buf));
}

static void load_config(void)
{
	char ini[MAX_PATH], buf[256], *p, *end;
	DWORD n = GetEnvironmentVariableA("MIRAGE_INI", ini, MAX_PATH);
	if (n == 0 || n >= MAX_PATH)
		_snprintf(ini, MAX_PATH, "%s\\mirage.ini", g_dir);
	cfg.enabled = ini_int(ini, "enabled", 1);
	cfg.toggle_key = ini_int(ini, "toggle_key", 0x4D);   // M
	cfg.toggle_mods = ini_int(ini, "toggle_mods", 3);    // Ctrl+Shift
	cfg.max_per_frame = ini_int(ini, "max_per_frame", 8);
	cfg.log_shaders = ini_int(ini, "log_shaders", 0);
	cfg.debug_view = ini_int(ini, "debug_view", 0);
	cfg.allow_native = ini_int(ini, "allow_native", 0);
	cfg.strength = ini_float(ini, "strength", 6.0f);
	cfg.spread = ini_float(ini, "spread", 6.0f);
	cfg.speed = ini_float(ini, "speed", 0.35f);
	cfg.chroma = ini_float(ini, "chroma", 0.35f);
	cfg.mask_gain = ini_float(ini, "mask_gain", 2.0f);
	cfg.noise_tiles = ini_float(ini, "noise_tiles", 6.0f);
	cfg.max_bright = ini_float(ini, "max_bright", 0.17f);
	ini_str(ini, "extra_ids", "", buf, sizeof buf);
	for (p = buf; *p && cfg.extra_count < 8; p = end) {
		unsigned long id = strtoul(p, &end, 16);
		if (end == p) {
			end = p + 1;
			continue;
		}
		cfg.extra_ids[cfg.extra_count++] = (unsigned int)id;
	}
	logf_("settings from %s: enabled %d, toggle key 0x%02x mods %d, strength %.1f px, spread %.1f px, speed %.2f, "
	      "chroma %.2f, mask gain %.2f, noise tiles %.1f, ghostfire at brightest <= %.3f, %d per frame, %d extra ids",
	      ini, cfg.enabled, cfg.toggle_key, cfg.toggle_mods, cfg.strength, cfg.spread, cfg.speed, cfg.chroma,
	      cfg.mask_gain, cfg.noise_tiles, cfg.max_bright, cfg.max_per_frame, cfg.extra_count);
}

// ---- the real d3d9 ----

static HMODULE g_real;
static int g_native;   // the real d3d9 is the system one, not DXVK

static HMODULE real_dll(void)
{
	char path[MAX_PATH];
	UINT n;
	if (g_real)
		return g_real;
	_snprintf(path, MAX_PATH, "%s\\dxvk_d3d9.dll", g_dir);
	g_real = LoadLibraryA(path);
	if (g_real) {
		logf_("loaded %s", path);
		return g_real;
	}
	n = GetSystemDirectoryA(path, MAX_PATH);
	if (n && n < MAX_PATH - 12) {
		lstrcatA(path, "\\d3d9.dll");
		g_real = LoadLibraryA(path);
		g_native = g_real != NULL;
	}
	logf_(g_real ? "no dxvk_d3d9.dll beside this DLL; loaded %s" : "no real d3d9 found (tried dxvk_d3d9.dll and %s)",
	      path);
	return g_real;
}

static FARPROC real_proc(const char *name)
{
	HMODULE m = real_dll();
	return m ? GetProcAddress(m, name) : NULL;
}

// ---- state ----

static IDirect3D9Vtbl R9;        // the real IDirect3D9 methods
static IDirect3DDevice9Vtbl R;   // the real device methods
static IDirect3DDevice9 *g_dev;

static IDirect3DPixelShader9 *g_blade_ps[16];
static int g_blade_n;

static int g_on = 1, g_broken, g_busy, g_first_done;
static LONGLONG g_qpf, g_t0, g_frame_t, g_stat_t;
static unsigned int g_frames, g_frame_mirages, g_stat_match, g_stat_done, g_stat_capped;
static unsigned int g_stat_bind, g_stat_blade, g_blade_logged;   // diagnostics: blade program binds and draws
static float g_stat_bmin = 9.0f, g_stat_bmax = -1.0f;            // brightest c3 channel seen on blade draws

static IDirect3DPixelShader9 *g_mask_ps, *g_haze_ps;
static IDirect3DTexture9 *g_noise;
static IDirect3DTexture9 *g_scene_tex, *g_mask_tex;
static IDirect3DSurface9 *g_scene_surf, *g_mask_surf, *g_mask_rt;
static IDirect3DStateBlock9 *g_sb;
static UINT g_w, g_h;
static D3DFORMAT g_fmt;
static D3DMULTISAMPLE_TYPE g_ms;
static DWORD g_msq;

#define RELEASE(p) do { if (p) { (p)->lpVtbl->Release(p); (p) = NULL; } } while (0)

// D3DPOOL_DEFAULT objects and the state block: Reset fails while any of them is alive.
static void release_default(void)
{
	RELEASE(g_sb);
	RELEASE(g_mask_rt);
	RELEASE(g_mask_surf);
	RELEASE(g_mask_tex);
	RELEASE(g_scene_surf);
	RELEASE(g_scene_tex);
	g_w = g_h = 0;
}

static void release_all(void)
{
	release_default();
	RELEASE(g_noise);
	RELEASE(g_haze_ps);
	RELEASE(g_mask_ps);
}

// ---- pixel program ids (blade_ids.py takes the same sum) ----

static unsigned int fnv(unsigned int h, DWORD tok)
{
	int i;
	for (i = 0; i < 4; i++, tok >>= 8)
		h = (h ^ (tok & 0xFF)) * 0x01000193u;
	return h;
}

static unsigned int shader_id(const DWORD *t)
{
	unsigned int h = fnv(0x811C9DC5u, t[0]);
	DWORD i = 1, k, n;
	while (i < 65536) {
		DWORD tok = t[i];
		if ((tok & 0xFFFF) == 0xFFFE) {
			i += 1 + ((tok >> 16) & 0x7FFF);
			continue;
		}
		if (tok == 0x0000FFFF)
			return fnv(h, tok);
		n = (tok >> 24) & 0xF;
		for (k = i; k <= i + n; k++)
			h = fnv(h, t[k]);
		i += 1 + n;
	}
	return h;
}

static int is_blade_id(unsigned int id)
{
	int i;
	for (i = 0; i < BLADE_ID_COUNT; i++)
		if (BLADE_IDS[i] == id)
			return 1;
	for (i = 0; i < cfg.extra_count; i++)
		if (cfg.extra_ids[i] == id)
			return 1;
	return 0;
}

static int is_blade_ps(IDirect3DPixelShader9 *ps)
{
	int i;
	for (i = 0; ps && i < g_blade_n; i++)
		if (g_blade_ps[i] == ps)
			return 1;
	return 0;
}

// ---- our resources ----

static float lattice(int ch, int x, int y, int n)
{
	unsigned int h = (unsigned int)(ch * 7919 + n * 104729) ^ ((unsigned int)(x & (n - 1)) * 73856093u) ^
	                 ((unsigned int)(y & (n - 1)) * 19349663u);
	h = (h ^ (h >> 13)) * 1274126177u;
	return (float)((h ^ (h >> 16)) & 0xFFFF) / 65535.0f;
}

// smooth value noise on an n x n lattice that tiles over the 64 x 64 texture
static float value_noise(int ch, int x, int y, int n)
{
	float fx = x * n / 64.0f, fy = y * n / 64.0f;
	int ix = (int)fx, iy = (int)fy;
	float u = fx - ix, v = fy - iy, a, b;
	u = u * u * (3 - 2 * u);
	v = v * v * (3 - 2 * v);
	a = lattice(ch, ix, iy, n) + (lattice(ch, ix + 1, iy, n) - lattice(ch, ix, iy, n)) * u;
	b = lattice(ch, ix, iy + 1, n) + (lattice(ch, ix + 1, iy + 1, n) - lattice(ch, ix, iy + 1, n)) * u;
	return a + (b - a) * v;
}

static IDirect3DTexture9 *make_noise(IDirect3DDevice9 *d)
{
	IDirect3DTexture9 *tex = NULL;
	D3DLOCKED_RECT lr;
	int x, y, ch;
	if (FAILED(d->lpVtbl->CreateTexture(d, 64, 64, 1, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, &tex, NULL)))
		return NULL;
	if (FAILED(tex->lpVtbl->LockRect(tex, 0, &lr, NULL, 0))) {
		RELEASE(tex);
		return NULL;
	}
	for (y = 0; y < 64; y++) {
		BYTE *row = (BYTE *)lr.pBits + y * lr.Pitch;
		for (x = 0; x < 64; x++)
			for (ch = 0; ch < 4; ch++) {
				float v = 0.65f * value_noise(ch, x, y, 8) + 0.35f * value_noise(ch, x, y, 16);
				static const int byte_of[4] = { 2, 1, 0, 3 };   // r g b a in A8R8G8B8 memory order
				row[x * 4 + byte_of[ch]] = (BYTE)(v * 255.0f + 0.5f);
			}
	}
	tex->lpVtbl->UnlockRect(tex, 0);
	return tex;
}

static int ensure(IDirect3DDevice9 *d, const D3DSURFACE_DESC *rd)
{
	IDirect3DDevice9Vtbl *v = d->lpVtbl;
	HRESULT hr;
	if (!g_mask_ps && (FAILED(hr = R.CreatePixelShader(d, (const DWORD *)g_mask_ps_code, &g_mask_ps)) ||
	                   FAILED(hr = R.CreatePixelShader(d, (const DWORD *)g_haze_ps_code, &g_haze_ps)))) {
		logf_("could not create the mirage pixel programs (0x%08lx); mirage off", hr);
		g_broken = 1;
		return 0;
	}
	if (!g_noise && !(g_noise = make_noise(d))) {
		logf_("could not create the noise texture; mirage off");
		g_broken = 1;
		return 0;
	}
	if (g_sb && g_w == rd->Width && g_h == rd->Height && g_fmt == rd->Format && g_ms == rd->MultiSampleType &&
	    g_msq == rd->MultiSampleQuality)
		return 1;

	release_default();
	if (FAILED(hr = v->CreateTexture(d, rd->Width, rd->Height, 1, D3DUSAGE_RENDERTARGET, rd->Format, D3DPOOL_DEFAULT,
	                                 &g_scene_tex, NULL)) ||
	    FAILED(hr = g_scene_tex->lpVtbl->GetSurfaceLevel(g_scene_tex, 0, &g_scene_surf)) ||
	    FAILED(hr = v->CreateTexture(d, rd->Width, rd->Height, 1, D3DUSAGE_RENDERTARGET, D3DFMT_A8R8G8B8,
	                                 D3DPOOL_DEFAULT, &g_mask_tex, NULL)) ||
	    FAILED(hr = g_mask_tex->lpVtbl->GetSurfaceLevel(g_mask_tex, 0, &g_mask_surf)) ||
	    FAILED(hr = R.CreateStateBlock(d, D3DSBT_ALL, &g_sb)))
		goto fail;
	if (rd->MultiSampleType != D3DMULTISAMPLE_NONE) {
		// the game's depth buffer is multisampled too, so the mask draws multisampled and resolves into g_mask_tex
		if (FAILED(hr = v->CreateRenderTarget(d, rd->Width, rd->Height, D3DFMT_A8R8G8B8, rd->MultiSampleType,
		                                      rd->MultiSampleQuality, FALSE, &g_mask_rt, NULL)))
			goto fail;
	} else {
		g_mask_rt = g_mask_surf;
		g_mask_rt->lpVtbl->AddRef(g_mask_rt);
	}
	g_w = rd->Width;
	g_h = rd->Height;
	g_fmt = rd->Format;
	g_ms = rd->MultiSampleType;
	g_msq = rd->MultiSampleQuality;
	logf_("mirage targets made: %ux%u, format %d, multisample %d", g_w, g_h, (int)g_fmt, (int)g_ms);
	return 1;
fail:
	logf_("could not make the mirage targets for %ux%u format %d multisample %d (0x%08lx); mirage off",
	      rd->Width, rd->Height, (int)rd->Format, (int)rd->MultiSampleType, hr);
	release_default();
	g_broken = 1;
	return 0;
}

// ---- the mirage ----

typedef struct {
	int kind;   // 0 DrawPrimitive, 1 DrawIndexedPrimitive, 2 DrawPrimitiveUP, 3 DrawIndexedPrimitiveUP
	D3DPRIMITIVETYPE type;
	INT base;
	UINT a, b, c, d;
	const void *idx, *vtx;
	D3DFORMAT ifmt;
	UINT stride;
} Draw;

static HRESULT replay(IDirect3DDevice9 *d, const Draw *c)
{
	switch (c->kind) {
	case 0: return R.DrawPrimitive(d, c->type, c->a, c->b);
	case 1: return R.DrawIndexedPrimitive(d, c->type, c->base, c->a, c->b, c->c, c->d);
	case 2: return R.DrawPrimitiveUP(d, c->type, c->a, c->vtx, c->stride);
	default: return R.DrawIndexedPrimitiveUP(d, c->type, c->a, c->b, c->c, c->idx, c->ifmt, c->vtx, c->stride);
	}
}

// log each failing step once (the steps below never stop the game's draw)
static void step_failed(int step, HRESULT hr)
{
	static unsigned int logged;
	if (FAILED(hr) && !(logged & (1u << step))) {
		logged |= 1u << step;
		logf_("mirage step %d failed: 0x%08lx", step, hr);
	}
}
#define STEP(n, call) step_failed(n, (call))

static void run(IDirect3DDevice9 *d, const Draw *c, IDirect3DSurface9 *rt, const D3DSURFACE_DESC *rd, LONGLONG now)
{
	IDirect3DDevice9Vtbl *v = d->lpVtbl;
	D3DVIEWPORT9 vp;
	DWORD scissor;
	float k[12];
	float t = (float)fmod((double)(now - g_t0) / (double)g_qpf, 1000.0);
	float w = (float)rd->Width, h = (float)rd->Height;
	struct { float x, y, z, rhw, u, v; } q[4] = {
		{ -0.5f, -0.5f, 0.0f, 1.0f, 0.0f, 0.0f }, { w - 0.5f, -0.5f, 0.0f, 1.0f, 1.0f, 0.0f },
		{ -0.5f, h - 0.5f, 0.0f, 1.0f, 0.0f, 1.0f }, { w - 0.5f, h - 0.5f, 0.0f, 1.0f, 1.0f, 1.0f } };
	DWORD s;

	STEP(0, g_sb->lpVtbl->Capture(g_sb));
	v->GetViewport(d, &vp);
	v->GetRenderState(d, D3DRS_SCISSORTESTENABLE, &scissor);

	// 1. the blade's own draw into the mask: same vertices, viewport and depth test; our pixel program, MAX blend
	STEP(1, v->SetRenderTarget(d, 0, g_mask_rt));   // resets the viewport
	v->SetRenderState(d, D3DRS_SCISSORTESTENABLE, FALSE);
	STEP(2, v->Clear(d, 0, NULL, D3DCLEAR_TARGET, 0, 1.0f, 0));
	v->SetRenderState(d, D3DRS_SCISSORTESTENABLE, scissor);
	v->SetViewport(d, &vp);
	STEP(3, R.SetPixelShader(d, g_mask_ps));
	k[0] = cfg.mask_gain;
	k[1] = k[2] = k[3] = 0.0f;
	R.SetPixelShaderConstantF(d, 0, k, 1);
	v->SetRenderState(d, D3DRS_ALPHABLENDENABLE, TRUE);
	v->SetRenderState(d, D3DRS_SEPARATEALPHABLENDENABLE, FALSE);
	v->SetRenderState(d, D3DRS_BLENDOP, D3DBLENDOP_MAX);
	v->SetRenderState(d, D3DRS_SRCBLEND, D3DBLEND_ONE);
	v->SetRenderState(d, D3DRS_DESTBLEND, D3DBLEND_ONE);
	v->SetRenderState(d, D3DRS_ALPHATESTENABLE, FALSE);
	v->SetRenderState(d, D3DRS_FOGENABLE, FALSE);
	v->SetRenderState(d, D3DRS_ZWRITEENABLE, FALSE);
	v->SetRenderState(d, D3DRS_COLORWRITEENABLE, 0xF);
	v->SetRenderState(d, D3DRS_SRGBWRITEENABLE, FALSE);
	STEP(4, replay(d, c));
	if (g_mask_rt != g_mask_surf)
		STEP(5, v->StretchRect(d, g_mask_rt, NULL, g_mask_surf, NULL, D3DTEXF_NONE));

	// 2. the scene drawn so far
	STEP(6, v->StretchRect(d, rt, NULL, g_scene_surf, NULL, D3DTEXF_NONE));

	// 3. that copy, bent through the mask, back onto the game's target (colour only: alpha may carry bloom)
	STEP(7, v->SetRenderTarget(d, 0, rt));
	STEP(8, R.SetPixelShader(d, g_haze_ps));
	v->SetVertexShader(d, NULL);
	v->SetFVF(d, D3DFVF_XYZRHW | D3DFVF_TEX1);
	v->SetTexture(d, 0, (IDirect3DBaseTexture9 *)g_scene_tex);
	v->SetTexture(d, 1, (IDirect3DBaseTexture9 *)g_mask_tex);
	v->SetTexture(d, 2, (IDirect3DBaseTexture9 *)g_noise);
	for (s = 0; s < 3; s++) {
		DWORD wrap = s == 2 ? D3DTADDRESS_WRAP : D3DTADDRESS_CLAMP;
		v->SetSamplerState(d, s, D3DSAMP_ADDRESSU, wrap);
		v->SetSamplerState(d, s, D3DSAMP_ADDRESSV, wrap);
		v->SetSamplerState(d, s, D3DSAMP_MAGFILTER, D3DTEXF_LINEAR);
		v->SetSamplerState(d, s, D3DSAMP_MINFILTER, D3DTEXF_LINEAR);
		v->SetSamplerState(d, s, D3DSAMP_MIPFILTER, D3DTEXF_NONE);
		v->SetSamplerState(d, s, D3DSAMP_SRGBTEXTURE, FALSE);
	}
	v->SetRenderState(d, D3DRS_ZENABLE, D3DZB_FALSE);
	v->SetRenderState(d, D3DRS_STENCILENABLE, FALSE);
	v->SetRenderState(d, D3DRS_CULLMODE, D3DCULL_NONE);
	v->SetRenderState(d, D3DRS_FILLMODE, D3DFILL_SOLID);
	v->SetRenderState(d, D3DRS_ALPHABLENDENABLE, FALSE);
	v->SetRenderState(d, D3DRS_ALPHATESTENABLE, FALSE);
	v->SetRenderState(d, D3DRS_FOGENABLE, FALSE);
	v->SetRenderState(d, D3DRS_SCISSORTESTENABLE, FALSE);
	v->SetRenderState(d, D3DRS_CLIPPLANEENABLE, 0);
	v->SetRenderState(d, D3DRS_SRGBWRITEENABLE, FALSE);
	v->SetRenderState(d, D3DRS_COLORWRITEENABLE, D3DCOLORWRITEENABLE_RED | D3DCOLORWRITEENABLE_GREEN |
	                  D3DCOLORWRITEENABLE_BLUE);
	k[0] = cfg.strength / w;
	k[1] = cfg.strength / h;
	k[2] = t * cfg.speed;
	k[3] = cfg.chroma;
	k[4] = cfg.spread / w;
	k[5] = cfg.spread / h;
	k[6] = 1.5f;
	k[7] = 0.0f;
	k[8] = cfg.noise_tiles * w / h;
	k[9] = cfg.noise_tiles;
	k[10] = cfg.debug_view ? 1.0f : 0.0f;
	k[11] = cfg.debug_view == 2 ? 1.0f : 0.0f;
	R.SetPixelShaderConstantF(d, 0, k, 3);
	STEP(9, R.DrawPrimitiveUP(d, D3DPT_TRIANGLESTRIP, 2, q, sizeof q[0]));

	// 4. the game's state back; the blade then draws on top of the bent scene
	STEP(10, g_sb->lpVtbl->Apply(g_sb));
	v->SetViewport(d, &vp);
}

static void mirage(IDirect3DDevice9 *d, const Draw *c)
{
	IDirect3DSurface9 *rt = NULL;
	D3DSURFACE_DESC rd;
	LARGE_INTEGER now;

	g_stat_match++;
	QueryPerformanceCounter(&now);
	if (now.QuadPart - g_frame_t > g_qpf / 10) {   // no Present for a while: count from here
		g_frame_mirages = 0;
		g_frame_t = now.QuadPart;
	}
	if (g_frame_mirages >= (unsigned int)cfg.max_per_frame) {
		g_stat_capped++;
		return;
	}
	if (FAILED(d->lpVtbl->GetRenderTarget(d, 0, &rt)) || !rt)
		return;
	g_busy = 1;
	__try {
		if (SUCCEEDED(rt->lpVtbl->GetDesc(rt, &rd)) && ensure(d, &rd)) {
			if (!g_first_done++)
				logf_("first ghostfire blade mirage: target %ux%u, format %d, draw kind %d", rd.Width, rd.Height,
				      (int)rd.Format, c->kind);
			run(d, c, rt, &rd, now.QuadPart);
			g_frame_mirages++;
			g_stat_done++;
		}
	} __except (EXCEPTION_EXECUTE_HANDLER) {
		g_broken = 1;
		logf_("exception 0x%08lx in the mirage; mirage off for this session", GetExceptionCode());
		d->lpVtbl->SetRenderTarget(d, 0, rt);
		if (g_sb)
			g_sb->lpVtbl->Apply(g_sb);
	}
	g_busy = 0;
	rt->lpVtbl->Release(rt);
}

// Reads the bound pixel program and c3 from the device at each draw instead of tracking the Set calls: in game
// (18 Oct, 7:11 and 7:35 PM) the tracked state never matched although the blade programs loaded, so the client may
// set them some other way (state blocks, say). Costs one GetPixelShader per draw once a blade program exists.
static int ghost_draw(IDirect3DDevice9 *d)
{
	IDirect3DPixelShader9 *ps = NULL;
	float c3[4], b;
	int blade, ghost;
	if (d != g_dev || !g_blade_n || !g_on || g_broken || g_busy)
		return 0;
	if (FAILED(d->lpVtbl->GetPixelShader(d, &ps)) || !ps)
		return 0;
	blade = is_blade_ps(ps);
	ps->lpVtbl->Release(ps);
	if (!blade || FAILED(d->lpVtbl->GetPixelShaderConstantF(d, 3, c3, 1)))
		return 0;
	b = max(c3[0], max(c3[1], c3[2]));
	ghost = b > 0.01f && b <= cfg.max_bright;
	g_stat_blade++;
	if (b < g_stat_bmin)
		g_stat_bmin = b;
	if (b > g_stat_bmax)
		g_stat_bmax = b;
	if (g_blade_logged < 8) {
		g_blade_logged++;
		logf_("blade program draw: c3 %.3f %.3f %.3f %.3f%s", c3[0], c3[1], c3[2], c3[3],
		      ghost ? " (ghostfire)" : "");
	}
	return ghost;
}

static void poll_toggle(void)
{
	static int was;
	int down;
	if (!cfg.toggle_key)
		return;
	down = (GetAsyncKeyState(cfg.toggle_key) & 0x8000) &&
	       (!(cfg.toggle_mods & 1) || (GetAsyncKeyState(VK_CONTROL) & 0x8000)) &&
	       (!(cfg.toggle_mods & 2) || (GetAsyncKeyState(VK_SHIFT) & 0x8000)) &&
	       (!(cfg.toggle_mods & 4) || (GetAsyncKeyState(VK_MENU) & 0x8000));
	if (down && !was) {
		DWORD pid = 0;
		HWND fg = GetForegroundWindow();
		GetWindowThreadProcessId(fg, &pid);
		if (fg && pid == GetCurrentProcessId()) {
			g_on = !g_on;
			logf_("mirage switched %s (toggle key)", g_on ? "on" : "off");
		}
	}
	was = down != 0;
}

static void end_frame(void)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	g_frames++;
	g_frame_mirages = 0;
	g_frame_t = now.QuadPart;
	poll_toggle();
	if (g_frames == 1200 && g_blade_n == 0)
		logf_("1200 frames and no blade pixel program seen yet (set log_shaders=1 to list the ids)");
	if (now.QuadPart - g_stat_t > 30 * g_qpf) {
		if (g_stat_match || g_stat_blade || g_stat_bind)
			logf_("last %.0f s: blade program bound %u times, %u draws with it (c3 brightest %.3f to %.3f), "
			      "%u ghostfire, %u mirage passes, %u over the per-frame cap%s",
			      (double)(now.QuadPart - g_stat_t) / g_qpf, g_stat_bind, g_stat_blade,
			      g_stat_blade ? g_stat_bmin : 0.0f, g_stat_blade ? g_stat_bmax : 0.0f, g_stat_match, g_stat_done,
			      g_stat_capped, g_on ? "" : " (switched off)");
		g_stat_match = g_stat_done = g_stat_capped = g_stat_bind = g_stat_blade = 0;
		g_stat_bmin = 9.0f;
		g_stat_bmax = -1.0f;
		g_stat_t = now.QuadPart;
	}
}

// ---- device hooks ----

static HRESULT STDMETHODCALLTYPE hk_Reset(IDirect3DDevice9 *d, D3DPRESENT_PARAMETERS *pp)
{
	HRESULT hr;
	if (d == g_dev)
		release_default();
	hr = R.Reset(d, pp);
	logf_("Reset %ux%u: 0x%08lx", pp ? pp->BackBufferWidth : 0, pp ? pp->BackBufferHeight : 0, hr);
	return hr;
}

static HRESULT STDMETHODCALLTYPE hk_Present(IDirect3DDevice9 *d, const RECT *src, const RECT *dst, HWND wnd,
                                            const RGNDATA *dirty)
{
	if (d == g_dev)
		end_frame();
	return R.Present(d, src, dst, wnd, dirty);
}

static HRESULT STDMETHODCALLTYPE hk_CreatePixelShader(IDirect3DDevice9 *d, const DWORD *fn,
                                                      IDirect3DPixelShader9 **out)
{
	HRESULT hr = R.CreatePixelShader(d, fn, out);
	if (SUCCEEDED(hr) && d == g_dev && fn && out && *out) {
		unsigned int id = shader_id(fn);
		int i;
		for (i = 0; i < g_blade_n; i++)   // an address the game freed and reused
			if (g_blade_ps[i] == *out) {
				g_blade_ps[i] = g_blade_ps[--g_blade_n];
				break;
			}
		if (is_blade_id(id) && g_blade_n < 16) {
			g_blade_ps[g_blade_n++] = *out;
			logf_("blade pixel program 0x%08x created", id);
		} else if (cfg.log_shaders) {
			logf_("pixel program 0x%08x, version 0x%08lx", id, fn[0]);
		}
	}
	return hr;
}

// diagnostics only: how often the game binds a blade program directly, and whether it records state blocks
static HRESULT STDMETHODCALLTYPE hk_SetPixelShader(IDirect3DDevice9 *d, IDirect3DPixelShader9 *ps)
{
	if (d == g_dev && g_blade_n && is_blade_ps(ps))
		g_stat_bind++;
	return R.SetPixelShader(d, ps);
}

static HRESULT STDMETHODCALLTYPE hk_BeginStateBlock(IDirect3DDevice9 *d)
{
	static int said;
	if (!said++)
		logf_("the game records state blocks (BeginStateBlock)");
	return R.BeginStateBlock(d);
}

static HRESULT STDMETHODCALLTYPE hk_CreateStateBlock(IDirect3DDevice9 *d, D3DSTATEBLOCKTYPE type,
                                                     IDirect3DStateBlock9 **out)
{
	static int said;
	if (!said++)
		logf_("the game creates state blocks (CreateStateBlock type %d)", (int)type);
	return R.CreateStateBlock(d, type, out);
}

static HRESULT STDMETHODCALLTYPE hk_DrawPrimitive(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, UINT start, UINT n)
{
	if (ghost_draw(d)) {
		Draw c = { 0 };
		c.kind = 0, c.type = type, c.a = start, c.b = n;
		mirage(d, &c);
	}
	return R.DrawPrimitive(d, type, start, n);
}

static HRESULT STDMETHODCALLTYPE hk_DrawIndexedPrimitive(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, INT base,
                                                         UINT minv, UINT nv, UINT start, UINT n)
{
	if (ghost_draw(d)) {
		Draw c = { 0 };
		c.kind = 1, c.type = type, c.base = base, c.a = minv, c.b = nv, c.c = start, c.d = n;
		mirage(d, &c);
	}
	return R.DrawIndexedPrimitive(d, type, base, minv, nv, start, n);
}

static HRESULT STDMETHODCALLTYPE hk_DrawPrimitiveUP(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, UINT n,
                                                    const void *vtx, UINT stride)
{
	if (ghost_draw(d)) {
		Draw c = { 0 };
		c.kind = 2, c.type = type, c.a = n, c.vtx = vtx, c.stride = stride;
		mirage(d, &c);
	}
	return R.DrawPrimitiveUP(d, type, n, vtx, stride);
}

static HRESULT STDMETHODCALLTYPE hk_DrawIndexedPrimitiveUP(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, UINT minv,
                                                           UINT nv, UINT n, const void *idx, D3DFORMAT ifmt,
                                                           const void *vtx, UINT stride)
{
	if (ghost_draw(d)) {
		Draw c = { 0 };
		c.kind = 3, c.type = type, c.a = minv, c.b = nv, c.c = n, c.idx = idx, c.ifmt = ifmt, c.vtx = vtx,
		c.stride = stride;
		mirage(d, &c);
	}
	return R.DrawIndexedPrimitiveUP(d, type, minv, nv, n, idx, ifmt, vtx, stride);
}

static void patch(void **slot, void *hook)
{
	DWORD old;
	if (*slot == hook || !VirtualProtect(slot, sizeof(void *), PAGE_READWRITE, &old))
		return;
	*slot = hook;
	VirtualProtect(slot, sizeof(void *), old, &old);
}

// The vtable is the real DLL's, shared by every device it makes, so it is patched once.
static void hook_device(IDirect3DDevice9 *d)
{
	IDirect3DDevice9Vtbl *vt = d->lpVtbl;
	if (vt->Present == hk_Present)
		return;
	R = *vt;
	patch((void **)&vt->Reset, (void *)hk_Reset);
	patch((void **)&vt->Present, (void *)hk_Present);
	patch((void **)&vt->CreatePixelShader, (void *)hk_CreatePixelShader);
	patch((void **)&vt->SetPixelShader, (void *)hk_SetPixelShader);
	patch((void **)&vt->BeginStateBlock, (void *)hk_BeginStateBlock);
	patch((void **)&vt->CreateStateBlock, (void *)hk_CreateStateBlock);
	patch((void **)&vt->DrawPrimitive, (void *)hk_DrawPrimitive);
	patch((void **)&vt->DrawIndexedPrimitive, (void *)hk_DrawIndexedPrimitive);
	patch((void **)&vt->DrawPrimitiveUP, (void *)hk_DrawPrimitiveUP);
	patch((void **)&vt->DrawIndexedPrimitiveUP, (void *)hk_DrawIndexedPrimitiveUP);
	logf_("device hooked%s", vt->Present == hk_Present ? "" : " (FAILED: vtable not writable)");
}

static HRESULT STDMETHODCALLTYPE hk_CreateDevice(IDirect3D9 *self, UINT adapter, D3DDEVTYPE type, HWND wnd,
                                                 DWORD flags, D3DPRESENT_PARAMETERS *pp, IDirect3DDevice9 **out)
{
	HRESULT hr = R9.CreateDevice(self, adapter, type, wnd, flags, pp, out);
	if (pp)
		logf_("CreateDevice %ux%u, format %d, multisample %d, windowed %d: 0x%08lx", pp->BackBufferWidth,
		      pp->BackBufferHeight, (int)pp->BackBufferFormat, (int)pp->MultiSampleType, pp->Windowed, hr);
	if (SUCCEEDED(hr) && out && *out) {
		if (g_dev && g_dev != *out)   // a new device: what we made belongs to the old one
			release_all();
		g_dev = *out;
		g_blade_n = 0;
		hook_device(*out);
	}
	return hr;
}

static void hook_d3d(IDirect3D9 *d3d)
{
	IDirect3D9Vtbl *vt = d3d->lpVtbl;
	if (vt->CreateDevice == hk_CreateDevice)
		return;
	R9 = *vt;
	patch((void **)&vt->CreateDevice, (void *)hk_CreateDevice);
}

// ---- exports (d3d9.def) ----

IDirect3D9 *WINAPI Direct3DCreate9(UINT sdk)
{
	typedef IDirect3D9 *(WINAPI *Fn)(UINT);
	Fn fn = (Fn)real_proc("Direct3DCreate9");
	IDirect3D9 *d3d = fn ? fn(sdk) : NULL;
	if (d3d && cfg.enabled && g_native && !cfg.allow_native) {
		static int said;
		if (!said++)
			logf_("system d3d9 without DXVK: passing through, no mirage (allow_native=1 to try anyway)");
	} else if (d3d && cfg.enabled) {
		hook_d3d(d3d);
	}
	return d3d;
}

HRESULT WINAPI Direct3DCreate9Ex(UINT sdk, IDirect3D9Ex **out)
{
	typedef HRESULT(WINAPI * Fn)(UINT, IDirect3D9Ex **);
	Fn fn = (Fn)real_proc("Direct3DCreate9Ex");
	return fn ? fn(sdk, out) : D3DERR_NOTAVAILABLE;
}

int WINAPI D3DPERF_BeginEvent(D3DCOLOR col, LPCWSTR name)
{
	typedef int(WINAPI * Fn)(D3DCOLOR, LPCWSTR);
	Fn fn = (Fn)real_proc("D3DPERF_BeginEvent");
	return fn ? fn(col, name) : 0;
}

int WINAPI D3DPERF_EndEvent(void)
{
	typedef int(WINAPI * Fn)(void);
	Fn fn = (Fn)real_proc("D3DPERF_EndEvent");
	return fn ? fn() : 0;
}

void WINAPI D3DPERF_SetMarker(D3DCOLOR col, LPCWSTR name)
{
	typedef void(WINAPI * Fn)(D3DCOLOR, LPCWSTR);
	Fn fn = (Fn)real_proc("D3DPERF_SetMarker");
	if (fn)
		fn(col, name);
}

void WINAPI D3DPERF_SetRegion(D3DCOLOR col, LPCWSTR name)
{
	typedef void(WINAPI * Fn)(D3DCOLOR, LPCWSTR);
	Fn fn = (Fn)real_proc("D3DPERF_SetRegion");
	if (fn)
		fn(col, name);
}

BOOL WINAPI D3DPERF_QueryRepeatFrame(void)
{
	typedef BOOL(WINAPI * Fn)(void);
	Fn fn = (Fn)real_proc("D3DPERF_QueryRepeatFrame");
	return fn ? fn() : FALSE;
}

void WINAPI D3DPERF_SetOptions(DWORD options)
{
	typedef void(WINAPI * Fn)(DWORD);
	Fn fn = (Fn)real_proc("D3DPERF_SetOptions");
	if (fn)
		fn(options);
}

DWORD WINAPI D3DPERF_GetStatus(void)
{
	typedef DWORD(WINAPI * Fn)(void);
	Fn fn = (Fn)real_proc("D3DPERF_GetStatus");
	return fn ? fn() : 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID unused)
{
	(void)unused;
	if (reason == DLL_PROCESS_ATTACH) {
		char path[MAX_PATH], exe[MAX_PATH], *slash;
		LARGE_INTEGER f, now;
		WIN32_FILE_ATTRIBUTE_DATA fa;
		DisableThreadLibraryCalls(inst);
		GetModuleFileNameA(inst, g_dir, MAX_PATH);
		slash = strrchr(g_dir, '\\');
		if (slash)
			*slash = 0;
		_snprintf(path, MAX_PATH, "%s\\mirage.log", g_dir);
		g_log = fopen(path, GetFileAttributesExA(path, GetFileExInfoStandard, &fa) && fa.nFileSizeLow > 512 * 1024 ?
		              "w" : "a");
		GetModuleFileNameA(NULL, exe, MAX_PATH);
		logf_("---- Ossus O15 mirage proxy in %s (pid %lu)", exe, GetCurrentProcessId());
		QueryPerformanceFrequency(&f);
		QueryPerformanceCounter(&now);
		g_qpf = f.QuadPart;
		g_t0 = g_frame_t = g_stat_t = now.QuadPart;
		load_config();
	} else if (reason == DLL_PROCESS_DETACH && g_log) {
		fclose(g_log);
		g_log = NULL;
	}
	return TRUE;
}
