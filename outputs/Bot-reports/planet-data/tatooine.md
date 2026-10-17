# Tatooine: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:02 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `tatooine.csv`.

- Bots here: 420 (0 explorers, 265 that killed something).
- Coverage: 75 of 256 squares of 1 km had a bot or a sighting in them (29%); explorers stood in 0.
- Templates: 25 creatures, 8 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 tatooine` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| kreetle | 1-3 | 1223 | 49 | 891 |  | 58 | -1,-6 (185); 1,1 (101); -4,1 (100); -1,-7 (90); -1,-5 (89) |
| dwarf_nuna | 1-5 | 572 | 4 | 144 |  | 37 | -1,-6 (148); 1,3 (64); -4,2 (62); -3,2 (45); -2,-5 (37) |
| tatooine_mynock | 1-3 | 370 | 1 | 300 |  | 40 | -1,-5 (51); -1,-6 (45); -1,-3 (39); -4,3 (33); 2,-6 (31) |
| gorg | 6 | 400 | 3 | 36 |  | 23 | 0,-6 (104); -3,1 (66); 1,2 (39); 4,-5 (34); -1,-6 (34) |
| womp_rat | 1-10 | 1 | 78 | 85 |  | 34 | -2,-5 (20); 1,4 (20); 0,-7 (20); -2,-3 (20); -1,-5 (16) |
| rill | 1-6 | 275 |  |  |  | 9 | -2,-4 (107); -1,-4 (50); 3,-5 (40); 0,-6 (31); 3,-6 (31) |
| evil_settler | 5 | 108 | 1 | 75 |  | 13 | -1,-5 (33); -1,-6 (29); 3,-4 (26); 0,-6 (15); 1,2 (14) |
| gorg_glutton | 7 | 150 | 1 | 5 |  | 10 | -1,-4 (41); 1,3 (40); 4,-5 (38); 3,-5 (23); 0,-6 (4) |
| sevorrt | 1-7 | 55 | 9 | 38 |  | 9 | 3,-6 (36); 0,-6 (25); 3,-5 (19); 4,-5 (13); -4,0 (12) |
| highwayman | 10 | 3 | 30 | 35 |  | 10 | 0,-5 (11); 1,-5 (11); 0,-6 (9); 1,-7 (8); 1,-6 (7) |
| evil_hermit | 6 | 28 |  | 18 |  | 7 | -1,-6 (18); 0,-6 (14); 0,-7 (7); 0,-5 (2); -2,-5 (2) |
| trandosian_slavemaster | 7 | 11 | 4 | 15 |  | 7 | -3,-4 (8); -5,2 (8); 1,4 (6); -2,-3 (6); 0,-5 (6) |
| death_kreetle | 9 | 5 | 7 | 16 |  | 14 | -1,-6 (4); 5,-5 (4); -3,3 (3); -4,1 (3); 1,3 (3) |
| trandosian_slaver | 5 | 9 | 3 | 12 |  | 5 | -2,-3 (8); -4,2 (8); 0,4 (6); 1,4 (4); 0,-5 (2) |
| minor_worrt | 1-5 | 24 |  |  |  | 4 | -1,-4 (15); 0,-6 (6); 3,-6 (2); -1,-5 (1) |
| worrt | 1-6 | 20 |  |  |  | 5 | 3,-6 (7); -1,-4 (4); 3,-5 (4); 0,-6 (3); -1,-6 (2) |
| drooling_nuna | 6 | 5 |  | 4 |  | 5 | -3,-5 (2); 0,-7 (2); 3,1 (2); -1,-8 (2); -5,3 (1) |
| rockmite | 1-8 | 7 |  |  |  | 2 | 3,-5 (4); 4,-5 (3) |
| lesser_desert_womp_rat | 5 | 7 |  |  |  | 2 | -4,2 (5); 3,-6 (2) |
| domestic_eopie | 4 | 5 |  |  |  | 3 | 3,-6 (2); 1,2 (2); 0,-7 (1) |
| dwarf_eopie | 3 | 4 |  | 1 |  | 1 | 2,-5 (5) |
| eopie | 7 | 2 |  |  |  | 1 | 2,-5 (2) |
| zucca_boar | 1 | 1 |  |  |  | 1 | 4,-6 (1) |
| lesser_dewback | 9 | 1 |  |  |  | 1 | 2,-6 (1) |
| jawa | 6 |  |  | 1 |  | 1 | -3,0 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| tatooine_kreetle_over_death_neutral_medium_boss_01 | ? | 58 | 100 |  | 38 | 5,-5 (9); -3,1 (9); -4,1 (8); -1,-7 (7); -3,3 (7) |
| tatooine_tatooine_mynock_lair_neutral_small | ? | 53 | 88 |  | 39 | -1,-5 (9); -1,-6 (8); -1,-3 (8); 4,-4 (7); -4,3 (7) |
| tatooine_womprat_womprat_neutral_medium_boss_01 | ? | 47 | 84 |  | 34 | 0,-7 (8); -2,-3 (8); 1,4 (7); -1,-5 (7); -4,2 (7) |
| tatooine_kreetle_lair_neutral_small | ? | 49 | 72 |  | 34 | -3,-3 (11); -2,-6 (9); 1,1 (8); 1,4 (7); -1,-5 (6) |
| tatooine_dwarf_nuna_nuna_neutral_medium_boss_01 | ? | 25 | 39 |  | 24 | 2,-4 (7); 0,-7 (7); -3,-5 (4); 3,1 (4); 0,4 (3) |
| tatooine_trandosian_slaver_neutral_medium_theater | ? | 7 | 12 |  | 7 | -3,-4 (3); 1,4 (3); -2,-3 (3); -4,2 (3); 0,-5 (3) |
| tatooine_gorg_lair_neutral_small | ? | 7 | 9 |  | 7 | 2,-4 (3); 0,4 (3); 4,-6 (2); -3,-3 (2); -1,2 (2) |
| tatooine_sevorrt_lair_neutral_medium | ? | 1 | 1 |  | 1 | -4,0 (2) |

