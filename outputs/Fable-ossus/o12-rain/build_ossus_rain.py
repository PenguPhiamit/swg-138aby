"""Ossus rain fix (O12): the forest areas take the plains environment, so the rain stops freezing at forest edges
(Claude, 18 Oct 2026).

Owner, 18 Oct ~5:30 PM: "its static and patchy, raining in some areas not in others", then "Rain hanging still in the
air, near trees or at the edge of a forest". The client picks an environment family per spot from the terrain's AENV
affectors and swaps the camera's rain particle whenever the family changes; the old rain is left hanging where it
was. Ossus's 'forest' family (2) sits in the 'forests' layer under a fractal filter ('forest patches'), so forest and
plains alternate in small patches all over the map and every crossing swaps the rain. All six Ossus families have the
same rain rows (datatables/environment/ossus.iff, the stock Dantooine rows) and the same sky and ramp; the forest
family differs only in its ambient sounds and environment maps (Dantooine's steppe ones). Owner, 18 Oct: "Yes, switch
off the Ossus forest weather area. Build the archive now; install it when I say I'm off the game."

  changed  terrain/ossus.trn   the 'forest' AENV affector's active flag 1 -> 0 (one byte); the layer, its fractal,
                               shader and flora (trees, undergrowth, ferns) stay on

Forests then fall through to the map-wide 'base: rolling hills' affector (family 1, ossus_plains). Every other entry
of the archive stays byte for byte.

    C:/Users/Pengw/miniconda3/python.exe -I build_ossus_rain.py [--base PATH] [--out PATH]
Default base: ../../SWG-client/local_planets.tre (installed, sha256 dc07e0b9..., the ghostfire LSD step).
Default out:  ../../../work/ossus-rain/local_planets-ossus-rain.tre (+ .sha256); checks in ./checks-rain.json.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

TRN = 'terrain/ossus.trn'
LAYER, AFFECTOR, FAMILY = 'forests', 'forest', 2
BASE_SHA_PREFIX = 'dc07e0b9'


def cstrings(b):
    return [s.decode('latin-1') for s in b.split(b'\0') if s]


def ihdr_data(node):
    """The DATA chunk of a FORM's own IHDR (FORM IHDR > FORM 0001 > DATA: u32 active, cstring name)."""
    for c in node.children:
        if c.is_form and c.form == 'IHDR':
            for _, x in trn_iff.walk(c.children):
                if not x.is_form and x.tag == 'DATA':
                    return x
    if node.children and node.children[0].is_form:   # a versioned form: FORM AENV > FORM 0000 > FORM IHDR
        return ihdr_data(node.children[0])
    return None


def name_of(node):
    d = ihdr_data(node)
    return (cstrings(d.data[4:]) or [''])[0] if d else ''


def environment_affectors(nodes):
    """[(layer names, affector name, active, family)] for every AENV, in file order."""
    out = []

    def visit(ns, layers):
        for n in ns:
            if n.is_form and n.form == 'LAYR':
                visit(n.children, layers + [name_of(n)])
            elif n.is_form and n.form == 'AENV':
                d = ihdr_data(n)
                fam = [x for _, x in trn_iff.walk(n.children) if not x.is_form and x.tag == 'DATA' and x is not d]
                out.append((tuple(layers), name_of(n), struct.unpack_from('<I', d.data)[0],
                            struct.unpack_from('<i', fam[-1].data)[0]))
            elif n.is_form:
                visit(n.children, layers)
    visit(nodes, [])
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre'))
    ap.add_argument('--out', default=os.path.join(H, 'work', 'ossus-rain', 'local_planets-ossus-rain.tre'))
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    if not base_sha.startswith(BASE_SHA_PREFIX):
        print('NOTE: base is %s, not the installed %s...' % (base_sha[:8], BASE_SHA_PREFIX))
    base = tre_write.read(base_bytes)[0]
    old = base[TRN]
    nodes = trn_iff.parse(old)
    assert trn_iff.build(nodes) == old, 'terrain does not round-trip'
    before = environment_affectors(nodes)

    hits = []
    for _, n in trn_iff.walk(nodes):
        if n.is_form and n.form == 'LAYR' and name_of(n) == LAYER:
            ver = n.children[0]
            hits += [c for c in ver.children if c.is_form and c.form == 'AENV' and name_of(c) == AFFECTOR]
    assert len(hits) == 1, 'expected one %r affector in layer %r, found %d' % (AFFECTOR, LAYER, len(hits))
    d = ihdr_data(hits[0])
    assert struct.unpack_from('<I', d.data)[0] == 1, 'the forest affector is already off'
    d.data = struct.pack('<I', 0) + d.data[4:]
    new = trn_iff.build(nodes)

    diff = [i for i in range(len(old)) if old[i] != new[i]]
    assert len(new) == len(old) and len(diff) == 1, diff[:5]
    after = environment_affectors(trn_iff.parse(new))
    changed_rows = [(b, a) for b, a in zip(before, after) if b != a]
    assert len(changed_rows) == 1 and changed_rows[0][0][3] == FAMILY and changed_rows[0][1][2] == 0, changed_rows
    base_layer = [a for a in after if a[3] == 1 and a[2] == 1 and len(a[0]) == 1]
    assert base_layer, 'no map-wide plains affector for the forests to fall back on'

    files = dict(base)
    files[TRN] = new
    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    sha = hashlib.sha256(out).hexdigest()
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (sha, os.path.basename(args.out)))
    ours = tre_write.read(out)[0]
    changed = sorted(n for n in base if base[n] != ours.get(n))
    assert changed == [TRN] and sorted(ours) == sorted(base), changed
    checks = {'base_sha256': base_sha, 'base_entries': len(base), 'out_sha256': sha, 'out_bytes': len(out),
              'out_entries': len(ours), 'changed': changed, 'trn_byte_changed': diff[0],
              'environment_before': [list(r) for r in before], 'environment_after': [list(r) for r in after]}
    with open(os.path.join(HERE, 'checks-rain.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: checks[k] for k in ('base_sha256', 'out_sha256', 'out_entries', 'changed', 'trn_byte_changed')},
                     indent=1))
    for b, a in zip(before, after):
        print('  %-55s family %d  %s' % (' / '.join(a[0]) + ' : ' + a[1], a[3], 'on' if a[2] else 'OFF (was on)' if b[2] else 'off'))
    print('Ossus rain step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
