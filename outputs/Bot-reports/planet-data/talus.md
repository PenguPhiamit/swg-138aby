# Talus: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:26 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 324 (0 explorers, 108 that killed something).
- Coverage: 40 of 256 squares of 1 km had a bot or a sighting in them (16%); explorers stood in 0.
- Templates: 24 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 262 | 9 | 63 |  | 24 | 4,4 (54); 4,5 (48); -1,-3 (42); 0,-3 (40); -1,-4 (28) |
| fearful_fynock_youth | 5 | 232 | 5 | 116 |  | 28 | 5,4 (39); 4,5 (34); -1,-3 (31); 0,-2 (26); 1,-2 (26) |
| feared_fynock_youth | 7 | 148 | 2 |  |  | 22 | 0,-3 (47); 4,5 (40); 0,-4 (29); 3,5 (25); 4,4 (8) |
| putrid_decay_mite_hatchling | 7 | 105 |  |  |  | 12 | 0,-4 (70); 4,5 (24); 0,-3 (6); 1,-4 (4); 3,5 (3) |
| repugnant_dung_mite_crawler | 7 | 41 | 3 | 28 |  | 13 | 1,-4 (12); 1,-3 (11); 4,5 (9); 3,4 (9); 0,-3 (8) |
| chunker_pest | 6 | 4 | 1 | 5 |  | 5 | 1,-4 (4); 5,4 (3); 0,-5 (3); -1,-2 (2); 0,-4 (1) |
| decay_mite | 1-9 | 2 | 2 | 2 |  | 2 | -1,-4 (9); 4,5 (2) |
| chunker_mooch | 7 | 2 | 1 | 3 |  | 3 | 3,5 (4); 5,5 (3); 0,-5 (2) |
| talus_liberation_party_volunteer | 8 | 2 | 1 | 3 |  | 1 | -1,-3 (9) |
| sleemo_punk | 6 | 2 |  | 2 |  | 3 | -1,-4 (3); 4,6 (3); -1,-3 (1) |
| sleemo_scamp | 8 | 1 | 1 | 2 |  | 1 | 0,-5 (6) |
| flail_enforcer | 19 |  | 2 | 1 |  | 1 | 3,6 (6) |
| chunker_punk | 6 | 2 |  | 2 |  | 2 | 0,-5 (3); 3,5 (2) |
| black_sun_initiate | 17 |  | 2 | 2 |  | 1 | 5,5 (4) |
| chunker_nitwit | 5 | 2 |  | 2 |  | 2 | -1,-2 (2); 3,5 (2) |
| dalyrake | 9 |  | 1 | 1 |  | 1 | 6,5 (4) |
| sleemo_hoodlum | 6 | 2 |  | 2 |  | 2 | 2,-3 (2); 4,6 (2) |
| sleemo_delinquent | 7 | 1 |  | 1 |  | 1 | 2,-3 (4) |
| puss_covered_decay_mite_soldier | 15 |  | 1 | 1 |  | 1 | 5,5 (3) |
| flite_rasp | 8 |  | 1 |  |  | 1 | 1,-5 (3) |
| minor_guf_drolg | 1 | 1 |  |  |  | 1 | 5,5 (3) |
| chunker_goon | 7 | 1 |  | 1 |  | 1 | 3,5 (2) |
| sleemo_vandal | 9 |  |  |  |  | 1 | 0,-5 (1) |
| vynock | 1 | 1 |  |  |  | 1 | 0,-4 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 43 | 75 |  | 24 | 5,4 (20); 0,-2 (12); 3,4 (8); 4,6 (7); -1,-5 (7) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 32 | 65 |  | 22 | -1,-3 (11); 2,-4 (10); 3,5 (8); 5,6 (7); 3,4 (6) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 23 | 49 |  | 17 | 0,-4 (9); 0,-5 (7); 1,-5 (7); 3,5 (6); -1,-4 (6) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 8 | 17 |  | 9 | -1,-4 (4); 4,6 (4); 1,-5 (3); 0,-2 (3); 5,4 (3) |
| talus_sleemo_vandal_camp_neutral_medium_theater | ? | 3 | 5 |  | 3 | 0,-5 (4); 5,5 (2); 6,5 (2) |
| talus_decay_mite_lair_neutral_boss_01 | ? | 2 | 5 |  | 2 | -1,-4 (4); 2,4 (3) |
| talus_dalyrake_nest_neutral_medium | ? | 2 | 4 |  | 3 | 5,6 (3); 6,5 (2); 5,5 (1) |
| talus_vynock_lair_neutral_medium | ? | 2 | 4 |  | 1 | 0,-5 (6) |
| talus_liberation_loyalist_camp_neutral_medium_theater | ? | 2 | 4 |  | 2 | -1,-3 (4); 5,3 (2) |

