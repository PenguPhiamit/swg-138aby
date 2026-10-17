# Talus: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:34 AM to 1:01 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 177 (0 explorers, 106 that killed something).
- Coverage: 37 of 256 squares of 1 km had a bot or a sighting in them (14%); explorers stood in 0.
- Templates: 24 creatures, 9 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| fearful_fynock_youth | 5 | 372 | 7 | 255 |  | 26 | 0,-5 (97); 3,4 (59); 3,3 (47); 1,-4 (44); 4,3 (36) |
| paralope | 1-6 | 376 | 19 | 102 |  | 18 | 0,-3 (131); 0,-4 (63); 4,5 (56); 3,5 (47); -1,-2 (47) |
| chunker_mooch | 7 | 17 | 12 | 30 |  | 10 | 5,6 (19); 3,6 (14); 4,6 (9); 0,-5 (8); 1,-4 (8) |
| repugnant_dung_mite_crawler | 1-7 | 56 |  | 22 |  | 11 | 4,5 (28); 0,-3 (11); -1,-3 (9); 0,-4 (8); 4,4 (4) |
| chunker_goon | 7 | 22 | 6 | 29 |  | 14 | -1,-3 (18); 1,-5 (11); 3,6 (10); 5,3 (9); 3,3 (4) |
| chunker_pest | 6 | 19 | 2 | 21 |  | 10 | 5,5 (8); 3,4 (8); 1,-5 (7); 3,6 (7); -1,-5 (6) |
| feared_fynock_youth | 7 | 45 |  |  |  | 9 | 4,5 (17); 0,-3 (9); -1,-4 (6); 0,-4 (5); 1,-3 (3) |
| sleemo_punk | 6 | 16 |  | 18 |  | 10 | 1,-5 (8); 4,3 (6); 3,4 (5); 3,5 (5); -2,-4 (4) |
| dalyrake | 9 | 1 | 8 | 9 |  | 4 | 0,-5 (15); 2,-4 (10); 1,-4 (8); 0,-4 (1) |
| putrid_decay_mite_hatchling | 7 | 29 |  |  |  | 6 | -1,-3 (17); -1,-2 (5); 0,-3 (3); -1,-4 (3); 3,5 (2) |
| sleemo_delinquent | 7 | 10 | 2 | 12 |  | 8 | 6,4 (7); 1,-4 (6); 3,4 (4); 2,6 (4); 4,3 (2) |
| sleemo_scamp | 8 | 2 | 6 | 8 |  | 2 | 1,-4 (16); 3,6 (12) |
| chunker_nitwit | 5 | 12 |  | 12 |  | 7 | 3,3 (6); -1,-3 (6); 5,6 (5); 3,5 (2); -1,-2 (2) |
| vynock | 9 |  | 5 | 5 |  | 3 | 5,6 (8); 2,-2 (8); 5,5 (4) |
| chunker_punk | 6 | 8 | 1 | 9 |  | 5 | 3,4 (7); 3,3 (4); 1,-5 (4); 5,6 (2); 3,5 (2) |
| talus_liberation_party_loyalist | 9 |  | 4 | 5 |  | 3 | 1,-3 (8); 5,6 (8); 4,6 (1) |
| sleemo_vandal | 9 |  | 4 | 4 |  | 1 | 3,6 (16) |
| talus_liberation_party_volunteer | 8 |  | 4 | 4 |  | 2 | 1,-5 (12); 1,-3 (4) |
| decay_mite | 9 |  | 4 | 4 |  | 2 | 4,6 (8); 1,-3 (8) |
| sleemo_hoodlum | 6 | 6 |  | 6 |  | 5 | -2,-4 (4); 1,-5 (2); 1,-2 (2); -2,-3 (2); 3,5 (2) |
| black_sun_initiate | 17 |  | 2 | 2 |  | 1 | 5,5 (4) |
| acicular_defender | 8 |  | 1 | 1 |  | 1 | -1,-2 (4) |
| black_sun_smuggler | 19 |  | 1 | 1 |  | 1 | 5,5 (3) |
| corsec_captain | 22 |  |  | 1 |  | 2 | 3,6 (2); 3,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 35 | 105 |  | 24 | 0,-5 (26); 3,4 (16); 1,-4 (9); 4,3 (9); 0,-2 (8) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 28 | 91 |  | 18 | 3,4 (13); 3,3 (13); 3,6 (12); 5,6 (11); 3,5 (11) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 21 | 46 |  | 15 | -1,-2 (11); 5,4 (7); 0,-2 (6); 3,6 (6); 1,-4 (5) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 11 | 34 |  | 11 | 3,5 (8); 4,3 (7); 1,-5 (5); -2,-3 (5); 1,-4 (4) |
| talus_sleemo_vandal_camp_neutral_medium_theater | ? | 3 | 10 |  | 2 | 3,6 (9); 1,-4 (4) |
| talus_liberation_loyalist_camp_neutral_medium_theater | ? | 3 | 9 |  | 3 | 1,-3 (4); 1,-5 (4); 5,6 (4) |
| talus_dalyrake_nest_neutral_medium | ? | 3 | 9 |  | 3 | 0,-5 (5); 1,-4 (4); 2,-4 (3) |
| talus_vynock_lair_neutral_medium | ? | 3 | 5 |  | 3 | 5,6 (3); 2,-2 (3); 5,5 (2) |
| talus_decay_mite_lair_neutral_boss_01 | ? | 2 | 4 |  | 2 | 4,6 (3); 1,-3 (3) |

