# Fable backport, batches 1 and 2 (14 Oct 2026)

Staged work for Claude to review, apply to `/opt/swg/Core3-dev`, build and test. Nothing here has been loaded by Core3 or seen in the client. Everything was produced read-only from the client archives, Core3-dev at commit `2f205cd2da8330b1784f65f450553af79fef4872` (dev, 14 Oct 05:06 -0700, clean tree), Bellum Gero's repository (text only) and the owner's disc extraction.

## Folder

| Path | What |
|---|---|
| `staged/MMOCoreORB/bin/scripts/object/...` | batch 1: full files, mirroring Core3-dev (1,100 files: 1,081 changed, 19 new) |
| `diffs/<path>.diff`, `batch1.diff` | unified diffs against Core3-dev for every batch-1 file |
| `apply-manifest.tsv`, `apply.sh` | per-file sha256 of the Core3-dev file each diff was made against; `apply.sh` refuses any file whose hash changed |
| `checks.json`, `checks-summary.md` | batch-1 verification |
| `staged-batch2/`, `diffs-batch2/`, `batch2.diff`, `apply-manifest-batch2.tsv`, `apply-batch2.sh`, `checks-batch2*.{json,md}` | batch 2 (builds on batch 1) |
| `work/` | analysis data: `dormant_analysis.json` (one record per truly dormant object), `dormant_listing.txt`, `tiers.md`, `registration_fixes.json`, `core3_*` dumps, `bellum_index.json`, `disc_index.json`, `core3_orig/` (copies of the Core3-dev files touched) |
| `tools/` | the scripts that produced all of this (`dormant_analysis.py`, `stage_batch1.py`, `stage_batch2.py`, `verify_batch.py`, `luac_staged.sh`, `swg_iff.py`, `bellum_index.py`, `disc_index.py`, `include_reach.py`) |

Apply, as swgemu inside Debian:

```
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-backport/apply.sh --check   # report only
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-backport/apply.sh           # copy batch 1
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-backport/apply-batch2.sh     # then batch 2
```

`apply.sh` was exercised against a copy of the originals inside `work/` (1,076 changed + 19 new copied; a second run reports 1,095 identical; a tampered file is refused). It was never run against `/opt/swg`.

## 1. The dormant count is 2,334, not 13,627

`tools/research/dormant_objects.py` counts a template as present only when `bin/scripts/object/<path>.lua` exists. Core3-dev keeps the Mod the Galaxy import under `object/custom_content/...` and registers it under the original paths, so 11,293 of the 13,627 listed objects already have a server template. Indexing every `ObjectTemplates:addTemplate(..., "path")` string across `bin/scripts/object` (custom_content included) leaves **2,334 truly dormant objects** (2,204 from MTG archives, 130 from SOE archives). All of the TCG, veteran-reward, holiday and furniture decor that batch 1 was meant to cover is already registered; batch 1 changed accordingly (section 3).

Two more findings from the same index:

- **1,297 server registrations point at a path with no client file.** 224 are Core3 upstream's own server-only templates (for example `object/resource_container/energy_gas.iff` for the client's `shared_resource_container_energy_gas.iff`, the crafted droids, areas) and are fine. **1,073 are MTG files whose path string was mangled when MTG generated them**: an underscore became a slash (`creature_loot` → `creature/loot`, `npc_loot` → `npc/loot`, `generic_usable`, `loot_schematic`, `simple_kit`, `generic_deed`, `cube_loot`, `nova_orion`, `kashyyyk_loot`). The same strings are in MTG's published tree (`work/research/mod-the-galaxy`), so the defect is MTG's, not the 13 Oct import's. The objects still display (the client gets the shared template's CRC), but nothing can spawn them by their real path and the staff catalogue `object/sandbox/mtg_catalog.lua` lists the wrong paths. No Core3-dev script outside `object/` references a mangled path. These 1,073 are the bulk of the "truly dormant" set (1,116 of the 2,334 have a shared template but no usable server path).
- **22 client registrations point at a shared file the client lacks**: 3 are mangled strings (repaired in batch 1c); the rest are MTG placeholders (`shared_del`, `shared_ptower`), Gungan/Kel Dor hair and two jackets whose client files are not in our archives, a `decd_wroshyr_tree_dead01e` typo, and 3 apron-schematic entries from Core3 upstream itself. Listed in `work/core3_client_paths_without_file.json`.
- 22 `objects.lua`/`serverobjects.lua` files under `custom_content` are never reached from `object/main.lua` (`tools/include_reach.py`). Most hold only MTG placeholders; five hold real templates: four are wired in batch 2, the fifth (`custom_content/draft_schematic/vehicle`, 11 vehicle schematics) belongs to Claude's Hoth vehicle chain.

## 2. Tiers (the 2,334 truly dormant objects)

Rules are in `tools/dormant_analysis.py` (RULES); per-object tier, reason and pre-CU note are in `work/dormant_analysis.json` and `work/dormant_listing.txt`. Counts: **A 1,282, B 580, C 116, D 356.**

| Tier | Category | Objects | Reason / pre-CU note | Examples |
|---|---|---|---|---|
| A | `object/tangible/loot` | 1122 | loot item: server template only, then a loot-group entry (1,073 of these are the mangled MTG registrations repaired in batch 1) | acorns, adventurers_remains_03, aero_magnifier_generic |
| A | `object/tangible/wearables` | 107 | wearable: server template only; 13 staged in batch 1, 70 are NGE per-gender/species variants of pre-CU necklaces (`_f`/`_m`/`_wke_`/`ith_`), 17 base templates, 7 cybernetic bases (NGE) | necklace_gcw_imperial, wod_nightsister_pants_s01, armor_bounty_hunter_crafted_chest_plate |
| A | `object/resource_container` | 37 | false positive: Core3 upstream uses them under short server names (`resource_container/energy_gas.iff`) | resource_container_energy_gas |
| A | `object/tangible/item` | 7 | Kashyyyk quest items (hunting licence, Wookiee scroll, totems); no quest, so hold | eqp_kash_hunting_license |
| A | `object/tangible/furniture` | 4 | 1 decor (Y-8 passenger chair, batch 2), 3 base templates | frn_chair_y8_passenger_s01, hologram_base |
| A | `object/static/*` | 2 | christmas tree 02 is a duplicate path of an already registered object; Mustafar mining facility static staged in batch 2 | som_droid_mining_facility |
| A | other | 3 | base templates (dance prop, contraband, Y-8 deed/space) | prop_base |
| B | `object/draft_schematic/armor` | 215 | armor schematic: needs the crafted armor, stats and a profession hook (NGE appearance armor) | armor_appearance_assault_trooper_* |
| B | `object/tangible/component` | 73 | crafting component: needs the schematic that makes it and the one that uses it | armor_appearance_enhancement_base |
| B | `object/tangible/loot` | 57 | loot schematic: needs the draft schematic it grants (TCG houses, WoD huts, planning tables) | atat_house_loot_schem, wod_ns_gate_schematic |
| B | `object/draft_schematic/weapon` | 55 | weapon schematic: needs the crafted weapon, stats and a profession hook | 2h_sword_sith, blasterfist |
| B | `object/weapon/ranged` + base/melee | 47 | weapon: needs damage/speed stats and a source (droid weapons, turrets, heavy NGE weapons, snowball) | droid_cww8, heavy_pulse_cannon, snow_ball_weapon |
| B | `object/tangible/medicine` | 36 | medicine: needs effect values and a source (NGE stimpack tiers, enhancers) | stimpack_a, enhancer_bactajab |
| B | `object/mobile/vendor` | 27 | TCG vendor/greeter bodies: need the vendor-deed chain (NGE greeters) | greeter_ewok_f, special_vendor_tcg_series1_vendor_jawa_male |
| B | `object/creature/player` | 20 | playable species (MTG new-species pack): Races.h, character creation, appearance work; owner: regular species first, no hybrids | aqualish_female, togruta_female |
| B | `object/building/player` | 16 | player-city buildings in three styles (SOE client files) and the WoD small hut: deed, building template, portal layout | player_city_bank_naboo_style_01, sm_hut |
| B | `object/draft_schematic/bio_engineer` | 10 | SOE-client bio-engineer food component schematics: profession hook | bio_component_food_duration |
| B | `object/static/structure` | 9 | statics placed by world building; the 8 Tatooine walls are staged in batch 2 | wall_tatooine_large_style_100 |
| B | `object/tangible/deed` | 6 | deed chains: 3 Kashyyyk pet deeds, 1 house deed, the 2 Hoth vehicle deeds (Claude's set) | bolotaur_deed, vehicle_deed_organa_speeder |
| B | other | 9 | structure schematics, food with effects, faction-perk base register/detector base, lightsaber base | ns_hut_schem, detector_base |
| C | `object/tangible/cybernetic` | 47 | cybernetics: NGE system | cybernetic_crafted_forearm_l_01 |
| C | `object/mobile/hologram` | 35 | hologram NPCs for NGE storyteller/heroics | atat_hoth, bearded_jax |
| C | `object/tangible/dungeon`, `terminal`, `theme_park`, `travel`, `location`, `ground_spawning` | 30 | props of instances/systems not ported (Avatar Platform, Myyydril, Kashyyyk content terminals, spawners) | avatar_terminal_master_console, myyydril_machine |
| C | `object/mobile/beast_master`, `object/player_quest` | 4 | beast master, NGE quest journal | bm_acklay, base_player_quest |
| D | space (`object/ship/*`, `tangible/ship`, `intangible/ship`, `draft_schematic/space`, `space_mining`, `shipcontrol`) | 268 | JTL; space is deferred | arc170_tier1, mass_reduction_kit_mk1 |
| D | `object/mobile/skeleton` | 52 | client animation rigs, not NPCs | bm_bat |
| D | `object/soundobject` | 19 | NGE event music objects | soundobject_ewok_loveday |
| D | inventories, bases, tests | 17 | container variants, base templates, test objects | creature_inventory_10, test_falcon |

Pre-CU fit, in short: tier A loot and wearables are cosmetic and fit; the 643 collection pieces and 160 space collection pieces are NGE collections fodder (usable as junk loot only); cybernetics, beast master, holograms, player quests and expertise-era weapons/medicine are NGE systems; the 20 species are the MTG new-species pack the owner has already decided on (regular species before hybrids).

## 3. Batch 1 (staged, 1,090 objects, 1,100 files)

Decor-first was the plan, but every candidate decor object was already in Core3-dev. The coherent set that remained is **making the MTG-imported NGE loot usable under its real paths**, plus the only tier-A items with no template at all that need nothing else.

- **1a, 1,074 server-path repairs** (one string per file, bytes and CRLF line endings otherwise untouched): 643 collection pieces (`creature_loot/collections`, incl. 160 space and 49 fried-ice-cream pieces), 189 NPC junk loot (`npc_loot`), 72 Mustafar cube loot, 69 generic creature loot (organs, bones, heroic junk, Empire Day autographs), 58 `generic_usable`, 29 `loot_schematic`, 6 `simple_kit`, 3 `generic_deed`, 3 quest (Nova Orion toy, Hero of Tatooine), 1 Kashyyyk loot, 1 Kashyyyk cave-driftwood static (`emperors_cave_driftwood` → `cave_driftwood`). The same 1,073 strings are corrected in `object/sandbox/mtg_catalog.lua` (1,073 occurrences). `work/registration_fixes.json` holds the mapping; it is derived by treating `/` and `_` as the same character and matching the client's `shared_` file, with no ambiguous matches.
- **1b, 13 new wearable templates** under `custom_content/tangible/wearables/{necklace,pants,ring}/` (new folders, `objects.lua` + `serverobjects.lua` + one server file each; includes added to `custom_content/tangible/wearables/serverobjects.lua` and `allobjects.lua`): Imperial/Rebellion Siege Necklace and Ring (GCW set), Life Day necklace, Black Sun medallion, primitive necklaces 01/03/04, Rodian safari necklace (base object; the `_f/_m/_wke` variants stay dormant), Nightsister Pestilence/Scourge Leggings, Outbreak prison-guard pants. Server files copy `object/tangible/wearables/<kind>/<kind>_s01.lua` (pre-CU `playerRaces` list, experimental properties, `RingObjectMenuComponent` for rings). Neither Bellum nor MTG has these.
- **1c, 3 client-path repairs** in `objects.lua` files: `creature_loot/kashyyyk/loot/` → `kashyyyk_loot/` (adventurers_remains_03), `object/object/static/.../shared_hoth_elevator.iff` → `object/static/...`, `object/dungeon/avatar_platform/...` → `object/tangible/dungeon/avatar_platform/...` (both strings, plus its server file). Lua variable names were left as MTG wrote them.

Left out on purpose: the 25 Hoth loot items in `tools/hoth/data/hoth_loot_inventory.json` (only the two vehicle deeds are truly dormant; the other 23 are registered in custom_content), and `custom_content/draft_schematic/vehicle` wiring (part of the same vehicle chain).

Sources to propose later (no loot or vendor wiring in this batch): generic creature loot and NPC junk → Core3 junk loot groups by creature/NPC type; heroic junk, cube loot, collections → hold until those systems or use as junk; Siege jewellery → GCW reward (faction recruiter); Life Day necklace → Life Day event; Black Sun medallion → Black Sun NPC loot; primitive necklaces → Tusken/primitive NPC loot; Nightsister leggings → Nightsister loot; prison-guard pants → Death Troopers theme if the owner wants it.

## 4. Batch 2 (staged, 55 objects, 22 files; apply after batch 1)

- **2a, wiring (45 MTG templates that exist in Core3-dev but never load):** one `includeFile` line each in `custom_content/tangible/holiday/empire_day/serverobjects.lua` (32 Empire Day crafting components), `custom_content/building/player/serverobjects.lua` (10 construction markers for TCG houses; `SIOT` installation templates), `custom_content/tangible/content/serverobjects.lua` (2 Empire of Wookiees data disks), `custom_content/static/serverobjects.lua` + `allobjects.lua` (flagpole base). The components load but have no recipes; the markers matter only once their house deeds exist.
- **2b, 10 new templates:** 8 Tatooine wall statics `object/static/structure/tatooine/wall_tatooine_large_style_{100,200,500,1000,2000,2500,4200,8000}` (MTG archive 023; not Borrie's Wall Pack: checked against its ZIP), the Mustafar `som_droid_mining_facility` static, and the Y-8 passenger chair `object/tangible/furniture/space/frn_chair_y8_passenger_s01` (SOE original: the disc copy in `patch_15_01.tre` is byte-identical to the copy our client loads from `mtg_patch_010_object_01.tre`, see `work/disc_index.json`). Statics are `SharedStaticObjectTemplate` (IFF form `STAT`) in the existing `custom_content/static/...` folder files; the chair gets a new `custom_content/tangible/furniture/space/` folder.

## 5. Rights per source

- Client files for every staged object come from the Mod the Galaxy archives (`mtg_patch_022.tre` 1,132, `mtg_patch_023.tre` 8, `mtg_patch_019.tre` 4, `mtg_patch_010_object_01.tre` 1). MTG's own condition is full creator credit on the server website and no claim of authorship; the catalogue decision for its item/decor/armor family is **P** (`Content-catalogue/SWG-active-content-catalogue.md`). The Lua files repaired or extended in `custom_content` are MTG's published scripts (AGPL, `work/research/mod-the-galaxy/COPYING`), already credited in `Community-content/CREDITS-and-sources.txt`; keep that credit. Most of these client files are SOE's own NGE data repacked by MTG; the owner's disc (2006) holds 897 of the 2,334 truly dormant objects in its version-5 archives (`disc_archives` in `work/dormant_analysis.json`; the Y-8 chair and the 7 Kashyyyk items among them), but not the 2008+ TCG/collections files. Spot check (`tools/disc_compare.py`): the disc copies of the Y-8 chair, the cave driftwood and the Kashyyyk hunting licence in `patch_15_01.tre` are byte-identical to the copies our client loads from the MTG archives.
- Nothing from Bellum Gero was ported in the end: its index (`work/bellum_index.json`, keyed by registered path, 16,734 server paths, 88 registered away from their folder) has none of the staged objects. Nothing from the Legends leak or SWG-Source was read.
- Nothing cleared as unknown was staged; the Gungan/Kel Dor hair and the two jackets with missing client files were left alone.

## 6. Verification (offline; `checks.json`, `checks-batch2.json`)

Batch 1: 1,090 objects, 1,090 pass. Client shared .iff present for all (winning archive per object recorded); IFF form `STOT` for 1,088 and `STAT` for 2 (driftwood, elevator), matching the `SharedTangibleObjectTemplate`/`SharedStaticObjectTemplate` class their shared template uses; all 1,090 are in the merged CRC table `Local-content/local_planets/misc/object_template_crc_string_table.iff` (29,358 names) and none in the stock table; each server path is registered exactly once after the batch and no Lua name or file collides with Core3-dev; every `includeFile` target exists and every staged file is reached from `object/main.lua`; `luac5.3 -p` passes all 1,100 files. 775 of 1,090 objects resolve a client name string; 315 do not (86 `static_item_template` keys, 74 with an empty table name, 57 `item_n`, 49 `component_n`, 12 `collection`, 10 `static_item_n`, rest smaller): the client will show the raw key for those until a string file or `customObjectName` supplies a name.

Batch 2: 55 objects, 55 pass; 22 files, `luac5.3 -p` passes all; 45 wired templates each registered once in their existing file, now reachable; the 10 new ones collide with nothing; all 55 in the merged CRC table. 22 of 55 resolve a client name (statics and markers have none by design).

Not proved: no file has been loaded by Core3; no object has been seen in the client; `/object createitem` accepts tangible templates only, so the statics (walls, mining facility, driftwood, elevator) need a static/world placement command to test; the wearables' per-species appearance was checked only for the presence of the `_f`/`_m` `.sat` files (the two Nightsister leggings and the prison-guard pants have a single `.sat` with no gender suffix, so their look on male characters is unverified).

## 7. Batch 3+ proposals

1. The two Hoth vehicle deeds (Claude's chain) and `custom_content/draft_schematic/vehicle` wiring (11 schematics).
2. Tier B loot schematics (57) with their draft schematics and the TCG house deed chain (construction markers are wired by batch 2).
3. NGE weapons, medicine and food with real stats (B, 83 objects) once the owner wants NGE-era items in a pre-CU economy.
4. The MTG new-species pack (20 player templates, 27 vendor bodies): owner decision on species order first.
5. Names for the 315 batch-1 objects without a client string (an added `.stf` in our own archive, or `customObjectName` in loot scripts).
6. Disc-only content: 58 object templates exist on the disc's version-5 archives and not in our client (34 ship, 11 space, 6 melee power-up schematics `draft_schematic/item/item_powerup_weapon_melee_*`, 4 space resource containers, Kashyyyk Rodian shuttle NPC, tutorial droid deed, newbie droideka). Each needs its client `.iff` (and appearance files) cherry-picked into our own archive and a CRC-table entry before a server template helps.
7. Fix `tools/research/dormant_objects.py` to index registered paths (outside my write area; `tools/dormant_analysis.py` here does it).

## 8. Open questions for the owner

1. Batch 1 renames 1,073 MTG server paths to the real SOE spelling (`creature_loot`, not `creature/loot`). MTG's catalogue is corrected to match. Keep the real names (as staged) or MTG's?
2. NGE junk and collection loot in a pre-CU galaxy: wire it into loot groups later, or keep it staff-only?
3. New wearables use the pre-CU species list; extend to the new species when they are in?
4. The disc's 71 later archives (`patch_18_*` to `patch_33_*`, `sku1/2/3`) are TRE version 6 (`EERT 6000`): the header's count and offsets are zero and no file table was found at the start or end of the file; Bellum's reader returns nothing. Only the version-5 archives (`patch_00` to `patch_17`, `data_*`) were indexed. Want a version-6 reader worked out (read-only) or is the 2006 content enough?
5. Prison-guard pants (Death Troopers/Outbreak theme): keep or drop?
