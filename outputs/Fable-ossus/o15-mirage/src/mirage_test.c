// Ossus O15 mirage test harness (Claude, 18 Oct 2026): drives the proxy d3d9.dll the way the client draws a blade,
// outside the game, and saves screenshots.
// Usage: mirage_test <proxy d3d9.dll> <blade .pexe> <out prefix>
// Each frame: a striped background, an opaque bar in front, a ghostfire blade (dark c3, stepping like the server's
// shimmer) on the left and a stock red blade on the right, with the real blade pixel program. Reset at frame 20,
// screenshots of frames 40 and 48 as <prefix>-40.bmp and <prefix>-48.bmp. Exit code 0 when every call worked.

#define CINTERFACE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define W 800
#define H 450

typedef struct { float x, y, z, rhw; DWORD c; float u, v; } Vtx;
#define FVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)

static int failures;

static void check(HRESULT hr, const char *what)
{
	if (FAILED(hr)) {
		printf("FAILED 0x%08lx: %s\n", hr, what);
		failures++;
	}
}

static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l)
{
	return DefWindowProcA(h, m, w, l);
}

static IDirect3DTexture9 *texture(IDirect3DDevice9 *d, int w, int h, int blade)
{
	IDirect3DTexture9 *t = NULL;
	D3DLOCKED_RECT lr;
	int x, y;
	check(d->lpVtbl->CreateTexture(d, w, h, 1, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, &t, NULL), "CreateTexture");
	check(t->lpVtbl->LockRect(t, 0, &lr, NULL, 0), "LockRect");
	for (y = 0; y < h; y++)
		for (x = 0; x < w; x++) {
			DWORD *p = (DWORD *)((BYTE *)lr.pBits + y * lr.Pitch) + x;
			if (blade) {   // u along the blade, v across: glow in rgb, white-hot core in alpha (like the stock texture)
				float v = (y + 0.5f) / h - 0.5f, u = (x + 0.5f) / w;
				float taper = u > 0.92f ? (1.0f - u) / 0.08f : 1.0f;
				int g = (int)(255 * taper * expf(-(v / 0.22f) * (v / 0.22f)));
				int a = (int)(255 * taper * expf(-(v / 0.06f) * (v / 0.06f)));
				*p = (DWORD)(a << 24 | g << 16 | g << 8 | g);
			} else {       // stripes and checks, so any bend shows
				int check8 = ((x / 16) + (y / 16)) & 1;
				int stripe = ((x + y) / 6) % 4 == 0;
				DWORD c = check8 ? 0xFF8A7F6A : 0xFF3A4F5E;
				*p = stripe ? 0xFFE8D8B0 : c;
			}
		}
	t->lpVtbl->UnlockRect(t, 0);
	return t;
}

static void quad(IDirect3DDevice9 *d, float x0, float y0, float x1, float y1, float z, DWORD c)
{
	Vtx q[4] = { { x0, y0, z, 1, c, 0, 0 }, { x1, y0, z, 1, c, 1, 0 }, { x0, y1, z, 1, c, 0, 1 }, { x1, y1, z, 1, c, 1, 1 } };
	check(d->lpVtbl->DrawPrimitiveUP(d, D3DPT_TRIANGLESTRIP, 2, q, sizeof q[0]), "DrawPrimitiveUP quad");
}

// a blade strip from (hx, hy) to (tx, ty), wide px across including the glow; u runs hilt to tip
static void blade(IDirect3DDevice9 *d, float hx, float hy, float tx, float ty, float wide)
{
	float dx = tx - hx, dy = ty - hy, len = sqrtf(dx * dx + dy * dy);
	float nx = -dy / len * wide * 0.5f, ny = dx / len * wide * 0.5f;
	Vtx q[4] = { { hx - nx, hy - ny, 0.5f, 1, 0xFFFFFFFF, 0, 0 }, { hx + nx, hy + ny, 0.5f, 1, 0xFFFFFFFF, 0, 1 },
	             { tx - nx, ty - ny, 0.5f, 1, 0xFFFFFFFF, 1, 0 }, { tx + nx, ty + ny, 0.5f, 1, 0xFFFFFFFF, 1, 1 } };
	check(d->lpVtbl->DrawPrimitiveUP(d, D3DPT_TRIANGLESTRIP, 2, q, sizeof q[0]), "DrawPrimitiveUP blade");
}

static void save_bmp(IDirect3DDevice9 *d, const char *path)
{
	IDirect3DSurface9 *bb = NULL, *sys = NULL;
	D3DLOCKED_RECT lr;
	BITMAPFILEHEADER fh = { 0 };
	BITMAPINFOHEADER ih = { 0 };
	FILE *f;
	int y;
	check(d->lpVtbl->GetBackBuffer(d, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb), "GetBackBuffer");
	check(d->lpVtbl->CreateOffscreenPlainSurface(d, W, H, D3DFMT_A8R8G8B8, D3DPOOL_SYSTEMMEM, &sys, NULL), "sysmem");
	check(d->lpVtbl->GetRenderTargetData(d, bb, sys), "GetRenderTargetData");
	check(sys->lpVtbl->LockRect(sys, &lr, NULL, D3DLOCK_READONLY), "LockRect sysmem");
	fh.bfType = 0x4D42;
	fh.bfOffBits = sizeof fh + sizeof ih;
	fh.bfSize = fh.bfOffBits + W * H * 4;
	ih.biSize = sizeof ih;
	ih.biWidth = W;
	ih.biHeight = H;
	ih.biPlanes = 1;
	ih.biBitCount = 32;
	f = fopen(path, "wb");
	fwrite(&fh, sizeof fh, 1, f);
	fwrite(&ih, sizeof ih, 1, f);
	for (y = H - 1; y >= 0; y--)
		fwrite((BYTE *)lr.pBits + y * lr.Pitch, 4, W, f);
	fclose(f);
	sys->lpVtbl->UnlockRect(sys);
	sys->lpVtbl->Release(sys);
	bb->lpVtbl->Release(bb);
	printf("saved %s\n", path);
}

int main(int argc, char **argv)
{
	typedef IDirect3D9 *(WINAPI * Create)(UINT);
	HMODULE proxy;
	Create create;
	IDirect3D9 *d3d;
	IDirect3DDevice9 *d = NULL;
	IDirect3DPixelShader9 *ps = NULL;
	IDirect3DTexture9 *bg, *bt;
	D3DPRESENT_PARAMETERS pp = { 0 };
	WNDCLASSA wc = { 0 };
	RECT r = { 0, 0, W, H };
	HWND wnd;
	FILE *f;
	DWORD code[1024];
	size_t n;
	int frame;
	char path[MAX_PATH];

	if (argc < 4) {
		printf("usage: mirage_test <proxy d3d9.dll> <blade .pexe> <out prefix>\n");
		return 2;
	}
	f = fopen(argv[2], "rb");
	if (!f) {
		printf("cannot read %s\n", argv[2]);
		return 2;
	}
	n = fread(code, 1, sizeof code, f);
	fclose(f);
	printf("blade program %s, %u bytes\n", argv[2], (unsigned)n);

	proxy = LoadLibraryA(argv[1]);
	create = proxy ? (Create)GetProcAddress(proxy, "Direct3DCreate9") : NULL;
	if (!create) {
		printf("cannot load Direct3DCreate9 from %s\n", argv[1]);
		return 2;
	}
	wc.lpfnWndProc = wndproc;
	wc.hInstance = GetModuleHandleA(NULL);
	wc.lpszClassName = "mirage_test";
	RegisterClassA(&wc);
	AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
	wnd = CreateWindowA("mirage_test", "mirage test", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 40, 40, r.right - r.left,
	                    r.bottom - r.top, NULL, NULL, wc.hInstance, NULL);

	d3d = create(D3D_SDK_VERSION);
	if (!d3d) {
		printf("Direct3DCreate9 returned NULL\n");
		return 2;
	}
	pp.BackBufferWidth = W;
	pp.BackBufferHeight = H;
	pp.BackBufferFormat = D3DFMT_A8R8G8B8;
	pp.BackBufferCount = 1;
	pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
	pp.hDeviceWindow = wnd;
	pp.Windowed = TRUE;
	pp.EnableAutoDepthStencil = TRUE;
	pp.AutoDepthStencilFormat = D3DFMT_D24S8;
	pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;
	check(d3d->lpVtbl->CreateDevice(d3d, 0, D3DDEVTYPE_HAL, wnd, D3DCREATE_HARDWARE_VERTEXPROCESSING, &pp, &d),
	      "CreateDevice");
	if (!d)
		return 2;
	check(d->lpVtbl->CreatePixelShader(d, code, &ps), "CreatePixelShader blade");
	bg = texture(d, 256, 256, 0);
	bt = texture(d, 256, 64, 1);

	for (frame = 0; frame <= 48; frame++) {
		MSG msg;
		float c7[4] = { 0, 0, 0, 1 };   // fade off, bloom off, opacity 1
		float ghost[4] = { 32 / 255.0f, (4 * (frame % 9)) / 255.0f, 32 / 255.0f, 1 };
		float red[4] = { 1.0f, 0.15f, 0.15f, 1 };
		while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE))
			DispatchMessageA(&msg);
		if (frame == 20) {
			HRESULT hr = d->lpVtbl->Reset(d, &pp);
			printf("Reset at frame 20: 0x%08lx\n", hr);
			check(hr, "Reset");
		}
		check(d->lpVtbl->Clear(d, 0, NULL, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER, 0xFF203040, 1.0f, 0), "Clear");
		check(d->lpVtbl->BeginScene(d), "BeginScene");
		d->lpVtbl->SetVertexShader(d, NULL);
		d->lpVtbl->SetFVF(d, FVF);
		d->lpVtbl->SetRenderState(d, D3DRS_LIGHTING, FALSE);
		d->lpVtbl->SetRenderState(d, D3DRS_CULLMODE, D3DCULL_NONE);
		d->lpVtbl->SetRenderState(d, D3DRS_ZENABLE, D3DZB_TRUE);
		d->lpVtbl->SetRenderState(d, D3DRS_ZWRITEENABLE, TRUE);
		d->lpVtbl->SetRenderState(d, D3DRS_ZFUNC, D3DCMP_LESSEQUAL);
		d->lpVtbl->SetRenderState(d, D3DRS_ALPHABLENDENABLE, FALSE);

		// background, then an opaque bar in front of the left blade's middle (fixed function)
		d->lpVtbl->SetPixelShader(d, NULL);
		d->lpVtbl->SetTexture(d, 0, (IDirect3DBaseTexture9 *)bg);
		d->lpVtbl->SetTextureStageState(d, 0, D3DTSS_COLOROP, D3DTOP_SELECTARG1);
		d->lpVtbl->SetTextureStageState(d, 0, D3DTSS_COLORARG1, D3DTA_TEXTURE);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_ADDRESSU, D3DTADDRESS_WRAP);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_ADDRESSV, D3DTADDRESS_WRAP);
		{
			Vtx q[4] = { { -0.5f, -0.5f, 0.9f, 1, 0xFFFFFFFF, 0, 0 }, { W - 0.5f, -0.5f, 0.9f, 1, 0xFFFFFFFF, W / 256.0f, 0 },
			             { -0.5f, H - 0.5f, 0.9f, 1, 0xFFFFFFFF, 0, H / 256.0f },
			             { W - 0.5f, H - 0.5f, 0.9f, 1, 0xFFFFFFFF, W / 256.0f, H / 256.0f } };
			check(d->lpVtbl->DrawPrimitiveUP(d, D3DPT_TRIANGLESTRIP, 2, q, sizeof q[0]), "background");
		}
		d->lpVtbl->SetTextureStageState(d, 0, D3DTSS_COLORARG1, D3DTA_DIFFUSE);
		quad(d, 120, 205, 330, 235, 0.2f, 0xFF6A3020);

		// the blades: the real blade program, additive, depth test on and depth write off (as for the game's blade)
		d->lpVtbl->SetTextureStageState(d, 0, D3DTSS_COLORARG1, D3DTA_TEXTURE);
		d->lpVtbl->SetTexture(d, 0, (IDirect3DBaseTexture9 *)bt);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_MINFILTER, D3DTEXF_LINEAR);
		d->lpVtbl->SetSamplerState(d, 0, D3DSAMP_MAGFILTER, D3DTEXF_LINEAR);
		d->lpVtbl->SetPixelShader(d, ps);
		d->lpVtbl->SetPixelShaderConstantF(d, 7, c7, 1);
		d->lpVtbl->SetRenderState(d, D3DRS_ZWRITEENABLE, FALSE);
		d->lpVtbl->SetRenderState(d, D3DRS_ALPHABLENDENABLE, TRUE);
		d->lpVtbl->SetRenderState(d, D3DRS_SRCBLEND, D3DBLEND_ONE);
		d->lpVtbl->SetRenderState(d, D3DRS_DESTBLEND, D3DBLEND_ONE);
		d->lpVtbl->SetPixelShaderConstantF(d, 3, ghost, 1);
		blade(d, 200, 400, 250, 60, 70);
		d->lpVtbl->SetPixelShaderConstantF(d, 3, red, 1);
		blade(d, 580, 400, 620, 60, 70);
		check(d->lpVtbl->EndScene(d), "EndScene");
		if (frame == 40 || frame == 48) {
			sprintf(path, "%s-%d.bmp", argv[3], frame);
			save_bmp(d, path);
		}
		check(d->lpVtbl->Present(d, NULL, NULL, NULL, NULL), "Present");
	}
	ps->lpVtbl->Release(ps);
	bg->lpVtbl->Release(bg);
	bt->lpVtbl->Release(bt);
	d->lpVtbl->Release(d);
	d3d->lpVtbl->Release(d3d);
	DestroyWindow(wnd);
	printf("%s\n", failures ? "SOME CALLS FAILED" : "all calls worked");
	return failures ? 1 : 0;
}
