# Corellia: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:33 AM to 1:01 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 451 (0 explorers, 271 that killed something).
- Coverage: 83 of 256 squares of 1 km had a bot or a sighting in them (32%); explorers stood in 0.
- Templates: 34 creatures, 17 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gubbur | 1-6 | 348 | 32 | 277 |  | 47 | -5,3 (52); 4,4 (41); -4,4 (40); -5,-2 (37); 7,-6 (37) |
| paralope | 1-6 | 326 | 34 | 244 |  | 37 | -4,3 (52); -5,3 (51); -5,-2 (50); 2,6 (44); 5,-7 (41) |
| durni | 1-7 | 293 | 31 | 97 |  | 32 | -4,3 (110); 4,5 (42); 5,-7 (38); -3,2 (34); 1,5 (26) |
| howling_plumed_rasp | 4 | 234 | 2 | 178 |  | 18 | -1,-4 (87); -5,-2 (39); -3,3 (34); 0,-6 (30); 0,-5 (28) |
| plumed_rasp | 1-7 | 120 | 12 | 121 |  | 25 | -5,-2 (30); 1,-4 (25); 2,4 (19); 6,-7 (19); 2,5 (18) |
| giant_gubbur | 9 | 37 | 44 | 83 |  | 25 | 2,6 (26); 0,-5 (23); -5,-3 (22); 0,-4 (20); -3,3 (18) |
| corellian_butterfly_drone | 5 | 215 |  |  |  | 15 | -4,3 (62); -4,2 (40); 0,-5 (23); 3,4 (23); -1,-6 (15) |
| scavenger_rat | 8 | 25 | 38 | 56 |  | 19 | -3,2 (30); 6,-7 (16); -6,-2 (15); -2,-4 (14); 0,-6 (14) |
| meatlump_stooge | 7 | 29 | 26 | 56 |  | 24 | -5,4 (16); -2,3 (14); -5,-2 (12); 5,-7 (12); -3,3 (11) |
| minor_gubbur | 4 | 157 |  |  |  | 16 | -4,3 (43); -4,2 (20); -5,3 (20); 2,5 (13); -1,-6 (11) |
| corellian_butterfly | 1-7 | 138 |  |  |  | 15 | 2,4 (43); -6,-3 (22); 7,-6 (18); 6,-6 (13); 7,-7 (12) |
| diseased_vrelt | 1-8 | 14 | 27 | 40 |  | 9 | 4,5 (34); 2,6 (30); 4,4 (14); 6,-7 (14); 5,-6 (12) |
| meatlump_fool | 6 | 36 | 7 | 43 |  | 17 | 0,-5 (13); 7,-5 (13); 1,-5 (12); -7,-3 (9); -8,-3 (8) |
| bloated_gubbur | 6 | 103 |  |  |  | 8 | -1,-5 (28); -6,-2 (21); 6,-6 (19); 3,4 (13); 2,5 (10) |
| meatlump_buffoon | 5 | 40 | 3 | 43 |  | 15 | 7,-5 (13); 2,6 (12); 1,-5 (12); -7,-3 (11); 7,-7 (8) |
| vrelt | 6 | 78 |  |  |  | 4 | -4,3 (40); -4,2 (28); -5,-2 (7); 0,-4 (3) |
| corellian_butterfly_worker | 1-9 | 2 | 14 | 16 |  | 7 | 1,4 (12); 6,-5 (10); -4,1 (8); 6,-8 (8); 1,3 (8) |
| rogue_corsec_trooper | 7 | 38 | 1 | 6 |  | 2 | -4,3 (34); -6,-3 (12) |
| dalyrake | 9 |  | 9 | 9 |  | 5 | 6,-7 (10); 5,-8 (8); 0,-3 (8); 7,-7 (6); 1,-5 (4) |
| krahbu | 10 |  | 8 | 8 |  | 3 | 2,5 (16); 7,-7 (12); -4,-2 (4) |
| slice_hound | 9 |  | 6 | 7 |  | 4 | -3,2 (8); 4,6 (8); -5,4 (7); 1,-5 (4) |
| vynock | 1-9 | 5 | 4 | 5 |  | 5 | 1,4 (10); -4,-2 (8); 6,-6 (2); -4,2 (1); -3,1 (1) |
| meatlump_clod | 8 |  | 5 | 5 |  | 2 | 4,5 (16); -5,-2 (4) |
| meatlump_loon | 10 |  | 4 | 4 |  | 2 | 4,3 (8); -5,4 (8) |
| meatlump_cretin | 9 |  | 3 | 3 |  | 1 | 6,-5 (12) |
| canoid | 10 |  | 3 | 3 |  | 1 | -3,4 (12) |
| crazed_durni | 10 |  | 3 | 3 |  | 3 | 0,-4 (5); -3,4 (4); -2,-4 (3) |
| meatlump_oaf | 9 | 1 | 2 | 3 |  | 2 | -4,-2 (8); -3,1 (2) |
| drall_patriot | 11 |  | 2 | 2 |  | 1 | -3,2 (8) |
| flail_enforcer | 19 |  | 2 | 2 |  | 1 | -5,-2 (6) |
| female_slice_hound | 8 |  | 1 | 1 |  | 1 | -5,4 (4) |
| bageraset | 10 | 2 |  | 2 |  | 1 | -4,1 (4) |
| flail_executioner | 25 |  | 1 | 1 |  | 1 | -5,-2 (4) |
| ragtag_kook | 5 | 1 |  | 1 |  | 1 | -4,3 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_gubbur_lair_neutral_small | ? | 49 | 120 |  | 39 | 7,-6 (11); -5,3 (8); -4,4 (8); 4,4 (8); 5,-5 (7) |
| corellia_paralope_lair_neutral_medium | ? | 46 | 101 |  | 34 | -5,-2 (16); -5,3 (10); 2,6 (10); 5,-7 (10); 3,4 (10) |
| corellia_meatlump_camp_neutral_medium_theater | ? | 39 | 98 |  | 28 | 7,-5 (16); -5,-2 (8); 2,6 (8); 1,-5 (8); -2,3 (7) |
| corellia_plumed_rasp_nest_neutral_small | ? | 26 | 61 |  | 23 | -5,-2 (8); 6,-7 (8); 1,-4 (7); 5,-6 (6); 2,4 (5) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 24 | 60 |  | 16 | 4,5 (15); 5,-7 (10); -3,2 (9); 1,5 (7); 5,-6 (6) |
| corellia_scavenger_rat_lair_neutral_small | ? | 18 | 47 |  | 18 | -3,2 (8); 6,-7 (5); 1,-5 (5); -2,-4 (5); -3,4 (4) |
| corellia_corellian_butterfly_pod_neutral_small | ? | 7 | 16 |  | 8 | 6,-5 (4); 1,4 (4); -4,1 (3); 6,-8 (3); 1,3 (3) |
| corellia_meatlump_outpost_neutral_medium_theater | ? | 7 | 15 |  | 7 | 4,5 (5); 6,-5 (4); 4,3 (3); -4,-2 (3); -5,4 (3) |
| corellia_diseased_vrelt_lair_neutral_boss_02 | ? | 9 | 6 |  | 7 | 4,5 (3); 2,6 (3); 5,-6 (2); 4,6 (2); 4,4 (2) |
| corellia_dalyrake_lair_neutral_medium | ? | 4 | 9 |  | 4 | 6,-7 (5); 5,-8 (3); 0,-3 (3); 1,-5 (2) |
| corellia_giant_gubbur_lair_neutral_medium | ? | 6 | 7 |  | 6 | -5,-3 (3); 0,-4 (2); 0,-5 (2); 2,6 (2); 6,-8 (2) |
| corellia_slice_hound_lair_neutral_medium | ? | 4 | 8 |  | 4 | -5,4 (4); -3,2 (3); 4,6 (3); 1,-5 (2) |
| corellia_krahbu_lair_neutral_medium | ? | 3 | 8 |  | 3 | 2,5 (5); 7,-7 (4); -4,-2 (2) |
| corellia_vynock_lair_neutral_small | ? | 2 | 4 |  | 2 | -4,-2 (3); 1,4 (3) |
| corellia_canoid_lair_neutral_medium | ? | 1 | 3 |  | 1 | -3,4 (4) |
| corellia_drall_patriot_camp_neutral_medium_theater | ? | 1 | 2 |  | 1 | -3,2 (3) |
| corellia_bageraset_lair_neutral_medium_boss_01 | ? | 1 | 2 |  | 1 | -4,1 (3) |

