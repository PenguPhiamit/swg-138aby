# C30 against the Ossus census

16 Oct 2026, 1:00 AM. Read-only check. Nothing under `/opt/swg` was written. C30 is the board row "six reviewed Ossus fauna + habitat spawns" (dev `80b66e65`, test galaxy since 15 Oct 2:03 AM). Its open item is "a bot visit to each habitat".

**Result: the open bot visit can be closed.** The explorers walked 97 to 100% of each habitat, every habitat holds exactly its expected creatures at the template levels, and nothing appears outside the habitats. What the census cannot show (fighting, loot, XP, display names) is listed at the end; none of it was part of the open item.

## What was compared

| Side | Source |
|---|---|
| C30 data | `managers/planet/ossus_regions.lua`, `mobile/spawn/ossus/*.lua` (3 groups), `mobile/lair/creature_dynamic/ossus/*.lua` (6 lairs), `mobile/ossus/*.lua` (6 creatures), all under `/opt/swg/Core3-dev/MMOCoreORB/bin/scripts/`. The test galaxy's copies are byte-identical to dev (`diff -rq`), and `git log` shows `80b66e65` as their last change. |
| Observations | `ossus-census.csv` (4,187 rows; 437 of them Ossus fauna; each name once per 256 m square, with level and x, y, z) and the coverage map in `ossus-census.md`. Runs 4 to 7, 10:11 PM to 12:20 AM. |
| Cross-check | The raw Ossus rows of the same runs up to 12:37 AM (explorer snapshots and sightings). It adds nothing new: the same six names, the same levels, 62 more squares. |

How the census sees: a creature counts when it is in the explorer's close-objects range (server side), so a row is "this name stood in this 256 m square", not a head count. The explorers also drag a droid (`helper_r2_unit`, 3,467 squares), and that droid is the best path trace: the planet has 4,096 squares of 256 m and the explorers stood in 3,467 of them. The `c` characters in the census map are mostly that droid, so I used droid squares as "walked".

## The data

Six creatures and the levels the Lua files give them: gokob 10, kaddyr bug 10, tribis 10, tree frog 6, kirruk 19, mud yak 19. Six dynamic lairs (`spawnLimit` 3 to 15, so 1 to 5 creatures each, four lives each). Three groups, every row `minDifficulty = maxDifficulty = 2`, which the new level gate (`10 + 3 x level`, at least 13) never blocks. Five habitat rows, all `SPAWNAREA` with no world spawner, plus no-spawn and no-build rows for the landing field, the academy ruins and the edges.

| Habitat (region row) | Shape | Table | Cap | Area |
|---|---|---|---|---|
| `ossus_adega_wetlands` | ring 650 to 1,050 m around (-3600, 1200) | `ossus_wetlands`: mud yak | 24 | 2.1 km2 |
| `ossus_forest_east` | circle 1,200 m at (1200, 5400) | `ossus_forest`: gokob 30, tree frog 25, tribis 25, kaddyr bug 20 | 32 | 4.5 km2 |
| `ossus_forest_southwest` | circle 900 m at (-3200, -3400) | `ossus_forest` | 24 | 2.5 km2 |
| `ossus_open_ground_west` | circle 1,200 m at (-4400, -1200) | `ossus_open_ground`: kirruk | 24 | 4.5 km2 |
| `ossus_open_ground_north` | circle 1,000 m at (-1500, 5200) | `ossus_open_ground` | 24 | 3.1 km2 |

No two habitats overlap. Together they cover 16.9 km2 of the planet's 268 km2 (6%).

## Seen or not, per creature and habitat

"Squares" are 256 m squares with a sighting of that name whose position lies inside the habitat shape. "Walked" counts squares whose centre is inside the habitat and that hold a droid sighting.

| Habitat | Walked | Creature | Seen | Squares | Levels seen | Expected | Where (first three) |
|---|---|---|---|---|---|---|---|
| Wetlands | 35 of 35 | mud yak | yes | 47 | 19 (all 47) | 19 | -2982/444, -3107/374, -2875/558 |
| Forest east | 68 of 70 | gokob | yes | 39 | 10 (all) | 10 | 1017/4270, 1032/4274, 1308/4373 |
| | | tree frog | yes | 26 | 6 (all) | 6 | 1603/4366, 358/4587, 238/4788 |
| | | tribis | yes | 39 | 10 (all) | 10 | 1216/4258, 1408/4498, 1864/4420 |
| | | kaddyr bug | yes | 29 | 10 (all) | 10 | 1360/4620, 1366/4598, 1374/4959 |
| Forest southwest | 41 of 41 | gokob | yes | 35 | 10 (34), 1 (1) | 10 | -2436/-3431, -2377/-3038, -2724/-3241 |
| | | tree frog | yes | 30 | 6 (all) | 6 | -2545/-3302, -2631/-2999, -2781/-4001 |
| | | tribis | yes | 30 | 10 (all) | 10 | -2452/-2914, -3086/-4184, -3224/-3325 |
| | | kaddyr bug | yes | 32 | 10 (31), 1 (1) | 10 | -2501/-3124, -2624/-3406, -2825/-3097 |
| Open ground west | 69 of 69 | kirruk | yes | 78 | 19 (76), 1 (2) | 19 | -3310/-1605, -3480/-1907, -3247/-1463 |
| Open ground north | 48 of 49 | kirruk | yes | 46 | 19 (all) | 19 | -1831/4425, -942/4395, -1080/4337 |

- **Habitats with nothing seen: none.** All 11 creature-in-habitat pairs are present, and no creature appears where its table does not list it.
- **Coverage.** The unwalked squares are three: (896, 5504) and (1152, 6528) in the east forest, (-1408, 5504) in the north open ground. Explorer snapshots in the raw logs (about one a minute per bot, so an undercount) show 97 different explorers in the wetlands, 76 in the west open ground, 62 in the southwest forest, 47 in the east forest and 44 in the north open ground.
- **Density.** Of the walked squares in each habitat, these held at least one of its creatures: wetlands 100%, southwest forest 98%, west open ground 97%, east forest 90%, north open ground 88%. The two northern habitats were reached last (first sightings at 10:52 and 10:53 PM against 10:34 PM in the southwest forest) and have the fewest visitors, which fits their lower share.
- **Boundaries hold.** Mud yaks stand 649 to 1,052 m from the lake centre, against a ring of 650 to 1,050 m, so the sunken basin stays empty. Forest and open-ground creatures stand at most 10 m outside their circle's edge. The 3,031 squares the explorers walked outside every habitat (300 m margin) hold no Ossus fauna at all, and none stand in the landing-field or academy no-spawn circles. This answers the Lua header's worry "habitat boundaries ... still need in-game verification".
- **Levels as expected.** 433 of 437 rows are at the template level. The four level-1 rows (gokob, kaddyr bug, two kirruk) are babies: all six templates have `tamingChance = 0.25`, a dynamic spawn makes about 5% of its creatures after the first into babies (`checkSpawnAsBaby`), and `loadTemplateDataForBaby` sets level to `level / 10`, minimum 1. The raw logs add three more babies (mud yak, tribis, kirruk) and no other deviation.

## What the census does not cover

- **Fighting.** Explorers never fight. Hit chance, damage against a low-level character, aggro (none of the six is aggressive: `pvpBitmask = ATTACKABLE`), loot, XP and the taming claim for the kirruk and others are untested.
- **Counts per lair and respawn.** The census is one row per name per square, so lives, herd size and respawn timing are unobserved.
- **Names.** The census prints template ids (`ossus_gokob`). Whether the client shows the intended names depends on the string table in the archive named on the board (`8ad04fec`); nothing here tested it.
- **The other 94% of the planet has no fauna by design** (habitat spawners only, no world spawner), and the weakest creature is the level-6 tree frog. A level 1 to 5 character on Ossus has only babies to hunt. That is a design fact for the owner, not a C30 defect.

## Proposed board wording

> C30 bot visit: done by the launch-simulation explorers (runs 4 to 7, 10:11 PM to 12:37 AM, 15 to 16 Oct): all five habitats walked (97 to 100%), all six creatures seen in every habitat that lists them at template levels, none outside, babies at level 1 as designed. Not covered: combat, loot, XP, display names. Report: `Bot-reports/launch-sim/c30-census-check.md`.

## How it was made

`ossus-census.csv` and `ossus-census.md` as above; geometry from the region rows read in WSL as `swgemu` (script in my temp folder, nothing written to `/opt/swg`); distances and squares computed with a short Python script over the CSV; the baby rule read from `CreatureManagerImplementation.cpp`, `DynamicSpawnObserverImplementation.cpp` and `CreatureImplementation.cpp` in `Core3-dev`; the gate from `SpawnAreaImplementation.cpp`.
