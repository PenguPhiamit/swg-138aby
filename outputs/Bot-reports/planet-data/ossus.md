# Ossus: planet data (run18)

From `botpop-launch.jsonl`, 16 Oct 10:26 PM to 11:30 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 200 (200 explorers, 0 that killed something).
- Coverage: 255 of 256 squares of 1 km had a bot or a sighting in them (100%); explorers stood in 255.
- Templates: 7 creatures, 0 lairs, 2 buildings, 0 named statics, 280 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ossus_kirruk | 1-19 |  |  |  | 130 | 15 | -5,-1 (16); -4,-2 (15); -2,4 (15); -2,5 (15); -5,-2 (14) |
| ossus_gokob | 1-10 |  |  |  | 75 | 15 | -4,-4 (11); -3,-4 (10); 1,4 (9); 1,5 (8); 0,5 (8) |
| ossus_tribis | 1-10 |  |  |  | 71 | 14 | -4,-4 (14); 0,5 (9); 1,4 (7); -3,-4 (6); 1,6 (6) |
| ossus_kaddyr_bug | 10 |  |  |  | 59 | 15 | -4,-4 (8); 1,4 (8); 1,5 (7); 0,4 (6); 0,5 (6) |
| ossus_tree_frog | 6 |  |  |  | 55 | 14 | -4,-4 (7); 0,4 (7); 1,4 (6); -3,-4 (5); 1,5 (5) |
| ossus_mud_yak | 19 |  |  |  | 51 | 8 | -4,0 (9); -3,1 (9); -5,1 (8); -5,0 (7); -4,1 (6) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| cave | 3 | -3,-5 (1); 4,-5 (1); 1,5 (1) |
| starport_corellia | 1 | 0,-4 (1) |

## Static objects with no name

280 sightings in 39 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-5540/-860/49, -5500/-1090/39, -5400/-710/53, -5280/-1860/46, -5280/-470/42, -5130/-750/54, -5120/-250/40, -5110/-710/52, -5100/-1680/43, -5070/-1400/57, -4950/-1040/45, -4930/-510/47, -4800/-80/49, -4790/-380/54, -4680/-2100/55, -4680/-660/51, -4670/-1770/49, -4620/1440/52, -4600/-1020/49, -4560/-250/43, -4540/-1840/48, -4530/-2080/41, -4520/1640/41, -4510/960/43, -4430/1800/41, -4420/1450/54, -4390/1160/50, -4360/730/57, -4340/1640/39, -4310/980/42, -4280/1070/45, -4220/-1730/39, -4190/-2370/50, -4130/-2070/60, -4130/-1360/49, -4130/2050/43, -4120/-1930/54, -4120/650/48, -4060/-310/46, -4000/-1790/51.

