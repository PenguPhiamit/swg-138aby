"""The chain up to the Ossus creature names, plus the MTG merges (Claude, 15 Oct 2026; shadow-audit files added the same day). It runs:

    ... > stage_gem_names > stage_creature_names > stage_npc_names > stage_mtg_merges

Packs local_planets-mtgmerge.tre and compares it with the installed fauna archive (Local-model-ossus-fauna, 6556537d).
Only the merged files (stage_mtg_merges.merged_files()) may differ: the ones the fauna archive lacks must be new, the
ones it already has (staged by an earlier step: planet CRC table, creature names, skill and species strings) must be
changed, and every other entry stays byte-identical. In each merged file every stock or staged row, string or CRC entry
is kept (the merge asserts it against its base; this script checks the changed files again against the fauna copy).
Also lists, for information, what differs from the client's current local_planets.tre. Writes checks.json.

    python -I build_mtg_merges_archive.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'Local-model-ossus-fauna'))
import build_fauna_archive as fauna  # noqa: E402  (brings the stock-only load order and the whole chain)
sys.path.insert(0, HERE)
import stage_mtg_merges as smm  # noqa: E402
sys.path.insert(0, os.path.join(OUTPUTS, 'Local-model-ossus-npcs'))
import stage_npc_names as snn  # noqa: E402  (the five Ossus NPC names, after the creatures')
from swgfmt import swg_tables as st  # noqa: E402

REF_TRE = os.path.join(OUTPUTS, 'Local-model-ossus-fauna', 'local_planets-fauna.tre')
REF_SHA = '6556537d589c411f9b0c1697c2a4f5bdd792800f96d0ee517d38cd3cd3dcb072'
INSTALLED_TRE = os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre')
BARC_FILES = ['datatables/mount/logical_saddle_name_map.iff', 'datatables/mount/saddle_appearance_map.iff',
              'datatables/mount/rider_pose_map.iff', 'datatables/mount/valid_scale_range.iff', 'string/en/monster_name.stf']


def keeps(name, old, new):
    """True when new holds every row / string / CRC entry of old unchanged (rows and strings in their order)."""
    if name in smm.TABLES:
        a, b = st.read_dtii(old), st.read_dtii(new)
        return a['columns'] == b['columns'] and a['types'] == b['types'] and b['rows'][:len(a['rows'])] == a['rows']
    if name in smm.WHOLE_FILES:
        return True   # take_whole checked it against its base
    if name in smm.STRINGS:
        a, b = st.stf_items(st.read_stf(old)), st.stf_items(st.read_stf(new))
        return b[:len(a)] == a
    a, b = st.read_cstb(old)['entries'], st.read_cstb(new)['entries']
    return set(a) <= set(b)


def main():
    names, lore = fauna.names, fauna.names.lore
    stage = os.path.join(HERE, 'work', 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder = lore.r3.load_patched_builder()
    builder.STAGE, builder.TRE = stage, os.path.join(HERE, 'work', 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed'
    base = lore.stage_ossus.staging_base(stage)
    lore.stage_ossus.stage_ossus(stage, base)
    lore.species_tables.stage_species(['chiss'], stage, base=base)
    lore.ossus_minerals.stage_ossus_minerals(stage, base)
    lore.stage_lore_materials.stage_lore_materials(stage, base)
    names.stage_gem_names.stage_gem_names(stage, base)
    fauna.scn.stage_creature_names(stage, base)
    npc_names = snn.stage_npc_names(stage, base)
    merged = smm.stage_mtg_merges(stage, base)
    twice = smm.stage_mtg_merges(stage, base)
    out_tre = os.path.join(HERE, 'local_planets-mtgmerge.tre')
    data, _ = lore.tre_write.pack_dir(stage, out_tre)
    ours = lore.tre_write.read(data)[0]
    ref_bytes = open(REF_TRE, 'rb').read()
    ref = lore.tre_write.read(ref_bytes)[0]
    changed = sorted(n for n in ref if n in ours and ref[n] != ours[n])
    new = sorted(n for n in ours if n not in ref)
    gone = sorted(n for n in ref if n not in ours)
    expected = smm.merged_files()
    expected_new = sorted(n for n in expected if n not in ref)
    expected_changed = sorted(n for n in expected if n in ref)
    kept = {n: keeps(n, ref[n], ours[n]) for n in changed if n in expected}
    installed = {}
    if os.path.exists(INSTALLED_TRE):
        inst_bytes = open(INSTALLED_TRE, 'rb').read()
        inst = lore.tre_write.read(inst_bytes)[0]
        installed = {'file': 'SWG-client/local_planets.tre', 'sha256': hashlib.sha256(inst_bytes).hexdigest(),
                     'changed': sorted(n for n in inst if n in ours and inst[n] != ours[n]),
                     'new_entries': sorted(n for n in ours if n not in inst),
                     'missing_entries': sorted(n for n in inst if n not in ours)}
        installed['only_merged_files_differ'] = all(n in expected for n in installed['changed'] + installed['new_entries']) \
            and not installed['missing_entries']
    out = {'built': '2026-10-15', 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
           'entries': len(ours), 'merged_files': len(expected), 'npc_names': npc_names,
           'reference': {'file': 'Local-model-ossus-fauna/local_planets-fauna.tre', 'sha256_expected': REF_SHA,
                         'sha256_ok': hashlib.sha256(ref_bytes).hexdigest() == REF_SHA},
           'against_fauna': {'changed': changed, 'new_entries': new, 'missing_entries': gone,
                             'expected_changed': expected_changed, 'staged_entries_kept': kept},
           'against_installed': installed,
           'merged': merged,
           'idempotent': all(twice[k]['sha256'] == merged[k]['sha256'] for k in merged) and all(twice[k]['added'] == 0 for k in twice)}
    out['ok'] = (sorted(npc_names['added']) == sorted(snn.NAMES) and new == expected_new and changed == expected_changed and not gone and all(kept.values())
                 and out['idempotent'] and out['reference']['sha256_ok']
                 and all(merged[k]['barc_keys'] for k in BARC_FILES) and all(merged[k]['added'] for k in merged))
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, default=list)
    print(json.dumps({k: v for k, v in out.items() if k not in ('merged', 'against_fauna', 'against_installed')}, indent=1))
    print(f'against fauna: {len(new)} new (expected {len(expected_new)}), {len(changed)} changed (expected {len(expected_changed)}), '
          f'{len(gone)} missing; staged entries kept: {all(kept.values())}')
    if installed:
        print(f'against installed {installed["sha256"][:8]}: {len(installed["changed"])} changed, {len(installed["new_entries"])} new, '
              f'{len(installed["missing_entries"])} missing; only merged files differ: {installed["only_merged_files_differ"]}')
    for k, v in merged.items():
        print(f'  {k}: +{v["added"]} {{{", ".join(f"{a[:-4]}: {c}" for a, c in v["from"].items() if c)}}}'
              + (f'; BARC: {v["barc_keys"][:4]}' if v['barc_keys'] else ''))
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
