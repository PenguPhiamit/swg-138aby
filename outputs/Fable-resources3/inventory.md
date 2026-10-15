# Resource inventory (R3 part 3) — Fable, 14 Oct 2026

Every resource row we may use, with its class path, attributes, planet restriction, the pool that spawns it today, its
planet coverage under `poolScaleZones = 10` with 12 active zones, and the schematics that would take it. Rows: `inventory.json`.
Sources: the stock tree (725 rows), MTG's tree (890 rows, 165 beyond stock), our test-session tree (843 rows: stock + Hoth 59 + Ossus 59),
the owner's book (48 mats for the ten stock planets; reference for new mats only). Excluded: SWG-Source, the Legends leak, Zeltros (on hold).
Pools from `resource_manager.lua` as patched by parts 1–2. Consumers from the 1746 Core3 draft schematics that name resource classes (231 distinct class tokens).

## 1. What we have, by source

| source | rows |
|---|---|
| hoth clone (R3 part 1) | 3 |
| hoth clone (builder) | 2 |
| mtg_hoth | 50 |
| mtg_hoth (R3 part 1) | 4 |
| ossus (O2c) | 45 |
| ossus (R3 part 2) | 14 |
| stock | 725 |
| mtg (not merged: Dromund Kaas 45, Taanab 45, space 18, energy class rows 3) | 111 |
| owner book mats (10 planets): exists 20, nearest existing class 6, new class 12, not a resource 10 | 48 |

## 2. Leaf types by class (our tree, 744 leaves)

| class (third level) | leaves | spawned by some pool | never spawned | galaxy-wide | planet-restricted | schematics taking the class (min–max over its leaves) |
|---|---|---|---|---|---|---|
| Chemical | 26 | 26 | 0 | 12 | 14 | 190–570 |
| Creature Resources | 246 | 246 | 0 | 6 | 240 | 77–344 |
| Flora Resources | 220 | 220 | 0 | 4 | 216 | 112–204 |
| Gas | 27 | 27 | 0 | 25 | 2 | 96–164 |
| Mineral | 147 | 147 | 0 | 123 | 24 | 119–991 |
| Renewable energy | 65 | 32 | 33 | 5 | 60 | 0–1 |
| Water | 13 | 13 | 0 | 1 | 12 | 71–72 |

Never spawned today (33 leaves, the 31 recycler outputs such as processed_meat left out): energy_renewable_site_limited_tidal_corellia, energy_renewable_site_limited_tidal_dathomir, energy_renewable_site_limited_tidal_dantooine, energy_renewable_site_limited_tidal_ossus, energy_renewable_site_limited_tidal_endor, energy_renewable_site_limited_tidal_lok, energy_renewable_site_limited_tidal_naboo, energy_renewable_site_limited_tidal_rori, energy_renewable_site_limited_tidal_talus, energy_renewable_site_limited_tidal_tatooine, energy_renewable_site_limited_tidal_yavin4, energy_renewable_site_limited_hydron3_corellia, energy_renewable_site_limited_hydron3_dantooine, energy_renewable_site_limited_hydron3_ossus, energy_renewable_site_limited_hydron3_dathomir, energy_renewable_site_limited_hydron3_endor, energy_renewable_site_limited_hydron3_lok, energy_renewable_site_limited_hydron3_naboo, energy_renewable_site_limited_hydron3_rori, energy_renewable_site_limited_hydron3_talus, energy_renewable_site_limited_hydron3_tatooine, energy_renewable_site_limited_hydron3_yavin4, energy_renewable_site_limited_geothermal_corellia, energy_renewable_site_limited_geothermal_dantooine, energy_renewable_site_limited_geothermal_ossus, energy_renewable_site_limited_geothermal_dathomir, energy_renewable_site_limited_geothermal_endor, energy_renewable_site_limited_geothermal_lok, energy_renewable_site_limited_geothermal_naboo, energy_renewable_site_limited_geothermal_rori, energy_renewable_site_limited_geothermal_talus, energy_renewable_site_limited_geothermal_tatooine, energy_renewable_site_limited_geothermal_yavin4.

## 3. Planet coverage under the scaling

Galaxy-wide leaf: Minimum/Maximum # Pools × 12/10, capped at 12 (8/8 → 10/10; 1/3 → 1/4; 1/1 → 1/1). Native and planet-restricted
types: one planet. Per-leaf values are in the JSON (`coverage`). The random pool keeps 27 spawns and the minimum pool one per entry,
so scaling widens where each spawn lives, not how many there are.

## 4. The site-limited energies (owner question: nativepoolincludes galaxy-wide?)

| planet | geothermal | tidal | hydron-3 |
|---|---|---|---|
| corellia | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| dantooine | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| dathomir | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| endor | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| lok | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| naboo | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| rori | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| talus | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| tatooine | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| yavin4 | in tree, never spawned | in tree, never spawned | in tree, never spawned |
| hoth | spawned: minimum x1 (own entry) | spawned: minimum x1 (own entry) | spawned: minimum x1 (own entry) |
| ossus | in tree, never spawned | in tree, never spawned | in tree, never spawned |

Every stock planet has all three rows in the tree and no pool ever spawns them (the native list carries solar and wind only).
Adding `energy_renewable_site_limited_geothermal,energy_renewable_site_limited_tidal,energy_renewable_site_limited_hydron3` to
`nativepoolincludes` spawns one of each on every active planet (45 natives a planet instead of 42; Hoth's three minimum-pool
lines then become redundant); Ossus has the three rows (O2c cloned Dantooine's 45) and, like the stock planets, nothing spawns them yet.

## 5. New classes and who would consume them

A new **leaf** under an existing class is used by every schematic that names the class or an ancestor on day one (e.g. a steel
leaf: 984 schematics name steel, metal_ferrous, metal or an ancestor). A new **class** has no consumer until a schematic names it.

| book mat (planet) | kind | nearest in SWG | consumers today |
|---|---|---|---|
| Silicate feedstock (Tatooine) | nearest existing class | no glass class; nearest `ore_siliclastic_*` | the nearest class's schematics |
| Plasma-associated feedstock [L] (Naboo) | new class | **no plasma class**; nearest `gas_reactive_*` or `energy_renewable_*_naboo` | none (new class: needs a tree class, container, survey tool and recipes) |
| Wetland biomass (Naboo) | new class | **no biomass class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Plant fiber (Naboo) | nearest existing class | no plant-fibre class; tailors use `fiberplast_naboo` | the nearest class's schematics |
| Ceramic clay (Naboo) | new class | **no clay class**; nearest `ore_carbonate_*` | none (new class: needs a tree class, container, survey tool and recipes) |
| Industrial solvent (Corellia) | nearest existing class | nearest `chemical_compound`, `petrochem_inert_lubricating_oil` | the nearest class's schematics |
| Spice-associated stock [L] (Rori) | nearest existing class | no spice class; spice is Smuggler's crafting line (Spices I–IV, XP "Spice Crafting") | the nearest class's schematics |
| Wetland reed (Rori) | nearest existing class | no reed class; nearest `fiberplast_rori` | the nearest class's schematics |
| Filter peat (Rori) | new class | **no peat class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Mineral clay (Rori) | new class | **no clay class**; nearest `ore_carbonate_*` | none (new class: needs a tree class, container, survey tool and recipes) |
| Freshwater biomass (Rori) | nearest existing class | nearest Rori seafood (`seafood_{fish,crustacean,mollusk}_rori`) | the nearest class's schematics |
| Pasture biomass (Dantooine) | new class | **no biomass class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Sulfur-associated feedstock [L] (Lok) | new class | **no sulfur class**; nearest `gas_reactive_*` | none (new class: needs a tree class, container, survey tool and recipes) |
| Jungle biomass (Yavin 4) | new class | **no biomass class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Plant resin (Yavin 4) | new class | **no resin class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Resin (Endor) | new class | **no resin class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Native biomass (Dathomir) | new class | **no biomass class** | none (new class: needs a tree class, container, survey tool and recipes) |
| Mineral clay (Dathomir) | new class | **no clay class** | none (new class: needs a tree class, container, survey tool and recipes) |

## 6. Integration list, cheap first

1. **Done in the chain (parts 1–2):** Hoth 54 + 3 energies, Ossus 45 natives + 14 minerals; all under stock classes, so every existing
   recipe that takes the class takes them (steel: 984 schematics, ore: 297, gas: 68, radioactive: 199, gemstone: 127).
2. **Site-limited energies into the native pool** (30 stock rows already in the tree, never spawned): one Lua line, galaxy-wide, +3 natives a planet.
3. **Planet minerals for the ten stock planets**, Hoth-style: 14 restricted leaves a planet (140 rows) by the part-2 rule, minimum pool one each;
   gives every planet its own named steel/ore/gas/fuel/gems inside existing recipes. One stage step (ossus_minerals generalised).
4. **MTG's Dromund Kaas (45) and Taanab (45) natives** when those planets exist; **MTG's 18 space rows** only with space zones (JTL mining).
5. **New classes from the book** (biomass ×4, plant resin, filter peat, clay, plasma feedstock, sulfur feedstock): each needs a tree class under
   organic/inorganic, a container template, a survey-tool type, string names and at least one recipe (Botanist, Pharmacist, Toxicologist); no
   consumer exists today, so they come with those professions, not before.
6. **Lore materials (slot for ChatGPT, Legends):** Mandalorian iron (Mandalore), Adegan crystals (Ossus; a gemstone leaf fits the Jedi story),
   cortosis, phrik (note: `aluminum_phrik` is already a stock aluminum leaf, galaxy-wide), songsteel, durasteel as a steel leaf, etc. Each lore
   material as a planet-restricted leaf under its stock class (cheap) or as a new class (expensive) once the planet and its story exist.
