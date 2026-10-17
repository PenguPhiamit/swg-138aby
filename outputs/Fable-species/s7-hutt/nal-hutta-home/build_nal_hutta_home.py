"""PL-04: Nal Hutta as the Hutt home, the client half = the installed archive + a dressed Bilbousa (Claude, 17 Oct 2026).

Darklight's Bilbousa snapshot (snapshot/hutta.ws, 25,795 B, 281 nodes, in MTG's mtg_patch_022.tre) and MTG's client
region table (datatables/clientregion/hutta.iff, in mtg_planets.tre) are not in local_planets.tre yet. Both sides load
local_planets.tre ahead of the MTG archives (client priority 49; first in the server's Core3.TreFiles), so this step adds
our copies of the two files there:
  snapshot/hutta.ws                     Darklight's 281 nodes byte for byte in content (re-read and compared node by
                                        node), plus the 29 statics of ../home.json (ids 7170001-7170029): two new
                                        Jabba-palace towers (the Tashuga and Bessolo kajidic seats), 12 stock banners and
                                        12 warm street lamps at the six seats' entrances, a round fountain and two lamps
                                        at the head of the bazaar. Stock templates only.
  datatables/clientregion/hutta.iff     the one Bilbousa row moves from (-746, 1645) r 300 to (-747, 1590) r 400, so the
                                        name covers the council palace (y 1260-1420) and the two new seats; same key
Every other entry of the base comes through byte for byte (checked). Nothing is installed.

    C:/Users/Pengw/miniconda3/python.exe -I build_nal_hutta_home.py [--base PATH] [--out PATH]
Default base: ../../../../work/chain-1016/local_planets-chain-1016.tre (installed for run 19, sha256 df1d538e...).
Default out:  ../../../../work/nal-hutta-home/local_planets-nalhutta-home.tre (+ .sha256); checks in ./checks.json.
Run tools/make_home.py first (it writes ../home.json); this step refuses a home.json with problems.
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o2', 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
import ws_write  # noqa: E402  (adds the ws_read path)
import ws_read  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'chain-1016', 'local_planets-chain-1016.tre')
BASE_SHA_PREFIX = 'df1d538e'
DEFAULT_OUT = os.path.join(H, 'work', 'nal-hutta-home', 'local_planets-nalhutta-home.tre')
WS, REGIONS = 'snapshot/hutta.ws', 'datatables/clientregion/hutta.iff'
# the MTG originals this step starts from (read-only from the owner's client folder)
SOURCES = {WS: ('mtg_patch_022.tre', 25795), REGIONS: ('mtg_planets.tre', None)}
BILBOUSA_ROW = ['@hutta_region_names:bilbousa', -747.0, 1590.0, 400.0]
CELL = 'object/cell/shared_cell.iff'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def quat(yaw):
    h = math.radians(yaw)
    return (math.cos(h / 2), 0.0, math.sin(h / 2), 0.0)


def source(name):
    archive, size = SOURCES[name]
    data = trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, archive), name)
    assert data is not None, '%s not in %s' % (name, archive)
    if size is not None:
        assert len(data) == size, '%s: %d bytes, expected %d' % (name, len(data), size)
    return data


def node_key(n):
    return (n['id'], n['parent'], n['template'], n['cell_index'], tuple(round(v, 6) for v in n['quat']), round(n['x'], 4), round(n['z'], 4),
            round(n['y'], 4), n['game_object_type'], n['unknown'], tuple(n['children']))


def build_snapshot(base_ws, home):
    nodes, templates = ws_read.read_ws(base_ws)
    rt = ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(base_ws)[0]), templates)
    assert rt == base_ws, 'Darklight snapshot does not round-trip through ws_write'
    top = ws_write.tree_from_reader(nodes)
    ids = {n['id'] for n in nodes}
    templates = list(templates)
    new = []
    for s in home['statics']:
        assert s['id'] not in ids, s['id']
        if s['template'] not in templates:
            templates.append(s['template'])
        info = s.get('cells', 0)
        assert not info, 'cell buildings are not placed by this step'
        new.append({'id': s['id'], 'parent': 0, 'template': s['template'], 'cell_index': 0, 'quat': quat(s['yaw']), 'x': s['x'], 'z': s['z'], 'y': s['y'],
                    # Darklight's file uses 512 for every node, statics included, and 0 in the last field for buildings
                    # without a portal layout (the four existing towers); the new nodes follow the file's own convention
                    'game_object_type': 512.0, 'unknown': 0, 'child_nodes': []})
    out = ws_write.write_ws(top + new, templates)
    return out, {'base_nodes': len(nodes), 'new_nodes': len(new), 'templates': len(templates)}


def check_snapshot(out, base_ws, home):
    problems = []
    nodes, templates = ws_read.read_ws(out)
    base_nodes, _ = ws_read.read_ws(base_ws)
    if ws_write.write_ws(ws_write.tree_from_reader(ws_read.read_ws(out)[0]), templates) != out:
        problems.append('result does not round-trip')
    got = {n['id']: n for n in nodes}
    same = sum(1 for b in base_nodes if b['id'] in got and node_key(got[b['id']]) == node_key(b))
    if same != len(base_nodes):
        problems.append('only %d of %d Darklight nodes read back unchanged' % (same, len(base_nodes)))
    ids = [n['id'] for n in nodes]
    if len(set(ids)) != len(ids):
        problems.append('duplicate ids')
    mine = set(range(home['first_id'], home['last_id'] + 1))
    clash = []
    idx = trn_iff.client_index()
    for name in sorted(k for k in idx if k.startswith('snapshot/') and k.endswith('.ws') and k != WS):
        other = {n['id'] for n in ws_read.read_ws(trn_iff.client_file(name))[0]}
        if other & mine:
            clash.append(name)
    if clash:
        problems.append('ids used by other snapshots: %s' % clash)
    for s in home['statics']:
        n = got.get(s['id'])
        if n is None or n['template'] != s['template'] or abs(n['x'] - s['x']) > 0.01 or abs(n['y'] - s['y']) > 0.01 or abs(n['z'] - s['z']) > 0.01:
            problems.append('static %d not read back as written' % s['id'])
    sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o7-build', 'tools'))
    from o7_common import crc_tables
    stock, _merged = crc_tables()
    missing = sorted({s['template'] for s in home['statics']} - stock)
    if missing:
        problems.append('templates not in the stock CRC table: %s' % missing)
    return problems, {'bytes': len(out), 'nodes': len(nodes), 'world_level': sum(1 for n in nodes if n['depth'] == 0), 'templates': len(templates),
                      'darklight_nodes_unchanged': same, 'ids_clash_with_client_snapshots': clash, 'new_ids': [home['first_id'], home['last_id']]}


def build_regions(base_tbl):
    t = st.read_dtii(base_tbl)
    assert st.write_dtii(t) == base_tbl, 'clientregion/hutta.iff does not round-trip'
    assert [r[0] for r in t['rows']] == [BILBOUSA_ROW[0]], t['rows']
    old = t['rows'][0]
    out = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': [BILBOUSA_ROW]})
    assert st.read_dtii(out)['rows'] == [BILBOUSA_ROW]
    return out, {'before': old, 'after': BILBOUSA_ROW}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    home = json.load(open(os.path.join(HERE, 'home.json'), encoding='utf-8'))
    assert not home['problems'], 'home.json has problems: rerun tools/make_home.py'
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(BASE_SHA_PREFIX), 'default base is not the df1d538e archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    for name in (WS, REGIONS):
        assert name not in base, '%s is already in the base; this step expects the MTG original only' % name

    src = {name: source(name) for name in (WS, REGIONS)}
    files = dict(base)
    report = {'sources': {name: {'archive': SOURCES[name][0], 'bytes': len(b), 'sha256': sha(b)} for name, b in src.items()}}
    files[WS], report['snapshot'] = build_snapshot(src[WS], home)
    problems, rep = check_snapshot(files[WS], src[WS], home)
    report['snapshot'].update(rep)
    files[REGIONS], report['regions'] = build_regions(src[REGIONS])

    data = tre_write.pack(files)
    back = tre_write.read(data)[0]
    unchanged = [k for k in base if back.get(k) == base[k]]
    if len(unchanged) != len(base):
        problems.append('only %d of %d base entries byte-identical' % (len(unchanged), len(base)))
    extra = sorted(set(back) - set(base))
    if extra != sorted([WS, REGIONS]):
        problems.append('unexpected new entries: %s' % extra)
    if problems:
        print('PROBLEMS:', problems)
        return 1
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(data)
    out_sha = sha(data)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))
    report.update({
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha, 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(data), 'sha256': out_sha, 'entries': len(back)},
        'base_entries_byte_identical': len(unchanged), 'new_entries': extra,
        'entries_sha256': {k: sha(back[k]) for k in extra},
    })
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=1)
        f.write('\n')
    print(json.dumps({k: report[k] for k in ('base', 'out', 'base_entries_byte_identical', 'new_entries')}, indent=1))
    print('snapshot', report['snapshot'])
    print('regions', report['regions'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
