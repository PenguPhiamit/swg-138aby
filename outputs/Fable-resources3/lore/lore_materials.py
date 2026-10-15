"""C29: Legends materials for the owner's resource plan -> lore-materials.md and lore-materials.json (Fable, 14 October 2026).

The records below are our own one- or two-line summaries of what Wookieepedia (Legends continuity first) says, each with
the page URL; Wookieepedia's text is CC BY-SA, so none of it is copied, and the in-game names are ours. For every material the
script looks up the stock class in R3's inventory.json (consumer counts: schematics that accept the class or one of its
ancestors) and computes attribute floors and ceilings either by the R3 part-2 rule (clone of the strongest stock leaf of the
class by summed minimums; quality minimum 500; other minimums rounded up to the next multiple of 50 unless that reaches the
maximum) or by a stated variant on a named base row. Era: the owner's New Jedi Order to Legacy window (25 to about 140 ABY).
    python -I lore_materials.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(R3, 'tools'))
import ossus_minerals as om  # noqa: E402  (PLANETS, JTL, round_up50)

INV = json.load(open(os.path.join(R3, 'inventory.json'), encoding='utf-8'))
ROWS = INV['rows']
BY = {r['enum']: r for r in ROWS}
W = 'https://starwars.fandom.com/wiki/'

# ---- the rule, from inventory rows -------------------------------------------------------------------------------

def strongest(cls):
    best, score = None, -1
    for r in ROWS:
        e = r['enum']
        if not r['leaf'] or cls not in r['class_enums'] or r['source'] != 'stock':
            continue
        if e.rsplit('_', 1)[-1] in om.PLANETS or e in om.JTL or e.endswith('_unknown') or '_hoth' in e or '_ossus' in e:
            continue
        s = sum(a[1] for a in r['attributes'])
        if s > score:
            best, score = r, s
    return best


def part2(cls):
    sib = strongest(cls)
    if sib is None:
        return None, None
    return sib['enum'], [(a, max(mn, 500) if a == 'res_quality' else om.round_up50(mn, mx), mx) for a, mn, mx in sib['attributes']]


def variant(base_enum, overrides):
    base = BY[base_enum]
    out = []
    for a, mn, mx in base['attributes']:
        if a in overrides:
            lo, hi = overrides[a]
            assert lo <= hi <= mx and lo >= 1, (base_enum, a, overrides[a], mx)
            out.append((a, lo, hi))
        else:
            out.append((a, mn, mx))
    return out


def consumers(cls):
    r = BY.get(cls)
    return (r['consumer_schematics'], r['consumer_examples'][:3]) if r else (0, [])


def short_attr(a):
    return {'res_decay_resist': 'DR', 'res_quality': 'OQ', 'res_cold_resist': 'CR', 'res_heat_resist': 'HR', 'res_malleability': 'MA',
            'res_toughness': 'UT', 'res_shock_resistance': 'SR', 'res_conductivity': 'CD', 'res_flavor': 'FL', 'res_potential_energy': 'PE',
            'entangle_resistance': 'ER'}.get(a, a)


def floors_text(attrs):
    return ' '.join(f'{short_attr(a)} {lo}-{hi}' for a, lo, hi in attrs) if attrs else '-'


# ---- the records -------------------------------------------------------------------------------------------------
# planet_state: ours | candidate | stock (a stock SWG planet) | other (no planet of ours)

MATERIALS = [
    dict(name='Adegan crystal', planets='Ossus (Adega system)', planet_state='ours', continuity='Legends',
         text='The Jedi\'s lightsaber crystals of the Old Republic came from the Adega system, and the first were found on Ossus. '
              'Five grades are named, kathracite the common training crystal and pontite the rarest; Ossus\'s Crystal Caves kept the Ysanna alive after the Cron supernova.',
         era='Known through all eras; Ossus hosted the Jedi Academy after the Vong war until the Sith raid of 130 ABY, so the crystals are in the window.',
         canon='Canon folds Adegan crystals into kyber and puts pontite in Ossus\'s caverns; Legends has no kyber.',
         sources=[W + 'Adegan_crystal/Legends', W + 'Ossus/Legends', W + 'Adega_system'],
         stock='not in the tree (the Ossus Type 1/2 gems are generic names)',
         proposal=dict(kind='leaf', cls='gemstone_crystalline', enum='crystalline_adegan_ossus', text='Adegan Crystal Crystalline Gemstone', rule='part-2',
                       pool='minimum pool 1 on Ossus, types 1/2; the random gemstone pool may add a second spawn, Ossus only', staged=True,
                       option='Cheaper still: rename crystalline_ossus_1/2 to Kathracite / Pontite (text only; new spawns only). Not done, it changes names already in play.')),
    dict(name='Lumni-spice (lumni lichen)', planets='Hoth (also Corulag)', planet_state='ours', continuity='Legends',
         text='Lumni lichen is a scarce fungus that grows on a few worlds, Hoth among them, in a sunless fissure near the equator; it is the source of lumni-spice, '
              'called the rarest spice in the galaxy, and dragon slugs grow huge on it. Pirates and a Shi\'ido changeling\'s wampa-run mine have gone after it.',
         era='Ancient stories (Raskar before Echo Base, the 27 BBY mine); nothing says it ran out, so it is in the window.',
         canon='Legends only.', sources=[W + 'Lumni-spice', W + 'Lumni_lichen', W + 'Hoth/Legends'],
         stock='not in the tree; Hoth has the generic vegetable_fungi_hoth native',
         proposal=dict(kind='leaf', cls='vegetable_fungi', enum='vegetable_fungi_lumni_hoth', text='Lumni Lichen Fungus',
                       rule='variant', base='vegetable_fungi_hoth', overrides={'res_quality': (500, 1000), 'res_flavor': (700, 1000), 'res_potential_energy': (500, 1000)},
                       pool='minimum pool 1 on Hoth, types 1/1 (as natives); the native pool never picks it (it builds <class>_<planet> names)', staged=True,
                       option='A Smuggler schematic "Lumni-spice" taking this fungus would make the spice itself; the pre-CU spice line has no fungus input today.')),
    dict(name='Hoth asteroid-field metals', planets='Hoth system (the Anoat belt, meteorites on Hoth)', planet_state='ours', continuity='Legends',
         text='The belt beyond Hoth formed from two shattered planets and holds nickel-iron ore, a rumoured platinum body (Kerane\'s Folly) and silicon crystal ferns; '
              'pieces fall on Hoth as meteorites, and the Hutts\' Orko SkyMine dug it for the Darksaber in 12 ABY.',
         era='Mining documented at 12 ABY; the belt is still there in the window.', canon='Legends page used.',
         sources=[W + 'Hoth_asteroid_field/Legends', W + 'Hoth/Legends'],
         stock='iron_hoth (Kammris clone) already covers Hoth\'s iron',
         proposal=dict(kind='text-option', cls='iron', enum='iron_hoth', text='Meteoric Iron (text only)', rule='keep iron_hoth\'s floors',
                       pool='unchanged', staged=False,
                       option='Space-only ore belongs to JTL mining if that ever comes; on the ground a rename of iron_hoth\'s class text is the whole cost (new spawns only).')),
    dict(name='Mandalorian iron (beskar)', planets='Mandalore, its moon Concordia', planet_state='candidate', continuity='Legends',
         text='Beskar comes only from Mandalore and Concordia. Forged with carbon it is light for its toughness and shrugs off lightsabers, which is why it outranks durasteel and cortosis; '
              'the Empire strip-mined it with slave labour and the Death Watch kept digging in secret.',
         era='In the window: fresh lodes were exposed by the Yuuzhan Vong attack, and Mandalore prospered on them under Boba Fett around the Second Galactic Civil War (40 ABY).',
         canon='Canon also calls it Mandalorian steel and an alloy; same worlds.', sources=[W + 'Beskar/Legends', W + 'Mandalore/Legends', W + 'Concordia/Legends'],
         stock='not in the tree',
         proposal=dict(kind='leaf', cls='iron', enum='iron_beskar_mandalore', text='Mandalorian Iron', rule='variant', base='iron_hoth',
                       overrides={'res_quality': (500, 1000), 'res_decay_resist': (900, 1000), 'res_cold_resist': (700, 800), 'res_heat_resist': (950, 1000),
                                  'res_malleability': (1, 150), 'res_toughness': (950, 1000), 'res_shock_resistance': (950, 1000), 'res_conductivity': (1, 150)},
                       pool='minimum pool 1 on Mandalore, max pool 1, types 1/1: one spawn at a time, never in the random pool (add it to randompoolexcludes)', staged=False,
                       option='Under iron, every armour and weapon recipe that takes iron, ferrous metal or metal (693) can use it; the stated floors make it the best iron in the game. '
                              'A steel leaf would reach 984 recipes but the name says iron.')),
    dict(name='Cortosis', planets='Apatros, Bal\'demnic, Duro, Katanos VII, Obredaan (none of ours)', planet_state='other', continuity='Legends',
         text='An ore whose conductive quirk shorts out a lightsaber on contact; too brittle for plain armour, so it is woven in, and refined cortosis-shield is the prized form (Roan Fel\'s Imperial Knights use it).',
         era='In the window (Imperial Knights, Legacy comics).', canon='Canon lists other worlds (Dinzo, Mokivj).', sources=[W + 'Cortosis/Legends'],
         stock='ALREADY STOCK: ore_siliclastic_cortosis "Cortosis Siliclastic Ore", galaxy-wide random pool',
         proposal=dict(kind='stock-already', cls='ore_siliclastic', enum='ore_siliclastic_cortosis', text='Cortosis Siliclastic Ore', rule='stock', pool='stock', staged=False,
                       option='Do not duplicate. A planet-locked rich variant could follow a cortosis world if one is ever added.')),
    dict(name='Phrik', planets='Gromas 16 (not ours)', planet_state='other', continuity='Legends',
         text='A light, nearly indestructible alloy made from phrikite ore of the moon Gromas 16 and tydirium; it resists lightsabers and went into MagnaGuard electrostaffs and Dark Trooper armour, at a price that kept it rare.',
         era='In the window as an alloy; the mine\'s later history is not given.', canon='Canon adds Tatooine as a source.', sources=[W + 'Phrik/Legends', W + 'Phrikite'],
         stock='ALREADY STOCK: aluminum_phrik "Phrik Aluminum", galaxy-wide random pool',
         proposal=dict(kind='stock-already', cls='aluminum', enum='aluminum_phrik', text='Phrik Aluminum', rule='stock', pool='stock', staged=False,
                       option='Do not duplicate.')),
    dict(name='Songsteel', planets='Cularin asteroid belt (not ours)', planet_state='other', continuity='Legends',
         text='A rare metal found in the Cularin belt during the Confederation Rock Rush; it turns lightsabers much as phrik and cortosis do without shorting them, and only exquisite, costly weapons were made of it.',
         era='Appearances are Rise of the Empire era; nothing says it is gone.', canon='Legends only.', sources=[W + 'Songsteel/Legends'],
         stock='not in the tree',
         proposal=dict(kind='leaf', cls='steel', enum='steel_songsteel', text='Songsteel', rule='part-2',
                       pool='no planet of ours: galaxy-wide random pool only, low weight (a rarity between the stock steels), or skip', staged=False,
                       option='984 steel recipes would take it; without a planet story it is just another top steel, so it is listed, not recommended.')),
    dict(name='Corusca gem', planets='Yavin Prime\'s atmosphere (Yavin 4 is its moon; stock planet)', planet_state='stock', continuity='Legends',
         text='Gems formed by the pressure of Yavin\'s gas-giant depths, fished from the upper layers or mined deep by Lando\'s GemDiver Station from 23 ABY; '
              'prized, lightsaber-capable, and brittle at their shatterpoints.',
         era='GemDiver Station (23 ABY) puts the mining right at the start of the window; Corusca crystals armed New Jedi Order lightsabers.', canon='Legends page used.',
         sources=[W + 'Corusca_gem/Legends', W + 'Yavin_Prime/Legends', W + 'GemDiver_Station'],
         stock='not in the tree',
         proposal=dict(kind='leaf', cls='gemstone_crystalline', enum='crystalline_corusca_yavin4', text='Corusca Gem Crystalline Gemstone', rule='part-2',
                       pool='minimum pool 1 on Yavin 4, types 1/2', staged=False,
                       option='A stretch: the gems come from the gas giant, not the moon. Surveying them on Yavin 4 is a game convenience; the honest alternative is a GemDiver vendor or loot item.')),
    dict(name='Mirkanite', planets='Mustafar', planet_state='candidate', continuity='Legends',
         text='A rare allotrope in Mustafar\'s crust and lava, melting low enough that the lava can be skimmed at about 800 C; the Techno Union and then the Empire mined it, and it went into the first Death Star\'s superlaser.',
         era='Imperial-era mining is documented; no source for 25+ ABY, so mark the mine\'s state an open question.', canon='Legends page used.',
         sources=[W + 'Mirkanite/Legends', W + 'Mustafar/Legends'],
         stock='not in the tree; Mustafar\'s other named ores dolovite and bronzium are stock iron leaves (iron_dolovite, iron_bronzium, galaxy-wide)',
         proposal=dict(kind='leaf', cls='ore_extrusive', enum='ore_extrusive_mirkanite_mustafar', text='Mirkanite Extrusive Ore', rule='part-2',
                       pool='minimum pool 1 on Mustafar, types 1/2', staged=False,
                       option='308 recipes take extrusive ore (armour layers, shield emitters). The lore-true variant would lower its heat-resistance ceiling (it melts low) and raise quality (superlaser grade).')),
    dict(name='Wroshyr wood', planets='Kashyyyk', planet_state='candidate', continuity='Legends',
         text='Timber of the kilometre-tall wroshyr trees: strong and flexible enough for starship hulls under shields, exported as costly flooring, and worked into Wookiee weapons, furniture and homes.',
         era='Kashyyyk stood through the Vong war; the trees are in the window.', canon='Legends page used.',
         sources=[W + 'Wroshyr_wood/Legends', W + 'Wroshyr_tree/Legends'],
         stock='not in the tree (natives would be wood_deciduous_kashyyyk)',
         proposal=dict(kind='leaf', cls='wood_deciduous', enum='wood_deciduous_wroshyr_kashyyyk', text='Wroshyr Hard Wood', rule='variant', base='wood_deciduous_hoth',
                       overrides={'res_quality': (500, 1000), 'res_decay_resist': (400, 800), 'res_malleability': (600, 800), 'res_toughness': (600, 800), 'res_shock_resistance': (500, 700)},
                       pool='minimum pool 1 on Kashyyyk, types 1/1', staged=False,
                       option='113 recipes take hard wood, including the Kashyyykian armour segments already in the schematic set.')),
    dict(name='Yorik coral', planets='Coruscant (Yuuzhan\'tar) and other Vongformed worlds, Nal Hutta among them', planet_state='candidate', continuity='Legends',
         text='The Yuuzhan Vong\'s grown shipbuilding stuff, hard enough to armour the Senate Building; after the war it kept growing in Coruscant\'s undercity and was even used as park decoration, '
              'and Vongformed remnants were still on the planet in 40 ABY.',
         era='ERA-SPECIFIC: did not exist in the galaxy before 25 ABY; remnants fit the whole window (Krayt still used yorik-kul seeds in 137 ABY).', canon='Legends only.',
         sources=[W + 'Yorik_coral', W + 'World_Brain'],
         stock='no stock class fits (grown biotech, not mined or farmed)',
         proposal=dict(kind='new-class or loot', cls='creature_structural', enum='-', text='Yorik Coral', rule='n/a',
                       pool='harvest node or loot from Vong remnants rather than a survey resource', staged=False,
                       option='Cheapest honest route: a bone-class leaf would feed 132 recipes but reads wrong; better a loot component for an era quest line. Needs a container and strings either way.')),
    dict(name='Dromund Kaas flora', planets='Dromund Kaas', planet_state='candidate', continuity='Legends',
         text='A jungle, swamp and ocean world; the Legends page names its flora Amanita Lumikurnizi (a fungus), the dart flower and Monotropa Triflora, and gives no mined resource.',
         era='Prophets of the Dark Side era documented; nothing for the window.', canon='Legends page used.', sources=[W + 'Dromund_Kaas/Legends'],
         stock='MTG\'s 45 Kaas natives are in the tree (vegetable_fungi_kaas, fruit_flowers_kaas ...)',
         proposal=dict(kind='text-option', cls='vegetable_fungi', enum='vegetable_fungi_kaas', text='Lumikurnizi Fungus (text only)', rule='keep the native\'s floors',
                       pool='unchanged', staged=False,
                       option='Lore names for the existing natives (fungus, flower) are free; a dark-side material would be our invention and is not proposed.')),
    dict(name='Chandrilan foods (muja, jaquira)', planets='Chandrila', planet_state='candidate', continuity='Legends',
         text='A Core agriworld that cornered the market in perishable luxury food: grains, muja and jaquira fruit, vegetables, beans and spices, with squalls wandering its roads.',
         era='Agriworld through the window.', canon='Legends page used.', sources=[W + 'Chandrila/Legends'],
         stock='not in the tree (natives would be fruit_fruits_chandrila ...)',
         proposal=dict(kind='leaf', cls='fruit_fruits', enum='fruit_fruits_muja_chandrila', text='Muja Fruit', rule='variant', base='fruit_fruits_hoth',
                       overrides={'res_quality': (500, 1000), 'res_flavor': (600, 1000)},
                       pool='minimum pool 1 on Chandrila, types 1/1; a second leaf "Jaquira Fruit" the same way', staged=False,
                       option='199 chef and bio-engineer recipes take fruit; squall meat is a creature template question, not a tree row.')),
    dict(name='Taanab livestock (roba, staga)', planets='Taanab', planet_state='candidate', continuity='Legends',
         text='An Inner Rim farm world feeding the Mid and Outer Rim, known for roba steak; staga came from Ambria as a food animal when Taanab was settled.',
         era='Agriworld through the window.', canon='Legends page used.', sources=[W + 'Taanab/Legends', W + 'Roba/Legends', W + 'Staga/Legends'],
         stock='MTG\'s 45 Taanab natives are in the tree (meat_domesticated_taanab ...)',
         proposal=dict(kind='creature-text', cls='meat_domesticated', enum='meat_domesticated_taanab', text='Roba Meat (text only)', rule='keep the native\'s floors',
                       pool='unchanged', staged=False,
                       option='Creature resources come from creature templates, not surveys: a roba creature yielding Taanab domesticated meat is the whole feature; naming the native "Roba Meat" is free.')),
    dict(name='Nal Hutta swamp chemicals', planets='Nal Hutta', planet_state='candidate', continuity='Legends',
         text='A world without natural heavy metals, strip-mined and bulldozed into swamps whose polluted waters are filtered for valuable chemicals (the New Muckworks); spice is the Hutt commodity.',
         era='Vongformed in the war (the page lists Vongformed terrain), so the window has both swamp and coral.', canon='Legends page used.',
         sources=[W + 'Nal_Hutta/Legends', W + 'New_Muckworks'],
         stock='no match; natives would follow the stock pattern',
         proposal=dict(kind='rule', cls='petrochem_inert', enum='-', text='Hutta Swamp Distillate (class to choose with the planet)', rule='n/a',
                       pool='design rule: no metal in Nal Hutta\'s pools (no heavy metals); a chemical/petrochem leaf as its one signature material', staged=False,
                       option='397 recipes take inert petrochemicals; which subclass (polymer, lubricating oil) is a planet-design choice.')),
    dict(name='Korriban', planets='Korriban (zone moraband)', planet_state='candidate', continuity='Legends',
         text='Red sands, tombs and the Valley of the Dark Lords; the page lists generic exports (raw material, weapons, artifacts) and no named mineral, and Sith lightsaber crystals are synthetic, not mined.',
         era='Sith ground in every era; the Legacy comics (130-139 ABY) have Krayt\'s One Sith, and the page gives no mining history for the window.',
         canon='Canon calls it Moraband (our zone key).', sources=[W + 'Korriban/Legends', W + 'Sith_lightsaber/Legends'],
         stock='-', proposal=dict(kind='none', cls='-', enum='-', text='-', rule='n/a', pool='-', staged=False,
                                  option='Nothing Legends-backed to add; a "Korriban sandstone" would be our invention. Standard natives only.')),
    dict(name='Coruscant', planets='Coruscant', planet_state='candidate', continuity='Legends',
         text='An ecumenopolis with no natural raw materials of its own; the Vong war left yorik coral and Vongformed ground (see Yorik coral).',
         era='-', canon='-', sources=[W + 'Yorik_coral'], stock='-',
         proposal=dict(kind='none', cls='-', enum='-', text='-', rule='n/a', pool='-', staged=False, option='Standard natives make little sense for a city planet; yorik coral is the era hook.')),
    dict(name='Kaiburr / kyber crystal', planets='Mimban (Legends relic); everywhere (canon kyber)', planet_state='other', continuity='canon-only as a resource',
         text='In Legends the Kaiburr crystal is one unique Force-amplifying relic in the Temple of Pomojema on Mimban, powerless off-world; the galaxy-wide "kyber crystal" that grows on many planets is canon.',
         era='n/a', canon='CANON-ONLY as a mineable material.', sources=[W + 'Kaiburr_crystal', W + 'Kyber_crystal'],
         stock='-', proposal=dict(kind='none', cls='-', enum='-', text='-', rule='n/a', pool='-', staged=False, option='Not a resource in Legends; the Adegan crystal is the Legends equivalent.')),
    dict(name='Durasteel', planets='manufactured', planet_state='other', continuity='Legends',
         text='The galaxy\'s everyday structural alloy; it is made, not mined.', era='-', canon='-', sources=[W + 'Durasteel/Legends'],
         stock='the stock tree already has Duralloy Steel (steel_duralloy) as its top steel',
         proposal=dict(kind='none', cls='steel', enum='steel_duralloy', text='-', rule='n/a', pool='-', staged=False, option='No leaf: an alloy is a crafted product.')),
]

STOCK_LORE_LEAVES = [('ore_siliclastic_cortosis', 'cortosis (Legends worlds above)'), ('aluminum_phrik', 'phrik (Gromas 16)'), ('iron_doonium', 'doonium'),
                     ('iron_dolovite', 'dolovite (named for Mustafar)'), ('iron_bronzium', 'bronzium (named for Mustafar)'), ('steel_duralloy', 'duralloy'),
                     ('ore_carbonate_lommite', 'lommite'), ('armophous_baradium', 'baradium'), ('armophous_ryll', 'ryll'), ('steel_carbonite', 'carbonite'),
                     ('aluminum_titanium', 'titanium'), ('aluminum_chromium', 'chromium')]


def build():
    out = []
    for m in MATERIALS:
        p = m['proposal']
        attrs, base = None, None
        if p['rule'] == 'part-2':
            base, attrs = part2(p['cls'])
        elif p['rule'] == 'variant':
            base, attrs = p['base'], variant(p['base'], p['overrides'])
        n, examples = consumers(p['cls']) if p['cls'] in BY else (0, [])
        out.append(dict(m, proposal=dict(p, base=base, attrs=attrs, consumers=n, consumer_examples=examples)))
    return out


def md(records, checks):
    L = []
    L += ['# C29: Legends materials for the resource plan (Fable, 14 October 2026)', '',
          'Lore read on Wookieepedia, Legends continuity first (its text is CC BY-SA: these lines are ours, each with the page URL). '
          'Era: the owner\'s New Jedi Order to Legacy window (25 to about 140 ABY); anything that did not exist or was not available then is marked. '
          'Planets: ours (Hoth, Ossus), the census candidates, stock SWG planets, or none of ours. '
          'Classes and consumer counts come from `inventory.json` (R3 part 3): a new **leaf** under a stock class is accepted on day one by every schematic '
          'that names the class or an ancestor; a new **class** has no consumer until a recipe names it. Floors and ceilings are by the R3 part-2 rule '
          '(clone of the strongest stock leaf of the class; OQ minimum 500; other minimums rounded up to the next 50 unless that reaches the maximum) '
          'or by a stated variant on a named base row. Attribute keys: DR decay, OQ quality, CR cold, HR heat, MA malleability, UT toughness, SR shock, CD conductivity, FL flavor, PE potential energy, ER entangle.', '',
          'Already in the stock tree (galaxy-wide random pool; **not duplicated**): ' + ', '.join(f'`{e}` ({why})' for e, why in STOCK_LORE_LEAVES) + '.', '',
          '## 1. Summary', '',
          '| Material | Planet(s) | Era (25-140 ABY) | Stock class -> proposal | Floors-ceilings | Pool / rarity | Recipes taking the class | Staged |',
          '|---|---|---|---|---|---|---|---|']
    for m in records:
        p = m['proposal']
        prop = f'`{p["cls"]}` -> `{p["enum"]}` "{p["text"]}" ({p["kind"]})' if p['kind'] not in ('none',) else p['kind']
        L.append(f'| {m["name"]} | {m["planets"]} [{m["planet_state"]}] | {m["era"]} | {prop} | {floors_text(p["attrs"])} | {p["pool"]} | {p["consumers"] or "-"} | {"yes" if p["staged"] else "no"} |')
    L += ['', '## 2. Each material', '']
    for m in records:
        p = m['proposal']
        L += [f'### {m["name"]}', '', f'{m["text"]}', '',
              f'- Planets: {m["planets"]} ({m["planet_state"]}). Continuity: {m["continuity"]}. Era: {m["era"]} Canon note: {m["canon"]}',
              f'- Sources: ' + ', '.join(f'<{s}>' for s in m['sources']),
              f'- Stock: {m["stock"]}',
              f'- Proposal: {p["kind"]}; class `{p["cls"]}`, leaf `{p["enum"]}` "{p["text"]}"; rule {p["rule"]}' + (f' (base `{p["base"]}`)' if p['base'] else '') + f'; {p["pool"]}.',
              f'- Floors-ceilings: {floors_text(p["attrs"])}',
              f'- Consumers: {p["consumers"] or "-"} schematics take `{p["cls"]}`' + (f' (e.g. {", ".join(p["consumer_examples"])})' if p['consumer_examples'] else '') + '.',
              f'- Note: {p["option"]}', '']
    L += ['## 3. The cheapest batch, staged (planets we have)', '',
          'Two leaves, both zone-restricted by their enum (`_ossus`, `_hoth`), staged by `stage_lore_materials.stage_lore_materials(stage_dir, base)` as the last step of the chain '
          '(Hoth build > stage_ossus > stage_species chiss > stage_ossus_minerals > lore). Pool lines: `patch/core3-c29-lore-pools.patch` (minimum pool 1 each, after the R3 part-2 Ossus block). '
          'Nothing is staged for planets we do not have; those rows above are proposals.', '']
    if checks:
        rt = checks['resource_tree']
        L += [f'- Archive `{checks["archive"]}` sha256 {checks["sha256"]} ({checks["bytes"]:,} B, {checks["entries"]} entries), built on the part-2 archive '
              f'({checks["reference"]["file"]}, sha256 verified: {checks["reference"]["sha256_ok"]}).',
              f'- Against part 2: changed {checks["against_part2"]["changed"]}, new entries {checks["against_part2"]["new_entries"]}, Chiss entries identical: {checks["against_part2"]["chiss_entries_identical"]}.',
              f'- Resource tree: {rt["rows_before"]} -> {rt["rows_after"]} rows; added {rt["added"]}; ancestors bumped {rt["ancestor_counts_bumped"]}; other cell changes {rt["other_cell_changes"]}; '
              f'stock order kept {rt["stock_order_kept"]}; idempotent {rt["idempotent"]}; all checks ok: {checks["ok"]}.']
        for d in rt['added_detail']:
            L.append(f'  - `{d["enum"]}` "{d["text"]}" after `{d["after"]}`, cloned from `{d["cloned_from"]}`, rule {d["rule"]}, pools {d["pools"]}, types {d["types"]}: '
                     + ' '.join(f'{short_attr(a)} {lo}-{hi}' for a, lo, hi in d['attrs']))
    L += ['', '## 4. Open points', '',
          '1. Adegan naming: keep the two generic Ossus gems and add the Adegan leaf (staged), or rename Type 1/2 to Kathracite/Pontite as well (text only, new spawns only).',
          '2. Lumni-spice needs a recipe to mean anything beyond a top-grade chef fungus: a Smuggler "Lumni-spice" schematic taking the fungus is the natural consumer.',
          '3. Beskar floors are a stated variant (best iron in the game, one spawn at a time); the owner may prefer the part-2 rule for parity with the planet minerals.',
          '4. Corusca gems on Yavin 4 are a convenience; say so in the resource name or make them a GemDiver vendor item instead.',
          '5. Yorik coral is the one era-exclusive material (25 ABY onward) and the one that needs a new class or a loot route.',
          '6. Wookieepedia could not be fetched directly in this session (HTTP 402 from the fetch tool); the pages were read through search summaries, so each claim was kept to what several results agreed on and the URLs are given for a second look.', '']
    return chr(10).join(L)


def main():
    records = build()
    # the rule reproduces R3 part 2's Ossus gem numbers (proof that this script applies the same rule)
    gem = dict((a, (lo, hi)) for a, lo, hi in part2('gemstone_crystalline')[1])
    ossus1 = dict((a, (lo, hi)) for a, lo, hi in BY['crystalline_ossus_1']['attributes'])
    assert gem == ossus1, (gem, ossus1)
    checks_path = os.path.join(HERE, 'checks.json')
    checks = json.load(open(checks_path, encoding='utf-8')) if os.path.exists(checks_path) else None
    data = {'built': '2026-10-14', 'era': 'NJO to Legacy (25 to about 140 ABY)', 'rule_check': 'part-2 rule on gemstone_crystalline reproduces crystalline_ossus_1',
            'stock_lore_leaves': STOCK_LORE_LEAVES, 'materials': records, 'staged': checks['resource_tree']['added_detail'] if checks else None,
            'archive': {k: checks[k] for k in ('archive', 'sha256', 'bytes', 'ok')} if checks else None}
    with open(os.path.join(HERE, 'lore-materials.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, 'lore-materials.md'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(md(records, checks))
    print(len(records), 'materials;', sum(1 for r in records if r['proposal']['staged']), 'staged;', 'checks' if checks else 'no checks.json')
    for r in records:
        p = r['proposal']
        print(f'  {r["name"]:<34} {p["kind"]:<18} {p["cls"]:<22} {floors_text(p["attrs"])}')


if __name__ == '__main__':
    main()
