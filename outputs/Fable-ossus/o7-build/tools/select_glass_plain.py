"""Select POI 17's centre inside the owner's foothill window, preserving its 600 x 300 m footprint.

Compare full-footprint relief on 25 m grids; break ties by proximity to the window centre,
then x/y. The census is sparse here, so record its terrain comparison rather than infer
flatness from a single truncated height. Read-only terrain/census; writes one o7 report.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from o7_common import Census, O7, Terrain, jsave


def main():
    terrain, census = Terrain(), Census()
    candidates = []
    for x in range(1850, 2451, 25):
        for y in range(-4800, -4499, 25):
            heights = [terrain.h(x + dx, y + dy)
                       for dx in range(-300, 301, 25) for dy in range(-150, 151, 25)]
            candidates.append((max(heights) - min(heights), abs(x - 2150) + abs(y + 4650),
                               x, y, min(heights), max(heights)))
    candidates.sort()
    relief, _, x, y, lo, hi = candidates[0]
    samples = [dict(r, terrain_z=round(terrain.h(r['x'], r['y']), 4)) for r in census.rows
               if 1850 <= r['x'] <= 2450 and -4800 <= r['y'] <= -4500]
    report = {
        'centre_window': [1850, -4800, 2450, -4500],
        'footprint_size_m': [600, 300], 'centre_grid_m': 25, 'footprint_grid_m': 25,
        'criterion': 'minimum full-rectangle max-minus-min height; ties: Manhattan distance to window centre, then x/y',
        'candidate_count': len(candidates), 'selected_centre': [x, y],
        'selected_rect': [x - 300, y - 150, x + 300, y + 150],
        'ground_min_m': lo, 'ground_max_m': hi, 'relief_m': relief,
        'census_samples_in_window': samples,
        'note': 'Centre constrained to owner window; footprint may extend beyond it. Census z is truncated; no terrain flattening.',
        'best_candidates': [{'centre': [r[2], r[3]], 'relief_m': r[0]} for r in candidates[:8]],
    }
    jsave(os.path.join(O7, 'out', 'glass-plain-selection.json'), report)
    print('POI 17 centre', (x, y), 'full-footprint relief %.4f m;' % relief, len(samples), 'census samples')
    return report


if __name__ == '__main__':
    main()
