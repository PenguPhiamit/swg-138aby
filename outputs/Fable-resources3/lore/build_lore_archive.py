"""C29 chain: Hoth build > stage_ossus (O4/O5) > stage_species chiss (S5) > stage_ossus_minerals (R3 part 2) > stage_lore_materials.
Packs lore/local_planets-lore.tre, compares it with R3's part-2 archive (248092a2: only resource_tree may change, two rows added,
Chiss and every other entry byte-identical) and writes lore/checks.json.   python -I build_lore_archive.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
sys.path.insert(0, R3)                       # R3's chain builder sets up the tool paths (swgfmt, stage_ossus, species_tables, ossus_minerals)
import build_test_archive as r3  # noqa: E402
sys.path.insert(0, HERE)
from swgfmt import tre_write  # noqa: E402
import stage_ossus  # noqa: E402
import species_tables  # noqa: E402
import ossus_minerals  # noqa: E402
import stage_lore_materials  # noqa: E402

PART2_TRE = os.path.join(R3, 'local_planets-part2.tre')
PART2_SHA = '248092a2db7ddb1a2d90f2ca15bcd8ed1064c9757ec07d3362681550ed7dc98c'


def main():
    stage = os.path.join(HERE, 'work', 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder = r3.load_patched_builder()
    builder.STAGE, builder.TRE = stage, os.path.join(HERE, 'work', 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed'
    base = stage_ossus.staging_base(stage)
    stage_ossus.stage_ossus(stage, base)
    species_tables.stage_species(['chiss'], stage, base=base)
    ossus_minerals.stage_ossus_minerals(stage, base)
    lore = stage_lore_materials.stage_lore_materials(stage, base)
    twice = stage_lore_materials.stage_lore_materials(stage, base)   # idempotence
    out_tre = os.path.join(HERE, 'local_planets-lore.tre')
    data, names = tre_write.pack_dir(stage, out_tre)
    ours = tre_write.read(data)[0]
    ref_bytes = open(PART2_TRE, 'rb').read()
    ref = tre_write.read(ref_bytes)[0]
    changed = sorted(n for n in ref if n in ours and ref[n] != ours[n])
    new = sorted(n for n in ours if n not in ref)
    t_new, ci = r3.tree_rows(ours['datatables/resource/resource_tree.iff'])
    t_old, _ = r3.tree_rows(ref['datatables/resource/resource_tree.iff'])
    old_by = {r[1]: r for r in t_old['rows']}
    added = [r[1] for r in t_new['rows'] if r[1] not in old_by]
    mx, mn = ci['Maximum # types'], ci['Minimum # types']
    bumped = [r[1] for r in t_new['rows'] if r[1] in old_by and (r[mx] != old_by[r[1]][mx] or r[mn] != old_by[r[1]][mn])]
    other = [r[1] for r in t_new['rows'] if r[1] in old_by and r[2:mx] != old_by[r[1]][2:mx]]
    order_kept = [r[1] for r in t_new['rows'] if r[1] in old_by] == [r[1] for r in t_old['rows']]
    zone = {e: ('_ossus' in e, '_hoth' in e) for e in added}
    out = {'built': '2026-10-14', 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'entries': len(ours),
           'reference': {'file': os.path.basename(PART2_TRE), 'sha256_expected': PART2_SHA, 'sha256_ok': hashlib.sha256(ref_bytes).hexdigest() == PART2_SHA},
           'against_part2': {'changed': changed, 'new_entries': new, 'only_resource_tree_changed': changed == ['datatables/resource/resource_tree.iff'] and not new,
                             'chiss_entries_identical': all(ref[n] == ours[n] for n in ref if 'creation/' in n or 'customization' in n or n in ('ui/ui_avatardata.inc', 'string/en/player_species.stf'))},
           'resource_tree': {'rows_before': len(t_old['rows']), 'rows_after': len(t_new['rows']), 'added': added, 'added_detail': lore['added'],
                             'ancestor_counts_bumped': bumped, 'other_cell_changes': other, 'stock_order_kept': order_kept,
                             'zone_substrings': zone, 'idempotent': twice['added'] == [] and twice['sha256'] == lore['sha256']},
           'ok': changed == ['datatables/resource/resource_tree.iff'] and not new and sorted(added) == sorted(stage_lore_materials.ENUMS) and not other and order_kept
                 and twice['added'] == [] and all(any(v) for v in zone.values())}
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'resource_tree'}, indent=1))
    print('tree:', {k: v for k, v in out['resource_tree'].items() if k != 'added_detail'})
    for d in lore['added']:
        print('  +', d['enum'], '|', d['text'], '| after', d['after'], '| from', d['cloned_from'], '|', d['rule'], '| pools', d['pools'], 'types', d['types'])
        print('    ', d['attrs'])
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
