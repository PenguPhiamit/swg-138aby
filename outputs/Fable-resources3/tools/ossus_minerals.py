"""ossus_minerals.stage_ossus_minerals(stage_dir, base): Ossus's own minerals, Hoth-style (Fable R3 part 2, 14 Oct 2026).

Fourteen zone-restricted leaf types under the same stock classes as Hoth's: steel, iron, copper, aluminum, extrusive and
intrusive ore, reactive gas, liquid and solid petrochem fuel, radioactive, two amorphous and two crystalline gems. Each
is a clone of the STRONGEST stock leaf of its class (the leaf whose attribute minimums add up highest; that is how
MTG's Hoth rows relate to their parents: steel_hoth = Duralloy Steel, iron_hoth = Kammris Iron, ore_extrusive_hoth =
Vintrium ore, radioactive_hoth = Class 7, the gems = Type 1/2 ...) with the rule MTG applied on top:
  quality minimum raised to 500; every other minimum rounded up to the next multiple of 50, except where that would
  reach the maximum (the sibling's minimum stays, so the range never collapses);
  Minimum/Maximum # Pools 1/1 (one planet); Minimum/Maximum # types 1/2 (as MTG's rows); container, survey tool and
  random-name class from the sibling. Names "Ossus <class text>" (gems "Ossus Type n Amorphous/Crystalline Gemstone").
ENUMs end in _ossus or hold _ossus_<n> (gems): Core3 restricts by the "_ossus" substring (ResourceTree::setZoneRestriction).
Rows go right after the Hoth row of the same class (so after the stock block); ancestors' type counts rise by the leaves
added under them (the O4 rule). Idempotent: present rows are left alone.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402

TREE = 'datatables/resource/resource_tree.iff'
PLANET, WORD = 'ossus', 'Ossus'
PLANETS = ('corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4', 'hoth', 'ossus', 'kaas', 'taanab')
JTL = {'steel_bicorbantium', 'steel_arveshian', 'aluminum_perovskitic', 'copper_borocarbitic', 'fiberplast_gravitonic', 'gas_reactive_organometallic', 'ore_siliclastic_fermionic', 'radioactive_polymetric'}
# class enum -> (new enum(s), text(s), the Hoth row each goes after)
PLAN = [('steel', ['steel_ossus'], ['Ossus Steel'], 'steel_hoth'),
        ('iron', ['iron_ossus'], ['Ossus Iron'], 'iron_hoth'),
        ('copper', ['copper_ossus'], ['Ossus Copper'], 'copper_hoth'),
        ('aluminum', ['aluminum_ossus'], ['Ossus Aluminum'], 'aluminum_hoth'),
        ('ore_extrusive', ['ore_extrusive_ossus'], ['Ossus Extrusive Ore'], 'ore_extrusive_hoth'),
        ('ore_intrusive', ['ore_intrusive_ossus'], ['Ossus Intrusive Ore'], 'ore_intrusive_hoth'),
        ('gas_reactive', ['gas_reactive_ossus'], ['Ossus Reactive Gas'], 'gas_reactive_hoth'),
        ('fuel_petrochem_liquid', ['petrochem_fuel_liquid_ossus'], ['Ossus Liquid Petro Fuel'], 'petrochem_fuel_liquid_hoth'),   # stock class enum; leaves are petrochem_fuel_liquid_typeN
        ('fuel_petrochem_solid', ['petrochem_fuel_solid_ossus'], ['Ossus Solid Petro Fuel'], 'petrochem_fuel_solid_hoth'),
        ('radioactive', ['radioactive_ossus'], ['Ossus Radioactive'], 'radioactive_hoth'),
        ('gemstone_armophous', ['armophous_ossus_1', 'armophous_ossus_2'], ['Ossus Type 1 Amorphous Gemstone', 'Ossus Type 2 Amorphous Gemstone'], 'armophous_hoth_2'),
        ('gemstone_crystalline', ['crystalline_ossus_1', 'crystalline_ossus_2'], ['Ossus Type 1 Crystalline Gemstone', 'Ossus Type 2 Crystalline Gemstone'], 'crystalline_hoth_2')]


def _analyse(rows, ci):
    def depth(r):
        return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
    stack, anc = [], {}
    for r in rows:
        d = depth(r)
        stack = [s for s in stack if s[0] < d]
        anc[r[1]] = [s[1] for s in stack]
        stack.append((d, r[1]))
    parents = {a for chain in anc.values() for a in chain}
    return depth, anc, parents


def round_up50(v, mx):
    """The next multiple of 50 above v; when that would close the range (reach the maximum) the sibling's own minimum stays."""
    if v <= 1:
        return v
    up = ((v + 49) // 50) * 50
    return up if up < mx else v


def strongest_sibling(rows, ci, cls, anc, parents):
    """The stock leaf under cls with the highest sum of attribute minimums (planet rows, JTL and *_unknown left out)."""
    best, score = None, -1
    for r in rows:
        e = r[1]
        if e in parents or cls not in anc[e] or e.rsplit('_', 1)[-1] in PLANETS or e in JTL or e.endswith('_unknown') or '_hoth' in e or '_ossus' in e:
            continue
        s = sum(r[ci['Att %d min' % i]] for i in range(1, 12) if r[ci['Attribute %d' % i]])
        if s > score:
            best, score = r, s
    return best


def ossus_rows(tree):
    rows, ci = tree['rows'], {c: i for i, c in enumerate(tree['columns'])}
    depth, anc, parents = _analyse(rows, ci)
    out = []
    for cls, enums, texts, after in PLAN:
        sib = strongest_sibling(rows, ci, cls, anc, parents)
        assert sib is not None, cls
        for enum, text in zip(enums, texts):
            r = list(sib)
            r[1] = enum
            r[ci['CLASS %d' % depth(sib)]] = text
            r[ci['Minimum # Pools']], r[ci['Maximum # Pools']] = 1, 1
            r[ci['Minimum # types']], r[ci['Maximum # types']] = 1, 2
            for i in range(1, 12):
                a = r[ci['Attribute %d' % i]]
                if not a:
                    continue
                mn, mx = r[ci['Att %d min' % i]], r[ci['Att %d max' % i]]
                r[ci['Att %d min' % i]] = max(mn, 500) if a == 'res_quality' else round_up50(mn, mx)
            out.append({'row': r, 'after': after, 'sibling': sib[1], 'class': cls})
    return out, ci


def stage_ossus_minerals(stage_dir, base):
    data = base(TREE)
    tree = st.read_dtii(data)
    assert st.write_dtii(tree) == data, 'resource tree base does not round-trip'
    ci = {c: i for i, c in enumerate(tree['columns'])}
    have = {r[1] for r in tree['rows']}
    plan, _ = ossus_rows(tree)
    rows = [list(r) for r in tree['rows']]
    added = []
    for item in plan:
        if item['row'][1] in have:
            continue
        at = next(i for i, r in enumerate(rows) if r[1] == item['after']) + 1
        rows.insert(at, item['row'])
        item['after'] = rows[at - 1][1]
        added.append(item)
        have.add(item['row'][1])
        # the next gem of the same class goes after this one
        for j in plan:
            if j is not item and j['class'] == item['class'] and j['after'] == rows[at - 1][1] and j['row'][1] not in have:
                j['after'] = item['row'][1]
    depth, anc, parents = _analyse(rows, ci)
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
    return {'file': TREE, 'rows': len(back['rows']), 'added': [{'enum': i['row'][1], 'text': i['row'][ci['CLASS %d' % depth(i['row'])]], 'after': i['after'], 'cloned_from': i['sibling'],
                                                                 'attrs': [(i['row'][ci['Attribute %d' % k]], i['row'][ci['Att %d min' % k]], i['row'][ci['Att %d max' % k]]) for k in range(1, 12) if i['row'][ci['Attribute %d' % k]]]} for i in added],
            'ancestors_bumped': bumped, 'sha256': hashlib.sha256(out).hexdigest(), 'enums': [i['row'][1] for i in plan]}
