# Spawn review: what killed new characters near the starting cities

15 Oct 2026. Read-only review of the Core3-dev spawn data and code against the launch-simulation logs (runs 2 and 3). Nothing under `/opt/swg` was written. Every recommendation below is **untested**.

Path shorthand used throughout:
- `S/` = `/opt/swg/Core3-dev/MMOCoreORB/bin/scripts/`
- `C/` = `/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/`
- Regions: `S/managers/planet/<planet>_regions.lua`. Spawn tables: `S/mobile/spawn/<planet>/<table>.lua`. Lairs: `S/mobile/lair/<creature_lair|creature_dynamic|npc_dynamic|npc_theater>/<planet>/`. Creatures: `S/mobile/<planet>/<name>.lua`.
- Dev head when I read it: `41764180`. The test galaxy's copy of the spawn files (`managers/planet`, `mobile/*`, `screenplays/cities|static_spawns|poi`) is identical to dev (`diff -rq`, no differences). `git log` on these paths shows only the upstream merge `403893d9`, so the data is unmodified Core3 as far as this tree's 100-commit history can tell.

## 1. Result in brief

- **Outliers are a quarter of all deaths, not the main problem.** Run 2: 1,011 of 4,013 deaths (25%). Run 3: 385 of 1,634 (24%). The 14 creatures reviewed here cause 582 of the 1,011 (58%) and 248 of the 385 (64%). The single biggest killer is the plain nightspider (level 7): 347 deaths in run 2, 96 in run 3. It comes out of the same pack as the spitter (section 3.3).
- **The spawn code never looks at the player's level.** A hunter in an area rolls that area's table by weight alone. `minDifficulty` and `maxDifficulty` only size and toughen the lair. A level-1 character in a "hard" rectangle gets hard lairs (section 2).
- **Areas stack.** A starting city sits inside its own newbie rings and also inside one or two huge "hard" rectangles that cover it completely. Each area rolls its own table. A no-spawn ring is not usable as a fix, because `NOSPAWNAREA` blocks every area, the newbie ones included.
- **Why 350 to 1,000 m:** that is the simulation's hunting ring (it starts at the city edge and widens), not a spawn rule. The spawn rule is "anywhere in the area".
- **Nine of the 14 come only from table rows with `minDifficulty` of 15 or more.** One small level gate in `SpawnAreaImplementation::tryToSpawn` would remove all nine (section 4). That is a C++ change in the engineering slice, so it needs the lock holder and a cross-review.
- **Five need data edits:** spineflap soldier, nightspider poison spitter and foaming vynock (their rows have difficulty 1 to 15 but contain level 11 to 14 creatures), the Restuss swamp rats (a scripted camp inside the town), and, optionally, the rogue bageraset.
- **Kills collapsed in five cities most likely because the only sustained supply there is the lair and pack stock, and it is thin.** The cities that hold up have 40 to 200 scripted low-level critters with a 300 s respawn inside or beside town. Coronet, Tyrena, Dearic and Nashal have none that a level 1 to 3 character can fight. Talus has 8 low-level lair templates against 33 on Naboo (section 5).
- **Could not verify:** terrain coverage, a live lair census, and the cause at Kaadara (section 6).

## 2. How spawning works here, and what that means

| # | Fact | Evidence |
|---|---|---|
| 1 | Spawn areas are the `SPAWNAREA` rows of `<planet>_regions.lua`: name, x, y, shape, flags, tables, **cap**. There is no `managers/spawn_manager/` folder in this tree. | `C/managers/planet/PlanetManagerImplementation.cpp:938-1094` |
| 2 | An area rolls when a player inside it moves. At most one lair per area every 5 s (setting `minimumLairSpawnInterval`, default 5000 ms), and only while its live count is below its cap. | `C/objects/region/SpawnAreaImplementation.cpp:46, 203`; `src/conf/ConfigManager.h:736-745` |
| 3 | The table row is picked by weight alone. | `SpawnAreaImplementation.cpp:210-224` |
| 4 | The player's level only feeds `lairBuildingLevel` (1 to 5): the lower the player is against the row's difficulty, the smaller the lair. It never excludes a row. The creature's level comes from its own template. | `SpawnAreaImplementation.cpp:284-319`; `C/managers/creature/CreatureManagerImplementation.cpp:140, 160` |
| 5 | The lair or pack appears about 32 to 160 m from the player, inside the same area (192 m is the close-object range). Not allowed inside a city region or any `NOSPAWNAREA`, a no-build object zone, water, or ground steeper than 15 m over 20 m. | `SpawnAreaImplementation.cpp:132`; `C/ZoneServer.idl:129`; `PlanetManagerImplementation.cpp:1311-1353` |
| 6 | A zone-wide **world spawner** (`<planet>_world`, cap 2048) rolls for every player everywhere, except inside `NOWORLDSPAWNAREA` zones. Naboo's city `*_nobuild_1` areas (640 to 1,200 m) carry that flag. The Rori and Talus newbie areas and the Bela Vistal, Coronet and Doaba Guerfel rings carry it themselves (Kor Vella and Tyrena do not). | `C/GroundZoneImplementation.cpp:259-277`; `naboo_regions.lua:100-104` |
| 7 | **Lair** creatures come back 120 to 240 s after dying, but every respawn after the first wave damages the lair until it dies and frees its cap slot. **Dynamic "none" spawns** (packs, herds, flights) give each creature 4 lives, respawn after 60 + 2 x level s, then despawn. A dynamic spawn holds about 5 to 6 creatures. Lairs also despawn when no player is in range. | `C/managers/creature/LairObserver.idl:26-27`; `LairObserverImplementation.cpp:632, 774-787`; `DynamicSpawnObserverImplementation.cpp:29-30, 74, 90-92`; `CreatureManagerImplementation.cpp:150` |
| 8 | **Scripted (static) spawns** in `screenplays/` respawn on a timer (300 s in nearly all city files) with no player trigger. | `S/screenplays/cities/*.lua`, `S/screenplays/static_spawns/*.lua` |
| 9 | The 1,500 launch bots ran in `all` mode, so they count as players for spawn areas. (`throttled` bots are skipped at `SpawnAreaImplementation.cpp:36-38`.) | `config-local.lua` in the test galaxy: `Core3.BotPopMode="all"`; `C/managers/botpop/BotPopManager.h:811` |
| 10 | A bot only attacks creatures up to level + 4 + level/2 (level 1: 5, level 2: 7, level 3: 8). Its hunting ring is city radius + 40 m to city radius + 40 m + `huntRadius` (400 m at the start, +500 m after every 5 idle minutes, to 3,000 m). | `C/managers/botpop/BotPopLaunchBrain.h` (`launchFindTarget`: `maxLevel`; the hunting loop: `huntRadius`, `reach`); `BotPopLaunch.h:131`. Line numbers drift while the lock holder edits these files. |

What follows from this:

1. **Fact 10 is the whole "350 to 1,000 m" band.** Bots start at the town and look outward from the city radius. A starting city's own no-spawn region is only the town (for example Moenia r 336 m, `naboo_regions.lua:95`; Dearic r 400 m, `talus_regions.lua:191`), so lairs start right outside it.
2. **Fact 3 and 4 explain every outlier.** A newbie table can hold a flight of level 14 soldiers at 6.6% of its rolls. A hard rectangle holds queens and dragonets at 3 to 40% of its rolls. Both spawn next to a level-1 character.
3. **Unhunted lairs probably fill caps** (fact 2 plus fact 10: bots skip anything above their reach, nobody clears it, and a full area stops spawning). This is a plausible mechanism for the collapse, not something I measured (section 6).
4. **Bot-side numbers are not live-player numbers.** 83 hunters per city is far more than a friends' launch. The findings matter for the ambient bots (B3), not for a handful of real players.

## 3. The 14 creatures

Deaths are outlier deaths (killer level 8 or more above the bot), run 2 / run 3, from `analysis.json`. "Min diff" is the lowest `minDifficulty` among the rows that spawn the creature in the areas where it killed. Death coordinates are the median of the 500 m cell with the most deaths, from `botpop-launch-run2.jsonl` and `run3.jsonl`. The "nearest city" in `analysis.json` is the bots' home city; where the creature killed bots from another city, the nearest city to the death spot is what I give.

### 3.1 Summary

| Creature (level) | Deaths | Comes from | Min diff | Recommendation |
|---|---|---|---|---|
| spineflap soldier (14) | 82 / 40 | Naboo newbie tables, line 39 and 102 | 1, 9, 5, 10 | **Lower the level** (swap the flight template, 1 line) |
| nightspider poison spitter (11) | 86 / 35 | Naboo and Rori newbie tables | 1 | **Lower the level** (newbie pack without spitter and aggressor) |
| foaming vynock (14) | 42 / 12 | Dearic and Nashal newbie tables | 9 | **Lower the level** (replace 2 rows in 4 tables, make the medium area a ring) |
| swamp rat (10) | 29 / 29 | Restuss script, plus Naboo swamps | script / 5 | **Move** the two Restuss camps out of the town |
| rogue bageraset (13) | 15 / 12 | 5 medium and hard areas, 0.6 to 5.6% | 5 to 25 | **Keep** as a warning (rare, spread thin) |
| dragonet (29) | 48 / 16 | Tatooine `north_eastern_krayt_background` | 20 | **Move the area** (one number), or the gate |
| spineflap guard (18) | 42 / 8 | Naboo and Rori hard rectangles | 40 to 75 | **Keep** as a warning, the gate covers it |
| devil gulginaw (18) | 57 / 19 | Talus `southern_easy` and the Nashal forests | 40 to 50 | **Gate** (no-spawn by level) |
| savage humbaba (24) | 44 / 15 | Talus `grasslands_1` and `prairie_1` (duplicates) | 25 to 45 | **Gate**; also remove one duplicate area |
| greater desert womp rat (22) | 34 / 24 | Tatooine `mos_eisley_se_hard`, `plateau` | 15 to 36 | **Keep** as a warning (gate covers it) |
| corellian butterfly warrior (14) | 29 / 4 | Corellia `northwestern_medium`, `grassland1` | 30 to 75 | **Keep** as a warning (same family the bots farm) |
| mauler (16) | 26 / 21 | Naboo hard rectangles, `southeast` | 30 to 75 | **Gate**; Moenia data fallback given below |
| mauler apprentice (12) | 23 / 6 | Naboo hard theaters | 20 to 35 | **Keep**, the gate covers it |
| noxious vrelt scavenger (10) | 25 / 7 | Corellia mountains, `grassland1` | 30 to 50 | **Keep** (only 9 above a level-1 bot) |

"Keep" means no data edit. If the gate in section 4 is adopted, the nine creatures that come only from rows with difficulty 15 or more also stop spawning near level 1 to 3 characters. Without the gate, "keep" means a deliberate warning that the numbers show is cheap (few deaths) or already rare.

### 3.2 Naboo and Rori

**spineflap soldier (level 14, aggressive pack, 2,000 HAM, damage up to 160)**
- Lair: `naboo_capper_spineflap_flight_neutral_none` (`S/mobile/lair/creature_dynamic/naboo/...flight_neutral_none.lua:2`, `{{"spineflap_soldier",1}}`, limit 15, so about 5 soldiers per flight). **Rori's own flight uses `capper_spineflap`, level 6** (`rori/rori_capper_spineflap_flight_neutral_none.lua:2`). The pod and drone rows in the same Naboo tables are level 6 too.
- Rows: `S/mobile/spawn/naboo/naboo_{keren,moenia,theed,beachtown,deeja}_easy_newbie.lua:39` (35 of 530 = 6.6%, difficulty 1 to 8) and the `_medium_newbie.lua:102` rows (35 of 580 = 6.0%, difficulty 9 to 15). The northern rectangles add 3 to 4% (`naboo_northern_plains.lua:210`, `naboo_hard_capper_spineflap_nw.lua:12`, difficulty 5 to 10).
- Areas: `naboo_regions.lua:109` Kaadara easy (circle r 1,300, cap 64), `:111` Keren, `:113` Moenia, `:115` and `:116` Theed (two circles r 1,750, cap 32 each). Medium rings `:110, :112, :114, :117`. Big rectangles `:120` northeast, `:121` northwest, `:165` plains_1.
- Where: Moenia (4587, -4435), 355 m; Keren (1240, 1867), 946 m and (1732, 1914), 830 m; Theed (-5111, 4890), 655 m; Kaadara (4868, 6865), 361 m. Run 2 median 914 m from the nearest city.
- Why it is there: it is inside the easy circle. The row is a data slip: a "difficulty 1 to 8" row that holds level 14 creatures.
- **Recommendation: lower the level.** Change `naboo_capper_spineflap_flight_neutral_none.lua:2` to `{{"capper_spineflap",1}}`, as Rori does. Soldiers stay in `naboo_capper_spineflap_nest_neutral_large` (gatherer 9 + soldier 14, difficulty 40 to 45) in the hard rectangles. Check with a grep that nothing else wants the soldier flight; every user I found is a Naboo spawn table.

**spineflap guard (level 18, aggressive, 4,100 HAM, damage up to 180)**
- Lairs: `naboo_capper_spineflap_escort_neutral_none` and `..._hive_neutral_large`: queen 19 + 2 handmaidens 15 + 3 guards 18.
- Rows (all difficulty 40 to 75): `naboo_hard_capper_spineflap_nw.lua:3, :21`; `naboo_northern_plains.lua:282, :327` (35 + 35 of 1,261); `naboo_medium_tusk_cat_ne.lua:336, :372`, `_nw.lua:336, :372`; `naboo_hard_veermok_ne.lua:246, :291`; `naboo_medium_ikopi_ne.lua:372`. Rori: `rori_northeastern_medium.lua:255` (15 of 465, difficulty 40 to 60).
- Areas: `naboo_regions.lua:120, :121, :165` (3.3 to 5.7% of rolls). Rori `rori_regions.lua:103`.
- Where: Kaadara (4982, 6452), 323 m (12 deaths); Keren (2517, 2271), 1,013 m; run 3 Theed (-6230, 4678), 1,057 m; Restuss (6125, 6842), 1,414 m.
- Why: the rectangles cover Theed, Keren and Kaadara completely.
- **Recommendation: keep as an intended warning.** It is the queen's court of a hard encounter, 3 to 6% of rolls in hard areas, 42 and 8 deaths. The gate (section 4) removes it from level-1 characters anyway.

**nightspider poison spitter (level 11, aggressive, 810 HAM, damage up to 140)**
- Lair: `naboo_nightspider_pack_neutral_none` (nightspider 7, aggressor 9, **spitter 11**, about 5 creatures). Rori: `rori_nightspider_pack_neutral_none` (2 x nightspider, aggressor, spitter). Boss lairs (difficulty 25+) add a king.
- Rows: Naboo `..._easy_newbie.lua:102` (35 of 530) and `..._medium_newbie.lua:12` (35 of 580), difficulty 1 to 15. Rori `rori_narmle_easy_newbie.lua:39` and `rori_restuss_easy_newbie.lua:39` (50 of 600 = 8.3%, difficulty 1 to 500), and the two medium tables at `:39`.
- Areas: Naboo `:107-117`; Rori `rori_regions.lua:95-98` (circles r 1,400, cap 64).
- Where: Moenia (4262, -4678), 526 m and (4320, -4281), 646 m; Theed (-5550, 3853), 492 m; Keren (2518, 3053), 956 m; Narmle (-5443, -2864), 631 m; Restuss (6029, 5477), 739 m.
- **Recommendation: lower the level.** Add `naboo_nightspider_pack_newbie_neutral_none` = `{{"nightspider",1}}` and point the 10 Naboo newbie rows at it. On Rori point the four rows at the existing `rori_nightspider_lair_neutral_small` (level 7 only). This also thins the level 7 nightspider, the biggest single killer, though it stays aggressive.

**mauler (level 16) and mauler apprentice (level 12)** - hostile NPC thugs, not animals
- Lairs: `naboo_mauler_roamers_neutral_none` (`npc_dynamic`, limit 9), `naboo_mauler_conclave_neutral_large_theater` (lord 27, 2 maulers, veermok), `mauler_gang` (12 to 54), `naboo_mauler_sect_neutral_medium_theater` (apprentice only). All in `S/mobile/lair/npc_*/naboo/`.
- Rows: `naboo_southeast.lua:3, :12, :21` (mauler rows 45 of 225 = **20%** of that table, difficulty 30 to 40); `naboo_northern_plains.lua:102, :120`; `naboo_hard_mauler_nw.lua:3, :12, :30`; `naboo_medium_tusk_cat_nw.lua:84, :138, :165` and `_ne`; `naboo_hard_veermok_ne.lua:66, :102, :129`. Apprentice shares are 1.7 to 2% in the north, 6.7% in `southeast` (via `mauler_gang`).
- Areas: `naboo_regions.lua:124` `southeast` (rect (2800,-7620) to (7630,-1940), 27 km2, cap 32; Moenia is in its middle), and `:120, :121, :165` for Kaadara, Theed and Keren.
- Where: Kaadara (5481, 6689), 291 m; Moenia (5253, -5059), 571 m (8 deaths) and (4204, -4984), 635 m; Theed (-4484, 4654), 875 m; apprentice Theed (-4456, 4283), 806 m and Keren (1877, 2006), 775 m.
- The mauler stronghold (`S/screenplays/poi/naboo_mauler_stronghold.lua:41-61`, around (2900, 1100)) is more than 1,400 m from Keren and is **not** the source.
- **Recommendation: mauler, the gate** (every row is difficulty 30 or more). A data-only fallback for Moenia: replace `southeast` with four rectangles around a 1,500 m hole: (2800,-7620)-(7630,-6229), (2800,-3229)-(7630,-1940), (2800,-6229)-(3286,-3229), (6286,-6229)-(7630,-3229). **Apprentice: keep**, the gate covers it.

**swamp rat (level 10, NPC thug)**
- Restuss: `S/screenplays/cities/rori_restuss.lua:284-289` (6 rats, (4937 to 4947, 5752 to 5762), about 384 m west of the centre) and `:305-310` (6 rats, (5623 to 5633, 5662 to 5672), about 310 m east). Respawn 300 s. **Both camps are inside Restuss's 700 m city circle** (`rori_regions.lua:91`). Deaths: Restuss (4931, 5766), 396 m (13) and (5631, 5657), 313 m (8) in run 2; 20 more in run 3.
- Naboo (Moenia): `naboo_southeast_swamp.lua:183, :192` (10 of 1,121 = 1.8%, difficulty 5) through `swamp_1` (`naboo_regions.lua:155`, circle r 1,840, cap 32) and `gallo_jungle_2` (`:163`). Where: Moenia (5442, -4605), 667 m; 17 deaths over both runs.
- **Recommendation (Restuss): move.** Put both camps at least 1,000 m from (5318, 5680), or cut each to two rats. The same function also places gundark camps (levels 6 to 9) and garyn's prowlers (11) at 150 to 400 m; they did not reach the outlier list but belong to the same decision. **Moenia swamp rats: keep.**

### 3.3 Talus

Talus's easy and medium newbie tables are the same table (500 weight, difficulty 9 to 15), and only 30% of its rolls hold a creature a level 1 to 3 bot may attack (paralope 6, fynock 7).

**foaming vynock (level 14, aggressive killer, 1,500 HAM, damage up to 180)**
- Lairs: `talus_foaming_vynock_lair_neutral_medium`, `talus_foaming_vynock_pack_neutral_none`.
- Rows: `talus_{dearic,nashal}_{easy,medium}_newbie.lua:57, :66` (50 + 50 of 500 = **20%**, difficulty 9 to 15). `talus_northeast_forest.lua:174, :183` (60 of 1,510).
- Areas: `talus_regions.lua:198` Dearic easy (circle r 800, cap 64), `:199` Dearic medium (**circle** r 1,500, cap 64), `:200` Nashal easy (r 750), `:201` Nashal medium (**circle** r 1,500). The medium areas are full circles, not rings, so the inner 800 m rolls the same table twice.
- Where: Nashal (3877, 5029), 518 m; Dearic (157, -3471), 536 m and (417, -2349), 655 m. All 42 and 12 are outliers.
- **Recommendation: lower the level.** Replace the two vynock rows (and the vynock 9 and song rasp 10 rows, which bots cannot attack) in the four tables with the low templates Talus has: `talus_fynock_youth_lair_neutral_small` (5), `talus_fynock_lair_neutral_small_01` (7), `talus_paralope_lair_neutral_medium` (6), `talus_paralope_herd_neutral_none` (6), `talus_dung_mite_lair_neutral_small` (7). Change `:199` and `:201` to `{RING, 800, 1500}` and `{RING, 750, 1500}`.

**devil gulginaw (level 18, aggressive killer, 2,900 HAM)**
- Lairs: `talus_devil_gulginaw_flight_neutral_none`, `..._nest_neutral_medium`.
- Dearic: `southern_easy` (`talus_regions.lua:207`, rect (-2009,-6675) to (2990,-1020), 28 km2, cap 32). Row `talus_southern_easy.lua:39, :48` (30 of 240 = 12.5%, difficulty 40 to 50). Despite the name, **94% of that table is level 9 or higher.** Dearic is at least 1,984 m inside every edge.
- Nashal: `forest` (`:222`, circle r 3,200 at (4800, 4544), cap 128; Nashal is 836 m from its centre) and `forest_2` (`:224`). Row `talus_northeast_forest.lua:138, :147` (100 of 1,510 = 6.6%, difficulty 50).
- Where: Dearic (179, -2452), 603 m; (834, -3138), 433 m; (-150, -2554), 727 m; Nashal (4278, 4067), 1,180 m and (3971, 5296), 380 m.
- **Recommendation: the gate.** There is no cheap edit, because the rectangle surrounds the whole city.

**savage humbaba (level 24, aggressive herd, 6,800 HAM, damage up to 200)**
- Lairs: `talus_savage_humbaba_lair_neutral_medium`, `talus_savage_humbaba_herd_neutral_none`.
- Dearic: **two near-identical rectangles** `grasslands_1` (`:240`, 94 km2, cap 128) and `prairie_1` (`:246`, 105 km2, cap 256), both on `talus_central_plains` (`talus_central_plains.lua:219`, 50 of 1,815 = 2.8%, difficulty 25). A hunter there rolls the table twice. Nashal: `northeastern_medium` (`:204`), row `talus_northeastern_medium.lua:174` (15 of 390, difficulty 45 to 55).
- Where: Dearic (783, -2745), 444 m (23 deaths); (-209, -3197), 659 m; Nashal run 3 (4036, 5661), 520 m.
- **Recommendation: the gate**, and remove `grasslands_1` (`:240`), which duplicates `prairie_1` and doubles every Talus plains spawn over 94 km2.

### 3.4 Tatooine

**dragonet (level 29, aggressive pack and stalker, 8,200 HAM, damage up to 270)**
- Lairs: `tatooine_dragonet_lair_neutral_medium`, `tatooine_dragonet_pack_neutral_none`, a boss lair with an armodragon.
- Area: `north_eastern_krayt_background` (`tatooine_regions.lua:214`, rect (908, 930) to (7830, 5357), 30.6 km2, cap 256). Rows `tatooine_north_eastern_krayt_background.lua:12, :21` (15 + 15 of 75 = **40%**, difficulty 20 to 25). The rest of that table is giant sand beetles, level 25 to 30. **Mos Entha (about 1,340, 3,150) is inside the rectangle; its west edge is 436 m from the town centre.**
- Smaller source: `grand_arena` (`:252`, circle r 1,130 at (872, 5000)), `tatooine_northern_wasteland.lua:102, :111` (5.5%, difficulty 42+).
- Where: (2224, 3183), 880 m (15 deaths); (1923, 3354), 614 m; (1332, 2845), 304 m; (1122, 4433), 1,303 m; run 3 (1292, 3664), 517 m. The other 42 run 3 dragonet deaths came from level-2 dragonets (probably babies), which are not outliers.
- Why: the rectangle is the whole north-east, so the dragonets start at the first block outside the town.
- **Recommendation: move the area.** Change the west edge of `:214` from x = 908 to about 3,000 (1,650 m from Mos Entha). One number. It still covers Mos Taike's hinterland, which has its own newbie rings (`tatooine_regions.lua:210-211`).

**greater desert womp rat (level 22, aggressive pack and stalker, 5,900 HAM, damage up to 220)**
- Lairs: `tatooine_greater_womprat_lair_neutral_medium`, `..._herd_neutral_none`, `tatooine_greater_desert_womprat`.
- Areas: `mos_eisley_se_hard` (`:200`, rect (-2909,-7700) to (7841, 930), 92.8 km2, cap 256), rows `tatooine_mos_eisley_se_hard.lua:3, :12` (30 of 255 = 11.8%, difficulty 15 to 20). `plateau` (`:241`, rect (-1408,-7088) to (7760, 1376), cap 256), four tables, womp rat rows in `tatooine_easy_criminals_se.lua:84, :93`, `tatooine_easy_militia_se.lua:48, :57`, `tatooine_easy_villiages_se.lua:66, :75` (110 of 1,216 = 9%, difficulty 25 to 36).
- Why near Anchorhead: the town's newbie areas are tiny. Easy circle r 500 (`:193`, cap 64), then a medium ring 500 to 900 m (`:194`) whose table (`tatooine_anchorhead_medium_newbie.lua`) is **100% level 10 to 12** (zucca boar, scyk, cu'pa). Nothing in 500 to 900 m can be attacked by a level 1 to 3 bot, so they walk on into the two hard rectangles.
- Where: Anchorhead (-97, -5445), 167 m (7 deaths); (421, -5043), 488 m; Bestine (-630, -3709), 574 m; run 3 (-136, -5788), 473 m. Tatooine's share of fights that end in death is 0 to 2%.
- **Recommendation: keep as an intended warning.** 58 deaths over two runs on the gentle planet is cheap; the gate would remove most of the rows anyway (`mos_eisley_se_hard` rows start at 15).

### 3.5 Corellia

**corellian butterfly warrior (level 14, aggressive pack and herd, 1,200 HAM, damage up to 180)**
- Lairs: `corellia_corellian_butterfly_hive_neutral_large` (monarch + 3 warriors), `..._boss_01`, `corellia_corellian_butterfly_swarm_neutral_none` (monarch, 2 defenders, 3 warriors).
- Areas: `northwestern_medium` (`corellia_regions.lua:152`, rect (-7875, 8) to (-2090, 7870), 45.5 km2, cap 512), rows `corellia_northwestern_medium.lua:93, :102` (30 of 435 = 6.9%, difficulty 30 to 35). `grassland1` (`:169`, circle r 1,896 at (-4088, 3176), cap 192), rows `corellia_northwest_plains.lua:327, :345` (100 of 1,768 = 5.7%, difficulty 50 to 75). Kor Vella (-3420, 3146) is inside both.
- Where: Kor Vella (-3831, 2464), 796 m (9 deaths); (-4229, 3365), 838 m; (-4139, 2738), 826 m.
- **Recommendation: keep.** Kor Vella is the best-supplied city, and the bots' main food there is this butterfly family (drone 5, butterfly 7). The warrior is the adult of the same brood, and it caused 33 deaths over both runs.

**noxious vrelt scavenger (level 10, aggressive herd, 810 HAM)**
- Lairs: `corellia_diseased_vrelt_lair_neutral_boss_03, _04, small_02, _03, _04`.
- Areas: `mountain2` (`:179`, Bela Vistal, 5.4%), `mountain6` (`:183`, Doaba Guerfel, 7.8%), `grassland1` (`:169`, 4%), `forest2` (`:132`, 2.8%). Difficulty 30 to 50.
- Where: Bela Vistal (7213, -5900), 493 m and (6133, -6032), 718 m; Kor Vella (-3333, 2243), 907 m; Doaba Guerfel (3699, 6476), 1,178 m.
- **Recommendation: keep.** Level 10 is the smallest outlier (9 above a level-1 bot), and the gate removes the rows.

**rogue bageraset (level 13, aggressive killer, 1,200 HAM)**
- Lairs: `corellia_rogue_bageraset_neutral_none` (lair), `..._herd_neutral_none`.
- Rows: `corellia_eastern_medium.lua:192` (4%, area `:129`, covers Bela Vistal), `corellia_hard_crimson_sand_panther_sw.lua:30` (2%, area `:162`, covers Tyrena), `corellia_southern_central_easy.lua:129` (5.6%, area `:167`, covers Coronet), `corellia_hard_gronda_sw.lua:48`, `corellia_hard_gulginaw_sw.lua:75`, `corellia_northwest_plains.lua:12`. Difficulty 5 to 25.
- Where: Bela Vistal (7207, -5392), 533 m (6 deaths, run 3); Tyrena (-4907, -2013), 540 m; Kor Vella (-4267, 3472), 907 m.
- **Recommendation: keep.** 15 and 12 deaths spread over six areas at 0.6 to 5.6% each. Not worth an edit.

## 4. One code change that covers nine of them

Level gate in `C/objects/region/SpawnAreaImplementation.cpp`, after `minDifficulty` is read (about line 291):

```cpp
// skip table rows far above the player's level; unlisted levels keep today's behaviour
if (minDifficulty > 10 + 3 * playerLevel)
    return;
```

(`return` before `lastSpawn` is touched, so a skipped roll costs nothing and the next position update tries again.) The threshold is mine and needs tuning. I measured with a flat 14, which is what a level 1 character would get:

| Creature | Rows that pass a 14 gate | Why |
|---|---|---|
| spineflap guard, devil gulginaw, dragonet, savage humbaba, greater desert womp rat, corellian butterfly warrior, mauler, mauler apprentice, noxious vrelt scavenger | **0%** | every row is difficulty 15 or more |
| spineflap soldier | 59% | newbie flight rows (1, 9) and hard rows with 5 or 10 |
| rogue bageraset | 82% | rows with 5 and 10 |
| foaming vynock | 86% | the newbie rows (9) |
| nightspider poison spitter, swamp rat | 100% | newbie rows (1) and swamp rows (5) |

So the gate fixes nine and leaves five that need the data edits in section 3. It changes behaviour for live players too: a new character would no longer draw hard lairs in the city's hinterland. Grouped players use the group level (`getPlayerSpawnLevel`, `SpawnAreaImplementation.cpp:410-444`). Unmeasured side effect: fewer unhunted high-level lairs, so possibly less memory growth and more free cap slots (section 5). The owner and the lock holder decide; I did not write it.

## 5. Cities whose kills collapsed

Kills per 15 minutes, first to last window, from `analysis.json`. Run 2 is 165 minutes; run 3 is 78.

| City | Run 2 | Run 3 | Deaths / kills (run 2) | Bots that left ("nothing to hunt") |
|---|---|---|---|---|
| Coronet | 187 -> 20 | 276 -> 90 | 107 / 1,154 | 38 |
| Kaadara | 448 -> 25 | 262 -> 52 | 209 / 1,647 | 50 |
| Nashal | 154 -> 34 | 169 -> 26 | 336 / 484 | 40 |
| Tyrena | 137 -> 34 | 192 -> 36 | 104 / 797 | 45 |
| Dearic | 78 -> 32 | 183 -> 112 | 608 / 475 | 26 |
| *Kor Vella (holds)* | *717 -> 654* | *599 -> 543* | *182 / 6,982* | *6* |
| *Theed (holds)* | *159 -> 250* | *123 -> 141* | *381 / 2,017* | *0* |

What I found, in order of how well it is supported:

1. **The cities that hold have scripted critters in or beside town; the five that collapse mostly do not.** Counts are scripted creature spawns within 2 km that a level 1 to 3 bot may attack (levels up to 8), each with a 300 s respawn (about 12 kills an hour each):

| City | Low-level scripted creatures | Source |
|---|---|---|
| Mos Entha | 176 | `screenplays/cities/tatooine_mos_entha.lua` |
| Mos Espa | 129 | `tatooine_mos_espa.lua` |
| Kor Vella | 84 | `corellia_kor_vella.lua:468-557` (drone 30, minor gubbur 18, durni 12, paralope 12, vrelt 12, at 208 to 594 m) |
| Theed | 60 | `naboo_theed.lua:261-344` |
| Restuss | 62 | `rori_restuss.lua` |
| Narmle | 42 | `rori_narmle.lua` |
| Mos Eisley | 40 | `tatooine_mos_eisley.lua` |
| Kaadara | 36 (12 are nightspiders) | `naboo_kaadara.lua:238-299` |
| Bestine / Moenia / Keren | 32 / 13 / 10 | |
| **Coronet** | **0** | `corellia_coronet.lua` has no creature spawns |
| **Tyrena** | **0** | `corellia_tyrena.lua` has none |
| **Dearic** | **0** (16 creatures, all level 9 to 10) | `talus_dearic.lua:326-344` |
| **Nashal** | **0** (all level 9 to 10) | `talus_nashal.lua:289-299` |

   A scripted spawn gives at most 3 kills per 15 minutes. For Theed (60 spawns, 180 per 15 minutes), Restuss (62, 186) and Narmle (42, 126) the late kill rate is of that size. In the four zero cities the late rate settles at 20 to 35 per 15 minutes, which is what the lair and pack stock gives once the starting pile is gone. The match is rough: Keren (10) and Moenia (13) hold on far fewer scripts than that, so lairs matter there.
2. **Talus is short of low-level stock.** Lair and pack templates whose creatures are all level 8 or lower: Naboo 33 (17 kinds), Tatooine 25 (16), Corellia 21 (14), Rori 13 (11), **Talus 8 (6)**. The Dearic and Nashal bots killed essentially two things: paralope and fynock youth. At Dearic deaths (608) exceed kills (475); it is low from the first window (78) rather than collapsing.
3. **Coronet and Tyrena have thin rings.** Coronet: easy ring 581 to 1,000 m (`corellia_regions.lua:124`, 2.1 km2, cap 32), medium ring 1,000 to 1,500 m (`:125`, 3.9 km2, cap 32), then `southern_central_easy` (`:167`, 25 km2, cap 256, table 27% low-level). Nine of the twelve easy-table rows (75% of the weight) are dynamic spawns, which give each creature four lives and then despawn. Tyrena: rings 622 to 1,000 and 1,000 to 1,400 m (`:140, :141`, cap 256 each), under `southwestern_medium` and a r 3,000 hard circle. Its cap is not the limit, so the cap alone does not explain it. 67% of Coronet's early kills were one creature (corellian butterfly drone, 194 of 288 in the first 20 minutes).
4. **Kaadara is unexplained.** It has the same two rings as Keren and Moenia (`naboo_regions.lua:109-110` against `:111-114`), and Keren (10 scripted) and Moenia (13) hold. Kills are missing from the north-east octant, but empty octants also appear in healthy Moenia, so I cannot tie it to terrain.
5. **Cap fill by unhunted lairs** (section 2, point 3) fits all five and I cannot rule it out, but I have no lair census.

Recommendations, one each:

| City | Recommendation | Where |
|---|---|---|
| Coronet | **Raise density:** add about 60 scripted level 4 to 7 critters at 300 to 900 m (the Kor Vella block is the model), 300 s respawn. Raise the two ring caps from 32 to 64. | `corellia_coronet.lua`; `corellia_regions.lua:124, :125` |
| Tyrena | **Raise density:** the same scripted block. | `corellia_tyrena.lua` |
| Dearic | **Rebuild the easy tier:** easy table from the 8 low templates (section 3.3), scripted level 5 to 7 critters in town, medium area to a ring. Until then, send ambient bots elsewhere. | `talus_dearic_easy_newbie.lua`; `talus_regions.lua:198-199`; `talus_dearic.lua` |
| Nashal | **The same as Dearic.** | `talus_nashal_easy_newbie.lua`; `:200-201`; `talus_nashal.lua` |
| Kaadara | **Measure before editing.** Run `/spawnStatus` (read-only, already in the sandbox) at 0, 20 and 60 minutes. If the rings are not full, swap the 12 scripted nightspiders for chuba or gnort (levels 5 and 4). | `naboo_kaadara.lua:259-299` |

Bot cap until the supply is fixed: about 10 hunters per city for these five. At 19 kills per hunter-hour (`FINDINGS.md`), 20 to 60 kills per 15 minutes feeds 4 to 12 hunters; Kor Vella feeds more than 100.

## 6. What I could not verify

- **Terrain.** I could not measure water or steep ground inside the rings (rule 5 in section 2). The direction pattern of kills around Kaadara, Coronet and Tyrena is inconclusive (section 5, point 4).
- **A live lair census.** `/spawnStatus` and `/showSpawnRegion` exist (`C/objects/creature/commands/SpawnStatusCommand.h`) but nobody ran them during the runs, and the test galaxy is not mine to query. Cap fill is therefore a hypothesis.
- **Which area spawned a given killer.** The logs name the killer, not its lair or area. I matched the median death spot of the busiest 500 m cells to the areas containing it. A lair spawns up to about 160 m from the hunter, and creatures wander, so expect an error of a couple of hundred metres. Where several areas hold the creature I list them all.
- **Baby and low-level variants.** Some deaths in `deaths.json` have a killer level of 1 or 2 (baby dragonets, soldiers and so on). I report outlier deaths only.
- **Stock comparison.** The tree's history is 100 commits, so I cannot diff the spawn files against the original release.
- **Static spawn counts are minimums.** I parsed `spawnMobile(...)` lines with a fixed pattern; spawns made by other helpers in the same files are not counted.
- **The bot rules in fact 10** are read from the dev tree at `41764180`. The botpop files change while the lock holder works, so line numbers there will drift.
- **Everything here is untested.** None of the recommended edits was made or run.

## 7. How the numbers were made

- Logs: `/opt/swg/agent/logs/botpop-launch-run2.jsonl` and `run3.jsonl` (death, kill, travel and spawn events), read from inside WSL as `swgemu`.
- Spawn data: copied read-only from `/opt/swg/Core3-dev` into the scratch folder and parsed with small Python scripts (region rows, spawn tables, lair templates, creature levels, `spawnMobile` lines). They are in the session scratch folder (`.../scratchpad/spawnrev/`: `parse.py`, `report2.py`, `ring.py`, `static.py`, `gate.py`), not committed, not part of the repo.
- Cross-check: the outlier counts from my own pass over the logs match `analysis.json` (82 / 40 spineflap soldier, 86 / 35 spitter, and the rest).
