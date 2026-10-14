# Fable: Hoth ice caves, staged port (14 Oct 2026)

Staged for Claude to review, apply to `/opt/swg/Core3-dev`, and test on the test galaxy. Nothing here has been loaded by Core3 or seen in game. Produced read-only from Bellum Gero's repository (read as text), MTG's `snapshot/hoth.ws` in the owner's client (read with our own reader) and Core3-dev's scripts (read with `cat`/`grep`). No git commands were run; `h/` is a git repo, Claude commits.

## Folder

| Path | What |
|---|---|
| `staged/MMOCoreORB/bin/scripts/screenplays/caves/hoth_ice_caves.lua` | the new screenplay, 129 spawns (new file) |
| `staged/MMOCoreORB/bin/scripts/screenplays/screenplays.lua` | Core3-dev's file with one `includeFile("caves/hoth_ice_caves.lua")` line added after `caves/endor_orphaned_marauder_cave.lua` (alphabetical, in the Caves block); LF endings kept, 37,798 → 37,880 bytes |
| `apply.sh`, `apply-manifest.tsv` | copies only when `screenplays.lua` still has sha256 `aeff5a52…` and the cave file does not exist yet; then `luac5.3 -p`. `--check` reports only (ran clean: 1 change, 1 new, 0 refused) |
| `checks.json`, `luac.txt` | the verification below |
| `tools/ws_read.py` (own `.ws` reader + verifier), `tools/stage_caves.py` (generator), `work/screenplays.lua.orig` (the Core3-dev original, for the diff) | |

Apply, as swgemu inside Debian: `bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-caves/apply.sh --check`, then without `--check`.

## Counts and checks

- **Source:** Bellum's `screenplays/caves/hoth_ice_caves.lua` (AGPL-3.0), 152 spawn rows in 5 caves, 73 distinct cell ids.
- **MTG snapshot (`snapshot/hoth.ws`, `mtg_planets.tre`):** 94 nodes, 17 at world level, read with `ws_read.py` following Core3's `WorldSnapshotIff`/`WorldSnapshotNode` layout. Every one of Bellum's 73 cell ids was checked: exists, is an `object/cell/shared_cell.iff` node, and its parent is the cave Bellum's comment names.
- **Kept 129 / skipped 23**, per cave:

| Building | Cave | Position in MTG's snapshot (x, y; height) | Bellum's comment | Cells | Kept | Skipped |
|---|---|---|---|---|---|---|
| 6452962 | `cave_04_ice_s01` | -385, 2436; 58.0 | matches | 6452963–6452973 (11) | 23 | 0 |
| 6452974 | `cave_02_ice` | -543, 2674; 36.5 | matches | 6452975–6452985 (11) | 23 | 0 |
| 6452986 | `cave_01_ice` | -622.5, 2292.3; 183.3 | matches | 6452987–6452997 (11) | 23 | 0 |
| 6452998 | `cave_03_ice` | -75, 2969; 35.0 | matches | 6452999–6453027 (29) | 60 | 0 |
| 6453174 | `cave_06_flatland_s01_ice` at -5819, 6093 | not in MTG's snapshot | – | 6453175–6453185 (11, all missing) | 0 | 23 |

- **Skipped spawns (all in the missing fifth cave):** 14 `hoth_ice_mynock`, 8 `hoth_greater_ice_mynock`, 1 `hoth_mynock_broodmother` (1800 s). Rows are listed in `checks.json` → `skipped_rows`, so the mynock den can be re-sited later (a `cave_06_flatland_s01_ice` building added to our snapshot, or outdoor spawns).
- **Templates:** the 7 used (`hoth_wampa`, `hoth_elder_wampa`, `hoth_wampa_frostfang`, `_icemaw`, `_matriarch`, `_patriarch`, `_snowblind`) and the 3 skipped ones are all registered in Core3-dev (`mobile/hoth/*.lua`, `CreatureTemplates:addCreatureTemplate`, included from `mobile/serverobjects.lua` line 14).
- **Respawn times kept:** 420 s, bosses 1800 s.
- **luac5.3 -p:** both staged files parse (`luac.txt`).
- **Floor check: skipped.** Whether each cell-local point sits near its cell's floor needs readers for the caves' `.pob` files (`thm_all_cave_s01_ice.pob`, `s02_ice`, `s03_ice`) and their `.flr` floor meshes (Core3-dev `src/templates/appearance/PortalLayout.cpp`, `CellProperty.cpp`, `FloorMesh.cpp`, `FLOR > 0003/0005/0006 > VERT, TRIS`); about half a day. The coordinates are Bellum's unchanged and the caves are SOE's standard ice caves, so the risk is low; a bot walk through one cave is the cheaper test.

## Boss loot: what was dropped, and the owner question

Bellum's bosses carried no corpse loot; on death every qualifying damager rolled `HOTH_CAVE_BOSS_LOOT` (15 groups) through their `WorldBossLootManager` and `giveHothBossRewards`, neither of which exists here. Both observers and the table are dropped; the five bosses keep the corpse loot of their mobile templates (dev b7f03b0e: `hoth_decor_rare` 5 %, `hoth_vehicle_deeds` 2 %).

| Bellum group (chance) | In Core3-dev? |
|---|---|
| armor_attachments (30 %), clothing_attachments (30 %), color_crystals (20 %), power_crystals (20 %), krayt_pearls (15 %) | yes, stock (`loot/groups/…`) |
| hoth_decor_rare (15 %), hoth_vehicle_deeds (10 %) | yes, ours (`loot/groups/hoth/`, with `hoth_decor_common`) |
| jedi_robe (5 %) | **not found** under `loot/groups/` (grep) |
| endgame_weapon_schematics (10 %), bg_token_group (25 %), hoth_snowtrooper_schematics (5 %), hoth_rebel_snow_schematics (5 %), hoth_paintings (25 %), hoth_ice_decor (20 %), hoth_art_rare (10 %), hoth_vehicle_schematics (15 %) | Bellum-only |

**Owner question:** keep corpse loot only (current staging), or build a per-player boss reward later (a small manager that tracks damagers in range and rolls a table into each inventory; the 7 groups we have could seed it)?

## Next: finishing Hoth, and the missing creatures (plan only)

What our Hoth has (hoth-port-log.md): terrain and snapshot (MTG), planet registration, travel, regions (edge no-build, outpost city, cave no-build, world spawner), 19 ordinary mobiles + 11 lairs + the `hoth_world` spawn group, the boss loot slice, and now the four wampa caves (staged). Compared with Bellum's and MTG's Hoth it still lacks:

1. **Spawn regions:** Bellum's region file has per-area spawn groups (tauntaun plains, mynock fields, scavenger and trooper zones) where ours has one world spawner; port the area split from `managers/planet/hoth_regions.lua` (Bellum) onto MTG's map, re-centring on our outpost at (0, -2000).
2. **POIs and NPC camps:** Bellum's `tools/newplanets/gen_hoth_pois.py` output (scavenger camps, Imperial and Rebel patrol camps, crash sites) sits at their moved outpost coordinates; re-site around MTG's starport, the debris field and the camp already in MTG's snapshot. The mynock den (23 spawns above) needs a home: add a `cave_06_flatland_s01_ice` building to our snapshot (a `.ws` writer is a small step on top of `ws_read.py`) or place them outdoors.
3. **Missions and reward chains:** `gen_hoth_missions.py` (kill/delivery chains) and `gen_hoth_loot.py` (the 8 Bellum-only groups: schematics, paintings, ice decor, art, vehicle schematics, tokens): write ours against the items we have; schematics and paintings need the client objects first (check `Fable-backport` tiers).
4. **Vehicles:** `gen_hoth_vehicles.py` (tauntaun mounts, snow speeders): client art is MTG's; server side is deeds + vehicle templates.
5. **Resources:** the resource manager hard-codes planet lists in C++ (log, step 3).
6. **Echo Base / Imperial base:** Flurry's screenplays (old AI API) and MTG has no base in the snapshot; a later slice.

**Creature types referenced without a Core3-dev template:** one, the **glacial rancor world boss** (`hoth_glacial_rancor`, Bellum; its body `object/mobile/shared_exotic_rancor.iff` is in no archive the client loads). All of MTG's Hoth creature bodies (wampa, snowtroopers, rebel snow soldiers) are already used by the ported mobiles; a diff of MTG's own server scripts (`work/research/mod-the-galaxy`) against ours was not run in this pass and is the first step of the creature audit. Clean-room rebuild per missing creature: pick a stock body from the client (`object/mobile/shared_*.iff`; for the glacial rancor `shared_rancor.iff` or `shared_mutant_rancor.iff` with a white `_hue` and `scale`), take level, HAM, damage, resists and XP from a comparable stock boss template (`mobile/dathomir/ancient_bull_rancor.lua`, the Core3 world bosses) scaled to the owner's chosen level (400), write our own name and description strings, loot from our groups, and spawn it from our screenplay; no Bellum stats or text copied. Any other gap found by the MTG diff follows the same recipe: client body present → our template; body absent → stock stand-in body, our template.

Part 2 (the Blender add-on study for F86) was not started, as instructed.
