import sys, os, re, struct
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools')
from swgfmt import trn_iff as I
idx = I.client_index()
def get(n): return I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n)
def strings(d): return [s.decode('latin-1') for s in re.findall(rb'[\x20-\x7e]{5,}', d)]
for n in ['object/building/heroic/shared_echo_base.iff']:
    d = get(n); print(n, '<-', idx[n], len(d), 'B'); print('   refs:', [s for s in strings(d) if '/' in s or '.' in s][:20])
    nodes = I.parse(d)
    def walk(ns, depth=0):
        for x in ns:
            if x.is_form: print('  ' * depth + 'FORM ' + x.form + ' [%d]' % len(x.children)); walk(x.children, depth + 1)
            else: print('  ' * depth + x.tag + ' [%d] %s' % (len(x.data), x.data[:48]))
    walk(nodes[:1])
pob = get('appearance/echo_base_pob.pob'); print('pob', idx['appearance/echo_base_pob.pob'], len(pob), 'B')
nodes = I.parse(pob)
tags = {}
def count(ns, path=''):
    for x in ns:
        if x.is_form: count(x.children, path + '/' + x.form)
        else: tags[path + '/' + x.tag] = tags.get(path + '/' + x.tag, 0) + 1
count(nodes); print({k: v for k, v in list(tags.items())[:30]})
print('pob refs:', [s for s in strings(pob) if '/' in s][:40])
