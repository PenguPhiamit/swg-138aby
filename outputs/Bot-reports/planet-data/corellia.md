# Corellia: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:03 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 416 (0 explorers, 268 that killed something).
- Coverage: 61 of 256 squares of 1 km had a bot or a sighting in them (24%); explorers stood in 0.
- Templates: 17 creatures, 5 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| durni | 1-7 | 486 |  | 9 |  | 20 | -4,3 (114); 3,5 (56); 6,-7 (51); -6,-2 (48); -1,-5 (42) |
| corellian_butterfly_drone | 5 | 485 |  | 2 |  | 19 | -4,3 (103); 7,-6 (85); -5,-3 (64); -4,2 (47); 2,5 (42) |
| gubbur | 1-6 | 323 | 10 | 60 |  | 27 | 3,5 (34); 3,6 (34); 6,-6 (33); -7,-3 (31); -6,-2 (26) |
| howling_plumed_rasp | 4 | 271 | 2 | 107 |  | 15 | 6,-6 (55); 7,-6 (49); -1,-5 (43); 6,-7 (42); -1,-4 (42) |
| paralope | 1-6 | 239 | 9 | 83 |  | 23 | -4,3 (96); -4,2 (55); 1,5 (31); 0,-6 (17); 7,-7 (16) |
| minor_gubbur | 4 | 269 |  | 1 |  | 16 | -4,2 (79); -4,3 (68); 3,6 (33); -6,-2 (20); -5,-2 (19) |
| corellian_butterfly | 1-7 | 257 |  | 1 |  | 15 | 6,-7 (69); -6,-3 (38); 7,-7 (26); 6,-6 (23); -1,-6 (20) |
| bloated_gubbur | 6 | 191 |  |  |  | 10 | 6,-7 (69); 3,4 (30); -6,-3 (29); -1,-6 (13); 2,5 (12) |
| vrelt | 6 | 146 |  | 1 |  | 3 | -4,3 (85); -4,2 (45); 0,-4 (17) |
| scavenger_rat | 8 | 119 |  | 2 |  | 12 | 3,4 (33); 6,-6 (24); -1,-4 (19); -6,-4 (15); -5,-3 (10) |
| meatlump_stooge | 7 | 11 | 8 | 20 |  | 13 | -4,4 (9); -4,1 (8); -6,-2 (8); -5,2 (7); -5,4 (6) |
| meatlump_fool | 6 | 14 | 7 | 21 |  | 10 | -3,2 (14); 3,7 (10); 5,-6 (6); -7,-2 (6); -4,-2 (6) |
| rogue_corsec_trooper | 7 | 46 |  | 4 |  | 2 | -4,3 (37); -6,-3 (13) |
| giant_gubbur | 9 | 8 | 2 | 11 |  | 9 | -5,-2 (5); 5,-7 (4); 0,-5 (3); -1,-4 (2); -4,1 (2) |
| meatlump_buffoon | 5 | 5 |  | 6 |  | 5 | -4,1 (4); 5,-5 (2); 4,5 (2); -7,-2 (2); -3,2 (2) |
| plumed_rasp | 7 | 3 | 1 | 4 |  | 1 | 6,-5 (12) |
| vynock | 1 | 6 |  |  |  | 4 | 6,-6 (2); -4,2 (2); -5,-3 (1); 5,-6 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_meatlump_camp_neutral_medium_theater | ? | 21 | 34 |  | 19 | -3,2 (8); -4,1 (6); -7,-2 (6); -5,2 (4); -4,4 (4) |
| corellia_paralope_lair_neutral_medium | ? | 19 | 31 |  | 18 | 1,5 (7); -7,-3 (5); 7,-7 (4); -1,-3 (4); 2,3 (3) |
| corellia_gubbur_lair_neutral_small | ? | 15 | 25 |  | 13 | -7,-3 (9); -5,2 (5); 5,-6 (3); 4,4 (3); 1,5 (3) |
| corellia_plumed_rasp_nest_neutral_small | ? | 1 | 2 |  | 1 | 6,-5 (3) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 1 | 1 |  | 1 | 4,4 (2) |

