# Corellia: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:26 AM to 3:08 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 235 (0 explorers, 101 that killed something).
- Coverage: 45 of 256 squares of 1 km had a bot or a sighting in them (18%); explorers stood in 0.
- Templates: 19 creatures, 5 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| corellian_butterfly_drone | 5 | 216 |  |  |  | 19 | -4,2 (38); 0,-5 (35); -4,3 (32); 6,-7 (20); -1,-6 (15) |
| gubbur | 1-6 | 148 | 2 | 31 |  | 19 | 4,5 (28); 6,-7 (23); 6,-6 (22); -1,-6 (17); -6,-3 (17) |
| howling_plumed_rasp | 4 | 103 | 1 | 63 |  | 15 | 7,-6 (33); -6,-3 (22); 6,-6 (18); -7,-3 (12); 6,-7 (10) |
| durni | 1-7 | 131 | 2 | 17 |  | 20 | -4,3 (32); -1,-4 (21); -5,3 (19); 6,-6 (15); 3,5 (10) |
| minor_gubbur | 4 | 135 |  |  |  | 12 | -4,3 (34); -4,2 (28); -1,-6 (16); 6,-6 (14); 0,-5 (14) |
| paralope | 1-6 | 93 | 3 | 28 |  | 10 | -4,3 (31); -4,2 (24); 0,-5 (22); 4,4 (19); -7,-3 (14) |
| corellian_butterfly | 1-7 | 84 |  |  |  | 12 | 7,-6 (30); 2,5 (9); 7,-7 (9); 0,-5 (8); -6,-3 (6) |
| meatlump_stooge | 7 | 14 | 3 | 17 |  | 9 | 7,-4 (9); 6,-5 (8); -8,-3 (7); 4,5 (6); -4,4 (6) |
| rogue_corsec_trooper | 7 | 35 |  | 7 |  | 2 | -4,3 (33); -6,-3 (9) |
| bloated_gubbur | 6 | 37 |  |  |  | 7 | 6,-7 (10); 7,-7 (10); -6,-2 (5); 2,5 (4); 3,4 (3) |
| vrelt | 6 | 29 |  |  |  | 3 | -4,3 (14); -4,2 (12); 0,-4 (3) |
| meatlump_fool | 6 | 6 | 1 | 8 |  | 5 | -3,2 (8); -4,1 (5); -7,-2 (2); 4,5 (2); 6,-5 (2) |
| meatlump_buffoon | 5 | 6 |  | 7 |  | 6 | 4,5 (4); 2,3 (3); -4,4 (3); -7,-2 (2); -4,1 (2) |
| scavenger_rat | 8 | 15 |  |  |  | 7 | -4,2 (4); -6,-3 (4); 3,5 (3); 7,-6 (1); 2,5 (1) |
| giant_gubbur | 9 | 4 | 2 | 6 |  | 3 | 4,5 (6); 2,4 (4); -7,-2 (4) |
| plumed_rasp | 7 | 4 |  | 4 |  | 1 | 3,7 (11) |
| vynock | 1-9 | 4 |  |  |  | 3 | -6,-3 (3); 7,-6 (2); 2,5 (1) |
| crazed_durni | 10 |  | 1 | 1 |  | 1 | -1,-4 (3) |
| ragtag_kook | 5 | 1 |  | 1 |  | 1 | -4,3 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_meatlump_camp_neutral_medium_theater | ? | 9 | 25 |  | 10 | 6,-5 (7); -3,2 (7); -4,4 (4); -7,-2 (3); -4,1 (3) |
| corellia_paralope_lair_neutral_medium | ? | 7 | 17 |  | 6 | 0,-5 (7); 4,4 (5); 6,-4 (4); -7,-3 (3); -5,2 (3) |
| corellia_gubbur_lair_neutral_small | ? | 5 | 13 |  | 4 | 6,-7 (7); 4,5 (6); -1,-6 (4); 6,-8 (1) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 2 | 7 |  | 2 | -5,3 (5); -1,-4 (4) |
| corellia_plumed_rasp_nest_neutral_small | ? | 1 | 2 |  | 1 | 3,7 (3) |

