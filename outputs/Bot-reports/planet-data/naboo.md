# Naboo: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:25 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `naboo.csv`.

- Bots here: 703 (0 explorers, 218 that killed something).
- Coverage: 67 of 256 squares of 1 km had a bot or a sighting in them (26%); explorers stood in 0.
- Templates: 41 creatures, 14 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 naboo` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| chuba | 1-5 | 215 | 19 | 86 |  | 29 | -5,3 (43); 4,5 (34); -5,5 (33); 5,6 (28); -4,3 (27) |
| gnort | 1-4 | 238 | 12 | 79 |  | 34 | 5,6 (41); 4,6 (39); 3,5 (38); -5,3 (29); 1,3 (21) |
| flesh_eating_chuba | 1-6 | 222 | 18 | 28 |  | 27 | -6,3 (62); 2,2 (36); 5,6 (30); 4,-5 (29); 2,1 (22) |
| capper_spineflap | 1-6 | 132 | 11 | 45 |  | 30 | 4,-5 (35); -5,4 (20); 5,6 (19); 1,3 (17); -5,2 (15) |
| flewt | 1-7 | 125 | 23 | 7 |  | 21 | 5,6 (85); 5,-5 (36); 4,-5 (15); 3,5 (10); 1,4 (9) |
| nightspider | 7 | 93 | 24 | 4 |  | 21 | -5,4 (43); -6,3 (30); -6,4 (23); 4,-5 (14); 5,-5 (12) |
| hermit_spider | 1-7 | 79 | 21 | 14 |  | 21 | 1,3 (42); 2,2 (14); 2,3 (11); 5,5 (11); 5,-5 (9) |
| diseased_nuna | 6 | 64 | 8 | 45 |  | 19 | -6,2 (24); -5,2 (16); -6,5 (13); -7,5 (12); -7,3 (12) |
| ikopi | 1-7 | 21 | 11 | 30 |  | 12 | 2,3 (14); -6,5 (12); 6,6 (12); 2,0 (10); -4,3 (10) |
| sentry_hermit_spider | 10 | 12 | 13 | 24 |  | 13 | -6,3 (19); 4,-5 (10); 1,3 (9); 2,2 (8); -6,4 (6) |
| greater_shaupaut | 14 |  | 18 | 17 |  | 9 | 5,6 (20); 1,3 (12); -5,3 (11); -5,5 (8); -4,3 (5) |
| massive_gnort | 4 | 52 | 3 |  |  | 6 | -6,3 (35); -6,4 (9); 4,-5 (5); -6,2 (5); 3,-4 (4) |
| large_chuba | 1-5 | 43 | 2 |  |  | 9 | -7,4 (21); -6,3 (15); -5,5 (7); 2,3 (4); -7,3 (4) |
| shaupaut | 7 | 20 | 6 | 2 |  | 8 | 5,6 (29); 3,2 (5); 1,3 (3); -5,4 (3); 5,5 (2) |
| narglatch_hunter | 12 |  | 12 | 10 |  | 8 | -7,4 (7); 4,-5 (6); 5,5 (4); 2,3 (4); 5,6 (3) |
| shaupaut_hunter | 22 |  | 6 | 6 |  | 3 | 1,3 (9); 5,5 (7); -7,5 (4) |
| trade_federation_pirate | 10 | 1 | 4 | 4 |  | 2 | 4,5 (16); 4,6 (1) |
| nightspider_poison_spitter | 11 |  | 4 | 4 |  | 2 | -6,3 (8); 6,-5 (7) |
| narglatch_cub | 8 | 1 | 5 | 4 |  | 6 | 4,-5 (7); -7,4 (2); 2,3 (2); 1,3 (1); 5,6 (1) |
| kaadu | 1-10 | 2 | 3 | 3 |  | 2 | 3,-6 (12); 4,-6 (2) |
| plains_hunter | 31 |  | 4 | 2 |  | 3 | -6,3 (6); 5,5 (3); 5,6 (1) |
| peko_peko | 1 | 3 | 2 |  |  | 3 | 2,3 (6); 4,6 (2); 0,1 (1) |
| rogue_falumpaset | 18 |  | 2 | 2 |  | 4 | 4,-4 (4); 2,0 (3); 1,0 (1); 3,-5 (1) |
| nightspider_aggressor | 9 |  | 2 | 2 |  | 1 | -6,3 (8) |
| trade_federation_loyalist | 12 |  | 2 | 2 |  | 1 | 3,1 (8) |
| mott | 1-8 | 1 | 1 | 1 |  | 2 | 3,-6 (4); 4,-5 (1) |
| swamp_rat | 10 |  | 3 | 2 |  | 3 | 0,1 (2); 4,-5 (2); 0,2 (1) |
| male_plains_tusk_cat | 1-16 | 1 | 2 | 1 |  | 2 | -7,3 (4); -5,4 (1) |
| female_narglatch | 23 |  | 2 | 2 |  | 1 | 5,-4 (4) |
| female_swamp_tusk_cat | 16 |  | 1 | 1 |  | 1 | 4,-4 (3) |
| dwarf_nuna | 5 |  |  |  |  | 2 | -7,3 (2); -6,4 (1) |
| male_swamp_tusk_cat | 17 |  | 1 | 1 |  | 1 | 5,-5 (3) |
| kreetle | 3 |  | 1 |  |  | 2 | -6,3 (2); -7,3 (1) |
| spitting_rawl | 24 |  | 1 | 1 |  | 1 | 4,-4 (2) |
| narglatch_guardian | 18 |  | 1 | 1 |  | 1 | 4,5 (2) |
| rill | 6 |  |  |  |  | 1 | -7,3 (2) |
| mauler_apprentice | 12 |  | 1 | 1 |  | 1 | -6,2 (2) |
| veermok_guard | 16 |  | 1 | 1 |  | 1 | 5,5 (2) |
| capper_spineflap_drone | 6 | 1 |  |  |  | 1 | -5,3 (1) |
| otolla_gungan | 10 |  |  |  |  | 1 | 6,-5 (1) |
| corellian_butterfly_drone | 5 |  |  |  |  | 1 | -7,3 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| naboo_gnort_lair_neutral_small | ? | 58 | 88 |  | 34 | -7,3 (10); 2,3 (9); 3,5 (8); -5,3 (8); 2,4 (8) |
| naboo_chuba_lair_neutral_small | ? | 47 | 73 |  | 25 | 4,5 (19); -5,5 (15); -4,3 (9); -7,3 (7); 3,-6 (6) |
| naboo_capper_spineflap_pod_neutral_small | ? | 32 | 51 |  | 24 | -5,4 (11); 6,6 (6); -7,3 (6); -5,5 (5); -5,2 (5) |
| naboo_diseased_nuna_lair_neutral_small | ? | 27 | 45 |  | 20 | -6,5 (9); -6,2 (7); 1,4 (6); 2,3 (6); -7,3 (6) |
| naboo_flesh_eating_chuba_lair_neutral_small | ? | 18 | 31 |  | 15 | -5,4 (6); 2,3 (5); -7,3 (5); 3,-5 (4); -5,3 (3) |
| naboo_ikopi_lair_neutral_medium | ? | 16 | 27 |  | 13 | -6,5 (5); -5,4 (5); -6,2 (4); 2,3 (4); -7,3 (4) |
| naboo_hermit_spider_lair_neutral_boss_01 | ? | 13 | 22 |  | 13 | 6,6 (3); 2,3 (3); 5,5 (3); 5,-4 (3); -4,3 (3) |
| naboo_flewt_lair_neutral_boss_02 | ? | 8 | 24 |  | 6 | -7,4 (17); 3,5 (5); -7,3 (3); 2,2 (3); 6,6 (2) |
| naboo_nightspider_lair_neutral_boss_01 | ? | 6 | 11 |  | 5 | -7,3 (6); 6,6 (3); 0,1 (3); -6,5 (3); -5,5 (2) |
| naboo_mott_lair_neutral_medium | ? | 3 | 3 |  | 3 | 3,-6 (2); -7,3 (2); 6,5 (2) |
| naboo_plasma_thief_camp_neutral_large_theater | ? | 2 | 3 |  | 2 | 0,4 (3); 4,5 (2) |
| naboo_kaadu_lair_neutral_medium_boss_01 | ? | 1 | 3 |  | 1 | 3,-6 (4) |
| naboo_ankura_gungan_camp_neutral_large_theater | ? | 1 | 2 |  | 1 | 4,5 (3) |
| naboo_otolla_gungan_camp_neutral_large_theater | ? | 1 | 1 |  | 1 | -7,5 (2) |

