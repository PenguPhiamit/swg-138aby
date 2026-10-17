"""O11c: one terrain fix for all six Ossus caves (Claude, 17 Oct 2026; the owner's run-29 reports, 12:00-12:15 PM).

Builds on build_cave_moves.py (the vault and adit moved above the 38.5 m water with their camps) and adds:
  1. O2's three hillside caves (the One Sith cell in the west foothills, the east foothill cave, the north cave):
     O2 cut a 9 m terrain hole (AEXC) centred on each doorway, half of it in front of the door where there is no cave
     floor ("a big gap in the terrain you can fall through"), while its 30 m levelled apron ran on across the tunnel
     behind the door ("a floor in the doorway"). These are hillside caves: their tunnel runs into a hill, and the
     levelled apron took the hill away. The holes go (the build leaves out O2's 'hole' layers), and behind each door
     the hill comes back: ROOF_CLEAR m over the roof of the first three tunnel cells (floor + TUNNEL_H), falling away
     from them at SLOPE (rise over run) to the natural ground, in 1 m cells and STEP m terraces, only behind the
     door's plane (the cave's rock face covers the step there; the apron in front of the door is untouched).
     These layers go at the very end of the layer list, after O2's cave-mouth layers, whose 30 m apron would
     otherwise flatten them again.
  2. Every cave's footprint loses its flora ("Sanctuary has a tree in the mouth": no snapshot object or screenplay prop
     stands there; the trees, bushes, grass and boulders come from the terrain's flora layers). A circle of FLORA_R m
     around each cave clears every flora family the terrain uses, boulders included.
"Behind the doorway" is tested against portal 0's own plane (the side its first cell lies on), so it also holds for
cave_02, whose door is in its side.
  changed  terrain/ossus.trn, snapshot/ossus.ws   (every other entry of the base byte for byte)

    C:/Users/Pengw/miniconda3/python.exe -I build_cave_fix.py [--base PATH] [--out PATH]
Default base: ../../../work/ossus-cave-mouths/local_planets-cave-mouths.tre (installed on run 29, beb06d28...).
Default out: ../../../work/ossus-cave-fix/local_planets-cave-fix.tre (+ .sha256), checks in ./checks-cave-fix.json.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import re
import shutil
import struct
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
from swgfmt.trn_iff import client_file, parse  # noqa: E402
import o7_terrain  # noqa: E402
from o7_common import jload, rot  # noqa: E402
import survey_caves as sc  # noqa: E402
import build_cave_mouths as bm  # noqa: E402
import build_cave_moves as mv  # noqa: E402

DEFAULT_BASE = mv.DEFAULT_BASE
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-cave-fix', 'local_planets-cave-fix.tre')
WATER = 38.5
WATER_CLEAR = 1.0   # m: a pit never goes lower than this above the water
ROOF_CLEAR = 1.5    # m of ground over a hillside tunnel's roof
SLOPE = 0.6         # the rebuilt hill's flanks: 0.6 m down per metre out (about 31 degrees)
CORE = 6.0          # m: the hill keeps its full height this far either side of the tunnel
STEP = 0.5          # m: raised heights are rounded down to this, one layer per height
TUNNEL_H = 9.25     # m: the tunnel's height, from portal 0 (floor -4.16, top 5.09 in cave_01)
FLORA_R = 50.0      # m around each cave node
GAP = 0.5           # m: the grown cell must stay this far behind portal 0's plane
O2_CAVES = {6900002: 'west foothill cave, the One Sith cell (cave_01)', 6900014: 'east foothill cave (cave_03)',
            6900044: 'north cave (cave_02)'}


def portal0(template):
    """Portal 0's vertices (building space) from the .pob's PRTS form."""
    d = client_file(template)
    pob = re.findall(rb'appearance/[A-Za-z0-9_/\.]+\.pob', d)[0].decode()
    root = parse(client_file(pob))[0]
    prts = [c for c in root.children[0].children if c.is_form and c.form == 'PRTS'][0]
    p = prts.children[0]
    n = struct.unpack('<i', p.data[:4])[0]
    f = struct.unpack('<%df' % (3 * n), p.data[4:4 + 12 * n])
    return [(f[3 * i], f[3 * i + 1], f[3 * i + 2]) for i in range(n)]


def behind_test(template):
    """A function (local x, local z) -> signed horizontal distance behind portal 0 (positive on its first cell's side)."""
    pv = portal0(template)
    xs, zs = [v[0] for v in pv], [v[2] for v in pv]
    # the portal is a vertical quad: its horizontal line runs between the two most distant (x, z) points
    a = max(((p, q) for p in pv for q in pv), key=lambda pq: (pq[0][0] - pq[1][0]) ** 2 + (pq[0][2] - pq[1][2]) ** 2)
    (x0, _, z0), (x1, _, z1) = a
    nx, nz = -(z1 - z0), (x1 - x0)
    ln = math.hypot(nx, nz)
    nx, nz = nx / ln, nz / ln
    cx, cz = sum(xs) / len(xs), sum(zs) / len(zs)
    r1 = sc.cell_floor(template, 1)
    mx, mz = sum(v[0] for v in r1) / len(r1), sum(v[2] for v in r1) / len(r1)
    if (mx - cx) * nx + (mz - cz) * nz < 0:
        nx, nz = -nx, -nz
    return lambda x, z: (x - cx) * nx + (z - cz) * nz


def cut_cells(o, terrain, at, verts, behind):
    xs, ys = [], []
    for vx, vy, vz in verts:
        ex, ny = rot(vx, vz, o['yaw'])
        xs.append(o['x'] + ex)
        ys.append(o['y'] + ny)
    C, E = bm.CELL, bm.EDGE
    cells = set()
    gx = math.floor(min(xs) / C) * C
    while gx < max(xs):
        gy = math.floor(min(ys) / C) * C
        while gy < max(ys):
            ok = True
            for fx in (-E, C / 2, C + E):
                for fy in (-E, C / 2, C + E):
                    px, py = gx + fx, gy + fy
                    lx, lz = bm.to_local(o, px, py)
                    f = at(lx, lz)
                    if f is None or behind(lx, lz) < GAP or o['z'] + f < terrain.h(px, py) + bm.SHELL_ABOVE:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                cells.add((round(gx, 3), round(gy, 3)))
            gy += C
        gx += C
    return cells


def raise_cells(o, terrain, behind, cells_upto=3):
    """Hillside caves: {cell: height} for the rebuilt hill over the first tunnel cells, behind the door only."""
    pts = []
    for k in range(1, cells_upto + 1):
        for vx, vy, vz in sc.cell_floor(o['template'], k):
            ex, ny = rot(vx, vz, o['yaw'])
            pts.append((o['x'] + ex, o['y'] + ny, o['z'] + vy + TUNNEL_H + ROOF_CLEAR))
    reach = CORE + 40.0 / SLOPE * 0.0 + 30.0
    x0, x1 = min(p[0] for p in pts) - reach, max(p[0] for p in pts) + reach
    y0, y1 = min(p[1] for p in pts) - reach, max(p[1] for p in pts) + reach
    C, E = bm.CELL, bm.EDGE
    cells = {}
    gx = math.floor(x0 / C) * C
    while gx < x1:
        gy = math.floor(y0 / C) * C
        while gy < y1:
            cx, cy = gx + C / 2, gy + C / 2
            ok = all(behind(*bm.to_local(o, gx + fx, gy + fy)) >= GAP for fx in (-E, C + E) for fy in (-E, C + E))
            if ok:
                best = None
                for px, py, roof in pts:
                    d = math.hypot(px - cx, py - cy)
                    t = roof - max(0.0, d - CORE) * SLOPE
                    if best is None or t > best:
                        best = t
                h = math.floor(best / STEP) * STEP
                if h > terrain.h(cx, cy) + 0.3:
                    cells[(round(gx, 3), round(gy, 3))] = h
            gy += C
        gx += C
    return cells


def crossings(o, terrain, cells_upto=3):
    """Tunnel floor points of cells 1..cells_upto where the ground lies between the floor and the roof."""
    n, worst = 0, []
    for k in range(1, cells_upto + 1):
        try:
            fl = sc.cell_floor(o['template'], k)
        except IndexError:
            continue
        for vx, vy, vz in fl:
            ex, ny = rot(vx, vz, o['yaw'])
            g = terrain.h(o['x'] + ex, o['y'] + ny)
            floor = o['z'] + vy
            if floor + 0.5 < g < floor + TUNNEL_H:
                n += 1
                worst.append({'cell': k, 'local': [round(vx, 1), round(vy, 1), round(vz, 1)], 'ground_above_floor_m': round(g - floor, 1)})
    return n, worst[:8]


def node_of(ws_nodes, nid, template_hint=None):
    n = next(x for x in ws_nodes if x['id'] == nid)
    q = n['quat']
    yaw = math.degrees(2 * math.atan2(q[2], q[0])) % 360
    return {'id': nid, 'template': n['template'], 'x': n['x'], 'y': n['y'], 'z': n['z'], 'yaw': round(yaw, 3)}


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
        assert base_sha.startswith(mv.DEFAULT_BASE_SHA_PREFIX), 'default base is not the run-29 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    nat_bytes = open(mv.NATURAL, 'rb').read()
    assert sha(nat_bytes).startswith(mv.NATURAL_SHA_PREFIX)
    natural, nat_trn = sc.load_terrain(nat_bytes)
    assert nat_trn == bm.O7_TRN_SHA

    # 1. the moves (as build_cave_moves.py)
    statics = json.load(open(os.path.join(OSSUS, 'o7-build', 'statics.json'), encoding='utf-8'))
    plans = {name: mv.plan_group(name, m, statics, natural) for name, m in mv.MOVES.items()}
    import ws_write
    import ws_read
    ws_nodes, templates = ws_read.read_ws(base[bm.WS])
    by_id = {n['id']: n for n in ws_nodes}
    for name, p in plans.items():
        for m in p['objects']:
            n = by_id[m['id']]
            n['x'], n['y'], n['z'] = m['to'][0], m['to'][1], m['to'][2]
            n['quat'] = mv.quat(m['to'][3])
    ws = ws_write.write_ws(ws_write.tree_from_reader(ws_nodes), templates)
    assert ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(ws)[0]), templates) == ws

    # 2. all six caves as they stand after the moves
    caves = {}
    for nid, name in list(sc.CAVES.items()) + list(O2_CAVES.items()):
        caves[nid] = dict(node_of(ws_read.read_ws(ws)[0], nid), name=name)

    layers, late, report = [], [], {}
    for nid, o in caves.items():
        at, _, verts = bm.floor_lookup(o['template'])
        behind = behind_test(o['template'])
        key = o['name'].split(' ')[0] + '-%d' % nid
        r1 = sc.cell_floor(o['template'], 1)
        low = o['z'] + min(v[1] for v in r1)
        info = {'name': o['name'], 'node': [round(o['x'], 2), round(o['y'], 2), round(o['z'], 2), o['yaw']],
                'first_tunnel_bottom_m': round(low, 2), 'flora_off_radius_m': FLORA_R}
        rects = []
        if nid in O2_CAVES:
            cells = raise_cells(o, natural, behind)
            levels = {}
            for c, h in cells.items():
                levels.setdefault(h, set()).add(c)
            for h in sorted(levels):
                rr = bm.rows_to_rects(levels[h])
                rects += rr
                late.append({'name': 'o11 %s hill %.1f m' % (key, h),
                               'boundaries': [{'type': 'BREC', 'name': '%s %.1f %d' % (key, h, i), 'x0': r[0], 'y0': r[1], 'x1': r[2], 'y1': r[3],
                                               'feather_type': 3, 'feather': 0.0} for i, r in enumerate(rr)],
                               'affectors': [{'type': 'AHCN', 'name': 'hill', 'op': 0, 'height': h}]})
            info.update({'fix': 'the hill rebuilt over the tunnel behind the door', 'hill_area_m2': len(cells) * bm.CELL ** 2,
                         'hill_heights_m': [min(levels), max(levels)] if levels else None, 'hill_layers': len(levels), 'rectangles': len(rects)})
        else:
            cells = cut_cells(o, natural, at, verts, behind)
            rects = bm.rows_to_rects(cells)
            pit = round(max(low - bm.PIT_MARGIN, WATER + WATER_CLEAR), 2)
            if rects:
                layers.append({'name': 'o11 %s pit' % key,
                               'boundaries': [{'type': 'BREC', 'name': '%s %d' % (key, i), 'x0': r[0], 'y0': r[1], 'x1': r[2], 'y1': r[3],
                                               'feather_type': 3, 'feather': 0.0} for i, r in enumerate(rects)],
                               'affectors': [{'type': 'AHCN', 'name': 'pit', 'op': 0, 'height': pit}]})
            info.update({'fix': 'pit under the mound behind the door', 'pit_height_m': pit, 'pit_area_m2': len(cells) * bm.CELL ** 2,
                         'rectangles': len(rects)})
        layers.append({'name': 'o11 %s no flora' % key,
                       'boundaries': [{'type': 'BCIR', 'name': 'cave', 'cx': o['x'], 'cy': o['y'], 'radius': FLORA_R, 'feather_type': 3, 'feather': 0.0}],
                       'affectors': [{'type': 'CLEAR_FLORA', 'prefix': key},
                                     {'type': 'AFSC', 'name': key + ' no boulders', 'family': 'rocks', 'op': 1, 'remove_all': 1}]})
        info['rects'] = rects
        report[nid] = info

    # 3. the terrain: O7 + the new layers, without O2's three doorway holes
    spec = jload(o7_terrain.TERRAIN_JSON)
    spec2 = copy.deepcopy(spec)
    spec2['layers'] = spec['layers'] + layers
    tmp = tempfile.mkdtemp(prefix='o11c-build-')
    spec_path = os.path.join(tmp, 'terrain-o11c.json')
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(spec2, f)
    ot = o7_terrain.ot
    orig_layer = ot.layer
    orig_form = ot.form
    appended = []

    def late_form(tag, *children):
        # the final pass's top layer list (O2's cave-mouth layers are in it): the hills go after everything
        if tag == 'LYRS' and final:
            final.clear()
            appended.append(len(late))
            return orig_form(tag, *(list(children) + [o7_terrain.build_layer(l, orig_layer) for l in late]))
        return orig_form(tag, *children)
    dropped = []
    SKIP = object()

    final = []

    def no_holes(name, *rules, **kw):
        if name == spec['insert_after_layer']:
            final.append(True)   # the ruins pad exists only in the final pass
        if name == 'hole':
            dropped.append(name)
            return SKIP
        return orig_layer(name, *[r for r in rules if r is not SKIP], **kw)
    keep = o7_terrain.TERRAIN_JSON
    o7_terrain.TERRAIN_JSON = spec_path
    ot.layer = no_holes
    ot.form = late_form
    try:
        rep = o7_terrain.build(tmp, with_layers=True, quiet=True)
    finally:
        o7_terrain.TERRAIN_JSON = keep
        ot.layer = orig_layer
        ot.form = orig_form
    assert rep.get('verdict') == 'PASS', rep.get('verdict')
    stage = os.path.join(tmp, 'staged', 'client')
    trn = open(os.path.join(stage, 'terrain', 'ossus.trn'), 'rb').read()
    for t in bm.TGAS:
        assert open(os.path.join(stage, *t.split('/')), 'rb').read() == base[t], t
    holes_before = base[bm.TRN].count(b'terrain hole')
    holes_after = trn.count(b'terrain hole')

    files = dict(base)
    files[bm.TRN], files[bm.WS] = trn, ws
    out = tre_write.pack(files)
    after, _ = sc.load_terrain(out)

    # 4. checks
    tunnels = {}
    for nid, o in caves.items():
        r1 = sc.cell_floor(o['template'], 1)
        behind = behind_test(o['template'])
        under, shallow, wet = [], [], 0
        for vx, vy, vz in r1:
            ex, ny = rot(vx, vz, o['yaw'])
            wx, wy = o['x'] + ex, o['y'] + ny
            g = after.h(wx, wy) - (o['z'] + vy)
            if after.h(wx, wy) < WATER:
                wet += 1
            if g > bm.SUNK:
                under.append(round(g, 1))
                if g < 10:
                    shallow.append({'local': [round(vx, 1), round(vy, 1), round(vz, 1)], 'ground_above_m': round(g, 1),
                                    'behind_door_m': round(behind(vx, vz), 1)})
        tunnels[o['name']] = {'r1_floor_vertices': len(r1), 'under_ground': len(under), 'under_ground_less_than_10m': len(shallow),
                              'ground_below_water_over_tunnel': wet, 'shallow_points': shallow[:12]}
    hillside = {}
    base_t, _ = sc.load_terrain(base_bytes)
    for nid in O2_CAVES:
        o = caves[nid]
        nb, wb = crossings(o, base_t)
        na, wa = crossings(o, after)
        hillside[o['name']] = {'ground_inside_tunnel_cells_1_3_before': nb, 'after': na, 'after_examples': wa}
    rects = [r for v in report.values() for r in v['rects']]
    circles = [(o['x'], o['y'], FLORA_R) for o in caves.values()]
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
    props_in_pits = []
    for nn in ws_read.read_ws(ws)[0]:
        if nn['depth'] == 0 and nn['id'] not in caves and bm.in_rects(rects, nn['x'], nn['y'], 0.5):
            props_in_pits.append((nn['id'], nn['template']))

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
        'untouched_identical': len(base) - len(changed), 'changed': changed, 'trn_sha256': sha(trn),
        'o2_doorway_holes': {'layers_left_out': len(dropped), 'terrain_hole_affectors_before': holes_before, 'after': holes_after},
        'caves': {str(k): {kk: vv for kk, vv in v.items() if kk != 'rects'} for k, v in report.items()},
        'tunnels_after': tunnels, 'hillside_ground_inside_tunnels': hillside,
        'planet_grid_vs_natural_outside_pits': {'samples': n, 'changed': changed_out, 'worst_m': round(worst, 4),
                                                'note': 'flora and the removed holes do not change heights'},
        'props_in_pits': props_in_pits, 'moved_groups': {k: {'yaw': p['yaw'], 'ground_spread_m': p['ground_spread_m']} for k, p in plans.items()},
        'flora_off_circles': circles,
    }
    with open(os.path.join(HERE, 'checks-cave-fix.json'), 'w', encoding='utf-8') as fh:
        json.dump(checks, fh, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    assert changed == sorted([bm.TRN, bm.WS]), changed
    assert holes_after == 0 and len(dropped) == 3, (holes_after, dropped)
    assert appended == [len(late)], appended
    assert not props_in_pits, props_in_pits
    print(json.dumps({k: checks[k] for k in ('out', 'untouched_identical', 'changed', 'o2_doorway_holes', 'caves', 'hillside_ground_inside_tunnels',
                                             'planet_grid_vs_natural_outside_pits')}, indent=1))
    for k, v in tunnels.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != 'shallow_points'}, v['shallow_points'][:4])
    print('Cave fix step: built')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
