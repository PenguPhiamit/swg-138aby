# Rori: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:05 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 73 (0 explorers, 40 that killed something).
- Coverage: 29 of 256 squares of 1 km had a bot or a sighting in them (11%); explorers stood in 0.
- Templates: 21 creatures, 6 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| capper_spineflap | 1-6 | 126 | 9 | 94 |  | 18 | -6,-2 (35); 5,6 (33); 3,5 (26); -6,-4 (25); -6,-3 (24) |
| nightspider | 7 | 74 | 22 | 38 |  | 15 | 4,5 (37); -5,-3 (27); -6,-3 (25); 5,4 (24); 5,5 (20) |
| young_borgle | 6 | 45 | 9 | 54 |  | 8 | -6,-2 (36); 5,6 (23); 3,6 (18); -6,-4 (16); 6,6 (15) |
| ikopi | 7 | 68 | 8 | 13 |  | 11 | 5,5 (47); 6,5 (16); 4,6 (12); -6,-3 (11); -7,-3 (11) |
| garyns_prowler | 11 |  | 17 | 17 |  | 1 | 5,5 (62) |
| frail_squall | 6 | 50 |  |  |  | 2 | 5,5 (46); -6,-3 (9) |
| swamp_rat | 10 | 3 | 25 | 19 |  | 2 | 5,5 (37); 4,5 (15) |
| gundark_crook | 5 | 16 | 4 | 20 |  | 7 | 5,6 (14); -7,-2 (12); 4,4 (11); 3,5 (4); -6,-2 (4) |
| gundark_rogue | 7 | 12 | 3 | 15 |  | 6 | 6,4 (14); 4,4 (8); -6,-2 (8); 5,6 (5); 6,6 (4) |
| young_borgle_gruntling | 6 | 18 | 2 | 6 |  | 5 | -5,-3 (12); 4,6 (9); -6,-2 (8); -6,-3 (4); 4,4 (1) |
| capper_spineflap_drone | 1-6 | 24 |  | 7 |  | 3 | -5,-3 (12); -6,-2 (10); -6,-3 (10) |
| vrobalet | 8 | 12 | 4 | 2 |  | 3 | 4,5 (19); 5,5 (5); -6,-3 (3) |
| gundark_hooligan | 6 | 11 |  | 11 |  | 6 | 5,6 (10); 6,4 (4); 6,6 (4); 3,4 (4); 3,5 (2) |
| hermit_spider | 1-7 | 21 |  |  |  | 4 | -6,-2 (11); -6,-3 (6); -7,-3 (2); -6,-4 (2) |
| pigmy_pugoriss | 8 | 19 |  |  |  | 1 | 5,5 (21) |
| frightened_borgle | 8 | 10 | 2 |  |  | 2 | 5,5 (10); -5,-3 (7) |
| first_brigade_trooper | 6 | 8 |  | 8 |  | 3 | 6,6 (7); -7,-3 (6); 5,4 (4) |
| timid_vir_vur | 8 | 13 | 1 |  |  | 2 | 5,5 (14); -6,-3 (2) |
| first_brigade_scout | 7 | 4 |  | 4 |  | 3 | 5,4 (5); 6,6 (2); -7,-3 (2) |
| scorched_krevol | 8 | 1 | 2 | 1 |  | 2 | 5,5 (5); -6,-2 (3) |
| meek_avenging_squall | 6 | 1 |  |  |  | 1 | 3,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 13 | 35 |  | 9 | 5,6 (12); 4,4 (11); 6,4 (6); -6,-2 (5); -7,-2 (4) |
| rori_capper_spineflap_hive_neutral_large | ? | 17 | 29 |  | 13 | -6,-4 (7); -4,-3 (6); 3,5 (6); -7,-3 (5); 4,3 (4) |
| rori_borgal_young_lair_neutral_small | ? | 10 | 36 |  | 8 | -6,-5 (18); -6,-2 (8); 3,6 (4); 5,6 (4); -6,-4 (4) |
| rori_nightspider_lair_neutral_small | ? | 9 | 23 |  | 9 | 5,4 (5); 5,5 (4); 4,6 (4); -5,-3 (4); 3,4 (3) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 4 | 9 |  | 4 | 6,5 (4); 4,6 (4); -7,-3 (3); 5,7 (2) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 3 | 9 |  | 3 | -7,-3 (7); 6,6 (3); 5,4 (2) |

