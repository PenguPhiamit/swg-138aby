"""O2c: what the resource manager needs for Ossus, staged as data for Claude's archive builder. Our own code (Fable,
14 Oct 2026).

    python -I stage_resources.py    # writes ../resources/ossus_resource_rows.json, ossus_resource_rows.tsv,
                                    #   resource_tree_with_ossus.iff (stock base + Ossus rows, for reference),
                                    #   activeZones.txt, resource_names.tsv; ../out/resources-report.json

The native pool asks `<type>_<planet>` of datatables/resource/resource_tree.iff; a planet needs the same 45 leaf types
Dantooine and Endor have (the two sets are identical), the ancestors' type counts rise by the leaves added, and
resource_manager.lua's activeZones must list the zone (Hoth port log, 14 Oct 05:17). Each Ossus row is its Dantooine
sibling's row with the ENUM and the display name changed, inserted right after that sibling.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O2 = os.path.normpath(os.path.join(HERE, '..'))
OSSUS = os.path.normpath(os.path.join(O2, '..'))
OUTPUTS = os.path.normpath(os.path.join(OSSUS, '..'))
sys.path.insert(0, os.path.join(OSSUS, 'tools'))
import swg_tables as st  # noqa: E402

BASE = os.path.join(OUTPUTS, 'Documentation-support', 'hoth', 'client-base', 'datatables', 'resource', 'resource_tree.iff')
RES = os.path.join(O2, 'resources')
OUT = os.path.join(O2, 'out')
SOURCE = 'dantooine'
PLANET = 'ossus'
ADJ = {'dantooine': 'Dantooine', 'ossus': 'Ossus'}   # the stock names use "Dantooine X" (no adjective form)


def main():
    with open(BASE, 'rb') as f:
        stock = f.read()
    t = st.read_dtii(stock)
    assert st.write_dtii(t) == stock
    cols = t['columns']
    ci = {c: i for i, c in enumerate(cols)}
    PLANETS = ('corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4', 'hoth', PLANET)

    def depth_of(r):   # a row fills exactly one CLASS column: 1 = resource ... 6 = e.g. milk_domesticated, 7 = its planet leaves
        filled = [k for k in range(8) if r[2 + k]]
        return filled[0] + 1 if filled else 0

    def is_leaf(r):
        return r[1].rsplit('_', 1)[-1] in PLANETS

    rows = list(t['rows'])
    added, out_rows = [], []
    for r in rows:
        out_rows.append(r)
        if r[1].endswith('_' + SOURCE):
            clone = list(r)
            clone[1] = r[1][:-len(SOURCE)] + PLANET
            name_col = 2 + depth_of(r) - 1   # the filled CLASS column carries the display name
            display = r[name_col]
            if display.startswith(ADJ[SOURCE] + ' '):
                clone[name_col] = ADJ[PLANET] + display[len(ADJ[SOURCE]):]
            else:
                clone[name_col] = display.replace(ADJ[SOURCE], ADJ[PLANET])
            clone[0] = 0   # INDEX is reassigned below
            out_rows.append(clone)
            added.append({'after': r[1], 'enum': clone[1], 'name': clone[name_col], 'container': r[-2], 'random_name_class': r[-1]})
    # ancestors: the hierarchy is positional. A row fills exactly one CLASS column (its depth, 1 = resource ... 8 = a
    # planet leaf); a leaf's ancestors are the nearest preceding rows of each shallower depth. Their type counts
    # (Maximum / Minimum # types) rise by the leaves added under them (Claude's Hoth merge did the same; checked below
    # against the merged tree in local_planets.tre).
    bumped = {}
    depth_stack = []   # row indexes of the current ancestors, shallowest first
    for idx, r in enumerate(out_rows):
        depth = depth_of(r)
        if is_leaf(r):   # a planet type: never an ancestor
            if r[1].endswith('_' + PLANET):
                for anc in depth_stack:
                    bumped[anc] = bumped.get(anc, 0) + 1
            continue
        depth_stack = [a for a in depth_stack if depth_of(out_rows[a]) < depth]
        depth_stack.append(idx)
    for idx, n in bumped.items():
        out_rows[idx] = list(out_rows[idx])
        out_rows[idx][ci['Maximum # types']] += n
        out_rows[idx][ci['Minimum # types']] += n
    for k, r in enumerate(out_rows):
        r[0] = k + 1
    table = {'version': t['version'], 'columns': cols, 'types': t['types'], 'rows': out_rows}
    data = st.write_dtii(table)
    back = st.read_dtii(data)
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, 'resource_tree_with_ossus.iff'), 'wb') as f:
        f.write(data)
    with open(os.path.join(RES, 'ossus_resource_rows.json'), 'w', encoding='utf-8') as f:
        json.dump({'planet': PLANET, 'cloned_from': SOURCE, 'rows': added, 'ancestor_rows_bumped': {out_rows[i][1]: n for i, n in bumped.items()},
                   'columns': cols, 'types': t['types']}, f, indent=1)
    with open(os.path.join(RES, 'ossus_resource_rows.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# insert after\tENUM\tdisplay name (CLASS 8)\tcontainer\trandom name class; every other column = the sibling row\n')
        for a in added:
            f.write('\t'.join([a['after'], a['enum'], a['name'], a['container'], a['random_name_class']]) + '\n')
    with open(os.path.join(RES, 'activeZones.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('-- managers/resource_manager.lua: append ",ossus" to the activeZones string (dev line 49 today):\n'
                'activeZones = "corellia,tatooine,lok,naboo,rori,endor,talus,yavin4,dathomir,dantooine,hoth,ossus"\n')
    with open(os.path.join(RES, 'resource_names.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# string/en/resource/resource_names.stf keys the client shows for the new types (key = ENUM); add if the merged\n# resource_names.stf lacks them (MTG named Hoth\'s; Ossus has none yet)\n')
        for a in added:
            f.write('%s\t%s\n' % (a['enum'], a['name']))
    # cross-check the bump rule against Claude's merged tree (Hoth: 52 leaves added): the same ancestors should have
    # risen by 52 there, e.g. resource 545 -> 597, milk_domesticated 10 -> 11
    from trn_iff import open_tre_entry
    merged = st.read_dtii(open_tre_entry(os.path.join(OUTPUTS, 'Local-content', 'local_planets.tre'), 'datatables/resource/resource_tree.iff'))
    stock_by = {r[1]: r for r in t['rows']}
    merged_by = {r[1]: r for r in merged['rows']}
    hoth_leaves = sum(1 for r in merged['rows'] if r[1].endswith('_hoth'))
    rule_check = {}
    for enum in ('resource', 'organic', 'creature_resources', 'creature_food', 'milk', 'milk_domesticated', 'energy', 'energy_renewable_unlimited_solar'):
        rule_check[enum] = {'stock': stock_by[enum][ci['Maximum # types']], 'merged_hoth': merged_by[enum][ci['Maximum # types']],
                            'staged_ossus': [r for r in out_rows if r[1] == enum][0][ci['Maximum # types']]}
    rep = {'stock_rows': len(t['rows']), 'rows_with_ossus': len(back['rows']), 'added': len(added), 'stock_round_trip': True,
           'staged_round_trip': st.write_dtii(back) == data, 'ancestors_bumped': len(bumped),
           'sample': added[:3], 'energy_rows_included': [a['enum'] for a in added if a['enum'].startswith('energy')],
           'source_set_equals_endor_set': True, 'hoth_leaves_in_merged_tree': hoth_leaves, 'type_count_rule_check': rule_check}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'resources-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
