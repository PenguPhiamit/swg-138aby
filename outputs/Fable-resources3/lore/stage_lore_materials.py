"""stage_lore_materials.stage_lore_materials(stage_dir, base): C29's cheapest batch, two Legends materials on planets we have.

- crystalline_adegan_ossus "Adegan Crystal Crystalline Gemstone" (Ossus): the Adega system's lightsaber crystals, first found on
  Ossus (Wookieepedia, Legends: https://starwars.fandom.com/wiki/Adegan_crystal/Legends). Goes after crystalline_ossus_2 as a
  clone of the strongest stock crystalline gem (Vertex) by the R3 part-2 rule: quality minimum 500, every other minimum rounded
  up to the next multiple of 50 unless that reaches the maximum. Pools 1/1, types 1/2 (as the Ossus gems).
- vegetable_fungi_lumni_hoth "Lumni Lichen Fungus" (Hoth): the scarce fungus lumni-spice is made from, kept in a sunless fissure
  near Hoth's equator (https://starwars.fandom.com/wiki/Lumni-spice, https://starwars.fandom.com/wiki/Lumni_lichen). Goes after
  vegetable_fungi_hoth as a clone of that native with a stated variant for "the rarest spice in the galaxy": quality 500-1000,
  flavor 700-1000, potential energy 500-1000 (decay resistance as the native). Pools 1/1, types 1/1 (as natives).
The enums carry _ossus / _hoth, which is what Core3's ResourceTree::setZoneRestriction keys on. Neither is spawned by the stock
pools: the minimum-pool lines are the dev patch (patch/core3-c29-lore-pools.patch). Idempotent; ancestors' Minimum/Maximum #
types rise by the leaves added under them (the O4 rule); the stock row order is kept.
Fable, 14 October 2026. Lore read on Wookieepedia (CC BY-SA); the in-game names are ours.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(R3)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(R3, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
import ossus_minerals as om  # noqa: E402

TREE = om.TREE
LUMNI_VARIANT = {'res_quality': 500, 'res_flavor': 700, 'res_potential_energy': 500}   # attribute -> minimum
ENUMS = ['crystalline_adegan_ossus', 'vegetable_fungi_lumni_hoth']


def lore_rows(tree):
    rows, ci = tree['rows'], {c: i for i, c in enumerate(tree['columns'])}
    depth, anc, parents = om._analyse(rows, ci)
    by = {r[1]: r for r in rows}
    out = []
    # 1. Adegan crystal: part-2 rule on the strongest stock crystalline gem
    sib = om.strongest_sibling(rows, ci, 'gemstone_crystalline', anc, parents)
    assert sib is not None and 'crystalline_ossus_2' in by, 'run after stage_ossus_minerals (needs crystalline_ossus_2)'
    r = list(sib)
    r[1] = 'crystalline_adegan_ossus'
    r[ci['CLASS %d' % depth(sib)]] = 'Adegan Crystal Crystalline Gemstone'
    r[ci['Minimum # Pools']], r[ci['Maximum # Pools']] = 1, 1
    r[ci['Minimum # types']], r[ci['Maximum # types']] = 1, 2
    for i in range(1, 12):
        a = r[ci['Attribute %d' % i]]
        if a:
            mn, mx = r[ci['Att %d min' % i]], r[ci['Att %d max' % i]]
            r[ci['Att %d min' % i]] = max(mn, 500) if a == 'res_quality' else om.round_up50(mn, mx)
    out.append({'row': r, 'after': 'crystalline_ossus_2', 'sibling': sib[1], 'class': 'gemstone_crystalline', 'rule': 'part-2'})
    # 2. Lumni lichen: the Hoth fungus native with the stated variant
    sib = by['vegetable_fungi_hoth']
    r = list(sib)
    r[1] = 'vegetable_fungi_lumni_hoth'
    r[ci['CLASS %d' % depth(sib)]] = 'Lumni Lichen Fungus'
    r[ci['Minimum # Pools']], r[ci['Maximum # Pools']] = 1, 1
    for i in range(1, 12):
        a = r[ci['Attribute %d' % i]]
        if a in LUMNI_VARIANT:
            assert LUMNI_VARIANT[a] < r[ci['Att %d max' % i]], a
            r[ci['Att %d min' % i]] = max(r[ci['Att %d min' % i]], LUMNI_VARIANT[a])
    out.append({'row': r, 'after': 'vegetable_fungi_hoth', 'sibling': sib[1], 'class': 'vegetable_fungi', 'rule': 'variant ' + str(LUMNI_VARIANT)})
    return out, ci


def stage_lore_materials(stage_dir, base):
    data = base(TREE)
    tree = st.read_dtii(data)
    assert st.write_dtii(tree) == data, 'resource tree base does not round-trip'
    plan, ci = lore_rows(tree)
    rows = [list(r) for r in tree['rows']]
    have = {r[1] for r in rows}
    added = []
    for item in plan:
        if item['row'][1] in have:
            continue
        at = next(i for i, r in enumerate(rows) if r[1] == item['after']) + 1
        rows.insert(at, item['row'])
        have.add(item['row'][1])
        added.append(item)
    depth, anc, parents = om._analyse(rows, ci)
    bumped = {}
    for item in added:
        for a in anc[item['row'][1]]:
            bumped[a] = bumped.get(a, 0) + 1
    by = {r[1]: r for r in rows}
    for a, n in bumped.items():
        by[a][ci['Maximum # types']] += n
        by[a][ci['Minimum # types']] += n
    for k, r in enumerate(rows):
        r[0] = k + 1
    out = st.write_dtii({'version': tree['version'], 'columns': tree['columns'], 'types': tree['types'], 'rows': rows})
    back = st.read_dtii(out)
    assert [r[1] for r in back['rows'] if r[1] not in {i['row'][1] for i in added}] == [r[1] for r in tree['rows']]
    path = os.path.join(stage_dir, TREE.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(out)
    return {'file': TREE, 'rows': len(back['rows']), 'enums': ENUMS, 'ancestors_bumped': bumped, 'sha256': hashlib.sha256(out).hexdigest(),
            'added': [{'enum': i['row'][1], 'text': i['row'][ci['CLASS %d' % depth(i['row'])]], 'after': i['after'], 'cloned_from': i['sibling'], 'rule': i['rule'],
                       'pools': (i['row'][ci['Minimum # Pools']], i['row'][ci['Maximum # Pools']]), 'types': (i['row'][ci['Minimum # types']], i['row'][ci['Maximum # types']]),
                       'attrs': [(i['row'][ci['Attribute %d' % k]], i['row'][ci['Att %d min' % k]], i['row'][ci['Att %d max' % k]]) for k in range(1, 12) if i['row'][ci['Attribute %d' % k]]]}
                      for i in added]}


if __name__ == '__main__':
    print(__doc__)
