import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-caves/tools')
import swg_tables as T, trn_iff as I, ws_read as W
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client/local_planets.tre'
print('local_planets.tre present:', os.path.exists(LP))
lp = I.list_tre(LP) if os.path.exists(LP) else {}
print('local_planets entries:', sorted(lp))
def lpget(n): return I.open_tre_entry(LP, n)
# travel fares
t = T.read_dtii(lpget('datatables/travel/travel.iff') if 'datatables/travel/travel.iff' in lp else get('datatables/travel/travel.iff')); print('\n== travel', t['columns'])
for r in t['rows']:
    s = str(r).lower()
    if r[0] in ('tatooine', 'corellia', 'hoth'): print('  ', r)
# resources
tree = T.read_dtii(lpget('datatables/resource/resource_tree.iff')); rn=[n for n in idx if 'resource_names' in n]; print('resource name files', rn); names = dict(T.stf_items(T.read_stf(get(rn[0])))) if rn else {}
print('\n== resource tree rows', len(tree['rows']), tree['columns'][:4])
hoth = [r for r in tree['rows'] if 'hoth' in str(r[0]).lower()]
print('hoth rows', len(hoth)); print('  ', [(r[0], names.get(r[0], '?')) for r in hoth])
# CRC table
cst = T.read_cstb(lpget('misc/object_template_crc_string_table.iff')); print('\n== CRC table type', type(cst), len(cst))
strs = [e[1] if isinstance(e, (list, tuple)) else e for e in (cst if isinstance(cst, list) else cst.get('entries', []))]
hits = sorted(s for s in strs if isinstance(s, str) and ('echo' in s.lower() or 'hoth' in s.lower() or 'heroic' in s.lower()))
print('echo/hoth/heroic names in merged CRC table:', len(hits)); [print('  ', s) for s in hits[:60]]
# appearance files for echo base
app = sorted(n for n in idx if 'echo' in n and n.startswith('appearance/'))
print('\n== appearance echo files', len(app)); [print('  ', n, '<-', idx[n]) for n in app[:30]]
# MTG snapshot world-level objects
ws = W.read_ws(get('snapshot/hoth.ws')); print('\n== hoth.ws type', type(ws))
nodes = ws['nodes'] if isinstance(ws, dict) else ws
print(len(nodes), nodes[0] if nodes else None)
