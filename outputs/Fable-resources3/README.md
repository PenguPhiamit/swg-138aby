# R3: Hoth complete, Ossus minerals, the resource inventory — Fable, 14 Oct 2026

Stage only; read-only on /opt/swg (dev HEAD 3a0b154f when built); nothing in h/tools or Local-content touched.
Numbers are mine unless a source is named. **Verified** = checked offline here; **staged** = not yet applied or run.

| path | what |
|---|---|
| `patch/h-r3-1-hoth_client_build.patch` | part 1, h repo: `resource_tree()` takes MTG's four gem leaves and clones the three site-limited energies |
| `patch/core3-r3-1-hoth-pools.patch` | part 1, Core3-dev: the seven Hoth types in the minimum pool |
| `patch/core3-r3-2-ossus-pools.patch` | part 2, Core3-dev (apply after part 1): the fourteen Ossus types in the minimum pool |
| `tools/ossus_minerals.py` | part 2: `stage_ossus_minerals(stage_dir, base)`, the tree step for the chain |
| `build_test_archive.py` | the chain: Hoth build (patched builder) → `stage_ossus` → `stage_species(['chiss'])` → R3 rows → `tre_write` |
| `local_planets-part1.tre`, `local_planets-part2.tre` | the test-session archives; `checks-part1.json`, `checks-part2.json` |
| `inventory.md`, `inventory.json`, `tools/inventory.py` | part 3 |

## Part 1. Hoth complete (verified offline; patches clean)

- **The four gems.** MTG names them `armophous_hoth_1/2`, `crystalline_hoth_1/2`, so the builder's `endswith('_hoth')`
  missed them. Core3 restricts a type by the **substring** `_<zone>` (`ResourceTree::setZoneRestriction`,
  `name.indexOf("_" + zonename)`), so the ENUMs stay as MTG has them and are Hoth-only. Their text was MTG's "Hothian
  Type 1 Crystal Amorphous Gem"; now "Hothian Type 1 Amorphous Gemstone" / "Type 2" and "Hothian Type 1/2 Crystalline
  Gemstone" (stock spells the class text "Amorphous Gemstone"; only the ENUM carries the old `armophous`). Pools 1/1,
  attributes as MTG wrote them; they sit after `armophous_baltaran` and `crystalline_vertex`, where MTG put them.
- **The three energies.** Cloned from Endor's rows the way solar and wind are, placed after the last leaf of their kind
  (stock has no class row for the site-limited energies, only the per-planet leaves): "Hoth Geothermal / Tidal /
  Hydron-3 Renewable Energy", pools 1/1. **Why 42 natives, not 45:** `nativepoolincludes` lists 42 types — its only
  energies are solar and wind; no stock pool spawns the site-limited energies on any planet. The patch puts Hoth's three
  in the minimum pool (Hoth-only, one of each); the galaxy-wide alternative is adding the three to `nativepoolincludes`
  (+3 natives on every planet, 45 each) — the owner's call, noted in the Lua comment.
- Builder log: 829 rows (822 + 7), stock order kept, ancestors' type counts raised (resource, inorganic, mineral,
  gemstone ×2 classes, energy ×3 levels), no other cell changed. Pool patch: 17 Hoth minimum-pool entries, luac ok.
- Archive (the chain, on top of S5): `local_planets-part1.tre` **sha256 fa7d3391814e2c354158300cfc2b126524f8abec0c5d9a8bcf1258b5fc40b13e**
  (3,785,030 B, 55 entries); against S5 (b1a0a232…) only `datatables/resource/resource_tree.iff` changes, the Chiss
  entries are byte-identical, both planets registered.

## Part 2. Ossus's own minerals (verified offline; patch clean)

Fourteen zone-restricted leaves under Hoth's classes: `steel_ossus`, `iron_ossus`, `copper_ossus`, `aluminum_ossus`,
`ore_extrusive_ossus`, `ore_intrusive_ossus`, `gas_reactive_ossus`, `petrochem_fuel_liquid_ossus`,
`petrochem_fuel_solid_ossus`, `radioactive_ossus`, `armophous_ossus_1/2`, `crystalline_ossus_1/2` (restricted by the
`_ossus` substring), each right after the Hoth row of its class. **The attribute rule, derived from MTG's Hoth rows:**
MTG's row is the strongest stock leaf of the class (steel_hoth = Duralloy Steel's ranges, iron_hoth = Kammris Iron,
ore_extrusive_hoth = Vintrium, radioactive_hoth = Class 7, the gems = Type 1/2) with the quality minimum raised to 500
and the other minimums rounded up to the next multiple of 50 (696→750 cold, 348→350 malleability, 566→600
conductivity, 522→550; MTG also themed cold resist to 750–800 on Hoth, which Ossus does not copy). So each Ossus row =
the strongest stock leaf by summed minimums (Duralloy, Kammris, Polysteel copper, Phrik aluminum, Vintrium, Katrium,
Tolium gas, Class 1 liquid fuel — all seven liquid types are equal — Class 7 solid fuel and radioactive, Baltaran and
Vertex gems), quality 500–1000, other minimums up to the next 50 unless that would close the range (then the sibling's
minimum stays: heat 957–1000 on Katrium ore, 951–1000 on Vertex), pools 1/1, types 1/2, container, survey tool and
random-name class from the sibling. Names "Ossus Steel" … "Ossus Type 2 Crystalline Gemstone" (lore-neutral). The full
ranges are in `checks-part2.json`.

- Tree: 843 rows (822 + 7 Hoth + 14 Ossus), stock order kept, no other cell changed; the pool patch adds a
  `for _, ossusType in ipairs({...})` loop after the Hoth one (44 minimum-pool entries: stock 13, Hoth 17, Ossus 14).
- Archive (the chain): `local_planets-part2.tre` **sha256 248092a2db7ddb1a2d90f2ca15bcd8ed1064c9757ec07d3362681550ed7dc98c**
  (3,785,306 B, 55 entries); against S5 only `resource_tree.iff` changes, Chiss entries identical, both planets registered.
- Under the new scaling nothing here moves: restricted types stay at one planet; the backfill does not touch them.

## Part 3. The inventory

See `inventory.md` (summary, consumers, the integration list, the lore slot) and `inventory.json` (every row).
