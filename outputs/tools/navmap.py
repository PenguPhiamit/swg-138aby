"""Floor plans of building interiors from the client's floor meshes (Claude, 15 Oct 2026; owner: "try and find a way to
actually track them and map the navmesh"). Indoors, Core3 paths every body over each cell's floor mesh
(src/templates/appearance/FloorMesh.cpp): the triangles are where a body can stand; an edge with flag 0 is uncrossable
(a wall), 1 joins two triangles, 2 blocks. This reads the same files from the owner's client archives (read-only, our
own reader in swgfmt) and writes one JSON per building that live_map.py draws under the bots' positions.

    python navmap.py build <planet> <building object id>   # e.g. endor 5996314, the Death Watch bunker
    python navmap.py find <planet> <template part>         # buildings in that planet's world snapshot

Coordinates are cell-local, the frame a bot reports inside a cell: x and y on the floor plan are the mesh's x and z
(SWG meshes are y-up), height is the mesh's y. Output: Bot-reports/navmaps/<planet>-<building>.json (not in git: it is
derived from the client's files).
"""
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'Bot-reports' / 'navmaps'
sys.path.insert(0, str(HERE))
from swgfmt import trn_iff, ws_read  # noqa: E402


def forms(nodes, kind):
    """Every FORM of this type, depth first, in file order."""
    for n in nodes:
        if n.is_form:
            if n.form == kind:
                yield n
            yield from forms(n.children, kind)


def chunk(nodes, tag):
    for n in nodes:
        if n.is_form:
            found = chunk(n.children, tag)
            if found is not None:
                return found
        elif n.tag == tag:
            return n
    return None


def floor_mesh(data):
    """(vertices, triangles) of a .flr: triangles as (i0, i1, i2, edge flags (3), neighbours (3))."""
    nodes = trn_iff.parse(data)
    vert, tris = chunk(nodes, 'VERT'), chunk(nodes, 'TRIS')
    if vert is None or tris is None:
        return [], []
    count = struct.unpack_from('<i', vert.data, 0)[0]
    vertices = [struct.unpack_from('<3f', vert.data, 4 + 12 * i) for i in range(count)]
    n = struct.unpack_from('<i', tris.data, 0)[0]
    size = (len(tris.data) - 4) // n if n else 60
    out = []
    for k in range(n):
        base = 4 + size * k
        i0, i1, i2, _tid, n0, n1, n2 = struct.unpack_from('<3iI3i', tris.data, base)
        flags = struct.unpack_from('<3B', tris.data, base + 40)   # after 3 ints, an id, 3 neighbours, a normal
        out.append((i0, i1, i2, flags, (n0, n1, n2)))
    return vertices, out


def snapshot(planet):
    nodes, _ = ws_read.read_ws(trn_iff.load(f'client:snapshot/{planet}.ws'))
    return nodes


def build(planet, building_id):
    nodes = snapshot(planet)
    building = next(n for n in nodes if n['id'] == building_id)
    cells = {n['cell_index']: n['id'] for n in nodes if n['parent'] == building_id}
    index = trn_iff.client_index()
    template = building['template']
    name = template.rsplit('/', 1)[-1].replace('shared_', '').replace('.iff', '')
    path = next((p for p in index if p.endswith('.pob') and name in p), None)
    if path is None:  # read the object template for its portal layout name
        obj = trn_iff.client_file(template if template.startswith('object/') else next(p for p in index if p.endswith(template)))
        m = re.search(rb'appearance/[\w./-]+\.pob', obj)
        path = m.group(0).decode() if m else None
    if path is None:
        raise SystemExit(f'no portal layout found for {template}')
    pob = trn_iff.parse(trn_iff.client_file(path))
    plan = {'planet': planet, 'building': building_id, 'template': template, 'portal_layout': path,
            'world': {'x': round(building['x'], 1), 'y': round(building['y'], 1), 'z': round(building['z'], 1)},
            'cells': []}
    for i, cell in enumerate(forms(pob, 'CELL')):
        raw = trn_iff.build([cell])
        m = re.search(rb'appearance/collision/[\w./-]+\.flr', raw)
        entry = {'index': i, 'oid': cells.get(i), 'floor': m.group(0).decode() if m else None, 'tris': [], 'walls': [],
                 'blocks': []}
        if entry['floor'] and entry['floor'] in index:
            vertices, tris = floor_mesh(trn_iff.client_file(entry['floor']))
            heights = []
            for i0, i1, i2, flags, _ in tris:
                corners = [vertices[i0], vertices[i1], vertices[i2]]
                entry['tris'].append([[round(v[0], 2), round(v[2], 2)] for v in corners])
                heights += [v[1] for v in corners]
                for e, (a, b) in enumerate(((0, 1), (1, 2), (2, 0))):
                    seg = [round(corners[a][0], 2), round(corners[a][2], 2), round(corners[b][0], 2), round(corners[b][2], 2)]
                    if flags[e] == 0:
                        entry['walls'].append(seg)
                    elif flags[e] == 2:
                        entry['blocks'].append(seg)
            if heights:
                entry['height'] = round(sum(heights) / len(heights), 1)
        m = re.search(r'_r\d+_?([a-z]*)', entry['floor'] or '')
        entry['room'] = (m.group(1) if m and m.group(1) else 'room') + f' {i}'
        plan['cells'].append(entry)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f'{planet}-{building_id}.json'
    target.write_text(json.dumps(plan), encoding='utf-8')
    walls = sum(len(c['walls']) for c in plan['cells'])
    print(f"{target.name}: {len(plan['cells'])} cells, {sum(len(c['tris']) for c in plan['cells'])} triangles, "
          f"{walls} wall edges, cells with a server id: {sum(1 for c in plan['cells'] if c['oid'])}")
    return target


def find(planet, part):
    for n in snapshot(planet):
        if n['parent'] == 0 and part in n['template']:
            kids = sum(1 for _ in n['children'])
            print(n['id'], n['template'], round(n['x']), round(n['y']), f'{kids} cells')


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'build':
        build(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) >= 4 and sys.argv[1] == 'find':
        find(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
