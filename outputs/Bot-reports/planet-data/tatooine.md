# Tatooine: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:33 AM to 1:01 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 436 (0 explorers, 275 that killed something).
- Coverage: 83 of 256 squares of 1 km had a bot or a sighting in them (32%); explorers stood in 0.
- Templates: 25 creatures, 10 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 1541 | 54 | 1139 |  | 68 | 2,2 (144); -1,-4 (119); 3,-6 (89); 0,3 (84); 2,-5 (83) |
| tatooine_mynock | 1-3 | 628 | 3 | 490 |  | 46 | -1,-5 (91); 1,-5 (73); -1,-7 (62); -2,-6 (58); 1,4 (48) |
| dwarf_nuna | 1-5 | 634 | 6 | 163 |  | 41 | 0,-6 (84); -3,1 (70); -2,-4 (47); -1,-6 (43); 1,3 (42) |
| gorg | 6 | 609 | 1 | 57 |  | 24 | -1,-6 (257); -2,-4 (76); -3,2 (58); -1,-4 (37); -2,-5 (34) |
| womp_rat | 1-10 | 12 | 137 | 148 |  | 42 | -1,-6 (33); -4,3 (32); 1,-6 (28); -1,-3 (28); 2,3 (24) |
| gorg_glutton | 7 | 194 |  | 3 |  | 16 | 1,2 (91); -1,-6 (30); -3,1 (22); 1,3 (20); -4,2 (8) |
| evil_settler | 5 | 89 | 3 | 67 |  | 9 | 3,-5 (37); 3,-6 (37); 4,-5 (32); -1,-6 (26); -1,-5 (13) |
| sevorrt | 7 | 23 | 13 | 33 |  | 12 | -4,1 (24); -2,-5 (16); -5,2 (13); -1,-6 (10); -3,-3 (10) |
| trandosian_slavemaster | 7 | 21 | 9 | 30 |  | 11 | -2,0 (13); -5,1 (12); 5,-6 (12); -1,-4 (8); -1,-6 (6) |
| highwayman | 10 | 1 | 29 | 30 |  | 12 | 1,-5 (17); 4,-6 (16); 3,-4 (7); 2,-4 (6); 3,-6 (4) |
| death_kreetle | 9 | 11 | 13 | 25 |  | 19 | 2,3 (6); 0,-4 (6); 4,-4 (6); 5,-5 (6); -1,-4 (5) |
| evil_hermit | 6 | 30 | 1 | 20 |  | 15 | 0,-6 (8); -1,-5 (8); 3,-5 (5); 3,-6 (4); 4,-5 (4) |
| domestic_eopie | 4 | 48 |  |  |  | 8 | -1,-6 (22); 3,-5 (13); -2,-4 (4); 4,-5 (4); -1,-3 (2) |
| eopie | 7 | 6 | 7 | 8 |  | 4 | 0,-6 (12); 0,-5 (10); -2,2 (9); 3,-6 (3) |
| trandosian_slaver | 5 | 12 | 1 | 14 |  | 8 | 2,-6 (8); -1,-3 (7); -1,-4 (5); -3,-4 (4); -1,-6 (4) |
| rill | 1-6 | 31 |  |  |  | 13 | 3,-5 (9); 4,-6 (6); 2,-5 (3); -3,-5 (3); 0,-6 (2) |
| minor_worrt | 1-5 | 23 | 1 |  |  | 6 | 3,-5 (11); -1,-3 (8); 2,-4 (2); -2,-6 (1); -1,-4 (1) |
| worrt | 1-6 | 19 |  |  |  | 9 | -1,-6 (9); -4,1 (2); 0,-7 (2); 3,-5 (1); 3,-6 (1) |
| diseased_bocatt | 8 | 3 | 3 | 6 |  | 1 | 0,2 (18) |
| drooling_nuna | 6 | 7 |  | 7 |  | 7 | -4,0 (4); -1,-7 (3); -2,-3 (2); 4,-6 (2); 4,-5 (2) |
| dwarf_eopie | 3 | 3 |  | 2 |  | 1 | 4,-6 (5) |
| tusken_warrior | 38 |  | 2 | 2 |  | 1 | -1,1 (5) |
| mound_mite | 9 |  | 1 |  |  | 1 | 0,-4 (3) |
| rockmite | 8 | 1 |  |  |  | 1 | 3,-5 (1) |
| lesser_desert_womp_rat | 5 | 1 |  |  |  | 1 | -3,-4 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_tatooine_mynock_lair_neutral_small | ? | 73 | 169 |  | 44 | -1,-5 (21); 1,-5 (15); -1,-7 (14); -2,2 (11); -2,-6 (10) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 61 | 150 |  | 40 | 5,-5 (12); 4,-4 (11); -3,-4 (11); -1,-3 (10); -2,2 (10) |
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 62 | 145 |  | 42 | -4,3 (11); -1,-6 (11); 1,-6 (10); -1,-3 (9); -1,-5 (9) |
| tatooine_kreetle_lair_neutral_small | ? | 66 | 130 |  | 47 | 2,2 (19); 2,-5 (10); 0,1 (8); -3,3 (8); 0,-7 (7) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 24 | 51 |  | 23 | 4,-6 (8); 2,3 (6); -2,-6 (6); 4,-5 (6); -1,-7 (5) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 12 | 29 |  | 11 | -1,-4 (5); 2,-6 (5); 1,4 (5); -3,-4 (4); -5,1 (4) |
| tatooine_gorg_lair_neutral_small | ? | 9 | 26 |  | 9 | -1,-4 (7); 1,4 (5); 0,2 (5); -2,-5 (5); 2,-6 (4) |
| tatooine_eopie_lair_neutral_small | ? | 2 | 7 |  | 3 | -2,2 (4); 0,-6 (3); 0,-5 (2) |
| tatooine_sevorrt_lair_neutral_medium | ? | 3 | 5 |  | 4 | -5,2 (3); -2,-5 (2); -1,-5 (2); -4,1 (1) |
| tatooine_diseased_bocatt_lair_neutral_medium | ? | 1 | 1 |  | 1 | 0,2 (2) |

