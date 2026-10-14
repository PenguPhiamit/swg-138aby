"""Write a SWG world snapshot (.ws) the way Core3 and the client read it, with an exact round trip of the files
in the owner's archives. Our own code (Fable, 14 Oct 2026); layout from Core3-dev src/templates/snapshot/
WorldSnapshotIff.cpp + WorldSnapshotNode.h, the same the reader in Fable-hoth-caves/tools/ws_read.py follows.

    python -I ws_write.py roundtrip client:snapshot/hoth.ws [more specs...]   # parse -> write -> compare bytes

FORM WSNP > FORM 0001 > FORM NODS (FORM NODE > FORM 0000 > DATA + child NODEs) + chunk OTNL.
NODE DATA (52 bytes): u32 objectID, u32 parentID, u32 nameID (index into OTNL), u32 cellIndex, quaternion w x y z,
position x z y, f32 gameObjectType (512 buildings, 1024 statics, 0 cells), u32 the SOE CRC of the template name
(0 for cells). OTNL: i32 count, then the template names, zero-terminated.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'Fable-hoth-caves', 'tools'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from trn_iff import Writer, build, chunk, form, load  # noqa: E402
import ws_read  # noqa: E402


def node_form(n, templates_index):
    w = (Writer().u32(n['id']).u32(n['parent']).u32(templates_index[n['template']]).u32(n['cell_index']))
    for v in n['quat']:
        w.f32(v)
    w.f32(n['x']).f32(n['z']).f32(n['y']).f32(n['game_object_type']).u32(n['unknown'])
    return form('NODE', form('0000', chunk('DATA', w.bytes()), *[node_form(c, templates_index) for c in n.get('child_nodes', [])]))


def write_ws(top_nodes, templates):
    """top_nodes: list of node dicts (id, parent, template, cell_index, quat, x, z, y, game_object_type, unknown,
    child_nodes); templates: the OTNL list in order."""
    index = {t: i for i, t in enumerate(templates)}
    w = Writer().i32(len(templates))
    for t in templates:
        w.cstr(t)
    return build([form('WSNP', form('0001', form('NODS', *[node_form(n, index) for n in top_nodes]), chunk('OTNL', w.bytes())))])


def tree_from_reader(nodes):
    """ws_read's flat list (with children ids) -> nested dicts with child_nodes."""
    by_id = {n['id']: n for n in nodes}
    for n in nodes:
        n['child_nodes'] = [by_id[c] for c in n['children']]
    return [n for n in nodes if n['depth'] == 0]


def roundtrip(spec):
    data = load(spec)
    nodes, templates = ws_read.read_ws(data)
    back = write_ws(tree_from_reader(nodes), templates)
    return back == data, len(data), len(nodes)


def main(argv):
    if len(argv) < 2 or argv[0] != 'roundtrip':
        print(__doc__)
        return 2
    status = 0
    for spec in argv[1:]:
        ok, n, count = roundtrip(spec)
        print(f'{"IDENTICAL" if ok else "DIFFERENT"} {n:8d} B {count:6d} nodes  {spec}')
        status |= 0 if ok else 1
    return status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
