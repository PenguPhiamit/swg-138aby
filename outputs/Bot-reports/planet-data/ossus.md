# Ossus: planet data (run20)

From `botpop-launch.jsonl`, 17 Oct 12:34 AM to 1:00 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 200 (200 explorers, 0 that killed something).
- Coverage: 200 of 256 squares of 1 km had a bot or a sighting in them (78%); explorers stood in 200.
- Templates: 24 creatures, 0 lairs, 6 buildings, 1 named statics, 93 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ossus_tree_frog | 6 |  |  |  | 58 | 9 | -3,-4 (11); 1,4 (11); -4,-4 (10); 0,4 (6); 0,5 (6) |
| brigand | 4 |  |  |  | 3 | 1 | 4,-1 (3) |
| imperial_sergeant | 16 |  |  |  | 2 | 2 | -3,-5 (1); 2,3 (1) |
| artisan | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| commoner | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| imperial_recruiter | 30 |  |  |  | 1 | 1 | 0,-4 (1) |
| junk_dealer | 100 |  |  |  | 1 | 1 | 0,-4 (1) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |
| ossus_ysanna_shaman | 30 |  |  |  | 1 | 1 | -2,-5 (1) |
| hermit | 4 |  |  |  | 1 | 1 | -2,-5 (1) |
| commoner_old | 4 |  |  |  | 1 | 1 | -1,-6 (1) |
| ossus_hutt_broker | 30 |  |  |  | 1 | 1 | 3,-3 (1) |
| smuggler | 14 |  |  |  | 1 | 1 | 3,-3 (1) |
| ossus_hamlet_fisher | 30 |  |  |  | 1 | 1 | -4,1 (1) |
| farmer | 4 |  |  |  | 1 | 1 | -4,1 (1) |
| ossus_adit_foreman | 30 |  |  |  | 1 | 1 | 4,-1 (1) |
| miner | 5 |  |  |  | 1 | 1 | 4,-1 (1) |
| ossus_vault_archivist | 30 |  |  |  | 1 | 1 | 2,1 (1) |
| commoner_technician | 4 |  |  |  | 1 | 1 | 2,2 (1) |
| stormtrooper_rifleman | 25 |  |  |  | 1 | 1 | 2,3 (1) |
| ossus_garrison_commander | 30 |  |  |  | 1 | 1 | 2,3 (1) |
| stormtrooper_squad_leader | 27 |  |  |  | 1 | 1 | 2,3 (1) |
| stormtrooper | 25 |  |  |  | 1 | 1 | 2,3 (1) |
| ossus_alliance_pilot | 30 |  |  |  | 1 | 1 | -2,5 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| cave | 5 | -3,-5 (1); 4,-5 (1); 4,-1 (1); 2,1 (1) |
| merchant_tent_tato_s01 | 2 | -1,-4 (1); 0,-4 (1) |
| military_guard_tower_1 | 2 | -1,-4 (1); 2,3 (1) |
| endor_lake_platform | 2 | -4,1 (1); 5,0 (1) |
| starport_corellia | 1 | 0,-4 (1) |
| endor_lake_walkway_straight | 1 | -4,1 (1) |

## Static objects

| template | seen (256 m squares) | where |
|---|---|---|
| shed_junkshop_watto | 1 | 0,-4 (1) |

## Static objects with no name

93 sightings in 31 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-3880/-3620/54, -3820/-2800/48, -3720/-2930/43, -3680/-3500/47, -3570/-3020/43, -3530/-3310/52, -3460/-4080/58, -3450/-3480/47, -3430/-3680/47, -3420/-2760/49, -3330/-2570/57, -3200/-4220/38, -3180/-2980/42, -3120/-3750/51, -3120/-3410/45, -3100/-3190/45, -3030/1070/42, -2990/-4950/51, -2960/-2640/51, -2890/-3080/39, -2840/-3650/46, -2830/-3940/47, -2810/-3590/47, -2750/-2650/54, -2670/-3040/57, -2620/-3880/50, -2620/-3500/46, -2560/-3190/49, -2460/-3480/42, -2390/-3750/59, -2390/-3070/50, -2320/-3220/41, -1500/5200/61, -1320/-4940/64, -970/-5610/229, -80/-3630/50, -70/-3580/50, 70/-3580/50, 90/-3610/50, 120/-3010/41.

