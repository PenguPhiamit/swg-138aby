"""Analyse the Hoth height scan: the outpost bowl, its exits and flatter sites. (Claude, 14 Oct 2026.)

    python -I tools/hoth/hoth_terrain_analyse.py

Input: tools/hoth/data/hoth_heights.json (from hoth_terrain_scan.py: server-side terrain heights, 50 m grid within
1.5 km of the pad and 125 m out to 4 km). Output: tools/hoth/data/hoth_terrain_findings.json and
Documentation-support/hoth-terrain-map.png (height shading, steep ground in red, pad and candidate sites marked).
Plain Python plus Pillow; no other libraries.
"""
import json, math, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'data', 'hoth_heights.json')
OUT = os.path.join(HERE, 'data', 'hoth_terrain_findings.json')
PNG = os.path.join(HERE, '..', '..', 'Documentation-support', 'hoth-terrain-map.png')
SITE_RADIUS = 150      # m: room for a starport and its no-spawn circle's core
SITE_RANGE_MAX = 6.0   # m: highest-lowest point allowed inside SITE_RADIUS
STEEP = 0.30           # grade: 30 % counts as a wall for walking


def load():
    d = json.load(open(SRC))
    return d, {(x, y): z for x, y, z in d['points']}


def nearest(h, x, y, step):
    gx, gy = round((x - PAD[0]) / step) * step + PAD[0], round((y - PAD[1]) / step) * step + PAD[1]
    return h.get((round(gx), round(gy)))


def grade_at(h, x, y, step):
    z = h.get((x, y))
    if z is None:
        return None
    g = 0.0
    for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
        n = h.get((x + dx, y + dy))
        if n is not None:
            g = max(g, abs(n - z) / step)
    return g


def main():
    global PAD
    d, h = load()
    PAD = tuple(d['pad'])
    fine = {k: v for k, v in h.items() if (k[0] - round(PAD[0])) % 50 == 0 and (k[1] - round(PAD[1])) % 50 == 0
            and abs(k[0] - PAD[0]) <= 1501 and abs(k[1] - PAD[1]) <= 1501}
    pad_z = h.get((round(PAD[0]), round(PAD[1])), 0.0)

    # 1. The bowl: 16 directions from the pad, out to 1.5 km on the 50 m grid.
    rays = []
    for i in range(16):
        a = math.radians(i * 22.5)
        prof, worst, wall_at, rise_500 = [], 0.0, None, None
        prev = pad_z
        for r in range(50, 1501, 50):
            z = nearest(fine, PAD[0] + r * math.sin(a), PAD[1] + r * math.cos(a), 50)
            if z is None:
                break
            g = abs(z - prev) / 50
            worst = max(worst, g)
            if wall_at is None and g >= STEEP:
                wall_at = r
            if r == 500:
                rise_500 = round(z - pad_z, 1)
            prof.append((r, round(z, 1)))
            prev = z
        rays.append(dict(bearing=i * 22.5, rise_at_500m=rise_500, steepest_grade_pct=round(worst * 100),
                         first_wall_at_m=wall_at, profile=prof))
    exits = sorted(rays, key=lambda r: (r['first_wall_at_m'] is not None, r['steepest_grade_pct']))

    # 2. Flat sites on the 50 m grid (fine area) and the 125 m grid (out to 4 km).
    sites = []
    for step, grid in ((50, fine), (125, h)):
        for (x, y), z in grid.items():
            if (x - round(PAD[0])) % step or (y - round(PAD[1])) % step:
                continue
            zs = [grid[(x + dx, y + dy)] for dx in range(-SITE_RADIUS, SITE_RADIUS + 1, step)
                  for dy in range(-SITE_RADIUS, SITE_RADIUS + 1, step)
                  if dx * dx + dy * dy <= SITE_RADIUS ** 2 and (x + dx, y + dy) in grid]
            if len(zs) < 5:
                continue
            spread = max(zs) - min(zs)
            if spread > SITE_RANGE_MAX:
                continue
            # openness: how far the ground stays walkable (< STEEP) in 8 directions, up to 800 m
            open_m = []
            for i in range(8):
                a = math.radians(i * 45)
                prev, reach = z, 0
                for r in range(step, 801, step):
                    n = nearest(grid, x + r * math.sin(a), y + r * math.cos(a), step)
                    if n is None or abs(n - prev) / step >= STEEP:
                        break
                    reach, prev = r, n
                open_m.append(reach)
            dist = math.hypot(x - PAD[0], y - PAD[1])
            sites.append(dict(x=x, y=y, z=round(z, 1), spread_m=round(spread, 1), grid_m=step,
                              walkable_reach_m=sorted(open_m), min_reach_m=min(open_m), distance_from_pad_m=round(dist)))
    # keep distinct sites: best first by openness then flatness; drop any within 400 m of a better one
    sites.sort(key=lambda s: (-s['min_reach_m'], s['spread_m'], s['distance_from_pad_m']))
    picked = []
    for s in sites:
        if all(math.hypot(s['x'] - p['x'], s['y'] - p['y']) > 400 for p in picked):
            picked.append(s)
        if len(picked) == 10:
            break
    pad_site = min(sites, key=lambda s: math.hypot(s['x'] - PAD[0], s['y'] - PAD[1])) if sites else None

    json.dump(dict(pad=PAD, pad_z=pad_z, points=len(h), exits=exits, best_sites=picked,
                   the_pad_as_a_site=pad_site), open(OUT, 'w'), indent=1)

    # 3. Map image of the fine 3 km square (the coarse ring is only partly sampled): heights shaded, steep cells red.
    xs = [k[0] for k in fine]; ys = [k[1] for k in fine]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = 25
    w, ht = (x1 - x0) // scale + 1, (y1 - y0) // scale + 1
    zmin, zmax = min(fine.values()), max(fine.values())
    img = Image.new('RGB', (w, ht), (20, 20, 30))
    px = img.load()
    for (x, y), z in fine.items():
        step = 50
        g = grade_at(fine, x, y, step) or 0
        shade = int(60 + 180 * (z - zmin) / max(zmax - zmin, 1))
        col = (min(255, shade + 90), max(0, shade - 60), max(0, shade - 60)) if g >= STEEP else (shade, shade, min(255, shade + 25))
        cx, cy = (x - x0) // scale, (y1 - y) // scale
        half = step // scale // 2
        for i in range(-half, half + 1):
            for j in range(-half, half + 1):
                if 0 <= cx + i < w and 0 <= cy + j < ht:
                    px[cx + i, cy + j] = col
    zoom = 6
    img = img.resize((w * zoom, ht * zoom), Image.NEAREST)
    dr = ImageDraw.Draw(img)

    def mark(x, y, color, r=7, label=None):
        cx, cy = (x - x0) / scale * zoom, (y1 - y) / scale * zoom
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
        if label:
            dr.text((cx + r + 2, cy - r - 2), label, fill=color)
    mark(PAD[0], PAD[1], (255, 255, 0), 7, 'pad')
    for n, s in enumerate(picked, 1):
        mark(s['x'], s['y'], (0, 255, 120), 6, str(n))
    dr.text((6, 6), f'Hoth around the outpost: {x1 - x0} m square, north up, darker = lower ({zmin:.0f}-{zmax:.0f} m).',
            fill=(255, 255, 255))
    dr.text((6, 20), 'Red = 30%+ grade. Yellow = landing pad. Green = flat, open sites (numbers as in the findings).',
            fill=(255, 255, 255))
    bar = 500 / scale * zoom  # 500 m scale bar
    dr.line([(10, img.height - 14), (10 + bar, img.height - 14)], fill=(255, 255, 255), width=3)
    dr.text((14 + bar, img.height - 22), '500 m', fill=(255, 255, 255))
    os.makedirs(os.path.dirname(PNG), exist_ok=True)
    img.save(PNG)

    print(f'{len(h)} points; pad z {pad_z}; height range {zmin:.0f}..{zmax:.0f} m')
    print('gentlest exits from the pad (bearing, first wall, steepest grade, rise at 500 m):')
    for r in exits[:6]:
        print(f"  {r['bearing']:5.1f} deg  wall {r['first_wall_at_m']}  max {r['steepest_grade_pct']}%  rise500 {r['rise_at_500m']}")
    print('steepest directions:')
    for r in exits[-4:]:
        print(f"  {r['bearing']:5.1f} deg  wall {r['first_wall_at_m']}  max {r['steepest_grade_pct']}%  rise500 {r['rise_at_500m']}")
    print('best flat, open sites:')
    for n, s in enumerate(picked, 1):
        print(f"  {n}. ({s['x']}, {s['y']}) z {s['z']}  spread {s['spread_m']} m  min walkable reach {s['min_reach_m']} m  "
              f"{s['distance_from_pad_m']} m from pad")
    print('the pad area itself:', pad_site and {k: pad_site[k] for k in ('spread_m', 'min_reach_m', 'walkable_reach_m')})
    print('wrote', OUT, 'and', os.path.normpath(PNG))


if __name__ == '__main__':
    main()
