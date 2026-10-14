# Resource names (R1) — Fable, 14 Oct 2026

Audit of every class row in our merged `datatables/resource/resource_tree.iff` (777 rows: stock 725, MTG's 50 Hoth rows,
Claude's two solar/wind clones) against `string/en/resource/resource_names.stf`, plus `stage_resource_names(stage_dir, base)`.
Read-only on /opt/swg; the merged tree for the CLI audit is read from the staging copy `Local-content/local_planets.tre`,
the string file from the client's winning copy (never our own archive). Numbers are mine unless a source is named.

## 1. The finding that changes the question

**Core3 never reads `resource_names.stf`, and the stock client does not even ship it.** A resource type's display name is
the tree's own CLASS text: `ResourceSpawner.cpp:387 newSpawn->setName(entry->getFinalClass())` (the deepest filled CLASS
column, `ResourceTree.cpp:63`), sent as plain text in `ResourceListForSurveyMessage` and as the `resource_class`
attribute. No client file mentions `resource_names` (scan of every `ui/`, `.inc`, `.lua`, `.txt` and resource table in
the load order), and the only copies of `string/en/resource/resource_names.stf` are MTG's two (mtg_planets.tre wins,
898 keys, identical to mtg_patch_019's). So in game the player sees the tree text, where **every row has a name**:
MTG wrote "Hothian Steel", "Hothian Reactive Gas", "Hothian Wild Meat" and so on. My guide's §7 warning about blank
names was wrong and is corrected (`Fable-hoth-guide/hoth-first-session.md`).

## 2. The audit (`python -I tools/resource_names.py --audit`)

| | rows | result |
|---|---|---|
| merged tree rows without a key in the string file | 12 | the root `resource` ("Resources"; no copy names it) and MTG's 11 Hoth inorganics: `wheat_wild_hoth`, `petrochem_fuel_liquid_hoth`, `petrochem_fuel_solid_hoth`, `radioactive_hoth`, `steel_hoth`, `iron_hoth`, `aluminum_hoth`, `copper_hoth`, `ore_extrusive_hoth`, `ore_intrusive_hoth`, `gas_reactive_hoth` |
| other planets | 0 | every stock planet row (45 per planet x 10) has a key; Claude's `energy_renewable_unlimited_{wind,solar}_hoth` too (MTG named them) |
| rows whose string-file text differs from the tree text | 88 | 49 stock (the tree's "Reptillian", "Dathomirian  Domesticated Milk" with two spaces, "Yavin IV Wild Milk" vs the file's "Reptilian", one space, "Yavinian") and 39 Hoth ("Hothian ..." in the tree, "Hoth ..." in MTG's file). The tree text is what players see; SOE's own typos ship on live, so nothing is changed |

Stock's per-planet pattern is `<planet word> <class>`, planet word from `fiberplast_<planet>`: Corellian, Dantooine,
Dathomirian, Endorian, Lokian, Nabooian, Rori, Talusian, Tatooinian, Yavinian (examples: "Tatooinian Wild Wheat",
"Dantooine Water Vapor", "Yavinian Wind Renewable Energy", "Rori Wild Meat"). MTG: Hothian, Kaasian, Taanab; Ossus (O2c):
"Ossus". Stock gives no planet an inorganic class (its steel, iron, ores, gases, fuels and radioactives are galaxy-wide
types), so the 11 Hoth rows have no stock example; the names follow the pattern with the stock generic class text
(`steel` "Steel", `ore_extrusive` "Extrusive Ore", `gas_reactive` "Reactive Gas", `wheat_wild` "Wild Wheat"; the two
petrochem classes have no generic text in stock, so MTG's "Liquid/Solid Petro Fuel" is kept).

## 3. `tools/resource_names.py`

```python
from resource_names import stage_resource_names, audit
report = stage_resource_names(stage_dir, base=winning_fn, tree=merged_tree_bytes)   # hoth_names style
report = stage_resource_names(stage_dir, base=winning_fn, tree=..., extra=ossus_extra())   # + the optional Ossus keys
```
`base(name) -> bytes`; `tree` is the merged tree (Claude's `resource_tree()` output); without it the base's tree is used.
The base string file is round-tripped byte-exact, ids continue from `next_id`, every missing key gets **exactly the
tree's CLASS text** (so the two sources agree), present keys are never touched, the root `resource` is skipped as stock
does. Staged result in `staged/client/string/en/resource/resource_names.stf`: 898 + 11 = 909 keys, next id 910,
75,207 bytes, sha256 `23fbcc57…`. A second pass adds nothing.

Proposed names for the same classes on other planets, should they ever get them (pattern above): `steel_tatooine`
"Tatooinian Steel", `ore_extrusive_dantooine` "Dantooine Extrusive Ore", `gas_reactive_naboo` "Nabooian Reactive Gas",
`petrochem_fuel_liquid_corellia` "Corellian Liquid Petro Fuel", `wheat_wild_ossus` "Ossus Wild Wheat" — `proposed_name()`
generates them; none are staged because no such rows exist.

**Ossus (optional, `--ossus` / `extra=ossus_extra()`):** the 45 O2c rows (`Fable-ossus/o2/resources/resource_names.tsv`,
"Ossus Wild Meat" … "Ossus Solar Renewable Energy") only matter when the Ossus tree rows are merged; tried on a scratch
copy (45 keys added), not in `staged/`.

## 4. Follow-ups for Claude

- The merged tree is the source of truth for names; keep the string file in step with `stage_resource_names` in the
  archive builder (one call, like `stage_hoth_names`), or drop MTG's file from the merge entirely — nothing reads it.
- If "Hothian" is not wanted (stock would say "Hothian" by its own pattern; MTG's string file says "Hoth"), the place to
  change it is the tree's CLASS text in `resource_tree()`, not the string file.
