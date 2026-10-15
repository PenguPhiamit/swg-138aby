import sys, os, struct
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools')
from swgfmt import trn_iff as I
idx = I.client_index(); pob = I.open_tre_entry(os.path.join(I.CLIENT, idx['appearance/echo_base_pob.pob']), 'appearance/echo_base_pob.pob')
root = I.parse(pob)[0]
def dump(n, depth=0, maxd=6):
    if n.is_form:
        print('  ' * depth + 'FORM ' + n.form + ' [%d]' % len(n.children))
        if depth < maxd:
            for c in n.children[:6]: dump(c, depth + 1, maxd)
    else:
        print('  ' * depth + n.tag + ' [%d] %s' % (len(n.data), n.data[:40]))
v4 = root.children[0]   # FORM 0004
print([c.form if c.is_form else c.tag for c in v4.children])
cels = next(c for c in v4.children if c.is_form and c.form == 'CELS')
cell0 = cels.children[0]
dump(cell0, 0, 5)
data0 = next(c for c in cell0.children[0].children if not c.is_form and c.tag == 'DATA'); print('cell0 DATA', data0.data[:60])
prtl = [c for c in cell0.children[0].children if c.is_form and c.form == 'PRTL']
print('cell0 PRTL forms', len(prtl))
for p in prtl[:4]:
    for c in p.children:
        print('   ', c.form if c.is_form else c.tag, len(c.data) if not c.is_form else len(c.children), (c.data[:30].hex() if not c.is_form else [x.tag for x in c.children][:4]))
        if c.is_form:
            for x in c.children[:3]: print('      ', x.tag, len(x.data), x.data[:24].hex())
