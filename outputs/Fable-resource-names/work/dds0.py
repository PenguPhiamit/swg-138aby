import sys, os, struct, collections
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import trn_iff as I
idx = I.client_index()
def get(n): return I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n)
def hdr(d):
    assert d[:4] == b'DDS '
    size, flags, h, w, pitch, depth, mips = struct.unpack_from('<7I', d, 4)
    pf = struct.unpack_from('<2I4s5I', d, 76)
    caps = struct.unpack_from('<4I', d, 108)
    return dict(size=size, flags=hex(flags), w=w, h=h, pitch=pitch, mips=mips, pf_flags=hex(pf[1]), fourcc=pf[2], bpp=pf[3], masks=[hex(m) for m in pf[4:8]], caps=[hex(c) for c in caps], total=len(d))
for n in ['texture/ui_map_tatooine.dds', 'texture/ui_map_hoth.dds', 'texture/ui_planet_sel_tatooine.dds', 'texture/ui_planet_sel_hoth.dds', 'texture/ui_load_tatooine.dds', 'texture/ui_load_tatooine_01.dds']:
    if n in idx: print(n, '<-', idx[n], hdr(get(n)))
    else: print(n, 'not in index')
print([n for n in idx if 'ui_planet_sel' in n][:20])
print([n for n in idx if n.startswith('texture/ui_load') or 'loading' in n and n.endswith('.dds')][:20])
# formats across a sample of DDS files
cnt = collections.Counter()
for n in [x for x in idx if x.endswith('.dds') and x.startswith('texture/ui_')][:400]:
    try: h = hdr(get(n)); cnt[(h['fourcc'], h['bpp'])] += 1
    except Exception as e: cnt['err'] += 1
print('ui_ dds formats (fourcc, bpp):', cnt.most_common(8))
