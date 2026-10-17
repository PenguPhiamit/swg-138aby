# Rori: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:03 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 166 (0 explorers, 109 that killed something).
- Coverage: 29 of 256 squares of 1 km had a bot or a sighting in them (11%); explorers stood in 0.
- Templates: 19 creatures, 5 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ikopi | 1-7 | 319 | 1 | 11 |  | 10 | 5,5 (89); -6,-2 (76); -6,-3 (70); -5,-3 (54); -5,-2 (15) |
| capper_spineflap | 1-6 | 137 | 7 | 59 |  | 17 | -6,-3 (65); 5,6 (38); -6,-2 (24); 6,5 (18); 3,5 (14) |
| nightspider | 7 | 130 | 4 | 4 |  | 9 | -6,-3 (48); 4,5 (44); -5,-3 (17); 5,5 (15); 5,6 (9) |
| meek_avenging_squall | 6 | 133 |  | 4 |  | 3 | -6,-3 (94); -5,-3 (38); 5,6 (6) |
| young_borgle | 6 | 28 | 9 | 37 |  | 10 | -6,-2 (21); 6,6 (17); -6,-4 (15); -5,-2 (12); -5,-3 (10) |
| hermit_spider | 7 | 97 |  |  |  | 8 | -6,-2 (39); -6,-3 (23); -5,-3 (11); 4,6 (8); 5,4 (7) |
| frail_squall | 6 | 88 |  |  |  | 2 | 5,5 (62); -6,-3 (28) |
| capper_spineflap_drone | 1-6 | 41 | 1 | 7 |  | 6 | -6,-3 (33); 5,5 (10); 4,5 (4); 4,6 (3); -5,-3 (3) |
| gundark_hooligan | 6 | 15 | 2 | 17 |  | 9 | -5,-2 (8); 6,4 (7); 3,6 (5); 6,5 (5); -7,-4 (5) |
| garyns_prowler | 11 | 2 | 6 | 12 |  | 1 | 5,5 (39) |
| scorched_krevol | 8 | 18 | 4 | 3 |  | 2 | -6,-2 (31); 5,5 (3) |
| young_borgle_gruntling | 6 | 19 | 2 | 6 |  | 3 | -6,-2 (17); 4,5 (13); 5,4 (3) |
| gundark_rogue | 7 | 6 | 3 | 9 |  | 5 | -7,-4 (9); -7,-3 (8); -6,-4 (4); 7,5 (4); -5,-2 (2) |
| swamp_rat | 10 | 3 | 7 | 10 |  | 2 | 5,5 (19); 4,5 (6) |
| frightened_borgle | 8 | 21 |  |  |  | 2 | -5,-3 (19); 5,5 (2) |
| vrobalet | 8 | 7 | 2 | 2 |  | 1 | -6,-3 (20) |
| pigmy_pugoriss | 8 | 15 |  |  |  | 1 | 5,5 (15) |
| gundark_crook | 5 | 6 |  | 6 |  | 5 | -5,-4 (6); 3,6 (2); -7,-3 (2); 7,5 (2); 6,4 (2) |
| timid_vir_vur | 8 | 13 |  |  |  | 2 | 5,5 (8); -6,-3 (5) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_capper_spineflap_hive_neutral_large | ? | 17 | 20 |  | 13 | 6,5 (6); 5,6 (4); 3,5 (4); -6,-4 (3); -7,-3 (3) |
| rori_borgal_young_lair_neutral_small | ? | 14 | 20 |  | 10 | -6,-2 (6); -6,-4 (5); -5,-4 (4); 6,6 (4); -5,-3 (3) |
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 13 | 18 |  | 10 | -5,-2 (5); -5,-4 (4); -7,-4 (4); -7,-3 (4); 7,5 (3) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 2 | 3 |  | 2 | -7,-2 (3); -5,-1 (2) |
| rori_nightspider_lair_neutral_small | ? | 2 | 2 |  | 2 | -5,-1 (2); -6,-1 (2) |

