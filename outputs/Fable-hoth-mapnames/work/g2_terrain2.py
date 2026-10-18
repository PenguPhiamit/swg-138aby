import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/tools')
import trn_iff as I, trn_read as R
idx = I.client_index()
data = I.open_tre_entry(os.path.join(I.CLIENT, idx['terrain/hoth.trn']), 'terrain/hoth.trn')
t = R.read_trn(data)
print('keys', list(t)[:12]); print('bitmaps', t.get('bitmaps'))
layers = t['layers'] if 'layers' in t else t.get('root')
def find(layer, depth=0, path=''):
    name = layer.get('name') if isinstance(layer, dict) else None
    rules = layer.get('rules', []) if isinstance(layer, dict) else []
    bits = [r for r in rules if r.get('tag') == 'FBIT' or r.get('type') == 'FBIT' or 'bitmap' in str(r.get('tag', '')).lower()]
    bounds = [r for r in rules if str(r.get('tag', '')) in ('BREC', 'BCIR', 'BPOL')]
    hit = any((r.get('family') == 1 or r.get('family_id') == 1) for r in bits)
    if bits or 'echo' in str(name).lower():
        print(' ' * depth, 'LAYER', name, 'bits', [(r.get('tag'), r.get('family', r.get('family_id'))) for r in bits], 'bounds', [(r.get('tag'), {k: v for k, v in r.items() if k not in ('tag',)}) for r in bounds][:2])
    for c in layer.get('children', []) if isinstance(layer, dict) else []:
        find(c, depth + 1)
if isinstance(layers, list):
    for L in layers: find(L)
else:
    print(type(layers)); print(str(layers)[:600])
