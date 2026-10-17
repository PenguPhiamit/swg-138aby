"""O11: open the three O7 flatland cave mouths (Claude, 17 Oct 2026; owner's report on run 28, 10:05 AM).

The stock flatland caves (cave_06/07/08_flatland) are a rock mound standing on flat ground: the r0 (outside) floor
is the mound's surface (up to 29 m high), and the first cell (r1) starts at the mouth (portal 0, building space
z = 18, floor at the ground) and goes down under the mound, 12-33 m below the ground. The planet's ground carries on
inside the mound, so it cuts across that first tunnel: the owner sees grass in the opening and walks down "through"
it. SWG terrain has no holes, so the fix is a pit in the terrain, only where the mound's shell covers it:
  - each cave's r0 floor (the shell) and r1 floor (from its .pob), placed in the world with its snapshot node;
  - a 1 m world grid; a cell is cut when the shell lies more than SHELL_ABOVE m above the current ground at every
    sample of the cell grown by EDGE m (so the cut stays under the shell, clear of its sloping sides), and the whole
    grown cell lies behind the mouth (building space z < MOUTH_Z - MOUTH_GAP), so nothing is cut in front of the portal;
  - the cut cells, merged into rows of world-aligned rectangles (BREC, no feather), make one layer per cave
    with one affector: the height set (AHCN op 0) to PIT_MARGIN m below the lowest point of that cave's r1 floor.
The layers go after the O7 layers (tools/o7_terrain.py with this spec added), so nothing else in the terrain changes:
the step checks that the three TGAs stay identical, that the height changes only inside the rectangles (whole-planet
grid), and that no bowl floor point is left under the ground (survey_caves.py before and after).
  changed  terrain/ossus.trn   (every other entry of the base byte for byte)
  changed  snapshot/ossus.ws   the O7 props that stood on the old false ground inside a bowl move out, along the line from
                               the bowl's middle, to the first point PROP_CLEAR m clear of every pit rectangle, at the ground
                               height there (unchanged ground); everything else in the snapshot is untouched
The same rule gives the new places of the two adit NPCs, which the server patch (server/) moves.

    C:/Users/Pengw/miniconda3/python.exe -I build_cave_mouths.py [--base PATH] [--out PATH]
Default base: ../../../work/chain-run28/local_planets-run28.tre (installed on run 28, sha256 b103e36f...).
Default out:  ../../../work/ossus-cave-mouths/local_planets-cave-mouths.tre (+ .sha256), checks in ./checks-cave-mouths.json.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OSSUS = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OSSUS)
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OSSUS, 'o7-build', 'tools'))
from swgfmt import tre_write  # noqa: E402
import o7_terrain  # noqa: E402
from o7_common import Terrain, jload, rot  # noqa: E402
import survey_caves as sc  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'chain-run28', 'local_planets-run28.tre')
DEFAULT_BASE_SHA_PREFIX = 'b103e36f'
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-cave-mouths', 'local_planets-cave-mouths.tre')
O7_TRN_SHA = '05c570f2f241d799e72bf162c844dc1d9fe00c27cc05f7cbb16e28bc9fc50f5c'
TRN = 'terrain/ossus.trn'
TGAS = ('terrain/ossus_academy.tga', 'terrain/ossus_canyon.tga', 'terrain/ossus_mesa.tga')
CELL = 1.0          # m, world grid
SHELL_ABOVE = 2.0   # m: the mound's surface must be this far above the ground for the cell to be cut
EDGE = 0.75         # m: each cell is tested grown by this much on every side
MOUTH_GAP = 0.5     # m: the grown cell must stay this far behind the mouth
MOUTH_Z = 18.0      # building space z of portal 0 (the mouth); the cut stays behind it
PIT_MARGIN = 2.0    # m below the lowest point of the first cell's floor
SUNK = 0.5          # m: for the before/after survey of the first cell's floor
PROP_CLEAR = 2.5    # m between a moved prop's origin and the nearest pit rectangle
WS = 'snapshot/ossus.ws'
NPCS = {'ossus_adit_foreman': (4590.0, -310.0), 'miner': (4596.0, -304.0)}   # screenplays/sandbox/ossus_people.lua


def floor_lookup(template):
    """A function (local x, local z) -> the highest r0 floor y there (the mound's surface), or None."""
    _, _, verts, tris = sc.r0_floor(template)
    boxes = []
    for a, b, c in tris:
        p, q, r = verts[a], verts[b], verts[c]
        boxes.append((min(p[0], q[0], r[0]), max(p[0], q[0], r[0]), min(p[2], q[2], r[2]), max(p[2], q[2], r[2]), p, q, r))

    def at(x, z):
        best = None
        for x0, x1, z0, z1, p, q, r in boxes:
            if x < x0 or x > x1 or z < z0 or z > z1:
                continue
            d = (q[2] - r[2]) * (p[0] - r[0]) + (r[0] - q[0]) * (p[2] - r[2])
            if abs(d) < 1e-9:
                continue
            l1 = ((q[2] - r[2]) * (x - r[0]) + (r[0] - q[0]) * (z - r[2])) / d
            l2 = ((r[2] - p[2]) * (x - r[0]) + (p[0] - r[0]) * (z - r[2])) / d
            l3 = 1 - l1 - l2
            if min(l1, l2, l3) < -1e-6:
                continue
            y = l1 * p[1] + l2 * q[1] + l3 * r[1]
            best = y if best is None else max(best, y)
        return best
    return at, min(v[1] for v in verts), verts


def to_local(o, wx, wy):
    """World (east, north) to building space (x, z): the inverse of o7_common.rot."""
    dx, dy = wx - o['x'], wy - o['y']
    h = math.radians(o['yaw'])
    return dx * math.cos(h) - dy * math.sin(h), dx * math.sin(h) + dy * math.cos(h)


def cut_cells(o, terrain, at, verts):
    xs, zs = [], []
    for vx, vy, vz in verts:
        ex, ny = rot(vx, vz, o['yaw'])
        xs.append(o['x'] + ex)
        zs.append(o['y'] + ny)
    x0, x1 = math.floor(min(xs) / CELL) * CELL, math.ceil(max(xs) / CELL) * CELL
    y0, y1 = math.floor(min(zs) / CELL) * CELL, math.ceil(max(zs) / CELL) * CELL
    cells = set()
    gx = x0
    while gx < x1:
        gy = y0
        while gy < y1:
            ok = True
            for fx in (-EDGE, CELL / 2, CELL + EDGE):
                for fy in (-EDGE, CELL / 2, CELL + EDGE):
                    px, py = gx + fx, gy + fy
                    lx, lz = to_local(o, px, py)
                    f = at(lx, lz)
                    if f is None or lz > MOUTH_Z - MOUTH_GAP or o['z'] + f < terrain.h(px, py) + SHELL_ABOVE:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                cells.add((round(gx, 3), round(gy, 3)))
            gy += CELL
        gx += CELL
    return cells


def rows_to_rects(cells):
    """Merge each row's runs of cells into rectangles (x0, y0, x1, y1)."""
    rects = []
    for gy in sorted({c[1] for c in cells}):
        xs = sorted(c[0] for c in cells if c[1] == gy)
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and abs(x - prev - CELL) < 1e-6:
                prev = x
                continue
            rects.append((start, gy, prev + CELL, gy + CELL))
            if x is not None:
                start = prev = x
    return rects


def in_rects(rects, x, y, pad=0.0):
    return any(r[0] - pad <= x <= r[2] + pad and r[1] - pad <= y <= r[3] + pad for r in rects)


def push_out(rects, x, y, pad):
    """The first point clear of the rectangles by pad, walking away from their middle in 0.25 m steps."""
    cx = sum((r[0] + r[2]) / 2 for r in rects) / len(rects)
    cy = sum((r[1] + r[3]) / 2 for r in rects) / len(rects)
    dx, dy = x - cx, y - cy
    d = math.hypot(dx, dy) or 1.0
    dx, dy = dx / d, dy / d
    t = 0.0
    while in_rects(rects, x + dx * t, y + dy * t, pad):
        t += 0.25
    return round(x + dx * t, 2), round(y + dy * t, 2), round(t, 2)


def move_props(ws_bytes, report, terrain):
    sys.path.insert(0, os.path.join(OSSUS, 'o2', 'tools'))
    import ws_write  # noqa: E402
    import ws_read  # noqa: E402
    nodes, templates = ws_read.read_ws(ws_bytes)
    assert ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(ws_bytes)[0]), templates) == ws_bytes
    statics = json.load(open(os.path.join(OSSUS, 'o7-build', 'statics.json'), encoding='utf-8'))
    kinds = {o['id']: (o['kind'], o['role']) for o in statics['objects']}
    moved = []
    for n in nodes:
        if n['depth'] != 0 or n['id'] not in kinds or kinds[n['id']][0] == 'building':
            continue
        for name, v in report.items():
            if in_rects(v['rects'], n['x'], n['y'], 1.0):
                nx, ny, t = push_out(v['rects'], n['x'], n['y'], PROP_CLEAR)
                nz = round(terrain.h(nx, ny), 2)
                moved.append({'id': n['id'], 'role': kinds[n['id']][1], 'cave': name.split(' ')[0], 'from': [round(n['x'], 2), round(n['y'], 2), round(n['z'], 2)],
                              'to': [nx, ny, nz], 'moved_m': t})
                n['x'], n['y'], n['z'] = nx, ny, nz
                break
    out = ws_write.write_ws(ws_write.tree_from_reader(nodes), templates)
    back, _ = ws_read.read_ws(out)
    assert len(back) == len(nodes) and ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(out)[0]), templates) == out
    return out, moved


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the run-28 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    assert sha(base[TRN]) == O7_TRN_SHA, 'the base terrain is not the O7 one; rebuild the O7 spec first'

    before, _ = sc.load_terrain(base_bytes)
    nodes = sc.cave_nodes()
    layers, report = [], {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        at, _, verts = floor_lookup(o['template'])
        cells = cut_cells(o, before, at, verts)
        rects = rows_to_rects(cells)
        r1 = sc.cell_floor(o['template'], 1)
        ymin = min(v[1] for v in r1)
        pit = round(o['z'] + ymin - PIT_MARGIN, 2)
        key = name.split(' ')[0]
        layers.append({'name': 'o11 %s mouth pit' % key,
                       'boundaries': [{'type': 'BREC', 'name': '%s %d' % (key, i), 'x0': r[0], 'y0': r[1], 'x1': r[2], 'y1': r[3],
                                       'feather_type': 3, 'feather': 0.0} for i, r in enumerate(rects)],
                       'affectors': [{'type': 'AHCN', 'name': 'pit', 'op': 0, 'height': pit}]})
        report[name] = {'cells': len(cells), 'area_m2': len(cells) * CELL * CELL, 'rectangles': len(rects), 'pit_height_m': pit,
                        'node_z': o['z'], 'r1_lowest_floor_m': round(o['z'] + ymin, 2), 'rects': rects}

    spec = jload(o7_terrain.TERRAIN_JSON)
    spec2 = copy.deepcopy(spec)
    spec2['layers'] = spec['layers'] + layers
    tmp = tempfile.mkdtemp(prefix='o11-build-')
    spec_path = os.path.join(tmp, 'terrain-o11.json')
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(spec2, f)
    keep = o7_terrain.TERRAIN_JSON
    o7_terrain.TERRAIN_JSON = spec_path
    try:
        rep = o7_terrain.build(tmp, with_layers=True, quiet=True)
    finally:
        o7_terrain.TERRAIN_JSON = keep
    assert rep.get('verdict') == 'PASS', rep.get('verdict')
    stage = os.path.join(tmp, 'staged', 'client')
    trn = open(os.path.join(stage, 'terrain', 'ossus.trn'), 'rb').read()
    for t in TGAS:
        assert open(os.path.join(stage, *t.split('/')), 'rb').read() == base[t], t

    files = dict(base)
    files[TRN] = trn
    after, _ = sc.load_terrain(tre_write.pack(files))
    ws, moved = move_props(base[WS], report, after)
    if moved:
        files[WS] = ws
    npcs = {}
    for tpl, (x, y) in NPCS.items():
        for name, v in report.items():
            if in_rects(v['rects'], x, y, 1.0):
                nx, ny, t = push_out(v['rects'], x, y, PROP_CLEAR)
                npcs[tpl] = {'from': [x, y], 'to': [nx, ny], 'ground': round(after.h(nx, ny), 2), 'moved_m': t}
    out = tre_write.pack(files)

    # 1. the first cell's floor: how much of it the ground covers, before and after
    bowls = {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        r1 = sc.cell_floor(o['template'], 1)
        res = {}
        for label, t in (('before', before), ('after', after)):
            under = []
            for vx, vy, vz in r1:
                ex, ny = rot(vx, vz, o['yaw'])
                wx, wy = o['x'] + ex, o['y'] + ny
                g = t.h(wx, wy)
                if g > o['z'] + vy + SUNK and vz < MOUTH_Z:
                    under.append({'local': [round(vx, 2), round(vy, 2), round(vz, 2)], 'ground_above_floor_m': round(g - o['z'] - vy, 2)})
            res[label] = under
        bowls[name] = {'r1_floor_vertices': len(r1), 'under_ground_before': len(res['before']), 'under_ground_after': len(res['after']),
                       'worst_after_m': max((u['ground_above_floor_m'] for u in res['after']), default=0.0),
                       'still_under_examples': res['after'][:8]}

    # 2. nothing else moved: a whole-planet grid and a ring around each cave
    rects = [r for v in report.values() for r in v['rects']]

    def inside(x, y):
        return any(r[0] - 1e-6 <= x <= r[2] + 1e-6 and r[1] - 1e-6 <= y <= r[3] + 1e-6 for r in rects)
    changed_out = changed_in = n = 0
    worst_out = 0.0
    step = 96.0
    x = -8192 + step / 2
    while x < 8192:
        y = -8192 + step / 2
        while y < 8192:
            n += 1
            d = abs(after.h(x, y) - before.h(x, y))
            if d > 1e-4:
                if inside(x, y):
                    changed_in += 1
                else:
                    changed_out += 1
                    worst_out = max(worst_out, d)
            y += step
        x += step
    near = {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        shifted, worst, samples = 0, 0.0, 0
        for gx in range(int(o['x'] - 120), int(o['x'] + 121), 1):
            for gy in range(int(o['y'] - 120), int(o['y'] + 121), 1):
                if inside(gx, gy) or inside(gx + 0.5, gy + 0.5):
                    continue
                # cells next to a rectangle blend through the terrain's own sampling; count them apart
                samples += 1
                d = abs(after.h(gx, gy) - before.h(gx, gy))
                if d > 1e-3:
                    shifted += 1
                    worst = max(worst, d)
        near[name] = {'samples_outside_rects_within_120m': samples, 'moved_over_1mm': shifted, 'worst_m': round(worst, 3)}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))
    ours = tre_write.read(out)[0]
    changed = sorted(k for k in base if k in ours and base[k] != ours[k])
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'sha256': base_sha, 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha, 'entries': len(ours)},
        'untouched_identical': len(base) - len(changed), 'changed': changed,
        'trn': {'before_sha256': sha(base[TRN]), 'after_sha256': sha(trn), 'bytes_before': len(base[TRN]), 'bytes_after': len(trn)},
        'settings': {'cell_m': CELL, 'shell_above_m': SHELL_ABOVE, 'edge_m': EDGE, 'mouth_z': MOUTH_Z, 'mouth_gap_m': MOUTH_GAP, 'pit_margin_m': PIT_MARGIN},
        'pits': {k: {kk: vv for kk, vv in v.items() if kk != 'rects'} for k, v in report.items()},
        'bowls': bowls,
        'planet_grid': {'step_m': step, 'samples': n, 'changed_inside_rects': changed_in, 'changed_outside_rects': changed_out,
                        'worst_outside_m': round(worst_out, 4)},
        'near_caves_1m_grid': near,
        'props_moved': moved, 'npcs_to_move': npcs,
        'rects': {k: v['rects'] for k, v in report.items()},
    }
    with open(os.path.join(HERE, 'checks-cave-mouths.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    assert changed == sorted([TRN] + ([WS] if moved else [])), changed
    print(json.dumps({k: checks[k] for k in ('out', 'untouched_identical', 'changed', 'pits', 'planet_grid', 'near_caves_1m_grid', 'npcs_to_move')}, indent=1))
    for m in moved:
        print('moved', m['id'], m['role'], m['from'], '->', m['to'], '%.2f m' % m['moved_m'])
    for k, v in bowls.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != 'still_under_examples'})
    print('Cave mouths step: built (read the bowl and near-cave checks above)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
