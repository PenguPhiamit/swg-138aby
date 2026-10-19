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

#define ROPE_MAX 64   // the whip rope's most segments

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
	int log_draws;        // >0: log this many draws of each blade program to mirage-draws-<pid>.log (the whip capture)
	int draw_key;         // with toggle_mods: log every blade draw for draw_burst seconds more (needs log_draws > 0)
	float draw_burst;
	// [whip]: the light whip's rope (step 3)
	int whip_enabled, whip_key, whip_segments;
	float whip_follow_base, whip_follow_tip, whip_momentum, whip_hz, whip_fixed_dt;
	float whip_droop, whip_coil, whip_coil_turns, whip_coil_speed, whip_width, whip_taper;
	unsigned int whip_ids[4];
	int whip_count;
	unsigned int extra_ids[8];
	int extra_count;
} cfg;

static char g_dir[MAX_PATH];
static FILE *g_log;
static int g_log_lines;
static DWORD g_pid;   // two clients write into the same mirage.log, so each line names its process

static void logf_(const char *fmt, ...)
{
	va_list ap;
	SYSTEMTIME st;
	if (!g_log || g_log_lines >= 4000)
		return;
	GetLocalTime(&st);
	fprintf(g_log, "%d:%02d:%02d.%03d %s [%lu]  ", st.wHour % 12 ? st.wHour % 12 : 12, st.wMinute, st.wSecond,
	        st.wMilliseconds, st.wHour < 12 ? "AM" : "PM", g_pid);
	va_start(ap, fmt);
	vfprintf(g_log, fmt, ap);
	va_end(ap);
	fputc('\n', g_log);
	if (++g_log_lines == 4000)
		fputs("(log full)\n", g_log);
	fflush(g_log);
}

static const char *g_sect = "mirage";   // the ini section being read

static const char *ini_str(const char *ini, const char *key, const char *def, char *buf, int size)
{
	GetPrivateProfileStringA(g_sect, key, def, buf, size, ini);
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
	cfg.log_draws = ini_int(ini, "log_draws", 0);
	cfg.draw_key = ini_int(ini, "draw_key", 0x4C);       // L
	cfg.draw_burst = ini_float(ini, "draw_burst", 4.0f);
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
	g_sect = "whip";
	cfg.whip_enabled = ini_int(ini, "enabled", 1);
	cfg.whip_key = ini_int(ini, "toggle_key", 0x42);   // B, with toggle_mods
	cfg.whip_segments = ini_int(ini, "segments", 40);
	if (cfg.whip_segments < 4)
		cfg.whip_segments = 4;
	if (cfg.whip_segments > ROPE_MAX)
		cfg.whip_segments = ROPE_MAX;
	cfg.whip_follow_base = ini_float(ini, "follow_base", 0.35f);
	cfg.whip_follow_tip = ini_float(ini, "follow_tip", 0.04f);
	cfg.whip_momentum = ini_float(ini, "momentum", 0.6f);
	cfg.whip_droop = ini_float(ini, "droop", 0.08f);
	cfg.whip_coil = ini_float(ini, "coil", 0.18f);
	cfg.whip_coil_turns = ini_float(ini, "coil_turns", 1.5f);
	cfg.whip_coil_speed = ini_float(ini, "coil_speed", 3.0f);
	cfg.whip_width = ini_float(ini, "width", 0.7f);
	cfg.whip_taper = ini_float(ini, "taper", 0.25f);
	cfg.whip_follow_base = max(0.001f, min(cfg.whip_follow_base, 1.0f));
	cfg.whip_follow_tip = max(0.001f, min(cfg.whip_follow_tip, 1.0f));
	cfg.whip_momentum = max(0.0f, min(cfg.whip_momentum, 0.95f));
	cfg.whip_hz = ini_float(ini, "substeps_hz", 240.0f);
	if (cfg.whip_hz < 30.0f)
		cfg.whip_hz = 30.0f;
	cfg.whip_fixed_dt = ini_float(ini, "fixed_dt", 0.0f);
	ini_str(ini, "ids", "238eb66a", buf, sizeof buf);
	for (p = buf; *p && cfg.whip_count < 4; p = end) {
		unsigned long id = strtoul(p, &end, 16);
		if (end == p) {
			end = p + 1;
			continue;
		}
		cfg.whip_ids[cfg.whip_count++] = (unsigned int)id;
	}
	g_sect = "mirage";
	logf_("whip rope %s: %d segments, follow %.2f at the hilt to %.2f at the tip, momentum %.2f, droop %.2f, coil %.2f "
	      "(%.1f turns, %.1f rad/s), width %.2f tapering to %.2f, %.0f sub-steps a second, toggle key 0x%02x, %d whip "
	      "program ids", cfg.whip_enabled ? "on" : "off", cfg.whip_segments, cfg.whip_follow_base, cfg.whip_follow_tip,
	      cfg.whip_momentum, cfg.whip_droop, cfg.whip_coil, cfg.whip_coil_turns, cfg.whip_coil_speed, cfg.whip_width,
	      cfg.whip_taper, cfg.whip_hz, cfg.whip_key, cfg.whip_count);
	if (cfg.log_draws > 0)
		logf_("blade-draw capture on: %d draws of each blade program, key 0x%02x adds %.0f s, to mirage-draws-%lu.log",
		      cfg.log_draws, cfg.draw_key, cfg.draw_burst, g_pid);
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
static unsigned int g_blade_id[16];
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

static int blade_slot(IDirect3DPixelShader9 *ps)
{
	int i;
	for (i = 0; ps && i < g_blade_n; i++)
		if (g_blade_ps[i] == ps)
			return i;
	return -1;
}

#define is_blade_ps(ps) (blade_slot(ps) >= 0)

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
	int replaced;   // the whip rule turned it into a DrawPrimitiveUP of the rope (whip_finish draws it)
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

// ---- blade-draw capture (log_draws: the light whip's bend, Documentation-support/lightwhip-design.md step 0) ----
// Writes each blade-program draw to mirage-draws-<pid>.log: the call, stream 0 and its vertex layout, the indices,
// the vertex positions, the first vertices in full and the vertex program constants c0-c11 (a_nolighting.vsh:
// c0-c3 object to clip, c4-c7 object to world, c8 camera position, c9 viewport, c10 fog, c11 material). Each new
// vertex program is saved as mirage-vs-<id>.bin (fxc /dumpbin reads it). Read-only: it never changes a draw.

#define CAP_VERTS 64
#define CAP_ROWS 4
#define CAP_INDICES 48
#define CAP_MAX_BYTES (24u << 20)

static FILE *g_cap;
static int g_cap_off;
static unsigned int g_cap_n, g_cap_bytes;
static struct { unsigned int id, n; } g_cap_count[8];
static int g_cap_ids;
static LONGLONG g_cap_until;
static void *g_cap_decl;
static unsigned int g_cap_vs[8];
static int g_cap_vs_n;

static void capf(const char *fmt, ...)
{
	va_list ap;
	int n;
	va_start(ap, fmt);
	n = vfprintf(g_cap, fmt, ap);
	va_end(ap);
	if (n > 0)
		g_cap_bytes += n;
}

static UINT verts_of(D3DPRIMITIVETYPE type, UINT prims)
{
	switch (type) {
	case D3DPT_POINTLIST: return prims;
	case D3DPT_LINELIST: return prims * 2;
	case D3DPT_LINESTRIP: return prims + 1;
	case D3DPT_TRIANGLELIST: return prims * 3;
	default: return prims + 2;   // triangle strips and fans
	}
}

static const BYTE g_dsize[17] = { 4, 8, 12, 16, 4, 4, 4, 8, 4, 4, 8, 4, 8, 4, 4, 4, 8 };
static const char *const g_dtype[17] = { "FLOAT1", "FLOAT2", "FLOAT3", "FLOAT4", "D3DCOLOR", "UBYTE4", "SHORT2",
	"SHORT4", "UBYTE4N", "SHORT2N", "SHORT4N", "USHORT2N", "USHORT4N", "UDEC3", "DEC3N", "FLOAT16_2", "FLOAT16_4" };
static const char *const g_dusage[14] = { "POSITION", "BLENDWEIGHT", "BLENDINDICES", "NORMAL", "PSIZE", "TEXCOORD",
	"TANGENT", "BINORMAL", "TESSFACTOR", "POSITIONT", "COLOR", "FOG", "DEPTH", "SAMPLE" };

// is this draw of blade program id due for the log (the per-program budget, or a capture-key burst)?
static int capture_due(unsigned int id, LONGLONG now)
{
	int i;
	if (cfg.log_draws <= 0 || g_cap_off)
		return 0;
	for (i = 0; i < g_cap_ids && g_cap_count[i].id != id; i++)
		;
	if (i == g_cap_ids && g_cap_ids < 8)
		g_cap_count[g_cap_ids].id = id, g_cap_count[g_cap_ids++].n = 0;
	if (i < g_cap_ids && g_cap_count[i].n < (unsigned int)cfg.log_draws) {
		g_cap_count[i].n++;
		return 1;
	}
	return now < g_cap_until;
}

static void save_vs(IDirect3DVertexShader9 *vs, unsigned int *id_out, UINT *size_out)
{
	static BYTE fn[65536];
	UINT size = 0, i;
	unsigned int id = 0x811C9DC5u;
	char path[MAX_PATH];
	FILE *f;
	if (FAILED(vs->lpVtbl->GetFunction(vs, NULL, &size)) || !size || size > sizeof fn ||
	    FAILED(vs->lpVtbl->GetFunction(vs, fn, &size)))
		return;
	for (i = 0; i < size; i++)
		id = (id ^ fn[i]) * 0x01000193u;
	*id_out = id;
	*size_out = size;
	for (i = 0; i < (UINT)g_cap_vs_n; i++)
		if (g_cap_vs[i] == id)
			return;
	if (g_cap_vs_n == 8)
		return;
	g_cap_vs[g_cap_vs_n++] = id;
	_snprintf(path, MAX_PATH, "%s\\mirage-vs-%08x.bin", g_dir, id);
	if ((f = fopen(path, "wb")) != NULL) {
		fwrite(fn, 1, size, f);
		fclose(f);
		capf("vertex program 0x%08x, %u bytes, saved to %s\n", id, size, path);
	}
}

static void capture_body(IDirect3DDevice9 *d, const Draw *c, unsigned int id, LONGLONG now)
{
	static const char *const kinds[4] = { "DrawPrimitive", "DrawIndexedPrimitive", "DrawPrimitiveUP",
		"DrawIndexedPrimitiveUP" };
	static BYTE vcopy[CAP_VERTS * 256];
	IDirect3DDevice9Vtbl *v = d->lpVtbl;
	IDirect3DVertexBuffer9 *vb = NULL;
	IDirect3DIndexBuffer9 *ib = NULL;
	IDirect3DVertexDeclaration9 *decl = NULL;
	IDirect3DVertexShader9 *vs = NULL;
	D3DVERTEXELEMENT9 el[MAXD3DDECLLENGTH + 1];
	D3DVERTEXBUFFER_DESC vd;
	D3DINDEXBUFFER_DESC idd;
	UINT nel = 0, off = 0, stride = c->stride, first = 0, nv = 0, ncopy = 0, nidx = 0, isz = 2, vsize = 0, i, k;
	UINT posoff = 0, prims = c->kind == 0 ? c->b : c->kind == 1 ? c->d : c->kind == 2 ? c->a : c->c;
	DWORD idx[CAP_INDICES], fvf = 0;
	unsigned int vsid = 0;
	float vc[48], pc[8];
	void *p;

	capf("draw %u frame %u t %.3f ps 0x%08x %s type %d", ++g_cap_n, g_frames, (double)(now - g_t0) / g_qpf, id,
	     kinds[c->kind], (int)c->type);
	if (c->kind == 0)
		capf(" start %u prims %u", c->a, c->b), first = c->a, nv = verts_of(c->type, c->b);
	else if (c->kind == 1)
		capf(" base %d minv %u nv %u start %u prims %u", c->base, c->a, c->b, c->c, c->d), first = c->base + c->a,
		    nv = c->b;
	else if (c->kind == 2)
		capf(" prims %u stride %u", c->a, c->stride), nv = verts_of(c->type, c->a);
	else
		capf(" minv %u nv %u prims %u ifmt %d stride %u", c->a, c->b, c->c, (int)c->ifmt, c->stride), first = c->a,
		    nv = c->b;
	capf("\n");

	// vertices: stream 0 for the buffer draws, the game's own memory for the UP ones
	if (c->kind < 2) {
		if (FAILED(v->GetStreamSource(d, 0, &vb, &off, &stride)) || !vb) {
			capf(" no stream 0\n");
		} else if (SUCCEEDED(vb->lpVtbl->GetDesc(vb, &vd))) {
			capf(" stream0 offset %u stride %u, buffer %u bytes pool %d usage 0x%lx fvf 0x%lx\n", off, stride, vd.Size,
			     (int)vd.Pool, vd.Usage, vd.FVF);
			ncopy = min(nv, CAP_VERTS);
			if (stride == 0 || stride > 256)
				ncopy = 0;
			while (ncopy && off + (first + ncopy) * stride > vd.Size)
				ncopy--;
			if (ncopy && SUCCEEDED(vb->lpVtbl->Lock(vb, off + first * stride, ncopy * stride, &p, D3DLOCK_READONLY))) {
				memcpy(vcopy, p, ncopy * stride);
				vb->lpVtbl->Unlock(vb);
			} else if (ncopy) {
				capf(" vertex buffer Lock failed\n");
				ncopy = 0;
			}
		}
	} else if (c->vtx && stride && stride <= 256) {
		ncopy = min(nv, CAP_VERTS);
		memcpy(vcopy, (const BYTE *)c->vtx + first * stride, ncopy * stride);
	}

	// indices
	nidx = c->kind == 1 || c->kind == 3 ? min(verts_of(c->type, prims), CAP_INDICES) : 0;
	if (c->kind == 1 && nidx) {
		if (FAILED(v->GetIndices(d, &ib)) || !ib || FAILED(ib->lpVtbl->GetDesc(ib, &idd))) {
			nidx = 0;
		} else {
			isz = idd.Format == D3DFMT_INDEX32 ? 4 : 2;
			while (nidx && (c->c + nidx) * isz > idd.Size)
				nidx--;
			if (nidx && SUCCEEDED(ib->lpVtbl->Lock(ib, c->c * isz, nidx * isz, &p, D3DLOCK_READONLY))) {
				for (i = 0; i < nidx; i++)
					idx[i] = isz == 4 ? ((const DWORD *)p)[i] : ((const WORD *)p)[i];
				ib->lpVtbl->Unlock(ib);
			} else {
				nidx = 0;
			}
		}
	} else if (c->kind == 3 && c->idx) {
		isz = c->ifmt == D3DFMT_INDEX32 ? 4 : 2;
		for (i = 0; i < nidx; i++)
			idx[i] = isz == 4 ? ((const DWORD *)c->idx)[i] : ((const WORD *)c->idx)[i];
	}
	if (nidx) {
		capf(" indices");
		for (i = 0; i < nidx; i++)
			capf(" %lu", idx[i]);
		capf("\n");
	}

	// the vertex layout (logged when it changes) and where the position is
	if (SUCCEEDED(v->GetVertexDeclaration(d, &decl)) && decl &&
	    SUCCEEDED(decl->lpVtbl->GetDeclaration(decl, el, &nel))) {
		if ((void *)decl != g_cap_decl) {
			g_cap_decl = decl;
			capf(" layout");
			for (i = 0; i < nel && el[i].Stream != 0xFF; i++)
				capf(" s%u+%u %s %s%u", el[i].Stream, el[i].Offset, el[i].Type < 17 ? g_dtype[el[i].Type] : "?",
				     el[i].Usage < 14 ? g_dusage[el[i].Usage] : "?", el[i].UsageIndex);
			capf("\n");
		}
		for (i = 0; i < nel && el[i].Stream != 0xFF; i++)
			if (el[i].Stream == 0 && el[i].UsageIndex == 0 &&
			    (el[i].Usage == D3DDECLUSAGE_POSITION || el[i].Usage == D3DDECLUSAGE_POSITIONT))
				posoff = el[i].Offset;
	} else {
		nel = 0;
		v->GetFVF(d, &fvf);
		capf(" no declaration, fvf 0x%lx\n", fvf);
	}

	// positions of up to CAP_VERTS vertices, then the first CAP_ROWS in full
	if (ncopy && posoff + 12 <= stride) {
		capf(" pos");
		for (i = 0; i < ncopy; i++) {
			const float *f = (const float *)(vcopy + i * stride + posoff);
			capf(" %.4f,%.4f,%.4f", f[0], f[1], f[2]);
		}
		capf("%s\n", ncopy < nv ? " ..." : "");
	}
	for (k = 0; k < ncopy && k < CAP_ROWS; k++) {
		const BYTE *row = vcopy + k * stride;
		capf(" v%u", k);
		if (nel) {
			for (i = 0; i < nel && el[i].Stream != 0xFF; i++) {
				UINT t = el[i].Type, j, sz = t < 17 ? g_dsize[t] : 4;
				if (el[i].Stream != 0 || el[i].Offset + sz > stride)
					continue;
				capf(" |");
				for (j = 0; j < sz / 4; j++)
					if (t <= D3DDECLTYPE_FLOAT4)
						capf(" %.4f", ((const float *)(row + el[i].Offset))[j]);
					else
						capf(" %08lx", ((const DWORD *)(row + el[i].Offset))[j]);
			}
		} else {
			for (i = 0; i + 4 <= stride && i < 64; i += 4)
				capf(" %.4f", *(const float *)(row + i));
		}
		capf("\n");
	}

	// the vertex program and its constants (the fixed-function transforms when there is none)
	if (SUCCEEDED(v->GetVertexShader(d, &vs)) && vs) {
		save_vs(vs, &vsid, &vsize);
		capf(" vs 0x%08x (%u bytes)\n", vsid, vsize);
		if (SUCCEEDED(v->GetVertexShaderConstantF(d, 0, vc, 12)))
			for (k = 0; k < 12; k += 4)
				capf(" c%u-c%u %g %g %g %g | %g %g %g %g | %g %g %g %g | %g %g %g %g\n", k, k + 3, vc[k * 4],
				     vc[k * 4 + 1], vc[k * 4 + 2], vc[k * 4 + 3], vc[k * 4 + 4], vc[k * 4 + 5], vc[k * 4 + 6],
				     vc[k * 4 + 7], vc[k * 4 + 8], vc[k * 4 + 9], vc[k * 4 + 10], vc[k * 4 + 11], vc[k * 4 + 12],
				     vc[k * 4 + 13], vc[k * 4 + 14], vc[k * 4 + 15]);
	} else {
		static const D3DTRANSFORMSTATETYPE ts[3] = { D3DTS_WORLD, D3DTS_VIEW, D3DTS_PROJECTION };
		static const char *const tn[3] = { "world", "view", "projection" };
		D3DMATRIX m;
		for (k = 0; k < 3; k++)
			if (SUCCEEDED(v->GetTransform(d, ts[k], &m)))
				capf(" fixed function %s %g %g %g %g | %g %g %g %g | %g %g %g %g | %g %g %g %g\n", tn[k], m._11,
				     m._12, m._13, m._14, m._21, m._22, m._23, m._24, m._31, m._32, m._33, m._34, m._41, m._42,
				     m._43, m._44);
	}
	if (SUCCEEDED(v->GetPixelShaderConstantF(d, 3, pc, 1)) && SUCCEEDED(v->GetPixelShaderConstantF(d, 7, pc + 4, 1)))
		capf(" ps c3 %.3f %.3f %.3f %.3f c7 %.3f %.3f %.3f %.3f\n", pc[0], pc[1], pc[2], pc[3], pc[4], pc[5], pc[6],
		     pc[7]);
	RELEASE(vs);
	RELEASE(decl);
	RELEASE(ib);
	RELEASE(vb);
}

static void capture(IDirect3DDevice9 *d, const Draw *c, unsigned int id)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	if (!capture_due(id, now.QuadPart))
		return;
	if (!g_cap) {
		char path[MAX_PATH];
		_snprintf(path, MAX_PATH, "%s\\mirage-draws-%lu.log", g_dir, g_pid);
		if (!(g_cap = fopen(path, "w"))) {
			logf_("could not write %s; capture off", path);
			g_cap_off = 1;
			return;
		}
		logf_("blade-draw capture writing to %s", path);
		capf("Ossus O15 blade-draw capture, pid %lu; t in seconds since the proxy loaded; matrices row by row\n",
		     g_pid);
	}
	__try {
		capture_body(d, c, id, now.QuadPart);
	} __except (EXCEPTION_EXECUTE_HANDLER) {
		g_cap_off = 1;
		logf_("exception 0x%08lx in the blade-draw capture; capture off for this session", GetExceptionCode());
	}
	fflush(g_cap);
	if (g_cap_bytes > CAP_MAX_BYTES) {
		g_cap_off = 1;
		capf("(capture full)\n");
		fflush(g_cap);
		logf_("blade-draw capture full after %u draws", g_cap_n);
	}
}

// ---- the light whip's bend (Documentation-support/lightwhip-design.md step 3; DESIGN.md "The light whip's bend") ----
// The client draws a blade as a 4-vertex triangle fan in object space (x = +-half width, y = 0, z = 0 at the base to
// the length at the tip; vertex 0 at the tip) and then a line list over its first two vertices (step 0 capture, 18 Oct
// 8:46 PM). For the whip program only, the fan becomes a rope: a chain of segments in world space from the base, each
// segment's direction easing towards its parent's direction of the step before (the first towards the straight
// blade), quickly near the hilt and slowly at the tip, with some momentum. So it trails a swing, snaps round when the
// swing stops, keeps its length and cannot fold back on itself (springs towards points on the straight blade folded it
// into a coil in the harness, 18 Oct 9:01 PM). Each segment's aim is its parent's direction bent a little down (droop)
// and a little round (coil: a helical wave travelling from the hilt to the tip, in the frame of the hilt's own x axis),
// both growing towards the tip, so at rest it hangs in curls rather than standing like a rod (owner, 9:10 PM: "more
// coily"). The strip narrows towards the tip (taper).
// The rope is drawn as a camera-facing strip, put back into the blade's object space through the inverse of c4-c7, with
// the game's own vertex layout, vertex program, constants, pixel program, textures and depth test. The edge line
// follows the rope. Anything unexpected draws the straight blade as the game does.

#define ROPES 8

typedef struct { float x, y, z; DWORD col; float u, v; } WVtx;   // the game's blade layout, stride 24

typedef struct {
	int used;
	unsigned int frame;           // the frame it was last drawn in
	LONGLONG t;                   // when it was last stepped
	float len, hw;                // world length and half width
	float base[3], tip[3];        // the straight blade last time
	float d[ROPE_MAX + 1][3];     // segment directions (1..n), and the step before
	float dp[ROPE_MAX + 1][3];
	float x[ROPE_MAX + 1][3];     // points, 0 at the base
	float time;                   // the coil wave's clock
} Rope;

static Rope g_rope[ROPES];
static WVtx g_wstrip[2 * (ROPE_MAX + 1)], g_wline[ROPE_MAX + 1];
static int g_whip_on = 1, g_whip_broken, g_whip_first;
static unsigned int g_wline_frame = 0xFFFFFFFFu, g_wline_start, g_wline_n;
static void *g_wdecl;                  // the last vertex declaration checked, and whether it had the blade layout
static int g_wdecl_ok;
static IDirect3DVertexBuffer9 *g_wvb;  // stream 0 to put back after the rope's DrawPrimitiveUP
static UINT g_wvb_off, g_wvb_stride;
static DWORD g_wcull;
static int g_wcull_set;
static unsigned int g_stat_rope, g_stat_straight;
static int g_wsaid[8];                 // each pass-through reason is logged once

static void whip_said(int why, const char *msg)
{
	if (!g_wsaid[why]++)
		logf_("whip drawn straight: %s (logged once)", msg);
}

static int is_whip_id(unsigned int id)
{
	int i;
	for (i = 0; i < cfg.whip_count; i++)
		if (cfg.whip_ids[i] == id)
			return 1;
	return 0;
}

static float v3len(const float *a)
{
	return sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
}

static void v3cross(float *o, const float *a, const float *b)
{
	o[0] = a[1] * b[2] - a[2] * b[1];
	o[1] = a[2] * b[0] - a[0] * b[2];
	o[2] = a[0] * b[1] - a[1] * b[0];
}

static int main_view(IDirect3DDevice9 *d)
{
	D3DVIEWPORT9 vp;
	IDirect3DSurface9 *rt = NULL;
	D3DSURFACE_DESC rd;
	int ok = 0;
	if (SUCCEEDED(d->lpVtbl->GetViewport(d, &vp)) && SUCCEEDED(d->lpVtbl->GetRenderTarget(d, 0, &rt)) && rt) {
		ok = SUCCEEDED(rt->lpVtbl->GetDesc(rt, &rd)) && vp.X == 0 && vp.Y == 0 && vp.Width == rd.Width &&
		     vp.Height == rd.Height;
		rt->lpVtbl->Release(rt);
	}
	return ok;
}

static int blade_layout(IDirect3DDevice9 *d)
{
	IDirect3DVertexDeclaration9 *decl = NULL;
	D3DVERTEXELEMENT9 el[MAXD3DDECLLENGTH + 1];
	UINT n = 0;
	if (FAILED(d->lpVtbl->GetVertexDeclaration(d, &decl)) || !decl)
		return 0;
	if ((void *)decl != g_wdecl) {
		g_wdecl = decl;
		g_wdecl_ok = SUCCEEDED(decl->lpVtbl->GetDeclaration(decl, el, &n)) && n == 4 &&
		             el[0].Stream == 0 && el[0].Offset == 0 && el[0].Type == D3DDECLTYPE_FLOAT3 &&
		             el[0].Usage == D3DDECLUSAGE_POSITION && el[1].Stream == 0 && el[1].Offset == 12 &&
		             el[1].Type == D3DDECLTYPE_D3DCOLOR && el[1].Usage == D3DDECLUSAGE_COLOR &&
		             el[2].Stream == 0 && el[2].Offset == 16 && el[2].Type == D3DDECLTYPE_FLOAT2 &&
		             el[2].Usage == D3DDECLUSAGE_TEXCOORD && el[3].Stream == 0xFF;
	}
	decl->lpVtbl->Release(decl);
	return g_wdecl_ok;
}

static void rope_points(Rope *r, const float *B, int n)
{
	int i, k;
	float rest = r->len / n;
	memcpy(r->x[0], B, sizeof r->x[0]);
	for (i = 1; i <= n; i++)
		for (k = 0; k < 3; k++)
			r->x[i][k] = r->x[i - 1][k] + r->d[i][k] * rest;
}

static void rope_reset(Rope *r, const float *B, const float *T, int n)
{
	float D[3] = { T[0] - B[0], T[1] - B[1], T[2] - B[2] }, l = v3len(D);
	int i, k;
	for (k = 0; k < 3; k++)
		D[k] = l > 1e-6f ? D[k] / l : (k == 2);
	for (i = 1; i <= n; i++) {
		memcpy(r->d[i], D, sizeof D);
		memcpy(r->dp[i], D, sizeof D);
	}
	memcpy(r->base, B, sizeof r->base);
	memcpy(r->tip, T, sizeof r->tip);
	rope_points(r, B, n);
}

// where segment q (0 at the hilt, 1 at the tip) aims: its parent's direction, bent down and round the coil
static void rope_aim(float *o, const float *par, const float *X, float q, float time)
{
	float s1[3], s2[3], l, ph, a = cfg.whip_coil * q, g = cfg.whip_droop * q, xp = X[0] * par[0] + X[1] * par[1] + X[2] * par[2];
	int k;
	for (k = 0; k < 3; k++)
		s1[k] = X[k] - xp * par[k];   // the hilt's x axis, square to the parent
	l = v3len(s1);
	if (l < 0.1f) {
		float up[3] = { 0, 1, 0 };
		v3cross(s1, par, up);
		l = v3len(s1);
	}
	if (l < 1e-6f) {
		memcpy(o, par, 3 * sizeof(float));
		return;
	}
	for (k = 0; k < 3; k++)
		s1[k] /= l;
	v3cross(s2, par, s1);
	ph = 6.2831853f * cfg.whip_coil_turns * q - cfg.whip_coil_speed * time;
	for (k = 0; k < 3; k++)
		o[k] = par[k] + a * (cosf(ph) * s1[k] + sinf(ph) * s2[k]) - (k == 1 ? g : 0.0f);   // y is up in SWG
	l = v3len(o);
	for (k = 0; k < 3; k++)
		o[k] = l > 1e-6f ? o[k] / l : par[k];
}

// one frame of the rope: the straight blade moves from (base, tip) to (B, T) over dt, in sub-steps; X is the hilt's
// x axis in the world
static void rope_step(Rope *r, const float *B, const float *T, const float *X, float dt, int n)
{
	static float old[ROPE_MAX + 1][3];
	float ae[ROPE_MAX + 1], me, h;
	int steps = (int)ceilf(dt * cfg.whip_hz), s, i, k;
	if (steps < 1)
		steps = 1;
	if (steps > 64)
		steps = 64;
	h = dt / steps;
	// per segment, how far it turns towards its parent each sub-step (rates are per 1/whip_hz s)
	for (i = 1; i <= n; i++) {
		float a = cfg.whip_follow_base * powf(cfg.whip_follow_tip / cfg.whip_follow_base, (float)i / n);
		ae[i] = 1.0f - powf(1.0f - a, cfg.whip_hz * h);
	}
	me = powf(cfg.whip_momentum, cfg.whip_hz * h);
	for (s = 1; s <= steps; s++) {
		float f = (float)s / steps, D[3], l;
		for (k = 0; k < 3; k++)
			D[k] = (r->tip[k] + (T[k] - r->tip[k]) * f) - (r->base[k] + (B[k] - r->base[k]) * f);
		l = v3len(D);
		if (l < 1e-6f)
			memcpy(D, r->d[1], sizeof D);
		else
			for (k = 0; k < 3; k++)
				D[k] /= l;
		memcpy(old, r->d, sizeof old);
		r->time += h;
		for (i = 1; i <= n; i++) {
			const float *par = i == 1 ? D : old[i - 1];
			float nw[3], aim[3];
			rope_aim(aim, par, X, (float)i / n, r->time);
			for (k = 0; k < 3; k++)
				nw[k] = old[i][k] + ae[i] * (aim[k] - old[i][k]) + me * (old[i][k] - r->dp[i][k]);
			l = v3len(nw);
			if (l < 1e-6f)
				memcpy(nw, aim, sizeof nw);
			else
				for (k = 0; k < 3; k++)
					nw[k] /= l;
			memcpy(r->dp[i], old[i], sizeof nw);
			memcpy(r->d[i], nw, sizeof nw);
		}
	}
	memcpy(r->base, B, sizeof r->base);
	memcpy(r->tip, T, sizeof r->tip);
	rope_points(r, B, n);
}

// the rope as a camera-facing strip in the blade's object space (inv = the inverse of c4-c7's 3x3, t = its translation)
static void rope_strip(const Rope *r, int n, const float *cam, const float inv[3][3], const float *t, DWORD col)
{
	float prev[3] = { 0, 0, 0 };
	int i, k, j;
	for (i = 0; i <= n; i++) {
		const float *a = r->x[i > 0 ? i - 1 : 0], *b = r->x[i < n ? i + 1 : n];
		float tan[3], view[3], side[3], l;
		for (k = 0; k < 3; k++) {
			tan[k] = b[k] - a[k];
			view[k] = r->x[i][k] - cam[k];
		}
		v3cross(side, tan, view);
		l = v3len(side);
		if (l < 1e-6f)
			memcpy(side, prev, sizeof side);
		else
			for (k = 0; k < 3; k++)
				side[k] /= l;
		if (i && side[0] * prev[0] + side[1] * prev[1] + side[2] * prev[2] < 0)
			for (k = 0; k < 3; k++)
				side[k] = -side[k];
		memcpy(prev, side, sizeof prev);
		for (j = 0; j < 2; j++) {
			float w[3], o[3];

			WVtx *v = &g_wstrip[2 * i + j];
			float hw = r->hw * cfg.whip_width * (1.0f - (1.0f - cfg.whip_taper) * i / n);
			for (k = 0; k < 3; k++)
				w[k] = r->x[i][k] + (j ? -side[k] : side[k]) * hw - t[k];
			for (k = 0; k < 3; k++)
				o[k] = inv[k][0] * w[0] + inv[k][1] * w[1] + inv[k][2] * w[2];
			v->x = o[0], v->y = o[1], v->z = o[2];
			v->col = col;
			v->u = 1.0f - (float)i / n;   // as the game's quad: u 1 at the base, 0 at the tip; v 0 and 1 across
			v->v = (float)j;
		}
		g_wline[i] = g_wstrip[2 * i];
	}
}

static int hold_stream(IDirect3DDevice9 *d)
{
	g_wvb = NULL;
	return SUCCEEDED(d->lpVtbl->GetStreamSource(d, 0, &g_wvb, &g_wvb_off, &g_wvb_stride)) && g_wvb;
}

static void whip_body(IDirect3DDevice9 *d, Draw *c)
{
	IDirect3DDevice9Vtbl *v = d->lpVtbl;
	WVtx q[4];
	void *p;
	float m[5][4], A[3][3], inv[3][3], det, B[3], T[3], len, hw, best = 1.0f, dt;
	int n = cfg.whip_segments, i, k, bi = -1, lo = 0, hi = 0;
	LARGE_INTEGER now;
	Rope *r;

	if (c->kind != 0) {
		whip_said(0, "not a DrawPrimitive call");
		return;
	}
	if (c->type == D3DPT_LINELIST && c->b == 1) {   // the edge line after the fan: along the rope
		if (g_wline_frame != g_frames || c->a != g_wline_start || !hold_stream(d))
			return;
		g_wline_frame = 0xFFFFFFFFu;
		c->kind = 2, c->type = D3DPT_LINESTRIP, c->a = g_wline_n, c->vtx = g_wline, c->stride = sizeof(WVtx);
		c->replaced = 1;
		return;
	}
	if (c->type != D3DPT_TRIANGLEFAN || c->b != 2) {
		whip_said(1, "not the 4-vertex fan");
		return;
	}
	if (!main_view(d))
		return;   // the examine or inventory view: the straight blade
	if (!blade_layout(d)) {
		whip_said(2, "another vertex layout");
		return;
	}
	if (!hold_stream(d))
		return;
	if (g_wvb_stride != sizeof(WVtx) ||
	    FAILED(g_wvb->lpVtbl->Lock(g_wvb, g_wvb_off + c->a * sizeof(WVtx), sizeof q, &p, D3DLOCK_READONLY))) {
		whip_said(3, "the vertex buffer could not be read");
		goto straight;
	}
	memcpy(q, p, sizeof q);
	g_wvb->lpVtbl->Unlock(g_wvb);
	for (i = 1; i < 4; i++) {
		if (q[i].z < q[lo].z)
			lo = i;
		if (q[i].z > q[hi].z)
			hi = i;
	}
	len = q[hi].z - q[lo].z;
	if (len < 0.01f)
		goto straight;   // off or igniting: nothing to bend
	for (i = 0; i < 4; i++)
		if (fabsf(q[i].y) > 1e-3f || (fabsf(q[i].z - q[lo].z) > 1e-3f && fabsf(q[i].z - q[hi].z) > 1e-3f) ||
		    fabsf(q[lo].z) > 1e-3f) {
			whip_said(4, "the quad has another shape");
			goto straight;
		}
	hw = fabsf(q[0].x);
	if (FAILED(v->GetVertexShaderConstantF(d, 4, &m[0][0], 5))) {
		whip_said(5, "no vertex constants");
		goto straight;
	}
	// c4-c7 as the game packs them (step 0): world.x = dot(p, c4), with c7 = 0 0 0 1
	for (i = 0; i < 3; i++)
		for (k = 0; k < 3; k++)
			A[i][k] = m[i][k];
	det = A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
	      A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]);
	if (fabsf(det) < 1e-9f || fabsf(m[3][3] - 1) > 1e-3f) {
		whip_said(6, "c4-c7 is not an object-to-world matrix");
		goto straight;
	}
	inv[0][0] = (A[1][1] * A[2][2] - A[1][2] * A[2][1]) / det;
	inv[0][1] = (A[0][2] * A[2][1] - A[0][1] * A[2][2]) / det;
	inv[0][2] = (A[0][1] * A[1][2] - A[0][2] * A[1][1]) / det;
	inv[1][0] = (A[1][2] * A[2][0] - A[1][0] * A[2][2]) / det;
	inv[1][1] = (A[0][0] * A[2][2] - A[0][2] * A[2][0]) / det;
	inv[1][2] = (A[0][2] * A[1][0] - A[0][0] * A[1][2]) / det;
	inv[2][0] = (A[1][0] * A[2][1] - A[1][1] * A[2][0]) / det;
	inv[2][1] = (A[0][1] * A[2][0] - A[0][0] * A[2][1]) / det;
	inv[2][2] = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) / det;
	for (i = 0; i < 3; i++) {
		B[i] = m[i][3];
		T[i] = A[i][2] * len + m[i][3];
	}
	{
		float x[3] = { A[0][0], A[1][0], A[2][0] }, wl[3] = { T[0] - B[0], T[1] - B[1], T[2] - B[2] };
		hw *= v3len(x);
		len = v3len(wl);
	}

	// the rope this whip had last frame: the nearest base within 1 m
	for (i = 0; i < ROPES; i++) {
		float dd[3];
		if (!g_rope[i].used || g_rope[i].frame == g_frames || g_frames - g_rope[i].frame > 10)
			continue;
		for (k = 0; k < 3; k++)
			dd[k] = g_rope[i].base[k] - B[k];
		if (v3len(dd) < best)
			best = v3len(dd), bi = i;
	}
	QueryPerformanceCounter(&now);
	if (bi < 0) {   // a new whip: a free rope, or the one seen longest ago
		for (i = 0, bi = 0; i < ROPES; i++) {
			if (!g_rope[i].used) {
				bi = i;
				break;
			}
			if (g_rope[i].frame < g_rope[bi].frame)
				bi = i;
		}
		r = &g_rope[bi];
		r->used = 0;
	}
	r = &g_rope[bi];
	dt = cfg.whip_fixed_dt > 0 ? cfg.whip_fixed_dt : (float)((double)(now.QuadPart - r->t) / g_qpf);
	if (!r->used || dt > 0.25f || fabsf(len - r->len) > 0.05f * len) {
		r->used = 1;
		r->len = len;
		rope_reset(r, B, T, n);
	} else {
		float X[3] = { A[0][0], A[1][0], A[2][0] }, xl = v3len(X);
		for (k = 0; k < 3; k++)
			X[k] /= xl;
		rope_step(r, B, T, X, min(dt, 0.05f), n);
	}
	r->hw = hw;
	r->frame = g_frames;
	r->t = now.QuadPart;
	{
		float cam[4];
		if (FAILED(v->GetVertexShaderConstantF(d, 8, cam, 1)))
			goto straight;
		rope_strip(r, n, cam, inv, B, q[0].col);
	}
	if (!g_whip_first++)
		logf_("first whip rope: %d segments, %.2f m, half width %.3f m", n, len, hw);
	g_wline_frame = g_frames;
	g_wline_start = c->a;
	g_wline_n = n;
	c->kind = 2, c->type = D3DPT_TRIANGLESTRIP, c->a = 2 * n, c->vtx = g_wstrip, c->stride = sizeof(WVtx);
	c->replaced = 1;
	return;
straight:
	RELEASE(g_wvb);
}

static void whip_rule(IDirect3DDevice9 *d, Draw *c)
{
	__try {
		whip_body(d, c);
		if (c->replaced) {
			d->lpVtbl->GetRenderState(d, D3DRS_CULLMODE, &g_wcull);
			d->lpVtbl->SetRenderState(d, D3DRS_CULLMODE, D3DCULL_NONE);
			g_wcull_set = 1;
			if (c->type == D3DPT_TRIANGLESTRIP)
				g_stat_rope++;
		} else if (c->type == D3DPT_TRIANGLEFAN) {
			g_stat_straight++;
		}
	} __except (EXCEPTION_EXECUTE_HANDLER) {
		g_whip_broken = 1;
		c->replaced = 0;
		RELEASE(g_wvb);
		logf_("exception 0x%08lx in the whip rope; whips straight for this session", GetExceptionCode());
	}
}

// draws the rope (or its edge line) in place of the game's draw, then puts stream 0 and the cull mode back
static HRESULT whip_finish(IDirect3DDevice9 *d, const Draw *c)
{
	HRESULT hr = R.DrawPrimitiveUP(d, c->type, c->a, c->vtx, c->stride);
	if (g_wvb) {
		d->lpVtbl->SetStreamSource(d, 0, g_wvb, g_wvb_off, g_wvb_stride);
		RELEASE(g_wvb);
	}
	if (g_wcull_set) {
		d->lpVtbl->SetRenderState(d, D3DRS_CULLMODE, g_wcull);
		g_wcull_set = 0;
	}
	return hr;
}

// Reads the bound pixel program and c3 from the device at each draw instead of tracking the Set calls: in game
// (18 Oct, 7:11 and 7:35 PM) the tracked state never matched although the blade programs loaded, so the client may
// set them some other way (state blocks, say). Costs one GetPixelShader per draw once a blade program exists.
static int ghost_draw(IDirect3DDevice9 *d, Draw *c)
{
	IDirect3DPixelShader9 *ps = NULL;
	float c3[4], b;
	int slot, ghost, on, whip;
	if (d != g_dev || !g_blade_n || g_busy)
		return 0;
	on = g_on && !g_broken;
	whip = cfg.whip_enabled && g_whip_on && !g_whip_broken && cfg.whip_count;
	if (!on && !whip && cfg.log_draws <= 0)
		return 0;
	if (FAILED(d->lpVtbl->GetPixelShader(d, &ps)) || !ps)
		return 0;
	slot = blade_slot(ps);
	ps->lpVtbl->Release(ps);
	if (slot < 0)
		return 0;
	if (cfg.log_draws > 0)
		capture(d, c, g_blade_id[slot]);
	if (whip && is_whip_id(g_blade_id[slot]))
		whip_rule(d, c);
	if (!on || FAILED(d->lpVtbl->GetPixelShaderConstantF(d, 3, c3, 1)))
		return 0;
	b = max(c3[0], max(c3[1], c3[2]));
	// the edge line the client draws after each blade quad lies inside the quad's mask: no second screen pass for it
	ghost = b > 0.01f && b <= cfg.max_bright && c->type != D3DPT_LINELIST && c->type != D3DPT_LINESTRIP;
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

// a key, with toggle_mods held, went down while this game's window is in front
static int key_pressed(int key, int *was)
{
	int down, hit = 0;
	if (!key)
		return 0;
	down = (GetAsyncKeyState(key) & 0x8000) &&
	       (!(cfg.toggle_mods & 1) || (GetAsyncKeyState(VK_CONTROL) & 0x8000)) &&
	       (!(cfg.toggle_mods & 2) || (GetAsyncKeyState(VK_SHIFT) & 0x8000)) &&
	       (!(cfg.toggle_mods & 4) || (GetAsyncKeyState(VK_MENU) & 0x8000));
	if (down && !*was) {
		DWORD pid = 0;
		HWND fg = GetForegroundWindow();
		GetWindowThreadProcessId(fg, &pid);
		hit = fg && pid == GetCurrentProcessId();
	}
	*was = down != 0;
	return hit;
}

static void poll_toggle(LONGLONG now)
{
	static int was_toggle, was_draw, was_whip;
	if (key_pressed(cfg.toggle_key, &was_toggle)) {
		g_on = !g_on;
		logf_("mirage switched %s (toggle key)", g_on ? "on" : "off");
	}
	if (cfg.whip_enabled && key_pressed(cfg.whip_key, &was_whip)) {
		g_whip_on = !g_whip_on;
		logf_("whip rope switched %s (toggle key)", g_whip_on ? "on" : "off");
	}
	if (cfg.log_draws > 0 && !g_cap_off && key_pressed(cfg.draw_key, &was_draw)) {
		g_cap_until = now + (LONGLONG)(cfg.draw_burst * g_qpf);
		logf_("capture key: every blade draw for %.0f s", cfg.draw_burst);
		if (g_cap) {
			capf("capture key at frame %u: every blade draw for %.0f s\n", g_frames, cfg.draw_burst);
			fflush(g_cap);
		}
	}
}

static void end_frame(void)
{
	LARGE_INTEGER now;
	QueryPerformanceCounter(&now);
	g_frames++;
	g_frame_mirages = 0;
	g_frame_t = now.QuadPart;
	poll_toggle(now.QuadPart);
	if (g_frames == 1200 && g_blade_n == 0)
		logf_("1200 frames and no blade pixel program seen yet (set log_shaders=1 to list the ids)");
	if (now.QuadPart - g_stat_t > 30 * g_qpf) {
		if (g_stat_match || g_stat_blade || g_stat_bind)
			logf_("last %.0f s: blade program bound %u times, %u draws with it (c3 brightest %.3f to %.3f), "
			      "%u ghostfire, %u mirage passes, %u over the per-frame cap%s",
			      (double)(now.QuadPart - g_stat_t) / g_qpf, g_stat_bind, g_stat_blade,
			      g_stat_blade ? g_stat_bmin : 0.0f, g_stat_blade ? g_stat_bmax : 0.0f, g_stat_match, g_stat_done,
			      g_stat_capped, g_on ? "" : " (switched off)");
		if (g_stat_rope || g_stat_straight)
			logf_("last %.0f s: whip %u drawn as a rope, %u straight (off, igniting or another view)%s",
			      (double)(now.QuadPart - g_stat_t) / g_qpf, g_stat_rope, g_stat_straight,
			      g_whip_on ? "" : " (switched off)");
		g_stat_rope = g_stat_straight = 0;
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
				g_blade_id[i] = g_blade_id[g_blade_n];
				break;
			}
		if (is_blade_id(id) && g_blade_n < 16) {
			g_blade_id[g_blade_n] = id;
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
	Draw c = { 0 };
	c.kind = 0, c.type = type, c.a = start, c.b = n;
	if (ghost_draw(d, &c))
		mirage(d, &c);
	if (c.replaced)
		return whip_finish(d, &c);
	return R.DrawPrimitive(d, type, start, n);
}

static HRESULT STDMETHODCALLTYPE hk_DrawIndexedPrimitive(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, INT base,
                                                         UINT minv, UINT nv, UINT start, UINT n)
{
	Draw c = { 0 };
	c.kind = 1, c.type = type, c.base = base, c.a = minv, c.b = nv, c.c = start, c.d = n;
	if (ghost_draw(d, &c))
		mirage(d, &c);
	return R.DrawIndexedPrimitive(d, type, base, minv, nv, start, n);
}

static HRESULT STDMETHODCALLTYPE hk_DrawPrimitiveUP(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, UINT n,
                                                    const void *vtx, UINT stride)
{
	Draw c = { 0 };
	c.kind = 2, c.type = type, c.a = n, c.vtx = vtx, c.stride = stride;
	if (ghost_draw(d, &c))
		mirage(d, &c);
	return R.DrawPrimitiveUP(d, type, n, vtx, stride);
}

static HRESULT STDMETHODCALLTYPE hk_DrawIndexedPrimitiveUP(IDirect3DDevice9 *d, D3DPRIMITIVETYPE type, UINT minv,
                                                           UINT nv, UINT n, const void *idx, D3DFORMAT ifmt,
                                                           const void *vtx, UINT stride)
{
	Draw c = { 0 };
	c.kind = 3, c.type = type, c.a = minv, c.b = nv, c.c = n, c.idx = idx, c.ifmt = ifmt, c.vtx = vtx,
	c.stride = stride;
	if (ghost_draw(d, &c))
		mirage(d, &c);
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
		g_pid = GetCurrentProcessId();
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
