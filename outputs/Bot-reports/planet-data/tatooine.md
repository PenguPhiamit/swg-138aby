# Tatooine: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:32 PM to 12:31 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 701 (0 explorers, 227 that killed something).
- Coverage: 80 of 256 squares of 1 km had a bot or a sighting in them (31%); explorers stood in 0.
- Templates: 30 creatures, 12 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 498 | 30 | 264 |  | 57 | 0,-4 (60); -1,-7 (47); -2,1 (44); -2,-6 (41); -5,1 (39) |
| gorg | 6 | 412 | 3 | 20 |  | 38 | -3,2 (103); -1,-6 (85); 1,3 (77); 1,2 (48); -3,1 (33) |
| dwarf_nuna | 1-5 | 394 | 3 | 34 |  | 43 | 0,-6 (117); 1,3 (60); 1,2 (42); -1,-6 (39); -3,1 (29) |
| tatooine_mynock | 1-3 | 241 | 6 | 114 |  | 36 | -3,0 (33); 3,-5 (30); -2,2 (22); -1,-5 (20); -3,1 (19) |
| gorg_glutton | 7 | 288 | 1 |  |  | 20 | -1,-6 (214); 1,3 (41); 1,2 (14); 3,-6 (6); 2,3 (5) |
| sevorrt | 1-7 | 72 | 12 | 20 |  | 22 | 3,-6 (37); 3,-5 (27); 4,-5 (19); -1,-6 (15); 4,-6 (6) |
| rill | 1-6 | 82 | 1 |  |  | 18 | -1,-6 (26); 3,-5 (24); 4,-6 (11); -1,-5 (7); 4,-5 (4) |
| womp_rat | 1-10 | 19 | 12 | 12 |  | 19 | 0,-5 (16); -3,0 (10); -3,3 (8); -2,-6 (6); -1,-5 (4) |
| worrt | 1-6 | 55 |  |  |  | 9 | 0,-6 (32); 3,-5 (6); -1,-5 (5); 3,-6 (4); -1,-6 (3) |
| evil_settler | 5 | 30 |  | 13 |  | 8 | 0,-6 (17); 1,4 (7); -4,0 (6); 1,-6 (6); 0,-5 (4) |
| eopie | 7 | 13 | 4 | 9 |  | 6 | 5,-6 (11); -4,2 (8); 0,-4 (8); 3,-6 (6); -1,-4 (3) |
| evil_hermit | 6 | 23 |  | 3 |  | 11 | -1,-6 (15); 0,-6 (5); 2,-5 (3); 0,-5 (2); 3,-5 (2) |
| dwarf_eopie | 3 | 14 | 1 |  |  | 5 | 3,-5 (20); -3,2 (3); 3,-6 (2); 2,-5 (2); 2,-7 (1) |
| lesser_desert_womp_rat | 5 | 18 |  |  |  | 6 | 3,-5 (12); -4,2 (7); 3,-6 (2); -4,3 (2); 4,-6 (1) |
| trandosian_slavemaster | 7 | 2 | 3 | 5 |  | 5 | -1,-7 (4); 1,-4 (4); -2,-6 (4); 1,1 (4); 0,2 (3) |
| minor_worrt | 5 | 16 |  |  |  | 5 | 0,-6 (11); 3,-6 (3); -1,-6 (2); -2,-6 (1); 1,-6 (1) |
| highwayman | 10 |  | 7 | 7 |  | 8 | 3,-6 (4); 1,-6 (3); 1,-5 (2); 0,-5 (2); 0,-8 (2) |
| domestic_eopie | 4 | 16 |  |  |  | 4 | 0,-6 (8); 3,-6 (5); -1,-6 (2); 1,-6 (1) |
| rockmite | 8 | 6 | 1 | 2 |  | 4 | 3,-5 (4); 0,1 (3); -2,-7 (3); 3,-6 (1) |
| trandosian_slaver | 5 | 5 |  | 5 |  | 3 | -1,-7 (4); 0,2 (4); 2,2 (2) |
| death_kreetle | 9 | 1 | 3 | 4 |  | 4 | 0,4 (3); 2,-4 (2); -3,3 (2); -2,1 (2) |
| diseased_bocatt | 8 |  | 1 | 1 |  | 1 | 0,1 (6) |
| mound_mite | 1 | 2 |  |  |  | 3 | 2,-5 (2); 4,-5 (1); 4,-6 (1) |
| brigand | 4 |  | 1 |  |  | 1 | 1,-4 (2) |
| minor_gubbur | 4 |  |  |  |  | 1 | -1,-7 (2) |
| corellian_butterfly | 7 |  |  |  |  | 1 | 0,-7 (2) |
| capper_spineflap_drone | 6 |  |  |  |  | 2 | -1,-5 (1); -1,-4 (1) |
| plumed_rasp | 1 |  |  |  |  | 1 | 1,-5 (2) |
| drooling_nuna | 6 |  |  |  |  | 1 | 0,-8 (1) |
| garyns_prowler | 11 |  |  |  |  | 1 | -1,-5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 71 | 140 |  | 41 | 3,-3 (17); -1,-7 (11); -3,1 (10); -3,0 (10); 0,-7 (9) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 69 | 116 |  | 39 | -1,-7 (13); -2,1 (13); -5,2 (13); 1,4 (12); -2,-6 (9) |
| tatooine_tatooine_mynock_lair_neutral_small | ? | 67 | 110 |  | 37 | -1,-5 (15); 1,-6 (13); -3,0 (12); -1,-7 (8); -5,1 (8) |
| tatooine_kreetle_lair_neutral_small | ? | 64 | 104 |  | 39 | 0,-4 (13); 2,-6 (11); 4,-4 (9); -3,0 (8); -2,1 (8) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 25 | 42 |  | 23 | 1,1 (6); -1,-4 (6); 4,-6 (4); 1,-5 (4); -5,2 (3) |
| tatooine_gorg_lair_neutral_small | ? | 13 | 26 |  | 13 | 0,-5 (4); -2,-5 (4); 1,4 (4); 4,-6 (3); -3,1 (3) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 11 | 24 |  | 10 | 2,2 (9); 0,2 (6); -1,-7 (4); 3,-7 (3); -2,-5 (3) |
| tatooine_eopie_lair_neutral_small | ? | 5 | 13 |  | 5 | -3,2 (4); -4,2 (4); 5,-6 (4); -1,-4 (3); 0,-4 (3) |
| tatooine_spice_fiend_neutral_small_theater | ? | 5 | 10 |  | 5 | 2,-5 (4); -2,-7 (3); -4,0 (3); 1,-7 (3); 1,-5 (2) |
| tatooine_sevorrt_lair_neutral_medium | ? | 4 | 8 |  | 4 | -2,2 (4); 1,-5 (3); 0,1 (3); 2,-6 (2) |
| tatooine_rockmite_click_neutral_small | ? | 2 | 3 |  | 2 | 0,1 (3); -2,-7 (2) |
| tatooine_diseased_bocatt_lair_neutral_medium | ? | 1 | 2 |  | 1 | 0,1 (3) |

