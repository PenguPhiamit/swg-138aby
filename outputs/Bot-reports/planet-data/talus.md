# Talus: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:03 PM to 7:16 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 166 (0 explorers, 109 that killed something).
- Coverage: 43 of 256 squares of 1 km had a bot or a sighting in them (17%); explorers stood in 0.
- Templates: 31 creatures, 11 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 902 | 73 | 171 |  | 34 | 4,5 (256); 4,4 (173); 0,-4 (172); 0,-3 (161); 3,5 (94) |
| fearful_fynock_youth | 5 | 583 | 80 | 236 |  | 34 | 3,5 (118); -1,-4 (114); 1,-4 (87); 0,-4 (81); 0,-3 (62) |
| feared_fynock_youth | 7 | 427 | 46 |  |  | 20 | 4,5 (306); 0,-4 (279); 0,-3 (83); 4,4 (32); 3,5 (31) |
| putrid_decay_mite_hatchling | 7 | 57 | 3 |  |  | 11 | 4,5 (21); 0,-4 (17); 3,4 (14); 3,5 (8); -1,-3 (7) |
| chunker_goon | 7 | 10 | 19 | 15 |  | 21 | 0,-5 (12); 5,3 (12); 2,4 (6); 4,6 (6); 2,-3 (5) |
| sleemo_delinquent | 7 | 5 | 16 | 21 |  | 14 | 0,-2 (8); 4,6 (8); -2,-5 (8); 1,-3 (8); 2,4 (6) |
| repugnant_dung_mite_crawler | 1-7 | 47 | 6 | 3 |  | 14 | 4,4 (17); 4,5 (11); -1,-3 (7); 3,6 (5); 0,-3 (4) |
| sleemo_hoodlum | 6 | 1 | 13 | 13 |  | 7 | 0,-3 (12); 5,4 (11); 5,5 (8); 4,3 (8); -1,-4 (7) |
| sleemo_punk | 6 | 4 | 9 | 14 |  | 10 | -1,-3 (10); 5,5 (8); -1,-4 (5); 0,-5 (5); 2,-5 (4) |
| chunker_mooch | 7 | 2 | 9 | 12 |  | 8 | 1,-2 (8); 2,-4 (8); 3,6 (8); 2,-3 (6); 2,4 (4) |
| chunker_punk | 6 | 6 | 4 | 11 |  | 10 | 4,6 (10); -1,-4 (5); -1,-2 (4); 0,-5 (4); 5,3 (4) |
| chunker_pest | 6 | 7 | 4 | 12 |  | 8 | 4,6 (9); -1,-4 (8); 5,3 (6); 2,-3 (4); 1,-3 (4) |
| vynock | 1-9 | 5 | 7 | 7 |  | 9 | 2,6 (8); 1,-4 (8); 4,5 (5); -1,-5 (4); 2,5 (4) |
| chunker_nitwit | 5 | 5 | 5 | 10 |  | 7 | 1,-2 (8); -1,-2 (6); -1,-4 (5); 0,-5 (4); 4,6 (2) |
| song_rasp | 10 | 4 | 6 | 3 |  | 5 | 4,5 (13); 5,5 (8); 5,3 (4); 3,4 (3); 1,-5 (1) |
| sleemo_scamp | 8 |  | 6 | 6 |  | 6 | -1,-2 (4); -1,-3 (4); 2,-3 (4); 5,4 (4); 0,-5 (4) |
| decay_mite | 1-9 | 1 | 4 | 4 |  | 5 | 1,-3 (12); -2,-4 (4); 0,-4 (3); -1,-3 (2); 3,4 (2) |
| dalyrake | 1-9 | 5 | 2 | 1 |  | 4 | 0,-3 (5); -1,-3 (5); 0,-4 (2); 1,-5 (2) |
| talus_liberation_party_volunteer | 8 | 1 | 2 | 3 |  | 2 | -1,-4 (8); 5,4 (4) |
| acicular_defender | 8 | 3 | 1 | 1 |  | 5 | 3,5 (4); 3,3 (3); -1,-4 (3); 3,4 (1); 5,4 (1) |
| flite_rasp | 8 |  | 3 |  |  | 4 | -1,-5 (3); -2,-3 (3); 4,3 (3); 1,-2 (3) |
| chunker_creep | 9 |  | 3 | 3 |  | 2 | 3,6 (8); 4,3 (3) |
| chunker_bruiser | 11 |  | 3 | 3 |  | 3 | 2,-3 (4); 1,-5 (3); -2,-4 (3) |
| lost_aqualish_scout | 9 |  | 2 | 2 |  | 1 | 5,4 (8) |
| sleemo_vandal | 9 |  | 2 | 2 |  | 2 | 2,-3 (4); 3,6 (4) |
| clipped_fynock | 9 | 1 | 1 | 1 |  | 1 | 4,5 (6) |
| chunker_swindler | 8 |  | 1 | 1 |  | 1 | 3,6 (4) |
| talus_liberation_party_loyalist | 9 |  | 1 | 1 |  | 1 | -1,-5 (4) |
| chunker_braggart | 8 |  |  |  |  | 1 | 1,-5 (3) |
| black_sun_initiate | 17 |  | 1 | 1 |  | 1 | 5,5 (2) |
| minor_sludge_panther | 10 | 1 |  |  |  | 1 | 0,-3 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 256 |  |  | 36 | 5,5 (19); -1,-5 (15); 3,5 (14); 1,-5 (13); -1,-4 (13) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 187 |  |  | 32 | 5,4 (13); 4,6 (12); 1,-4 (12); -1,-3 (10); 3,6 (9) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 156 |  |  | 33 | -1,-4 (11); 3,6 (10); 1,-2 (10); -1,-2 (9); 1,-3 (9) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 86 |  |  | 31 | 1,-3 (8); 0,-2 (7); 0,-5 (6); 5,5 (6); 3,6 (5) |
| talus_vynock_lair_neutral_medium | ? | 17 |  |  | 12 | 2,5 (3); 3,6 (3); 1,-4 (2); 4,6 (1); 2,6 (1) |
| talus_liberation_loyalist_camp_neutral_medium_theater | ? | 15 |  |  | 12 | 4,3 (3); 5,4 (2); 1,-2 (1); -1,-5 (1); 1,-4 (1) |
| talus_sleemo_vandal_camp_neutral_medium_theater | ? | 15 |  |  | 11 | 0,-5 (2); -1,-2 (2); -1,-4 (2); 5,5 (2); -1,-3 (1) |
| talus_dalyrake_nest_neutral_medium | ? | 15 |  |  | 11 | 3,3 (2); 3,4 (2); 1,-5 (2); 1,-3 (2); 1,-4 (1) |
| talus_decay_mite_lair_neutral_boss_01 | ? | 11 |  |  | 10 | 0,-5 (2); 1,-3 (1); -2,-4 (1); 3,5 (1); -1,-3 (1) |
| talus_song_rasp_lair_neutral_medium | ? | 4 |  |  | 4 | 5,5 (1); 5,3 (1); 2,5 (1); 3,3 (1) |
| talus_chunker_bruiser_camp_neutral_medium_theater | ? | 1 |  |  | 1 | 3,6 (1) |

