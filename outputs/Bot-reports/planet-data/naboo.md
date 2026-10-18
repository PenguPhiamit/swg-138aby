# Naboo: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:05 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 179 (0 explorers, 70 that killed something).
- Coverage: 61 of 256 squares of 1 km had a bot or a sighting in them (24%); explorers stood in 0.
- Templates: 20 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 296 | 2 | 182 |  | 28 | 6,-5 (53); 4,5 (34); 5,-5 (32); 5,5 (32); 5,-4 (31) |
| capper_spineflap | 1-6 | 166 | 7 | 126 |  | 27 | -6,5 (38); 2,1 (35); 5,5 (28); 4,-4 (22); 5,6 (19) |
| chuba | 1-5 | 160 | 7 | 95 |  | 20 | 4,5 (35); 2,3 (33); -6,5 (32); 6,-4 (24); 4,-5 (23) |
| flesh_eating_chuba | 1-6 | 115 | 2 | 39 |  | 19 | 4,-5 (44); 3,5 (23); -7,3 (15); -7,4 (14); 5,5 (12) |
| diseased_nuna | 6 | 55 | 3 | 49 |  | 11 | 6,-4 (22); 2,1 (20); -5,5 (17); 1,3 (16); 3,-4 (11) |
| nightspider | 7 | 51 | 7 | 6 |  | 14 | 4,-5 (25); 5,5 (12); 1,3 (11); 5,6 (9); 6,5 (8) |
| sentry_hermit_spider | 10 | 9 | 20 | 30 |  | 13 | 5,-5 (20); 5,6 (11); 3,-5 (8); 4,5 (7); 6,6 (6) |
| flewt | 1-7 | 51 | 1 | 11 |  | 12 | 5,6 (13); -1,2 (12); 6,6 (10); 2,3 (7); -6,3 (6) |
| massive_gnort | 4 | 59 |  |  |  | 7 | 5,6 (25); -6,3 (13); 1,3 (9); 5,5 (5); 5,-5 (5) |
| hermit_spider | 1-7 | 29 | 2 | 18 |  | 8 | 4,-4 (20); 0,3 (14); 5,6 (7); -6,2 (7); -6,3 (3) |
| capper_spineflap_drone | 1-6 | 34 | 1 | 12 |  | 5 | -6,3 (24); 5,6 (8); 5,-5 (7); 4,6 (7); 4,-5 (3) |
| ikopi | 7 | 14 | 4 | 14 |  | 8 | 3,2 (12); 5,-6 (12); 5,-4 (6); 6,6 (5); 3,6 (5) |
| large_chuba | 1-5 | 26 |  |  |  | 6 | 5,6 (6); 5,-6 (6); 1,3 (6); -5,3 (5); 4,-5 (4) |
| nightspider_poison_spitter | 11 |  | 4 | 4 |  | 2 | 3,-5 (8); 3,-6 (8) |
| mauler_apprentice | 12 |  | 5 | 5 |  | 2 | 4,-4 (6); 4,-5 (5) |
| mott_calf | 4 | 6 |  | 2 |  | 1 | 5,6 (8) |
| spiked_krevol | 1-10 | 3 | 1 |  |  | 3 | 5,6 (3); 2,3 (2); 0,2 (1) |
| nuna | 1-10 | 1 |  |  |  | 2 | 4,-6 (1); 4,-5 (1) |
| swamp_rat | 10 |  | 1 | 1 |  | 1 | 5,-4 (2) |
| hermit_spider_queen | 11 | 1 |  | 1 |  | 1 | 4,-4 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 25 | 78 |  | 19 | 6,-5 (18); 4,5 (9); 0,2 (8); -6,5 (7); 5,5 (7) |
| naboo_capper_spineflap_pod_neutral_small | ? | 19 | 39 |  | 16 | -6,5 (9); 5,5 (6); 2,1 (6); 4,-4 (5); 3,5 (3) |
| naboo_chuba_lair_neutral_small | ? | 14 | 30 |  | 13 | 4,5 (8); -6,5 (6); 6,-4 (4); 2,3 (4); 2,4 (4) |
| naboo_diseased_nuna_lair_neutral_small | ? | 9 | 21 |  | 9 | -5,5 (6); 2,1 (5); 6,-4 (5); 5,4 (3); 1,3 (3) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 9 | 13 |  | 8 | -7,3 (4); 3,5 (4); 5,-4 (3); 5,5 (3); -7,5 (2) |
| naboo_ikopi_lair_neutral_medium | ? | 5 | 9 |  | 5 | 3,2 (4); 5,-6 (4); 6,6 (2); 5,-4 (2); 3,6 (2) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 3 | 7 |  | 3 | 4,-4 (5); -6,2 (3); 0,3 (2) |
| naboo_flewt_lair_neutral_boss_02 | ? | 3 | 4 |  | 3 | 6,6 (3); -1,2 (2); 2,3 (2) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 2 | 5 |  | 2 | 5,5 (4); 6,5 (3) |

