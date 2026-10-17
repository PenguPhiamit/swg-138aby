# Ossus: planet data (run21)

From `botpop-launch.jsonl`, 17 Oct 1:03 AM to 1:22 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 200 (200 explorers, 0 that killed something).
- Coverage: 137 of 256 squares of 1 km had a bot or a sighting in them (54%); explorers stood in 137.
- Templates: 17 creatures, 0 lairs, 6 buildings, 1 named statics, 59 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ossus_tree_frog | 6 |  |  |  | 25 | 6 | -3,-4 (12); -4,-3 (6); -4,-4 (4); -3,-5 (1); -5,-4 (1) |
| brigand | 4 |  |  |  | 2 | 1 | 4,-1 (2) |
| imperial_recruiter | 30 |  |  |  | 1 | 1 | 0,-4 (1) |
| junk_dealer | 100 |  |  |  | 1 | 1 | 0,-4 (1) |
| artisan | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| commoner | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |
| ossus_ysanna_shaman | 30 |  |  |  | 1 | 1 | -2,-5 (1) |
| hermit | 4 |  |  |  | 1 | 1 | -2,-5 (1) |
| imperial_sergeant | 16 |  |  |  | 1 | 1 | -3,-5 (1) |
| ossus_hutt_broker | 30 |  |  |  | 1 | 1 | 3,-3 (1) |
| smuggler | 14 |  |  |  | 1 | 1 | 3,-3 (1) |
| ossus_adit_foreman | 30 |  |  |  | 1 | 1 | 4,-1 (1) |
| miner | 5 |  |  |  | 1 | 1 | 4,-1 (1) |
| ossus_hamlet_fisher | 30 |  |  |  | 1 | 1 | -4,1 (1) |
| farmer | 4 |  |  |  | 1 | 1 | -4,1 (1) |
| ossus_vault_archivist | 30 |  |  |  | 1 | 1 | 2,1 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| cave | 5 | -3,-5 (1); 4,-5 (1); 4,-1 (1); 2,1 (1) |
| merchant_tent_tato_s01 | 2 | -1,-4 (1); 0,-4 (1) |
| military_guard_tower_1 | 1 | -1,-4 (1) |
| starport_corellia | 1 | 0,-4 (1) |
| endor_lake_walkway_straight | 1 | -4,1 (1) |
| endor_lake_platform | 1 | -4,1 (1) |

## Static objects

| template | seen (256 m squares) | where |
|---|---|---|
| shed_junkshop_watto | 1 | 0,-4 (1) |

## Static objects with no name

59 sightings in 23 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-4040/-3150/39, -3870/-2920/44, -3840/-3160/51, -3410/-2590/53, -3280/-3680/50, -3200/-2620/51, -3130/-2970/41, -3120/-3340/48, -3080/-3120/46, -3020/1090/42, -3010/-2590/49, -2990/-4950/51, -2990/-3850/44, -2980/-3500/39, -2970/-3230/39, -2820/-3760/50, -2770/-3310/40, -2710/-4130/46, -2680/-3010/56, -2660/-2750/42, -2620/-3840/54, -2570/-3500/44, -2540/-3980/49, -2420/-3080/48, -2410/-3540/43, -2360/-3700/53, -1320/-4930/64, -70/-3580/50, -60/-3680/50, 40/-3680/50, 70/-3580/50, 120/-3010/41, 260/-2600/58, 280/-6410/337, 280/-6390/338, 340/-2240/48, 410/-1860/53, 490/-1500/40, 610/-1140/57, 690/-760/42.

