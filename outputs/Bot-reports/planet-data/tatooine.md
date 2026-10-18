# Tatooine: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:05 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 528 (0 explorers, 331 that killed something).
- Coverage: 90 of 256 squares of 1 km had a bot or a sighting in them (35%); explorers stood in 0.
- Templates: 29 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 2702 | 84 | 2055 |  | 78 | -1,-5 (220); -2,-3 (163); 0,-6 (139); 0,-4 (139); 0,2 (134) |
| tatooine_mynock | 1-3 | 1031 | 3 | 792 |  | 62 | 2,3 (96); 0,3 (87); -3,-4 (84); 1,4 (63); 2,2 (61) |
| dwarf_nuna | 1-5 | 969 | 9 | 323 |  | 49 | 0,-6 (87); -1,-6 (75); 3,-6 (71); -3,1 (66); 1,2 (61) |
| womp_rat | 1-10 | 30 | 256 | 276 |  | 61 | -1,-5 (90); -3,3 (54); 5,-5 (48); 0,-4 (44); 4,-5 (38) |
| gorg | 6 | 508 | 4 | 100 |  | 33 | 1,3 (85); -3,2 (50); -2,-4 (47); -3,-5 (46); -3,1 (37) |
| sevorrt | 1-7 | 127 | 46 | 106 |  | 32 | 3,-6 (51); -1,-6 (45); 0,-6 (43); -3,-4 (27); 0,-5 (26) |
| gorg_glutton | 7 | 302 |  | 3 |  | 18 | -1,-6 (90); 1,2 (48); 0,-6 (37); -4,2 (29); 1,3 (28) |
| evil_settler | 5 | 159 | 6 | 116 |  | 22 | -1,-6 (73); 0,-5 (48); -2,-4 (34); -1,-5 (16); -1,-3 (14) |
| highwayman | 10 | 8 | 110 | 115 |  | 14 | 3,-5 (64); 0,-6 (57); 4,-6 (29); 2,-5 (26); 1,-5 (21) |
| rill | 1-6 | 226 | 2 |  |  | 24 | -2,-4 (90); 3,-5 (37); 4,-5 (33); 3,-6 (11); -3,1 (10) |
| worrt | 1-6 | 132 |  |  |  | 12 | 3,-5 (66); -1,-4 (24); 3,-6 (13); 0,-6 (11); -2,2 (5) |
| death_kreetle | 9 | 23 | 29 | 53 |  | 35 | 3,-4 (10); 2,3 (9); -1,-5 (9); -5,1 (7); -1,2 (6) |
| evil_hermit | 6 | 70 |  | 56 |  | 23 | 3,-4 (23); -1,-6 (13); 3,-5 (11); -1,-4 (8); 0,-5 (8) |
| trandosian_slavemaster | 7 | 17 | 16 | 33 |  | 13 | 1,3 (20); -3,-4 (16); -5,2 (12); -2,-6 (10); 1,2 (9) |
| minor_worrt | 5 | 97 |  |  |  | 6 | 3,-5 (67); 0,-6 (18); -4,2 (5); -1,-4 (4); -4,1 (2) |
| eopie | 1-7 | 34 | 4 | 23 |  | 4 | 3,-7 (20); 1,4 (19); -2,-3 (18); 3,-5 (12) |
| lesser_desert_womp_rat | 5 | 59 | 2 |  |  | 8 | 3,-5 (28); -3,2 (21); -1,-5 (7); 3,-6 (4); -3,-5 (3) |
| trandosian_slaver | 5 | 16 |  | 16 |  | 8 | -5,2 (12); -2,3 (9); -3,4 (4); 5,-5 (4); -4,0 (3) |
| drooling_nuna | 6 | 20 |  | 17 |  | 16 | -5,1 (5); -1,3 (4); -2,1 (4); 3,-4 (3); -3,-3 (2) |
| domestic_eopie | 4 | 31 |  |  |  | 8 | -1,-6 (14); 0,-6 (7); 0,-5 (4); 3,-5 (2); 1,-6 (1) |
| scyk | 1-12 | 1 | 6 | 6 |  | 4 | 3,-6 (16); 4,-4 (4); 3,-5 (4); 4,-6 (1) |
| dwarf_eopie | 3 | 5 |  | 1 |  | 2 | 3,-5 (5); 3,-6 (1) |
| giant_worrt | 13 |  | 1 | 1 |  | 2 | 3,-7 (4); 3,-6 (1) |
| rockmite | 8 | 3 |  |  |  | 1 | 3,-5 (3) |
| greater_desert_womp_rat | 22 |  | 1 | 1 |  | 1 | 2,-4 (3) |
| jawa | 6 | 1 |  | 1 |  | 1 | 0,2 (2) |
| hermit | 4 | 1 |  | 1 |  | 1 | 0,-7 (2) |
| zucca_boar | 10 | 1 |  |  |  | 1 | 2,-5 (1) |
| kreetle_swarmling | 6 | 1 |  |  |  | 1 | -2,-6 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_tatooine_mynock_lair_neutral_small | ? | 117 | 274 |  | 60 | 2,3 (22); 0,3 (20); -3,-4 (18); 0,-5 (14); -1,-3 (13) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 122 | 248 |  | 60 | -1,-5 (20); 4,-4 (15); 2,3 (13); -1,2 (12); 1,-7 (12) |
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 110 | 259 |  | 56 | -1,-5 (27); 5,-5 (17); 0,-4 (16); -3,3 (16); 4,-5 (13) |
| tatooine_kreetle_lair_neutral_small | ? | 114 | 242 |  | 59 | -1,-5 (20); 2,-6 (16); 0,-4 (13); -2,-6 (13); 1,-6 (12) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 49 | 104 |  | 38 | 3,-4 (12); -2,1 (12); -3,-5 (9); 0,-5 (8); -2,-6 (6) |
| tatooine_gorg_lair_neutral_small | ? | 14 | 32 |  | 12 | -3,-5 (9); -2,-5 (5); -1,-5 (4); 1,4 (4); 2,2 (4) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 15 | 30 |  | 13 | -5,2 (9); 1,3 (6); 1,2 (5); -3,-4 (4); -2,3 (3) |
| tatooine_sevorrt_lair_neutral_medium | ? | 7 | 10 |  | 6 | 0,-5 (5); 4,-4 (4); 4,-6 (3); 1,-5 (2); -1,3 (2) |
| tatooine_eopie_lair_neutral_small | ? | 3 | 10 |  | 3 | -2,-3 (5); 3,-7 (4); 1,4 (4) |

