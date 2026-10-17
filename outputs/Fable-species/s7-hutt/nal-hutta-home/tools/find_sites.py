"""Search the Bilbousa shelf for clear, flat spots for a footprint (diagnostic; prints only)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hutta_common import existing_footprints, Terrain, obb, poly_overlap, TOWN_CENTRE
tpl = sys.argv[1]; r = float(sys.argv[2]); box = [float(v) for v in sys.argv[3].split(',')]; step = float(sys.argv[4]) if len(sys.argv) > 4 else 10
fp = existing_footprints(pad=3.0)
t = Terrain()
res = []
y = box[2]
while y <= box[3]:
    x = box[0]
    while x <= box[1]:
        poly = obb(tpl, x, y, 0, 2.0)
        if not any(poly_overlap(poly, f[5]) for f in fp if 'lamp' not in f[1]):
            lo, hi = t.disc(x, y, r, step=r / 4)
            if lo >= 79.0 and hi - lo <= 2.5:
                lamps = sum(1 for f in fp if 'lamp' in f[1] and poly_overlap(poly, f[5]))
                res.append((round(hi - lo, 2), x, y, round(lo, 1), round(hi, 1), lamps, round(math.hypot(x - TOWN_CENTRE[0], y - TOWN_CENTRE[1]))))
        x += step
    y += step
res.sort()
for row in res[:40]:
    print(row)
print(len(res), 'sites')
