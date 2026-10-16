# Cities that run out of creatures: data-only proposals

16 Oct 2026, 1:10 AM. Read-only review; **nothing is applied**. Every diff below is against `/opt/swg/Core3-dev` at `74fa3e8c` (the dev head I read; the spawn files there are identical to the test galaxy's, `diff -rq`, and unchanged since `b20a46d7`). Every effect stated is **untested**: the table shares are arithmetic on the data, the kill figures are from the running simulation, and no edit has been run.

Path shorthand: `S/` = `/opt/swg/Core3-dev/MMOCoreORB/bin/scripts/`. Patches apply from `S/` with `patch -p1`. The full set is in `city-spawn-proposals.patch` (same folder as this file); it was dry-run and applied to a temporary copy of the live dev files (outside `/opt/swg`), and all 11 patched files pass `luac -p`. Not loaded by a server.

## 1. Result in brief

- **The five cities are not a special group in run 7.** In the last full 15-minute window (45 to 60 minutes) the five average 29 kills per city (1.4 per bot-hour). The other eight non-Tatooine cities average 21.5. The five Tatooine towns average 115 (5.5 per bot-hour). Kaadara, the odd one in the first review, is at 396 kills, 7th of 18, and shows no collapse now; the data fixes of `b20a46d7` seem to have settled it. Outside Rori, Coronet (159), Nashal (189) and Tyrena (199) have the fewest kills; Dearic (232) is above Keren and Theed.
- **Why Tatooine holds: it is the only planet with level-3 animals.** Kreetle and the Tatooine mynock (both level 3) are 46 to 70% of all kills in the five Tatooine towns. The weakest animal in a newbie table is level 4 on Corellia and Naboo, **5 on Talus and 6 on Rori**. A level 1 bot can attack up to level 5, and where the floor is 5 or 6 it dies often (Dearic 103 deaths for 232 kills, Restuss 140 for 150; Tatooine 13 to 23 deaths for 470 to 740). For a level 1 character the supply is the floor creature, not the table size.
- **A correction to the first review (spawn-review.md section 5).** It counted scripted critters near each city with a text search that included commented-out code. In this tree the creature blocks of Theed, Keren, Moenia, Kaadara, Mos Eisley, Mos Entha, Mos Espa, Bestine and Anchorhead are inside `--[[ ... ]]`; compiling the files with `luac` and looking for the creature names confirms it. **Active scripted critters within 2 km: Kor Vella 84, Restuss 62, Narmle 42, Doaba Guerfel 8, Mos Espa 2, every other city 0** (all 51 city and static-spawn screenplay files checked against the compiler: 0 mismatches). So "the cities that hold have scripted critters" is wrong. Tatooine holds with none, and Restuss and Narmle, which have 62 and 42, get 3 kills a window because their critters are level 6 to 8.
- **The cleanest comparison in the data is Kor Vella against Coronet.** Their easy and medium tables are identical (rows, weights, difficulties), both rings have cap 32, and Kor Vella has 84 active scripted critters (the floor animals: butterfly drone, minor gubbur, paralope, vrelt, durni). Kor Vella has 521 kills against Coronet's 159 (3.3 times); 300 of them were within 300 m of the town centre, where Coronet has none. In the last full window it is 42 against 26, so the lead shrinks (the 84 critters are being eaten faster than they respawn) but does not vanish.
- **What I propose, in order of support:** (S) permanent floor-level critters in the 300 to 1,500 m band for Coronet, Tyrena, Dearic and Nashal, modelled on Kor Vella (36 to 53 each); (T) re-weight the newbie tables toward the floor animals (3 rows in two Corellia tables, 2 rows in four Talus tables); nothing for Kaadara except an optional block I would hold back.
- **What no data edit can fix:** Talus has no animal below level 5 and Rori none below 6, so level 1 characters there stay at the edge of what they can win. That needs new level 2 to 4 creatures (section 5), which is the owner's call.
- **What I considered and do not propose:** raising caps, stacking another spawn area, `NOWORLDSPAWNAREA` for Tyrena. Reasons in section 5.

## 2. Run 7 so far

Source: `/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl`, rows since 11:53 PM on 15 Oct (spawn level gate and five data fixes in, dev `b20a46d7`), read at 1:04 AM (71 minutes; the run was still going). 1,500 bots, about 83 per city, all level 1 to 3. A window is 15 minutes; w1 starts at 11:53 PM; the 11-minute tail after w4 is left out of the window columns but is in Kills and Deaths. The five cities are in bold.

| City | Planet | Bots | w1 | w2 | w3 | w4 | w4/w1 | Kills | Deaths | Median kill distance (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| Anchorhead | tatooine | 84 | 317 | 131 | 85 | 150 | 0.47 | 742 | 22 | 413 |
| Bestine | tatooine | 84 | 218 | 70 | 66 | 116 | 0.53 | 522 | 15 | 840 |
| Mos Espa | tatooine | 84 | 176 | 79 | 88 | 115 | 0.65 | 507 | 23 | 1062 |
| Mos Eisley | tatooine | 84 | 136 | 66 | 93 | 111 | 0.82 | 472 | 15 | 767 |
| Mos Entha | tatooine | 84 | 188 | 89 | 96 | 81 | 0.43 | 525 | 13 | 683 |
| **Kaadara** | naboo | 83 | 211 | 24 | 69 | 47 | 0.22 | 396 | 48 | 365 |
| Kor Vella | corellia | 83 | 297 | 47 | 91 | 42 | 0.14 | 521 | 28 | 284 |
| Moenia | naboo | 83 | 118 | 30 | 38 | 42 | 0.36 | 245 | 49 | 557 |
| **Dearic** | talus | 83 | 118 | 18 | 56 | 28 | 0.24 | 232 | 103 | 492 |
| Bela Vistal | corellia | 83 | 127 | 37 | 58 | 27 | 0.21 | 284 | 44 | 544 |
| **Coronet** | corellia | 84 | 78 | 15 | 30 | 26 | 0.33 | 159 | 42 | 783 |
| Keren | naboo | 83 | 85 | 22 | 49 | 24 | 0.28 | 206 | 47 | 949 |
| **Nashal** | talus | 83 | 117 | 16 | 17 | 23 | 0.20 | 189 | 83 | 398 |
| **Tyrena** | corellia | 83 | 66 | 37 | 50 | 21 | 0.32 | 199 | 44 | 772 |
| Theed | naboo | 83 | 115 | 23 | 31 | 16 | 0.14 | 216 | 34 | 836 |
| Doaba Guerfel | corellia | 83 | 98 | 25 | 62 | 15 | 0.15 | 234 | 25 | 752 |
| Narmle | rori | 83 | 111 | 6 | 2 | 3 | 0.03 | 124 | 115 | 463 |
| Restuss | rori | 83 | 94 | 7 | 34 | 3 | 0.03 | 150 | 140 | 307 |

What the rows say:

- **Every window shows the same dip at w2** (the starting pile is gone, bots rest and train), including the cities that hold. The comparison is w4 against the other cities, not w4 against w1.
- **Kill distance.** Kor Vella's median kill is 284 m from the centre (300 of 521 within 300 m); Coronet's is 783 m, Tyrena's 772 m. The two cities with the same tables kill in different places because Kor Vella has animals standing next to town. Dearic (492 m) and Nashal (398 m) kill near town too, because the bots' hunting ring starts just outside the city edge (400 m and 350 m for these two).
- **What the five kill.** Coronet: howling plumed rasp (4) 45, butterfly drone (5) 33, gubbur (6) 20, baby vynock (1) 12. Tyrena: minor gubbur (4) 35, durni (7) 28, rasp (4) 27. Dearic: paralope (6) 88, fearful fynock youth (5) 76, feared fynock youth (7) 40, baby paralope 21. Nashal: paralope 85, feared fynock youth 56, fearful fynock youth 35. Kaadara: hermit spider 77, gnort (4) 74, flesh-eating chuba 60, chuba 51, large chuba 44. The Talus cities live on two kinds; Kaadara on six.
- **Deaths.** Dearic: fearful fynock youth (level 5) 46, paralope 30. Nashal: fynock youth 33, paralope 25. Those are the bots' own limit (level + 4 + level / 2 = 5 at level 1), not outliers. Coronet's biggest killers are the meatlump camps (19 of 42), which are not in the newbie tables.

## 3. Why: four facts from the data

**3.1 The floor creature, by planet.** Animals (not NPCs) at level 5 or lower, with how many lair templates use them:

| Planet | Animals at level 5 or lower | Cities |
|---|---|---|
| Tatooine | dwarf eopie 3, **kreetle 3**, **tatooine mynock 3**, domestic eopie 4, dwarf nuna 5, lesser desert womp rat 5, minor worrt 5 | Mos Eisley, Mos Entha, Mos Espa, Bestine, Anchorhead hold |
| Corellia | howling plumed rasp 4 (aggressive), minor gubbur 4, butterfly drone 5 | Coronet, Tyrena, Kor Vella, Bela Vistal, Doaba |
| Naboo | gnort 4, massive gnort 4, mott calf 4, chuba 5, large chuba 5, domesticated mott 5 (unused) | Kaadara, Theed, Keren, Moenia |
| Talus | fearful fynock youth 5 | Dearic, Nashal |
| Rori | domestic bearded jax 5 (unused); wild ones start at 6 | Narmle, Restuss |

Share of a table's rolls that give a lair a bot of that level may attack (the bot rule: level + 4 + level / 2, so 5, 7, 8 at levels 1, 2, 3; after the new gate):

| Table (easy ring) | Level 1 | Level 2 | Level 3 |
|---|---|---|---|
| Tatooine (Anchorhead, Mos Entha, Mos Espa, Bestine; Mos Eisley 43%, 83%, 91%) | 57% | 100% | 100% |
| Naboo (Theed, Keren, Moenia, Kaadara) | 36% | 96% | 100% |
| Corellia (Coronet, Tyrena, Kor Vella, Bela Vistal, Doaba) | 25% | 67% | 75% |
| Talus (Dearic, Nashal) | 10% | 90% | 100% |
| Rori (Narmle, Restuss) | 0% | 83% | 83% |

By planet the order is roughly monotonic (the ranges overlap between Talus, Corellia and Naboo): Rori 0% gives 3 kills in w4; Talus 10% gives 23 and 28; Corellia 25% gives 15 to 42; Naboo 36% gives 16 to 47; Tatooine 43 to 57% gives 81 to 150. Within a planet the table share does not separate the cities (the Corellia tables are identical), which is why 3.3 matters.

**3.2 Lair strength follows the difficulty numbers, and Corellia and Talus rows give level 1 characters the weakest lairs.** `SpawnAreaImplementation::tryToSpawn` sets the lair's building level from player level / lair level (below 0.25 is level 1, up to level 5). Corellia rows are `5 to 500` and Talus rows `9 to 15`, so a level 1 character always gets building level 1; Naboo and Tatooine easy rows are `1 to 8` and average 2.1 (simulated; level 2: 3.2, level 3: 3.9, against 1.6 and 2.3 for Corellia, 1.0 and 1.7 for Talus). In `LairObserverImplementation::spawnLairMobile` each respawn wave after the first damages the lair by `maxCondition / (min(buildingLevel, spawnLimit / 3) x 5)`, so a level 1 lair is gone after about 5 respawns and a level 2 lair after about 10. Dynamic ("none") spawns are not affected except for one extra creature at building level 4 or 5. This is a real but second-order lever (section 5, item 4).

**3.3 Kor Vella against Coronet (above).** Same tables, same caps, same ring size class, 3.3 times the kills with 84 permanent critters. This is one pair, so treat the size of the effect as a guess; the direction is the strongest thing in the data.

**3.4 Caps do not look like the limit.** Tyrena's two rings have cap 256 each, Coronet's 32 each, and Tyrena has 25% more kills (199 against 159) with the same tables and the same level 1 share. If full caps of unhunted lairs were the cause, Tyrena would be far ahead. I cannot rule it out (no lair census; `/spawnStatus` was not run), but this pair does not support it.

## 4. Proposals

Each proposal gives the effect on the data, then what it risks. "Level 1 share" is the table arithmetic from 3.1.

### T1. Corellia: swap three rows in `coronet_easy_newbie.lua` and `tyrena_easy_newbie.lua`

`S/mobile/spawn/corellia/coronet_easy_newbie.lua` and `tyrena_easy_newbie.lua` (the two files hold identical rows). The three rows that no level 1 to 3 bot can use (razor cat cub hunt 10, vynock flight 9, vynock lair 9; 150 of 600 weight) become the floor animals: butterfly drone pack (5), howling plumed rasp pack (4), gubbur herd (minor gubbur 4 and gubbur 6).

```diff
--- a/mobile/spawn/corellia/coronet_easy_newbie.lua
+++ b/mobile/spawn/corellia/coronet_easy_newbie.lua
@@ -1,7 +1,7 @@
 coronet_easy_newbie = {
 	lairSpawns = {
 		{
-			lairTemplateName = "corellia_razor_cat_cub_hunt_neutral_none",
+			lairTemplateName = "corellia_corellian_butterfly_drone_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -64,7 +64,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_flight_neutral_none",
+			lairTemplateName = "corellia_plumed_rasp_howling_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_lair_neutral_small",
+			lairTemplateName = "corellia_gubbur_herd_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
```

- **Effect:** level 1 share 25% to 50%, level 2 67% to 92%, level 3 75% to 100%. The Tyrena diff is the same text.
- **Risk:** the ring gets fewer vynocks and cat cubs, so level 4 to 6 characters see less variety there (the medium ring and the big areas keep them). The howling rasp is aggressive; its share doubles from 8% to 17% of easy-ring rolls, so more level 1 characters get a pack chasing them (in run 7 Coronet's bots killed 45 and lost 2 to them). The drone is the animal the bots already farm (the first review found it was 67% of Coronet's early kills in runs 2 and 3; in run 7 it is 21%), so concentration is higher.

### T2. Talus: swap two rows in the four Dearic and Nashal ring tables

`S/mobile/spawn/talus/talus_dearic_easy_newbie.lua`, `talus_dearic_medium_newbie.lua`, `talus_nashal_easy_newbie.lua`, `talus_nashal_medium_newbie.lua` (four copies of one table). The level 8 to 11 rasp flite pack (a row only level 3 and up can use) becomes a second fearful fynock youth lair (5), and the second of the two duplicate paralope lairs becomes the putrid decay mite hatchling pack (7, not aggressive, defined but used by no table).

```diff
--- a/mobile/spawn/talus/talus_dearic_easy_newbie.lua
+++ b/mobile/spawn/talus/talus_dearic_easy_newbie.lua
@@ -55,7 +55,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_paralope_lair_neutral_medium",
+			lairTemplateName = "talus_putrid_decay_mite_hatchling_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_rasp_flite_large_neutral_none",
+			lairTemplateName = "talus_fynock_youth_lair_neutral_small",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
```

- **Effect:** level 1 share 10% to 20%, level 2 90% to 100%. The other three diffs are the same text.
- **Risk:** the fynock youth is the animal that killed 46 and 33 bots at Dearic and Nashal, so more of them means more level 1 deaths and more kills in the same ratio; this raises supply without making it safer. The hatchling pack adds a new kind to the towns but it is level 7, so it helps level 2 and up. The only other Talus rows affected are in these four files; the bigger Talus areas are untouched.

### S1 to S4. Permanent floor-level critters for Coronet, Tyrena, Dearic and Nashal

Added at the end of `spawnMobiles()` in `S/screenplays/cities/corellia_coronet.lua` (53 critters), `corellia_tyrena.lua` (36), `talus_dearic.lua` (49) and `talus_nashal.lua` (47), in the style of the Kor Vella block: `spawnMobile(self.planet, "<creature>", 300, x, z, y, heading, 0)`, 300 s respawn.

| City | Creatures (existing templates, same planet) | Placed |
|---|---|---|
| Coronet | butterfly drone (5) 19, minor gubbur (4) 19, vrelt (6) 8, paralope (6) 7 | 8 groups, 650 to 950 m from the centre |
| Tyrena | butterfly drone 15, minor gubbur 13, vrelt 8 | 6 groups, 760 to 1,040 m |
| Dearic | fearful fynock youth (5) 24, paralope (6) 13, putrid decay mite hatchling (7) 8, feared fynock youth (7) 4 | 8 groups, 540 to 880 m |
| Nashal | fearful fynock youth 18, paralope 13, hatchling 8, feared fynock youth 8 | 8 groups, 550 to 770 m |

How the positions were chosen: from the snapshots of this run's city bots (not the Ossus explorers): x, y, z of bots walking, fighting, idle or resting; eight 45-degree sectors around each city, the sector's busiest spot, up to eight creatures within 90 m of it, each at a place a bot actually stood (so the ground is walkable and the height is real). Anything within 120 m of a death, incapacitation or aggro in this run was dropped. Sectors with fewer than 25 candidate points (Tyrena's south side, for example) got nothing.

```diff
--- a/screenplays/cities/corellia_coronet.lua
+++ b/screenplays/cities/corellia_coronet.lua
@@ -386,4 +386,67 @@
 		self:setCustomName(pNpc, "Hunter Javeezo")
 		CreatureObject(pNpc):clearOptionBit(AIENABLED)
 	end
+
+	--Low-level hunting stock for the Coronet ring: 53 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -956, -23, -4693, 47, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -957, -24, -4706, 94, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -1030, -29, -4677, 141, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -231, 26, -5187, 188, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -220, 27, -5183, 235, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -228, 28, -5162, 282, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -234, 23, -5220, 329, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -183, 31, -5188, 16, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -191, 32, -5159, 63, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -261, 24, -5147, 110, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 73, 10, -5202, 157, 0)
+	spawnMobile(self.planet, "paralope", 300, 55, 2, -5200, 204, 0)
+	spawnMobile(self.planet, "paralope", 300, 74, 6, -5179, 251, 0)
+	spawnMobile(self.planet, "paralope", 300, 51, 3, -5214, 298, 0)
+	spawnMobile(self.planet, "paralope", 300, 67, 1, -5162, 345, 0)
+	spawnMobile(self.planet, "paralope", 300, 121, 23, -5166, 32, 0)
+	spawnMobile(self.planet, "paralope", 300, 34, -2, -5145, 79, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, 602, 16, -4848, 126, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 593, 7, -4805, 173, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 586, 28, -4893, 220, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 614, 29, -4920, 267, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 677, 3, -4831, 314, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 511, 1, -4258, 1, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 501, 0, -4242, 48, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 514, 0, -4218, 95, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 446, 7, -4274, 142, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 444, 10, -4285, 189, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 527, 3, -4330, 236, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 437, 10, -4279, 283, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 432, 10, -4273, 330, 0)
+
+	spawnMobile(self.planet, "vrelt", 300, 128, 22, -3751, 17, 0)
+	spawnMobile(self.planet, "vrelt", 300, 114, 20, -3755, 64, 0)
+	spawnMobile(self.planet, "vrelt", 300, 111, 26, -3791, 111, 0)
+	spawnMobile(self.planet, "vrelt", 300, 92, 27, -3786, 158, 0)
+	spawnMobile(self.planet, "vrelt", 300, 170, 28, -3718, 205, 0)
+	spawnMobile(self.planet, "vrelt", 300, 200, 25, -3788, 252, 0)
+	spawnMobile(self.planet, "vrelt", 300, 155, 25, -3829, 299, 0)
+	spawnMobile(self.planet, "vrelt", 300, 133, 27, -3667, 346, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -510, 28, -3732, 33, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -467, 27, -3752, 80, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -550, 28, -3767, 127, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -459, 27, -3770, 174, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -575, 28, -3721, 221, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -517, 25, -3657, 268, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -452, 25, -3782, 315, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -544, 25, -3659, 2, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -939, -8, -3993, 49, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -925, -8, -4002, 96, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -918, -8, -4022, 143, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -968, -8, -3972, 190, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -913, -2, -3957, 237, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -943, -8, -4050, 284, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -891, -7, -4036, 331, 0)
 end
```

The other three diffs have the same shape (Appendix A prints all five).

- **Effect (a guess from one pair):** the Kor Vella block gave 3.3 times Coronet's kills over 71 minutes and 1.6 times in the last full window. Expect something between 1.5 and 3 times, not more, and a lead that fades as bots eat the stock faster than the 300 s respawn. Each critter is worth at most 12 kills an hour.
- **Risk:** (1) these are permanent AI agents, 36 to 53 per city, awake whenever a player is near. The test galaxy's tick is 7 to 8 ms now (200 to 290 ms in the first minutes) but its resident memory grew from 4.8 GB to 7.9 GB over this run, so measure memory and tick before and after; the live galaxy will have far fewer players. (2) The creatures stand where bots walked in the simulation, which is where the simulation's hunting ring is, not necessarily where a player would like them; a good place for a player is next to town and a road, and I did not check roads, buildings or points of interest, only that bots had stood there. (3) Heights come from the bot snapshots and are right where the bot stood; one Nashal group spans 64 m of height within 90 m (a steep slope), where creatures may look odd until they move. (4) On Talus the floor creature is level 5, so more of it means the same deaths: S3 and S4 raise supply, not safety. (5) Scripted critters ignore the level gate and the caps, which is the point, and also means they are there for every character including level 10 ones, who get little from them.

### S5. Kaadara: optional, I would hold it back

Kaadara needs no change on the evidence: 396 kills, 48 deaths, a w4 of 47 (best of the non-Tatooine cities). The first review's remedy ("measure before editing") still stands. If the owner wants insurance anyway, Appendix A has a 39-critter block of gnort (16), chuba (15) and mott calf (8), all level 4 to 5, placed the same way. It adds no table or region change. Risk as for S1 to S4, plus: Kaadara's own stock creature block (nuna, nightspider, mott calf, hermit spider, flewt; 54 critters, positions with real heights) is commented out in the file, which is a cheaper choice if the owner wants to switch something back on, but its level 10 nunas and level 7 spiders would hurt level 1 characters.

## 5. Considered and not proposed

1. **Raising caps** (Coronet 32 to 64). Not supported (3.4). One line of data if wanted: `corellia_regions.lua:124-125`, the last number.
2. **`NOWORLDSPAWNAREA` on Tyrena's rings.** Tyrena's rings are the only ones of the five without it, so the planet-wide world spawner also rolls there. But Tyrena's deaths per kill (22%) are no worse than Coronet's (26%) which has the flag, and the world table is mostly gated out for level 1. Not worth a region edit on this evidence.
3. **A stacked low-level spawn area per city** (a new `SPAWNAREA` ring with its own table of floor animals, cap 48). It would add concurrency, but caps do not look binding. Worth trying only if S disappoints. It would need a new table file, an `includeFile` line in `mobile/spawn/serverobjects.lua` and a region row.
4. **Difficulty numbers `1 to 8` on the kept rows** (3.2). Changing `minDifficulty` and `maxDifficulty` of every row in `coronet_easy_newbie.lua`, `tyrena_easy_newbie.lua` and the four Talus tables from `5 / 500` and `9 / 15` to `1 / 8` would double lair longevity for level 1 characters and add one creature to 14% of dynamic spawns. About 130 changed lines, no new content, but no measurement behind it, so I left it as a second wave: apply it only after S and T show how much is left to gain.
5. **Level 2 to 4 creatures for Talus and Rori** (and a level 3 floor for Corellia and Naboo, the way Tatooine has). This is the fix that the data points to and it is new content, so the owner decides. Each needs a template (a copy of the floor creature at a lower level and HAM, keeping its appearance and name string so no client string table is touched) and a dynamic lair around it, and each should go through the creature review that the Ossus six went through. Suggested floor: level 3 for each planet, as Tatooine's kreetle and mynock. Cross-planet loans (Tatooine's kreetle on Corellia) are the cheap alternative; I did not propose them because they break the owner's "same planet" rule and the lore of the place.
6. **A long run first.** Run 7 has 71 minutes. The first review's collapse showed at 165 minutes (run 2). Everything above should be re-read against the last window of a 2-hour run before it is applied.

## 6. How to try it

1. Owner decides which of T1, T2, S1 to S4 (S5 held). They are independent; the patch has one block per file.
2. Lock holder: `cd /opt/swg/Core3-dev/MMOCoreORB/bin/scripts && patch -p1 < <path>/city-spawn-proposals.patch` (the patch has one block per file, so unwanted blocks can be deleted first), then `python3 .../tools/check_lua.py`, commit in `dev`, restart the test galaxy under the standing OK (no client running, no round in progress).
3. Run the launch simulation for at least 90 minutes with the same 1,500 bots; compare the w4 and w5 columns above per city. Success looks like the five cities reaching Kor Vella's and Moenia's w4 (42 to 47 kills per 15 minutes) or the Tatooine band (80 to 150); failure looks like no change in w4.
4. Read-only checks alongside: `/spawnStatus` on each ring at 0, 20 and 60 minutes (to see whether caps are full), and the server tick.

## 7. What is not known

- **No lair census.** Whether caps fill with lairs nobody hunts is still a hypothesis; the Tyrena/Coronet pair argues against it.
- **Terrain beyond the bots' paths.** I did not look at water, slopes or points of interest around the proposed positions; they are only known to be standable.
- **Real players.** Everything is measured on level 1 to 3 bots at 83 per city. A handful of real characters would not eat the stock or fill the rings the same way.
- **The effect of every edit.** None of them has been run. The level 1 shares are arithmetic on the tables, the size of the S effect is a guess from one pair.
- **My scripted-spawn recount.** Comments were stripped by a script; for all 51 city and static-spawn screenplay files the set of creature names that survives equals the set of creature-name string constants in the `luac -l -l` listing. The per-city counts (positions within 2 km, creatures of level 8 or lower that are not NPCs) rest on the script's pattern for `spawnMobile` lines, as in the first review; a spawn made through another helper would be missed.

## 8. How the numbers were made

- Run 7 log: copied from the test galaxy's `botpop-launch.jsonl` into my temp folder at 12:36, 12:58 and 1:04 AM (read-only) and analysed with Python; kill, death, spawn and snapshot rows by `city`, `t`, `target`, `tlvl`, `x`, `y`.
- Spawn data: `S/managers/planet/*_regions.lua`, `S/mobile/spawn/*`, `S/mobile/lair/*`, `S/mobile/<planet>/*.lua`, `S/screenplays/cities/*.lua`, copied from dev `74fa3e8c` to my temp folder and parsed (the parser is the first review's, re-pointed at the current files). Code read for the rules: `SpawnAreaImplementation.cpp`, `CreatureManagerImplementation.cpp`, `DynamicSpawnObserverImplementation.cpp`, `LairObserverImplementation.cpp`, `PlanetManagerImplementation.cpp`.
- Building-level averages in 3.2 are a Monte Carlo of the formula in `tryToSpawn` (200,000 draws per cell).
- Diffs: generated by script from the pristine copies, then dry-run, applied to a copy built from the live dev files, and compiled with `luac5.3 -p`; the six table files were also loaded with a stub `addSpawnGroup` (row count and total weight unchanged: 600 and 500).

## Appendix A. All diffs

### T1 Coronet: `S/mobile/spawn/corellia/coronet_easy_newbie.lua`

```diff
--- a/mobile/spawn/corellia/coronet_easy_newbie.lua
+++ b/mobile/spawn/corellia/coronet_easy_newbie.lua
@@ -1,7 +1,7 @@
 coronet_easy_newbie = {
 	lairSpawns = {
 		{
-			lairTemplateName = "corellia_razor_cat_cub_hunt_neutral_none",
+			lairTemplateName = "corellia_corellian_butterfly_drone_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -64,7 +64,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_flight_neutral_none",
+			lairTemplateName = "corellia_plumed_rasp_howling_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_lair_neutral_small",
+			lairTemplateName = "corellia_gubbur_herd_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
```

### T1 Tyrena: `S/mobile/spawn/corellia/tyrena_easy_newbie.lua`

```diff
--- a/mobile/spawn/corellia/tyrena_easy_newbie.lua
+++ b/mobile/spawn/corellia/tyrena_easy_newbie.lua
@@ -1,7 +1,7 @@
 tyrena_easy_newbie = {
 	lairSpawns = {
 		{
-			lairTemplateName = "corellia_razor_cat_cub_hunt_neutral_none",
+			lairTemplateName = "corellia_corellian_butterfly_drone_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -64,7 +64,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_flight_neutral_none",
+			lairTemplateName = "corellia_plumed_rasp_howling_large_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "corellia_vynock_lair_neutral_small",
+			lairTemplateName = "corellia_gubbur_herd_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 5,
 			maxDifficulty = 500,
```

### T2 Dearic easy: `S/mobile/spawn/talus/talus_dearic_easy_newbie.lua`

```diff
--- a/mobile/spawn/talus/talus_dearic_easy_newbie.lua
+++ b/mobile/spawn/talus/talus_dearic_easy_newbie.lua
@@ -55,7 +55,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_paralope_lair_neutral_medium",
+			lairTemplateName = "talus_putrid_decay_mite_hatchling_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_rasp_flite_large_neutral_none",
+			lairTemplateName = "talus_fynock_youth_lair_neutral_small",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
```

### T2 Dearic medium: `S/mobile/spawn/talus/talus_dearic_medium_newbie.lua`

```diff
--- a/mobile/spawn/talus/talus_dearic_medium_newbie.lua
+++ b/mobile/spawn/talus/talus_dearic_medium_newbie.lua
@@ -55,7 +55,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_paralope_lair_neutral_medium",
+			lairTemplateName = "talus_putrid_decay_mite_hatchling_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_rasp_flite_large_neutral_none",
+			lairTemplateName = "talus_fynock_youth_lair_neutral_small",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
```

### T2 Nashal easy: `S/mobile/spawn/talus/talus_nashal_easy_newbie.lua`

```diff
--- a/mobile/spawn/talus/talus_nashal_easy_newbie.lua
+++ b/mobile/spawn/talus/talus_nashal_easy_newbie.lua
@@ -55,7 +55,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_paralope_lair_neutral_medium",
+			lairTemplateName = "talus_putrid_decay_mite_hatchling_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_rasp_flite_large_neutral_none",
+			lairTemplateName = "talus_fynock_youth_lair_neutral_small",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
```

### T2 Nashal medium: `S/mobile/spawn/talus/talus_nashal_medium_newbie.lua`

```diff
--- a/mobile/spawn/talus/talus_nashal_medium_newbie.lua
+++ b/mobile/spawn/talus/talus_nashal_medium_newbie.lua
@@ -55,7 +55,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_paralope_lair_neutral_medium",
+			lairTemplateName = "talus_putrid_decay_mite_hatchling_neutral_none",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
@@ -73,7 +73,7 @@
 			size = 15,
 		},
 		{
-			lairTemplateName = "talus_rasp_flite_large_neutral_none",
+			lairTemplateName = "talus_fynock_youth_lair_neutral_small",
 			spawnLimit = -1,
 			minDifficulty = 9,
 			maxDifficulty = 15,
```

### S1 Coronet: `S/screenplays/cities/corellia_coronet.lua`

```diff
--- a/screenplays/cities/corellia_coronet.lua
+++ b/screenplays/cities/corellia_coronet.lua
@@ -386,4 +386,67 @@
 		self:setCustomName(pNpc, "Hunter Javeezo")
 		CreatureObject(pNpc):clearOptionBit(AIENABLED)
 	end
+
+	--Low-level hunting stock for the Coronet ring: 53 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -956, -23, -4693, 47, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -957, -24, -4706, 94, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -1030, -29, -4677, 141, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -231, 26, -5187, 188, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -220, 27, -5183, 235, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -228, 28, -5162, 282, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -234, 23, -5220, 329, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -183, 31, -5188, 16, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -191, 32, -5159, 63, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -261, 24, -5147, 110, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 73, 10, -5202, 157, 0)
+	spawnMobile(self.planet, "paralope", 300, 55, 2, -5200, 204, 0)
+	spawnMobile(self.planet, "paralope", 300, 74, 6, -5179, 251, 0)
+	spawnMobile(self.planet, "paralope", 300, 51, 3, -5214, 298, 0)
+	spawnMobile(self.planet, "paralope", 300, 67, 1, -5162, 345, 0)
+	spawnMobile(self.planet, "paralope", 300, 121, 23, -5166, 32, 0)
+	spawnMobile(self.planet, "paralope", 300, 34, -2, -5145, 79, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, 602, 16, -4848, 126, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 593, 7, -4805, 173, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 586, 28, -4893, 220, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 614, 29, -4920, 267, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, 677, 3, -4831, 314, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 511, 1, -4258, 1, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 501, 0, -4242, 48, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 514, 0, -4218, 95, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 446, 7, -4274, 142, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 444, 10, -4285, 189, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 527, 3, -4330, 236, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 437, 10, -4279, 283, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, 432, 10, -4273, 330, 0)
+
+	spawnMobile(self.planet, "vrelt", 300, 128, 22, -3751, 17, 0)
+	spawnMobile(self.planet, "vrelt", 300, 114, 20, -3755, 64, 0)
+	spawnMobile(self.planet, "vrelt", 300, 111, 26, -3791, 111, 0)
+	spawnMobile(self.planet, "vrelt", 300, 92, 27, -3786, 158, 0)
+	spawnMobile(self.planet, "vrelt", 300, 170, 28, -3718, 205, 0)
+	spawnMobile(self.planet, "vrelt", 300, 200, 25, -3788, 252, 0)
+	spawnMobile(self.planet, "vrelt", 300, 155, 25, -3829, 299, 0)
+	spawnMobile(self.planet, "vrelt", 300, 133, 27, -3667, 346, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -510, 28, -3732, 33, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -467, 27, -3752, 80, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -550, 28, -3767, 127, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -459, 27, -3770, 174, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -575, 28, -3721, 221, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -517, 25, -3657, 268, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -452, 25, -3782, 315, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -544, 25, -3659, 2, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -939, -8, -3993, 49, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -925, -8, -4002, 96, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -918, -8, -4022, 143, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -968, -8, -3972, 190, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -913, -2, -3957, 237, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -943, -8, -4050, 284, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -891, -7, -4036, 331, 0)
 end
```

### S2 Tyrena: `S/screenplays/cities/corellia_tyrena.lua`

```diff
--- a/screenplays/cities/corellia_tyrena.lua
+++ b/screenplays/cities/corellia_tyrena.lua
@@ -444,4 +444,48 @@
 	spawnMobile(self.planet, "swooper_leader", 300,-5416.8,4.57113,-2286.37,76.0594,0)
 	spawnMobile(self.planet, "swooper_leader", 300,-5415.8,5.33258,-2277.08,224.956,0)
 	spawnMobile(self.planet, "swooper_leader", 300,-5420.58,3.58008,-2285.59,200.562,0)
+
+	--Low-level hunting stock for the Tyrena ring: 36 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -6158, 16, -2899, 47, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -6115, -1, -2953, 94, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -4439, 2, -2646, 141, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4452, 4, -2628, 188, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4409, 0, -2653, 235, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4427, 0, -2680, 282, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4482, 3, -2660, 329, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4396, 1, -2626, 16, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -4365, 3, -2598, 63, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4447, 18, -2215, 110, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4453, 25, -2246, 157, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4463, 23, -2250, 204, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4413, 22, -2253, 251, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4422, 25, -2261, 298, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4448, 28, -2269, 345, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4502, 17, -2197, 32, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -4481, 14, -2166, 79, 0)
+
+	spawnMobile(self.planet, "vrelt", 300, -4878, 24, -1637, 126, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4872, 24, -1633, 173, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4908, 26, -1649, 220, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4849, 24, -1655, 267, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4924, 22, -1657, 314, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4931, 21, -1660, 1, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4848, 23, -1689, 48, 0)
+	spawnMobile(self.planet, "vrelt", 300, -4939, 26, -1635, 95, 0)
+
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -5514, 2, -1606, 142, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -5516, 1, -1622, 189, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -5507, 6, -1648, 236, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -5562, -1, -1567, 283, 0)
+	spawnMobile(self.planet, "corellian_butterfly_drone", 300, -5592, 0, -1647, 330, 0)
+
+	spawnMobile(self.planet, "minor_gubbur", 300, -6063, 1, -2170, 17, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -6072, 0, -2162, 64, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -6028, 1, -2149, 111, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -6015, 17, -2185, 158, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -5984, 13, -2155, 205, 0)
+	spawnMobile(self.planet, "minor_gubbur", 300, -6112, 21, -2240, 252, 0)
 end
```

### S3 Dearic: `S/screenplays/cities/talus_dearic.lua`

```diff
--- a/screenplays/cities/talus_dearic.lua
+++ b/screenplays/cities/talus_dearic.lua
@@ -342,4 +342,63 @@
 	spawnMobile(self.planet, "docile_kahmurra", 300, getRandomNumber(10) + 225.8, 6.0, getRandomNumber(10) + -3157, getRandomNumber(360), 0)
 	spawnMobile(self.planet, "docile_kahmurra", 300, getRandomNumber(10) + 225.8, 6.0, getRandomNumber(10) + -3157, getRandomNumber(360), 0)
 	spawnMobile(self.planet, "docile_kahmurra", 300, getRandomNumber(10) + 225.8, 6.0, getRandomNumber(10) + -3157, getRandomNumber(360), 0)
+
+	--Low-level hunting stock for the Dearic ring: 49 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -161, 31, -3209, 47, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -132, 29, -3183, 94, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -103, 32, -3217, 141, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -105, 25, -3167, 188, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -98, 23, -3151, 235, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -117, 36, -3285, 282, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 171, 43, -3684, 329, 0)
+	spawnMobile(self.planet, "paralope", 300, 171, 43, -3701, 16, 0)
+	spawnMobile(self.planet, "paralope", 300, 127, 42, -3686, 63, 0)
+	spawnMobile(self.planet, "paralope", 300, 150, 42, -3641, 110, 0)
+	spawnMobile(self.planet, "paralope", 300, 149, 42, -3631, 157, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 694, 32, -3653, 204, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 667, 34, -3649, 251, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 647, 42, -3716, 298, 0)
+
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1129, 25, -3145, 345, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1170, 30, -3156, 32, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1105, 18, -3095, 79, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1184, 32, -3128, 126, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1077, 13, -3112, 173, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1092, 14, -3086, 220, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1198, 33, -3101, 267, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 1212, 32, -3136, 314, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1131, 6, -2774, 1, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1104, 6, -2783, 48, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1173, -2, -2780, 95, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1173, 0, -2766, 142, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1134, 6, -2716, 189, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1208, 0, -2749, 236, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1202, 7, -2813, 283, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 1134, 4, -2859, 330, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 679, 6, -2411, 17, 0)
+	spawnMobile(self.planet, "paralope", 300, 663, 6, -2436, 64, 0)
+	spawnMobile(self.planet, "paralope", 300, 659, 6, -2457, 111, 0)
+	spawnMobile(self.planet, "paralope", 300, 648, 6, -2452, 158, 0)
+	spawnMobile(self.planet, "paralope", 300, 707, 6, -2455, 205, 0)
+	spawnMobile(self.planet, "paralope", 300, 628, 6, -2432, 252, 0)
+	spawnMobile(self.planet, "paralope", 300, 669, 6, -2466, 299, 0)
+	spawnMobile(self.planet, "paralope", 300, 741, 6, -2409, 346, 0)
+
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 108, 6, -2216, 33, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 135, 3, -2221, 80, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 101, 10, -2185, 127, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 31, 9, -2250, 174, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -159, 6, -2774, 221, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -129, 3, -2765, 268, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -166, 7, -2738, 315, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -197, 9, -2772, 2, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -145, 4, -2833, 49, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -218, 11, -2812, 96, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, -148, 5, -2846, 143, 0)
 end
```

### S4 Nashal: `S/screenplays/cities/talus_nashal.lua`

```diff
--- a/screenplays/cities/talus_nashal.lua
+++ b/screenplays/cities/talus_nashal.lua
@@ -297,4 +297,61 @@
 	spawnMobile(self.planet, "song_rasp", 300, getRandomNumber(10) + 4237.4, 28.6, getRandomNumber(10) + 5389.7, getRandomNumber(360), 0)
 	spawnMobile(self.planet, "song_rasp", 300, getRandomNumber(10) + 4237.4, 28.6, getRandomNumber(10) + 5389.7, getRandomNumber(360), 0)
 	spawnMobile(self.planet, "song_rasp", 300, getRandomNumber(10) + 4237.4, 28.6, getRandomNumber(10) + 5389.7, getRandomNumber(360), 0)
+
+	--Low-level hunting stock for the Nashal ring: 47 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3707, 50, 5051, 47, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3675, 50, 5040, 94, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3757, 55, 5090, 141, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 4029, 60, 4620, 188, 0)
+	spawnMobile(self.planet, "paralope", 300, 4046, 55, 4601, 235, 0)
+	spawnMobile(self.planet, "paralope", 300, 4043, 49, 4579, 282, 0)
+	spawnMobile(self.planet, "paralope", 300, 4010, 54, 4578, 329, 0)
+	spawnMobile(self.planet, "paralope", 300, 4085, 56, 4615, 16, 0)
+	spawnMobile(self.planet, "paralope", 300, 4010, 54, 4554, 63, 0)
+	spawnMobile(self.planet, "paralope", 300, 3955, 63, 4647, 110, 0)
+	spawnMobile(self.planet, "paralope", 300, 3952, 55, 4587, 157, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4537, -1, 4581, 204, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4521, -1, 4586, 251, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4484, 15, 4560, 298, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4529, -1, 4518, 345, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4615, 46, 4594, 32, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4548, -1, 4500, 79, 0)
+
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4938, 146, 5127, 126, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4957, 148, 5129, 173, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4920, 144, 5140, 220, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4919, 144, 5153, 267, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4987, 136, 5124, 314, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4939, 112, 5178, 1, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4953, 84, 5180, 48, 0)
+	spawnMobile(self.planet, "putrid_decay_mite_hatchling", 300, 4883, 125, 5119, 95, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4949, 46, 5388, 142, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4973, 72, 5336, 189, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4888, 74, 5356, 236, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4922, 76, 5324, 283, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 4937, 76, 5312, 330, 0)
+
+	spawnMobile(self.planet, "paralope", 300, 4610, 68, 5816, 17, 0)
+	spawnMobile(self.planet, "paralope", 300, 4605, 56, 5798, 64, 0)
+	spawnMobile(self.planet, "paralope", 300, 4617, 38, 5762, 111, 0)
+	spawnMobile(self.planet, "paralope", 300, 4663, 56, 5785, 158, 0)
+	spawnMobile(self.planet, "paralope", 300, 4673, 71, 5818, 205, 0)
+
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4167, 62, 5869, 252, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4170, 55, 5828, 299, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4220, 61, 5876, 346, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4164, 63, 5929, 33, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4184, 61, 5932, 80, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4162, 54, 5800, 127, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4240, 64, 5877, 174, 0)
+	spawnMobile(self.planet, "feared_fynock_youth", 300, 4236, 68, 5899, 221, 0)
+
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3796, 60, 5474, 268, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3762, 77, 5424, 315, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3868, 45, 5526, 2, 0)
+	spawnMobile(self.planet, "fearful_fynock_youth", 300, 3713, 74, 5442, 49, 0)
 end
```

### S5 Kaadara (optional, held back): `S/screenplays/cities/naboo_kaadara.lua`

```diff
--- a/screenplays/cities/naboo_kaadara.lua
+++ b/screenplays/cities/naboo_kaadara.lua
@@ -306,4 +306,50 @@
 	if pNpc ~= nil then
 		AiAgent(pNpc):setConvoTemplate("junkDealerFineryConvoTemplate")
 	end
+
+	--Low-level hunting stock for the Kaadara ring: 39 existing critters, 300 s respawn.
+	--Positions (x, z, y) are ground that launch-simulation run 7 bots walked, 120 m or more from any death, incapacitation or aggro in that run.
+	spawnMobile(self.planet, "gnort", 300, 4606, -251, 6359, 47, 0)
+	spawnMobile(self.planet, "gnort", 300, 4560, -255, 6370, 94, 0)
+	spawnMobile(self.planet, "gnort", 300, 4626, -254, 6417, 141, 0)
+	spawnMobile(self.planet, "gnort", 300, 4553, -254, 6313, 188, 0)
+	spawnMobile(self.planet, "gnort", 300, 4532, -256, 6369, 235, 0)
+	spawnMobile(self.planet, "gnort", 300, 4642, -241, 6292, 282, 0)
+	spawnMobile(self.planet, "gnort", 300, 4671, -248, 6403, 329, 0)
+	spawnMobile(self.planet, "gnort", 300, 4677, -239, 6317, 16, 0)
+
+	spawnMobile(self.planet, "chuba", 300, 4943, -195, 6012, 63, 0)
+	spawnMobile(self.planet, "chuba", 300, 4968, -195, 6008, 110, 0)
+	spawnMobile(self.planet, "chuba", 300, 4912, -193, 5994, 157, 0)
+	spawnMobile(self.planet, "chuba", 300, 4974, -195, 5984, 204, 0)
+	spawnMobile(self.planet, "chuba", 300, 4906, -192, 6042, 251, 0)
+	spawnMobile(self.planet, "chuba", 300, 4891, -190, 5993, 298, 0)
+	spawnMobile(self.planet, "chuba", 300, 4899, -191, 6054, 345, 0)
+	spawnMobile(self.planet, "chuba", 300, 4902, -191, 6064, 32, 0)
+
+	spawnMobile(self.planet, "mott_calf", 300, 5474, -195, 6049, 79, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5479, -195, 6029, 126, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5486, -195, 6020, 173, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5517, -196, 6039, 220, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5486, -195, 6092, 267, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5480, -195, 6000, 314, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5427, -195, 6022, 1, 0)
+	spawnMobile(self.planet, "mott_calf", 300, 5418, -195, 6032, 48, 0)
+
+	spawnMobile(self.planet, "gnort", 300, 5762, -195, 6407, 95, 0)
+	spawnMobile(self.planet, "gnort", 300, 5744, -195, 6417, 142, 0)
+	spawnMobile(self.planet, "gnort", 300, 5718, -196, 6420, 189, 0)
+	spawnMobile(self.planet, "gnort", 300, 5779, -196, 6358, 236, 0)
+	spawnMobile(self.planet, "gnort", 300, 5695, -196, 6402, 283, 0)
+	spawnMobile(self.planet, "gnort", 300, 5681, -197, 6420, 330, 0)
+	spawnMobile(self.planet, "gnort", 300, 5795, -197, 6329, 17, 0)
+	spawnMobile(self.planet, "gnort", 300, 5674, -197, 6404, 64, 0)
+
+	spawnMobile(self.planet, "chuba", 300, 5806, -193, 6748, 111, 0)
+	spawnMobile(self.planet, "chuba", 300, 5832, -191, 6736, 158, 0)
+	spawnMobile(self.planet, "chuba", 300, 5768, -196, 6777, 205, 0)
+	spawnMobile(self.planet, "chuba", 300, 5744, -194, 6733, 252, 0)
+	spawnMobile(self.planet, "chuba", 300, 5740, -195, 6765, 299, 0)
+	spawnMobile(self.planet, "chuba", 300, 5885, -192, 6767, 346, 0)
+	spawnMobile(self.planet, "chuba", 300, 5886, -193, 6774, 33, 0)
 end
```

