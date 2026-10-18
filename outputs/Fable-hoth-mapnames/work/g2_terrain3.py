import sys, os, json
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/tools')
import trn_iff as I, trn_read as R
idx = I.client_index()
data = I.open_tre_entry(os.path.join(I.CLIENT, idx['terrain/hoth.trn']), 'terrain/hoth.trn')
t = R.read_trn(data)
def short(d):
    return {k: v for k, v in d.items() if k not in ('children', 'rules', 'kind') and not isinstance(v, (bytes, bytearray))}
def find(layer, depth=0):
    name = str(layer.get('name', ''))
    if 'echo' in name.lower():
        print(' ' * depth, 'LAYER', name, 'bounds', [short(b) for b in layer['boundaries']], 'filters', [short(f) for f in layer['filters']][:3], 'affectors', [short(a) for a in layer['affectors']][:3])
        for c in layer['children']:
            print(' ' * (depth + 2), 'child', c.get('name'), 'bounds', [short(b) for b in c['boundaries']], 'filters', [short(f) for f in c['filters']][:2], 'affectors', [short(a) for a in c['affectors']][:2])
    for c in layer['children']:
        find(c, depth + 1)
for L in t['layers']:
    find(L)
