# Tatooine: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:25 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 745 (0 explorers, 192 that killed something).
- Coverage: 69 of 256 squares of 1 km had a bot or a sighting in them (27%); explorers stood in 0.
- Templates: 32 creatures, 11 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 524 | 44 | 246 |  | 46 | 1,3 (97); 1,2 (60); -4,1 (55); 0,2 (50); -2,-5 (49) |
| gorg | 6 | 433 | 22 | 7 |  | 36 | 0,-6 (117); 1,2 (99); -3,1 (75); -3,2 (61); -1,-6 (56) |
| dwarf_nuna | 1-5 | 280 | 16 | 35 |  | 32 | 1,3 (91); 0,-6 (77); -2,2 (23); -3,2 (20); -3,1 (16) |
| gorg_glutton | 7 | 279 | 23 |  |  | 26 | -1,-6 (216); -3,2 (41); 1,3 (26); 0,-6 (20); 0,-5 (18) |
| tatooine_mynock | 1-3 | 139 | 8 | 77 |  | 31 | 2,2 (31); 0,2 (31); 1,4 (23); -2,1 (14); -2,-7 (13) |
| giant_worrt | 1-13 | 9 | 43 | 41 |  | 8 | 0,-6 (126); -1,-6 (40); 3,-5 (5); 1,-6 (4); -1,-5 (4) |
| rill | 1-6 | 115 | 6 |  |  | 16 | -1,-6 (63); -2,-5 (10); -2,-4 (9); 0,-6 (8); -1,-5 (8) |
| scyk | 12 | 1 | 18 | 19 |  | 10 | 0,-5 (21); 1,-6 (11); -1,-6 (10); 2,-5 (9); 2,2 (6) |
| womp_rat | 1-10 | 9 | 15 | 15 |  | 15 | 1,1 (14); 0,1 (8); -1,-4 (8); 2,2 (5); -2,3 (5) |
| sevorrt | 1-7 | 20 | 10 | 12 |  | 11 | -1,-6 (21); -2,3 (11); 0,-6 (6); 3,-6 (6); 1,-6 (6) |
| greater_desert_womp_rat | 2-22 |  | 9 | 9 |  | 7 | -1,-6 (16); -2,-4 (14); 4,-6 (4); 0,-7 (4); 3,-5 (3) |
| domestic_eopie | 4 | 27 | 4 |  |  | 7 | -1,-6 (17); 0,-6 (11); 3,-5 (6); -1,-5 (2); 2,-6 (1) |
| eopie | 7 | 12 | 4 | 8 |  | 7 | -2,3 (12); 0,-7 (8); 3,-6 (5); -4,0 (3); 3,3 (2) |
| evil_hermit | 6 | 10 | 5 | 5 |  | 7 | -1,-5 (10); 2,-5 (5); -1,-6 (5); 0,2 (4); 3,-5 (3) |
| mutant_womp_rat | 13 |  | 8 | 8 |  | 9 | -2,-6 (8); 0,-5 (7); -1,-7 (4); 4,-6 (4); -1,2 (2) |
| dwarf_eopie | 3 | 14 |  |  |  | 2 | 3,-5 (14); 3,-6 (6) |
| trandosian_slavemaster | 7 | 5 | 2 | 7 |  | 4 | -1,2 (8); -2,-5 (5); -2,1 (5); 1,-5 (2) |
| trandosian_slaver | 5 | 5 | 2 | 6 |  | 5 | 2,3 (5); 3,2 (4); 1,-5 (4); -2,1 (3); 1,-6 (2) |
| highwayman | 10 |  | 7 | 7 |  | 4 | 0,-5 (5); 1,-5 (5); 1,-7 (4); 3,-5 (2) |
| feral_bantha | 1-15 | 1 | 6 | 5 |  | 4 | -4,2 (5); -2,-5 (5); 4,-6 (3); -1,-5 (3) |
| kreetle_swarmling | 6 | 4 | 1 | 4 |  | 2 | 1,2 (9); -1,-4 (3) |
| bull_bantha | 2 |  | 3 |  |  | 2 | 3,-6 (6); 4,-5 (4) |
| cannibal_dewback | 21 |  | 2 | 2 |  | 2 | -4,2 (6); -4,3 (4) |
| evil_settler | 5 | 4 | 1 |  |  | 2 | 0,-5 (5); 3,-5 (3) |
| rockmite | 1-8 | 1 |  |  |  | 2 | 3,-5 (6); 4,-5 (1) |
| death_kreetle | 9 |  | 3 | 3 |  | 3 | -4,2 (3); -2,-5 (2); 0,1 (2) |
| worrt | 6 | 4 |  |  |  | 3 | 3,-6 (3); 2,-5 (2); 2,2 (1) |
| lesser_desert_womp_rat | 5 | 5 |  |  |  | 2 | -4,1 (4); -4,2 (2) |
| flewt | 7 |  | 1 |  |  | 2 | 0,-7 (3); 0,-6 (2) |
| spice_fiend | 8 |  | 1 | 1 |  | 1 | -1,-5 (4) |
| zucca_boar | 1 | 3 |  |  |  | 2 | 2,-5 (2); 3,-6 (1) |
| minor_worrt | 5 | 1 |  |  |  | 1 | 3,-5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 49 | 83 |  | 36 | -2,1 (9); 0,1 (9); 0,-7 (8); -2,2 (7); -1,-6 (6) |
| tatooine_tatooine_mynock_lair_neutral_small | ? | 51 | 79 |  | 29 | -2,2 (11); 0,2 (10); -2,1 (9); 2,2 (8); -1,-4 (7) |
| tatooine_kreetle_lair_neutral_small | ? | 46 | 71 |  | 32 | -2,-5 (10); 0,4 (8); -4,1 (6); -1,-5 (6); 1,2 (6) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 48 | 68 |  | 37 | 2,1 (9); 0,3 (8); -1,-7 (6); -4,3 (6); -5,2 (5) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 16 | 28 |  | 16 | 1,-6 (5); -2,2 (4); 0,-7 (3); -3,0 (3); -4,3 (3) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 9 | 17 |  | 9 | -1,2 (4); -2,1 (4); -2,-5 (3); 2,3 (3); 1,4 (3) |
| tatooine_eopie_lair_neutral_small | ? | 6 | 8 |  | 6 | -2,3 (4); 0,-7 (3); -1,-4 (2); 5,-6 (2); -4,0 (2) |
| tatooine_sevorrt_lair_neutral_medium | ? | 5 | 7 |  | 6 | 0,3 (3); 1,-5 (3); 2,2 (2); -4,0 (2); 1,-6 (1) |
| tatooine_gorg_lair_neutral_small | ? | 3 | 4 |  | 3 | -2,2 (3); 0,-4 (2); 0,4 (2) |
| tatooine_spice_fiend_neutral_small_theater | ? | 2 | 3 |  | 2 | -1,-5 (3); -4,3 (2) |
| tatooine_diseased_bocatt_lair_neutral_medium | ? | 1 | 3 |  | 1 | -1,-5 (4) |

