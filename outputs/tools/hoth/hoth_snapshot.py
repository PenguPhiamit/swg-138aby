"""List the static objects in a planet snapshot (.ws) from our client, grouped by template.

    python -I tools/hoth/hoth_snapshot.py [planet] [x y radius]      default: hoth; with x y radius, only near there

Shows where the buildings, starports, shuttleports and caves of MTG's hoth.ws really are, to check coordinates
taken from other servers' scripts (Bellum's Hoth was built on a different snapshot). Read-only; uses Bellum's
TRE and IFF readers (AGPL-3.0, read before use).
"""
import os, sys
from collections import Counter

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
sys.path.insert(0, BELLUM)
exec(open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8').read().split('if __name__')[0])
import iff_tool  # noqa: E402  (Bellum's; ws_objects is defined at module level)


def snapshot(planet):
    hit = None
    for tre in walk_tres(CLIENT):
        try:
            for entry in read_tre(tre):
                if entry['name'].lower() == f'snapshot/{planet}.ws':
                    hit = (tre, entry)
        except Exception:
            pass
    tre, entry = hit
    with open(tre, 'rb') as stream:
        stream.seek(entry['offset'])
        blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
    return os.path.basename(tre), _inflate(blob, entry['comp'], entry['size'])


def main(args):
    planet = args[0] if args and not args[0].lstrip('-').replace('.', '').isdigit() else 'hoth'
    rest = [float(a) for a in args[1 if args and args[0] == planet else 0:]]
    tre, data = snapshot(planet)
    objects = iff_tool.ws_objects(data)
    top = [o for o in objects if o[1] == 0]  # world objects (parent 0); children are cells and their contents
    print(f'snapshot/{planet}.ws from {tre}: {len(objects)} objects, {len(top)} at world level')
    if len(rest) == 3:
        x, y, r = rest
        near = sorted((((o[3] - x) ** 2 + (o[5] - y) ** 2) ** 0.5, o) for o in top if ((o[3] - x) ** 2 + (o[5] - y) ** 2) ** 0.5 <= r)
        for d, o in near[:40]:
            print(f'  {d:6.0f} m  {o[2]}  at {o[3]:.0f} {o[5]:.0f} (height {o[4]:.0f})')
        return
    kinds = Counter(o[2] for o in top)
    for template, n in kinds.most_common():
        spots = [f'{o[3]:.0f} {o[5]:.0f}' for o in top if o[2] == template][:6]
        print(f'  {n:4d}  {template}   e.g. ' + '; '.join(spots))


if __name__ == '__main__':
    main(sys.argv[1:])
