# Rori: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:03 PM to 7:16 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 166 (0 explorers, 105 that killed something).
- Coverage: 41 of 256 squares of 1 km had a bot or a sighting in them (16%); explorers stood in 0.
- Templates: 33 creatures, 10 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| capper_spineflap | 1-6 | 220 | 91 | 124 |  | 34 | 5,6 (86); -5,-3 (75); -6,-2 (72); 6,4 (50); -7,-3 (43) |
| nightspider | 7 | 130 | 56 | 27 |  | 34 | -6,-3 (176); 4,5 (55); -5,-3 (49); 6,5 (40); 5,5 (29) |
| ikopi | 1-7 | 161 | 31 | 21 |  | 31 | 5,5 (112); -6,-3 (75); 5,6 (40); -5,-3 (36); -6,-2 (33) |
| young_borgle | 6 | 42 | 66 | 90 |  | 30 | -7,-3 (40); -5,-4 (38); 3,5 (34); 5,7 (34); 6,5 (34) |
| meek_avenging_squall | 6 | 138 | 2 |  |  | 16 | -6,-2 (100); -6,-3 (28); 5,4 (16); 4,5 (10); -5,-3 (9) |
| frail_squall | 6 | 123 | 4 |  |  | 7 | 5,5 (107); -6,-3 (54); 3,6 (3); 4,6 (2); -5,-4 (2) |
| capper_spineflap_drone | 6 | 33 | 11 | 1 |  | 23 | -6,-3 (20); -5,-2 (14); -6,-2 (13); -5,-3 (13); 5,6 (9) |
| young_borgle_gruntling | 6 | 39 | 7 | 3 |  | 15 | -6,-3 (41); 6,5 (19); 5,5 (10); -6,-2 (6); -4,-2 (5) |
| gundark_rogue | 7 | 6 | 13 | 21 |  | 13 | -6,-4 (16); 5,7 (8); 5,4 (7); 4,7 (6); 5,5 (6) |
| hermit_spider | 1-7 | 10 | 1 |  |  | 16 | -6,-3 (13); -5,-3 (11); -6,-4 (6); -5,-2 (5); 4,6 (5) |
| sickle_rasp | 8 | 6 | 11 | 14 |  | 11 | 6,6 (12); 5,4 (12); -7,-2 (9); -4,-3 (8); 6,5 (6) |
| first_brigade_scout | 7 | 5 | 12 | 18 |  | 8 | 5,4 (11); -5,-5 (10); -7,-3 (8); -5,-4 (8); 3,5 (7) |
| gundark_hooligan | 6 | 9 | 9 | 17 |  | 14 | -5,-1 (11); 5,6 (8); -5,-4 (5); 4,4 (4); 4,7 (4) |
| first_brigade_trooper | 6 | 4 | 11 | 17 |  | 10 | -5,-4 (11); 4,4 (6); -7,-3 (6); 6,4 (6); -6,-4 (6) |
| vicious_squall | 1-12 | 4 | 10 | 10 |  | 6 | -6,-3 (18); -6,-2 (11); -5,-2 (8); 5,7 (4); 4,5 (4) |
| gundark_crook | 5 | 13 | 6 | 19 |  | 14 | -6,-4 (8); 5,4 (6); -5,-4 (5); 3,7 (4); -4,-3 (4) |
| scorched_krevol | 8 | 9 | 9 | 4 |  | 3 | -6,-2 (24); 5,5 (15); -7,-2 (1) |
| vrobalet | 8 | 5 | 9 | 3 |  | 4 | -6,-3 (24); 4,5 (5); 5,5 (3); -7,-2 (1) |
| timid_vir_vur | 8 | 20 |  |  |  | 2 | 5,5 (15); -6,-3 (12) |
| garyns_prowler | 11 |  | 2 | 3 |  | 2 | 5,5 (14); -7,-2 (8) |
| pigmy_pugoriss | 8 | 11 |  |  |  | 2 | 5,5 (13); 6,7 (2) |
| swamp_rat | 10 |  | 3 | 3 |  | 2 | 5,5 (5); 4,5 (3) |
| frightened_borgle | 8 | 6 |  |  |  | 2 | -5,-3 (4); 5,5 (4) |
| garyns_thief | 15 |  | 2 | 2 |  | 1 | -7,-2 (6) |
| kobola_thief | 9 | 1 | 1 | 2 |  | 2 | -4,-3 (4); 5,7 (2) |
| narmle_militia_grenadier | 11 |  | 1 | 1 |  | 1 | 5,3 (5) |
| gundark_desperado | 8 |  | 1 | 1 |  | 1 | -8,-3 (4) |
| nightspider_poison_spitter | 11 |  | 1 | 1 |  | 1 | -7,-2 (4) |
| kobola_miner | 8 | 1 |  | 1 |  | 1 | 6,5 (3) |
| gundark_raider | 9 | 1 |  | 1 |  | 1 | -7,-4 (2) |
| female_squall | 1-10 |  |  |  |  | 2 | -6,-3 (1); -7,-3 (1) |
| male_squall | 1 |  |  |  |  | 2 | -6,-3 (1); -7,-3 (1) |
| insane_miner | 9 |  | 1 |  |  | 1 | 6,6 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_borgal_young_lair_neutral_small | ? | 160 |  |  | 35 | -7,-3 (11); -7,-2 (9); 3,5 (8); 4,4 (8); 5,7 (8) |
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 150 |  |  | 32 | -7,-2 (11); -6,-4 (10); 6,5 (10); -7,-3 (9); 5,6 (9) |
| rori_capper_spineflap_hive_neutral_large | ? | 145 |  |  | 32 | 4,4 (10); -6,-4 (10); 5,4 (10); 6,5 (9); -5,-4 (9) |
| rori_nightspider_lair_neutral_small | ? | 78 |  |  | 29 | 4,6 (6); 6,5 (6); -7,-2 (5); -4,-2 (4); 4,7 (4) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 77 |  |  | 29 | -6,-4 (6); 3,6 (6); -7,-3 (5); -4,-3 (5); 6,5 (4) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 61 |  |  | 30 | -6,-4 (6); 3,5 (4); -5,-4 (4); 6,6 (4); -7,-4 (3) |
| rori_sickle_rasp_nest_neutral_medium | ? | 32 |  |  | 22 | 5,7 (3); -4,-2 (3); -4,-3 (2); 6,6 (2); 5,4 (2) |
| rori_kobola_miner_base_neutral_large_theater | ? | 8 |  |  | 8 | 3,4 (1); 3,5 (1); -6,-4 (1); 4,6 (1); 6,5 (1) |
| rori_gundark_raider_camp_neutral_medium_theater | ? | 7 |  |  | 7 | -7,-4 (1); -8,-3 (1); -4,-3 (1); -5,-4 (1); -7,-1 (1) |
| rori_narmle_camp_neutral_large_theater | ? | 3 |  |  | 3 | 5,3 (1); -4,-2 (1); -6,-2 (1) |

