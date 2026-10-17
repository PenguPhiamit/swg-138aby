# Rori: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:26 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 294 (0 explorers, 103 that killed something).
- Coverage: 38 of 256 squares of 1 km had a bot or a sighting in them (15%); explorers stood in 0.
- Templates: 27 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| capper_spineflap | 1-6 | 137 | 9 | 32 |  | 16 | -6,-3 (60); 5,6 (41); 4,4 (22); -7,-3 (20); -6,-2 (19) |
| ikopi | 1-7 | 144 | 6 | 10 |  | 15 | 5,5 (60); -6,-3 (43); 4,6 (24); -5,-3 (21); -7,-4 (11) |
| nightspider | 7 | 70 | 11 | 11 |  | 19 | -6,-3 (28); 4,5 (26); -5,-2 (18); -5,-3 (17); 4,6 (8) |
| capper_spineflap_drone | 1-6 | 52 | 1 |  |  | 11 | -6,-2 (30); -5,-3 (22); -7,-4 (4); 4,5 (3); -5,-4 (3) |
| young_borgle_gruntling | 6 | 39 | 4 | 2 |  | 10 | -6,-2 (25); 5,6 (9); -7,-2 (8); -6,-3 (6); -5,-2 (6) |
| meek_avenging_squall | 6 | 37 | 3 |  |  | 13 | -6,-3 (16); 5,5 (16); -6,-2 (5); 4,5 (4); -7,-3 (4) |
| young_borgle | 6 | 14 | 6 | 17 |  | 10 | 4,4 (16); -8,-2 (9); -5,-4 (9); -6,-1 (5); -8,-3 (4) |
| frail_squall | 6 | 25 | 1 |  |  | 6 | 5,5 (21); -6,-3 (13); 4,5 (2); -7,-2 (2); 6,6 (2) |
| gundark_crook | 5 | 7 | 2 | 8 |  | 6 | 3,6 (10); 7,5 (4); 6,5 (4); 5,4 (2); -7,-3 (2) |
| swamp_rat | 10 | 1 | 9 | 9 |  | 2 | 5,5 (15); 4,5 (7) |
| pigmy_pugoriss | 8 | 20 |  |  |  | 1 | 5,5 (20) |
| gundark_hooligan | 6 | 5 | 2 | 7 |  | 4 | -7,-3 (6); -6,-2 (5); -7,-4 (5); 6,5 (4) |
| gundark_rogue | 7 | 3 | 3 | 6 |  | 4 | -6,-2 (7); -5,-4 (5); -6,-5 (5); -7,-3 (3) |
| first_brigade_scout | 7 | 3 | 2 | 5 |  | 4 | -5,-3 (7); 5,5 (4); -7,-3 (4); -6,-1 (4) |
| sickle_rasp | 8 | 2 | 2 | 4 |  | 2 | -7,-3 (12); -6,-4 (3) |
| garyns_prowler | 11 |  | 2 | 3 |  | 2 | 5,5 (12); -6,-2 (1) |
| gundark_desperado | 8 | 3 | 1 | 4 |  | 2 | -6,-4 (6); -5,-2 (4) |
| scorched_krevol | 8 | 2 | 1 | 1 |  | 2 | -6,-2 (5); 5,5 (3) |
| vicious_squall | 12 |  | 2 | 2 |  | 2 | -6,-3 (4); -6,-2 (3) |
| kobola_thief | 9 |  | 1 | 1 |  | 1 | 4,4 (5) |
| first_brigade_trooper | 6 | 1 |  | 1 |  | 2 | -7,-4 (3); -7,-3 (2) |
| vrobalet | 8 |  | 1 |  |  | 2 | -6,-3 (3); -6,-2 (2) |
| frightened_borgle | 8 | 2 | 1 |  |  | 2 | 5,5 (2); -5,-3 (1) |
| hermit_spider | 7 | 3 |  |  |  | 1 | -5,-3 (3) |
| timid_vir_vur | 8 | 2 |  |  |  | 1 | 5,5 (2) |
| garyns_thief | 15 |  | 1 |  |  | 1 | -6,-2 (2) |
| chuba | 5 |  |  |  |  | 1 | -5,-2 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 26 | 63 |  | 19 | 4,5 (16); -6,-2 (15); -7,-4 (9); -7,-3 (7); -7,-2 (5) |
| rori_borgal_young_lair_neutral_small | ? | 17 | 62 |  | 12 | -6,-1 (21); -7,-4 (15); -6,-4 (9); -6,-2 (8); 4,4 (6) |
| rori_capper_spineflap_hive_neutral_large | ? | 20 | 36 |  | 11 | 4,4 (12); -7,-3 (8); -7,-2 (7); 5,4 (6); 6,4 (6) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 15 | 27 |  | 14 | 4,4 (6); 4,6 (5); 5,4 (3); -7,-1 (3); -4,-3 (3) |
| rori_nightspider_lair_neutral_small | ? | 14 | 27 |  | 12 | -6,-1 (8); -5,-2 (5); -5,-1 (5); -7,-3 (3); -4,-3 (3) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 12 | 25 |  | 11 | -5,-3 (7); 5,5 (4); -6,-2 (4); -7,-3 (3); -7,-4 (3) |
| rori_sickle_rasp_nest_neutral_medium | ? | 6 | 12 |  | 6 | -7,-3 (4); -6,-4 (3); 4,4 (3); 5,6 (3); 4,6 (3) |
| rori_gundark_raider_camp_neutral_medium_theater | ? | 4 | 11 |  | 4 | -6,-4 (7); -5,-2 (3); -7,-3 (3); -5,-4 (2) |
| rori_kobola_miner_base_neutral_large_theater | ? | 1 | 2 |  | 1 | 4,4 (3) |

