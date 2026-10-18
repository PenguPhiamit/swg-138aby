# Hutta: planet data (run29)

From `botpop-launch.jsonl`, 17 Oct 11:29 AM to 1:15 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `hutta.csv`.

- Bots here: 147 (0 explorers, 8 that killed something).
- Coverage: 15 of 256 squares of 1 km had a bot or a sighting in them (6%); explorers stood in 0.
- Templates: 2 creatures, 0 lairs, 0 buildings, 0 named statics, no unnamed statics.
- **No explorers here**, so buildings, statics and creatures nobody fought are missing. To send some: `botpop explore 50 hutta` in the test galaxy console (the galaxy owner runs it).

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| rot_mite | 1-11 | 11 | 3 | 5 |  | 5 | -1,1 (7); -2,2 (7); -1,2 (6); -1,0 (5); -2,1 (1) |
| clipped_fynock | 9 | 3 | 1 | 1 |  | 1 | -1,1 (8) |

