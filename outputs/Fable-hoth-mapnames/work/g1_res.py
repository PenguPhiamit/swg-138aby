import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-caves/tools')
import swg_tables as T, trn_iff as I, ws_read as W
idx = I.client_index()
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client/local_planets.tre'
tree = T.read_dtii(I.open_tre_entry(LP, 'datatables/resource/resource_tree.iff'))
names = dict(T.stf_items(T.read_stf(I.open_tre_entry(os.path.join(I.CLIENT, idx['string/en/resource/resource_names.stf']), 'string/en/resource/resource_names.stf'))))
cols = tree['columns']; print(cols[:12])
hoth = [r for r in tree['rows'] if any('hoth' in str(c).lower() for c in r[:2])]
print('hoth rows', len(hoth))
for r in hoth: print('  ', r[1], '=', names.get(r[1], '?'))
ws = W.read_ws(I.open_tre_entry(os.path.join(I.CLIENT, idx['snapshot/hoth.ws']), 'snapshot/hoth.ws'))
nodes = ws['nodes'] if isinstance(ws, dict) else ws
print('ws nodes', len(nodes), 'sample', nodes[0])
world = [n for n in nodes if (n.get('parent', n.get('parent_id', 0)) if isinstance(n, dict) else n[1]) == 0]
print('world-level', len(world))
for n in world: print('  ', n if not isinstance(n, dict) else {k: n[k] for k in n if k in ('template', 'name', 'x', 'y', 'z', 'id', 'position', 'template_name')})
