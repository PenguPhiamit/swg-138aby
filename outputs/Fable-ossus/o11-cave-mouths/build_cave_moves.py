"""O11b: move the vault and adit flatland caves above the water (Claude, 17 Oct 2026; owner on run 29, about 12:00 PM:
"theres water there now, but i can still traverse").

O11's pits opened the first tunnels, but Ossus's global water table is 38.5 m: the vault's first tunnel bottoms out at
5.8 m and the adit's at 23.2 m, so the pits filled with water. The water table can't be lowered (5.4 % of the planet,
Adega Lake and the hamlet's pier, lie under it, and the vault would need it under 4 m), SWG terrain has no way to keep
water out of one spot, and raising the caves in place would need hills 35 m and 17 m high. So the two caves move, each with
its camp, to the nearest flat ground high enough for their tunnels (the mouth at least 77.3 m and 62.4 m):
  vault  POI 4, 20 objects:  (2299.7, 1907.0) -> VAULT_TO on the Academy Benchland (about 171 m), mouth to the north
  adit   POI 9, 17 objects:  (4578.1, -296.5) -> ADIT_TO on the mesa rim above Imhar Canyon (about 104 m)
Each group turns about its cave by the yaw change and moves with it; each object keeps its height above the ground
(the cave node: ground at the mouth - 3.85 m, as O7 placed it). The pits are cut as in build_cave_mouths.py, at the
new places (the sanctuary's stays as it is), on the O7 terrain, so the old vault and adit sites get their natural ground back.
  changed  terrain/ossus.trn, snapshot/ossus.ws    (every other entry of the base byte for byte)
The server patch (server/core3-dev-ossus-cave-moves.patch) moves what stands with them: the archivist, the foreman and
the miner, the vault's ghostfire site and its waypoint, the adit waypoint, and the two places' no-spawn circles.

    C:/Users/Pengw/miniconda3/python.exe -I build_cave_moves.py [--base PATH] [--out PATH]
Default base: ../../../work/ossus-cave-mouths/local_planets-cave-mouths.tre (installed on run 29, sha256 beb06d28...).
The O7 terrain without pits comes from ../../../work/chain-run28/local_planets-run28.tre (b103e36f...).
Default out: ../../../work/ossus-cave-moves/local_planets-cave-moves.tre (+ .sha256), checks in ./checks-cave-moves.json.
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
sys.path.insert(0, os.path.join(OSSUS, 'o2', 'tools'))
from swgfmt import tre_write  # noqa: E402
import o7_terrain  # noqa: E402
from o7_common import jload, rot  # noqa: E402
import survey_caves as sc  # noqa: E402
import build_cave_mouths as bm  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'ossus-cave-mouths', 'local_planets-cave-mouths.tre')
DEFAULT_BASE_SHA_PREFIX = 'beb06d28'
NATURAL = os.path.join(H, 'work', 'chain-run28', 'local_planets-run28.tre')
NATURAL_SHA_PREFIX = 'b103e36f'
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-cave-moves', 'local_planets-cave-moves.tre')
WATER = 38.5
MOUTH_LOCAL = (0.26, 18.0)   # portal 0's centre in building space (x, z), floor 3.85 m above the origin
# poi, cave node id, new (x, y), new yaw: the flattest ground above the need found by the grid search in README.md
MOVES = {
    'vault': {'poi': 4, 'node': 6900193, 'to': (1940.0, 2237.0), 'yaw': 0.0},
    'adit': {'poi': 9, 'node': 6900295, 'to': (4488.0, -206.0), 'yaw': None},   # None: the flattest of 24 headings
}
# points of the server patch that move with each group: (label, x, y)
POINTS = {
    'vault': [('archivist', 2302.0, 1987.0), ('ghostfire site and waypoint', 2300.0, 1925.0), ('no-spawn circle', 2300.0, 1960.0)],
    'adit': [('foreman', 4590.0, -310.0), ('miner', 4596.0, -304.0), ('adit waypoint', 4590.0, -310.0), ('no-spawn circle', 4600.0, -321.0)],
}


def quat(yaw):
    h = math.radians(yaw)
    return (math.cos(h / 2), 0.0, math.sin(h / 2), 0.0)


def transform(o_from, to, dyaw):
    """A function (x, y) -> (x, y): turn about the old cave node by dyaw (compass) and move it to `to`."""
    def f(x, y):
        dx, dy = x - o_from[0], y - o_from[1]
        # compass yaw: turning by d moves an offset (dx east, dy north) by -d in math angle
        a = -math.radians(dyaw)
        rx = dx * math.cos(a) - dy * math.sin(a)
        ry = dx * math.sin(a) + dy * math.cos(a)
        return to[0] + rx, to[1] + ry
    return f


def sha(b):
    return hashlib.sha256(b).hexdigest()


def plan_group(name, mv, statics, natural):
    objs = [o for o in statics['objects'] if o['poi'] == mv['poi']]
    cave = next(o for o in objs if o['id'] == mv['node'])
    yaws = [mv['yaw']] if mv['yaw'] is not None else [15.0 * k for k in range(24)]
    best = None
    for yaw in yaws:
        f = transform((cave['x'], cave['y']), mv['to'], yaw - cave['yaw'])
        spots = [f(o['x'], o['y']) for o in objs]
        mx, my = mv['to'][0] + rot(*MOUTH_LOCAL, yaw)[0], mv['to'][1] + rot(*MOUTH_LOCAL, yaw)[1]
        apron = [(mx + rot(0, d, yaw)[0], my + rot(0, d, yaw)[1]) for d in (5, 10, 20, 30)]
        hs = [natural.h(x, y) for x, y in spots + apron]
        spread = max(hs) - min(hs)
        if best is None or spread < best[0]:
            best = (spread, yaw, f)
    spread, yaw, f = best
    moved = []
    for o in objs:
        nx, ny = f(o['x'], o['y'])
        if o['id'] == mv['node']:
            mx, my = nx + rot(*MOUTH_LOCAL, yaw)[0], ny + rot(*MOUTH_LOCAL, yaw)[1]
            nz = natural.h(mx, my) - 3.85
        else:
            nz = o['z'] - natural.h(o['x'], o['y']) + natural.h(nx, ny)
        moved.append({'id': o['id'], 'role': o['role'], 'from': [o['x'], o['y'], o['z'], o['yaw']],
                      'to': [round(nx, 2), round(ny, 2), round(nz, 2), round((o['yaw'] + yaw - cave['yaw']) % 360, 1)]})
    return {'yaw': yaw, 'dyaw': yaw - cave['yaw'], 'ground_spread_m': round(spread, 2), 'objects': moved, 'f': f,
            'from_node': (cave['x'], cave['y'])}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the run-29 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    nat_bytes = open(NATURAL, 'rb').read()
    assert sha(nat_bytes).startswith(NATURAL_SHA_PREFIX)
    natural, nat_trn = sc.load_terrain(nat_bytes)
    assert nat_trn == bm.O7_TRN_SHA

    statics = json.load(open(os.path.join(OSSUS, 'o7-build', 'statics.json'), encoding='utf-8'))
    plans = {name: plan_group(name, mv, statics, natural) for name, mv in MOVES.items()}

    # the new cave nodes (and the sanctuary as it is) for the pits
    nodes = sc.cave_nodes()
    for name, mv in MOVES.items():
        to = next(m['to'] for m in plans[name]['objects'] if m['id'] == mv['node'])
        nodes[mv['node']] = dict(nodes[mv['node']], x=to[0], y=to[1], z=to[2], yaw=to[3])

    checks_need = {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        r1 = sc.cell_floor(o['template'], 1)
        low = o['z'] + min(v[1] for v in r1)
        checks_need[name] = {'node': [o['x'], o['y'], o['z'], o['yaw']], 'first_tunnel_bottom_m': round(low, 2),
                             'above_water_m': round(low - WATER, 2)}
        assert low - bm.PIT_MARGIN > WATER, (name, low)

    layers, report = [], {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        at, _, verts = bm.floor_lookup(o['template'])
        cells = bm.cut_cells(o, natural, at, verts)
        rects = bm.rows_to_rects(cells)
        r1 = sc.cell_floor(o['template'], 1)
        pit = round(o['z'] + min(v[1] for v in r1) - bm.PIT_MARGIN, 2)
        key = name.split(' ')[0]
        layers.append({'name': 'o11 %s mouth pit' % key,
                       'boundaries': [{'type': 'BREC', 'name': '%s %d' % (key, i), 'x0': r[0], 'y0': r[1], 'x1': r[2], 'y1': r[3],
                                       'feather_type': 3, 'feather': 0.0} for i, r in enumerate(rects)],
                       'affectors': [{'type': 'AHCN', 'name': 'pit', 'op': 0, 'height': pit}]})
        report[name] = {'cells': len(cells), 'area_m2': len(cells) * bm.CELL ** 2, 'rectangles': len(rects), 'pit_height_m': pit,
                        'pit_above_water_m': round(pit - WATER, 2), 'rects': rects}

    spec = jload(o7_terrain.TERRAIN_JSON)
    spec2 = copy.deepcopy(spec)
    spec2['layers'] = spec['layers'] + layers
    tmp = tempfile.mkdtemp(prefix='o11b-build-')
    spec_path = os.path.join(tmp, 'terrain-o11b.json')
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
    for t in bm.TGAS:
        assert open(os.path.join(stage, *t.split('/')), 'rb').read() == base[t], t

    # the snapshot: move the two groups
    import ws_write
    import ws_read
    ws_nodes, templates = ws_read.read_ws(base[bm.WS])
    by_id = {n['id']: n for n in ws_nodes}
    for name, p in plans.items():
        for m in p['objects']:
            n = by_id[m['id']]
            n['x'], n['y'], n['z'] = m['to'][0], m['to'][1], m['to'][2]
            n['quat'] = quat(m['to'][3])
    ws = ws_write.write_ws(ws_write.tree_from_reader(ws_nodes), templates)
    back, _ = ws_read.read_ws(ws)
    assert len(back) == len(ws_nodes)
    assert ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(ws)[0]), templates) == ws

    files = dict(base)
    files[bm.TRN], files[bm.WS] = trn, ws
    out = tre_write.pack(files)
    after, _ = sc.load_terrain(out)

    # checks: the tunnels, the water, the old sites back to natural, nothing else changed
    tunnels = {}
    for nid, name in sc.CAVES.items():
        o = nodes[nid]
        r1 = sc.cell_floor(o['template'], 1)
        under, shallow, wet = 0, 0, 0
        for vx, vy, vz in r1:
            ex, ny = rot(vx, vz, o['yaw'])
            wx, wy = o['x'] + ex, o['y'] + ny
            g = after.h(wx, wy) - (o['z'] + vy)
            if g > bm.SUNK:
                under += 1
                if g < 10:
                    shallow += 1
            if after.h(wx, wy) < WATER:
                wet += 1
        tunnels[name] = {'r1_floor_vertices': len(r1), 'under_ground_after': under, 'shallow_under_10m_after': shallow,
                         'ground_under_water_over_tunnel': wet}
    rects = [r for v in report.values() for r in v['rects']]
    changed_out = n = 0
    worst = 0.0
    x = -8192 + 48.0
    while x < 8192:
        y = -8192 + 48.0
        while y < 8192:
            n += 1
            if not bm.in_rects(rects, x, y):
                d = abs(after.h(x, y) - natural.h(x, y))
                if d > 1e-4:
                    changed_out += 1
                    worst = max(worst, d)
            y += 96.0
        x += 96.0
    old_sites = {}
    for name, (ox, oy) in (('vault', (2299.7, 1907.0)), ('adit', (4578.1, -296.5))):
        diff = max(abs(after.h(ox + dx, oy + dy) - natural.h(ox + dx, oy + dy)) for dx in range(-60, 61, 2) for dy in range(-60, 61, 2))
        lowest = min(after.h(ox + dx, oy + dy) for dx in range(-60, 61, 2) for dy in range(-60, 61, 2))
        old_sites[name] = {'max_change_from_natural_within_60m': round(diff, 4), 'lowest_ground_within_60m': round(lowest, 2)}
    groups = {}
    for name, p in plans.items():
        hs = [after.h(m['to'][0], m['to'][1]) for m in p['objects']]
        groups[name] = {'yaw': p['yaw'], 'turned_by_deg': round(p['dyaw'] % 360, 1), 'ground_spread_over_group_m': p['ground_spread_m'],
                        'ground_min_m': round(min(hs), 2), 'objects': p['objects']}
    points = {}
    for name, pts in POINTS.items():
        f = plans[name]['f']
        points[name] = [{'what': lab, 'from': [x0, y0], 'to': [round(f(x0, y0)[0], 1), round(f(x0, y0)[1], 1)]} for lab, x0, y0 in pts]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as fh:
        fh.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as fh:
        fh.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))
    ours = tre_write.read(out)[0]
    changed = sorted(k for k in base if k in ours and base[k] != ours[k])
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'sha256': base_sha, 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha, 'entries': len(ours)},
        'untouched_identical': len(base) - len(changed), 'changed': changed,
        'trn_sha256': sha(trn), 'caves': checks_need,
        'pits': {k: {kk: vv for kk, vv in v.items() if kk != 'rects'} for k, v in report.items()},
        'tunnels_after': tunnels,
        'planet_grid_vs_natural_outside_pits': {'samples': n, 'changed': changed_out, 'worst_m': round(worst, 4)},
        'old_sites': old_sites, 'groups': groups, 'server_points': points,
    }
    with open(os.path.join(HERE, 'checks-cave-moves.json'), 'w', encoding='utf-8') as fh:
        json.dump(checks, fh, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    assert changed == sorted([bm.TRN, bm.WS]), changed
    print(json.dumps({k: checks[k] for k in ('out', 'untouched_identical', 'changed', 'caves', 'pits', 'tunnels_after',
                                             'planet_grid_vs_natural_outside_pits', 'old_sites', 'server_points')}, indent=1))
    for name, g in groups.items():
        print(name, 'yaw', g['yaw'], 'turned', g['turned_by_deg'], 'ground spread', g['ground_spread_over_group_m'], 'lowest', g['ground_min_m'])
    print('Cave moves step: built')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
