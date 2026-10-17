# Naboo: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:26 AM to 3:08 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 200 (0 explorers, 88 that killed something).
- Coverage: 47 of 256 squares of 1 km had a bot or a sighting in them (18%); explorers stood in 0.
- Templates: 13 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 199 | 2 | 112 |  | 20 | 1,1 (60); -6,3 (27); -6,2 (25); 5,-4 (25); 5,6 (23) |
| chuba | 1-5 | 121 | 1 | 46 |  | 14 | -6,4 (27); 4,-5 (21); 6,6 (21); 5,-4 (21); 1,1 (21) |
| flesh_eating_chuba | 1-6 | 115 |  | 37 |  | 14 | 5,6 (38); 6,6 (19); 5,-5 (17); -7,4 (17); 3,-5 (10) |
| capper_spineflap | 1-6 | 81 | 6 | 34 |  | 12 | 5,-5 (24); 5,5 (23); 2,3 (14); 5,6 (12); 4,4 (12) |
| nightspider | 7 | 47 | 3 | 4 |  | 8 | 4,6 (23); 4,-5 (19); 4,-4 (10); -6,3 (8); 5,6 (4) |
| capper_spineflap_drone | 1-6 | 42 |  | 9 |  | 7 | 5,6 (19); -6,3 (11); -5,4 (9); 5,-5 (8); -6,5 (3) |
| massive_gnort | 4 | 36 |  |  |  | 3 | -6,3 (30); 1,2 (5); 4,-5 (2) |
| diseased_nuna | 6 | 10 | 1 | 12 |  | 4 | 0,1 (15); -7,2 (5); 3,-5 (4); 7,6 (3) |
| sentry_hermit_spider | 10 | 3 | 6 | 10 |  | 5 | 4,5 (7); 4,-5 (7); 5,-5 (4); -6,5 (4); 5,-4 (3) |
| large_chuba | 5 | 24 |  |  |  | 3 | 1,3 (17); -6,3 (6); 5,-5 (1) |
| flewt | 1-7 | 20 |  |  |  | 5 | 4,6 (8); 4,-5 (5); 5,6 (4); -6,4 (2); -7,3 (1) |
| ikopi | 7 | 2 | 3 | 5 |  | 2 | 4,5 (8); 6,6 (8) |
| hermit_spider | 7 | 4 | 1 | 2 |  | 3 | 4,4 (5); 4,5 (2); 1,3 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 20 | 45 |  | 17 | 1,1 (13); 5,-4 (7); -6,2 (6); 2,3 (5); 1,4 (5) |
| naboo_chuba_lair_neutral_small | ? | 9 | 15 |  | 8 | 6,6 (5); 5,-4 (4); 1,1 (4); -6,2 (3); 5,-6 (2) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 8 | 13 |  | 7 | -7,4 (7); 6,6 (4); 5,-5 (3); -6,5 (2); 4,4 (2) |
| naboo_capper_spineflap_pod_neutral_small | ? | 4 | 8 |  | 4 | 5,5 (4); 2,3 (3); 4,4 (3); 6,-6 (2) |
| naboo_diseased_nuna_lair_neutral_small | ? | 4 | 6 |  | 4 | 0,1 (4); -7,2 (2); 3,-5 (2); 7,6 (2) |
| naboo_ikopi_lair_neutral_medium | ? | 2 | 3 |  | 2 | 4,5 (3); 6,6 (2) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 1 | 2 |  | 1 | 4,-4 (3) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 1 | 1 |  | 1 | 4,4 (2) |
| naboo_flewt_lair_neutral_boss_02 | ? | 1 |  |  | 1 | -7,5 (1) |

