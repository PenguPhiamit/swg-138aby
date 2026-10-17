"""PL-06: find dry, flat ground in the Nal Hutta swamp for the places to find (diagnostic; writes sites.json).
Uses PL-04's terrain reader (nal-hutta-home/tools/hutta_common.py: hutta.trn through Fable's Core3 port). For each of
eight compass sectors and a distance band, keeps the flattest dry disc of radius R (lowest point >= 77 m, two metres
above the 75 m water; relief <= 2.5 m). No terrain edits.
    C:/Users/Pengw/miniconda3/python.exe -I find_swamp_sites.py
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'nal-hutta-home', 'tools'))
from hutta_common import Terrain, TOWN_CENTRE  # noqa: E402

R, STEP, BAND = 22.0, 40.0, (750.0, 2600.0)
t = Terrain()
best = {}
cx, cy = TOWN_CENTRE
for gy in range(int(cy - BAND[1]), int(cy + BAND[1]) + 1, int(STEP)):
    for gx in range(int(cx - BAND[1]), int(cx + BAND[1]) + 1, int(STEP)):
        d = math.hypot(gx - cx, gy - cy)
        if not BAND[0] <= d <= BAND[1] or abs(gx) > 7500 or abs(gy) > 7500:
            continue
        lo, hi = t.disc(gx, gy, R, step=R / 3)
        if lo < 77.0 or hi - lo > 2.5:
            continue
        sector = int(((math.degrees(math.atan2(gx - cx, gy - cy)) + 360 + 22.5) % 360) // 45)
        key = (sector, 'near' if d < 1600 else 'mid')
        cand = (round(hi - lo, 2), gx, gy, round(lo, 1), round(hi, 1), round(d))
        if key not in best or cand < best[key]:
            best[key] = cand
rows = [{'sector': 'N NE E SE S SW W NW'.split()[k[0]], 'band': k[1], 'relief': v[0], 'x': v[1], 'y': v[2], 'lo': v[3],
         'hi': v[4], 'dist': v[5]} for k, v in sorted(best.items())]
for r in rows:
    print(r)
json.dump(rows, open(os.path.join(HERE, '..', 'sites.json'), 'w'), indent=1)
