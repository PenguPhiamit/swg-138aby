# Tatooine: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:25 AM to 3:08 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 230 (0 explorers, 141 that killed something).
- Coverage: 69 of 256 squares of 1 km had a bot or a sighting in them (27%); explorers stood in 0.
- Templates: 22 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 504 | 12 | 367 |  | 45 | -1,-4 (48); 1,-5 (45); -5,2 (45); -1,-3 (40); -2,-3 (36) |
| dwarf_nuna | 1-5 | 251 |  | 45 |  | 21 | -1,-4 (45); 1,2 (27); -1,-6 (25); 1,3 (24); 0,-6 (20) |
| tatooine_mynock | 1-3 | 116 |  | 92 |  | 13 | -2,1 (36); 2,-5 (26); 0,-4 (18); 5,-6 (18); 0,4 (16) |
| gorg | 6 | 156 |  | 27 |  | 14 | 0,-6 (60); 0,-7 (19); -3,2 (16); 4,-3 (16); 4,-6 (14) |
| womp_rat | 1-10 | 2 | 33 | 35 |  | 16 | -1,-3 (24); 3,-7 (21); 0,3 (16); -3,-4 (12); 4,-4 (12) |
| rill | 1-6 | 111 |  | 2 |  | 8 | 0,-6 (40); -2,-5 (31); 3,-6 (17); -4,2 (15); 4,-5 (3) |
| evil_settler | 5 | 49 |  | 21 |  | 7 | -1,-6 (40); 0,-3 (9); -1,-5 (8); -2,-5 (5); 0,-7 (4) |
| gorg_glutton | 7 | 68 | 1 |  |  | 7 | -1,-6 (43); 1,3 (15); -3,2 (6); 3,-6 (2); -1,-4 (1) |
| sevorrt | 7 | 15 | 10 | 16 |  | 7 | 3,-5 (20); 1,4 (17); 0,-6 (8); 0,4 (5); 0,-5 (4) |
| lesser_desert_womp_rat | 5 | 52 |  |  |  | 3 | 3,-5 (48); 2,-5 (2); 3,-6 (2) |
| worrt | 6 | 37 |  |  |  | 3 | 3,-5 (26); 3,-6 (10); 1,-5 (1) |
| highwayman | 10 | 1 | 12 | 14 |  | 7 | 3,-4 (9); 3,-5 (6); 2,-5 (5); 3,-7 (3); 0,-5 (3) |
| trandosian_slaver | 5 | 7 |  | 7 |  | 4 | 0,-3 (6); 3,-4 (6); -1,-7 (4); 1,-5 (1) |
| death_kreetle | 9 | 4 | 3 | 6 |  | 6 | 3,-4 (5); 0,-7 (4); 1,-5 (2); 1,4 (2); -1,-5 (2) |
| domestic_eopie | 4 | 14 |  |  |  | 3 | -1,-6 (12); -1,-4 (1); 0,-6 (1) |
| dwarf_eopie | 3 | 10 |  | 4 |  | 3 | 3,-5 (12); 3,-6 (1); 4,-6 (1) |
| minor_worrt | 5 | 11 |  |  |  | 2 | -3,1 (10); -4,1 (1) |
| trandosian_slavemaster | 7 | 4 | 1 | 5 |  | 2 | 1,-5 (9); -1,-7 (2) |
| evil_hermit | 6 | 3 | 1 | 4 |  | 3 | 0,-7 (4); 0,-6 (2); 4,-4 (2) |
| rockmite | 1-8 | 7 |  |  |  | 2 | 3,-5 (6); 3,-6 (1) |
| drooling_nuna | 6 | 3 |  | 2 |  | 3 | 2,-6 (2); -1,3 (2); 0,4 (1) |
| cu_pa | 1 | 1 |  |  |  | 1 | 3,-5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_kreetle_lair_neutral_small | ? | 28 | 46 |  | 24 | -2,-6 (6); 3,3 (6); -1,-3 (5); 1,-6 (5); -3,-4 (5) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 18 | 36 |  | 17 | 1,-5 (9); -1,-5 (6); -1,-4 (4); 0,-7 (4); -3,-3 (3) |
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 16 | 34 |  | 14 | -1,-3 (8); 3,-7 (7); 0,3 (5); -3,-4 (4); -3,3 (4) |
| tatooine_tatooine_mynock_lair_neutral_small | ? | 17 | 30 |  | 14 | 2,-5 (9); -2,1 (5); 0,4 (4); -5,3 (4); -4,1 (4) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 7 | 17 |  | 8 | -1,3 (7); 0,4 (4); -3,2 (3); 2,-6 (3); -2,-7 (2) |
| tatooine_gorg_lair_neutral_small | ? | 4 | 10 |  | 4 | 0,-7 (4); 4,-3 (4); 4,-6 (3); -1,-3 (3) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 5 | 6 |  | 4 | 1,-5 (4); 0,-3 (3); 3,-4 (2); -1,-7 (2) |
| tatooine_sevorrt_lair_neutral_medium | ? | 1 | 3 |  | 1 | 1,4 (4) |
| tatooine_rockmite_click_neutral_small | ? | 1 | 1 |  | 1 | 5,-5 (2) |

