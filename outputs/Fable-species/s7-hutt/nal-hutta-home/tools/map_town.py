"""ASCII map of Bilbousa's footprints and ground (diagnostic; prints only)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hutta_common import existing_footprints, Terrain, circle_poly_overlap
fp = existing_footprints()
t = Terrain()
x0, x1, y0, y1, s = -1180, -280, 1180, 2020, 10
for y in range(y1, y0 - 1, -s):
    row = ''
    for x in range(x0, x1 + 1, s):
        hit = [f for f in fp if circle_poly_overlap(x, y, s / 2, f[5])]
        if hit:
            tpl = hit[0][1]
            c = 'L' if 'lamp' in tpl else 'b' if 'banner' in tpl else 't' if 'tent' in tpl else 'T' if 'tower' in tpl else 'W' if 'wall' in tpl else 'B'
        else:
            h = t.h(x, y)
            c = '~' if h < 75 else '.' if h < 79.5 else ' ' if h <= 82.5 else '^'
        row += c
    print('%5d %s' % (y, row))
print('      ' + ''.join(str(abs(x) // 100 % 10) if x % 100 == 0 else ' ' for x in range(x0, x1 + 1, s)))
