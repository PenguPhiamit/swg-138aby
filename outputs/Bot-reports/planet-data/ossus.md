# Ossus: planet data (run13)

From `botpop-launch.jsonl.1955.old`, 16 Oct 4:04 PM to 7:16 PM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 200 (200 explorers, 0 that killed something).
- Coverage: 256 of 256 squares of 1 km had a bot or a sighting in them (100%); explorers stood in 256.
- Templates: 7 creatures, 0 lairs, 2 buildings, 0 named statics, 326 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ossus_kirruk | 1-19 |  |  |  | 149 | 17 | -5,-1 (17); -5,-2 (16); -2,5 (16); -4,-2 (14); -2,4 (14) |
| ossus_gokob | 1-10 |  |  |  | 121 | 16 | 1,5 (16); 0,5 (13); -3,-4 (12); -4,-4 (12); 1,4 (10) |
| ossus_tree_frog | 6 |  |  |  | 120 | 16 | -4,-4 (17); 1,4 (16); 1,5 (14); 0,5 (13); -3,-4 (11) |
| ossus_tribis | 1-10 |  |  |  | 119 | 16 | -4,-4 (17); 1,5 (17); 0,5 (16); -3,-4 (11); 1,4 (11) |
| ossus_kaddyr_bug | 1-10 |  |  |  | 113 | 15 | 1,5 (16); -4,-4 (15); 1,4 (11); 0,5 (11); -3,-4 (10) |
| ossus_mud_yak | 1-19 |  |  |  | 57 | 8 | -5,1 (13); -4,0 (12); -3,1 (9); -3,0 (6); -4,2 (6) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| cave | 3 | -3,-5 (1); 4,-5 (1); 1,5 (1) |
| starport_corellia | 1 | 0,-4 (1) |

## Static objects with no name

326 sightings in 39 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-5440/-1020/39, -5350/-1160/47, -5250/-960/55, -5180/-350/41, -5150/-760/57, -5110/-1980/52, -5010/-230/47, -4980/-1010/49, -4970/-1310/42, -4920/-550/47, -4910/-1160/47, -4670/-210/41, -4660/-370/46, -4620/-1250/49, -4560/-810/45, -4540/-20/49, -4520/1000/40, -4500/-2000/40, -4500/-1210/44, -4480/1680/38, -4440/-2380/55, -4410/-520/41, -4390/1470/54, -4380/-1670/42, -4370/1800/38, -4300/1010/44, -4250/-1820/39, -4200/440/39, -4190/-870/50, -4180/-1140/47, -4160/690/48, -4150/-230/49, -4120/-1440/45, -4110/-1770/44, -4110/-480/47, -4050/-1310/48, -3970/320/51, -3930/620/49, -3900/-1790/45, -3900/-990/39.

