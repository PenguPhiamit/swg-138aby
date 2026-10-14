"""Read a SWG world snapshot (.ws) the way Core3 does, and verify cave spawn cell IDs against it.
Our own code (Fable, 14 Oct 2026). Layout from Core3-dev src/templates/snapshot/WorldSnapshotIff.cpp and
WorldSnapshotNode.h: FORM WSNP > FORM 0001 > FORM NODS (FORM NODE > FORM 0000 > DATA + child NODEs) + chunk OTNL.
NODE DATA: objectID, parentID, nameID (index into OTNL), cellIndex, quaternion w x y z, position x z y (Core3 reads
x, z, y and stores (x, z, y)), gameObjectType float, unknown int.

    python -I ws_read.py list <spec>                       # every node: id, parent, template, cell index, position
    python -I ws_read.py verify <spec> <bellum_caves.lua>  # JSON report on every spawn's cell ID

<spec>: a file path, or client:snapshot/hoth.ws (owner's client archives, stock first then MTG). The IFF code comes
from ../../Fable-planet-test/tools/trn_iff.py.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
from .trn_iff import Reader, load, parse  # noqa: E402


def read_ws(data):
    """Return (nodes, templates). nodes: list of dicts in file order, each with children ids."""
    root = parse(data)
    wsnp = root[0]
    assert wsnp.is_form and wsnp.form == 'WSNP', wsnp
    ver = wsnp.children[0]
    assert ver.is_form and ver.form == '0001', ver
    nods = ver.children[0]
    assert nods.is_form and nods.form == 'NODS', nods
    otnl = ver.children[1]
    assert otnl.tag == 'OTNL', otnl
    r = Reader(otnl.data)
    templates = [r.cstr() for _ in range(r.i32())]
    nodes = []

    def parse_node(node, depth):
        assert node.is_form and node.form == 'NODE', node
        v = node.children[0]
        assert v.is_form and v.form == '0000', v
        d = v.children[0]
        assert d.tag == 'DATA', d
        r = Reader(d.data)
        rec = {'id': r.u32(), 'parent': r.u32(), 'name_id': r.u32(), 'cell_index': r.u32(),
               'quat': (r.f32(), r.f32(), r.f32(), r.f32()), 'x': r.f32(), 'z': r.f32(), 'y': r.f32(),
               'game_object_type': r.f32(), 'unknown': r.u32(), 'depth': depth, 'children': []}
        rec['template'] = templates[rec['name_id']] if rec['name_id'] < len(templates) else '?'
        nodes.append(rec)
        for child in v.children[1:]:
            rec['children'].append(parse_node(child, depth + 1))
        return rec['id']

    for node in nods.children:
        parse_node(node, 0)
    return nodes, templates


BELLUM_ROW = re.compile(r'\{\s*"([a-z0-9_]+)"\s*,\s*(\d+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*(\d+)\s*\}')
BELLUM_CAVE = re.compile(r'--\s*([a-z0-9_]+) at \[([-\d.]+), ([-\d.]+), ([-\d.]+)\] \(building (\d+)\)')


def read_bellum(path):
    """Spawn rows and cave comment lines from Bellum's generated screenplay (read as text)."""
    rows, caves, current = [], {}, None
    for line in open(path, encoding='utf-8'):
        m = BELLUM_CAVE.search(line)
        if m:
            current = int(m.group(5))
            caves[current] = {'name': m.group(1), 'x': float(m.group(2)), 'z': float(m.group(3)), 'y': float(m.group(4))}
            continue
        m = BELLUM_ROW.search(line)
        if m:
            rows.append({'template': m.group(1), 'respawn': int(m.group(2)), 'x': float(m.group(3)), 'z': float(m.group(4)),
                         'y': float(m.group(5)), 'heading': float(m.group(6)), 'cell': int(m.group(7)), 'cave_comment': current})
    return rows, caves


def verify(ws_spec, bellum_path):
    nodes, templates = read_ws(load(ws_spec))
    by_id = {n['id']: n for n in nodes}
    rows, caves = read_bellum(bellum_path)
    report = {'snapshot': ws_spec, 'nodes': len(nodes), 'world_level': sum(1 for n in nodes if n['parent'] == 0),
              'templates': templates, 'bellum_rows': len(rows), 'caves': {}, 'rows': [], 'kept': 0, 'skipped': 0,
              'missing_cells': sorted({r['cell'] for r in rows if r['cell'] not in by_id})}
    for bid, c in caves.items():
        n = by_id.get(bid)
        entry = dict(c, building_in_snapshot=n is not None)
        if n:
            entry.update(template=n['template'], snapshot_x=n['x'], snapshot_z=n['z'], snapshot_y=n['y'],
                         position_matches=abs(n['x'] - c['x']) < 0.6 and abs(n['y'] - c['y']) < 0.6 and abs(n['z'] - c['z']) < 0.6,
                         cells=[k for k in n['children'] if by_id[k]['template'].endswith('shared_cell.iff')])
        report['caves'][str(bid)] = entry
    per_cave = {}
    for r in rows:
        cell = by_id.get(r['cell'])
        ok = cell is not None and cell['template'].endswith('shared_cell.iff') and cell['parent'] == r['cave_comment']
        reason = ('ok' if ok else 'cell id not in MTG snapshot' if cell is None else
                  'not a cell' if not cell['template'].endswith('shared_cell.iff') else
                  f'cell belongs to building {cell["parent"]}, not {r["cave_comment"]}')
        r2 = dict(r, keep=ok, reason=reason, cell_index=cell['cell_index'] if cell else None)
        report['rows'].append(r2)
        k = per_cave.setdefault(str(r['cave_comment']), {'kept': 0, 'skipped': 0})
        k['kept' if ok else 'skipped'] += 1
        report['kept' if ok else 'skipped'] += 1
    report['per_cave'] = per_cave
    return report


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[0] == 'list':
        nodes, templates = read_ws(load(argv[1]))
        print(f'{len(nodes)} nodes, {sum(1 for n in nodes if n["parent"] == 0)} at world level, {len(templates)} templates')
        for n in nodes:
            pad = '  ' * n['depth']
            print(f'{pad}{n["id"]} parent {n["parent"]} cell#{n["cell_index"]} {n["template"].split("/")[-1]} at ({n["x"]:.1f}, {n["z"]:.1f}, {n["y"]:.1f})')
        return 0
    if argv[0] == 'verify' and len(argv) >= 3:
        rep = verify(argv[1], argv[2])
        print(json.dumps({k: v for k, v in rep.items() if k != 'rows'}, indent=1))
        print(f'kept {rep["kept"]}, skipped {rep["skipped"]}, per cave {rep["per_cave"]}')
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


def ws_objects(buf):
    """(object id, parent id, template, x, height, y) for every node of a .ws snapshot, in file order (the shape
    tools/hoth/hoth_snapshot.py reads)."""
    nodes = read_ws(buf)
    nodes = nodes['nodes'] if isinstance(nodes, dict) else nodes[0] if isinstance(nodes, tuple) else nodes
    return [(n['id'], n['parent'], n['template'], n['x'], n['z'], n['y']) for n in nodes]
