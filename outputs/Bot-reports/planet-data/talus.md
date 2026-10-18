# Talus: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:05 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 70 (0 explorers, 37 that killed something).
- Coverage: 31 of 256 squares of 1 km had a bot or a sighting in them (12%); explorers stood in 0.
- Templates: 17 creatures, 4 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 276 | 3 | 90 |  | 14 | 4,5 (72); 3,5 (50); 0,-3 (47); -1,-3 (39); 0,-5 (28) |
| fearful_fynock_youth | 5 | 193 | 2 | 106 |  | 21 | 0,-5 (34); -1,-5 (32); -1,-4 (30); 0,-4 (26); 2,-3 (26) |
| repugnant_dung_mite_crawler | 1-7 | 65 | 3 | 52 |  | 14 | 0,-5 (19); 0,-4 (16); 4,5 (15); 0,-3 (11); 3,4 (11) |
| feared_fynock_youth | 7 | 117 |  |  |  | 9 | 0,-4 (56); 0,-3 (16); 4,4 (16); 4,5 (15); 3,5 (10) |
| chunker_goon | 7 | 7 | 10 | 16 |  | 7 | 1,-4 (16); -1,-3 (12); 0,-2 (12); -1,-4 (5); 4,6 (4) |
| putrid_decay_mite_hatchling | 7 | 41 |  |  |  | 5 | 0,-3 (16); 0,-4 (13); 4,5 (5); 4,4 (5); 1,-4 (3) |
| sleemo_delinquent | 7 | 9 | 4 | 14 |  | 5 | 1,-3 (15); 5,6 (12); -1,-2 (6); 3,6 (4); 0,-5 (2) |
| chunker_pest | 6 | 12 | 2 | 14 |  | 7 | 2,-4 (8); 1,-2 (6); 5,5 (6); -1,-3 (4); 5,3 (4) |
| chunker_nitwit | 5 | 9 | 1 | 10 |  | 5 | -1,-3 (8); -1,-4 (6); 1,-2 (4); 5,5 (2); 2,-4 (2) |
| sleemo_punk | 6 | 9 |  | 10 |  | 5 | 1,-3 (6); 3,6 (6); 0,-5 (4); -1,-2 (4); 5,6 (2) |
| chunker_punk | 6 | 5 | 1 | 6 |  | 4 | 1,-2 (8); 4,6 (4); 3,3 (3); 0,-2 (2) |
| chunker_mooch | 7 | 5 | 2 | 7 |  | 6 | 5,3 (6); 1,-2 (2); 3,3 (2); 1,-5 (2); -1,-4 (2) |
| acicular_defender | 1-8 | 4 | 2 | 6 |  | 5 | -1,-4 (6); 4,3 (4); 3,5 (2); -1,-3 (2); 3,6 (2) |
| song_rasp | 10 | 7 | 1 | 3 |  | 1 | 4,5 (12) |
| sleemo_hoodlum | 6 | 4 |  | 4 |  | 3 | 1,-3 (5); 5,6 (2); -1,-2 (2) |
| docile_kahmurra | 10 | 2 |  |  |  | 1 | 0,-4 (2) |
| clipped_fynock | 9 | 1 |  |  |  | 1 | 4,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 18 | 43 |  | 11 | -1,-5 (9); 2,-3 (7); 0,-5 (7); 5,5 (7); 4,6 (6) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 16 | 41 |  | 11 | -1,-3 (12); 1,-2 (10); 5,5 (7); 0,-2 (6); -1,-4 (5) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 14 | 32 |  | 10 | 3,5 (9); 0,-5 (8); -1,-3 (7); 4,3 (4); 3,6 (4) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 6 | 21 |  | 5 | 1,-3 (11); 3,6 (5); 0,-5 (4); -1,-2 (4); 5,6 (3) |

