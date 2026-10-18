# Corellia: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:05 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 219 (0 explorers, 95 that killed something).
- Coverage: 60 of 256 squares of 1 km had a bot or a sighting in them (23%); explorers stood in 0.
- Templates: 24 creatures, 5 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| howling_plumed_rasp | 4 | 193 | 5 | 140 |  | 23 | 6,-6 (50); 6,-7 (39); -1,-4 (31); 3,6 (29); 2,5 (24) |
| paralope | 1-6 | 197 | 5 | 87 |  | 18 | 0,-6 (48); -4,3 (45); -4,2 (27); -3,2 (22); -7,-3 (22) |
| gubbur | 1-6 | 186 | 10 | 66 |  | 26 | -4,4 (32); 6,-5 (24); 3,5 (21); -5,-3 (20); -3,2 (20) |
| durni | 1-7 | 265 | 1 | 9 |  | 23 | -4,3 (57); 3,5 (27); -6,-3 (23); 2,5 (20); 7,-6 (17) |
| corellian_butterfly_drone | 5 | 242 |  |  |  | 19 | -4,3 (47); -4,2 (43); 2,5 (26); 3,4 (19); -6,-3 (15) |
| minor_gubbur | 4 | 192 |  | 3 |  | 13 | -4,3 (51); 0,-5 (40); -4,2 (37); 3,4 (23); 6,-6 (17) |
| bloated_gubbur | 6 | 94 |  |  |  | 10 | -6,-2 (21); 2,4 (19); 6,-6 (15); 6,-7 (13); 6,-5 (12) |
| meatlump_stooge | 7 | 25 | 5 | 30 |  | 15 | -4,4 (10); 3,6 (10); -1,-6 (9); -4,-2 (8); 1,-4 (7) |
| plumed_rasp | 1-7 | 37 | 2 | 31 |  | 7 | -4,-2 (20); 4,4 (17); -7,-2 (15); 0,-4 (8); 0,-5 (8) |
| rogue_corsec_trooper | 7 | 51 |  | 18 |  | 2 | -4,3 (54); -6,-3 (17) |
| corellian_butterfly | 1-7 | 62 |  |  |  | 11 | 6,-7 (24); 0,-5 (14); -1,-4 (9); 6,-6 (8); -1,-6 (3) |
| meatlump_fool | 6 | 20 | 5 | 25 |  | 12 | -7,-3 (11); 3,4 (10); -4,4 (8); -6,-1 (8); -4,-2 (6) |
| scavenger_rat | 8 | 52 | 1 |  |  | 14 | -5,-3 (9); -1,-4 (8); 6,-6 (7); 3,5 (6); -6,-2 (5) |
| vrelt | 6 | 37 |  |  |  | 3 | -4,3 (20); -4,2 (16); 3,4 (1) |
| crazed_durni | 1-10 | 1 | 9 | 8 |  | 7 | 3,4 (8); 1,-5 (7); 7,-5 (7); 3,6 (4); -1,-4 (4) |
| meatlump_buffoon | 5 | 11 | 1 | 12 |  | 8 | -6,-1 (8); -4,-2 (6); -5,-3 (4); 7,-5 (4); -7,-2 (4) |
| giant_gubbur | 9 | 4 | 4 | 8 |  | 5 | -5,-2 (12); 6,-7 (4); 3,4 (4); -3,4 (4); 3,6 (2) |
| vynock | 1-9 | 4 |  |  |  | 5 | 0,-5 (1); -5,-2 (1); -4,-2 (1); 4,5 (1); -1,-5 (1) |
| flail_cutthroat | 15 |  | 2 | 2 |  | 1 | -5,-2 (5) |
| diseased_vrelt | 8 | 2 |  | 1 |  | 1 | -6,-4 (3) |
| murra | 10 |  | 1 |  |  | 1 | 0,-5 (3) |
| flail_executioner | 25 |  | 1 | 1 |  | 1 | -5,-2 (2) |
| agrilat_rasp | 8 | 1 |  |  |  | 1 | -1,-5 (1) |
| razor_cat_cub | 10 | 1 |  |  |  | 1 | 6,-6 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_meatlump_camp_neutral_medium_theater | ? | 23 | 42 |  | 19 | -5,-3 (6); -4,4 (6); 3,4 (6); -4,-2 (5); -1,-6 (5) |
| corellia_paralope_lair_neutral_medium | ? | 14 | 30 |  | 12 | 7,-5 (6); -3,2 (5); -7,-3 (5); 0,-6 (4); 1,-6 (4) |
| corellia_gubbur_lair_neutral_small | ? | 13 | 23 |  | 12 | -4,4 (6); 6,-5 (5); -3,2 (4); 4,6 (3); 6,-4 (3) |
| corellia_plumed_rasp_nest_neutral_small | ? | 5 | 10 |  | 6 | 4,4 (4); -4,-2 (3); 0,-4 (2); 0,-5 (2); -7,-2 (2) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 2 | 3 |  | 2 | 3,3 (3); 3,7 (2) |

