"""O7: generate statics.json, poi-placements.json and the checks from the o7 terrain build, the census and the client's
template tables. Our own code (Claude, 16 Oct 2026). Read-only on the client archives and on /opt/swg.

    python -I make_o7.py [--terrain DIR] [--server out/server-templates.txt]

--terrain DIR  a folder holding staged/client/terrain/ossus.trn and its TGAs, as o7_terrain.py build --out writes it
               (default: build one into a temp folder first; nothing in the repo is touched by the build)
--server FILE  the output of tools/server_check.sh (run inside WSL as swgemu; it only reads Core3-dev templates); when
               missing, the server-template column stays "unchecked"
"""
import collections
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from o7_common import (CENSUS_MD, EDGE_STRIPS, KNOSSA, NOBUILD, O7, OUTPUTS, WATER, Census, Terrain, bearing, client_idx, dist, jload, jsave,  # noqa: E402
                       obb, poly_overlap, tinfo)
import o7_pois as P  # noqa: E402
import o7_terrain as OT  # noqa: E402

ID_BASE = 6900087        # o2's snapshot uses 6900000-6900086
POI_NAMES = {
    1: 'Academy ruins: craters, drop pod, memorial ring', 2: 'The hidden sanctuary', 3: "Krayt's garrison (benchland rim) and its dig",
    4: 'Great Library vaults and dig camp', 5: 'Ysanna hunting camp', 6: 'Ysanna stone circle', 8: 'Adega Lake fishing hamlet',
    9: 'Kathracite adit', 10: 'Imhar Canyon crossing', 11: 'Knossa old town', 12: 'The Jedi memorial road', 13: 'Eocho watch ruin',
    14: 'Sith interrogation post', 15: 'Crashed Alliance fighter', 16: 'Ysanna sky-burial cliff', 17: 'Supernova glass plain (terrain only)',
    18: 'The Hutt landing field'}
NOTES = {
    1: "Craters 4 and 5 are 2.0 m deep, not o6's 1.5 and 1.0 m (the owner said 2-4 m). o6 put the drop pod at (2160, 2700), 92 m from the nearest crater, so it stands on the south lip of "
       "crater 2 instead. The two fallen temple pillars o6 mentions are already in the snapshot (nothing new).",
    2: "A flatland cave on the benchland south-south-east of the hall, its mouth facing the hall, in the rubble apron; chosen as the nearest mouth distance (120-230 m from the pad centre) where the "
       "footprint clears every ruin static, crater and the memorial ring. The interior (cells 1-11 = building id + k) is a screenplay job.",
    3: "The owner's answer of 15 Oct: the garrison sits on the benchland rim over the ruins, guarding the dig, not by Knossa; o6's (600, -3300) site is dropped. Flat ground (2 m of relief over r 40) "
       "nearest the crest north-east of the ruins (the ground drops 8 m within 70 m of it); the compound's front faces the ruins and the dig sits between the gate and the hall.",
    4: "o6's (2300, 1900) is 43 m plain, not a summit; the cave stands on the flattest ground 25 m north of it. There is no hill behind it (flatland cave).",
    5: "o6's (-1200, -5200) is a 37 degree slope with 36 m of relief in the Eocho band (116 m, not the 180 m o6 assumed). The camp stands on the nearest ground that is flat "
       "(1.5 m over r 25), north-north-west at the foot of the mountains. There is no flat ground at 100-200 m within 450 m.",
    6: "Moved to the flattest ground within 90 m of o6's point; still a mountain shoulder (ground 4-5 m of relief over the ring).",
    8: "o6's (-2900, 1300) is 52 m up a 9 degree hillside; the hamlet stands 250 m south-west at the lake edge, 5 m above the water, with a short pier (three walkways and a platform) whose deck is set 1 m over the 38.5 m water, the one place objects stand on or over water.",
    9: "o6's (4500, -300) is on the canyon wall (spread 40 m). The cave stands on the floor against the wall, 100 m away, mouth facing the canyon centre line; the back of the mound is buried in the wall.",
    10: "Measured across the canyon every 40 m along its path, the narrowest places are 284-292 m between the 100 m contours (the painted floor half width swings 0.65 to 1.35 of 90 m, the walls are "
        "100 m); several such places exist, so the span is put at one 240 m up the canyon from o6's vertex (4300, -700) and runs north-west to south-east (142 m of walk each side of the centre line).",
    11: "Inside Knossa's city circle (r 200) and no-build circle (r 320). The starport footprint (48 x 30 m) and the shuttle pad stay clear.",
    12: "A line of 16 pillars 8-12 m off the road, one at the end of each 480 m piece; the centre shown is the middle marker.",
    13: "The summit shoulder at o6's point is the best within 60 m (steep; each static takes its own ground height).",
    14: "Outside dressing only. The cave node (6900002) and its 10 cell nodes already exist; the cells are dressed by screenplay.",
    15: "At o6's point (flat plain, 62 m).",
    16: "o6's (5000, 900) is flat mesa top 280 m from the nearest canyon rim. The platform stands 16 m back from that rim point.",
    17: "Terrain only (terrain.json layer 'o7 supernova glass plain'). The ground there is a 105 m, 41 degree mountain slope: the layer paints and clears it, it does not make a plain. "
        "The flat alternative (spread 12.6 m) is the foothills at x 1850-2450, y -4800 to -4500.",
    18: "o6's camp building (object/building/poi/shared_tatooine_hutt_businessmen_camp_medium) is a server theater anchor with no art, so the field is built from statics: a landing pad, tents, pallets, crates.",
}
SKIP_OVERLAP_GROUPS ={'fortification', 'markers', 'bridge', 'fence', 'pier', 'platform'}


def snapshot_usage(templates, cache_path):
    """How the stock and MTG snapshots use each template: node count, planets, and the node float they carry (mode)."""
    if os.path.exists(cache_path):
        cached = jload(cache_path)
        if all(t in cached and 'node_crcs' in cached[t] for t in templates):
            return cached
    from swgfmt import trn_iff, ws_read
    idx = client_idx()
    want = set(templates)
    use = {t: {'nodes': 0, 'planets': {}, 'floats': collections.Counter(), 'crcs': collections.Counter(), 'children': collections.Counter()} for t in want}
    for nm in sorted(k for k in idx if k.startswith('snapshot/') and k.endswith('.ws')):
        try:
            nodes, _ = ws_read.read_ws(trn_iff.client_file(nm))
        except Exception:
            continue
        planet = nm.split('/')[1][:-3]
        for n in nodes:
            if n['template'] in want:
                u = use[n['template']]
                u['nodes'] += 1
                u['planets'][planet] = u['planets'].get(planet, 0) + 1
                u['floats'][str(n['game_object_type'])] += 1
                u['crcs'][str(n['unknown'])] += 1
                u['children'][str(len(n['children']))] += 1
    out = {t: {'nodes': u['nodes'], 'planets': u['planets'], 'node_float_mode': (u['floats'].most_common(1)[0][0] if u['floats'] else None),
               'node_crcs': dict(u['crcs']), 'node_child_counts': dict(u['children'])} for t, u in use.items()}
    jsave(cache_path, out)
    return out


def building_vs_stock(template, objects, usage):
    """For a building template that stock or MTG snapshots place: do our nodes carry the same portal-layout CRC and cell-node count?"""
    mine = [o for o in objects if o['template'] == template and o['kind'] == 'building']
    u = usage.get(template, {})
    if not mine or not u.get('nodes'):
        return None
    crcs, kids = set(u['node_crcs']), set(u['node_child_counts'])
    return {'stock_crcs': sorted(crcs), 'stock_child_counts': sorted(kids), 'ours_crc': mine[0]['pob_crc'], 'ours_children': mine[0]['cells'] - 1,
            'match': str(mine[0]['pob_crc']) in crcs and str(mine[0]['cells'] - 1) in kids}


def server_status(path):
    status = {}
    if path and os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if line.startswith('ok '):
                status[line.split()[1]] = 'ok'
            elif line.startswith('MISSING-SERVER '):
                status[line.split()[1]] = 'missing'
    return status


def main(argv):
    terrain_dir = argv[argv.index('--terrain') + 1] if '--terrain' in argv else None
    server_file = argv[argv.index('--server') + 1] if '--server' in argv else os.path.join(O7, 'out', 'server-templates.txt')
    if terrain_dir is None:
        terrain_dir = tempfile.mkdtemp(prefix='o7-terrain-')
        print('building the o7 terrain into', terrain_dir)
        rep = OT.build(terrain_dir, quiet=True)
        print('terrain build verdict', rep['verdict'])
    stage_client = os.path.join(terrain_dir, 'staged', 'client')
    T = Terrain(os.path.join(stage_client, 'terrain', 'ossus.trn'), stage_client)
    census = Census()
    spec = jload(OT.TERRAIN_JSON)
    craters = spec['design']['craters']

    L = P.Layout(T)
    ruins_fixed = P.existing_ruins()
    meta = {}
    meta[1] = P.poi1_ruins(L, spec)
    meta[2] = P.poi2_sanctuary(L, T, spec, ruins_fixed, craters)
    meta[3] = P.poi3_garrison(L, T, spec, craters)
    meta[4] = P.poi4_vaults(L, T)
    meta[5] = P.poi5_ysanna_camp(L, T)
    meta[6] = P.poi6_stone_circle(L, T)
    meta[8] = P.poi8_hamlet(L, T)
    meta[9] = P.poi9_adit(L, T)
    meta[10] = P.poi10_bridge(L, T)
    meta[11] = P.poi11_knossa(L, T)
    meta[12] = P.poi12_markers(L, T)
    meta[13] = P.poi13_watch(L, T)
    meta[14] = P.poi14_sith_post(L, T, (-2976.0, -4960.0))
    meta[15] = P.poi15_crash(L, T)
    meta[16] = P.poi16_sky_burial(L, T)
    gp = spec['design']['glass_plain']['rect']
    meta[17] = {'centre': ((gp[0] + gp[2]) / 2, (gp[1] + gp[3]) / 2), 'radius': 330.0, 'o6_point': (0.0, -5500.0)}
    meta[18] = P.poi18_hutt(L, T)

    # ---- ids, node floats, building facts
    templates = sorted(set(o['template'] for o in L.objs))
    usage = snapshot_usage(templates, os.path.join(O7, 'out', 'snapshot-usage.json'))
    srv = server_status(server_file)
    next_id = ID_BASE
    objects = []
    for o in L.objs:
        info = tinfo(o['template'])
        rec = dict(o)
        rec['id'] = next_id
        if o['kind'] == 'building':
            pi = info.get('pob_info') or {}
            rec['pob'] = info.get('pob')
            rec['cells'] = pi.get('cells', 0)
            rec['pob_crc'] = pi.get('crc', 0)
            rec['node_float'] = 512.0
            next_id += max(1, rec['cells'])      # the building node, then one cell node per interior cell 1..cells-1
        else:
            mode = usage.get(o['template'], {}).get('node_float_mode')
            rec['node_float'] = float(mode) if mode is not None else 200.0
            next_id += 1
        objects.append(rec)
    last_id = next_id - 1
    with open(os.path.join(O7, 'out', 'server-templates.list'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# client template names the o7 statics use, plus the Hutt broker body; tools/server_check.sh looks each up in Core3-dev\n')
        for t in templates + ['object/mobile/shared_hutt_male.iff']:
            f.write(t + '\n')

    # ---- per-template resolution table
    tpl_rows = []
    for t in templates:
        i = tinfo(t)
        sx = size_ext(i)
        tpl_rows.append({'template': t, 'client_table': 'stock' if i['in_stock_table'] else ('merged only (MTG/Hoth)' if i['in_merged_table'] else 'ABSENT'),
                         'client_file': i['client_file'], 'missing_appearances': i['missing_appearances'], 'size_xyz_m': sx,
                         'portal_layout': i.get('pob'), 'cells': (i.get('pob_info') or {}).get('cells'),
                         'server_template': srv.get(t, 'unchecked'), 'stock_snapshot_nodes': usage.get(t, {}).get('nodes'),
                         'stock_snapshot_planets': usage.get(t, {}).get('planets'), 'uses': sum(1 for o in objects if o['template'] == t),
                         'building_node_vs_stock': building_vs_stock(t, objects, usage)})
    problems = [r for r in tpl_rows if r['client_table'] != 'stock' or not r['client_file'] or r['missing_appearances'] or r['server_template'] == 'missing']

    # ---- the o6 "(confirm)" items against the client's template list
    from o7_resolution import RESOLUTION
    idx = client_idx()
    resolution, res_bad = [], []
    for r in RESOLUTION:
        row = {k: v for k, v in r.items() if k not in ('chosen', 'shaders')}
        row['chosen'] = []
        for t in r.get('chosen', []):
            i = tinfo(t)
            ok = i['in_stock_table'] and i['client_file'] and not i['missing_appearances'] and srv.get(t, 'unchecked') != 'missing'
            row['chosen'].append({'template': t, 'in_stock_table': i['in_stock_table'], 'client_file': i['client_file'], 'appearances_missing': i['missing_appearances'],
                                  'server_template': srv.get(t, 'unchecked'), 'size_xyz_m': size_ext(i), 'in_statics_json': t in templates})
            if not ok or t not in templates:
                res_bad.append((r['poi'], t, 'not in statics.json' if t not in templates else 'check failed'))
        row['shaders'] = [{'shader': s, 'in_client': s.lower() in idx} for s in r.get('shaders', [])]
        res_bad += [(r['poi'], s['shader'], 'shader missing') for s in row['shaders'] if not s['in_client']]
        resolution.append(row)
    jsave(os.path.join(O7, 'template-resolution.json'), {'schema': 'o7-resolution-1', 'source': 'misc/object_template_crc_string_table.iff, stock copy in patch_14_00.tre '
                                                          '(15,792 names) and the installed local_planets.tre (29,358 names)', 'items': resolution})
    for b in res_bad:
        print('  RESOLUTION CHECK', b)

    # ---- overlap and ground checks
    fixed = [('existing ruin', obb(t, x, y, yaw, 0.0), t) for t, x, y, yaw in ruins_fixed]
    fixed.append(('Knossa starport', [(-24.0, -3608.0), (24.0, -3608.0), (24.0, -3577.5), (-24.0, -3577.5)], 'starport'))
    polys = [(o, obb(o['template'], o['x'], o['y'], o['yaw'], 0.0)) for o in objects]
    overlaps = []
    for i, (a, pa) in enumerate(polys):
        for b, pb in polys[i + 1:]:
            if a['poi'] != b['poi'] and abs(a['x'] - b['x']) > 120:
                continue
            if a['group'] in SKIP_OVERLAP_GROUPS and a['group'] == b['group']:
                continue
            if poly_overlap(pa, pb):
                overlaps.append((a, b))
        for name, pf, tpl in fixed:
            if abs(pf[0][0] - a['x']) < 150 and poly_overlap(pa, pf):
                overlaps.append((a, {'poi': name, 'role': tpl.split('/')[-1], 'template': tpl, 'x': pf[0][0], 'y': pf[0][1], 'group': name}))
    over_rows = [{'a': '%d:%s' % (a['poi'], a['role']), 'a_template': a['template'].split('/')[-1], 'b': '%s:%s' % (b['poi'], b['role']), 'b_template': b['template'].split('/')[-1],
                  'at': [a['x'], a['y']]} for a, b in overlaps]
    # statics inside crater bowls (other than the debris and pod that belong there)
    in_crater = []
    for o in objects:
        for c in craters:
            if o['poi'] not in (1,) and math.hypot(o['x'] - c['cx'], o['y'] - c['cy']) < c['burn_radius']:
                in_crater.append({'object': o['role'], 'template': o['template'].split('/')[-1], 'crater': c['id']})
    tilt = []
    for o in objects:
        x0, x1, z0, z1 = size_ext_box(o['template'])
        pts = [(o['x'], o['y'])]
        for lx, lz in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            dx, dy = P.rot(lx, lz, o['yaw'])
            pts.append((o['x'] + dx, o['y'] + dy))
        hs = [T.h(px, py) for px, py in pts]
        sp = max(hs) - min(hs)
        if sp > 2.5 and o['kind'] == 'static' and o['group'] not in ('bridge',):
            tilt.append({'poi': o['poi'], 'role': o['role'], 'template': o['template'].split('/')[-1], 'ground_spread_under_footprint_m': round(sp, 1)})

    # does the ground meet each building? ground minus the building origin over its solid footprint, against the exterior mesh's own range
    fit = []
    for o in objects:
        if o['kind'] != 'building':
            continue
        info = tinfo(o['template'])
        ext = info['ext']
        x0, x1, z0, z1 = size_xz_solid(o['template'])
        gs = []
        for fx in (0.0, 0.5, 1.0):
            for fz in (0.0, 0.5, 1.0):
                dx, dy = P.rot(x0 + (x1 - x0) * fx, z0 + (z1 - z0) * fz, o['yaw'])
                gs.append(T.h(o['x'] + dx, o['y'] + dy) - o['z'])
        fit.append({'poi': o['poi'], 'role': o['role'], 'template': o['template'].split('/')[-1], 'origin_z': o['z'],
                    'ground_minus_origin_min': round(min(gs), 1), 'ground_minus_origin_max': round(max(gs), 1),
                    'mesh_height_range_above_origin': [ext['min'][1], ext['max'][1]] if ext else None,
                    'verdict': ('ground below the mesh base by %.1f m (gap)' % (ext['min'][1] - min(gs)) if ext and min(gs) < ext['min'][1] - 0.5
                                else 'fits' if not ext or max(gs) < ext['max'][1] else 'ground above the mesh top')})
    wet = [{'poi': o['poi'], 'role': o['role'], 'template': o['template'].split('/')[-1], 'ground_z': round(T.h(o['x'], o['y']), 2)}
           for o in objects if o['group'] != 'pier' and T.h(o['x'], o['y']) < WATER + 0.3]
    in_nb = collections.Counter()
    for o in objects:
        for (x, y, r, n) in NOBUILD:
            if math.hypot(o['x'] - x, o['y'] - y) < r:
                in_nb[(o['poi'], n)] += 1

    # ---- per-POI placement report
    pois = {}
    for pid in sorted(POI_NAMES):
        m = meta[pid]
        cx, cy = m['centre']
        rad = m['radius']
        probe_r = min(rad, 45.0)
        lo, hi, sp = T.relief(cx, cy, probe_r, 5.0)
        slope = T.max_slope_deg(cx, cy, probe_r, 5.0)
        if pid == 12:           # a line of 16 markers, not one place: judge each marker's own 6 m neighbourhood
            probe_r = 6.0
            ms = [(T.relief(px, py, 6.0, 2.0), T.max_slope_deg(px, py, 6.0, 2.0)) for px, py in m['points']]
            lo, hi = min(r[0][0] for r in ms), max(r[0][1] for r in ms)
            sp = max(r[0][2] for r in ms)
            slope = max(r[1] for r in ms)
        smp, sd = census.nearest_sample(cx, cy)
        near3 = sorted(((math.hypot(r['x'] - cx, r['y'] - cy), r) for r in census.rows), key=lambda t: t[0])[:3]
        near3 = [{'distance_m': round(d), 'kind': r['kind'], 'name': r['name'], 'census_z': r['z'], 'terrain_z_at_sample': round(T.h(r['x'], r['y']), 1)} for d, r in near3]
        fauna = census.around(cx, cy, 300.0, census.fauna)
        fauna_by = collections.defaultdict(list)
        for d, r in fauna:
            fauna_by[r['name']].append((d, r))
        fauna_rows = []
        for name, rows in sorted(fauna_by.items(), key=lambda kv: min(d for d, _ in kv[1])):
            lv = sorted(set(int(r['lvl']) for _, r in rows))
            fauna_rows.append({'name': name, 'sightings': len(rows), 'levels': '%d' % lv[0] if len(lv) == 1 else '%d-%d' % (lv[0], lv[-1]), 'nearest_m': round(min(d for d, _ in rows))})
        nearest_fauna = None
        if census.fauna:
            r = min(census.fauna, key=lambda r: math.hypot(r['x'] - cx, r['y'] - cy))
            nearest_fauna = {'name': r['name'], 'level': r['lvl'], 'distance_m': round(math.hypot(r['x'] - cx, r['y'] - cy))}
        # census statics are lair props and dens ("unknown_object"); the 31 ruin statics and the snapshot buildings are not lairs
        lair_rows = [r for r in census.props if math.hypot(r['x'] - 2016.0, r['y'] - 2848.0) > 125.0]
        props = census.around(cx, cy, 300.0, lair_rows)
        flat_hit = [f for f in census.flat if math.hypot(f['x'] - cx, f['y'] - cy) <= 181.0]       # inside the 256 m square (half-diagonal 181)
        nb = [n for (x, y, r, n) in NOBUILD if math.hypot(cx - x, cy - y) < r]
        nb_objects = collections.Counter()
        for o in objects:
            if o['poi'] == pid:
                for (x, y, r, n) in NOBUILD:
                    if math.hypot(o['x'] - x, o['y'] - y) < r:
                        nb_objects[n] += 1
        edge = abs(cx) > 8000 - EDGE_STRIPS or abs(cy) > 8000 - EDGE_STRIPS
        z = T.h(cx, cy)
        count = sum(1 for o in objects if o['poi'] == pid)
        flags = []
        if slope > 20.0:
            flags.append('STEEP: %.0f deg over r %d m (spread %.0f m)' % (slope, probe_r, sp))
        elif sp > 6.0:
            flags.append('rough: %.0f m of relief over r %d m' % (sp, probe_r))
        if lo < WATER + 0.5:
            flags.append('WATER: ground reaches %.1f m (global water %.1f m) within r %d m' % (lo, WATER, probe_r))
        if nb or nb_objects:
            flags.append('inside a no-build circle: %s' % ', '.join(sorted(set(nb) | set(nb_objects))))
        if sd > 600:
            flags.append('census blind spot: nearest explorer sample %d m away' % sd)
        if not fauna_rows:
            flags.append('no census creature within 300 m (nearest %s)' % (('%s at %d m' % (nearest_fauna['name'], nearest_fauna['distance_m'])) if nearest_fauna else 'none seen'))
        o6 = m.get('o6_point')
        pois[str(pid)] = {
            'poi': pid, 'name': POI_NAMES[pid], 'objects': count, 'centre': [round(cx, 1), round(cy, 1)], 'o6_point': list(o6) if o6 else None,
            'moved_from_o6_m': round(dist((cx, cy), o6)) if o6 else None, 'ground_z_terrain': round(z, 1),
            'census_nearest_sample': {'kind': smp['kind'], 'name': smp['name'], 'distance_m': round(sd), 'z': smp['z'], 'terrain_minus_sample_z': round(T.h(smp['x'], smp['y']) - smp['z'], 2)},
            'census_nearest_3_ground_samples': near3,
            'footprint_probe_radius_m': probe_r, 'ground_min': round(lo, 1), 'ground_max': round(hi, 1), 'relief_m': round(sp, 1), 'steepest_slope_deg': round(slope, 1),
            'distance_from_knossa_m': round(dist((cx, cy), KNOSSA)), 'creatures_within_300m': fauna_rows, 'nearest_creature': nearest_fauna,
            'lair_props_within_300m': {'count': len(props), 'nearest_m': round(min((d for d, _ in props), default=-1))},
            'census_flat_squares_nearby': flat_hit, 'no_build_circles_containing_centre': nb, 'objects_inside_no_build': dict(nb_objects),
            'edge_strip': edge, 'flags': flags, 'notes': NOTES.get(pid, ''), 'extra': {k: v for k, v in m.items() if k not in ('centre', 'radius', 'o6_point')}}

    # ---- NPC and screenplay anchor points (the spawn step reads these)
    npcs = npc_points(meta, objects, T)

    out = {
        'schema': 'o7-statics-1',
        'units': 'x east, y north, z up (metres); yaw = compass heading in degrees (0: the object\'s +z faces north, 90: east), as in o2 stage_snapshot.py',
        'z': 'ground height from the o7 terrain build (Core3 port); buildings that open at ground level (flatland caves) are lowered so the entrance floor meets the ground',
        'first_id': ID_BASE, 'last_id': last_id,
        'id_rule': 'a building takes its id plus one id per interior cell 1..cells-1 (cell k = building id + k); a static takes one id',
        'snapshot_fields': 'node_float is the float after the position in the .ws node (512 for buildings; for statics the value stock snapshots use for that template, else 200); '
                           'pob_crc is the node\'s last field for buildings (0 for statics)',
        'templates': templates,
        'objects': [{k: v for k, v in o.items() if k != 'group'} for o in objects],
    }
    jsave(os.path.join(O7, 'statics.json'), out)
    placements = {'schema': 'o7-placements-1', 'terrain': 'o7 build', 'water_m': WATER, 'census': 'Bot-reports/launch-sim/ossus-census.csv/.md (16 Oct 2026 12:20 AM)',
                  'pois_note': 'ground_z_terrain is the Core3 port of the built terrain at the centre; census samples are rows of ossus-census.csv (z there is whole metres, truncated); '
                               'flags mark steep ground (over 20 degrees), water (ground at or under 39 m) and no-build circles; creatures_within_300m are census sightings (levels from the census); '
                               'lair props are the census statics (the lair and den props), the ruins\' own statics removed',
                  'pois': pois,
                  'npc_points_note': 'where the persons of each place stand: x east, y north, z ground height, heading in compass degrees; mobile_candidates are stock mobile template names '
                                     'that exist in Core3-dev (checked 16 Oct 2026), suggestions only; levels are not touched',
                  'npc_points': npcs}
    jsave(os.path.join(O7, 'poi-placements.json'), placements)
    checks = {'objects': len(objects), 'ids': [ID_BASE, last_id], 'templates': len(templates), 'template_problems': problems, 'overlaps': over_rows,
              'non_poi1_objects_inside_crater_burn_zones': in_crater, 'static_ground_tilt_over_2_5_m': tilt, 'objects_with_ground_at_or_under_water': wet,
              'objects_inside_no_build_circles': {'%d / %s' % k: v for k, v in sorted(in_nb.items())}, 'building_ground_fit': fit, 'templates_table': tpl_rows}
    jsave(os.path.join(O7, 'out', 'checks-statics.json'), checks)
    print('objects %d, ids %d-%d, templates %d, problems %d, overlaps %d, in crater zones %d, tilted %d' % (len(objects), ID_BASE, last_id, len(templates), len(problems), len(over_rows), len(in_crater), len(tilt)))
    for r in over_rows[:60]:
        print('  OVERLAP', r)
    for r in problems:
        print('  PROBLEM', r['template'], r['client_table'], r['missing_appearances'], r['server_template'])
    for k, v in pois.items():
        print(k, v['name'], 'objs', v['objects'], 'centre', v['centre'], 'moved', v['moved_from_o6_m'], 'z', v['ground_z_terrain'], 'slope', v['steepest_slope_deg'], 'flags', v['flags'])
    return 0


def size_ext(info):
    e = info['ext']
    if not e:
        return None
    return [round(e['max'][i] - e['min'][i], 1) for i in range(3)]


def size_ext_box(template):
    from o7_common import size_xz
    return size_xz(template)


def size_xz_solid(template):
    from o7_common import solid_box
    return solid_box(template)


def npc_points(meta, objects, T):
    """Spawn anchors for the screenplay step: where the persons of each place stand (role names, not templates)."""
    def pt(poi, role, x, y, heading, note=''):
        return {'poi': poi, 'role': role, 'x': round(x, 1), 'y': round(y, 1), 'z': round(T.h(x, y), 2), 'heading': round(heading % 360, 1), 'note': note}
    out = []
    g = meta[3]
    gate = g['gate']
    h = g['heading']
    F = P.Frame(g['centre'][0], g['centre'][1], h)
    out += [pt(3, 'garrison commander', *F.at(-12, -2.5), bearing(F.at(-12, -2.5), F.at(-12, -10.5)) , "in front of the commander's quarters"),
            pt(3, 'gate sentry', *F.at(-5, 22), h), pt(3, 'gate sentry', *F.at(12, 22), h),
            pt(3, 'tower sentry', *F.at(-29, 22.5), h, 'on the left front tower'), pt(3, 'tower sentry', *F.at(29, 22.5), h, 'on the right front tower'),
            pt(3, 'patrol (walks the rim)', *F.at(0, 26), h + 90, 'loop 60 m east-west along the rim'),
            pt(3, 'courtyard trooper', *F.at(2, -3), h + 180), pt(3, 'courtyard trooper', *F.at(-5, 6), h),
            pt(3, 'dig overseer', *F.at(0, 50), h + 180), pt(3, 'dig worker', *F.at(-10, 52), h), pt(3, 'dig worker', *F.at(10, 53), h + 90)]
    c = meta[2]['mouth']
    out.append(pt(2, 'sanctuary lookout (outside, hidden)', c[0], c[1], meta[2]['yaw'] + 180, 'the hidden Jedi encounter itself spawns inside, in the cave cells'))
    out.append(pt(4, 'scholar droid', meta[4]['mouth'][0] + 2, meta[4]['mouth'][1] + 62, 180, 'dig camp'))
    c = meta[5]['centre']
    out += [pt(5, 'Ysanna hunter', c[0] + 4, c[1] - 3, 0), pt(5, 'Ysanna hunter', c[0] - 5, c[1] + 6, 90), pt(5, 'Ysanna shaman', c[0] - 1, c[1] + 18, 180, 'by the stone hut')]
    c = meta[6]['centre']
    out += [pt(6, 'Ysanna ritual dancer (night loop)', c[0] + 4, c[1], 0, 'emote loop, dusk to dawn'), pt(6, 'Ysanna ritual dancer (night loop)', c[0] - 4, c[1], 180)]
    c = meta[8]['centre']
    out += [pt(8, 'fisher (bait and one lake-fish schematic)', c[0] + 3, c[1] + 4, 280), pt(8, 'fisher', c[0] - 10, c[1] - 6, 100)]
    c = meta[9]['mouth']
    out += [pt(9, 'foreman (Hutt-backed crew)', c[0], c[1], meta[9]['yaw'], 'at the mouth'), pt(9, 'miner', c[0] + 6, c[1] + 6, meta[9]['yaw'] + 90)]
    out += [pt(10, 'ambush point (under the bridge)', meta[10]['centre'][0], meta[10]['centre'][1], 0, 'canyon floor under the middle spans: bandits as the canyon group')]
    k = meta[11]['centre']
    out += [pt(11, 'Imperial recruiter (at the pad only)', k[0] + 22, k[1] - 18, 180, 'by the shuttle pad'),
            pt(11, 'artisan and entertainer terminals', k[0] - 20, k[1] - 56, 0, 'start of the market street'),
            pt(11, 'junk dealer', k[0] + 80, k[1] - 40, 90, 'by the junk shed'), pt(11, 'cantina patrons', k[0] - 70, k[1] - 10, 90, 'outside the cantina')]
    c = meta[13]['centre']
    out.append(pt(13, 'vantage waypoint (surveying)', c[0], c[1], 0, 'no NPC; a waypoint and a badge trigger'))
    c = meta[15]['centre']
    out.append(pt(15, 'Alliance pilot (neutral)', c[0] + 24, c[1] - 6, 270, 'asks for a part from the adit crew'))
    c = meta[18]['centre']
    out += [pt(18, 'Hutt broker (object/mobile/hutt_male.iff)', c[0], c[1] + 40, 180, 'in front of the broker tents'), pt(18, 'kathracite buyer', c[0] - 12, c[1] + 33, 0)]
    c = meta[14]['mouth']
    out += [pt(14, 'abandoned-post guard (dark-side ambient lingers inside)', c[0], c[1] + 14, 0, 'on the apron; the cells are dressed by screenplay')]
    # stock mobile templates that exist in Core3-dev (checked 16 Oct 2026, 9,044 names); suggestions only, the screenplay step chooses
    suggest = [('garrison commander', ['imperial_major', 'imperial_colonel']), ('sentry', ['stormtrooper_rifleman', 'stormtrooper']),
               ('patrol', ['stormtrooper_squad_leader', 'dark_trooper']), ('courtyard trooper', ['stormtrooper', 'imperial_sergeant']),
               ('dig overseer', ['imperial_inquisitor']), ('dig worker', ['miner', 'commoner_technician']),
               ('sanctuary lookout', ['jedi_light']), ('scholar droid', []), ('Ysanna shaman', ['hermit']), ('Ysanna', ['commoner_old', 'hermit']),
               ('fisher', ['commoner', 'farmer']), ('foreman', ['miner']), ('miner', ['miner']), ('ambush', ['brigand', 'bounty_hunter']),
               ('recruiter', ['imperial_recruiter']), ('terminals', ['artisan', 'entertainer']), ('junk dealer', ['junk_dealer']),
               ('cantina', ['commoner']), ('pilot', ['rebel_pilot']), ('Hutt broker', ['hutt_thug_npc']), ('buyer', ['smuggler']),
               ('guard', ['imperial_sergeant'])]
    for p in out:
        p['mobile_candidates'] = next((m for k, m in suggest if k in p['role']), [])
    return out


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
