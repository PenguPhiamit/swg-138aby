"""PL-02: Ossus people, the client half = any base archive + the memorial-road badge (Claude, 16 Oct 2026).

The server half (screenplays/sandbox/ossus_people.lua) awards badge 140 at the end of the memorial road. Core3 reads
the badge list from datatables/badge/badge_map.iff in the archives it loads, and the client shows the badge from
the same table, so both read this archive:
  datatables/badge/badge_map.iff        the base's copy if it has one, else the stock client's (140 rows, 0-139),
                                        + row 140 bdg_exp_oss_memorial_road (exploration, category 2, shown)
  string/en/badge_n.stf, badge_d.stf    + the badge's name and description (our text); the base's copies, else the client's
Every other entry of the base comes through byte for byte (checked). Nothing is installed.

    C:/Users/Pengw/miniconda3/python.exe -I build_ossus_people.py [--base PATH] [--out PATH]
Default base: ../../../work/ossus-o7/local_planets-ossus-o7.tre (the PL-01 step's output, sha256 efeff508...).
Default out:  ../../../work/ossus-o7/local_planets-ossus-people.tre (+ .sha256), checks in ./checks-people.json.
Badge 140 must be free in the base: the step stops if another step already used the index or the key.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'ossus-o7', 'local_planets-ossus-o7.tre')
DEFAULT_BASE_SHA_PREFIX = 'efeff508'
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-o7', 'local_planets-ossus-people.tre')
BADGE_MAP = 'datatables/badge/badge_map.iff'
BADGE_N, BADGE_D = 'string/en/badge_n.stf', 'string/en/badge_d.stf'
# INDEX, KEY, MUSIC, CATEGORY, SHOW, TYPE: the shape of the stock exploration rows (exp_dan_jedi_temple is 30)
BADGE = [140, 'bdg_exp_oss_memorial_road', 'sound/music_acq_miner.snd', 2, 1, 'exploration_jedi']
NAME = 'Location: The Memorial Road of Ossus'
DESC = "...has walked the pilgrims' road from Knossa to the ruined Jedi academy on Ossus."
TOUCHED = {BADGE_MAP, BADGE_N, BADGE_D}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def source(base, rel):
    if rel in base:
        return base[rel], 'base'
    data = trn_iff.client_file(rel)
    assert data is not None, rel
    return data, trn_iff.client_index()[rel]


def merge_badge_map(data):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'badge_map.iff: source does not round-trip'
    assert t['columns'] == ['INDEX', 'KEY', 'MUSIC', 'CATEGORY', 'SHOW', 'TYPE'], t['columns']
    assert BADGE[0] not in {r[0] for r in t['rows']}, 'badge index %d already used' % BADGE[0]
    assert BADGE[1] not in {r[1] for r in t['rows']}, 'badge key already used'
    assert BADGE[0] < 160, 'Core3 keeps 5 x 32 badge bits'
    assert BADGE[5] in {r[5] for r in t['rows']}, 'badge type not used by any stock row'
    rows = t['rows'] + [list(BADGE)]
    out = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    assert st.read_dtii(out)['rows'][:-1] == t['rows']
    return out, {'rows': len(rows), 'added': BADGE}


def merge_stf(data, key, text):
    s = st.read_stf(data)
    assert st.write_stf(s) == data, 'stf does not round-trip'
    have = dict(st.stf_items(s))
    assert key not in have, key
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    st.stf_add(s, key, text)
    out = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(out))) == {**have, key: text}
    return out, {'keys': len(have) + 1, key: text}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the PL-01 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]

    files = dict(base)
    report = {}
    data, src = source(base, BADGE_MAP)
    files[BADGE_MAP], report['badge_map'] = merge_badge_map(data)
    report['badge_map']['from'] = src
    for rel, text in ((BADGE_N, NAME), (BADGE_D, DESC)):
        data, src = source(base, rel)
        files[rel], report[rel] = merge_stf(data, BADGE[1], text)
        report[rel]['from'] = src

    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))

    ours = tre_write.read(out)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    dropped = sorted(n for n in base if n not in ours)
    new = sorted(n for n in ours if n not in base)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped),
        'changed': changed, 'new': new, 'dropped': dropped, 'report': report,
    }
    with open(os.path.join(HERE, 'checks-people.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped, dropped
    assert set(changed) | set(new) == TOUCHED, (changed, new)
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new')}, indent=1))
    print('Ossus people client step: PASS (badge %d added, every other entry byte-identical)' % BADGE[0])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
