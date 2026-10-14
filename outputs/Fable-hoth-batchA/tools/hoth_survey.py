"""Coarse survey of MTG's Hoth terrain for siting spawn areas: height and local slope on a grid, plus a check of
candidate area centres. Uses the Core3 height port in ../../Fable-planet-test/tools/trn_read.py (validated against
the server's Hoth heights). Our own code (Fable, 14 Oct 2026).

    python -I hoth_survey.py grid [step]            # text map of heights (and steep cells) over the whole planet
    python -I hoth_survey.py check x y r [x y r ...] # mean height, max 100 m slope and max height inside each circle
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'Fable-planet-test', 'tools'))
import trn_read  # noqa: E402
from trn_iff import client_file  # noqa: E402

_ev = None


def evaluator():
    global _ev
    if _ev is None:
        _ev = trn_read.HeightEvaluator(trn_read.read_trn(client_file('terrain/hoth.trn')), trn_read.client_bitmap_loader)
    return _ev


def grid(step):
    ev = evaluator()
    half = 8192
    ys = list(range(half - step // 2, -half, -step))
    xs = list(range(-half + step // 2, half, step))
    print(f'height grid, {step} m cells; each cell: mean height (m) of 4 samples, "!" if any 100 m step inside exceeds 35 m (too steep)')
    print('       ' + ''.join(f'{x:>6d}' for x in xs))
    for y in ys:
        row = []
        for x in xs:
            pts = [(x - step / 4, y - step / 4), (x + step / 4, y - step / 4), (x - step / 4, y + step / 4), (x + step / 4, y + step / 4)]
            hs = [ev.height(px, py) for px, py in pts]
            steep = any(abs(ev.height(px + 100, py) - h) > 35 or abs(ev.height(px, py + 100) - h) > 35 for (px, py), h in zip(pts, hs))
            row.append(f'{sum(hs) / 4:5.0f}' + ('!' if steep else ' '))
        print(f'{y:>6d} ' + ''.join(row))


def check(circles):
    ev = evaluator()
    for cx, cy, r in circles:
        hs, slopes = [], []
        for i in range(-4, 5):
            for j in range(-4, 5):
                x, y = cx + i * r / 4, cy + j * r / 4
                if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                    continue
                h = ev.height(x, y)
                hs.append(h)
                slopes.append(max(abs(ev.height(x + 100, y) - h), abs(ev.height(x, y + 100) - h)))
        print(f'circle ({cx:.0f}, {cy:.0f}) r {r:.0f}: mean {sum(hs) / len(hs):.1f} m, min {min(hs):.1f}, max {max(hs):.1f}, '
              f'steepest 100 m step {max(slopes):.1f} m, samples {len(hs)}')


def main(argv):
    if argv[:1] == ['grid']:
        grid(int(argv[1]) if len(argv) > 1 else 1024)
        return 0
    if argv[:1] == ['check']:
        vals = [float(v) for v in argv[1:]]
        check(list(zip(vals[::3], vals[1::3], vals[2::3])))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
