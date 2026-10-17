# Talus: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:03 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 166 (0 explorers, 108 that killed something).
- Coverage: 27 of 256 squares of 1 km had a bot or a sighting in them (11%); explorers stood in 0.
- Templates: 13 creatures, 4 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 525 | 1 | 37 |  | 14 | 0,-3 (204); 4,5 (121); 0,-4 (85); 4,4 (51); -1,-3 (38) |
| fearful_fynock_youth | 5 | 276 | 3 | 126 |  | 18 | 1,-3 (47); 3,5 (46); 4,3 (39); -1,-3 (37); 1,-5 (34) |
| feared_fynock_youth | 7 | 379 |  | 1 |  | 8 | 0,-4 (136); 4,5 (115); 3,5 (63); 0,-3 (30); 4,4 (27) |
| putrid_decay_mite_hatchling | 7 | 110 |  |  |  | 6 | 0,-3 (65); 4,5 (26); 3,5 (11); 1,-4 (4); -1,-4 (3) |
| repugnant_dung_mite_crawler | 1-7 | 33 |  | 23 |  | 12 | 3,5 (8); 4,5 (8); -1,-4 (8); 0,-4 (4); 5,4 (4) |
| chunker_goon | 7 | 8 | 2 | 10 |  | 7 | 4,3 (6); 4,6 (5); -1,-5 (4); -2,-3 (4); 5,4 (2) |
| chunker_mooch | 7 | 1 | 2 | 3 |  | 2 | 1,-3 (8); -1,-4 (2) |
| sleemo_delinquent | 7 | 1 | 1 | 2 |  | 2 | 1,-5 (4); -1,-2 (2) |
| sleemo_hoodlum | 6 | 2 |  | 2 |  | 2 | -1,-2 (4); 1,-5 (2) |
| chunker_punk | 6 | 2 |  | 2 |  | 1 | 4,6 (4) |
| lost_aqualish_scout | 9 |  | 1 | 1 |  | 1 | 5,4 (4) |
| chunker_pest | 6 | 1 |  | 1 |  | 1 | 4,6 (2) |
| chunker_nitwit | 5 | 1 |  | 1 |  | 1 | 5,4 (2) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 26 | 44 |  | 14 | 4,3 (10); 1,-3 (9); 1,-5 (8); -1,-3 (7); 0,-5 (6) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 9 | 10 |  | 7 | 5,4 (4); 1,-4 (4); 1,-2 (3); 4,3 (2); -1,-5 (2) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 5 | 6 |  | 5 | 1,-3 (3); 4,6 (3); 5,4 (2); -2,-3 (2); -1,-5 (1) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 2 | 2 |  | 2 | -1,-2 (2); 1,-5 (2) |

