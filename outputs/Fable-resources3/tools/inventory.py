"""R3 part 3: inventory of every resource row we may use (stock, MTG extras, Ossus, R3, the owner's book), with class path,
attributes, planet restriction, the pool that spawns it today, planet coverage under poolScaleZones, and the schematics
that would consume it. Writes ../inventory.json and ../inventory.md.  python -I inventory.py"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(R3)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st, trn_iff as I, tre_write  # noqa: E402

STOCK = os.path.join(OUTPUTS, 'Documentation-support', 'hoth', 'client-base', 'datatables', 'resource', 'resource_tree.iff')
MERGED_TRE = os.path.join(R3, 'local_planets-part2.tre')
LUA = os.path.join(R3, 'work', 'new2', 'MMOCoreORB', 'bin', 'scripts', 'managers', 'resource_manager.lua')
SCHEMATICS = os.path.join(R3, 'work', 'schematic_types_by_file.txt')
BOOK = os.path.join(OUTPUTS, 'Content-catalogue', 'owner-SWG-SW5E', 'README.md')
STOCK_PLANETS = ['corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4']
PLANETS = STOCK_PLANETS + ['hoth', 'ossus', 'kaas', 'taanab']
ZONES_TODAY, SCALE_BASE = 12, 10


def read_tree(data):
    t = st.read_dtii(data)
    ci = {c: i for i, c in enumerate(t['columns'])}
    rows = t['rows']

    def depth(r):
        return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
    stack, anc, text = [], {}, {}
    for r in rows:
        d = depth(r)
        stack = [s for s in stack if s[0] < d]
        anc[r[1]] = [s[1] for s in stack]
        text[r[1]] = r[ci['CLASS %d' % d]] if d else ''
        stack.append((d, r[1]))
    parents = {a for chain in anc.values() for a in chain}
    info = {}
    for r in rows:
        e = r[1]
        info[e] = {'enum': e, 'text': text[e], 'class_path': [text[a] for a in anc[e]], 'class_enums': anc[e], 'leaf': e not in parents,
                   'pools': [r[ci['Minimum # Pools']], r[ci['Maximum # Pools']]], 'types': [r[ci['Minimum # types']], r[ci['Maximum # types']]],
                   'attributes': [[r[ci['Attribute %d' % i]], r[ci['Att %d min' % i]], r[ci['Att %d max' % i]]] for i in range(1, 12) if r[ci['Attribute %d' % i]]],
                   'container': r[ci['Resource Container Type']].split('/')[-1], 'planet': next((p for p in PLANETS if ('_' + p) in e), ''),
                   'recycled': bool(r[ci['Recycled']]) if 'Recycled' in ci else False}
    return info, [r[1] for r in rows], anc


def parse_pools(lua):
    def pairs(name):
        m = re.search(r'^%s = \{(.*?)\}\s*$' % name, lua, re.M | re.S)
        return re.findall(r'\{"(\w+)",\s*(\d+)\}', m.group(1)) if m else []
    minimum = [(n, int(c)) for n, c in pairs('minimumpoolincludes')]
    for loop in re.findall(r'for _, \w+ in ipairs\(\{(.*?)\}\) do', lua, re.S):
        minimum += [(n, 1) for n in re.findall(r'"(\w+)"', loop)]
    jtl = re.search(r'^jtlresources = "([^"]+)"', lua, re.M).group(1).split(',')
    random_inc = [(n, int(w)) for n, w in pairs('randompoolincludes')]
    random_size = int(re.search(r'^randompoolsize = (\d+)', lua, re.M).group(1))
    random_exc = jtl + ['iron', 'fiberplast']
    fixed = [('iron', 14)] + [(j, 1) for j in jtl]
    native = re.search(r'^nativepoolincludes = "([^"]+)"', lua, re.M).group(1).split(',')
    return {'minimum': minimum, 'minimum_excludes': jtl, 'random': random_inc, 'random_size': random_size, 'random_excludes': random_exc, 'fixed': fixed, 'native': native, 'jtl': jtl}


def main():
    stock, stock_order, _ = read_tree(open(STOCK, 'rb').read())
    merged_files = tre_write.read(open(MERGED_TRE, 'rb').read())[0]
    merged, order, anc = read_tree(merged_files['datatables/resource/resource_tree.iff'])
    idx = I.client_index()
    mtg, mtg_order, _ = read_tree(I.open_tre_entry(os.path.join(I.CLIENT, 'mtg_planets.tre'), 'datatables/resource/resource_tree.iff'))
    mtg22, mtg22_order, _ = read_tree(I.open_tre_entry(os.path.join(I.CLIENT, 'mtg_patch_022.tre'), 'datatables/resource/resource_tree.iff'))   # Taanab's 45 live here
    for e in mtg22_order:
        if e not in mtg:
            mtg[e] = mtg22[e]
            mtg_order.append(e)
    pools = parse_pools(open(LUA, encoding='utf-8').read())
    # schematics: token -> files; a schematic accepts a node if it names the node or one of its ancestors
    sch = defaultdict(set)
    for line in open(SCHEMATICS, encoding='utf-8'):
        if ':' not in line:
            continue
        f, types = line.rstrip('\n').split(':', 1)
        for tkn in types.split(','):
            if tkn and not tkn.startswith('object/'):
                sch[tkn].add(f)

    def consumers(enum, a):
        files = set()
        for n in [enum] + a.get(enum, []):
            files |= sch.get(n, set())
        return files

    def under(enum, cls, a):
        return enum == cls or cls in a.get(enum, [])

    def pool_of(enum, a, planet):
        out = []
        if planet:
            base = enum[:enum.index('_' + planet)] if ('_' + planet) in enum else enum
            if base in pools['native'] and planet in ('corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4', 'hoth', 'ossus'):
                out.append('native (one per planet)')
            for n, c in pools['minimum']:
                if n == enum:
                    out.append('minimum x%d (own entry)' % c)
            return out
        for n, c in pools['minimum']:
            if under(enum, n, a) and not any(under(enum, x, a) for x in pools['minimum_excludes']):
                out.append('minimum x%d via %s' % (c, n))
        for n, w in pools['random']:
            if under(enum, n, a) and not any(under(enum, x, a) for x in pools['random_excludes']):
                out.append('random via %s (weight %d of 100, %d spawns)' % (n, w, pools['random_size']))
        for n, c in pools['fixed']:
            if under(enum, n, a):
                out.append('fixed x%d via %s' % (c, n))
        return out

    def coverage(row, pool_list):
        if row['planet']:
            return {'planets': 1, 'note': row['planet']}
        if not pool_list:
            return {'planets': 0, 'note': 'never spawned'}
        mn, mx = row['pools']
        s = lambda v: min(ZONES_TODAY, round(v * ZONES_TODAY / SCALE_BASE))   # noqa: E731
        return {'planets_min': s(mn), 'planets_max': s(mx), 'of': ZONES_TODAY, 'stock_pools': [mn, mx], 'scale': '%d/%d' % (ZONES_TODAY, SCALE_BASE)}
    rows = []
    hoth_r3 = {'armophous_hoth_1', 'armophous_hoth_2', 'crystalline_hoth_1', 'crystalline_hoth_2', 'energy_renewable_site_limited_geothermal_hoth', 'energy_renewable_site_limited_tidal_hoth', 'energy_renewable_site_limited_hydron3_hoth'}
    for e in order:
        r = dict(merged[e])
        if e in stock:
            src = 'stock'
        elif e in hoth_r3:
            src = 'mtg_hoth (R3 part 1)' if 'energy' not in e else 'hoth clone (R3 part 1)'
        elif e.endswith('_hoth'):
            src = 'mtg_hoth' if e in mtg else 'hoth clone (builder)'
        elif '_ossus' in e:
            src = 'ossus (R3 part 2)' if e not in {x for x in order if x.endswith('_ossus') and any(x.startswith(p) for p in ('milk', 'meat', 'seafood', 'bone', 'hide', 'corn', 'rice', 'oats', 'wheat', 'vegetable', 'fruit', 'wood', 'softwood', 'fiberplast', 'water', 'energy'))} else 'ossus (O2c)'
        else:
            src = 'other'
        pl = pool_of(e, anc, r['planet']) if r['leaf'] else []
        if r['leaf'] and not pl and r.get('recycled'):
            pl = ['recycler output (Recycled flag; never a spawn by design)']
        c = consumers(e, anc)
        r.update({'source': src, 'in_test_archive': True, 'pool_today': pl, 'coverage': coverage(r, pl) if r['leaf'] else None,
                  'consumer_schematics': len(c), 'consumer_examples': sorted(c)[:3]})
        rows.append(r)
    # MTG extras not merged (kaas, taanab are in mtg_patch_022, space, the 3 energy class rows)
    extras = []
    for e in mtg_order:
        if e in merged:
            continue
        r = dict(mtg[e])
        r.update({'source': 'mtg (not merged)', 'in_test_archive': False, 'pool_today': [], 'coverage': {'planets': 0, 'note': 'not in our tree'},
                  'consumer_schematics': len(consumers(e, anc if e in anc else {e: mtg[e]['class_enums']})), 'consumer_examples': []})
        extras.append(r)
    # the owner's book
    book = []
    planet = ''
    for line in open(BOOK, encoding='utf-8'):
        m = re.match(r'^\| ([^|]*)\| ([^|]*)\| (.*)\|\s*$', line)
        if not m or m.group(2).strip() in ('Book mat', '---'):
            continue
        p, mat, real = (s.strip() for s in m.groups())
        if p:
            planet = p
        if planet not in ('Tatooine', 'Naboo', 'Corellia', 'Talus', 'Rori', 'Dantooine', 'Lok', 'Yavin 4', 'Endor', 'Dathomir'):
            continue
        low = real.lower()
        if 'not a resource' in low or 'not resources' in low or 'inactive' in low or 'story item' in low or 'crafted component' in low:
            kind = 'not a resource'
        elif '**no' in low:
            kind = 'new class'
        elif low.startswith('no ') or 'nearest' in low:
            kind = 'nearest existing class'
        else:
            kind = 'exists'
        book.append({'planet': planet, 'book_mat': mat, 'real_swg': real, 'kind': kind})
    # site-limited energies per stock planet
    site = {}
    for p in STOCK_PLANETS + ['hoth', 'ossus']:
        site[p] = {}
        for kind in ('geothermal', 'tidal', 'hydron3'):
            e = 'energy_renewable_site_limited_%s_%s' % (kind, p)
            if e not in merged:
                site[p][kind] = 'no row'
            else:
                pl = pool_of(e, anc, p)
                site[p][kind] = ('spawned: ' + '; '.join(pl)) if pl else 'in tree, never spawned'
    # summaries
    by_source = Counter(r['source'] for r in rows)
    leaves = [r for r in rows if r['leaf']]
    never = [r['enum'] for r in leaves if not r['pool_today']]
    recycled = [r['enum'] for r in leaves if r.get('recycled')]
    cls3 = Counter((r['class_path'][2] if len(r['class_path']) > 2 else r['class_path'][-1] if r['class_path'] else 'root') for r in leaves)
    out = {'built': '2026-10-14', 'sources': {'stock_rows': len(stock_order), 'mtg_rows': len(mtg_order), 'mtg_extras': len(mtg_order) - sum(1 for e in mtg_order if e in stock),
                                              'merged_test_archive_rows': len(order), 'by_source': by_source, 'book_mats': len(book)},
           'pools': pools, 'scaling': {'poolScaleZones': SCALE_BASE, 'active_zones_today': ZONES_TODAY},
           'leaf_types': len(leaves), 'leaf_types_never_spawned': never, 'site_limited_energies': site,
           'rows': rows, 'mtg_not_merged': extras, 'book': book,
           'schematics': {'files_with_resource_types': len({f for s in sch.values() for f in s}), 'tokens': len(sch)}}
    with open(os.path.join(R3, 'inventory.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else o)
    # ---- markdown
    L = []
    L.append('# Resource inventory (R3 part 3) — Fable, 14 Oct 2026')
    L.append('')
    L.append('Every resource row we may use, with its class path, attributes, planet restriction, the pool that spawns it today, its')
    L.append('planet coverage under `poolScaleZones = %d` with %d active zones, and the schematics that would take it. Rows: `inventory.json`.' % (SCALE_BASE, ZONES_TODAY))
    L.append('Sources: the stock tree (%d rows), MTG\'s tree (%d rows, %d beyond stock), our test-session tree (%d rows: stock + Hoth %d + Ossus %d),' % (
        len(stock_order), len(mtg_order), out['sources']['mtg_extras'], len(order), sum(1 for e in order if '_hoth' in e), sum(1 for e in order if '_ossus' in e)))
    L.append('the owner\'s book (%d mats for the ten stock planets; reference for new mats only). Excluded: SWG-Source, the Legends leak, Zeltros (on hold).' % len(book))
    L.append('Pools from `resource_manager.lua` as patched by parts 1–2. Consumers from the %d Core3 draft schematics that name resource classes (%d distinct class tokens).' % (out['schematics']['files_with_resource_types'], out['schematics']['tokens']))
    L.append('')
    L.append('## 1. What we have, by source')
    L.append('')
    L.append('| source | rows |')
    L.append('|---|---|')
    for k, v in sorted(by_source.items()):
        L.append('| %s | %d |' % (k, v))
    L.append('| mtg (not merged: Dromund Kaas %d, Taanab %d, space %d, energy class rows %d) | %d |' % (
        sum(1 for r in extras if r['enum'].endswith('_kaas')), sum(1 for r in extras if r['enum'].endswith('_taanab')), sum(1 for r in extras if r['enum'].startswith('space_')),
        sum(1 for r in extras if r['enum'].startswith('energy_renewable_site_limited') and not r['planet']), len(extras)))
    L.append('| owner book mats (10 planets): exists %d, nearest existing class %d, new class %d, not a resource %d | %d |' % (
        sum(1 for b in book if b['kind'] == 'exists'), sum(1 for b in book if b['kind'] == 'nearest existing class'), sum(1 for b in book if b['kind'] == 'new class'), sum(1 for b in book if b['kind'] == 'not a resource'), len(book)))
    L.append('')
    L.append('## 2. Leaf types by class (our tree, %d leaves)' % len(leaves))
    L.append('')
    L.append('| class (third level) | leaves | spawned by some pool | never spawned | galaxy-wide | planet-restricted | schematics taking the class (min–max over its leaves) |')
    L.append('|---|---|---|---|---|---|---|')
    for c, n in sorted(cls3.items()):
        ls = [r for r in leaves if (r['class_path'][2] if len(r['class_path']) > 2 else r['class_path'][-1] if r['class_path'] else 'root') == c]
        cons = [r['consumer_schematics'] for r in ls]
        L.append('| %s | %d | %d | %d | %d | %d | %d–%d |' % (c, n, sum(1 for r in ls if r['pool_today']), sum(1 for r in ls if not r['pool_today']), sum(1 for r in ls if not r['planet']), sum(1 for r in ls if r['planet']), min(cons), max(cons)))
    L.append('')
    L.append('Never spawned today (%d leaves, the %d recycler outputs such as processed_meat left out): %s.' % (len(never), len(recycled), ', '.join(never[:45]) + (' …' if len(never) > 45 else '')))
    L.append('')
    L.append('## 3. Planet coverage under the scaling')
    L.append('')
    L.append('Galaxy-wide leaf: Minimum/Maximum # Pools × %d/%d, capped at %d (8/8 → 10/10; 1/3 → 1/4; 1/1 → 1/1). Native and planet-restricted' % (ZONES_TODAY, SCALE_BASE, ZONES_TODAY))
    L.append('types: one planet. Per-leaf values are in the JSON (`coverage`). The random pool keeps %d spawns and the minimum pool one per entry,' % pools['random_size'])
    L.append('so scaling widens where each spawn lives, not how many there are.')
    L.append('')
    L.append('## 4. The site-limited energies (owner question: nativepoolincludes galaxy-wide?)')
    L.append('')
    L.append('| planet | geothermal | tidal | hydron-3 |')
    L.append('|---|---|---|---|')
    for p, d in site.items():
        L.append('| %s | %s | %s | %s |' % (p, d['geothermal'], d['tidal'], d['hydron3']))
    L.append('')
    L.append('Every stock planet has all three rows in the tree and no pool ever spawns them (the native list carries solar and wind only).')
    L.append('Adding `energy_renewable_site_limited_geothermal,energy_renewable_site_limited_tidal,energy_renewable_site_limited_hydron3` to')
    L.append('`nativepoolincludes` spawns one of each on every active planet (45 natives a planet instead of 42; Hoth\'s three minimum-pool')
    L.append('lines then become redundant); Ossus has the three rows (O2c cloned Dantooine%ss 45) and, like the stock planets, nothing spawns them yet.' % chr(39))
    L.append('')
    L.append('## 5. New classes and who would consume them')
    L.append('')
    L.append('A new **leaf** under an existing class is used by every schematic that names the class or an ancestor on day one (e.g. a steel')
    L.append('leaf: %d schematics name steel, metal_ferrous, metal or an ancestor). A new **class** has no consumer until a schematic names it.' % (merged.get('steel') and len(consumers('steel', anc)) or 0))
    L.append('')
    L.append('| book mat (planet) | kind | nearest in SWG | consumers today |')
    L.append('|---|---|---|---|')
    for b in [b for b in book if b['kind'] in ('new class', 'nearest existing class')]:
        L.append('| %s (%s) | %s | %s | %s |' % (b['book_mat'], b['planet'], b['kind'], b['real_swg'].replace('|', '/'), 'none (new class: needs a tree class, container, survey tool and recipes)' if b['kind'] == 'new class' else 'the nearest class\'s schematics'))
    L.append('')
    L.append('## 6. Integration list, cheap first')
    L.append('')
    L.append('1. **Done in the chain (parts 1–2):** Hoth 54 + 3 energies, Ossus 45 natives + 14 minerals; all under stock classes, so every existing')
    L.append('   recipe that takes the class takes them (steel: %d schematics, ore: %d, gas: %d, radioactive: %d, gemstone: %d).' % tuple(len(consumers(c, anc)) for c in ('steel', 'ore', 'gas', 'radioactive', 'gemstone')))
    L.append('2. **Site-limited energies into the native pool** (30 stock rows already in the tree, never spawned): one Lua line, galaxy-wide, +3 natives a planet.')
    L.append('3. **Planet minerals for the ten stock planets**, Hoth-style: 14 restricted leaves a planet (140 rows) by the part-2 rule, minimum pool one each;')
    L.append('   gives every planet its own named steel/ore/gas/fuel/gems inside existing recipes. One stage step (ossus_minerals generalised).')
    L.append('4. **MTG\'s Dromund Kaas (45) and Taanab (45) natives** when those planets exist; **MTG\'s 18 space rows** only with space zones (JTL mining).')
    L.append('5. **New classes from the book** (biomass ×4, plant resin, filter peat, clay, plasma feedstock, sulfur feedstock): each needs a tree class under')
    L.append('   organic/inorganic, a container template, a survey-tool type, string names and at least one recipe (Botanist, Pharmacist, Toxicologist); no')
    L.append('   consumer exists today, so they come with those professions, not before.')
    L.append('6. **Lore materials (slot for ChatGPT, Legends):** Mandalorian iron (Mandalore), Adegan crystals (Ossus; a gemstone leaf fits the Jedi story),')
    L.append('   cortosis, phrik (note: `aluminum_phrik` is already a stock aluminum leaf, galaxy-wide), songsteel, durasteel as a steel leaf, etc. Each lore')
    L.append('   material as a planet-restricted leaf under its stock class (cheap) or as a new class (expensive) once the planet and its story exist.')
    with open(os.path.join(R3, 'inventory.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('rows', len(rows), 'leaves', len(leaves), 'never spawned', len(never), 'extras', len(extras), 'book', len(book))
    print('by source', dict(by_source))
    print('site', {p: d for p, d in list(site.items())[:3]})
    print('consumers steel', len(consumers('steel', anc)), 'metal', len(consumers('metal', anc)), 'hide_wooly_hoth', len(consumers('hide_wooly_hoth', anc)))


if __name__ == '__main__':
    main()
