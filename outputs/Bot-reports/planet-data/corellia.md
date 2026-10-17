# Corellia: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:02 PM to 7:17 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 416 (0 explorers, 269 that killed something).
- Coverage: 97 of 256 squares of 1 km had a bot or a sighting in them (38%); explorers stood in 0.
- Templates: 52 creatures, 25 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| durni | 1-7 | 844 | 54 | 105 |  | 76 | 6,-7 (201); -4,3 (197); -6,-2 (94); 6,-6 (73); 2,5 (73) |
| gubbur | 1-6 | 779 | 80 | 251 |  | 79 | 3,4 (91); 3,5 (63); 6,-7 (56); -5,2 (55); -1,-4 (53) |
| paralope | 1-6 | 714 | 62 | 219 |  | 71 | -4,3 (136); -4,2 (107); -1,-4 (62); 5,-6 (52); -6,-2 (46) |
| corellian_butterfly_drone | 5 | 667 | 2 |  |  | 31 | -4,3 (180); -4,2 (122); 0,-5 (109); -1,-4 (56); -3,2 (39) |
| scavenger_rat | 8 | 378 | 34 | 87 |  | 54 | -6,-2 (57); 0,-6 (49); 6,-7 (40); -1,-6 (33); -6,-3 (25) |
| corellian_butterfly | 1-7 | 320 | 11 |  |  | 39 | 6,-6 (154); -1,-5 (73); -6,-3 (54); -5,-3 (40); 2,6 (25) |
| plumed_rasp | 1-7 | 205 | 31 | 101 |  | 63 | 2,6 (31); -5,2 (25); -7,-3 (20); -6,3 (19); 1,-5 (19) |
| minor_gubbur | 4 | 454 |  |  |  | 22 | -4,3 (184); -4,2 (104); -1,-6 (35); -1,-4 (26); 0,-5 (23) |
| howling_plumed_rasp | 4 | 328 | 14 | 16 |  | 36 | 6,-7 (70); -1,-6 (57); 3,4 (46); 6,-6 (34); 0,-5 (32) |
| diseased_vrelt | 1-8 | 82 | 46 | 84 |  | 43 | 1,4 (23); -1,-6 (19); -5,-2 (18); 0,-4 (18); 3,6 (18) |
| vrelt | 6 | 193 | 3 |  |  | 18 | -4,3 (91); -4,2 (78); 0,-4 (19); 6,-5 (16); -1,-4 (8) |
| giant_gubbur | 9 | 48 | 41 | 59 |  | 29 | 5,-7 (18); 5,-6 (15); -1,-4 (14); 1,-6 (12); 3,6 (12) |
| bloated_gubbur | 6 | 142 | 5 |  |  | 25 | -6,-3 (30); -1,-5 (30); 3,5 (23); -1,-4 (19); 0,-6 (19) |
| vynock | 1-9 | 120 | 13 | 22 |  | 40 | 6,-6 (27); 2,5 (17); 0,-4 (14); 1,-5 (12); 1,4 (11) |
| meatlump_stooge | 7 | 5 | 36 | 54 |  | 28 | -7,-4 (24); 7,-5 (22); 2,4 (17); 4,4 (15); 0,-4 (12) |
| rogue_corsec_trooper | 7 | 120 |  | 1 |  | 2 | -4,3 (132); -6,-3 (32) |
| meatlump_buffoon | 5 | 20 | 21 | 44 |  | 29 | 3,6 (10); 5,-7 (8); 6,-5 (8); -7,-4 (8); -7,-3 (8) |
| meatlump_fool | 6 | 8 | 25 | 38 |  | 28 | -4,4 (12); 7,-5 (10); 6,-8 (10); -3,3 (8); -5,3 (7) |
| dalyrake | 1-9 | 15 | 18 | 21 |  | 18 | 2,4 (13); 7,-5 (12); 5,-5 (9); -7,-3 (8); 0,-6 (8) |
| corellian_butterfly_worker | 1-9 | 2 | 15 | 15 |  | 13 | -7,-3 (12); 0,-4 (11); -5,3 (8); 2,5 (8); 4,6 (7) |
| carrion_spat | 1-10 | 5 | 8 | 11 |  | 9 | 2,6 (10); -5,-2 (8); -7,-3 (7); 7,-5 (5); -6,-1 (4) |
| slice_hound | 1-9 | 8 | 6 | 10 |  | 12 | -4,-2 (4); 7,-5 (4); 6,-8 (4); 1,-6 (4); 4,4 (4) |
| female_slice_hound | 1-8 | 14 | 3 | 5 |  | 12 | -5,-1 (5); -5,2 (5); 5,-5 (4); 5,-7 (4); 6,-7 (3) |
| gurrcat | 10 | 3 | 3 | 2 |  | 8 | 5,-7 (14); 0,-4 (4); 0,-6 (4); 2,6 (3); 5,5 (3) |
| canoid | 1-10 | 1 | 6 | 6 |  | 5 | 4,6 (8); -6,-1 (8); -2,4 (7); 0,-6 (3); -6,-3 (1) |
| rogue_bageraset | 1-13 | 2 | 6 | 6 |  | 6 | -2,-6 (8); -5,2 (6); 5,-5 (4); -5,-2 (3); -7,-2 (2) |
| razor_cat_cub | 10 | 11 | 1 | 2 |  | 7 | 2,4 (9); 6,-6 (5); -6,-1 (4); 7,-8 (2); 3,4 (1) |
| humbaba | 1-17 | 2 | 5 | 1 |  | 7 | 7,-7 (6); 4,6 (5); 0,-6 (3); -5,-2 (3); -3,3 (1) |
| meatlump_clod | 8 |  | 4 | 4 |  | 3 | -5,-2 (8); -7,-1 (4); 5,-7 (4) |
| wooded_paralope | 7 | 5 | 1 |  |  | 3 | -2,-4 (6); -1,-4 (5); -1,-5 (5) |
| murra | 1-10 | 1 |  | 1 |  | 6 | 3,3 (5); -5,-2 (3); -2,-5 (3); 1,-5 (2); 1,-6 (2) |
| drall_patriot | 11 | 1 | 3 | 4 |  | 2 | -5,-2 (10); 0,-6 (4) |
| meatlump_oaf | 9 | 1 | 2 | 3 |  | 3 | -2,2 (4); -7,-2 (4); 2,6 (4) |
| meatlump_cretin | 9 | 1 | 2 | 3 |  | 4 | -4,2 (4); -4,-2 (4); -6,3 (2); 1,-4 (1) |
| grecks_assassin | 11 | 1 | 2 | 3 |  | 2 | -3,1 (7); 2,5 (2) |
| agrilat_rasp | 8 | 6 |  |  |  | 1 | -1,-4 (8) |
| drall_guard | 11 | 1 | 1 | 2 |  | 2 | 2,4 (4); 0,-7 (3) |
| meatlump_loon | 10 |  | 2 | 2 |  | 2 | -7,-2 (4); 1,-4 (3) |
| krahbu | 10 |  | 1 | 1 |  | 2 | -5,3 (4); -5,-2 (3) |
| vehement_warrior | 9 | 3 |  | 2 |  | 3 | -7,-3 (3); -4,4 (3); -6,-4 (1) |
| grecks_mugger | 9 | 1 | 1 | 2 |  | 1 | 4,5 (6) |
| hidden_daggers_dissident | 11 |  | 1 | 1 |  | 1 | -1,-4 (4) |
| crazed_durni | 1-10 | 1 |  |  |  | 3 | -2,3 (2); -5,2 (1); 5,-7 (1) |
| drall_sentry | 8 | 2 |  | 2 |  | 2 | 0,-7 (2); -3,1 (2) |
| swooper_gangmember | 9 |  |  | 1 |  | 1 | -2,-4 (4) |
| afarathu_hellion | 15 |  | 1 | 1 |  | 1 | 7,-5 (4) |
| afarathu_cult_leader | 18 |  | 1 | 1 |  | 1 | 7,-5 (3) |
| violent_krahbu | 1 |  | 1 |  |  | 1 | -2,-6 (3) |
| afarathu_cult_bodyguard | 15 |  | 1 | 1 |  | 1 | 7,-5 (3) |
| hidden_daggers_activist | 9 | 1 |  | 1 |  | 1 | 5,-7 (2) |
| diseased_vrelt_matriarch | 11 |  | 1 | 1 |  | 1 | 1,6 (2) |
| dire_cat | 1 | 1 |  |  |  | 1 | -6,-1 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_gubbur_lair_neutral_small | ? | 352 |  |  | 81 | -4,-2 (16); -5,-2 (12); 6,-5 (11); -4,1 (10); 4,5 (10) |
| corellia_paralope_lair_neutral_medium | ? | 345 |  |  | 74 | -1,-4 (15); -5,-2 (15); -6,-2 (12); 0,-4 (12); 5,-6 (11) |
| corellia_meatlump_camp_neutral_medium_theater | ? | 325 |  |  | 77 | -7,-2 (13); 6,-5 (11); 3,6 (11); -7,-4 (10); 2,6 (9) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 209 |  |  | 74 | 2,6 (8); 0,-6 (8); -6,-2 (7); 6,-5 (7); 5,-7 (7) |
| corellia_plumed_rasp_nest_neutral_small | ? | 196 |  |  | 70 | 7,-5 (8); -5,2 (8); 2,6 (8); 5,-6 (7); -7,-4 (7) |
| corellia_scavenger_rat_lair_neutral_small | ? | 122 |  |  | 62 | 0,-6 (7); 5,-7 (6); -5,2 (4); 1,-5 (4); -7,-3 (4) |
| corellia_diseased_vrelt_lair_neutral_boss_02 | ? | 104 |  |  | 49 | 5,-7 (6); 5,-6 (5); 3,6 (4); -5,-2 (4); -6,-2 (4) |
| corellia_giant_gubbur_lair_neutral_medium | ? | 48 |  |  | 30 | 6,-5 (6); 5,-7 (4); -1,-4 (3); 0,-6 (2); 0,-4 (2) |
| corellia_meatlump_outpost_neutral_medium_theater | ? | 46 |  |  | 34 | -7,-2 (3); -5,-2 (3); -1,-3 (3); -5,2 (2); -6,3 (2) |
| corellia_dalyrake_lair_neutral_medium | ? | 44 |  |  | 28 | 0,-6 (3); 3,4 (3); 5,-7 (3); 7,-5 (2); 7,-8 (2) |
| corellia_slice_hound_lair_neutral_medium | ? | 41 |  |  | 30 | -4,-2 (4); 6,-7 (3); 0,-6 (3); -7,-2 (3); 6,-5 (2) |
| corellia_vynock_lair_neutral_small | ? | 37 |  |  | 28 | -5,-1 (3); -4,4 (3); 5,-7 (2); 0,-4 (2); 4,5 (2) |
| corellia_corellian_butterfly_pod_neutral_small | ? | 33 |  |  | 23 | 0,-4 (4); -4,4 (3); -5,4 (3); -5,3 (2); -5,2 (2) |
| corellia_krahbu_lair_neutral_medium | ? | 9 |  |  | 8 | -1,-3 (2); 0,-6 (1); 4,-7 (1); -5,3 (1); 1,-5 (1) |
| corellia_hidden_daggers_camp_neutral_medium_theater | ? | 9 |  |  | 8 | -1,-4 (2); 6,-7 (1); -4,-2 (1); 5,-7 (1); -3,2 (1) |
| corellia_gurrcat_lair_neutral_medium | ? | 9 |  |  | 7 | 5,-7 (3); -5,-1 (1); 0,-6 (1); -3,1 (1); -2,3 (1) |
| corellia_greck_base_neutral_large_theater | ? | 8 |  |  | 8 | 0,-6 (1); -6,4 (1); -7,-2 (1); -3,1 (1); -4,4 (1) |
| corellia_carrion_spat_lair_neutral_medium_boss_01 | ? | 8 |  |  | 8 | -6,-1 (1); -7,-3 (1); -5,-2 (1); 2,6 (1); -3,2 (1) |
| corellia_drall_patriot_camp_neutral_medium_theater | ? | 6 |  |  | 6 | 2,4 (1); 0,-6 (1); 0,-7 (1); -5,-2 (1); -3,1 (1) |
| corellia_canoid_lair_neutral_medium | ? | 6 |  |  | 6 | -2,4 (1); 4,6 (1); -6,-1 (1); -3,3 (1); 0,-6 (1) |
| corellia_swooper_camp_neutral_small_theater | ? | 6 |  |  | 6 | -5,1 (1); 6,-8 (1); 0,-6 (1); -2,-4 (1); 7,-4 (1) |
| corellia_lord_nyax_chapel_neutral_medium_theater | ? | 6 |  |  | 6 | -1,-6 (1); 0,-6 (1); -7,-2 (1); 3,3 (1); -5,-3 (1) |
| corellia_bageraset_lair_neutral_medium_boss_01 | ? | 5 |  |  | 5 | -1,-3 (1); -2,2 (1); 4,4 (1); 7,-7 (1); 5,-7 (1) |
| corellia_murra_lair_neutral_medium | ? | 5 |  |  | 5 | -5,-2 (1); -7,-3 (1); -2,-5 (1); 3,3 (1); -5,2 (1) |
| corellia_tabage_lair_neutral_medium | ? | 1 |  |  | 1 | 4,3 (1) |

