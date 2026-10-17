"""PL-06 shared helpers: Bilbousa's occupied ground (Darklight's snapshot plus PL-04's statics and people)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIFE = os.path.normpath(os.path.join(HERE, '..'))
HOME = os.path.normpath(os.path.join(LIFE, '..', 'nal-hutta-home'))
sys.path.insert(0, os.path.join(HOME, 'tools'))
from hutta_common import existing_footprints, obb, poly_overlap, TOWN_CENTRE  # noqa: E402,F401


def occupied(pad=1.5):
    """Polygons of every building and static in town, and PL-04's people as 1.5 m squares."""
    polys = [(f[1].split('/')[-1], f[5]) for f in existing_footprints(pad=pad)]
    home = json.load(open(os.path.join(HOME, 'home.json')))
    for s in home['statics']:
        polys.append((s['template'].split('/')[-1], obb(s['template'], s['x'], s['y'], s['yaw'], pad)))
    for p in home['people']:
        x, y = p['x'], p['y']
        polys.append(('pl04:' + p.get('key', p.get('template', '?')), square(x, y, 1.5)))
    t = home['trade_yard']
    polys.append(('trade_yard', obb(t['template'], t['x'], t['y'], 0, pad)))
    return polys


def square(x, y, r):
    return [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]


def blocked(polys, x, y, r=0.6):
    sq = square(x, y, r)
    return [n for n, p in polys if poly_overlap(sq, p)]


def segment_clear(polys, a, b, step=1.0):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    hits = set()
    for i in range(n + 1):
        x = a[0] + (b[0] - a[0]) * i / n
        y = a[1] + (b[1] - a[1]) * i / n
        hits.update(blocked(polys, x, y))
    return sorted(hits)
