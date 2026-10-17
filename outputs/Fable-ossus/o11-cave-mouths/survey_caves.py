"""O11: where the planet's ground pokes through the sunken entrances of the three O7 flatland caves (Claude, 17 Oct 2026).

For each cave: the r0 (outside) collision floor of its portal layout, moved to the world with the snapshot node, against
the server's terrain height (the Core3 port of the terrain in a given archive). Floor points more than TOL below the
ground are where the owner walks "through the floor": the drawn ground covers the ramp.

    C:/Users/Pengw/miniconda3/python.exe -I survey_caves.py [ARCHIVE]      # default: the installed run-28 archive
Prints a summary and writes ./survey-<archive sha prefix>.json.
"""
import hashlib
import json
import math
import os
import re
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OSSUS = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OSSUS)
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OSSUS, 'o7-build', 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt.trn_iff import client_file, parse  # noqa: E402
from o7_common import Terrain, rot  # noqa: E402

DEFAULT_ARCHIVE = os.path.join(H, 'work', 'chain-run28', 'local_planets-run28.tre')
TOL = 0.05
CAVES = {   # snapshot node id -> name (statics.json)
    6900107: 'sanctuary (cave_06_flatland_s01_damprock)',
    6900193: 'vault (cave_07_flatland_s02)',
    6900295: 'adit (cave_08_flatland_s03)',
}


def find(node, tag):
    for c in node.children:
        if not c.is_form and c.tag == tag:
            return c
        if c.is_form:
            x = find(c, tag)
            if x is not None:
                return x
    return None


def r0_floor(template):
    """(vertices, triangles) of the r0 collision floor, building space (x right, y up, z forward)."""
    d = client_file(template)
    pob = re.findall(rb'appearance/[A-Za-z0-9_/\.]+\.pob', d)[0].decode()
    root = parse(client_file(pob))[0]
    cels = [c for c in root.children[0].children if c.is_form and c.form == 'CELS'][0]
    data = [x for x in cels.children[0].children[0].children if not x.is_form and x.tag == 'DATA'][0].data
    pos = 4 + 1
    name_end = data.index(b'\0', pos)
    pos = name_end + 1
    app_end = data.index(b'\0', pos)
    pos = app_end + 1
    assert data[pos] == 1, 'r0 has no floor'
    flr = data[pos + 1:data.index(b'\0', pos + 1)].decode()
    fr = parse(client_file(flr))[0]
    vt, tr = find(fr, 'VERT'), find(fr, 'TRIS')
    verts = [struct.unpack_from('<3f', vt.data, 12 * i) for i in range(len(vt.data) // 12)]
    nt = struct.unpack_from('<i', tr.data, 0)[0]
    size = (len(tr.data) - 4) // nt
    tris = [struct.unpack_from('<3i', tr.data, 4 + size * t) for t in range(nt)]
    return pob, flr, verts, tris


def load_terrain(archive_bytes):
    files = tre_write.read(archive_bytes)[0]
    tmp = tempfile.mkdtemp(prefix='o11-trn-')
    for rel in ('terrain/ossus.trn', 'terrain/ossus_academy.tga', 'terrain/ossus_canyon.tga', 'terrain/ossus_mesa.tga'):
        path = os.path.join(tmp, *rel.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(files[rel])
    return Terrain(os.path.join(tmp, 'terrain', 'ossus.trn'), tmp), hashlib.sha256(files['terrain/ossus.trn']).hexdigest()


def cave_nodes():
    statics = json.load(open(os.path.join(OSSUS, 'o7-build', 'statics.json'), encoding='utf-8'))
    return {o['id']: o for o in statics['objects'] if o['id'] in CAVES}


def survey(terrain, nodes):
    out = {}
    for nid, name in CAVES.items():
        o = nodes[nid]
        pob, flr, verts, tris = r0_floor(o['template'])
        pts = []
        for vx, vy, vz in verts:
            ex, ny = rot(vx, vz, o['yaw'])
            wx, wy, wz = o['x'] + ex, o['y'] + ny, o['z'] + vy
            pts.append({'local': (round(vx, 2), round(vy, 2), round(vz, 2)), 'world': (round(wx, 2), round(wy, 2)), 'floor': round(wz, 2),
                        'ground': round(terrain.h(wx, wy), 2)})
        # triangle centroids too: the ground can poke up between vertices
        cents = []
        for a, b, c in tris:
            vx = (verts[a][0] + verts[b][0] + verts[c][0]) / 3
            vy = (verts[a][1] + verts[b][1] + verts[c][1]) / 3
            vz = (verts[a][2] + verts[b][2] + verts[c][2]) / 3
            ex, ny = rot(vx, vz, o['yaw'])
            wx, wy = o['x'] + ex, o['y'] + ny
            cents.append({'local': (round(vx, 2), round(vy, 2), round(vz, 2)), 'world': (round(wx, 2), round(wy, 2)), 'floor': round(o['z'] + vy, 2),
                          'ground': round(terrain.h(wx, wy), 2)})
        allp = pts + cents
        under = [p for p in allp if p['ground'] > p['floor'] + TOL]
        out[name] = {
            'node': {k: o[k] for k in ('id', 'template', 'x', 'y', 'z', 'yaw')}, 'pob': pob, 'r0_floor': flr,
            'samples': len(allp), 'floor_under_ground': len(under),
            'worst_ground_above_floor_m': round(max((p['ground'] - p['floor'] for p in allp), default=0), 2),
            'under_local_z_range': [min(p['local'][2] for p in under), max(p['local'][2] for p in under)] if under else None,
            'under_local_x_range': [min(p['local'][0] for p in under), max(p['local'][0] for p in under)] if under else None,
            'floor_min': min(p['floor'] for p in allp), 'under_points': under,
        }
    return out


def main(argv):
    archive = argv[0] if argv else DEFAULT_ARCHIVE
    data = open(archive, 'rb').read()
    terrain, trn_sha = load_terrain(data)
    rep = {'archive': os.path.relpath(archive, H).replace(os.sep, '/'), 'archive_sha256': hashlib.sha256(data).hexdigest(),
           'trn_sha256': trn_sha, 'tolerance_m': TOL, 'caves': survey(terrain, cave_nodes())}
    with open(os.path.join(HERE, 'survey-%s.json' % rep['archive_sha256'][:8]), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    print('archive', rep['archive_sha256'][:8], 'trn', trn_sha[:8])
    for name, c in rep['caves'].items():
        print('%-45s samples %4d  floor under ground %4d  worst %.2f m  local z %s  x %s' % (
            name, c['samples'], c['floor_under_ground'], c['worst_ground_above_floor_m'], c['under_local_z_range'], c['under_local_x_range']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
