# Talus: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:26 AM to 3:08 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 85 (0 explorers, 51 that killed something).
- Coverage: 26 of 256 squares of 1 km had a bot or a sighting in them (10%); explorers stood in 0.
- Templates: 13 creatures, 4 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 197 |  | 27 |  | 10 | 0,-3 (63); 4,5 (51); 0,-4 (43); 3,4 (19); 4,4 (13) |
| fearful_fynock_youth | 5 | 117 | 1 | 41 |  | 15 | 4,5 (29); 3,5 (22); 3,6 (19); -1,-4 (18); 1,-5 (18) |
| repugnant_dung_mite_crawler | 7 | 29 |  | 12 |  | 7 | 0,-4 (13); 3,5 (7); 0,-3 (5); 4,4 (5); 0,-5 (4) |
| putrid_decay_mite_hatchling | 7 | 31 |  |  |  | 5 | 4,4 (13); -1,-4 (8); 4,5 (5); -1,-3 (4); 3,4 (1) |
| feared_fynock_youth | 7 | 27 |  |  |  | 5 | 0,-4 (9); 4,5 (8); 0,-3 (7); 4,4 (2); -1,-4 (1) |
| chunker_nitwit | 5 | 7 |  | 7 |  | 5 | 3,5 (4); 4,6 (4); -1,-5 (2); 0,-5 (2); 3,4 (2) |
| sleemo_delinquent | 7 | 3 | 2 | 5 |  | 2 | 0,-2 (10); 1,-3 (4) |
| chunker_mooch | 7 |  | 2 | 2 |  | 1 | 2,5 (8) |
| chunker_punk | 6 | 3 |  | 3 |  | 2 | 3,4 (4); -1,-5 (2) |
| sleemo_punk | 6 | 3 |  | 3 |  | 2 | 1,-3 (4); 0,-2 (2) |
| sleemo_hoodlum | 6 | 2 |  | 3 |  | 2 | 0,-2 (4); 3,3 (1) |
| chunker_goon | 7 | 2 |  | 2 |  | 2 | -1,-5 (2); 4,6 (2) |
| acicular_defender | 8 |  | 1 | 1 |  | 1 | 3,4 (4) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_chunker_goon_camp_neutral_small_theater | ? | 5 | 16 |  | 5 | 4,6 (7); 3,5 (6); -1,-5 (3); 3,4 (3); 2,5 (2) |
| talus_fynock_youth_lair_neutral_small | ? | 7 | 12 |  | 7 | 3,6 (4); -1,-4 (3); 1,-5 (3); 1,-3 (3); 5,6 (2) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 4 | 12 |  | 3 | 0,-2 (12); 1,-3 (2); 3,3 (2) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 5 | 10 |  | 6 | 3,4 (4); -2,-3 (3); 5,4 (3); -1,-5 (2); -1,-2 (2) |

