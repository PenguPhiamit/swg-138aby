import sys, os, struct
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-caves/tools')
import trn_iff as I, ws_read as W
idx = I.client_index()
def get(n): return I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n)
data = get('terrain/hoth.trn'); nodes = I.parse(data)
# find bitmap family ids whose name/file mention echo_base
def walk(ns, path=()):
    for n in ns:
        yield n, path
        if getattr(n, 'children', None):
            yield from walk(n.children, path + (n.form_type if hasattr(n, 'form_type') else getattr(n, 'tag', '?'),))
fam = {}
for n, path in walk(nodes):
    d = getattr(n, 'data', None)
    if d and b'echo_base' in d:
        tag = getattr(n, 'tag', None) or getattr(n, 'form_type', None)
        print('chunk with echo_base:', tag, 'path', path[-4:], 'len', len(d))
        print('   ', d[:120])
