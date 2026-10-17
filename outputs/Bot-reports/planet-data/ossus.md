# Ossus: planet data (run22)

From `botpop-launch.jsonl`, 17 Oct 2:26 AM to 2:28 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 100 (100 explorers, 0 that killed something).
- Coverage: 6 of 256 squares of 1 km had a bot or a sighting in them (2%); explorers stood in 6.
- Templates: 5 creatures, 0 lairs, 3 buildings, 1 named statics, 6 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| imperial_recruiter | 30 |  |  |  | 1 | 1 | 0,-4 (1) |
| junk_dealer | 100 |  |  |  | 1 | 1 | 0,-4 (1) |
| artisan | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| commoner | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| merchant_tent_tato_s01 | 2 | -1,-4 (1); 0,-4 (1) |
| military_guard_tower_1 | 1 | -1,-4 (1) |
| starport_corellia | 1 | 0,-4 (1) |

## Static objects

| template | seen (256 m squares) | where |
|---|---|---|
| shed_junkshop_watto | 1 | 0,-4 (1) |

## Static objects with no name

6 sightings in 3 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-80/-3630/50, -70/-3580/50, 70/-3580/50, 90/-3610/50, 120/-3010/41, 260/-2600/58.

