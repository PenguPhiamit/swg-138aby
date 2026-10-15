"""R3: the test-session local_planets.tre with the resource additions, built like O5 but from the PATCHED builder source
(work/new/tools/hoth/hoth_client_build.py, executed with the real file's location so its paths resolve), then
stage_ossus (O4) and, with --part2, stage_ossus_minerals (R3 part 2). Writes checks-<part>.json and the archive.
    python -I build_test_archive.py [--part2] [--no-chiss]     (the chain: Hoth build > stage_ossus > stage_species chiss > R3 rows)
"""
import hashlib
import io
import json
import os
import shutil
import sys
import types
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
WORK = os.path.join(HERE, 'work')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o4', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-species', 's4', 'tools'))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
import stage_ossus  # noqa: E402

O5_TRE = os.path.join(OUTPUTS, 'Fable-ossus', 'o5', 'local_planets.tre')
S5_TRE = os.path.join(OUTPUTS, 'Fable-species', 's5', 'local_planets.tre')
REAL_BUILDER = os.path.join(OUTPUTS, 'tools', 'hoth', 'hoth_client_build.py')
PATCHED_BUILDER = os.path.join(WORK, 'new', 'tools', 'hoth', 'hoth_client_build.py')


def load_patched_builder():
    m = types.ModuleType('hoth_client_build')
    m.__file__ = REAL_BUILDER
    sys.modules['hoth_client_build'] = m
    src = open(PATCHED_BUILDER, encoding='utf-8').read()
    exec(compile(src, REAL_BUILDER, 'exec'), m.__dict__)
    return m


def tree_rows(data):
    t = st.read_dtii(data)
    ci = {c: i for i, c in enumerate(t['columns'])}
    return t, ci


def main(argv):
    part2 = '--part2' in argv
    part = 'part2' if part2 else 'part1'
    stage = os.path.join(WORK, 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder = load_patched_builder()
    builder.STAGE, builder.TRE = stage, os.path.join(WORK, 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    log = [l for l in buf.getvalue().splitlines() if 'swgemu_login' not in l]
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed:' + chr(10).join(log[-8:])
    stage_ossus.stage_ossus(stage, stage_ossus.staging_base(stage))
    extra = {}
    chiss = '--no-chiss' not in argv                      # the official chain: Hoth build, stage_ossus, stage_species chiss, R3 rows
    if chiss:
        import species_tables
        species_tables.stage_species(['chiss'], stage, base=stage_ossus.staging_base(stage))
    if part2:
        import ossus_minerals
        extra = ossus_minerals.stage_ossus_minerals(stage, stage_ossus.staging_base(stage))
    out_tre = os.path.join(HERE, 'local_planets-%s.tre' % part)
    data, names = tre_write.pack_dir(stage, out_tre)
    ours = tre_write.read(data)[0]
    o5 = tre_write.read(open(S5_TRE if chiss else O5_TRE, 'rb').read())[0]
    ref_name = 'S5 b1a0a232' if chiss else 'O5 254d0e49'
    changed = sorted(n for n in o5 if n in ours and o5[n] != ours[n])
    new = sorted(n for n in ours if n not in o5)
    t_new, ci = tree_rows(ours['datatables/resource/resource_tree.iff'])
    t_old, _ = tree_rows(o5['datatables/resource/resource_tree.iff'])
    old_by = {r[1]: r for r in t_old['rows']}
    added = [r[1] for r in t_new['rows'] if r[1] not in old_by]
    mx, mn = ci['Maximum # types'], ci['Minimum # types']
    bumped = [r[1] for r in t_new['rows'] if r[1] in old_by and (r[mx] != old_by[r[1]][mx] or r[mn] != old_by[r[1]][mn])]
    other_changes = [r[1] for r in t_new['rows'] if r[1] in old_by and r[2:mx] != old_by[r[1]][2:mx]]
    order_kept = [r[1] for r in t_new['rows'] if r[1] in old_by] == [r[1] for r in t_old['rows']]

    def dep(r):
        return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
    added_detail = [{'enum': r[1], 'text': r[ci['CLASS %d' % dep(r)]], 'after': t_new['rows'][k - 1][1], 'pools': (r[ci['Minimum # Pools']], r[ci['Maximum # Pools']]),
                     'attrs': [(r[ci['Attribute %d' % i]], r[ci['Att %d min' % i]], r[ci['Att %d max' % i]]) for i in range(1, 12) if r[ci['Attribute %d' % i]]]}
                    for k, r in enumerate(t_new['rows']) if r[1] not in old_by]
    crc = {name for _, name in st.read_cstb(ours['misc/planet_crc_string_table.iff'])['entries']}
    travel = st.read_dtii(ours['datatables/travel/travel.iff'])
    out = {'built': '2026-10-14', 'part': part, 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'entries': len(ours),
           'builder_log_tree_lines': [l for l in log if l.startswith('resource tree:')],
           'against_' + ref_name.replace(' ', '_'): {'changed': changed, 'new_entries': new, 'only_resource_tree_changed': changed == ['datatables/resource/resource_tree.iff'] and not new,
                                                  'chiss_entries_identical': chiss and all(o5[n] == ours[n] for n in o5 if 'creation/' in n or 'customization' in n or n in ('ui/ui_avatardata.inc', 'string/en/player_species.stf', 'datatables/skill/skills.iff', 'string/en/skl_n.stf', 'string/en/skl_d.stf'))},
           'resource_tree': {'rows_before': len(t_old['rows']), 'rows_after': len(t_new['rows']), 'added': added, 'added_detail': added_detail,
                             'ancestor_counts_bumped': bumped, 'other_cell_changes': other_changes, 'stock_order_kept': order_kept},
           'registration': {'planet_crc': {p: p in crc for p in ('hoth', 'ossus')}, 'travel_columns': travel['columns'][-3:], 'travel_rows': [r[0] for r in travel['rows'] if r[0] in ('hoth', 'ossus')]},
           'part2': extra}
    with open(os.path.join(HERE, 'checks-%s.json' % part), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('resource_tree',)}, indent=1))
    print('tree:', {k: v for k, v in out['resource_tree'].items() if k != 'added_detail'})
    for d in added_detail:
        print('  +', d['enum'], '|', d['text'], '| after', d['after'], '| pools', d['pools'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
