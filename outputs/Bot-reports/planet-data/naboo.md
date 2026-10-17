# Naboo: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:33 PM to 12:31 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 643 (0 explorers, 213 that killed something).
- Coverage: 67 of 256 squares of 1 km had a bot or a sighting in them (26%); explorers stood in 0.
- Templates: 19 creatures, 12 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 284 | 1 | 105 |  | 39 | 5,6 (43); -7,4 (39); -6,3 (33); -6,5 (27); -5,4 (21) |
| chuba | 1-5 | 309 | 1 | 47 |  | 35 | 4,-5 (55); 5,6 (48); -6,4 (34); 5,-5 (30); 2,2 (23) |
| flesh_eating_chuba | 1-6 | 269 | 3 | 32 |  | 22 | 5,6 (102); -6,3 (55); -5,3 (42); 5,-5 (33); -5,5 (17) |
| capper_spineflap | 1-6 | 157 | 5 | 37 |  | 32 | -5,4 (37); 5,6 (21); 5,-5 (21); 1,2 (21); 4,-4 (16) |
| flewt | 1-7 | 113 | 6 | 23 |  | 20 | 5,6 (56); 1,3 (14); 2,3 (11); 3,-5 (11); -6,3 (10) |
| diseased_nuna | 6 | 56 | 4 | 48 |  | 17 | -5,5 (24); 1,4 (22); -6,2 (12); 6,5 (9); -5,2 (9) |
| nightspider | 7 | 48 | 3 | 9 |  | 16 | 5,-5 (18); -5,4 (12); 4,-5 (11); 5,5 (8); 6,-6 (7) |
| hermit_spider | 1-7 | 25 | 4 | 26 |  | 12 | -6,2 (12); -6,3 (12); 6,5 (10); 2,3 (10); -6,5 (9) |
| ikopi | 1-7 | 30 | 7 | 17 |  | 10 | 2,2 (16); 4,6 (15); 4,-4 (12); 2,3 (12); 2,4 (7) |
| large_chuba | 1-5 | 39 |  |  |  | 3 | 4,-5 (43); 3,-4 (1); -6,5 (1) |
| capper_spineflap_drone | 1-6 | 30 |  | 2 |  | 11 | -6,4 (23); 4,-4 (5); 1,3 (4); -6,5 (2); -5,3 (2) |
| ankura_gungan | 8 | 1 | 4 | 5 |  | 3 | 6,6 (12); 5,-4 (5); 2,1 (5) |
| massive_gnort | 4 | 19 |  |  |  | 5 | 0,2 (7); -7,3 (7); 4,-5 (3); 2,1 (1); -5,4 (1) |
| mott | 1-8 | 2 | 2 | 3 |  | 3 | -7,4 (7); 4,-4 (6); 3,2 (3) |
| sentry_hermit_spider | 10 |  | 6 | 6 |  | 4 | 4,5 (7); -6,4 (3); 5,5 (3); -5,4 (2) |
| plasma_thief | 7 | 2 | 1 | 3 |  | 4 | 0,4 (5); 4,-4 (4); 2,1 (2); 2,2 (2) |
| paralope | 6 |  |  |  |  | 1 | -5,3 (2) |
| giant_gubbur | 9 |  |  |  |  | 1 | -5,3 (1) |
| kreetle | 1 |  |  |  |  | 1 | -5,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 73 | 140 |  | 35 | 4,5 (21); 4,-4 (13); -7,4 (13); 1,3 (12); 6,5 (11) |
| naboo_chuba_lair_neutral_small | ? | 34 | 74 |  | 22 | -5,5 (19); -7,3 (12); 6,6 (9); 3,-4 (6); 3,-5 (6) |
| naboo_diseased_nuna_lair_neutral_small | ? | 33 | 54 |  | 21 | 6,5 (10); -5,5 (8); 1,4 (7); 2,1 (6); -7,2 (6) |
| naboo_capper_spineflap_pod_neutral_small | ? | 21 | 34 |  | 19 | 4,-4 (6); 1,0 (4); -5,2 (4); 6,5 (3); -7,2 (3) |
| naboo_flewt_lair_neutral_boss_02 | ? | 17 | 30 |  | 15 | -7,3 (6); -5,3 (6); 3,-5 (3); 1,1 (3); -5,5 (3) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 17 | 26 |  | 14 | 6,5 (6); 6,6 (6); 0,4 (5); 6,-6 (3); 5,5 (3) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 13 | 27 |  | 12 | 2,3 (7); -5,3 (6); -5,5 (5); -7,3 (4); 6,6 (3) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 13 | 26 |  | 12 | -5,5 (7); 6,5 (4); -6,3 (4); 2,3 (3); 2,1 (3) |
| naboo_ikopi_lair_neutral_medium | ? | 12 | 24 |  | 11 | 2,2 (4); 4,-4 (4); 2,3 (4); 3,3 (4); 5,5 (3) |
| naboo_plasma_thief_camp_neutral_large_theater | ? | 4 | 12 |  | 4 | 4,-4 (6); 0,4 (4); 3,3 (3); 2,1 (3) |
| naboo_mott_lair_neutral_medium | ? | 4 | 8 |  | 4 | 4,-4 (4); 3,2 (3); -7,4 (3); -5,5 (2) |
| naboo_ankura_gungan_camp_neutral_large_theater | ? | 4 | 8 |  | 4 | 6,6 (4); 5,-4 (3); 2,1 (3); 6,5 (2) |

