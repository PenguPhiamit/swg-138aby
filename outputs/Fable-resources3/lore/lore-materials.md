# C29: Legends materials for the resource plan (Fable, 14 October 2026)

Lore read on Wookieepedia, Legends continuity first (its text is CC BY-SA: these lines are ours, each with the page URL). Era: the owner's New Jedi Order to Legacy window (25 to about 140 ABY); anything that did not exist or was not available then is marked. Planets: ours (Hoth, Ossus), the census candidates, stock SWG planets, or none of ours. Classes and consumer counts come from `inventory.json` (R3 part 3): a new **leaf** under a stock class is accepted on day one by every schematic that names the class or an ancestor; a new **class** has no consumer until a recipe names it. Floors and ceilings are by the R3 part-2 rule (clone of the strongest stock leaf of the class; OQ minimum 500; other minimums rounded up to the next 50 unless that reaches the maximum) or by a stated variant on a named base row. Attribute keys: DR decay, OQ quality, CR cold, HR heat, MA malleability, UT toughness, SR shock, CD conductivity, FL flavor, PE potential energy, ER entangle.

Already in the stock tree (galaxy-wide random pool; **not duplicated**): `ore_siliclastic_cortosis` (cortosis (Legends worlds above)), `aluminum_phrik` (phrik (Gromas 16)), `iron_doonium` (doonium), `iron_dolovite` (dolovite (named for Mustafar)), `iron_bronzium` (bronzium (named for Mustafar)), `steel_duralloy` (duralloy), `ore_carbonate_lommite` (lommite), `armophous_baradium` (baradium), `armophous_ryll` (ryll), `steel_carbonite` (carbonite), `aluminum_titanium` (titanium), `aluminum_chromium` (chromium).

## 1. Summary

| Material | Planet(s) | Era (25-140 ABY) | Stock class -> proposal | Floors-ceilings | Pool / rarity | Recipes taking the class | Staged |
|---|---|---|---|---|---|---|---|
| Adegan crystal | Ossus (Adega system) [ours] | Known through all eras; Ossus hosted the Jedi Academy after the Vong war until the Sith raid of 130 ABY, so the crystals are in the window. | `gemstone_crystalline` -> `crystalline_adegan_ossus` "Adegan Crystal Crystalline Gemstone" (leaf) | DR 850-1000 OQ 500-1000 CR 850-1000 HR 951-1000 MA 350-400 UT 900-1000 SR 900-1000 ER 950-1000 | minimum pool 1 on Ossus, types 1/2; the random gemstone pool may add a second spawn, Ossus only | 168 | yes |
| Lumni-spice (lumni lichen) | Hoth (also Corulag) [ours] | Ancient stories (Raskar before Echo Base, the 27 BBY mine); nothing says it ran out, so it is in the window. | `vegetable_fungi` -> `vegetable_fungi_lumni_hoth` "Lumni Lichen Fungus" (leaf) | DR 1-1000 OQ 500-1000 FL 700-1000 PE 500-1000 | minimum pool 1 on Hoth, types 1/1 (as natives); the native pool never picks it (it builds <class>_<planet> names) | 202 | yes |
| Hoth asteroid-field metals | Hoth system (the Anoat belt, meteorites on Hoth) [ours] | Mining documented at 12 ABY; the belt is still there in the window. | `iron` -> `iron_hoth` "Meteoric Iron (text only)" (text-option) | - | unchanged | 693 | no |
| Mandalorian iron (beskar) | Mandalore, its moon Concordia [candidate] | In the window: fresh lodes were exposed by the Yuuzhan Vong attack, and Mandalore prospered on them under Boba Fett around the Second Galactic Civil War (40 ABY). | `iron` -> `iron_beskar_mandalore` "Mandalorian Iron" (leaf) | DR 900-1000 OQ 500-1000 CR 700-800 HR 950-1000 MA 1-150 UT 950-1000 SR 950-1000 CD 1-150 | minimum pool 1 on Mandalore, max pool 1, types 1/1: one spawn at a time, never in the random pool (add it to randompoolexcludes) | 693 | no |
| Cortosis | Apatros, Bal'demnic, Duro, Katanos VII, Obredaan (none of ours) [other] | In the window (Imperial Knights, Legacy comics). | `ore_siliclastic` -> `ore_siliclastic_cortosis` "Cortosis Siliclastic Ore" (stock-already) | - | stock | 311 | no |
| Phrik | Gromas 16 (not ours) [other] | In the window as an alloy; the mine's later history is not given. | `aluminum` -> `aluminum_phrik` "Phrik Aluminum" (stock-already) | - | stock | 821 | no |
| Songsteel | Cularin asteroid belt (not ours) [other] | Appearances are Rise of the Empire era; nothing says it is gone. | `steel` -> `steel_songsteel` "Songsteel" (leaf) | DR 950-1000 OQ 500-1000 CR 700-800 HR 950-1000 MA 350-400 UT 950-1000 SR 950-1000 CD 600-650 | no planet of ours: galaxy-wide random pool only, low weight (a rarity between the stock steels), or skip | 984 | no |
| Corusca gem | Yavin Prime's atmosphere (Yavin 4 is its moon; stock planet) [stock] | GemDiver Station (23 ABY) puts the mining right at the start of the window; Corusca crystals armed New Jedi Order lightsabers. | `gemstone_crystalline` -> `crystalline_corusca_yavin4` "Corusca Gem Crystalline Gemstone" (leaf) | DR 850-1000 OQ 500-1000 CR 850-1000 HR 951-1000 MA 350-400 UT 900-1000 SR 900-1000 ER 950-1000 | minimum pool 1 on Yavin 4, types 1/2 | 168 | no |
| Mirkanite | Mustafar [candidate] | Imperial-era mining is documented; no source for 25+ ABY, so mark the mine's state an open question. | `ore_extrusive` -> `ore_extrusive_mirkanite_mustafar` "Mirkanite Extrusive Ore" (leaf) | DR 950-1000 OQ 500-1000 CR 900-1000 HR 950-1000 MA 550-600 UT 950-1000 SR 950-1000 | minimum pool 1 on Mustafar, types 1/2 | 308 | no |
| Wroshyr wood | Kashyyyk [candidate] | Kashyyyk stood through the Vong war; the trees are in the window. | `wood_deciduous` -> `wood_deciduous_wroshyr_kashyyyk` "Wroshyr Hard Wood" (leaf) | DR 400-800 OQ 500-1000 MA 600-800 UT 600-800 SR 500-700 | minimum pool 1 on Kashyyyk, types 1/1 | 113 | no |
| Yorik coral | Coruscant (Yuuzhan'tar) and other Vongformed worlds, Nal Hutta among them [candidate] | ERA-SPECIFIC: did not exist in the galaxy before 25 ABY; remnants fit the whole window (Krayt still used yorik-kul seeds in 137 ABY). | `creature_structural` -> `-` "Yorik Coral" (new-class or loot) | - | harvest node or loot from Vong remnants rather than a survey resource | 77 | no |
| Dromund Kaas flora | Dromund Kaas [candidate] | Prophets of the Dark Side era documented; nothing for the window. | `vegetable_fungi` -> `vegetable_fungi_kaas` "Lumikurnizi Fungus (text only)" (text-option) | - | unchanged | 202 | no |
| Chandrilan foods (muja, jaquira) | Chandrila [candidate] | Agriworld through the window. | `fruit_fruits` -> `fruit_fruits_muja_chandrila` "Muja Fruit" (leaf) | DR 1-1000 OQ 500-1000 FL 600-1000 PE 1-1000 | minimum pool 1 on Chandrila, types 1/1; a second leaf "Jaquira Fruit" the same way | 199 | no |
| Taanab livestock (roba, staga) | Taanab [candidate] | Agriworld through the window. | `meat_domesticated` -> `meat_domesticated_taanab` "Roba Meat (text only)" (creature-text) | - | unchanged | 178 | no |
| Nal Hutta swamp chemicals | Nal Hutta [candidate] | Vongformed in the war (the page lists Vongformed terrain), so the window has both swamp and coral. | `petrochem_inert` -> `-` "Hutta Swamp Distillate (class to choose with the planet)" (rule) | - | design rule: no metal in Nal Hutta's pools (no heavy metals); a chemical/petrochem leaf as its one signature material | 397 | no |
| Korriban | Korriban (zone moraband) [candidate] | Sith ground in every era; the Legacy comics (130-139 ABY) have Krayt's One Sith, and the page gives no mining history for the window. | none | - | - | - | no |
| Coruscant | Coruscant [candidate] | - | none | - | - | - | no |
| Kaiburr / kyber crystal | Mimban (Legends relic); everywhere (canon kyber) [other] | n/a | none | - | - | - | no |
| Durasteel | manufactured [other] | - | none | - | - | 984 | no |

## 2. Each material

### Adegan crystal

The Jedi's lightsaber crystals of the Old Republic came from the Adega system, and the first were found on Ossus. Five grades are named, kathracite the common training crystal and pontite the rarest; Ossus's Crystal Caves kept the Ysanna alive after the Cron supernova.

- Planets: Ossus (Adega system) (ours). Continuity: Legends. Era: Known through all eras; Ossus hosted the Jedi Academy after the Vong war until the Sith raid of 130 ABY, so the crystals are in the window. Canon note: Canon folds Adegan crystals into kyber and puts pontite in Ossus's caverns; Legends has no kyber.
- Sources: <https://starwars.fandom.com/wiki/Adegan_crystal/Legends>, <https://starwars.fandom.com/wiki/Ossus/Legends>, <https://starwars.fandom.com/wiki/Adega_system>
- Stock: not in the tree (the Ossus Type 1/2 gems are generic names)
- Proposal: leaf; class `gemstone_crystalline`, leaf `crystalline_adegan_ossus` "Adegan Crystal Crystalline Gemstone"; rule part-2 (base `crystalline_vertex`); minimum pool 1 on Ossus, types 1/2; the random gemstone pool may add a second spawn, Ossus only.
- Floors-ceilings: DR 850-1000 OQ 500-1000 CR 850-1000 HR 951-1000 MA 350-400 UT 900-1000 SR 900-1000 ER 950-1000
- Consumers: 168 schematics take `gemstone_crystalline` (e.g. armor/component/armor_layer_acid.lua, armor/component/deflector_shield_emitter_assembly.lua, armor/shield_generator_personal.lua).
- Note: Cheaper still: rename crystalline_ossus_1/2 to Kathracite / Pontite (text only; new spawns only). Not done, it changes names already in play.

### Lumni-spice (lumni lichen)

Lumni lichen is a scarce fungus that grows on a few worlds, Hoth among them, in a sunless fissure near the equator; it is the source of lumni-spice, called the rarest spice in the galaxy, and dragon slugs grow huge on it. Pirates and a Shi'ido changeling's wampa-run mine have gone after it.

- Planets: Hoth (also Corulag) (ours). Continuity: Legends. Era: Ancient stories (Raskar before Echo Base, the 27 BBY mine); nothing says it ran out, so it is in the window. Canon note: Legends only.
- Sources: <https://starwars.fandom.com/wiki/Lumni-spice>, <https://starwars.fandom.com/wiki/Lumni_lichen>, <https://starwars.fandom.com/wiki/Hoth/Legends>
- Stock: not in the tree; Hoth has the generic vegetable_fungi_hoth native
- Proposal: leaf; class `vegetable_fungi`, leaf `vegetable_fungi_lumni_hoth` "Lumni Lichen Fungus"; rule variant (base `vegetable_fungi_hoth`); minimum pool 1 on Hoth, types 1/1 (as natives); the native pool never picks it (it builds <class>_<planet> names).
- Floors-ceilings: DR 1-1000 OQ 500-1000 FL 700-1000 PE 500-1000
- Consumers: 202 schematics take `vegetable_fungi` (e.g. bio_engineer/bio_component/bio_component_clothing_field_bleeding.lua, bio_engineer/bio_component/bio_component_clothing_field_bleeding_2.lua, bio_engineer/bio_component/bio_component_clothing_field_defense_2.lua).
- Note: A Smuggler schematic "Lumni-spice" taking this fungus would make the spice itself; the pre-CU spice line has no fungus input today.

### Hoth asteroid-field metals

The belt beyond Hoth formed from two shattered planets and holds nickel-iron ore, a rumoured platinum body (Kerane's Folly) and silicon crystal ferns; pieces fall on Hoth as meteorites, and the Hutts' Orko SkyMine dug it for the Darksaber in 12 ABY.

- Planets: Hoth system (the Anoat belt, meteorites on Hoth) (ours). Continuity: Legends. Era: Mining documented at 12 ABY; the belt is still there in the window. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Hoth_asteroid_field/Legends>, <https://starwars.fandom.com/wiki/Hoth/Legends>
- Stock: iron_hoth (Kammris clone) already covers Hoth's iron
- Proposal: text-option; class `iron`, leaf `iron_hoth` "Meteoric Iron (text only)"; rule keep iron_hoth's floors; unchanged.
- Floors-ceilings: -
- Consumers: 693 schematics take `iron` (e.g. armor/armor_segment_bone.lua, armor/armor_segment_chitin.lua, armor/armor_segment_composite.lua).
- Note: Space-only ore belongs to JTL mining if that ever comes; on the ground a rename of iron_hoth's class text is the whole cost (new spawns only).

### Mandalorian iron (beskar)

Beskar comes only from Mandalore and Concordia. Forged with carbon it is light for its toughness and shrugs off lightsabers, which is why it outranks durasteel and cortosis; the Empire strip-mined it with slave labour and the Death Watch kept digging in secret.

- Planets: Mandalore, its moon Concordia (candidate). Continuity: Legends. Era: In the window: fresh lodes were exposed by the Yuuzhan Vong attack, and Mandalore prospered on them under Boba Fett around the Second Galactic Civil War (40 ABY). Canon note: Canon also calls it Mandalorian steel and an alloy; same worlds.
- Sources: <https://starwars.fandom.com/wiki/Beskar/Legends>, <https://starwars.fandom.com/wiki/Mandalore/Legends>, <https://starwars.fandom.com/wiki/Concordia/Legends>
- Stock: not in the tree
- Proposal: leaf; class `iron`, leaf `iron_beskar_mandalore` "Mandalorian Iron"; rule variant (base `iron_hoth`); minimum pool 1 on Mandalore, max pool 1, types 1/1: one spawn at a time, never in the random pool (add it to randompoolexcludes).
- Floors-ceilings: DR 900-1000 OQ 500-1000 CR 700-800 HR 950-1000 MA 1-150 UT 950-1000 SR 950-1000 CD 1-150
- Consumers: 693 schematics take `iron` (e.g. armor/armor_segment_bone.lua, armor/armor_segment_chitin.lua, armor/armor_segment_composite.lua).
- Note: Under iron, every armour and weapon recipe that takes iron, ferrous metal or metal (693) can use it; the stated floors make it the best iron in the game. A steel leaf would reach 984 recipes but the name says iron.

### Cortosis

An ore whose conductive quirk shorts out a lightsaber on contact; too brittle for plain armour, so it is woven in, and refined cortosis-shield is the prized form (Roan Fel's Imperial Knights use it).

- Planets: Apatros, Bal'demnic, Duro, Katanos VII, Obredaan (none of ours) (other). Continuity: Legends. Era: In the window (Imperial Knights, Legacy comics). Canon note: Canon lists other worlds (Dinzo, Mokivj).
- Sources: <https://starwars.fandom.com/wiki/Cortosis/Legends>
- Stock: ALREADY STOCK: ore_siliclastic_cortosis "Cortosis Siliclastic Ore", galaxy-wide random pool
- Proposal: stock-already; class `ore_siliclastic`, leaf `ore_siliclastic_cortosis` "Cortosis Siliclastic Ore"; rule stock; stock.
- Floors-ceilings: -
- Consumers: 311 schematics take `ore_siliclastic` (e.g. armor/component/armor_layer_electrical.lua, armor/component/armor_layer_energy.lua, armor/component/deflector_shield_emitter_assembly.lua).
- Note: Do not duplicate. A planet-locked rich variant could follow a cortosis world if one is ever added.

### Phrik

A light, nearly indestructible alloy made from phrikite ore of the moon Gromas 16 and tydirium; it resists lightsabers and went into MagnaGuard electrostaffs and Dark Trooper armour, at a price that kept it rare.

- Planets: Gromas 16 (not ours) (other). Continuity: Legends. Era: In the window as an alloy; the mine's later history is not given. Canon note: Canon adds Tatooine as a source.
- Sources: <https://starwars.fandom.com/wiki/Phrik/Legends>, <https://starwars.fandom.com/wiki/Phrikite>
- Stock: ALREADY STOCK: aluminum_phrik "Phrik Aluminum", galaxy-wide random pool
- Proposal: stock-already; class `aluminum`, leaf `aluminum_phrik` "Phrik Aluminum"; rule stock; stock.
- Floors-ceilings: -
- Consumers: 821 schematics take `aluminum` (e.g. armor/armor_segment.lua, armor/armor_segment_bone.lua, armor/armor_segment_composite.lua).
- Note: Do not duplicate.

### Songsteel

A rare metal found in the Cularin belt during the Confederation Rock Rush; it turns lightsabers much as phrik and cortosis do without shorting them, and only exquisite, costly weapons were made of it.

- Planets: Cularin asteroid belt (not ours) (other). Continuity: Legends. Era: Appearances are Rise of the Empire era; nothing says it is gone. Canon note: Legends only.
- Sources: <https://starwars.fandom.com/wiki/Songsteel/Legends>
- Stock: not in the tree
- Proposal: leaf; class `steel`, leaf `steel_songsteel` "Songsteel"; rule part-2 (base `steel_duralloy`); no planet of ours: galaxy-wide random pool only, low weight (a rarity between the stock steels), or skip.
- Floors-ceilings: DR 950-1000 OQ 500-1000 CR 700-800 HR 950-1000 MA 350-400 UT 950-1000 SR 950-1000 CD 600-650
- Consumers: 984 schematics take `steel` (e.g. armor/armor_segment_bone.lua, armor/armor_segment_chitin.lua, armor/armor_segment_composite.lua).
- Note: 984 steel recipes would take it; without a planet story it is just another top steel, so it is listed, not recommended.

### Corusca gem

Gems formed by the pressure of Yavin's gas-giant depths, fished from the upper layers or mined deep by Lando's GemDiver Station from 23 ABY; prized, lightsaber-capable, and brittle at their shatterpoints.

- Planets: Yavin Prime's atmosphere (Yavin 4 is its moon; stock planet) (stock). Continuity: Legends. Era: GemDiver Station (23 ABY) puts the mining right at the start of the window; Corusca crystals armed New Jedi Order lightsabers. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Corusca_gem/Legends>, <https://starwars.fandom.com/wiki/Yavin_Prime/Legends>, <https://starwars.fandom.com/wiki/GemDiver_Station>
- Stock: not in the tree
- Proposal: leaf; class `gemstone_crystalline`, leaf `crystalline_corusca_yavin4` "Corusca Gem Crystalline Gemstone"; rule part-2 (base `crystalline_vertex`); minimum pool 1 on Yavin 4, types 1/2.
- Floors-ceilings: DR 850-1000 OQ 500-1000 CR 850-1000 HR 951-1000 MA 350-400 UT 900-1000 SR 900-1000 ER 950-1000
- Consumers: 168 schematics take `gemstone_crystalline` (e.g. armor/component/armor_layer_acid.lua, armor/component/deflector_shield_emitter_assembly.lua, armor/shield_generator_personal.lua).
- Note: A stretch: the gems come from the gas giant, not the moon. Surveying them on Yavin 4 is a game convenience; the honest alternative is a GemDiver vendor or loot item.

### Mirkanite

A rare allotrope in Mustafar's crust and lava, melting low enough that the lava can be skimmed at about 800 C; the Techno Union and then the Empire mined it, and it went into the first Death Star's superlaser.

- Planets: Mustafar (candidate). Continuity: Legends. Era: Imperial-era mining is documented; no source for 25+ ABY, so mark the mine's state an open question. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Mirkanite/Legends>, <https://starwars.fandom.com/wiki/Mustafar/Legends>
- Stock: not in the tree; Mustafar's other named ores dolovite and bronzium are stock iron leaves (iron_dolovite, iron_bronzium, galaxy-wide)
- Proposal: leaf; class `ore_extrusive`, leaf `ore_extrusive_mirkanite_mustafar` "Mirkanite Extrusive Ore"; rule part-2 (base `ore_extrusive_vintrium`); minimum pool 1 on Mustafar, types 1/2.
- Floors-ceilings: DR 950-1000 OQ 500-1000 CR 900-1000 HR 950-1000 MA 550-600 UT 950-1000 SR 950-1000
- Consumers: 308 schematics take `ore_extrusive` (e.g. armor/component/armor_layer_energy.lua, armor/component/deflector_shield_emitter_assembly.lua, armor/component/deflector_shield_generator_energy_ray.lua).
- Note: 308 recipes take extrusive ore (armour layers, shield emitters). The lore-true variant would lower its heat-resistance ceiling (it melts low) and raise quality (superlaser grade).

### Wroshyr wood

Timber of the kilometre-tall wroshyr trees: strong and flexible enough for starship hulls under shields, exported as costly flooring, and worked into Wookiee weapons, furniture and homes.

- Planets: Kashyyyk (candidate). Continuity: Legends. Era: Kashyyyk stood through the Vong war; the trees are in the window. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Wroshyr_wood/Legends>, <https://starwars.fandom.com/wiki/Wroshyr_tree/Legends>
- Stock: not in the tree (natives would be wood_deciduous_kashyyyk)
- Proposal: leaf; class `wood_deciduous`, leaf `wood_deciduous_wroshyr_kashyyyk` "Wroshyr Hard Wood"; rule variant (base `wood_deciduous_hoth`); minimum pool 1 on Kashyyyk, types 1/1.
- Floors-ceilings: DR 400-800 OQ 500-1000 MA 600-800 UT 600-800 SR 500-700
- Consumers: 113 schematics take `wood_deciduous` (e.g. armor/armor_segment_kashyyykian_black_mtn.lua, armor/armor_segment_kashyyykian_ceremonial.lua, bio_engineer/bio_component/bio_component_clothing_casual_entertainer.lua).
- Note: 113 recipes take hard wood, including the Kashyyykian armour segments already in the schematic set.

### Yorik coral

The Yuuzhan Vong's grown shipbuilding stuff, hard enough to armour the Senate Building; after the war it kept growing in Coruscant's undercity and was even used as park decoration, and Vongformed remnants were still on the planet in 40 ABY.

- Planets: Coruscant (Yuuzhan'tar) and other Vongformed worlds, Nal Hutta among them (candidate). Continuity: Legends. Era: ERA-SPECIFIC: did not exist in the galaxy before 25 ABY; remnants fit the whole window (Krayt still used yorik-kul seeds in 137 ABY). Canon note: Legends only.
- Sources: <https://starwars.fandom.com/wiki/Yorik_coral>, <https://starwars.fandom.com/wiki/World_Brain>
- Stock: no stock class fits (grown biotech, not mined or farmed)
- Proposal: new-class or loot; class `creature_structural`, leaf `-` "Yorik Coral"; rule n/a; harvest node or loot from Vong remnants rather than a survey resource.
- Floors-ceilings: -
- Consumers: 77 schematics take `creature_structural` (e.g. bio_engineer/bio_component/bio_component_clothing_field_bleeding.lua, bio_engineer/bio_component/bio_component_clothing_field_bleeding_2.lua, bio_engineer/bio_component/bio_component_food_heavy_nutrition.lua).
- Note: Cheapest honest route: a bone-class leaf would feed 132 recipes but reads wrong; better a loot component for an era quest line. Needs a container and strings either way.

### Dromund Kaas flora

A jungle, swamp and ocean world; the Legends page names its flora Amanita Lumikurnizi (a fungus), the dart flower and Monotropa Triflora, and gives no mined resource.

- Planets: Dromund Kaas (candidate). Continuity: Legends. Era: Prophets of the Dark Side era documented; nothing for the window. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Dromund_Kaas/Legends>
- Stock: MTG's 45 Kaas natives are in the tree (vegetable_fungi_kaas, fruit_flowers_kaas ...)
- Proposal: text-option; class `vegetable_fungi`, leaf `vegetable_fungi_kaas` "Lumikurnizi Fungus (text only)"; rule keep the native's floors; unchanged.
- Floors-ceilings: -
- Consumers: 202 schematics take `vegetable_fungi` (e.g. bio_engineer/bio_component/bio_component_clothing_field_bleeding.lua, bio_engineer/bio_component/bio_component_clothing_field_bleeding_2.lua, bio_engineer/bio_component/bio_component_clothing_field_defense_2.lua).
- Note: Lore names for the existing natives (fungus, flower) are free; a dark-side material would be our invention and is not proposed.

### Chandrilan foods (muja, jaquira)

A Core agriworld that cornered the market in perishable luxury food: grains, muja and jaquira fruit, vegetables, beans and spices, with squalls wandering its roads.

- Planets: Chandrila (candidate). Continuity: Legends. Era: Agriworld through the window. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Chandrila/Legends>
- Stock: not in the tree (natives would be fruit_fruits_chandrila ...)
- Proposal: leaf; class `fruit_fruits`, leaf `fruit_fruits_muja_chandrila` "Muja Fruit"; rule variant (base `fruit_fruits_hoth`); minimum pool 1 on Chandrila, types 1/1; a second leaf "Jaquira Fruit" the same way.
- Floors-ceilings: DR 1-1000 OQ 500-1000 FL 600-1000 PE 1-1000
- Consumers: 199 schematics take `fruit_fruits` (e.g. bio_engineer/bio_component/bio_component_clothing_field_bleeding.lua, bio_engineer/bio_component/bio_component_clothing_field_bleeding_2.lua, bio_engineer/bio_component/bio_component_clothing_field_defense_2.lua).
- Note: 199 chef and bio-engineer recipes take fruit; squall meat is a creature template question, not a tree row.

### Taanab livestock (roba, staga)

An Inner Rim farm world feeding the Mid and Outer Rim, known for roba steak; staga came from Ambria as a food animal when Taanab was settled.

- Planets: Taanab (candidate). Continuity: Legends. Era: Agriworld through the window. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Taanab/Legends>, <https://starwars.fandom.com/wiki/Roba/Legends>, <https://starwars.fandom.com/wiki/Staga/Legends>
- Stock: MTG's 45 Taanab natives are in the tree (meat_domesticated_taanab ...)
- Proposal: creature-text; class `meat_domesticated`, leaf `meat_domesticated_taanab` "Roba Meat (text only)"; rule keep the native's floors; unchanged.
- Floors-ceilings: -
- Consumers: 178 schematics take `meat_domesticated` (e.g. bio_engineer/bio_component/bio_component_clothing_casual_entertainer.lua, bio_engineer/bio_component/bio_component_clothing_casual_entertainer_2.lua, bio_engineer/bio_component/bio_component_clothing_casual_medic.lua).
- Note: Creature resources come from creature templates, not surveys: a roba creature yielding Taanab domesticated meat is the whole feature; naming the native "Roba Meat" is free.

### Nal Hutta swamp chemicals

A world without natural heavy metals, strip-mined and bulldozed into swamps whose polluted waters are filtered for valuable chemicals (the New Muckworks); spice is the Hutt commodity.

- Planets: Nal Hutta (candidate). Continuity: Legends. Era: Vongformed in the war (the page lists Vongformed terrain), so the window has both swamp and coral. Canon note: Legends page used.
- Sources: <https://starwars.fandom.com/wiki/Nal_Hutta/Legends>, <https://starwars.fandom.com/wiki/New_Muckworks>
- Stock: no match; natives would follow the stock pattern
- Proposal: rule; class `petrochem_inert`, leaf `-` "Hutta Swamp Distillate (class to choose with the planet)"; rule n/a; design rule: no metal in Nal Hutta's pools (no heavy metals); a chemical/petrochem leaf as its one signature material.
- Floors-ceilings: -
- Consumers: 397 schematics take `petrochem_inert` (e.g. armor/armor_segment.lua, bio_engineer/utilities/pet_stimpack_a.lua, bio_engineer/utilities/pet_vitapack_a.lua).
- Note: 397 recipes take inert petrochemicals; which subclass (polymer, lubricating oil) is a planet-design choice.

### Korriban

Red sands, tombs and the Valley of the Dark Lords; the page lists generic exports (raw material, weapons, artifacts) and no named mineral, and Sith lightsaber crystals are synthetic, not mined.

- Planets: Korriban (zone moraband) (candidate). Continuity: Legends. Era: Sith ground in every era; the Legacy comics (130-139 ABY) have Krayt's One Sith, and the page gives no mining history for the window. Canon note: Canon calls it Moraband (our zone key).
- Sources: <https://starwars.fandom.com/wiki/Korriban/Legends>, <https://starwars.fandom.com/wiki/Sith_lightsaber/Legends>
- Stock: -
- Proposal: none; class `-`, leaf `-` "-"; rule n/a; -.
- Floors-ceilings: -
- Consumers: - schematics take `-`.
- Note: Nothing Legends-backed to add; a "Korriban sandstone" would be our invention. Standard natives only.

### Coruscant

An ecumenopolis with no natural raw materials of its own; the Vong war left yorik coral and Vongformed ground (see Yorik coral).

- Planets: Coruscant (candidate). Continuity: Legends. Era: - Canon note: -
- Sources: <https://starwars.fandom.com/wiki/Yorik_coral>
- Stock: -
- Proposal: none; class `-`, leaf `-` "-"; rule n/a; -.
- Floors-ceilings: -
- Consumers: - schematics take `-`.
- Note: Standard natives make little sense for a city planet; yorik coral is the era hook.

### Kaiburr / kyber crystal

In Legends the Kaiburr crystal is one unique Force-amplifying relic in the Temple of Pomojema on Mimban, powerless off-world; the galaxy-wide "kyber crystal" that grows on many planets is canon.

- Planets: Mimban (Legends relic); everywhere (canon kyber) (other). Continuity: canon-only as a resource. Era: n/a Canon note: CANON-ONLY as a mineable material.
- Sources: <https://starwars.fandom.com/wiki/Kaiburr_crystal>, <https://starwars.fandom.com/wiki/Kyber_crystal>
- Stock: -
- Proposal: none; class `-`, leaf `-` "-"; rule n/a; -.
- Floors-ceilings: -
- Consumers: - schematics take `-`.
- Note: Not a resource in Legends; the Adegan crystal is the Legends equivalent.

### Durasteel

The galaxy's everyday structural alloy; it is made, not mined.

- Planets: manufactured (other). Continuity: Legends. Era: - Canon note: -
- Sources: <https://starwars.fandom.com/wiki/Durasteel/Legends>
- Stock: the stock tree already has Duralloy Steel (steel_duralloy) as its top steel
- Proposal: none; class `steel`, leaf `steel_duralloy` "-"; rule n/a; -.
- Floors-ceilings: -
- Consumers: 984 schematics take `steel` (e.g. armor/armor_segment_bone.lua, armor/armor_segment_chitin.lua, armor/armor_segment_composite.lua).
- Note: No leaf: an alloy is a crafted product.

## 3. The cheapest batch, staged (planets we have)

Two leaves, both zone-restricted by their enum (`_ossus`, `_hoth`), staged by `stage_lore_materials.stage_lore_materials(stage_dir, base)` as the last step of the chain (Hoth build > stage_ossus > stage_species chiss > stage_ossus_minerals > lore). Pool lines: `patch/core3-c29-lore-pools.patch` (minimum pool 1 each, after the R3 part-2 Ossus block). Nothing is staged for planets we do not have; those rows above are proposals.

- Archive `local_planets-lore.tre` sha256 fbf62971bbbf2b65e613c7972e2a65ea78b98740d0fa39e26e1613beb97d95b1 (3,785,357 B, 55 entries), built on the part-2 archive (local_planets-part2.tre, sha256 verified: True).
- Against part 2: changed ['datatables/resource/resource_tree.iff'], new entries [], Chiss entries identical: True.
- Resource tree: 843 -> 845 rows; added ['vegetable_fungi_lumni_hoth', 'crystalline_adegan_ossus']; ancestors bumped ['resource', 'organic', 'flora_resources', 'flora_food', 'seeds', 'vegetable', 'vegetable_fungi', 'inorganic', 'mineral', 'gemstone', 'gemstone_crystalline']; other cell changes []; stock order kept True; idempotent True; all checks ok: True.
  - `crystalline_adegan_ossus` "Adegan Crystal Crystalline Gemstone" after `crystalline_ossus_2`, cloned from `crystalline_vertex`, rule part-2, pools [1, 1], types [1, 2]: DR 850-1000 OQ 500-1000 CR 850-1000 HR 951-1000 MA 350-400 UT 900-1000 SR 900-1000 ER 950-1000
  - `vegetable_fungi_lumni_hoth` "Lumni Lichen Fungus" after `vegetable_fungi_hoth`, cloned from `vegetable_fungi_hoth`, rule variant {'res_quality': 500, 'res_flavor': 700, 'res_potential_energy': 500}, pools [1, 1], types [1, 1]: DR 1-1000 OQ 500-1000 FL 700-1000 PE 500-1000

## 4. Open points

1. Adegan naming: keep the two generic Ossus gems and add the Adegan leaf (staged), or rename Type 1/2 to Kathracite/Pontite as well (text only, new spawns only).
2. Lumni-spice needs a recipe to mean anything beyond a top-grade chef fungus: a Smuggler "Lumni-spice" schematic taking the fungus is the natural consumer.
3. Beskar floors are a stated variant (best iron in the game, one spawn at a time); the owner may prefer the part-2 rule for parity with the planet minerals.
4. Corusca gems on Yavin 4 are a convenience; say so in the resource name or make them a GemDiver vendor item instead.
5. Yorik coral is the one era-exclusive material (25 ABY onward) and the one that needs a new class or a loot route.
6. Wookieepedia could not be fetched directly in this session (HTTP 402 from the fetch tool); the pages were read through search summaries, so each claim was kept to what several results agreed on and the URLs are given for a second look.
