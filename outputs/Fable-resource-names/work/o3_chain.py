import sys, os, struct, re
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
def strings(d): return [s.decode('latin-1') for s in re.findall(rb'[\x20-\x7e]{6,}', d)]
for n in ['appearance/ui_planet_sel_tato.apt', 'appearance/mesh/ui_planet_sel_tato.msh', 'appearance/ui_planet_sel_hoth.apt', 'appearance/mesh/ui_planet_sel_hoth.msh']:
    if n in idx:
        d = get(n); print(n, '<-', idx[n], len(d), 'B', [s for s in strings(d) if '/' in s or '.' in s][:8])
    else: print(n, 'not in index')
sh = [s for s in strings(get('appearance/mesh/ui_planet_sel_tato.msh')) if s.endswith('.sht')]
for s in sh:
    if s in idx: d = get(s); print(s, '<-', idx[s], len(d), [x for x in strings(d) if '/' in x][:6])
# hoth shader
sh = [s for s in strings(get('appearance/mesh/ui_planet_sel_hoth.msh')) if s.endswith('.sht')] if 'appearance/mesh/ui_planet_sel_hoth.msh' in idx else []
for s in sh:
    if s in idx: d = get(s); print(s, '<-', idx[s], len(d), [x for x in strings(d) if '/' in x][:6])
# loading tables
for n in ['datatables/loading/lok.iff', 'datatables/loading/hoth.iff']:
    if n in idx:
        t = T.read_dtii(get(n)); print(n, '<-', idx[n], t['columns'], t['types'], t['rows'][:3])
o = T.read_dtii(open('C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/staged/client/datatables/loading/ossus.iff', 'rb').read()); print('O1c ossus loading rows', o['rows'])
# loading tile header
def hdr(d):
    size, flags, h, w, pitch, depth, mips = struct.unpack_from('<7I', d, 4); pf = struct.unpack_from('<2I4s5I', d, 76)
    return dict(w=w, h=h, mips=mips, fourcc=pf[2], bpp=pf[3], total=len(d))
for n in ['texture/loading/lok/ui_load_lok.dds', 'texture/loading/tatooine/cities/tatooine_wayfar.dds', 'texture/ui_map_dant.dds', 'texture/ui_map_dantooine.dds']:
    if n in idx: print(n, '<-', idx[n], hdr(get(n)))
print([n for n in idx if n.startswith('texture/ui_map')][:20])
# who references the planet model .apt
for n in ['datatables/player/waypoint_planets.iff']:
    t = T.read_dtii(get(n)); print(n, t['columns'], [r for r in t['rows'] if 'tato' in str(r) or 'hoth' in str(r)][:3])
