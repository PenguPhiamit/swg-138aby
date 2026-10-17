# Naboo: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:03 PM to 7:17 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 332 (0 explorers, 208 that killed something).
- Coverage: 76 of 256 squares of 1 km had a bot or a sighting in them (30%); explorers stood in 0.
- Templates: 46 creatures, 19 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| gnort | 1-4 | 1040 | 47 | 155 |  | 65 | 4,-5 (142); 5,6 (104); 3,-5 (57); 1,4 (57); 5,5 (55) |
| chuba | 1-5 | 761 | 36 | 130 |  | 59 | 4,-5 (110); 4,6 (83); 5,6 (77); 5,-5 (56); 6,6 (48) |
| capper_spineflap | 1-6 | 531 | 55 | 103 |  | 50 | 5,6 (212); 5,-5 (72); 3,-5 (54); 1,3 (48); -7,4 (44) |
| flesh_eating_chuba | 1-6 | 429 | 27 | 100 |  | 49 | 1,3 (62); 4,5 (40); 4,6 (39); 3,-4 (35); 6,6 (33) |
| nightspider | 7 | 196 | 40 | 17 |  | 47 | 5,6 (69); 5,-5 (65); 4,-5 (61); 4,-6 (35); -6,4 (32) |
| diseased_nuna | 6 | 221 | 32 | 101 |  | 44 | 5,-4 (54); -5,3 (34); 3,-5 (34); 3,-6 (32); -7,3 (21) |
| flewt | 1-7 | 233 | 27 | 52 |  | 42 | 1,2 (56); 2,3 (40); 4,-6 (37); 6,6 (36); 4,6 (28) |
| hermit_spider | 1-7 | 170 | 42 | 59 |  | 41 | 1,3 (59); 4,6 (43); 6,6 (27); -5,4 (23); 5,-4 (22) |
| ikopi | 1-7 | 74 | 27 | 48 |  | 38 | 1,1 (41); 5,5 (17); -5,2 (16); 6,-6 (14); -6,5 (13) |
| massive_gnort | 4 | 133 | 1 |  |  | 13 | -6,3 (52); 4,6 (29); 5,6 (24); 2,2 (10); -5,4 (10) |
| mott | 1-8 | 3 | 13 | 14 |  | 19 | 1,3 (15); 3,2 (14); -6,3 (10); 1,0 (10); 6,-5 (9) |
| shaupaut | 1-7 | 19 | 17 |  |  | 14 | 4,6 (21); 5,6 (17); 1,2 (15); -7,4 (15); 3,6 (6) |
| capper_spineflap_drone | 1-6 | 37 | 4 | 2 |  | 16 | 5,-6 (20); -6,3 (19); -7,3 (6); 5,6 (6); 0,3 (5) |
| large_chuba | 1-5 | 44 | 1 |  |  | 11 | 5,-5 (17); 3,-5 (12); 4,-5 (7); -5,4 (6); 6,6 (4) |
| rabid_shaupaut | 9 | 16 | 9 | 8 |  | 14 | 5,5 (8); 2,2 (6); 0,3 (5); 6,5 (5); -5,4 (5) |
| sentry_hermit_spider | 10 | 16 | 5 | 8 |  | 11 | 4,6 (12); 5,6 (6); 1,1 (5); -7,4 (4); 1,3 (4) |
| swamp_rat | 10 |  | 6 | 6 |  | 3 | 3,-6 (9); 4,-5 (9); 3,-4 (4) |
| spiked_krevol | 1-10 | 1 | 4 | 3 |  | 6 | 5,-5 (8); 3,-5 (4); 2,1 (3); 4,5 (3); -7,4 (2) |
| ankura_gungan | 8 | 6 | 2 | 8 |  | 4 | 6,6 (10); 6,-5 (4); 4,5 (4); 1,1 (2) |
| narglatch_cub | 8 | 6 | 6 | 1 |  | 7 | 2,3 (5); 3,-5 (3); 5,-6 (3); 0,3 (2); -5,4 (1) |
| rogue_falumpaset | 18 |  | 4 | 4 |  | 4 | 5,-5 (4); 3,-4 (4); 1,1 (4); 5,-6 (2) |
| narglatch_hunter | 12 |  | 5 | 4 |  | 4 | -5,3 (4); 0,3 (3); 2,3 (3); 2,2 (2) |
| greater_shaupaut | 1-14 |  | 3 | 2 |  | 3 | 5,6 (4); 3,-6 (4); 5,-5 (3) |
| veermok_sentry | 9 | 1 | 2 | 2 |  | 1 | 5,-6 (9) |
| plasma_thief | 7 |  | 2 | 2 |  | 2 | 1,0 (4); 0,1 (4) |
| kaadu | 1-10 | 6 |  |  |  | 4 | 1,0 (3); -7,4 (2); 0,1 (2); 3,-5 (1) |
| mott_calf | 4 | 7 |  |  |  | 2 | 5,6 (4); 5,5 (3) |
| plasma_bandit | 8 | 1 | 1 | 2 |  | 2 | 2,1 (4); -6,2 (2) |
| male_swamp_tusk_cat | 1-17 | 1 | 2 | 1 |  | 2 | 4,-6 (3); 4,-5 (2) |
| peko_peko | 1 | 2 |  |  |  | 3 | 6,6 (3); 1,3 (1); 5,6 (1) |
| trade_federation_loyalist | 12 |  | 1 | 1 |  | 2 | 5,5 (4); 1,1 (1) |
| kaadu_male | 1-14 | 1 | 1 | 1 |  | 1 | 6,6 (5) |
| female_swamp_tusk_cat | 1-16 | 1 | 2 | 1 |  | 2 | 5,-5 (2); 4,-5 (2) |
| plasma_thief_leader | 9 |  | 1 | 1 |  | 1 | -6,2 (4) |
| rogue_fambaa | 37 |  | 1 | 1 |  | 1 | -5,2 (4) |
| nightspider_poison_spitter | 11 |  | 1 | 1 |  | 1 | 0,3 (4) |
| female_narglatch | 2-23 |  | 2 |  |  | 2 | 6,5 (2); 5,5 (1) |
| motley_kaadu | 8 | 3 |  |  |  | 1 | 6,6 (3) |
| shaupaut_hunter | 2 |  | 1 |  |  | 1 | -7,4 (3) |
| carnivorous_nuna | 1 | 3 |  |  |  | 2 | 2,1 (2); -7,4 (1) |
| flewt_leviathan | 9 | 1 |  | 1 |  | 2 | 6,5 (2); 5,5 (1) |
| otolla_gungan | 10 | 1 |  | 1 |  | 1 | 4,5 (3) |
| plodding_falumpaset | 1-10 | 1 |  |  |  | 2 | 0,1 (1); 5,-5 (1) |
| nuna | 10 | 1 |  |  |  | 2 | 5,5 (1); -7,3 (1) |
| female_plains_tusk_cat | 16 |  | 1 | 1 |  | 1 | -7,4 (2) |
| vine_rawl | 1 |  | 1 |  |  | 1 | 2,3 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 419 |  |  | 61 | 5,5 (24); 4,-4 (18); 4,5 (18); 6,5 (17); 6,6 (16) |
| naboo_chuba_lair_neutral_small | ? | 249 |  |  | 59 | 6,6 (15); 4,5 (14); 4,-4 (13); 6,5 (13); 5,-4 (11) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 171 |  |  | 49 | 4,5 (12); 6,6 (9); 3,-4 (8); 6,5 (8); 0,1 (7) |
| naboo_diseased_nuna_lair_neutral_small | ? | 156 |  |  | 46 | 5,-4 (8); 5,5 (8); 6,5 (8); -7,4 (7); -5,3 (6) |
| naboo_capper_spineflap_pod_neutral_small | ? | 143 |  |  | 52 | 3,-5 (9); 4,5 (8); 4,-4 (8); 0,3 (6); 5,5 (6) |
| naboo_ikopi_lair_neutral_medium | ? | 87 |  |  | 40 | 1,1 (6); 4,5 (6); -6,5 (6); 5,5 (5); 3,-4 (4) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 82 |  |  | 45 | 6,6 (6); 5,-4 (4); 2,3 (4); 4,5 (4); 6,-5 (3) |
| naboo_flewt_lair_neutral_boss_02 | ? | 80 |  |  | 40 | 6,5 (7); 4,5 (6); 5,5 (6); 6,-5 (6); 6,6 (5) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 79 |  |  | 41 | -6,2 (6); 6,6 (4); 4,5 (4); 3,-6 (3); 2,-6 (3) |
| naboo_plasma_thief_camp_neutral_large_theater | ? | 39 |  |  | 27 | 2,1 (4); 4,5 (4); 0,1 (2); 5,-6 (2); 3,2 (2) |
| naboo_mott_lair_neutral_medium | ? | 33 |  |  | 27 | 5,-4 (2); 2,4 (2); -6,3 (2); -5,2 (2); 0,1 (2) |
| naboo_ankura_gungan_camp_neutral_large_theater | ? | 21 |  |  | 17 | 6,6 (2); 4,-4 (2); 6,-5 (2); 4,5 (2); -7,5 (1) |
| naboo_sharupat_family_diseased_neutral_medium | ? | 20 |  |  | 17 | 6,6 (3); -6,2 (2); 5,5 (1); -8,3 (1); 2,4 (1) |
| naboo_krevol_lair_neutral_boss_02 | ? | 5 |  |  | 5 | 2,1 (1); 5,-5 (1); 6,5 (1); 3,-5 (1); 3,2 (1) |
| naboo_otolla_gungan_camp_neutral_large_theater | ? | 4 |  |  | 4 | -7,5 (1); 1,3 (1); 4,5 (1); 6,4 (1) |
| naboo_nuna_lair_neutral_medium | ? | 2 |  |  | 2 | 5,5 (1); -7,3 (1) |
| naboo_veermok_camp_neutral_medium | ? | 1 |  |  | 1 | 5,-6 (1) |
| naboo_trade_federation_camp_neutral_large_theater | ? | 1 |  |  | 1 | 3,-5 (1) |
| naboo_kaadu_lair_neutral_medium_boss_01 | ? | 1 |  |  | 1 | 1,0 (1) |

