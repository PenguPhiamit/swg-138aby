"""Append the o7 statics (statics.json) to the Ossus world snapshot. Our own code (Claude, 16 Oct 2026), on Fable's
o2 reader/writer (Fable-ossus/o2/tools/ws_write.py, which round-trips MTG's hoth.ws and the stock snapshots byte for byte).

    python -I append_snapshot.py [--out FILE] [--stage]

default   read Fable-ossus/o2/staged/client/snapshot/ossus.ws (87 nodes), add every object of ../statics.json, write
          ../out/ossus.ws (not committed) and print the checks
--out F   write F instead
--stage   write Fable-ossus/o2/staged/client/snapshot/ossus.ws itself (the real step; rerunnable: it first drops any
          node whose id is in the o7 range, so running it twice gives the same file)

Checks (all printed, exit 1 on a failure): byte round trip of the result; ids unique and unused by every snapshot the client
loads; every template in the client archives and in the merged object CRC table; node count; building cell ids in range.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from o7_common import EXISTING_WS, O7, OSSUS, client_idx, crc_tables, jload  # noqa: E402
sys.path.insert(0, os.path.join(OSSUS, 'o2', 'tools'))
import ws_write  # noqa: E402  (adds the Fable-hoth-caves/tools path that holds the ws_read shim)
import ws_read  # noqa: E402

CELL = 'object/cell/shared_cell.iff'


def quat(yaw):
    h = math.radians(yaw)
    return (math.cos(h / 2), 0.0, math.sin(h / 2), 0.0)


def build(statics, base_path):
    data = open(base_path, 'rb').read()
    nodes, templates = ws_read.read_ws(data)
    top = ws_write.tree_from_reader(nodes)
    lo, hi = statics['first_id'], statics['last_id']
    kept = [n for n in top if not (lo <= n['id'] <= hi)]
    dropped = len(top) - len(kept)
    templates = list(templates)
    new_nodes = []
    for o in statics['objects']:
        if o['template'] not in templates:
            templates.append(o['template'])
        node = {'id': o['id'], 'parent': 0, 'template': o['template'], 'cell_index': 0, 'quat': quat(o['yaw']), 'x': o['x'], 'z': o['z'], 'y': o['y'],
                'game_object_type': float(o['node_float']), 'unknown': int(o.get('pob_crc', 0)), 'child_nodes': []}
        if o['kind'] == 'building':
            if CELL not in templates:
                templates.append(CELL)
            for k in range(1, o['cells']):
                node['child_nodes'].append({'id': o['id'] + k, 'parent': o['id'], 'template': CELL, 'cell_index': k, 'quat': (1.0, 0.0, 0.0, 0.0),
                                            'x': 0.0, 'z': 0.0, 'y': 0.0, 'game_object_type': 0.0, 'unknown': 0, 'child_nodes': []})
        new_nodes.append(node)
    out = ws_write.write_ws(kept + new_nodes, templates)
    return out, {'base_nodes': len(nodes), 'dropped_o7_nodes': dropped, 'templates': len(templates), 'new_top_nodes': len(new_nodes)}


def check(out, statics):
    problems = []
    nodes, templates = ws_read.read_ws(out)
    rt = ws_write.write_ws(ws_write.tree_from_reader(nodes), templates) == out
    ids = [n['id'] for n in nodes]
    if not rt:
        problems.append('byte round trip differs')
    if len(set(ids)) != len(ids):
        problems.append('duplicate ids')
    mine = set(range(statics['first_id'], statics['last_id'] + 1))
    idx = client_idx()
    from swgfmt import trn_iff
    clash = []
    for name in sorted(k for k in idx if k.startswith('snapshot/') and k.endswith('.ws')):
        other = {n['id'] for n in ws_read.read_ws(trn_iff.client_file(name))[0]}
        if other & mine:
            clash.append(name)
    if clash:
        problems.append('ids used by other snapshots: %s' % clash)
    stock, merged = crc_tables()
    miss_client = [t for t in templates if t.lower() not in idx]
    miss_crc = [t for t in templates if t not in merged]
    if miss_client:
        problems.append('templates not in the client archives: %s' % miss_client)
    if miss_crc:
        problems.append('templates not in the merged CRC table: %s' % miss_crc)
    placed = {n['id']: n for n in nodes}
    for o in statics['objects']:
        n = placed.get(o['id'])
        if n is None or abs(n['x'] - o['x']) > 0.01 or abs(n['y'] - o['y']) > 0.01 or abs(n['z'] - o['z']) > 0.01 or n['template'] != o['template']:
            problems.append('object %d not read back as written' % o['id'])
            break
        if o['kind'] == 'building' and len(n['children']) != o['cells'] - 1:
            problems.append('building %d has %d cell nodes, expected %d' % (o['id'], len(n['children']), o['cells'] - 1))
    top = [n for n in nodes if n['depth'] == 0]
    return problems, {'bytes': len(out), 'nodes': len(nodes), 'world_level': len(top), 'templates': len(templates), 'round_trip_identical': rt,
                      'ids': [min(ids), max(ids)], 'ids_clash_with_client_snapshots': clash, 'templates_missing_in_client': miss_client,
                      'templates_missing_in_merged_crc': miss_crc}


def main(argv):
    statics = jload(os.path.join(O7, 'statics.json'))
    out_path = os.path.join(O7, 'out', 'ossus.ws')
    if '--out' in argv:
        out_path = argv[argv.index('--out') + 1]
    if '--stage' in argv:
        out_path = EXISTING_WS
    out, info = build(statics, EXISTING_WS)
    problems, rep = check(out, statics)
    rep.update(info)
    print(rep)
    if problems:
        print('PROBLEMS:', problems)
        return 1
    with open(out_path, 'wb') as f:
        f.write(out)
    print('wrote', out_path, '(%d bytes)' % len(out))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
