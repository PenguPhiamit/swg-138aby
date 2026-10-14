import sys, os, struct, re, time
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I, trn_read as R
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
def strings(d): return [s.decode('latin-1') for s in re.findall(rb'[\x20-\x7e]{5,}', d)]
def hdr(d):
    size, flags, h, w, pitch, depth, mips = struct.unpack_from('<7I', d, 4); pf = struct.unpack_from('<2I4s5I', d, 76); caps = struct.unpack_from('<4I', d, 108)
    return dict(flags=hex(flags), w=w, h=h, pitch=pitch, mips=mips, pf_flags=hex(pf[1]), fourcc=pf[2], bpp=pf[3], masks=[hex(m) for m in pf[4:8]], caps1=hex(caps[0]), caps2=hex(caps[1]), total=len(d))
for s in ['shader/ui_planet_sel_tatt_as8.sht', 'shader/ui_planet_sel_hoth.sht']:
    d = get(s); print(s, '<-', idx[s], len(d), strings(d)[:12])
for n in ['texture/loading/lok/ui_load_lok.dds', 'texture/loading/tatooine/cities/tatooine_wayfar.dds', 'texture/ui_planet_sel_tatt.dds', 'texture/ui_planet_sel_tato.dds', 'texture/ui_planet_sel_hoth.dds', 'texture/ui_map_hoth.dds', 'texture/ui_map_yavin4.dds']:
    if n in idx: print(n, '<-', idx[n], hdr(get(n)))
    else: print(n, 'not in index')
print('planet sel textures:', [n for n in idx if 'ui_planet_sel' in n and n.endswith('.dds')])
print('ossus loading strings:', [n for n in os.listdir('C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/staged/client/string/en') ])
# time the Ossus height evaluator
trn = R.read_trn(open('C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/staged/client/terrain/ossus.trn', 'rb').read())
import importlib
ev = R.HeightEvaluator(trn, R.client_bitmap_loader) if hasattr(R, 'client_bitmap_loader') else None
print('header', trn['header'])
t0 = time.time(); n = 0
for y in range(-8000, 8000, 500):
    for x in range(-8000, 8000, 500): ev.height(x, y); n += 1
dt = time.time() - t0; print('evals', n, 'in %.2f s -> %.3f ms each; 512^2 would take %.0f s, 1024^2 %.0f s' % (dt, dt / n * 1000, dt / n * 512 * 512, dt / n * 1024 * 1024))
