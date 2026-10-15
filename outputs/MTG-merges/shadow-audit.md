# Stock shadowing MTG: the audit and the extended merge (15 Oct 2026)

Analysis and staging only. Nothing was installed, no server or bot was touched, and no git commit was made.

## What was done

- `shadow_audit.py` (new, read-only, about 20 seconds once the archives are cached) compares every file that a stock archive and an MTG archive both hold. It writes `shadow-audit.json`.
- `stage_mtg_merges.py` was extended from 5 files to 83: 6 datatables, 75 string files and 2 CRC string tables. It also gained a third list, `CRC_TABLES`. Its docstring describes the new scope.
- `build_mtg_merges_archive.py` now takes its expectation from the merge lists. Merged files the fauna archive lacks must be new. Merged files an earlier chain step already staged must be changed, with every staged entry kept. Every other entry must stay byte-identical. The script also lists what differs from the client's current `local_planets.tre`.
- No other chain step's files were edited.
- Trial build: `local_planets-mtgmerge.tre`, sha256 `a241de9de6fb785b42368a54418aafd42539b2417177dad05491d65c67561fe6`, 4,185,284 bytes, 133 entries. `checks.json` says `"ok": true`.
  - 78 new entries and 5 changed ones, against 78 and 5 expected. Nothing is missing. All staged entries were kept.
  - The merge is idempotent: a second run adds nothing.
  - Against the client's current `local_planets.tre` (1315dbb4): only merged files differ. The five original merge files are byte-identical to the installed ones.
  - Not installed, and untested in game.

## How the comparison works

- **Load order.** The client order comes from `swgemu_live.cfg` through `client_load_order.py`: 51 stock archives at priorities 24–49, then the 23 MTG archives at 1–23.
  - The stock winner for each file is the one `trn_iff.client_index()` picks. That is also the merge step's base.
  - The MTG copy compared is the highest-priority one.
  - The server does the same thing. Core3's `TreeArchive` keeps the first archive in `TreFiles` that has a file: `TreeDirectory` uses a no-duplicate insert plan, as read in `h/work/Core3`. The test galaxy appends `MTG_TRES` after stock in client order (`test_galaxy.py`).
- **Same-priority archives.** For archives that share a priority (25, 37 and 38), `client_index` lets the later one in the list win, but Core3 keeps the earlier one. Across all 125,571 shared files, the two choices hold identical bytes in every case (0 differences), so this does not matter today.
- **Datatables** are compared on a key: the fewest leading columns on which the stock rows and MTG's rows are each unique. If a table repeats whole rows, the whole row is the key.
  - `mtg_changes` means MTG has a key that stock also has, with other values.
  - `mtg_superset` means MTG adds rows and changes none of stock's.
- **Strings** are compared key by key. **CRC tables** are compared name by name; each added CRC is checked against the SOE CRC of its name, and against collisions with stock.
- **Files our chain already stages** (`local_planets-fauna.tre`) were compared against the staged copy too, because the merge builds on that copy.
- **What the server reads** comes from string literals in `h/work/Core3/MMOCoreORB/src`. That is upstream Core3 `unstable` 403893d9, not the live `sandbox` branch, which I could not read. Tests and the client code were excluded. The list is in `SERVER_FILES` and `SERVER_PREFIXES` in `shadow_audit.py`.

## Inventory

- Stock holds 125,572 files and MTG holds 202,951. **125,571 are in both.**
  - The one stock file MTG lacks is `appearance/animation/boss_nass_cbt_rifle_prone_ready_to_rifle_standing_ready.ans`.
  - 77,380 files are MTG-only. Those are not shadowed and not part of this audit.
- MTG is essentially a full repack of the client plus its additions.

| class | files | what they are |
|---|---:|---|
| `same` (byte-identical) | 124,354 | including 2,136 datatables and 4,315 string files |
| `binary` (differs, not a table or string file) | 775 | 430 appearance (226 .msh, 47 .lod, 45 .flr, 44 .lat ...), 76 shader, 64 object templates, 61 palettes, 57 textures, 23 terrain, 11 clientdata, 11 input maps, 8 creation, 5 UI .inc, 4 snapshots, others |
| `mtg_changes` | 262 | 217 Japanese string files, 42 English string files, 3 datatables (door_style and two mount tables) |
| `mtg_superset` | 130 | 74 + 44 string files (en + ja), 9 datatables, 3 CRC tables |
| `same_content` (same keys and texts, other ids or order) | 38 | string files, nothing to merge |
| `different_format` | 10 | datatables, see below |
| `mtg_subset` (MTG only lacks stock keys) | 2 | `quest/ground/test_destroy_multiple.stf`, `socials.stf` |

| decision | files |
|---|---:|
| merged | 83 (the original 5 plus 78) |
| nothing to merge | 124,394 |
| skipped: binary | 775 |
| skipped: not English (string/ja; the English client and the server read only string/en) | 261 |
| for Claude: MTG edits stock rows or strings | 42 |
| for Claude: different format | 10 |
| for Claude: additive, but read by the server or a planet-scope decision | 5 |
| nothing left (`misc/object_template_crc_string_table.iff`) | 1 |

## Merged (in `stage_mtg_merges.py`)

3,835 entries in total. "From" names the MTG archive each entry came from. A key in two copies takes the higher copy's value.

### Datatables (`TABLES`): identical columns and types, MTG only adds rows

| file | key | added | from | what it unlocks |
|---|---|---:|---|---|
| `datatables/mount/logical_saddle_name_map.iff` | 1 | 48 | 022 | Saddles for MTG vehicles and mounts (the BARC). *Already merged by Claude.* |
| `datatables/mount/saddle_appearance_map.iff` | 2 | 44 | 022 | As above. *Already merged.* |
| `datatables/mount/rider_pose_map.iff` | 2 | 54 | 022 | Rider poses. *Already merged.* |
| `datatables/mount/valid_scale_range.iff` | 2 | 58 | 022 | Mount scales. **The server reads it**, see the risks. *Already merged.* |
| `datatables/planetary_map/disabled_planetary_map.iff` | 1 (Planet) | 1 | 022 | `dungeon2`, like stock's `dungeon1`. Client only. |
| `datatables/radar/radar_range.iff` | 1 (Planet) | 1 | 022 | `dungeon2` radar range (-1, 128), like stock's `dungeon1`. Client only. |

### CRC string tables (`CRC_TABLES`, new list)

| file | added | from | what it unlocks |
|---|---:|---|---|
| `misc/planet_crc_string_table.iff` | 39 | 022 25, planets 3, 019 11 | MTG zone names: kashyyyk (and its sub-zones), mustafar, dungeon2–4, coruscant, mandalore, chandrila, moraband, hutta, taanab, avatar, and space zones (space_kashyyyk, space_ord_mantell ...). Builds on the staged table, so Hoth and Ossus are kept. Client only. Inert unless the server serves those zones. |
| `misc/quest_crc_string_table.iff` | 1,953 | 019 | MTG quests: space duties, EP3 and NPE quests, ground quests. **The server reads it**: see below. |

All of these CRCs equal the SOE CRC of their names, and none collides with an existing entry. The merge asserts both.

### Strings (`STRINGS`): 75 files, MTG adds keys and edits none

All are in `string/en`, so **the server reads them** too (see below). Four of them (creature_names, player_species, skl_d, skl_n), plus the planet CRC table, were already staged by the chain; the merge keeps every staged string.

| file (`string/en/`) | added | from | sample keys |
|---|---:|---|---|
| `monster_name.stf` | 183 | 022 | a1_deluxe_floater, advanced_stap_speeder, air2_swoop_speeder_n (the BARC; *already merged*) |
| `craft_armor_ingredients_n.stf` | 309 | 013 | absorbtion_coating, appearance_enhancement_one |
| `mob/creature_names.stf` | 313 | 023 27, 013 286 | nerf, nerf_male, ambrian_staga (staged by the chain) |
| `space/ship_names.stf` | 83 | 013 | avatar_platform, corellian_corvette_ep3 |
| `space_crafting_n.stf` | 39 | 013 | advanced_xwing_reward_deed, arc170_reward_deed |
| `sign_name.stf` | 36 | planets | aurilia_cantina_sign, armory |
| `theme_park/racing/racing.stf` | 36 | planets | mosrassen_laptime_checkpoint0 ... |
| `player_species.stf` | 30 | 023 | name_hutt, desc_hutt, name_togruta (staged by the chain) |
| `space_ship.stf` | 30 | 022 | player_advanced_xwing, player_arc170, player_blacksun_heavy |
| `deed.stf`, `deed_detail.stf` | 29 each | 013 | atat_house_deed, bespin_house_deed, commando_house_deed |
| `food_name.stf` | 28 | planets | dessert_luilris_mushroom_pie, drink_rancoraid |
| `craft_item_ingredients_d/_n.stf` | 27 each | 013 | vipbunkerhouse, atathouse, bespinhouse |
| `obj_d.stf` | 27 | planets | gmf_crafted_bat_pheromone_d, obj_downey_box |
| `player/player_utility.stf` | 26 | planets | alarm_clock_*, enzyme_buff_extra_roll |
| `building_detail.stf` | 25 | planets | dathomir_quarantine_zone_cantina_d, garden_imperial_01 |
| `badge_n.stf` / `badge_d.stf` | 20 / 19 | planets | bdg_exp_kash_kachirho, bdg_racing_mosrassen_hills |
| `event_perk_jukebox_songs.stf` | 20 | planets | anakin_theme, battle_of_hoth |
| `monster_lookat.stf` | 19 | 022 | bane_back, finned_blaggart |
| `faction/faction_names.stf` | 17 | 023 15, planets 2 | azure_cabal, faction_sayormi |
| `space/space_mobile_type.stf` | 17 | 013 | awing_mercenary, kessel_mine_turret_tier1 |
| `spacequest/quests.stf` | 17 | planets | ep3_civilian_protection_guild |
| `ui_opt.stf` | 17 | 013 | combat_spam_brief, combat_spam_show_armor ... |
| `space/space_item.stf` | 16 | 013 | bst_nova_breaker, crg_mining_large |
| `skl_d.stf`, `skl_n.stf` | 14 each | 023 | species_nautolan, species_togruta (staged by the chain) |
| `lair_n.stf` / `lair_d.stf` | 12 / 5 | planets | lair names (endor_arachne_drone_lair ..., eow_imperial_power_gen) |
| `dungeon/space_dungeon.stf` | 11 | 013 | ep3_bocctyyy_path_ticket, ep3_hracca_glade_ticket |
| `craft_clothing_ingredients_n/_d.stf` | 10 / 4 | 013 | advanced_armor_layer_*, armor_core_enhancement |
| `got_n.stf` | 9 | 013 | armor_core, armor_layer, armor_psg |
| `space_item_n.stf` | 9 | 013 | advanced_xwing_pcd, arc170_pcd, grievous_starship_pcd |
| `terminal_ui.stf` | 8 | 013 | door_locks_disabled, no_passcard |
| `ui_auc.stf` | 7 | 023 | help_all_filter_text, include_entrance_fee |
| `building_lookat.stf` | 6 | planets | eow_imperial_endor_base, housing_naboo_window_style_1 |
| `performance.stf` | 6 | 013 | perform_inspire_building, perform_inspire_crafting_bonus |
| `ship_slot_compatabilities_n.stf` | 5 | 013 | crg_0, mod_0 |
| `space/space_interaction.stf` | 5 | 013 | no_ep3, unload |
| `space_crafting_d.stf` | 5 | 013 | ancient_asteroid_chunk |
| 4 keys each | 4 | 013 / planets | `hyperspace_points_n/_d` (space_kashyyyk_0–3), `space/quest`, `terminal_lookat`, `ui_trade` |
| 3 keys each | 3 | 013 | `craft_dna_components_n/_d` (player DNA), `pet/pet_menu` (ep3_unpack, mount_restricted_scene ...), `slicing/slicing`, `space/scst_short_n`, `ui_text_color` |
| 2 keys each | 2 | 013 | `game_language` (hutt, huttese), `ship_slot_compatabilities_d`, `ship_slot_n/_d`, `ui_group_launch`, `ui_opt_sound`, `ui_planet_map`, `wound_terminal` |
| 1 key each | 1 | 013 | `craft_results`, `error_message`, `group`, `launch_names` (station_kashyyyk), `money/acct_n`, `npc_lookat` / `npc_name` (general_grievous), `quest/pirates`, `ship_component_n`, `texture_kit`, `theme_park_name` (royal_guard), `ui_chatroom`, `ui_radial` (bio_link), `ui_spacehud` |

Four of these files lack one stock key in MTG's copy: `error_message`, `lair_n`, `pet/pet_menu` and `ui_opt`. The merge keeps the stock key. Per-file keys and samples are in `shadow-audit.json` and `checks.json`.

### Server-read files among the merged ones (flagged)

- **`datatables/mount/valid_scale_range.iff`** (existing merge) controls which creatures a Creature Handler can train as mounts, through `PetManager::checkMountEligibility` and `isValidMountScale`. See the risks.
- **`misc/quest_crc_string_table.iff`** is loaded at startup by `PlayerManager::loadQuestCrcTable`; the test galaxy's log should then report 2,709 quest CRCs instead of 756. It is used only lazily: `getQuestTasks(crc)` opens `datatables/questtask/<name>.iff` when a script asks for that quest. Those files for MTG's quests are MTG-only, so they are not shadowed. Nothing runs until something requests one of those CRCs.
- **Every `string/en` file** goes into the server's strings database (`StringIdManager::populateDatabase`). That database is filled only when it is new or truncated, with the `reloadstrings` argument, or with `Core3.TreManager.ReloadStrings`. The test galaxy sees the new strings only after a reload.

## For Claude to decide (skipped)

### 1. MTG edits stock strings: 41 English string files, plus door_style (largest first)

The additive part of these is the biggest remaining unlock: names and descriptions of MTG's items, armor, weapons, furniture, houses and structures. Without it, MTG objects show raw `@file:key` text.

`monster_name.stf` was the precedent: it also has 5 MTG edits, and the existing merge adds the missing keys and keeps the stock texts. The same function would apply unchanged. The rules here said to skip these, so they are listed rather than merged.

| file | MTG adds | MTG edits | sample edit (stock → MTG) |
|---|---:|---:|---|
| `item_n.stf` | 1,435 | 17 (3 only case or whitespace) | broken_grav_unit: "Broken Grav Unit" → "Grav Unit" |
| `player_structure.stf` | 782 | 21 | change_residence_time: "...for %NO hours." → "...for %TT." |
| `item_d.stf` | 737 | 40 | art_crate: "something heavily" → "something heavy" |
| `gcw.stf` | 390 | 2 | headline texts |
| `wearables_name.stf` | 228 | 10 | "Leather Amor Chest Plate" → "Leather Armor Chest Plate" |
| `wearables_detail.stf` | 217 | 155 | bone armor descriptions |
| `frn_n.stf` | 212 | 5 | frn_desk: "Desk" → "Professor's Desk" |
| `obj_n.stf` | 211 | 1 | droid_battery: "A Droid Battery" → "Droid Battery" |
| `weapon_name.stf` | 199 | 9 | carbine_dxr6: "DXR6 Carbine" → "DXR6 Heavy Carbine" |
| `weapon_detail.stf` | 187 | 44 | descriptions |
| `building_name.stf` | 174 | 9 | bank_general: "bank general" → "bank general - DELETE ME!" |
| `frn_d.stf` | 170 | 18 | descriptions |
| `crafting.stf` | 119 | 1 | case only |
| `clientpoi_n.stf` | 117 | 2 | Staged by the chain (our Hoth POIs). |
| `clientpoi_d.stf` | 81 | 53 | Staged by the chain. |
| `quest_item_n.stf` | 80 | 1 | fs_crafting4_computer_core renamed |
| `monster_detail.stf` | 63 | 2 | "X31" → "X-31" |
| `craft_armor_ingredients_d.stf` | 52 | 11 | |
| `theme_park_nym/messages.stf` | 52 | 1 | |
| `quest_item_d.stf` | 48 | 4 | |
| `datatables/appearance/door_style.iff` (key doorStyleName) | 39 | 14 | 39 door styles for MTG houses and POIs (ply_all_atat_door, ply_yt1300_door, poi_kash_*, thm_must_*). The edits change triggerRadius (4 → 32) and door effects (`door_open_djt.cef`, `door_open_ljt.cef`, `door_open_blast_style_01.cef`). |
| `pet_deed.stf` | 35 | 2 | |
| `terminal_name.stf` | 32 | 1 | "Insurance Terminal" → "Repair Terminal" |
| `planet_n.stf` | 31 | 2 | Staged by the chain. "Yavin" → "Yavin 4". |
| `food_detail.stf` | 29 | 28 | |
| `terminal_detail.stf` | 25 | 3 | |
| `event_perk.stf` | 7 | 13 | |
| 15 more files | 0–5 each | 1–87 each | `quest/groundquests`, `quest_armorsmith`, `ui` (avatar text), `container_error_message`, `dungeon/death_watch`, `crafting_detail`, `space/cargo`, three spacequest escort files, `event_perk_detail` (+0 ~87), `event_perk_npc_actor`, `newbie_tutorial/system_messages` (MTG blanks two texts), `stormtrooper_attitude/st_response`, `ui_shipview` |

### 2. Different format: 10 datatables

Eight differ only in how a type is written: stock `I` against MTG `i`, or `f(0.0)` / `f[0.0]` against `f[0]`. In our reader, and for the cell bytes, these are the same 4-byte values. What uppercase `I` means to the client was not checked. If they are compared by value under stock's types:

| file | by value | notes |
|---|---|---|
| `datatables/weapon/weapon.iff` | superset, +58 rows | MTG's file is stock's 62 rows in order plus 58 weapon effects (rifle_dc15, rifle_proton, rifle_trando_hunter ...), probably needed for MTG weapons' bolts and effects. Rows repeat, so a key of (Weapon Effect Id, Weapon Effect Index) would be needed. One added row is empty (`''`, 0). |
| `datatables/interior/interior.iff` | superset, +3 | echo_base_pob cells r0, r1, r15: cave ambience for MTG's Echo Base. |
| `datatables/environment/talus.iff` | changes, +1 ~27 | Adds a lifeday row; MTG edits 27 of stock's rows (sky gradients and more). |
| `datatables/creation/racial_mods.iff` | superset, +18 (+17 against the chain) | Species workstream. The server reads it. |
| `datatables/customization/customization_data.iff` | superset, +149 (+107 against the chain) | Species and Image Designer data. The server reads it. |
| `datatables/customization/customization_group_instance.iff` | superset, +80 | Species. Staged by the chain. |
| `datatables/customization/hair_assets_skill_mods.iff` | superset, +163 (+85 against the chain) | Hair per Image Designer skill. The server reads it. |
| `datatables/customization/palette_columns.iff` | changes, +21 ~4 | MTG changes 4 palettes' index counts (ui, wr_cloth_general: 10000 → 256). The server reads it. |

The other two really differ in columns:

- `datatables/environment/taanab.iff`: MTG's newer environment format, with 11 other columns.
- `datatables/travel/travel.iff`: MTG adds columns taanab, kaas and kashyyyk_main; our chain adds ossus. The server reads it for fares.

### 3. Additive, but skipped on purpose

| file | MTG adds | why skipped |
|---|---|---|
| `datatables/clientpoi/clientpoi.iff` | 20 rows | The server reads it (PlanetManager POIs). MTG adds its own Hoth POIs (hothechobase, hothstarport at 0,-2000, hothlake, hothwampacave) beside our Hoth's, plus 10 Mandalore and 6 Taanab POIs. |
| `datatables/creation/attribute_limits.iff` | 18 rows, 16 species | The server reads it (character creation). Species workstream. bith and aqualish appear twice, with different values. |
| `datatables/customization/allow_bald.iff` | 8 rows | The server reads it. Species: hutt, nautolan, togruta, aqualish (chiss is already staged). |
| `datatables/player/waypoint_planets.iff` | taanab, nalhutta, kashyyyk, kaas | They would appear in the waypoint planet list. Which planets exist is the owner's call. |
| `datatables/resource/resource_tree.iff` | 45 rows against stock | The server reads it (resource classes). It conflicts with the chain's staged copy: 765 differences (Ossus rows, raised type counts). |
| `misc/object_template_crc_string_table.iff` | nothing left | The Hoth build already merges patch_14_00 + mtg_patch_022 + mtg_patch_023 (29,358 names). No MTG copy (023, 022, 021, 019, 013) has a name the staged table lacks. |

### 4. Binary (775), not mergeable here. The ones that matter most:

- **Planets.** `terrain/tatooine.trn` and `snapshot/tatooine.ws`: MTG 023's Tatooine, with 1.62 MB against 1.43 MB of buildouts, is hidden by stock. `terrain/taanab.trn`, `terrain/environment/taanab.iff` and the Taanab color ramps: stock's own Taanab hides MTG's. Also `terrain/otoh_gunga.trn`, `snapshot/dathomir|lok|rori.ws`, and 17 space terrains (MTG's `space_09.trn` is 0 bytes). The server reads terrain and snapshots too.
- **Server-read templates and descriptors.**
  - `abstract/slot/descriptor/mount_rider.iff` (MTG adds rider slots; may matter for multi-seat MTG vehicles).
  - `abstract/slot/slot_definition/slot_definitions.iff`.
  - `customization/asset_customization_manager.iff` (342 KB against 386 KB).
  - `chat/mood_types.iff`.
  - `creation/default_pc_equipment.iff`, `default_pc_hairstyles.iff` and 6 `profession_defaults_*.iff`, all staged by the chain.
  - 64 object templates, among them `object/mobile/vehicle/shared_landspeeder_base.iff` and `shared_landspeeder_xp38.iff`, `object/creature/base/shared_base_creature.iff`, Death Watch and Mandalorian loot schematics and armor, and 14 draft schematics.
  - Interior layouts `bunker_blacksun_outpost.ilf` and `shared_association_hall_style_naboo2.ilf`.
- **Client UI and input.**
  - `ui/ui_auction.inc`, `ui_backdrop_default.inc`.
  - `ui_avatardata.inc`, `ui_planet_map.inc`, `ui_ticketpurchase.inc` (all three staged by the chain).
  - 11 input maps, `scene/game_music_manager.iff`.

## Risks and things to check

1. **The existing merge changes the server's mount training.** By this audit's rules, 3 of the original 5 files are `mtg_changes`. The merge does not apply MTG's edits, but it does add rows the server reads.
   - Besides vehicles (40 pv_/pvp_ rows, podracers, the Grievous wheel bike ...), `valid_scale_range` gains rows for creatures: nerf_hue, tauntaun_hue, varactyl, bolotaur and kashyyyk_bantha.
   - With them, those creatures pass `isValidMountScale` on the test galaxy, if their template has a `rider` slot (`checkMountEligibility`).
   - The nerf is inconsistent: it now has a scale row, but `logical_saddle_name_map` keeps stock's `x` (no saddle) for nerf_hue. MTG's copy gives it `lookup/mnt_saddle_body2_medium_s01`.
   - MTG also edits bantha_hue's minimum scale (0.6 → 0.5). The stock 0.6 is kept.
   - MTG's own copies repeat rows: 9 duplicate rows in valid_scale_range and 3 in logical_saddle_name_map; saddle_appearance_map and rider_pose_map also repeat whole rows. The merge keeps the first row for each key.
2. **Lower MTG copies add what MTG's own top copy lacks.** `MTG_COPIES` is read in full, as the original merge did. In MTG's own client the top copy wins wholesale, so these entries were invisible there too:
   - `creature_names.stf`: 286 names from 013 that 023 lacks.
   - Planet CRCs: 11 from 019 and 3 from mtg_planets.
   - faction_names: 2 from mtg_planets.
   They are all names and strings, so they are inert unless something references them.
3. **Server strings database.** The new strings reach Core3 only after `reloadstrings` or `Core3.TreManager.ReloadStrings`.
4. **MTG species strings are merged, but their tables are not.** player_species, skl_n and skl_d gain about 14 MTG species, while attribute_limits, racial_mods, allow_bald and the customization tables stay skipped. The strings are inert until those tables are added. If a later species step adds its own text for one of those keys, it has to run before this step (it does in the current order).
5. **Live server not checked.** The test galaxy's archive list was taken from `test_galaxy.py`, which notes that live's config does not list `local_planets.tre`. The live config (`config-local.lua`) was not read, as instructed. The server-read list comes from upstream Core3, not the sandbox branch.
6. **`shadow-audit.json` is 7.1 MB**, mostly the 124,354 byte-identical names. The other big generated inventories are in `.gitignore`; this one could be ignored too and rebuilt with `shadow_audit.py`.
7. **Untested in game.** Nothing here was loaded by the client or the test galaxy.

## Files

- `MTG-merges/shadow_audit.py`: the audit, read-only.
- `MTG-merges/shadow-audit.json`: counts, decisions, the merge step's lists, a record for every non-identical file (class, archives, sizes, key, added, edited, samples, lower copies, chain comparison, server use, decision), and the identical file names.
- `MTG-merges/stage_mtg_merges.py`: `TABLES`, `STRINGS`, `CRC_TABLES`, `MTG_COPIES` (023, 022, mtg_planets, 019, 013) and `merged_files()`.
- `MTG-merges/build_mtg_merges_archive.py` and `checks.json`: the trial build, sha256 a241de9d…

## Claude's review and additions (15 Oct 2026, 04:4x)

- Reviewed `stage_mtg_merges.py` and `build_mtg_merges_archive.py`: every merge keeps the base's rows, strings and CRC entries; the CRC tables are written sorted (`write_cstb`); MTG's edits are never applied. Reproduced the trial build (a241de9d) before changing anything.
- Added the BARC rider fix as `WHOLE_FILES`: MTG's `appearance/lat/all_m.lat` replaces stock's (it adds `vehicle_barc_speeder` and 188 other names, drops four checked ones). The owner's BARC needed it to mount (`build_barc_ride_archive.py`, installed on the client as f7cc806f).
- Added top item 1: 35 of the 41 string files where MTG also edits stock strings (only the missing keys are added; the other six only edit). Empty placeholder copies in lower MTG archives are skipped.
- The chain now also stages the five Ossus NPC names (`Local-model-ossus-npcs/stage_npc_names.py`).
- Result: `local_planets-mtgmerge.tre` 8ad04fec, 119 merged files, 7,388 string keys added, `ok` and idempotent. Not installed yet: it goes in at the next test-galaxy restart. Items 2 to 5 stay open.
