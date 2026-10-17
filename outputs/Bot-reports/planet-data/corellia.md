# Corellia: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:25 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `corellia.csv`.

- Bots here: 925 (0 explorers, 205 that killed something).
- Coverage: 72 of 256 squares of 1 km had a bot or a sighting in them (28%); explorers stood in 0.
- Templates: 36 creatures, 22 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 corellia` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| durni | 1-7 | 276 | 9 | 35 |  | 41 | -4,3 (104); 6,-7 (54); 3,5 (50); 6,-6 (23); 6,-5 (16) |
| corellian_butterfly_drone | 5 | 299 | 7 |  |  | 30 | -4,2 (74); 0,-5 (40); -4,3 (38); 6,-6 (27); 6,-7 (27) |
| gubbur | 1-6 | 170 | 9 | 74 |  | 40 | 3,5 (46); -4,4 (29); 6,-5 (25); -5,-3 (19); 2,5 (18) |
| paralope | 1-6 | 197 | 12 | 72 |  | 25 | -4,3 (74); 0,-6 (48); 3,6 (33); -4,2 (31); 1,-6 (18) |
| minor_gubbur | 4 | 151 | 2 |  |  | 23 | -4,2 (61); -4,3 (51); 7,-6 (16); 6,-6 (12); 6,-5 (10) |
| howling_plumed_rasp | 4 | 91 | 3 | 62 |  | 21 | 2,4 (25); 0,-6 (20); -1,-6 (18); -5,-3 (18); 7,-5 (13) |
| plumed_rasp | 7 | 51 | 6 | 48 |  | 14 | 6,-5 (25); 1,-5 (17); 2,4 (14); -3,3 (14); 1,5 (14) |
| vrelt | 6 | 79 |  |  |  | 10 | -4,3 (44); -4,2 (23); 0,-4 (8); -3,4 (2); -4,4 (2) |
| giant_gubbur | 9 | 8 | 13 | 22 |  | 13 | 6,-5 (15); -6,3 (8); 6,-7 (7); -3,4 (5); 0,-4 (5) |
| corellian_butterfly | 1-7 | 48 | 1 |  |  | 17 | 3,6 (14); 6,-7 (8); 3,4 (6); -4,2 (5); 7,-7 (4) |
| diseased_vrelt | 1-8 | 4 | 10 | 11 |  | 10 | -5,2 (14); 6,-5 (13); -1,-4 (12); 0,-5 (10); 0,-4 (3) |
| meatlump_fool | 6 | 17 | 3 | 20 |  | 12 | 3,6 (10); 6,-7 (8); 5,-6 (7); 7,-4 (6); -3,3 (5) |
| rogue_corsec_trooper | 7 | 32 | 2 | 1 |  | 3 | -4,3 (40); -6,-3 (3); -5,-3 (3) |
| scavenger_rat | 8 | 14 | 4 | 7 |  | 13 | -3,3 (10); -2,-6 (7); 4,5 (4); 7,-4 (4); 6,-6 (4) |
| bloated_gubbur | 6 | 32 |  |  |  | 9 | 3,4 (11); 0,-6 (8); 7,-6 (6); -5,-3 (5); 3,5 (3) |
| vynock | 1-9 | 6 | 8 | 9 |  | 8 | 3,6 (16); 7,-7 (14); 6,-5 (4); 5,-6 (1); 6,-6 (1) |
| rogue_bageraset | 13 |  | 15 | 14 |  | 6 | -4,2 (14); 6,-5 (6); -5,2 (5); 6,-8 (5); 2,7 (4) |
| meatlump_buffoon | 5 | 9 | 2 | 11 |  | 9 | 6,-5 (6); 6,-4 (5); 2,5 (4); 5,-5 (4); 6,-7 (3) |
| meatlump_stooge | 7 | 7 | 3 | 10 |  | 7 | 6,-5 (9); 7,-4 (6); 5,-7 (4); 3,6 (2); 4,-7 (2) |
| dalyrake | 1-9 | 4 | 4 | 4 |  | 4 | 6,-5 (13); -4,3 (4); 5,-6 (3); -3,3 (3) |
| carrion_spat | 10 |  | 5 | 5 |  | 2 | 5,-6 (16); 5,-4 (5) |
| drall_sentry | 8 |  | 3 | 3 |  | 1 | 7,-5 (12) |
| slice_hound | 9 |  | 3 | 2 |  | 3 | -3,2 (6); 1,6 (4); -4,2 (1) |
| female_slice_hound | 1-8 | 1 | 2 | 2 |  | 3 | -3,2 (4); 1,6 (4); 6,-7 (1) |
| krahbu | 10 |  | 2 | 2 |  | 1 | 5,-5 (8) |
| humbaba | 1 | 1 | 1 |  |  | 4 | -5,-3 (3); 5,-6 (1); -7,-3 (1); -6,-3 (1) |
| giant_carrion_spat | 18 |  | 2 | 2 |  | 1 | 2,5 (6) |
| murra | 10 |  | 1 | 1 |  | 1 | 7,-4 (4) |
| swooper_corellia | 8 |  | 1 | 1 |  | 1 | 5,-7 (4) |
| tabage | 11 |  | 1 | 1 |  | 1 | 0,-4 (4) |
| kreetle | 3 |  |  |  |  | 1 | 7,-5 (3) |
| crazed_durni | 1 | 2 |  |  |  | 1 | 1,5 (2) |
| hermit_spider | 7 |  |  |  |  | 1 | 5,-6 (2) |
| gnort | 4 |  |  |  |  | 1 | 6,-5 (2) |
| gorg | 6 |  |  |  |  | 1 | 6,-5 (2) |
| nightspider | 7 |  |  |  |  | 1 | 5,-5 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| corellia_gubbur_lair_neutral_small | ? | 52 | 98 |  | 30 | 6,-5 (17); 5,-6 (12); 4,5 (11); 5,-5 (10); 1,6 (9) |
| corellia_paralope_lair_neutral_medium | ? | 43 | 81 |  | 27 | 3,6 (12); 6,-7 (11); -3,2 (9); 0,-6 (9); 5,-6 (7) |
| corellia_meatlump_camp_neutral_medium_theater | ? | 39 | 83 |  | 29 | 3,6 (14); -5,3 (12); 6,-5 (9); -1,-3 (7); 5,-7 (6) |
| corellia_plumed_rasp_nest_neutral_small | ? | 32 | 70 |  | 21 | 6,-5 (14); 2,4 (11); 1,-5 (10); 5,-7 (8); 2,6 (7) |
| corellia_durni_warren_neutral_small_boss_01 | ? | 23 | 44 |  | 21 | -3,2 (6); 4,5 (6); -3,4 (6); 6,-5 (5); 1,6 (5) |
| corellia_scavenger_rat_lair_neutral_small | ? | 13 | 23 |  | 13 | 4,5 (5); -3,3 (4); -1,-6 (4); -3,4 (3); -2,3 (3) |
| corellia_diseased_vrelt_lair_neutral_boss_02 | ? | 12 | 19 |  | 11 | -1,-4 (7); 7,-5 (3); -5,2 (3); 2,6 (3); 5,-5 (3) |
| corellia_dalyrake_lair_neutral_medium | ? | 6 | 13 |  | 4 | 6,-5 (11); 5,-6 (3); -3,4 (3); 5,4 (2) |
| corellia_vynock_lair_neutral_small | ? | 5 | 12 |  | 5 | 7,-7 (5); 3,6 (5); 0,-6 (3); 1,-4 (2); 6,-5 (2) |
| corellia_greck_base_neutral_large_theater | ? | 1 | 14 |  | 1 | -4,1 (15) |
| corellia_slice_hound_lair_neutral_medium | ? | 4 | 9 |  | 4 | -3,2 (4); 7,-7 (3); 1,6 (3); 6,-7 (3) |
| corellia_giant_gubbur_lair_neutral_medium | ? | 4 | 6 |  | 4 | 6,-8 (3); 7,-4 (3); -6,3 (2); -3,2 (2) |
| corellia_meatlump_outpost_neutral_medium_theater | ? | 3 | 6 |  | 3 | -1,-6 (4); 6,-5 (3); 1,4 (2) |
| corellia_carrion_spat_lair_neutral_medium_boss_01 | ? | 2 | 6 |  | 2 | 5,-6 (5); 5,-4 (3) |
| corellia_murra_lair_neutral_medium | ? | 2 | 4 |  | 2 | 7,-4 (3); -2,3 (3) |
| corellia_corellian_butterfly_pod_neutral_small | ? | 2 | 3 |  | 2 | 5,-5 (3); -6,-1 (2) |
| corellia_drall_patriot_camp_neutral_medium_theater | ? | 1 | 3 |  | 1 | 7,-5 (4) |
| corellia_gurrcat_lair_neutral_medium | ? | 1 | 2 |  | 1 | 1,-4 (3) |
| corellia_canoid_lair_neutral_medium | ? | 1 | 2 |  | 1 | -6,3 (3) |
| corellia_lord_nyax_chapel_neutral_medium_theater | ? | 1 | 2 |  | 1 | -4,-2 (3) |
| corellia_krahbu_lair_neutral_medium | ? | 1 | 2 |  | 1 | 5,-5 (3) |
| corellia_swooper_camp_neutral_small_theater | ? | 1 | 1 |  | 1 | 5,-7 (2) |

