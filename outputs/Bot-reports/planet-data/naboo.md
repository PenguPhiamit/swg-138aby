# Naboo: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:03 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 332 (0 explorers, 214 that killed something).
- Coverage: 58 of 256 squares of 1 km had a bot or a sighting in them (23%); explorers stood in 0.
- Templates: 14 creatures, 7 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 510 | 7 | 249 |  | 35 | 2,2 (68); 6,6 (60); 0,2 (49); 0,3 (49); -5,4 (43) |
| capper_spineflap | 1-6 | 350 | 2 | 77 |  | 18 | 5,6 (87); 5,-5 (68); -6,3 (65); 4,-5 (48); 4,6 (42) |
| chuba | 1-5 | 305 | 6 | 90 |  | 27 | 4,-5 (40); 5,-4 (35); 4,6 (34); 2,3 (31); 1,3 (29) |
| massive_gnort | 4 | 309 |  | 3 |  | 8 | -6,3 (98); 5,-5 (87); -5,3 (47); 5,6 (40); -6,4 (22) |
| capper_spineflap_drone | 1-6 | 256 |  | 19 |  | 6 | 5,-5 (113); -5,4 (65); 4,6 (44); 5,6 (43); 1,3 (10) |
| flesh_eating_chuba | 1-6 | 190 | 5 | 44 |  | 18 | -6,4 (64); 4,-5 (36); 5,6 (24); -7,4 (22); 0,2 (14) |
| nightspider | 7 | 164 | 2 | 1 |  | 11 | 4,-5 (58); 1,2 (51); 4,6 (35); -6,3 (10); 5,6 (8) |
| flewt | 1-7 | 88 |  | 1 |  | 9 | 5,6 (40); 5,-5 (18); -6,3 (17); 4,-5 (15); 4,-6 (5) |
| large_chuba | 1-5 | 98 |  |  |  | 7 | 1,3 (35); -6,4 (25); -6,3 (17); -7,4 (9); 5,6 (8) |
| diseased_nuna | 6 | 34 | 5 | 40 |  | 11 | -5,3 (16); 4,5 (13); 3,-5 (10); 6,5 (10); -6,2 (8) |
| mott_calf | 4 | 13 |  | 2 |  | 2 | 5,6 (14); 5,5 (1) |
| ikopi | 7 | 14 |  |  |  | 2 | 5,6 (12); 5,5 (2) |
| hermit_spider | 1-7 | 7 | 1 | 5 |  | 3 | 4,5 (10); -6,5 (3); 2,1 (1) |
| spiked_krevol | 1 | 1 |  |  |  | 1 | 0,2 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 43 | 78 |  | 28 | 6,6 (15); 4,-4 (9); 4,5 (8); 2,3 (8); 0,3 (8) |
| naboo_chuba_lair_neutral_small | ? | 20 | 38 |  | 16 | 5,-5 (9); 5,-4 (8); 2,3 (7); 6,5 (5); 3,-5 (3) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 12 | 16 |  | 10 | 4,5 (4); -7,4 (4); 5,-6 (3); 5,5 (3); 0,2 (3) |
| naboo_diseased_nuna_lair_neutral_small | ? | 12 | 16 |  | 11 | -5,3 (5); 3,-5 (3); 4,5 (3); 7,5 (3); -6,2 (2) |
| naboo_capper_spineflap_pod_neutral_small | ? | 8 | 10 |  | 8 | 2,3 (3); -4,3 (3); 3,-5 (2); 5,-6 (2); 3,6 (2) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 1 | 2 |  | 1 | 4,5 (3) |
| naboo_flewt_lair_neutral_boss_02 | ? | 1 | 1 |  | 2 | 3,6 (1); 3,5 (1) |

