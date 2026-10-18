import sys, os, re
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-caves/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
print('local_planets in index:', any('local_planets' in v for v in idx.values()))
def get(name, arc=None):
    arc = arc or idx[name]
    return I.open_tre_entry(os.path.join(I.CLIENT, arc), name)
# 1. buildings of interest
pats = ['echo', 'hoth', 'military', 'bunker', 'hangar', 'rebl', 'rebel', 'snow', 'ice']
bl = [n for n in idx if n.startswith('object/building/') and any(p in n for p in pats)]
print('\n== object/building matches', len(bl))
for n in sorted(bl): print('  ', n, '<-', idx[n])
print('\n== MTG-only buildings (any)'); mtg = sorted(n for n in idx if n.startswith('object/building/') and idx[n].startswith('mtg_'))
print(len(mtg)); [print('  ', n, '<-', idx[n]) for n in mtg[:60]]
print('\n== appearance .pob with echo/hoth/snow/ice/rebl'); pobs = sorted(n for n in idx if n.endswith('.pob') and any(p in n for p in ['echo', 'hoth', 'snow', 'ice', 'rebl', 'military', 'hangar']))
[print('  ', n, '<-', idx[n]) for n in pobs]
# 2. travel fares
t = T.read_dtii(get('datatables/travel/travel.iff')); print('\n== travel.iff from', idx['datatables/travel/travel.iff'], t['columns'])
for r in t['rows']:
    s = str(r).lower()
    if ('tatooine' in s and 'corellia' in s) or 'hoth' in s: print('  ', r)
# 3. hoth resources (merged tree + names)
try:
    tree = T.read_dtii(get('datatables/resource/resource_tree.iff')); names = dict(T.stf_items(T.read_stf(get('string/en/resource_names.stf'))))
    print('\n== resource_tree from', idx['datatables/resource/resource_tree.iff'], tree['columns'][:8])
    hoth = [r for r in tree['rows'] if 'hoth' in str(r[0]).lower() or 'hoth' in str(r[1]).lower()]
    print('hoth rows', len(hoth)); [print('  ', r[0], '|', names.get(r[0], names.get(r[1], '?'))) for r in hoth[:60]]
except Exception as e: print('resource tree:', e)
# 4. merged CRC table entries
try:
    cst = T.read_cstb(get('misc/object_template_crc_string_table.iff')); print('\n== CRC table from', idx['misc/object_template_crc_string_table.iff'], len(cst) if not isinstance(cst, dict) else len(cst.get('entries', cst)))
    ents = cst if isinstance(cst, list) else cst.get('entries', [])
    strs = [e[1] if isinstance(e, (list, tuple)) else e for e in ents]
    hits = [s for s in strs if isinstance(s, str) and ('echo' in s.lower() or 'hoth' in s.lower())]
    print('echo/hoth names', len(hits)); [print('  ', s) for s in hits[:40]]
except Exception as e: print('crc table:', e)
