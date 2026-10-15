"""O5: build the test-session local_planets.tre with Ossus on top of Hoth, without touching h/tools or Local-content.

Runs tools/hoth/hoth_client_build.py's main() with its STAGE and TRE pointed into o5/work (the Hoth build as Claude
makes it), then stage_ossus(stage, base=staging_base(stage)) on that folder (O4), then packs o5/local_planets.tre with
swgfmt.tre_write (the builder's own writer and MD5 rule). Checks: the registration tables carry hoth and ossus; every
entry shared with the installed aee83cc6 archive is byte-identical unless Ossus adds rows to it; the Ossus closure
(terrain, snapshot, UI art) resolves through the loaded archives plus ours with nothing missing.
    python -I build_test_archive.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
OSSUS = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OSSUS)
WORK = os.path.join(HERE, 'work')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
sys.path.insert(0, os.path.join(OSSUS, 'o4', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-live-client', 't2', 'staged', 'tools', 'swgfmt'))
from swgfmt import tre_write, trn_iff  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
import asset_refs  # noqa: E402
import hoth_client_build as builder  # noqa: E402
import stage_ossus  # noqa: E402

INSTALLED = os.path.join(OUTPUTS, 'Local-content', 'local_planets.tre')
OUT_TRE = os.path.join(HERE, 'local_planets.tre')
SEEDS = ['terrain/ossus.trn', 'snapshot/ossus.ws', 'appearance/ui_planet_sel_ossus.apt', 'texture/ui_map_ossus.dds',
         'texture/loading/ossus/ui_load_ossus.dds', 'datatables/environment/ossus.iff', 'terrain/environment/ossus.iff']


def main():
    stage = os.path.join(WORK, 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder.STAGE, builder.TRE = stage, os.path.join(WORK, 'local_planets.tre')     # the builder's outputs land here
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    log = [l for l in buf.getvalue().splitlines() if 'swgemu_login' not in l]
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed:\n' + '\n'.join(log[-10:])
    hoth_tre = open(builder.TRE, 'rb').read()
    rep_ossus = stage_ossus.stage_ossus(stage, stage_ossus.staging_base(stage))
    ver = stage_ossus.verify(stage, stage_ossus.staging_base(os.path.join(WORK, 'hoth-only')) if False else lambda n: tre_write.read(hoth_tre)[0].get(n))
    data, names = tre_write.pack_dir(stage, OUT_TRE)
    sha = hashlib.sha256(data).hexdigest()
    ours, header, meta = tre_write.read(data)
    inst, iheader, imeta = tre_write.read(open(INSTALLED, 'rb').read())
    shared_changed = sorted(n for n in inst if n in ours and inst[n] != ours[n])
    shared_same = sorted(n for n in inst if n in ours and inst[n] == ours[n])
    new_entries = sorted(n for n in ours if n not in inst)
    gone = sorted(n for n in inst if n not in ours)
    # registration tables: both planets
    crc = {name for _, name in st.read_cstb(ours['misc/planet_crc_string_table.iff'])['entries']}
    travel = st.read_dtii(ours['datatables/travel/travel.iff'])
    pn = dict(st.stf_items(st.read_stf(ours['string/en/planet_n.stf'])))
    wp = [r[0] for r in st.read_dtii(ours['datatables/player/waypoint_planets.iff'])['rows']]
    tree = st.read_dtii(ours['datatables/resource/resource_tree.iff'])['rows']
    reg = {'planet_crc': {p: p in crc for p in ('hoth', 'ossus')},
           'travel': {'columns': travel['columns'][-3:], 'rows': [r[0] for r in travel['rows'] if r[0] in ('hoth', 'ossus')],
                      'corellia_to': {p: dict(zip(travel['columns'], travel['rows'][[r[0] for r in travel['rows']].index('corellia')]))[p] for p in ('hoth', 'ossus')}},
           'planet_n': {p: pn.get(p) for p in ('hoth', 'ossus')}, 'waypoint_planets': [p for p in wp if p in ('hoth', 'ossus')],
           'resource_rows': {'total': len(tree), 'hoth': sum(1 for r in tree if r[1].endswith('_hoth')), 'ossus': sum(1 for r in tree if r[1].endswith('_ossus'))}}
    # closure of the Ossus seeds through the client's load order plus our archive
    idx = trn_iff.client_index()

    def get(path):
        if path in ours:
            return ours[path]
        arc = idx.get(path)
        return None if arc is None else trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), path)
    seen, queue, missing, from_ours = set(), list(SEEDS), [], 0
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        d = get(p)
        if d is None:
            missing.append(p)
            continue
        from_ours += p in ours
        if p.endswith(('.dds', '.tga', '.wav', '.snd', '.flr')):
            continue
        for r in asset_refs.refs(d):
            if r not in seen:
                queue.append(r)
    out = {'built': '2026-10-14', 'archive': 'o5/local_planets.tre', 'sha256': sha, 'bytes': len(data), 'entries': len(ours),
           'hoth_build': {'archive_verified': True, 'round_trips_exact': sum('exact' in l for l in log), 'sha256': hashlib.sha256(hoth_tre).hexdigest()[:16],
                          'identical_to_installed': hoth_tre == open(INSTALLED, 'rb').read()},
           'ossus_stage': {'shared': {k: v.get('action') for k, v in rep_ossus['shared'].items()}, 'copied': len(rep_ossus['copied']), 'verify_ok': ver['ok'], 'hoth_kept': ver['hoth_kept']},
           'against_installed_aee83cc6': {'entries_installed': len(inst), 'shared_identical': shared_same, 'shared_changed_by_ossus': shared_changed, 'new_entries': new_entries, 'entries_gone': gone},
           'registration': reg,
           'closure': {'seeds': SEEDS, 'files': len(seen), 'from_our_archive': from_ours, 'missing': sorted(missing)}}
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('against_installed_aee83cc6',)}, indent=1))
    print('shared changed:', shared_changed)
    print('new entries:', len(new_entries), 'gone:', gone)
    return 0


if __name__ == '__main__':
    sys.exit(main())
