# Rori: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:33 PM to 12:31 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `rori.csv`.

- Bots here: 268 (0 explorers, 96 that killed something).
- Coverage: 37 of 256 squares of 1 km had a bot or a sighting in them (14%); explorers stood in 0.
- Templates: 23 creatures, 8 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 rori` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ikopi | 1-7 | 151 | 4 | 3 |  | 18 | 5,5 (74); -6,-3 (55); 6,5 (12); -5,-3 (11); 4,6 (7) |
| capper_spineflap | 1-6 | 75 | 7 | 46 |  | 21 | -6,-2 (27); 4,6 (26); -7,-4 (19); -5,-3 (16); 5,6 (14) |
| nightspider | 7 | 68 | 8 | 12 |  | 16 | -6,-3 (17); 4,5 (15); -5,-3 (12); 5,5 (11); -6,-4 (10) |
| capper_spineflap_drone | 1-6 | 72 |  |  |  | 14 | -6,-3 (27); -6,-2 (18); -5,-2 (11); 4,6 (6); -5,-3 (5) |
| meek_avenging_squall | 6 | 60 | 2 |  |  | 11 | -6,-2 (29); -6,-3 (13); 5,6 (13); 5,5 (8); -4,-3 (6) |
| frail_squall | 6 | 43 | 1 |  |  | 8 | 5,5 (48); -6,-3 (8); 6,4 (6); 6,6 (4); -6,-4 (4) |
| young_borgle | 6 | 26 | 6 | 17 |  | 11 | -4,-3 (19); 5,6 (10); -6,-4 (9); -8,-3 (9); 6,6 (8) |
| hermit_spider | 1-7 | 56 | 1 |  |  | 10 | -6,-3 (30); 6,5 (16); -6,-2 (7); 5,5 (5); 4,5 (4) |
| gundark_crook | 5 | 11 | 2 | 12 |  | 7 | -5,-1 (9); -5,-3 (7); 5,5 (4); 3,6 (4); 6,5 (2) |
| garyns_prowler | 11 |  | 6 | 5 |  | 3 | -6,-2 (13); 5,5 (10); -7,-2 (3) |
| gundark_hooligan | 6 | 8 |  | 8 |  | 7 | -7,-3 (7); -6,-1 (4); -5,-3 (3); -5,-1 (2); 5,7 (2) |
| gundark_rogue | 7 | 4 | 2 | 6 |  | 5 | -6,-1 (5); -7,-3 (5); -7,-1 (3); -5,-1 (2); 3,6 (2) |
| sickle_rasp | 8 |  | 3 | 2 |  | 4 | 6,5 (9); 4,7 (1); 3,7 (1); 4,6 (1) |
| swamp_rat | 10 |  | 5 | 4 |  | 2 | 5,5 (7); 4,5 (3) |
| scorched_krevol | 8 | 4 | 2 |  |  | 2 | -6,-2 (7); 5,5 (2) |
| narmle_militia_grenadier | 11 |  | 2 | 2 |  | 2 | 5,7 (4); 5,6 (4) |
| timid_vir_vur | 8 | 7 |  |  |  | 1 | 5,5 (7) |
| first_brigade_trooper | 6 | 1 | 2 | 2 |  | 2 | 3,5 (6); 4,5 (1) |
| frightened_borgle | 8 | 3 |  |  |  | 4 | -5,-3 (2); -7,-2 (2); 5,5 (1); -6,-2 (1) |
| young_borgle_gruntling | 6 | 1 | 1 |  |  | 1 | -5,-2 (4) |
| narmle_militia_lieutenant | 9 |  | 1 | 1 |  | 2 | 5,7 (3); 5,6 (1) |
| first_brigade_scout | 7 | 1 |  | 1 |  | 1 | 5,3 (3) |
| vrobalet | 8 |  | 1 |  |  | 1 | 4,5 (3) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| rori_capper_spineflap_hive_neutral_large | ? | 30 | 54 |  | 19 | -6,-1 (9); -6,-2 (8); -7,-2 (8); 4,6 (7); 3,5 (7) |
| rori_gundark_hooligan_camp_neutral_medium_theater | ? | 22 | 47 |  | 17 | -7,-3 (8); -5,-1 (7); 6,4 (6); -6,-4 (6); 3,6 (5) |
| rori_borgal_young_lair_neutral_small | ? | 21 | 41 |  | 15 | -4,-3 (11); 5,6 (6); -7,-2 (6); -7,-4 (6); 3,5 (4) |
| rori_nightspider_lair_neutral_small | ? | 14 | 37 |  | 12 | 3,4 (16); 5,7 (5); -6,-1 (5); -7,-2 (3); 4,5 (3) |
| rori_ikopi_lair_neutral_medium_boss_01 | ? | 11 | 20 |  | 7 | 6,6 (6); 6,5 (6); -7,-3 (6); 4,6 (5); 6,4 (3) |
| rori_brigade_scout_camp_neutral_medium_theater | ? | 8 | 15 |  | 9 | 6,4 (4); -5,-4 (4); 6,5 (3); 3,5 (3); 4,6 (2) |
| rori_sickle_rasp_nest_neutral_medium | ? | 5 | 10 |  | 6 | 6,5 (4); -6,-4 (3); -4,-3 (3); -7,-2 (3); 4,7 (1) |
| rori_narmle_camp_neutral_large_theater | ? | 1 | 3 |  | 2 | 5,6 (3); 5,7 (1) |

