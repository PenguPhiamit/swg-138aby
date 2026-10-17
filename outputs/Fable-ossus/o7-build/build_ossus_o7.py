"""PL-01: Ossus O7, the client half = any base archive + the O7 terrain, snapshot and two region labels (Claude, 16 Oct 2026).

What this step changes in the base archive (all four entries already exist there, from O4/O5):
  terrain/ossus.trn                     rebuilt with the 14 O7 layers (tools/o7_terrain.py, in a temp folder): five craters,
                                        four scorch fans, the glass pan and rubble apron, Westmarch and Knossa Fields, the POI 17
                                        glass plain; the three TGAs it also writes must equal the base's byte for byte
  snapshot/ossus.ws                     the base's 87 nodes + the 295 O7 statics and their 80 cell nodes (tools/append_snapshot.py)
  datatables/clientregion/ossus.iff     + westmarch (-5344, 96) r 400 and knossa_fields (1500, -3300) r 450, before the
                                        planet-wide 'ossus' row
  string/en/ossus_region_names.stf      + "Westmarch", "Knossa Fields"
Every other entry of the base comes through byte for byte (checked). Nothing is installed and no staged file is written.

    C:/Users/Pengw/miniconda3/python.exe -I build_ossus_o7.py [--base PATH] [--out PATH]
Default base: ../../../work/c59-walk-on-0e4fe92d/local_planets-c59-walk.tre (the installed archive, sha256 9ce108a0...).
Default out:  ../../../work/ossus-o7/local_planets-ossus-o7.tre (+ .sha256), checks in ./checks-build.json.
On another base (the floater, Nal Hutta or Hoth steps, in any order) the four entries must still be the O5 ones; the step
refuses a base whose Ossus terrain, snapshot or region rows it does not recognise.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OSSUS = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OSSUS)
H = os.path.dirname(OUTPUTS)
TOOLS = os.path.join(HERE, 'tools')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, TOOLS)
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
import o7_terrain  # noqa: E402
import append_snapshot  # noqa: E402
from o7_common import jload  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'c59-walk-on-0e4fe92d', 'local_planets-c59-walk.tre')
DEFAULT_BASE_SHA_PREFIX = '9ce108a0'
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-o7', 'local_planets-ossus-o7.tre')
# the O5 entries this step replaces (sha256, as installed since O5; same as Fable-ossus/staged and o2/staged)
O5 = {
    'terrain/ossus.trn': '0c2600f08703ed4dd8ee80563964c2ad349f9008823a72f034e03976170bb3ec',
    'snapshot/ossus.ws': '7f3ec2672ef9da76755e5325fa424dfe29e6ce73a95136aba0bda1a61d53c651',
    'datatables/clientregion/ossus.iff': 'a8e00ab1e9ce7c6edeb4f7260d39b8fde77a9683bec1d43f9f962ac46165c19e',
    'string/en/ossus_region_names.stf': '4841f1e5696dc93868bf08cd06278c2dd686f0956ea7d1f1fe4a040de03720d5',
}
TGAS = ('terrain/ossus_academy.tga', 'terrain/ossus_canyon.tga', 'terrain/ossus_mesa.tga')
NEW_REGIONS = [('westmarch', 'Westmarch', -5344.0, 96.0, 400.0), ('knossa_fields', 'Knossa Fields', 1500.0, -3300.0, 450.0)]
CHANGED = set(O5)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build_terrain(base):
    tmp = tempfile.mkdtemp(prefix='ossus-o7-trn-')
    rep = o7_terrain.build(tmp, with_layers=True, quiet=True)
    stage = os.path.join(tmp, 'staged', 'client')
    trn = open(os.path.join(stage, 'terrain', 'ossus.trn'), 'rb').read()
    tga_same = {t: open(os.path.join(stage, *t.split('/')), 'rb').read() == base[t] for t in TGAS}
    assert all(tga_same.values()), tga_same
    verdict = rep.get('verdict') if isinstance(rep, dict) else None
    assert verdict == 'PASS', 'terrain build verdict: %s' % verdict
    shutil.rmtree(tmp, ignore_errors=True)
    return trn, {'bytes': len(trn), 'sha256': sha(trn), 'tgas_identical_to_base': tga_same, 'verdict': verdict}


def build_snapshot(base):
    statics = jload(os.path.join(HERE, 'statics.json'))
    tmp = tempfile.mkdtemp(prefix='ossus-o7-ws-')
    path = os.path.join(tmp, 'ossus.ws')
    with open(path, 'wb') as f:
        f.write(base['snapshot/ossus.ws'])
    out, info = append_snapshot.build(statics, path)
    problems, rep = append_snapshot.check(out, statics)
    assert not problems, problems
    shutil.rmtree(tmp, ignore_errors=True)
    rep.update(info)
    return out, rep


def merge_regions(table, names):
    t = st.read_dtii(table)
    assert st.write_dtii(t) == table, 'clientregion/ossus.iff: base does not round-trip'
    keys = [r[0] for r in t['rows']]
    assert keys[-1] == '@ossus_region_names:ossus', keys
    for key, *_ in NEW_REGIONS:
        assert '@ossus_region_names:' + key not in keys, key
    new_rows = [['@ossus_region_names:' + key, x, y, r] for key, _, x, y, r in NEW_REGIONS]
    rows = t['rows'][:-1] + new_rows + t['rows'][-1:]
    tout = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    assert [r for r in st.read_dtii(tout)['rows'] if r not in new_rows] == t['rows']

    s = st.read_stf(names)
    assert st.write_stf(s) == names, 'ossus_region_names.stf: base does not round-trip'
    have = dict(st.stf_items(s))
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    for key, text, *_ in NEW_REGIONS:
        assert key not in have, key
        st.stf_add(s, key, text)
    nout = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(nout))) == {**have, **{k: v for k, v, *_ in NEW_REGIONS}}
    return tout, nout, {'rows': st.read_dtii(tout)['rows'], 'names': st.stf_items(st.read_stf(nout))}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the 9ce108a0 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    seen = {rel: sha(base[rel]) if rel in base else None for rel in O5}
    assert seen == O5, 'base does not carry the O5 Ossus entries: %s' % {k: v for k, v in seen.items() if v != O5[k]}

    files = dict(base)
    report = {}
    files['terrain/ossus.trn'], report['terrain'] = build_terrain(base)
    files['snapshot/ossus.ws'], report['snapshot'] = build_snapshot(base)
    (files['datatables/clientregion/ossus.iff'], files['string/en/ossus_region_names.stf'],
     report['regions']) = merge_regions(base['datatables/clientregion/ossus.iff'], base['string/en/ossus_region_names.stf'])

    data = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(data)
    out_sha = sha(data)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))

    ours = tre_write.read(data)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    dropped = sorted(n for n in base if n not in ours)
    new = sorted(n for n in ours if n not in base)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(data), 'sha256': out_sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped),
        'changed': changed, 'new': new, 'dropped': dropped,
        'entries_sha256': {rel: sha(ours[rel]) for rel in sorted(CHANGED)},
        'report': report,
    }
    with open(os.path.join(HERE, 'checks-build.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped, dropped
    assert not new, new
    assert set(changed) == CHANGED, changed
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new')}, indent=1))
    print('snapshot nodes:', report['snapshot']['nodes'], 'terrain bytes:', report['terrain']['bytes'])
    print('Ossus O7 client step: PASS (four Ossus entries replaced, every other entry byte-identical)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
