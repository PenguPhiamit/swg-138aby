# Ossus batch O2: snapshot, server Lua, resources (story-neutral)

Staged by Fable, 14 Oct 2026, in `Fable-ossus/o2/`. Our own code, data and text; stock art referenced by template
name only (the Hoth basis), nothing copied out of the owner's client, no Bellum or MTG material. Nothing applied to
`/opt/swg`. No Ysanna, Imperials or Jedi: ruins and fauna only, both of the owner's story options keep them.

Contents: `staged/client/snapshot/ossus.ws` (O2a), `staged/MMOCoreORB/bin/scripts/` (30 new Lua files) + `snippets/
planet_manager_ossus.lua` + `new-files.txt` + `patches.tsv` + `apply.sh` (O2b), `resources/` (O2c, data for Claude),
`checks.json` (hashes + every report + the dev check, dry run and self-test logs), `out/*.json`, `tools/`.

```
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o2/apply.sh --selftest   # every patch mode on scratch copies
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o2/apply.sh --check      # dry run (today: 30 copies, 5 patches, 0 refused)
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o2/apply.sh              # apply; luac5.3 on every touched file
sh   /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o2/tools/dev_check.sh    # read-only: templates, anchors, luac (0 problems today)
```

`apply.sh` is the batch C applier rebuilt after the IFS/tab bug: fields are split with parameter expansion (never
`read` with `IFS=$'\t'`), lines reach awk through `ENVIRON` (never `-v`, which re-processes escapes), every patch is
checked to have added lines before the file is replaced, and `--selftest` runs all four modes (after, before with a
tab-leading anchor, before-file, append, plus a backslash anchor) on scratch copies, compares the result with the
expected file and re-applies to prove idempotence (`work/selftest.txt`: PASSED).

## O2a: `snapshot/ossus.ws` (8,614 B, 87 nodes, 35 at world level, 20 templates)

`tools/ws_write.py` writes the format Core3 reads (`WorldSnapshotIff.cpp`); byte-identical round trips of MTG's
`hoth.ws` (94 nodes) and the stock `dantooine.ws`, `yavin4.ws`, `tatooine.ws` (16,514 nodes). Conventions read from
those files: a building node carries 512 and the CRC chunk of its portal layout (`.pob`) in the last field, with one
child cell node per interior cell; statics carry the value stock snapshots use for the same template; quaternion
`(cos h/2, 0, sin h/2, 0)` for a yaw, yaw 0 = the building's +z faces north. Object ids 6900000-6900086, a range no
snapshot the client loads uses (all 29 scanned).

| Piece | Template(s) | Placement (from `../out/ossus-sites.json`) |
|---|---|---|
| Knossa starport | `object/building/military/shared_outpost_starport.iff` (+1 cell) | pad centre (0, 50.3, -3600), yaw 180 like Hoth's; the landing pad falls at +20.3, +17.8, so the travel point is (20.3, 50.3, -3582.2); footprint 48 x 30 m inside the exactly flat 88 m; it spawns its own travel terminal, collector and shuttle (`outpost_starport.lua` childObjects) |
| Cave, west foothills | `shared_cave_01.iff` (`thm_all_cave_s01.pob`, 11 cells) | mouth at the terrain hole (-2976, -4960) facing north; origin 18 m behind at (-2976.3, 56.1, -4978.0); origin height = apron 51.9 + 4.16 so the entrance portal floor meets the levelled apron |
| Cave, east foothills | `shared_cave_03.iff` (`thm_all_cave_s03.pob`, 29 cells, same exterior) | mouth (4896, -4960), origin (4895.7, 62.6, -4978.0) |
| Cave, north hills | `shared_cave_02.iff` (`thm_all_cave_s02.pob`, 11 cells; its mouth sits at building-space (-17.4, 4.9)) | mouth (1376, 5920), origin (1393.4, 46.1, 5915.1) |
| Academy ruins (31 statics) | Dantooine Jedi temple main structure, altar, 11 pillars/bases/fallen pillars, 8 wall pieces; `poi_temple_ancient_ruined`; Gungan and Tatooine ruined walls and pillars as weathered outer courts | on the ruins pad (2016, 2848) within 104 m of the centre; heights 170.4-170.65 m from the terrain port |

Footprint checks (`out/snapshot-report.json`): every cave's exterior box (49 x 39 m, rising 9.4 m above the origin and
reaching 25 m below it) was rotated into the world and the terrain probed at its corners: ground sits -7.6 to +3.9 m
from the origin, inside the mesh's range, and the farthest corner is 33 m from the mouth (apron r 30, hole r 9).
The cave height rule was calibrated on Dantooine's stock janta cave (same `.pob`): its snapshot height is the mouth
ground + 8.9 with the origin 17 m under the hill behind, so "origin = mouth ground + portal floor offset" is the
conservative reading; the real client is the judge (owner question 3). `shared_poi_all_jedi_temple_ruined.iff` was
dropped: its `.pob` is not in the client archives. All 20 templates are in the merged object CRC table
(`Local-content/local_planets.tre`, 29,358 entries), in the client archives, and their server templates exist in
Core3-dev (`work/dev-templates.txt`, checked by `dev_check.sh`).

## O2b: server Lua (30 new files, 5 one-line patches)

- `snippets/planet_manager_ossus.lua`: the `ossus` block (weather, GCW, travel point "Knossa" at (20.3, 50.3, -3582.2),
  nav area over the pad), inserted before `tutorial = {`.
- `managers/planet/ossus_regions.lua`: the four edge no-build strips, Knossa (city r 200 + no-build r 320), no-spawn/
  no-build over the ruins (r 260), no-build r 120 at each cave, six spawn areas (plains west/north, forest east/
  south-west, highlands south, canyon country; 48-64 each) and the world spawner (1024).
- Fauna on stock bodies, `mobile/ossus/` (customName, no string file needed): gokob 22 / gokob scavenger 27 (womp rat
  body), tribis 28 / bull 34 (tybis), kaddyr bug 32 / soldier 40 (kliknik), kirruk 48 / alpha 56 (gurreck), Ossus bol
  30 / bull 36 (bol; the mount beast). Stats scaled from the stock bodies' templates; pet control devices where the
  stock creature has one. **Levels are a placeholder mid band 20-60** (owner question 1).
- Lairs: 5 with props (`mobile/lair/creature_lair/ossus/`: gokob den (warren), tribis lair (mound), kaddyr hive
  (insect hill), kirruk den (rock shelter/bones), bol lair (rocks)) and 5 dynamic herds/packs
  (`creature_dynamic/ossus/`, each with a mission building so destroy missions can use them later).
- Spawn groups `mobile/spawn/ossus/`: `ossus_plains`, `ossus_forest`, `ossus_highlands`, `ossus_canyon`, `ossus_world`.
- Patches: one include line each in `mobile/serverobjects.lua`, the two lair list files and `mobile/spawn/
  serverobjects.lua` (all after the Hoth lines), plus the planet block. Anchors occur exactly once in dev today.
- Checks: luac5.3 on all 31 files (`work/dev-check.txt`), every stock body, PCD and lair prop has a server template,
  no `ossus_*` name is taken, the regions file and planet block are free, dry run refuses nothing.

Not staged (needs the test galaxy): `ossus` in `ZonesEnabled`, which Claude's `test_galaxy.py` handles.

## O2c: resources (`resources/`, data for the archive builder)

- `activeZones.txt`: append `,ossus` to `managers/resource_manager.lua` line 49.
- `ossus_resource_rows.tsv` / `.json`: 45 rows cloned from Dantooine's (Dantooine's and Endor's native sets are
  identical: milk 2, meat 8, seafood 3, bone 3, hide 4, grains 8, vegetables 4, fruit 3, wood 3, fiberplast, water
  vapour, energy 5), each inserted right after its sibling with ENUM `<type>_ossus` and name "Ossus ..." (the
  stock Dantooine rows use the planet name, not an adjective).
- `resource_tree_with_ossus.iff`: the stock tree (725 rows, round-trips) with those rows and the ancestors' type
  counts raised, 770 rows; it re-reads and round-trips. The count rule was checked against Claude's Hoth merge:
  organic 390 -> 428, creature_resources 206 -> 226, creature_food 133 -> 146, milk_domesticated 10 -> 11 are the
  same for both planets (resource 545 -> 590 here vs 597 for Hoth's 52; energy 55 -> 60 vs 57, MTG's set lacked three
  energy types). Claude merges it with the Hoth rows in his builder as agreed.
- `resource_names.tsv`: the 45 display names, in case the merged `resource_names.stf` needs them (MTG named Hoth's).

## What only the test galaxy and the real client can show

Server: the zone boots with the regions file, the travel point lands on the pad, snapshot objects load (87 nodes,
the three caves' cells), spawn areas populate. Client: the caves sit right on their aprons and the mouths open
at the holes (the height rule above), the ruins read as a field, the starport draws on the pad.

## Owner questions

1. Fauna level band: 20-60 as placed, or lower/higher (Dantooine runs 10-60, Hoth 62-115)?
2. Creature names (gokob, tribis, kaddyr bug, kirruk from the asset plan; "Ossus bol" for the mount beast): keep?
3. Caves: `cave_01`/`cave_03`/`cave_02` on the three hillsides, or the self-contained `flatland` variants on flat
   ground (bigger mounds, 56 x 79 m)? The first client look decides the height rule.
4. Ruins: Dantooine Jedi temple pieces around `poi_temple_ancient_ruined`, with Gungan/Tatooine ruined walls as older
   outer courts. Enough, or a crater/scorched version too (that would signal the Massacre at Ossus, 130 ABY, when the academy fell)?
5. Knossa no-build 320 m and the ruins no-build 260 m: fine for player housing later?
