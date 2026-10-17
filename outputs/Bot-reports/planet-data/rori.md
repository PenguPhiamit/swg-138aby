# Rori: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:26 AM to 3:08 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 90 (0 explorers, 45 that killed something).
- Coverage: 22 of 256 squares of 1 km had a bot or a sighting in them (9%); explorers stood in 0.
- Templates: 19 creatures, 6 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| capper_spineflap | 1-6 | 63 | 4 | 41 |  | 8 | -5,-4 (27); -7,-3 (21); -6,-3 (20); -6,-4 (20); 5,6 (11) |
| nightspider | 7 | 44 | 3 | 3 |  | 6 | 4,5 (25); -6,-3 (20); -5,-3 (16); -6,-4 (9); 5,5 (3) |
| young_borgle | 6 | 17 | 7 | 24 |  | 8 | 3,5 (13); 6,5 (13); 5,7 (12); 4,7 (12); -6,-4 (7) |
| ikopi | 1-7 | 39 | 4 | 5 |  | 7 | 5,5 (22); -6,-2 (17); 5,6 (6); -6,-3 (4); -5,-3 (3) |
| young_borgle_gruntling | 6 | 25 | 3 | 9 |  | 3 | -6,-3 (21); -6,-2 (15); -4,-3 (6) |
| gundark_rogue | 7 | 6 | 5 | 11 |  | 6 | -5,-3 (11); 7,5 (7); 5,4 (6); 4,7 (6); -6,-4 (2) |
| frail_squall | 6 | 29 |  |  |  | 2 | 5,5 (16); -6,-3 (13) |
| swamp_rat | 10 | 3 | 8 | 11 |  | 2 | 5,5 (15); 4,5 (9) |
| garyns_prowler | 11 |  | 6 | 6 |  | 1 | 5,5 (22) |
| gundark_crook | 5 | 2 | 3 | 5 |  | 3 | 4,4 (12); -6,-4 (3); 5,4 (2) |
| gundark_hooligan | 6 | 2 | 2 | 4 |  | 2 | 5,4 (8); 4,4 (5) |
| first_brigade_trooper | 6 | 6 |  | 6 |  | 2 | -6,-5 (6); 6,4 (6) |
| vrobalet | 8 | 1 | 2 |  |  | 2 | 5,5 (4); -6,-3 (3) |
| capper_spineflap_drone | 6 | 4 |  | 2 |  | 2 | 4,6 (3); -6,-4 (3) |
| timid_vir_vur | 8 | 5 |  |  |  | 1 | -6,-3 (5) |
| meek_avenging_squall | 6 | 4 |  |  |  | 1 | -6,-2 (4) |
| first_brigade_scout | 7 | 2 |  | 2 |  | 1 | 6,4 (4) |
| scorched_krevol | 8 |  | 1 |  |  | 1 | -6,-2 (2) |
| hermit_spider | 1 | 1 |  |  |  | 1 | 5,4 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_borgal_young_lair_neutral_small | ? | 8 | 14 |  | 9 | 6,5 (4); -6,-4 (3); 4,7 (3); 4,5 (3); 5,7 (2) |
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 7 | 14 |  | 6 | 4,4 (6); -5,-3 (4); 5,4 (4); 7,5 (3); -6,-4 (2) |
| rori_capper_spineflap_hive_neutral_large | ? | 5 | 13 |  | 4 | -6,-4 (6); -5,-4 (6); -7,-3 (4); -4,-3 (2) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 2 | 6 |  | 2 | -6,-5 (4); 6,4 (4) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 1 | 4 |  | 1 | -6,-2 (5) |
| rori_nightspider_lair_neutral_small | ? | 1 | 2 |  | 1 | -6,-4 (3) |

