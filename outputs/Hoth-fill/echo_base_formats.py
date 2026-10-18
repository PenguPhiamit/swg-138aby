"""H1 (Claude, 18 Oct 2026; owner: "check the client side first: compare the Echo Base building's appearance and portal
files with what the pre-CU client can read"). For the NGE Echo Base and for stock pre-CU buildings the client already
draws, print each file's archive and IFF form versions: the object template, its portal layout (pob), and the cell
appearances and floors the pob names. A version the stock buildings never use is the first suspect. Reads the client
archives only (swgfmt.trn_iff, the load order of SWG-client); writes nothing.
    python -I echo_base_formats.py
"""
import collections
import os
import re
import sys

OUTPUTS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import trn_iff as I  # noqa: E402

idx = I.client_index()
BUILDINGS = {
    'echo_base (NGE, MTG)': 'object/building/heroic/shared_echo_base.iff',
    'bunker_rebel_01 (stock)': 'object/building/general/shared_bunker_rebel_01.iff',
    'cantina_tatooine (stock)': 'object/building/tatooine/shared_cantina_tatooine.iff',
    'jabbas_palace (stock)': 'object/building/tatooine/shared_palace_tatooine_jabba.iff',
}


def get(name):
    arc = idx.get(name.lower())
    return (None, None) if arc is None else (arc, I.open_tre_entry(os.path.join(I.CLIENT, arc), name))


def shape(data, depth=3):
    """The first forms and chunk tags, e.g. FORM PRTO > FORM 0004 > ..."""
    out = []

    def walk(nodes, d):
        for n in nodes[:6]:
            out.append(('  ' * d) + (('FORM ' + n.form) if n.is_form else n.tag))
            if n.is_form and d < depth:
                walk(n.children, d + 1)
    walk(I.parse(data), 0)
    return out


def strings(data, pattern):
    return sorted(set(m.decode('latin-1') for m in re.findall(pattern, data)))


def versions(data):
    """Top form and its first version form, e.g. ('PRTO', '0004')."""
    root = I.parse(data)[0]
    first = next((c for c in root.children if c.is_form), None)
    return root.form if root.is_form else root.tag, first.form if first is not None else '-'


report = {}
for label, template in BUILDINGS.items():
    arc, data = get(template)
    print(f'\n== {label}: {template} from {arc}')
    if data is None:
        print('   not in the client archives')
        continue
    print('   template', versions(data))
    pobs = strings(data, rb'appearance/[\w/]+\.pob')
    for pob in pobs:
        parc, pdata = get(pob)
        print(f'   pob {pob} from {parc}: {versions(pdata) if pdata else "MISSING"}')
        if not pdata:
            continue
        cells_forms = collections.Counter(m.decode() for m in re.findall(rb'FORM....CELLFORM....(\d{4})', pdata))
        print('   cell form versions:', dict(cells_forms))
        refs = strings(pdata, rb'appearance/[\w/.-]+\.(?:msh|lod|cmp|flr|mgn|apt|sat)')
        kinds = collections.Counter()
        for ref in refs:
            rarc, rdata = get(ref)
            kinds[(ref.rsplit('.', 1)[1], versions(rdata) if rdata else 'MISSING', rarc and rarc.split('/')[-1])] += 1
        for (ext, ver, a), n in sorted(kinds.items(), key=lambda x: str(x)):
            print(f'     {n:3d} x .{ext} {ver} from {a}')
        report[label] = {'pob': versions(pdata), 'cells': dict(cells_forms),
                         'refs': {f'{e} {v}': n for (e, v, a), n in kinds.items()}}

print('\n== versions only in echo_base:')
echo = next((v for k, v in report.items() if k.startswith('echo_base')), {})
stock = [v for k, v in report.items() if not k.startswith('echo_base')]
seen = {str(s['pob']) for s in stock} | {k for s in stock for k in s['refs']} | {c for s in stock for c in s['cells']}
for key in [str(echo.get('pob'))] + list(echo.get('refs', {})) + list(echo.get('cells', {})):
    if key not in seen:
        print('  ', key)
