# Talus: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:33 PM to 12:31 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `talus.csv`.

- Bots here: 271 (0 explorers, 106 that killed something).
- Coverage: 38 of 256 squares of 1 km had a bot or a sighting in them (15%); explorers stood in 0.
- Templates: 20 creatures, 10 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 talus` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| paralope | 1-6 | 262 | 6 | 84 |  | 22 | 0,-3 (58); 3,5 (34); -1,-3 (33); 4,5 (32); 5,4 (27) |
| fearful_fynock_youth | 5 | 230 | 6 | 85 |  | 27 | 4,5 (37); -1,-3 (35); 5,5 (34); 0,-2 (32); 0,-3 (30) |
| feared_fynock_youth | 7 | 96 | 4 |  |  | 17 | 0,-3 (42); 4,5 (30); 0,-4 (16); 3,5 (13); -1,-3 (8) |
| putrid_decay_mite_hatchling | 7 | 94 |  |  |  | 7 | 0,-4 (73); 0,-3 (11); 1,-4 (6); -1,-3 (5); -1,-4 (2) |
| repugnant_dung_mite_crawler | 7 | 35 | 6 | 5 |  | 17 | 0,-4 (12); 5,4 (8); 4,5 (7); 4,4 (7); 4,3 (6) |
| chunker_mooch | 7 | 3 | 6 | 8 |  | 7 | 1,-5 (9); -1,-3 (8); 2,-3 (5); 4,4 (3); 3,6 (2) |
| chunker_goon | 7 | 6 | 4 | 9 |  | 4 | 3,6 (14); 5,6 (10); -1,-3 (4); 1,-5 (2) |
| sleemo_punk | 6 | 7 | 3 | 10 |  | 6 | 3,5 (10); 1,-3 (4); 5,6 (4); 0,-5 (4); 4,4 (2) |
| sleemo_delinquent | 7 | 2 | 5 | 7 |  | 5 | 2,4 (7); 4,4 (6); 3,5 (4); 0,-2 (4); 5,6 (4) |
| sleemo_hoodlum | 6 | 6 |  | 6 |  | 4 | 0,-5 (6); 3,5 (4); 4,4 (4); 2,4 (2) |
| chunker_braggart | 8 | 1 | 2 | 3 |  | 1 | 3,5 (12) |
| chunker_nitwit | 5 | 2 | 1 | 3 |  | 3 | 0,-5 (4); 4,6 (4); -2,-3 (1) |
| sleemo_vandal | 9 |  | 2 | 2 |  | 1 | 0,-5 (8) |
| talus_liberation_party_loyalist | 9 |  | 2 | 2 |  | 1 | -1,-3 (7) |
| chunker_pest | 6 | 1 | 1 | 2 |  | 3 | 2,4 (4); 3,6 (2); 3,5 (1) |
| chunker_punk | 6 | 1 | 1 | 2 |  | 2 | -2,-3 (4); -1,-3 (3) |
| talus_liberation_party_volunteer | 8 |  | 1 | 1 |  | 1 | -1,-3 (5) |
| song_rasp | 10 |  | 1 | 1 |  | 3 | -1,-5 (2); 0,-5 (2); 0,-4 (1) |
| dalyrake | 9 |  | 1 | 1 |  | 1 | 6,4 (4) |
| decay_mite | 1 | 1 |  |  |  | 1 | 6,5 (1) |

## Lairs

| template | level | mission finds | fought (checks) | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|
| talus_fynock_youth_lair_neutral_small | ? | 43 | 77 |  | 26 | 0,-2 (13); 4,3 (12); -1,-3 (11); 5,5 (10); -1,-5 (8) |
| talus_paralope_lair_neutral_medium_boss_01 | ? | 32 | 65 |  | 20 | -1,-3 (12); 5,4 (12); 3,5 (10); 1,-3 (9); 0,-5 (9) |
| talus_chunker_goon_camp_neutral_small_theater | ? | 25 | 52 |  | 20 | -1,-3 (10); 3,6 (10); 0,-5 (6); 5,6 (5); 0,-2 (5) |
| talus_sleemo_delinquent_camp_neutral_medium_theater | ? | 11 | 25 |  | 9 | 3,5 (7); 0,-2 (7); 4,4 (4); 1,-3 (4); 0,-5 (4) |
| talus_liberation_loyalist_camp_neutral_medium_theater | ? | 4 | 10 |  | 4 | -1,-3 (4); -1,-4 (4); 4,3 (3); 1,-2 (3) |
| talus_sleemo_vandal_camp_neutral_medium_theater | ? | 2 | 4 |  | 2 | 3,6 (3); 0,-5 (3) |
| talus_chunker_bruiser_camp_neutral_medium_theater | ? | 1 | 4 |  | 1 | 3,5 (5) |
| talus_song_rasp_lair_neutral_medium | ? | 1 | 1 |  | 1 | -1,-5 (2) |
| talus_decay_mite_lair_neutral_boss_01 | ? | 1 | 1 |  | 1 | 6,5 (2) |
| talus_dalyrake_nest_neutral_medium | ? | 1 | 1 |  | 1 | 6,4 (2) |

