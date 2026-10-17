# Tatooine: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:02 PM to 7:18 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 420 (0 explorers, 267 that killed something).
- Coverage: 91 of 256 squares of 1 km had a bot or a sighting in them (36%); explorers stood in 0.
- Templates: 40 creatures, 14 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 3462 | 51 | 382 |  | 81 | -1,-6 (256); -1,-5 (140); 1,3 (123); -2,-6 (117); -5,2 (117) |
| tatooine_mynock | 1-3 | 1562 | 12 | 226 |  | 80 | -2,-6 (94); 1,4 (83); -2,1 (77); 4,-4 (75); 0,-4 (71) |
| gorg | 6 | 777 | 7 | 22 |  | 69 | -1,-4 (138); 1,2 (134); 1,3 (105); -3,2 (96); -2,-4 (67) |
| dwarf_nuna | 1-5 | 923 | 8 | 49 |  | 73 | 0,-6 (185); 1,2 (69); -1,-6 (55); -3,2 (50); -1,-5 (43) |
| womp_rat | 1-10 | 230 | 128 | 83 |  | 76 | 0,-5 (34); 3,-4 (33); -2,-5 (32); -3,-4 (30); -1,-3 (29) |
| gorg_glutton | 7 | 308 | 1 |  |  | 27 | -2,-4 (263); 1,2 (74); -1,-4 (59); -4,1 (42); -1,-6 (22) |
| rill | 1-6 | 187 | 2 |  |  | 41 | 0,-6 (108); -1,-4 (45); 0,3 (22); 3,-6 (17); -2,1 (14) |
| sevorrt | 1-7 | 132 | 9 | 27 |  | 39 | -2,-3 (15); -5,2 (14); -1,-4 (12); -3,-4 (12); 2,-6 (11) |
| minor_worrt | 5 | 169 | 1 |  |  | 9 | 3,-5 (158); 2,-5 (10); -1,-4 (4); 0,3 (3); 0,-7 (3) |
| worrt | 1-6 | 92 | 2 |  |  | 21 | 0,-6 (103); 4,-4 (10); -1,-7 (7); 0,-4 (7); -2,-6 (6) |
| eopie | 1-7 | 81 | 4 | 24 |  | 31 | -3,0 (12); 3,2 (10); 0,-7 (8); 2,5 (8); -1,2 (8) |
| lesser_desert_womp_rat | 1-5 | 86 | 4 |  |  | 17 | 3,-5 (56); -4,1 (23); 0,-5 (11); 3,-6 (6); 0,-7 (6) |
| dwarf_eopie | 3 | 124 |  | 3 |  | 2 | 3,-5 (123); 2,-5 (4) |
| domestic_eopie | 4 | 35 | 1 |  |  | 18 | -1,-6 (16); -1,-7 (5); 4,-6 (5); 0,-5 (3); 4,-5 (2) |
| rockmite | 1-8 | 31 |  | 9 |  | 12 | 3,-7 (11); 2,3 (7); -1,-5 (6); 1,-7 (4); -3,-4 (3) |
| trandosian_slaver | 5 | 10 | 4 | 17 |  | 11 | 4,-6 (6); 2,-5 (6); 0,-7 (6); -4,3 (5); -1,2 (4) |
| trandosian_slavemaster | 7 | 8 |  | 16 |  | 11 | 4,-6 (8); 0,-7 (6); 0,1 (4); 3,-7 (3); -4,3 (3) |
| evil_hermit | 6 | 19 |  |  |  | 11 | 0,-6 (10); -1,-6 (3); -1,-7 (3); 1,-5 (3); 0,-5 (3) |
| evil_settler | 5 | 14 | 1 | 2 |  | 10 | -2,0 (7); -3,-4 (5); 2,-6 (4); 3,-6 (4); -2,-7 (2) |
| kreetle_swarmling | 6 | 8 | 1 | 1 |  | 8 | 4,-5 (9); 0,4 (4); -4,0 (4); -2,-6 (3); 4,-7 (2) |
| diseased_bocatt | 8 | 12 |  | 6 |  | 7 | -2,-2 (6); 0,2 (4); 0,-4 (4); -2,3 (4); 1,-6 (3) |
| bull_bantha | 2 | 2 | 2 |  |  | 7 | -3,1 (5); -3,3 (4); -2,-5 (3); 1,-6 (3); -3,2 (2) |
| greater_desert_womp_rat | 2-22 | 1 | 1 | 1 |  | 4 | -1,-6 (7); 3,-6 (7); -3,-3 (2); -2,-7 (1) |
| lesser_dewback | 1-9 | 12 |  | 1 |  | 3 | -2,-6 (10); 2,-6 (2); -2,-7 (1) |
| highwayman | 10 | 3 | 1 | 1 |  | 5 | 4,-4 (5); 4,-6 (3); 3,-7 (2); 2,-5 (1); 2,-6 (1) |
| zucca_boar | 1-10 | 8 |  |  |  | 6 | 3,-5 (5); 0,-4 (2); 4,-5 (1); 1,-7 (1); 3,-4 (1) |
| feral_bantha | 1 | 7 |  |  |  | 6 | -4,2 (5); 3,-6 (2); -5,3 (1); -2,0 (1); -3,0 (1) |
| cu_pa | 1 | 6 | 1 |  |  | 5 | 3,-5 (5); 3,-6 (1); 4,-6 (1); 4,-5 (1); -1,-5 (1) |
| mutant_womp_rat | 1-13 | 2 | 1 | 2 |  | 4 | -2,-6 (4); 4,-6 (3); -2,-4 (1); 1,-6 (1) |
| scyk | 1-12 | 2 | 2 | 1 |  | 4 | 1,-6 (4); -1,-6 (3); 0,-5 (1); -1,4 (1) |
| giant_worrt | 1 | 2 | 2 |  |  | 3 | -1,-5 (6); 0,-4 (1); -3,-4 (1) |
| drooling_nuna | 6 | 7 |  | 1 |  | 5 | -4,3 (3); 2,1 (2); 1,-6 (1); -4,1 (1); -2,2 (1) |
| spice_fiend | 8 | 3 |  | 4 |  | 3 | -2,-5 (4); 5,-7 (2); 2,-5 (2) |
| bantha | 1 |  |  |  |  | 2 | -4,0 (3); -4,2 (2) |
| mound_mite | 1-9 | 4 |  |  |  | 2 | 3,-6 (3); 0,4 (1) |
| jawa_engineer | 10 | 1 |  | 1 |  | 1 | 1,-7 (3) |
| dune_lizard | 1 |  |  |  |  | 1 | 0,4 (3) |
| variegated_womp_rat | 1 | 1 |  |  |  | 2 | -2,-4 (1); -3,-3 (1) |
| death_kreetle | 9 | 1 |  | 1 |  | 1 | 1,4 (2) |
| rock_beetle | 1 |  |  |  |  | 1 | 0,1 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 549 |  |  | 78 | 3,-4 (21); 1,-5 (18); 0,-4 (17); -3,-4 (15); -1,-5 (15) |
| tatooine_tatooine_mynock_lair_neutral_small | ? | 508 |  |  | 81 | 4,-4 (20); -1,-5 (20); -2,-6 (18); 0,-4 (18); 1,4 (16) |
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 505 |  |  | 78 | -2,-5 (18); -1,-5 (17); 1,4 (17); -1,-3 (16); 0,-7 (14) |
| tatooine_kreetle_lair_neutral_small | ? | 504 |  |  | 78 | -1,-5 (21); 1,-5 (19); -2,-6 (18); 0,-4 (17); 0,-5 (15) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 184 |  |  | 70 | -1,-5 (9); 1,-6 (7); 0,-7 (7); 0,4 (7); -2,1 (7) |
| tatooine_gorg_lair_neutral_small | ? | 116 |  |  | 58 | 1,-5 (6); 3,-7 (5); 1,4 (5); 0,-4 (5); -4,3 (4) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 98 |  |  | 46 | 1,-7 (5); 0,-7 (5); 4,-6 (4); -3,-5 (4); -4,3 (4) |
| tatooine_sevorrt_lair_neutral_medium | ? | 57 |  |  | 40 | 2,-6 (3); 1,4 (3); -1,-5 (3); -3,-5 (3); -5,2 (3) |
| tatooine_eopie_lair_neutral_small | ? | 45 |  |  | 34 | -2,-5 (3); -3,1 (3); 0,-7 (2); -1,-5 (2); -1,-7 (2) |
| tatooine_rockmite_click_neutral_small | ? | 25 |  |  | 22 | -1,-5 (3); 3,-7 (2); 1,-5 (1); 0,-4 (1); 2,-6 (1) |
| tatooine_diseased_bocatt_lair_neutral_medium | ? | 18 |  |  | 18 | 1,4 (1); 0,2 (1); 0,-4 (1); -1,-8 (1); 3,-4 (1) |
| tatooine_spice_fiend_neutral_small_theater | ? | 12 |  |  | 12 | -1,-4 (1); -2,1 (1); -2,-5 (1); -1,-5 (1); 5,-7 (1) |
| tatooine_jawa_outpost_neutral_medium_theater | ? | 4 |  |  | 4 | 1,-7 (1); 0,4 (1); 0,-5 (1); 4,-5 (1) |
| tatooine_weequay_outpost_neutral_large_theater | ? | 1 |  |  | 1 | -1,2 (1) |

