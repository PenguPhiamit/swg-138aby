"""O2a: snapshot/ossus.ws from the surveyed sites (../out/ossus-sites.json): the Knossa starport, three stock caves at
the terrain's cave mouths, and a ruins field on the Academy pad from stock static pieces. Our own code (Fable,
14 Oct 2026); stock art referenced by template name only.

    python -I stage_snapshot.py     # writes ../staged/client/snapshot/ossus.ws, ../out/snapshot-report.json,
                                    #   ../work/dev-templates.txt (server templates for the dev check)

Conventions (read from MTG's hoth.ws and the stock snapshots with ws_read.py): buildings carry gameObjectType 512 and
the CRC chunk of their portal layout (.pob) in the last field, with one child NODE per interior cell (cellIndex
1..n-1, template object/cell/shared_cell.iff); statics carry the value stock snapshots use for the same template
and 0; cells 0 and 0. Quaternion (w, x, y, z) = (cos(h/2), 0, sin(h/2), 0) for a yaw h; the Hoth starport is
(0, 0, 1, 0) = 180 degrees. Positions are x, height, y as Core3 reads them.
"""
import json
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O2 = os.path.normpath(os.path.join(HERE, '..'))
OSSUS = os.path.normpath(os.path.join(O2, '..'))
OUTPUTS = os.path.normpath(os.path.join(OSSUS, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(OSSUS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-hoth-caves', 'tools'))
from trn_iff import Reader, client_file, client_index, open_tre_entry, parse  # noqa: E402
import swg_tables as st  # noqa: E402
import trn_read  # noqa: E402
from trn_road import RoadHeightEvaluator  # noqa: E402
import ws_read  # noqa: E402
import ws_write  # noqa: E402

STAGED = os.path.join(O2, 'staged', 'client')
OUT = os.path.join(O2, 'out')
WORK = os.path.join(O2, 'work')
SITES = os.path.join(OSSUS, 'out', 'ossus-sites.json')
TRN = os.path.join(OSSUS, 'staged', 'client', 'terrain', 'ossus.trn')
MERGED_CRC = os.path.join(OUTPUTS, 'Local-content', 'local_planets.tre')
ID_BASE = 6900000      # unused by every snapshot the client loads (checked below)

CELL = 'object/cell/shared_cell.iff'
STARPORT = 'object/building/military/shared_outpost_starport.iff'
CAVES = {   # template, portal layout, mouth position in building space (x, z forward), portal floor height, interior cells
    'cave_01': ('object/building/general/shared_cave_01.iff', 'appearance/thm_all_cave_s01.pob', (0.26, 18.0), -4.16),
    'cave_02': ('object/building/general/shared_cave_02.iff', 'appearance/thm_all_cave_s02.pob', (-17.4, 4.92), -0.43),
    'cave_03': ('object/building/general/shared_cave_03.iff', 'appearance/thm_all_cave_s03.pob', (0.26, 18.0), -4.15),
}
CAVE_FOR_SITE = {'cave_foothills_west': 'cave_01', 'cave_foothills_east': 'cave_03', 'cave_north': 'cave_02'}
# the gameObjectType value stock snapshots carry for each static (dantooine/corellia/talus .ws), else 200
STATIC_GOT = {'shared_dant_jedi_main_structure': 512, 'shared_dant_jedi_temple_altar': 512, 'shared_dant_jedi_temple_pillar': 512,
              'shared_dant_jedi_temple_pillar_med': 512, 'shared_dant_jedi_temple_pillar_sm': 512, 'shared_dant_jedi_temple_pillar_base': 512,
              'shared_dant_jedi_temple_pillar_fallen': 512, 'shared_dant_jedi_wall_1': 256, 'shared_dant_jedi_wall_2': 256,
              'shared_poi_temple_ancient_ruined': 175, 'shared_gungan_wall_ruined_lg_s01': 200, 'shared_gungan_wall_ruined_sm_s01': 200,
              'shared_gungan_pillar_ruined_s01': 200, 'shared_pillar_ruined_large_style_01': 128, 'shared_wall_ruined_tatooine_large_style_01': 128}
D = 'object/static/structure/dantooine/shared_dant_jedi_'
N = 'object/static/structure/naboo/shared_gungan_'
T = 'object/static/structure/tatooine/shared_'
# the ruins field, in pad space: (template, dx east, dy north, heading degrees)
RUINS = [
    (D + 'main_structure.iff', 0.0, 0.0, 0.0),                      # the ruined hall (31 x 28 m), centre of the pad
    ('object/static/structure/general/shared_poi_temple_ancient_ruined.iff', 0.0, 86.0, 90.0),   # the library block, long axis east-west
    (D + 'temple_altar.iff', 0.0, -44.0, 180.0),
    # colonnade down the avenue south of the altar, two rows 12 m apart, every 11 m
    (D + 'temple_pillar.iff', -6.0, -56.0, 0.0), (D + 'temple_pillar_med.iff', 6.0, -56.0, 0.0),
    (D + 'temple_pillar_base.iff', -6.0, -67.0, 0.0), (D + 'temple_pillar.iff', 6.0, -67.0, 0.0),
    (D + 'temple_pillar_fallen.iff', -4.0, -78.0, 70.0), (D + 'temple_pillar_sm.iff', 6.0, -78.0, 0.0),
    (D + 'temple_pillar.iff', -6.0, -89.0, 0.0), (D + 'temple_pillar_base.iff', 6.0, -89.0, 0.0),
    (D + 'temple_pillar_med.iff', -6.0, -100.0, 0.0), (D + 'temple_pillar_fallen.iff', 9.0, -101.0, 20.0),
    # wall fragments ringing the hall at 45-60 m
    (D + 'wall_1.iff', -52.0, 20.0, 0.0), (D + 'wall_1.iff', -52.0, -4.0, 10.0), (D + 'wall_2.iff', -48.0, 38.0, 35.0),
    (D + 'wall_1.iff', 54.0, 18.0, 180.0), (D + 'wall_2.iff', 55.0, -6.0, 160.0), (D + 'wall_1.iff', 50.0, 40.0, 150.0),
    (D + 'wall_2.iff', 30.0, -46.0, 90.0), (D + 'wall_2.iff', -30.0, -46.0, 90.0),
    # older, lower ruins to the west and east (Gungan and Tatooine ruined walls and pillars, as weathered outer courts)
    (N + 'wall_ruined_lg_s01.iff', -80.0, 50.0, 60.0), (N + 'wall_ruined_sm_s01.iff', -88.0, 40.0, 60.0), (N + 'pillar_ruined_s01.iff', -84.0, 62.0, 0.0),
    (N + 'wall_ruined_lg_s01.iff', -82.0, -40.0, 120.0), (N + 'pillar_ruined_s01.iff', -90.0, -28.0, 0.0),
    (T + 'wall_ruined_tatooine_large_style_01.iff', 82.0, 48.0, 120.0), (T + 'pillar_ruined_large_style_01.iff', 88.0, 36.0, 0.0),
    (T + 'wall_ruined_tatooine_large_style_01.iff', 84.0, -38.0, 60.0), (T + 'pillar_ruined_large_style_01.iff', 76.0, -52.0, 0.0),
    (T + 'pillar_ruined_large_style_01.iff', 92.0, -46.0, 0.0),
]


def quat(heading_deg):
    h = math.radians(heading_deg)
    return (math.cos(h / 2), 0.0, math.sin(h / 2), 0.0)


def local_to_world(lx, lz, heading_deg):
    """Building-space (x right, z forward) -> world offset (east, north) for a yaw; yaw 0 = forward is north."""
    h = math.radians(heading_deg)
    return lx * math.cos(h) + lz * math.sin(h), -lx * math.sin(h) + lz * math.cos(h)


def pob_info(path):
    d = client_file(path)
    root = parse(d)[0]
    v = root.children[0]
    info = {'portals': 0, 'cells': 0, 'crc': 0, 'exterior': None}
    for c in v.children:
        if not c.is_form and c.tag == 'DATA':
            info['portals'], info['cells'] = struct.unpack('<ii', c.data)
        elif not c.is_form and c.tag == 'CRC ':
            info['crc'] = struct.unpack('<I', c.data)[0]
        elif c.is_form and c.form == 'CELS':
            cv = c.children[0].children[0]
            data = [x for x in cv.children if not x.is_form and x.tag == 'DATA'][0]
            r = Reader(data.data)
            r.i32(); r.u8(); r.cstr()
            info['exterior'] = r.cstr()
    return info


def extents(appearance):
    """(max xyz, min xyz) from the EXBX box of an .apt/.lod/.msh chain."""
    d = client_file(appearance)
    if d is None:
        return None
    root = parse(d)[0]
    if root.form == 'APT ':
        return extents(re.findall(rb'appearance/[A-Za-z0-9_/\.]+', d)[0].decode())

    def find(nodes, tag):
        for n in nodes:
            if n.is_form and n.form == tag:
                return n
        return None
    appr = find(root.children[0].children, 'APPR')
    exbx = find(appr.children[0].children, 'EXBX') if appr else None
    if exbx is None:
        return None
    box = [c for c in exbx.children[0].children if not c.is_form and c.tag == 'BOX '][0]
    f = struct.unpack('<6f', box.data)
    return {'max': f[:3], 'min': f[3:]}


def footprint(ext, heading_deg, ox, oy):
    """World corners of a building-space box (x, z) rotated by the yaw and placed at (ox, oy)."""
    corners = []
    for lx in (ext['min'][0], ext['max'][0]):
        for lz in (ext['min'][2], ext['max'][2]):
            dx, dy = local_to_world(lx, lz, heading_deg)
            corners.append((round(ox + dx, 1), round(oy + dy, 1)))
    return corners


def main():
    with open(SITES, encoding='utf-8') as f:
        sites = json.load(f)
    with open(TRN, 'rb') as f:
        trn = trn_read.read_trn(f.read())
    bitmaps = {}
    for name in ('terrain/ossus_academy.tga', 'terrain/ossus_canyon.tga', 'terrain/ossus_mesa.tga'):
        with open(os.path.join(OSSUS, 'staged', 'client', name.replace('/', os.sep)), 'rb') as f:
            bitmaps[name] = f.read()
    ev = RoadHeightEvaluator(trn, lambda n: trn_read.load_tga_grey(bitmaps[n]))
    idx = client_index()
    merged = set(n for _, n in st.read_cstb(open_tre_entry(MERGED_CRC, 'misc/object_template_crc_string_table.iff'))['entries'])

    templates, nodes, report = [], [], {'objects': [], 'caves': [], 'checks': {}}
    next_id = [ID_BASE]

    def tid(t):
        if t not in templates:
            templates.append(t)
        return t

    def new_id():
        next_id[0] += 1
        return next_id[0] - 1

    def building(template, pob, x, z, y, heading, label):
        info = pob_info(pob)
        node = {'id': new_id(), 'parent': 0, 'template': tid(template), 'cell_index': 0, 'quat': quat(heading), 'x': x, 'z': z, 'y': y,
                'game_object_type': 512.0, 'unknown': info['crc'], 'child_nodes': []}
        for k in range(1, info['cells']):
            node['child_nodes'].append({'id': new_id(), 'parent': node['id'], 'template': tid(CELL), 'cell_index': k, 'quat': (1.0, 0.0, 0.0, 0.0),
                                        'x': 0.0, 'z': 0.0, 'y': 0.0, 'game_object_type': 0.0, 'unknown': 0, 'child_nodes': []})
        nodes.append(node)
        report['objects'].append({'what': label, 'id': node['id'], 'template': template, 'x': x, 'z': z, 'y': y, 'heading': heading,
                                  'cells': info['cells'] - 1, 'pob_crc': info['crc']})
        return node, info

    def static(template, x, z, y, heading, label):
        node = {'id': new_id(), 'parent': 0, 'template': tid(template), 'cell_index': 0, 'quat': quat(heading), 'x': x, 'z': z, 'y': y,
                'game_object_type': float(STATIC_GOT.get(template.split('/')[-1][:-4], 200)), 'unknown': 0, 'child_nodes': []}
        nodes.append(node)
        report['objects'].append({'what': label, 'id': node['id'], 'template': template, 'x': x, 'z': z, 'y': y, 'heading': heading})
        return node

    # 1. the Knossa starport on the pad, yaw 180 like Hoth's (the pad lies at +20.3, +17.8 from the building)
    pad = sites['starport_pad']
    sp, info = building(STARPORT, 'appearance/mun_all_landing_pad_s01.pob', pad['x'], pad['height'], pad['y'], 180.0, 'Knossa starport')
    ext = extents(info['exterior'])
    fp = footprint(ext, 180.0, pad['x'], pad['y'])
    report['starport'] = {'travel_point': {'x': round(pad['x'] + 20.3, 1), 'z': pad['height'], 'y': round(pad['y'] + 17.8, 1)},
                          'footprint_corners': fp, 'ground_at_corners': [round(ev.height(cx, cy), 2) for cx, cy in fp],
                          'exterior_box': ext, 'flat_pad_radius': pad['flat_inner_radius']}

    # 2. the caves: origin = mouth - (mouth offset in building space, rotated); height = apron + portal floor offset
    for site in sites['caves']:
        key = CAVE_FOR_SITE[site['name']]
        template, pob, (mx_l, mz_l), floor = CAVES[key]
        heading = float(site['mouth_faces_deg'])
        dx, dy = local_to_world(mx_l, mz_l, heading)
        ox, oy = round(site['x'] - dx, 1), round(site['y'] - dy, 1)
        oz = round(site['height'] - floor, 1)
        node, info = building(template, pob, ox, oz, oy, heading, 'cave at ' + site['name'])
        ext = extents(info['exterior'])
        fp = footprint(ext, heading, ox, oy)
        mouth_world = (round(ox + dx, 1), round(oy + dy, 1))
        report['caves'].append({
            'site': site['name'], 'cave': key, 'origin': [ox, oz, oy], 'heading': heading, 'mouth_world': mouth_world,
            'mouth_matches_hole': abs(mouth_world[0] - site['x']) < 0.2 and abs(mouth_world[1] - site['y']) < 0.2,
            'portal_floor_height': round(oz + floor, 1), 'apron_height': site['height'],
            'exterior_box_building_space': ext, 'footprint_corners': fp,
            'ground_at_corners': [round(ev.height(cx, cy), 2) for cx, cy in fp],
            'ground_minus_origin_at_corners': [round(ev.height(cx, cy) - oz, 2) for cx, cy in fp],
            'exterior_height_range_above_origin': [round(ext['min'][1], 1), round(ext['max'][1], 1)],
            'farthest_corner_from_mouth': round(max(math.hypot(cx - site['x'], cy - site['y']) for cx, cy in fp), 1), 'apron_radius': 30.0,
            'hole_radius': 9.0})

    # 3. the ruins field on the Academy pad
    ruins = sites['academy_ruins']
    for template, dx, dy, heading in RUINS:
        x, y = round(ruins['x'] + dx, 1), round(ruins['y'] + dy, 1)
        static(template, x, round(ev.height(x, y), 2), y, heading, 'ruins: ' + template.split('/')[-1][7:-4])
    hs = [o['z'] for o in report['objects'] if o['what'].startswith('ruins')]
    report['ruins'] = {'centre': [ruins['x'], ruins['y']], 'pieces': len(RUINS), 'height_range': [min(hs), max(hs)], 'pad_radius': ruins['radius'],
                       'farthest_piece_from_centre': round(max(math.hypot(dx, dy) for _, dx, dy, _ in RUINS), 1)}

    # write, round trip, checks
    data = ws_write.write_ws(nodes, templates)
    path = os.path.join(STAGED, 'snapshot', 'ossus.ws')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    back_nodes, back_templates = ws_read.read_ws(data)
    rt = ws_write.write_ws(ws_write.tree_from_reader(back_nodes), back_templates) == data
    ids = [n['id'] for n in back_nodes]
    used_elsewhere = []
    for name in sorted(k for k in idx if k.startswith('snapshot/') and k.endswith('.ws')):
        other = {n['id'] for n in ws_read.read_ws(client_file(name))[0]}
        if other & set(ids):
            used_elsewhere.append(name)
    missing_client = [t for t in templates if t.lower() not in idx]
    missing_crc = [t for t in templates if t not in merged]
    pobs = [CAVES[k][1] for k in CAVES] + ['appearance/mun_all_landing_pad_s01.pob']
    report['checks'] = {'bytes': len(data), 'nodes': len(back_nodes), 'world_level': sum(1 for n in back_nodes if n['parent'] == 0),
                        'templates': templates, 'round_trip_identical': rt, 'ids': [min(ids), max(ids)], 'ids_unique': len(set(ids)) == len(ids),
                        'ids_used_by_other_snapshots': used_elsewhere, 'templates_missing_in_client': missing_client,
                        'templates_missing_in_merged_crc_table': missing_crc,
                        'portal_layouts_present': {p: p.lower() in idx for p in pobs},
                        'hoth_ws_round_trip': ws_write.roundtrip('client:snapshot/hoth.ws')[0]}
    with open(os.path.join(WORK, 'dev-templates.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# server templates the snapshot needs in Core3-dev (object/<path>/<name>.lua without shared_)\n')
        for t in templates:
            f.write(t.replace('shared_', '').replace('.iff', '.lua') + '\n')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'snapshot-report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report['checks'], indent=1))
    for c in report['caves']:
        print(c['site'], c['cave'], 'origin', c['origin'], 'heading', c['heading'], 'mouth ok', c['mouth_matches_hole'], 'ground-origin at corners', c['ground_minus_origin_at_corners'],
              'exterior y', c['exterior_height_range_above_origin'], 'farthest corner', c['farthest_corner_from_mouth'])
    print('starport', report['starport'])
    print('ruins', report['ruins'])
    ok = rt and not used_elsewhere and not missing_client and not missing_crc and all(report['checks']['portal_layouts_present'].values()) and all(c['mouth_matches_hole'] for c in report['caves'])
    print('snapshot:', 'PASS' if ok else 'CHECK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
