"""S5: the test-session local_planets.tre = the O5 build (Hoth + Ossus, 254d0e49...) + stage_species(['chiss']).

Runs tools/hoth/hoth_client_build.main() with STAGE/TRE pointed into s5/work, stage_ossus on that folder (O4), then
species_tables.stage_species(['chiss'], stage, base=staging_base(stage)) (S4), then packs with swgfmt.tre_write. Checks:
every entry shared with the O5 archive is byte-identical unless Chiss adds rows to it; both planets still registered;
the Chiss closure (the two player templates and their customisation tables) resolves with nothing missing.
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
SPECIES = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(SPECIES)
WORK = os.path.join(HERE, 'work')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o4', 'tools'))
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-live-client', 't2', 'staged', 'tools', 'swgfmt'))
from swgfmt import tre_write, trn_iff  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
import asset_refs  # noqa: E402
import hoth_client_build as builder  # noqa: E402
import stage_ossus  # noqa: E402
import species_tables  # noqa: E402

O5_TRE = os.path.join(OUTPUTS, 'Fable-ossus', 'o5', 'local_planets.tre')
OUT_TRE = os.path.join(HERE, 'local_planets.tre')
SEEDS = ['object/creature/player/shared_chiss_male.iff', 'object/creature/player/shared_chiss_female.iff']


def main():
    stage = os.path.join(WORK, 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder.STAGE, builder.TRE = stage, os.path.join(WORK, 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed'
    stage_ossus.stage_ossus(stage, stage_ossus.staging_base(stage))
    o5 = tre_write.read(open(O5_TRE, 'rb').read())[0]
    before, _ = tre_write.pack_dir(stage)
    same_as_o5 = before == open(O5_TRE, 'rb').read()
    rep = species_tables.stage_species(['chiss'], stage, base=stage_ossus.staging_base(stage))
    data, names = tre_write.pack_dir(stage, OUT_TRE)
    sha = hashlib.sha256(data).hexdigest()
    ours, header, meta = tre_write.read(data)
    changed = sorted(n for n in o5 if n in ours and o5[n] != ours[n])
    same = sorted(n for n in o5 if n in ours and o5[n] == ours[n])
    new = sorted(n for n in ours if n not in o5)
    crc = {name for _, name in st.read_cstb(ours['misc/planet_crc_string_table.iff'])['entries']}
    travel = st.read_dtii(ours['datatables/travel/travel.iff'])
    reg = {'planet_crc': {p: p in crc for p in ('hoth', 'ossus')}, 'travel_columns': travel['columns'][-3:],
           'travel_rows': [r[0] for r in travel['rows'] if r[0] in ('hoth', 'ossus')],
           'waypoint_rows': [r[0] for r in st.read_dtii(ours['datatables/player/waypoint_planets.iff'])['rows'] if r[0] in ('hoth', 'ossus')]}
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
    out = {'built': '2026-10-14', 'archive': 's5/local_planets.tre', 'sha256': sha, 'bytes': len(data), 'entries': len(ours),
           'o5_rebuild_identical_to_o5_archive': same_as_o5,
           'species_stage': {'files': {k: {kk: vv for kk, vv in v.items() if kk in ('bytes', 'added', 'rows_added', 'keys_added', 'note', 'unchanged')} for k, v in rep['files'].items()}, 'notes': rep.get('notes', [])},
           'against_o5_254d0e49': {'entries_o5': len(o5), 'identical': len(same), 'changed_by_chiss': changed, 'new_entries': new},
           'registration': reg,
           'closure': {'seeds': SEEDS, 'files': len(seen), 'from_our_archive': from_ours, 'missing': sorted(missing)}}
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'species_stage'}, indent=1))
    print('species files:', list(rep['files']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
