# Ossus: planet data (run19)

From `botpop-launch.jsonl`, 16 Oct 11:33 PM to 12:30 AM. Written by `tools/bots/planet_census.py`; every row with its squares is in `ossus.csv`.

- Bots here: 200 (200 explorers, 0 that killed something).
- Coverage: 250 of 256 squares of 1 km had a bot or a sighting in them (98%); explorers stood in 250.
- Templates: 24 creatures, 0 lairs, 6 buildings, 1 named statics, 146 sightings of unnamed statics.

Squares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. Counts in brackets are events in that square (sightings, kills, deaths and so on).

## Creatures

| template | level | killed | killed a bot | attacked first | seen (256 m squares) | 1 km squares | most met in |
|---|---|---|---|---|---|---|---|
| ossus_tree_frog | 6 |  |  |  | 110 | 14 | -4,-4 (14); 0,5 (14); 1,5 (13); 1,4 (11); 0,4 (10) |
| imperial_sergeant | 16 |  |  |  | 2 | 2 | -3,-5 (1); 2,3 (1) |
| brigand | 4 |  |  |  | 2 | 1 | 4,-1 (2) |
| imperial_recruiter | 30 |  |  |  | 1 | 1 | 0,-4 (1) |
| junk_dealer | 100 |  |  |  | 1 | 1 | 0,-4 (1) |
| artisan | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| commoner | 4 |  |  |  | 1 | 1 | -1,-4 (1) |
| Transport Shuttle | 10 |  |  |  | 1 | 1 | 0,-4 (1) |
| ossus_ysanna_shaman | 30 |  |  |  | 1 | 1 | -2,-5 (1) |
| hermit | 4 |  |  |  | 1 | 1 | -2,-5 (1) |
| smuggler | 14 |  |  |  | 1 | 1 | 3,-3 (1) |
| ossus_hutt_broker | 30 |  |  |  | 1 | 1 | 3,-3 (1) |
| ossus_hamlet_fisher | 30 |  |  |  | 1 | 1 | -4,1 (1) |
| farmer | 4 |  |  |  | 1 | 1 | -4,1 (1) |
| ossus_adit_foreman | 30 |  |  |  | 1 | 1 | 4,-1 (1) |
| miner | 5 |  |  |  | 1 | 1 | 4,-1 (1) |
| ossus_vault_archivist | 30 |  |  |  | 1 | 1 | 2,1 (1) |
| commoner_old | 4 |  |  |  | 1 | 1 | -1,-6 (1) |
| stormtrooper_rifleman | 25 |  |  |  | 1 | 1 | 2,3 (1) |
| commoner_technician | 4 |  |  |  | 1 | 1 | 2,2 (1) |
| ossus_garrison_commander | 30 |  |  |  | 1 | 1 | 2,3 (1) |
| stormtrooper_squad_leader | 27 |  |  |  | 1 | 1 | 2,3 (1) |
| stormtrooper | 25 |  |  |  | 1 | 1 | 2,3 (1) |
| ossus_alliance_pilot | 30 |  |  |  | 1 | 1 | -2,5 (1) |

## Buildings

| template | seen (256 m squares) | where |
|---|---|---|
| cave | 6 | -3,-5 (1); 4,-1 (1); 2,1 (1); 2,2 (1) |
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

146 sightings in 35 squares of 1 km: objects the server holds with no name (no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:

-4000/-3640/53, -3980/-3480/47, -3920/-3170/45, -3900/-2950/38, -3840/-3660/56, -3830/-3860/54, -3790/-3430/54, -3740/-3200/55, -3650/-2690/45, -3620/-4140/46, -3610/-2870/51, -3520/-3920/56, -3470/-4250/44, -3450/-3780/54, -3450/-3220/53, -3450/-2700/55, -3420/-2940/46, -3360/-3420/54, -3280/-4220/42, -3270/-3280/57, -3260/-2720/46, -3210/-3520/49, -3160/-4040/49, -3140/-3010/42, -3110/-2520/56, -3030/1100/42, -3020/-2520/54, -3010/-3410/38, -2990/-4950/51, -2970/-3160/39, -2930/-3740/42, -2930/-2920/43, -2910/-4050/54, -2860/-2600/56, -2820/-4170/48, -2780/-2770/47, -2730/-3140/50, -2710/-4060/47, -2690/-3820/55, -2620/-3520/47.

