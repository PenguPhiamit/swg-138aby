# Rori: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:34 AM to 1:01 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 172 (0 explorers, 105 that killed something).
- Coverage: 37 of 256 squares of 1 km had a bot or a sighting in them (14%); explorers stood in 0.
- Templates: 21 creatures, 7 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| capper_spineflap | 1-6 | 138 | 14 | 92 |  | 20 | -6,-2 (66); -7,-3 (26); 5,4 (24); 5,6 (22); 4,4 (20) |
| ikopi | 7 | 143 | 14 | 27 |  | 14 | -6,-3 (57); -6,-2 (42); 5,5 (35); 3,5 (17); 6,5 (13) |
| nightspider | 7 | 122 | 9 | 36 |  | 14 | -6,-3 (46); 4,5 (22); -6,-4 (20); -7,-3 (16); 6,4 (16) |
| young_borgle | 6 | 42 | 14 | 57 |  | 11 | -5,-1 (37); -4,-3 (28); 4,6 (24); -6,-4 (19); -7,-2 (15) |
| sickle_rasp | 8 | 8 | 13 | 22 |  | 9 | -7,-3 (14); -7,-4 (12); -5,-4 (10); -7,-1 (10); 4,7 (8) |
| garyns_prowler | 11 | 4 | 16 | 20 |  | 2 | 5,5 (47); -6,-2 (24) |
| first_brigade_scout | 7 | 9 | 11 | 21 |  | 10 | -5,-4 (19); -6,-1 (12); -6,-2 (10); 6,5 (6); 4,4 (5) |
| gundark_crook | 5 | 29 | 1 | 31 |  | 14 | -6,-4 (14); -5,-2 (8); 3,5 (7); -7,-2 (6); 5,7 (5) |
| frail_squall | 6 | 55 |  |  |  | 2 | 5,5 (51); -6,-3 (9) |
| gundark_rogue | 7 | 15 | 5 | 21 |  | 11 | -7,-2 (10); 4,5 (10); -5,-5 (8); -5,-2 (6); 4,4 (4) |
| swamp_rat | 10 | 4 | 19 | 24 |  | 2 | 5,5 (28); 4,5 (27) |
| capper_spineflap_drone | 1-6 | 46 |  | 5 |  | 6 | -6,-3 (36); 5,6 (5); 6,5 (4); -7,-3 (4); -5,-1 (1) |
| young_borgle_gruntling | 6 | 31 |  | 8 |  | 3 | -6,-2 (29); 4,5 (11); -7,-4 (2) |
| gundark_hooligan | 6 | 16 |  | 17 |  | 11 | -6,-4 (13); 7,5 (6); 5,6 (4); 4,3 (4); 4,4 (2) |
| meek_avenging_squall | 6 | 35 |  | 2 |  | 3 | -5,-3 (31); -5,-4 (5); -6,-3 (1) |
| first_brigade_trooper | 6 | 14 | 1 | 15 |  | 7 | -6,-1 (11); 3,5 (8); 4,4 (4); 6,4 (4); -7,-1 (3) |
| hermit_spider | 1-7 | 19 |  |  |  | 3 | -5,-3 (17); -6,-3 (1); -6,-1 (1) |
| scorched_krevol | 8 | 5 |  | 3 |  | 1 | -6,-2 (10) |
| frightened_borgle | 8 | 3 | 1 |  |  | 1 | -5,-3 (6) |
| insane_miner | 9 |  | 1 | 1 |  | 1 | 6,6 (3) |
| timid_vir_vur | 8 | 1 |  |  |  | 1 | 5,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_capper_spineflap_hive_neutral_large | ? | 22 | 57 |  | 17 | -7,-3 (24); 6,6 (6); 4,4 (5); -6,-2 (5); 5,7 (5) |
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 21 | 42 |  | 15 | -6,-4 (13); 5,6 (5); 4,4 (5); -7,-2 (5); 3,5 (5) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 12 | 51 |  | 11 | -5,-3 (17); 4,3 (15); 6,5 (6); 3,5 (6); 5,7 (4) |
| rori_borgal_young_lair_neutral_small | ? | 16 | 30 |  | 11 | -5,-1 (9); -4,-3 (7); 4,6 (6); -7,-2 (5); -6,-4 (4) |
| rori_nightspider_lair_neutral_small | ? | 9 | 32 |  | 8 | 4,4 (17); -6,-4 (4); -7,-3 (4); 6,5 (4); 6,4 (4) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 11 | 27 |  | 12 | -6,-1 (9); -5,-4 (6); -6,-2 (4); 4,4 (4); 6,5 (4) |
| rori_sickle_rasp_nest_neutral_medium | ? | 8 | 18 |  | 9 | -5,-4 (4); -7,-3 (4); -7,-4 (3); 4,7 (3); 5,7 (3) |

