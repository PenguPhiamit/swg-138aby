# Naboo: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:34 AM to 1:01 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 357 (0 explorers, 204 that killed something).
- Coverage: 65 of 256 squares of 1 km had a bot or a sighting in them (25%); explorers stood in 0.
- Templates: 20 creatures, 12 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 575 | 5 | 416 |  | 41 | 5,5 (98); -7,3 (74); 6,5 (72); -6,3 (62); 1,4 (42) |
| chuba | 1-5 | 331 | 11 | 208 |  | 31 | 2,3 (55); 3,-5 (53); 6,-6 (43); 4,-5 (36); -6,3 (35) |
| capper_spineflap | 1-6 | 251 | 18 | 97 |  | 23 | 5,6 (74); 4,6 (50); 4,-5 (44); 5,-4 (35); 4,-4 (26) |
| flesh_eating_chuba | 1-6 | 181 | 14 | 113 |  | 24 | 6,5 (38); 2,1 (35); 4,5 (31); -6,2 (26); 5,-4 (22) |
| diseased_nuna | 6 | 142 | 14 | 139 |  | 21 | -7,3 (48); 6,6 (40); 5,-4 (30); 3,-5 (23); 6,5 (23) |
| nightspider | 7 | 143 | 10 | 20 |  | 13 | 5,-5 (76); -6,3 (22); 1,3 (21); 4,-4 (21); -5,3 (12) |
| flewt | 1-7 | 95 | 12 | 34 |  | 15 | 5,6 (43); 0,3 (20); 3,-5 (16); 2,1 (15); 0,1 (14) |
| ikopi | 1-7 | 36 | 16 | 36 |  | 12 | 6,6 (16); 3,-5 (16); 5,6 (15); 6,-6 (14); 4,-4 (14) |
| capper_spineflap_drone | 1-6 | 66 |  | 7 |  | 2 | -6,3 (50); 5,6 (27) |
| mott | 1-8 | 4 | 13 | 17 |  | 3 | -5,5 (24); 3,-5 (18); 5,5 (18) |
| ankura_gungan | 8 | 9 | 10 | 19 |  | 5 | 6,6 (20); 3,2 (12); 0,4 (10); 6,-4 (8); 3,-4 (8) |
| hermit_spider | 1-7 | 15 | 6 | 21 |  | 7 | -4,4 (13); 3,4 (8); 1,0 (8); -5,2 (8); 5,5 (7) |
| massive_gnort | 4 | 46 |  |  |  | 4 | 4,-5 (22); 4,6 (19); 4,7 (4); 4,5 (1) |
| large_chuba | 1-5 | 37 |  |  |  | 3 | 5,6 (32); 4,-5 (3); 2,2 (2) |
| plasma_bandit | 8 | 4 | 3 | 7 |  | 4 | -5,4 (10); 3,5 (7); 5,-4 (4); 2,1 (4) |
| sentry_hermit_spider | 10 | 2 | 3 | 5 |  | 2 | 3,-6 (11); -6,2 (2) |
| plasma_thief | 7 | 3 | 1 | 4 |  | 3 | -5,4 (4); 2,1 (2); 5,-4 (2) |
| motley_kaadu | 1-8 | 4 |  |  |  | 2 | 4,-5 (3); 5,-4 (2) |
| nightspider_aggressor | 9 |  | 1 | 1 |  | 1 | 6,-5 (4) |
| plasma_thief_leader | 9 | 1 |  | 1 |  | 1 | 2,1 (3) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 60 | 167 |  | 37 | -7,3 (30); 5,5 (24); 5,-4 (23); 6,5 (20); 1,4 (10) |
| naboo_chuba_lair_neutral_small | ? | 35 | 108 |  | 25 | -6,5 (16); -8,4 (14); 3,-5 (12); 2,3 (11); 6,-6 (10) |
| naboo_diseased_nuna_lair_neutral_small | ? | 23 | 56 |  | 20 | -7,3 (11); 6,6 (10); 6,5 (6); 3,-5 (5); 5,5 (5) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 18 | 60 |  | 13 | 4,-4 (17); 6,5 (8); 2,1 (8); 5,-4 (7); 4,5 (7) |
| naboo_capper_spineflap_pod_neutral_small | ? | 13 | 32 |  | 10 | 5,-4 (8); 4,-4 (8); -5,2 (6); 6,5 (4); -6,5 (4) |
| naboo_flewt_lair_neutral_boss_02 | ? | 9 | 33 |  | 9 | -7,3 (16); 0,1 (5); 3,-5 (4); 0,3 (4); 4,4 (3) |
| naboo_ikopi_lair_neutral_medium | ? | 11 | 26 |  | 11 | 6,6 (6); 3,-5 (5); 6,-6 (4); 4,-4 (4); -4,4 (4) |
| naboo_ankura_gungan_camp_neutral_large_theater | ? | 6 | 15 |  | 6 | 6,6 (8); 3,2 (3); 6,-4 (3); 3,-4 (3); 0,4 (3) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 6 | 13 |  | 8 | -4,4 (3); 5,6 (3); -7,3 (3); 1,0 (3); -5,2 (3) |
| naboo_mott_lair_neutral_medium | ? | 4 | 14 |  | 3 | -5,5 (8); 3,-5 (5); 5,5 (5) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 5 | 11 |  | 5 | 4,-4 (4); 5,5 (3); 1,4 (3); -6,2 (3); 3,3 (3) |
| naboo_plasma_thief_camp_neutral_large_theater | ? | 4 | 9 |  | 4 | -5,4 (4); 2,1 (3); 3,5 (3); 5,-4 (3) |

