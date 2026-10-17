# Corellia: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:32 PM to 12:31 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 825 (0 explorers, 208 that killed something).
- Coverage: 82 of 256 squares of 1 km had a bot or a sighting in them (32%); explorers stood in 0.
- Templates: 30 creatures, 16 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 205 | 9 | 107 |  | 37 | -4,2 (56); -4,3 (47); 7,-5 (21); -3,2 (19); -1,-6 (19) |
| corellian_butterfly_drone | 5 | 289 | 2 |  |  | 28 | -4,3 (87); -1,-4 (49); -4,2 (46); 0,-5 (32); 6,-7 (27) |
| gubbur | 1-6 | 172 | 7 | 80 |  | 34 | 3,5 (30); 1,-5 (29); 4,5 (26); 3,4 (23); 3,6 (23) |
| howling_plumed_rasp | 4 | 163 | 1 | 84 |  | 24 | 6,-6 (39); 7,-6 (31); -1,-4 (30); 6,-7 (21); -1,-6 (21) |
| minor_gubbur | 4 | 165 |  |  |  | 20 | -4,3 (82); -4,2 (34); 3,4 (16); -1,-6 (15); -3,4 (7) |
| durni | 1-7 | 114 | 2 | 17 |  | 33 | -4,3 (43); 3,5 (20); -1,-6 (15); 6,-7 (9); 2,4 (8) |
| corellian_butterfly | 1-7 | 120 | 4 |  |  | 19 | 3,4 (32); -1,-4 (23); 7,-6 (16); 7,-7 (15); 6,-7 (14) |
| plumed_rasp | 1-7 | 54 | 4 | 48 |  | 18 | 7,-7 (31); 6,-5 (16); 1,5 (12); -1,-4 (9); 1,-5 (9) |
| giant_gubbur | 9 | 9 | 24 | 32 |  | 14 | 5,-5 (14); 5,-6 (12); 1,5 (12); 3,4 (11); 6,-5 (10) |
| diseased_vrelt | 1-8 | 13 | 18 | 27 |  | 9 | 5,-5 (22); -3,4 (21); -4,4 (16); -1,-4 (13); 1,-4 (8) |
| scavenger_rat | 8 | 23 | 13 | 18 |  | 11 | 0,-4 (16); -3,4 (14); -5,-1 (12); -1,-3 (11); 5,-5 (10) |
| vrelt | 6 | 66 | 1 |  |  | 6 | -4,3 (36); -4,2 (30); -3,3 (5); -3,2 (2); -6,3 (2) |
| meatlump_fool | 6 | 12 | 8 | 20 |  | 11 | 6,-5 (17); 5,-5 (8); 1,-5 (7); -1,-4 (6); -3,3 (5) |
| meatlump_stooge | 7 | 9 | 9 | 17 |  | 10 | -5,2 (12); -4,4 (10); 4,6 (8); -4,2 (7); -3,2 (6) |
| rogue_corsec_trooper | 7 | 42 | 1 | 4 |  | 2 | -4,3 (48); -6,-3 (2) |
| bloated_gubbur | 6 | 44 | 1 |  |  | 7 | -1,-4 (18); 3,4 (9); 4,5 (9); -1,-6 (6); -3,3 (5) |
| vynock | 1-9 | 6 | 5 | 5 |  | 7 | 7,-5 (12); 4,5 (8); 7,-6 (2); 6,-5 (1); 4,6 (1) |
| meatlump_buffoon | 5 | 8 |  | 8 |  | 7 | 6,-5 (7); 4,-6 (2); 5,-5 (2); 1,-5 (2); -4,-2 (2) |
| gurrcat | 10 |  | 2 | 2 |  | 1 | -4,1 (9) |
| slice_hound | 1-9 | 3 | 1 | 1 |  | 4 | 6,-4 (4); 6,-6 (2); 3,5 (1); 6,-5 (1) |
| corellian_butterfly_worker | 1-9 | 2 | 1 | 1 |  | 2 | 5,4 (5); -1,-5 (2) |
| womp_rat | 1-10 |  |  |  |  | 3 | 5,-6 (3); 6,-5 (2); 4,-6 (2) |
| dalyrake | 9 |  | 1 | 1 |  | 1 | 5,-5 (5) |
| female_slice_hound | 1-8 | 5 |  |  |  | 4 | 3,5 (2); 4,5 (1); 1,5 (1); 6,-5 (1) |
| meatlump_loon | 10 |  | 1 | 1 |  | 1 | -7,-3 (5) |
| krahbu | 10 |  | 1 | 1 |  | 1 | 2,4 (4) |
| tatooine_mynock | 3 |  |  |  |  | 1 | 7,-8 (2) |
| flesh_eating_chuba | 6 |  |  |  |  | 1 | 6,-8 (1) |
| evil_hermit | 6 |  |  |  |  | 1 | 4,-6 (1) |
| fearful_fynock_youth | 5 |  |  |  |  | 1 | 6,-7 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_paralope_lair_neutral_medium | ? | 46 | 94 |  | 35 | -3,3 (9); 6,-4 (8); 7,-5 (6); -3,2 (6); 5,-6 (6) |
| corellia_gubbur_lair_neutral_small | ? | 47 | 88 |  | 34 | 1,-5 (12); 5,-7 (10); -3,2 (9); 5,-6 (9); 3,6 (7) |
| corellia_meatlump_camp_neutral_medium_theater | ? | 41 | 82 |  | 28 | 6,-5 (17); -4,4 (9); -5,2 (7); 4,-6 (7); -1,-6 (6) |
| corellia_plumed_rasp_nest_neutral_small | ? | 34 | 66 |  | 25 | 6,-5 (13); 7,-7 (13); 3,3 (9); 1,5 (8); 4,6 (6) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 28 | 49 |  | 24 | 7,-7 (10); 6,-4 (6); 1,-5 (5); -5,2 (4); 2,4 (4) |
| corellia_diseased_vrelt_lair_neutral_boss_02 | ? | 13 | 26 |  | 13 | 1,5 (5); -4,4 (4); -3,4 (4); 4,6 (3); 1,-4 (3) |
| corellia_scavenger_rat_lair_neutral_small | ? | 11 | 26 |  | 10 | -3,4 (7); 0,-4 (5); 2,4 (4); -1,-3 (4); 7,-7 (3) |
| corellia_giant_gubbur_lair_neutral_medium | ? | 7 | 16 |  | 7 | -3,1 (4); 4,5 (4); 5,-5 (4); 1,5 (3); -3,4 (3) |
| corellia_slice_hound_lair_neutral_medium | ? | 7 | 11 |  | 7 | 1,5 (3); 4,5 (3); 5,-6 (3); 6,-5 (3); -3,4 (2) |
| corellia_corellian_butterfly_pod_neutral_small | ? | 4 | 8 |  | 4 | -1,-6 (4); -5,2 (3); 5,4 (3); -7,-3 (2) |
| corellia_vynock_lair_neutral_small | ? | 3 | 8 |  | 3 | 7,-5 (5); 4,5 (3); 4,4 (3) |
| corellia_dalyrake_lair_neutral_medium | ? | 3 | 5 |  | 3 | -5,2 (3); 5,-5 (3); -3,1 (2) |
| corellia_gurrcat_lair_neutral_medium | ? | 1 | 3 |  | 1 | -4,1 (4) |
| corellia_krahbu_lair_neutral_medium | ? | 1 | 2 |  | 1 | 2,4 (3) |
| corellia_meatlump_outpost_neutral_medium_theater | ? | 1 | 2 |  | 1 | -7,-3 (3) |
| corellia_hidden_daggers_camp_neutral_medium_theater | ? | 1 | 1 |  | 1 | 6,-7 (2) |

