"""H1 (Claude, 18 Oct 2026): the PRTO version of every portal layout (.pob) in the client archives, split into stock
(SOE) and Mod the Galaxy archives, and the shape of the portal block in each version. Reads only.
    python -I pob_versions.py
"""
import collections
import os
import sys

OUTPUTS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import trn_iff as I  # noqa: E402

idx = I.client_index()
count = collections.Counter()
examples = {}
for name, arc in idx.items():
    if not name.endswith('.pob'):
        continue
    group = 'mtg' if 'mtg' in arc.lower() else ('local' if 'local' in arc.lower() else 'stock')
    try:
        root = I.parse(I.open_tre_entry(os.path.join(I.CLIENT, arc), name))[0]
        version = next(c.form for c in root.children if c.is_form)
    except Exception as error:  # a file the reader can't parse is worth seeing too
        version = 'unreadable: ' + str(error)[:40]
    count[(group, version)] += 1
    examples.setdefault((group, version), []).append(name)
for (group, version), n in sorted(count.items()):
    print(f'{group:6} PRTO {version}: {n:4d}   e.g. {", ".join(examples[(group, version)][:3])}')


def outline(name, depth=4):
    root = I.parse(I.open_tre_entry(os.path.join(I.CLIENT, idx[name]), name))[0]
    lines = []

    def walk(n, d):
        lines.append('  ' * d + (('FORM ' + n.form) if n.is_form else f'{n.tag} ({len(n.data)} bytes)'))
        if n.is_form and d < depth:
            kids = n.children
            for c in kids[:3]:
                walk(c, d + 1)
            if len(kids) > 3:
                lines.append('  ' * (d + 1) + f'... {len(kids) - 3} more')
    walk(root, 0)
    return lines


for name in ('appearance/poi_all_rebl_bunker_s01.pob', 'appearance/echo_base_pob.pob'):
    print(f'\n{name}:')
    print('\n'.join(outline(name)))
