# Ossus census (launch-simulation explorers)

Written by `tools/bots/ossus_census.py` from `ossus-census-input.jsonl`, 16 Oct 2026 12:20 AM. Data from 10:11 PM to 12:20 AM (test galaxy, server bots).

- Explorers seen: 800. Map cells visited: 946 of 1024 (512 m cells).
- Sightings (each name once per 256 m square): building 4, creature 3905, static 278.
- Ground samples: 27834 in 3472 squares of 256 m. Flat: at least 4 samples within 4 m of each other: 245 squares.
- Every sighting with coordinates: `ossus-census.csv`.

## Map

One character per 512 m; north up; x from -8192 (left) to 8192. `.` visited, `c` creatures, `L` lair, `S` static object, `B` building, blank not visited.

```
+--------------------------------+
|  cc ccc  ccc cccccc cccc  cc   |
|ccccccccccccccccccccccccccccccc |
| cccccccccccccccccccccccccccccc |
|cccccccccccccccccSSSccccccccccc |
|cccccccccccSSSScSSBSScccccccccc |
|cccccccccccSSSScSSSSSccccccccccc|
| ccccccccccSSSScSSSSSccccccccccc|
|cccccccccccSSSScSSSScccccccccccc|
| ccccccccccccccccccccccccccccccc|
| ccccccccccccccccccccccccccccccc|
|  cccccccccccccccccSScccccccccc |
| cccccccSScccccccccccccccccccccc|
|cccccccSSSScccccccccccccccccccc |
| cccccSSccSccccccccccccccccccccc|
|cccccccSSSSccccccccccccccccccccc|
|cccccccSSSSccccccccccccccccccccc|
| ccccSSSSccccccccccccccccccccccc|
|c  ccSSSSSccccccccccccccccccccc |
|cccccSSSSScccccccccccccccccccccc|
|cccccSSSSSccccccccccccccccccccc |
|ccccccSSSccccccccccccccccccccccc|
|ccccccccSSSScccccccccccccccccccc|
|ccccccccSSSSccccccccccccccccccc |
|   cccccSSSSccccBccccccccccccccc|
|   ccccccSSccccccccccccccccccccc|
|  ccccccccBccccccccccccccBccccc |
| ccccccccccccccccccccccccccccccc|
| cccccccccccccccccccccccccccccc |
|ccccccccccccccccccccccccccccccc |
|  ccccccccccccccccccccccccccccc |
| ccccccccccccccccc cccccccccccc |
|   ccc ccccccccccc    c      ccc|
+--------------------------------+
```

## Buildings and static objects

| Name | Kind | Squares | Where (up to 4, x/y) |
|---|---|---|---|
| unknown_object | static | 278 | -2442/-3416; -2495/-3145; -2366/-3064; -2637/-3419 |
| cave | building | 3 | -2976/-4978; 4895/-4978; 1393/5915 |
| starport_corellia | building | 1 | 0/-3600 |

## Creatures

| Name | Kind | Squares | Level | Where (up to 4, x/y) |
|---|---|---|---|---|
| helper_r2_unit | creature | 3467 | 7 | -3/-3598; 11/-3600; -10/-3581; 12/-3578 |
| ossus_kirruk | creature | 125 | 1-19 | -3310/-1605; -3480/-1907; -3247/-1463; -3450/-1374 |
| ossus_gokob | creature | 74 | 1-10 | -2436/-3431; -2377/-3038; -2724/-3241; -2592/-2766 |
| ossus_tribis | creature | 71 | 10 | -2452/-2914; -3086/-4184; -3224/-3325; -3055/-4164 |
| ossus_kaddyr_bug | creature | 62 | 1-10 | -2501/-3124; -2624/-3406; -2825/-3097; -2809/-3093 |
| ossus_tree_frog | creature | 56 | 6 | -2545/-3302; -2631/-2999; -2781/-4001; -2872/-4184 |
| ossus_mud_yak | creature | 49 | 19 | -2982/444; -3107/374; -2875/558; -2691/694 |
| Transport Shuttle | creature | 1 | 10 | 0/-3600 |

## Flat ground (256 m squares, best sampled first, up to 40)

| Centre x/y | Height | Range (m) | Samples |
|---|---|---|---|
| 2688/-1920 | 105 | 3.0 | 21 |
| 2944/-2176 | 104 | 2.0 | 20 |
| 1408/-640 | 54 | 4.0 | 20 |
| 3200/-1408 | 104 | 1.0 | 19 |
| 2944/-1664 | 104 | 2.0 | 17 |
| 3456/-1152 | 105 | 2.0 | 17 |
| -640/-384 | 53 | 4.0 | 17 |
| 4736/640 | 104 | 2.0 | 16 |
| 2688/-2176 | 103 | 3.0 | 16 |
| -128/1664 | 48 | 4.0 | 16 |
| 3968/-640 | 104 | 1.0 | 15 |
| 3712/-896 | 104 | 4.0 | 15 |
| 2944/-2432 | 104 | 2.0 | 14 |
| 2944/-1920 | 103 | 2.0 | 14 |
| 3200/-1664 | 104 | 2.0 | 14 |
| 3968/-1920 | 105 | 2.0 | 14 |
| 3200/-2432 | 104 | 2.0 | 13 |
| 4736/-1152 | 104 | 2.0 | 13 |
| 4224/-128 | 105 | 2.0 | 13 |
| 1408/2688 | 170 | 2.0 | 13 |
| 4480/-1152 | 105 | 3.0 | 13 |
| 4736/-896 | 104 | 3.0 | 13 |
| -2432/-1920 | 47 | 4.0 | 13 |
| -3968/-1152 | 39 | 4.0 | 13 |
| 3712/-1152 | 104 | 1.0 | 12 |
| 4480/-1408 | 104 | 1.0 | 12 |
| 4736/384 | 104 | 1.0 | 12 |
| 4224/-1664 | 104 | 2.0 | 12 |
| 3968/-384 | 105 | 2.0 | 12 |
| 3712/-2176 | 104 | 3.0 | 12 |
| 4480/128 | 104 | 3.0 | 12 |
| 4480/-1664 | 104 | 4.0 | 12 |
| 2944/-1408 | 103 | 1.0 | 11 |
| 5248/-384 | 103 | 1.0 | 11 |
| 3456/-896 | 105 | 2.0 | 11 |
| -1408/2432 | 51 | 2.0 | 11 |
| 3456/-1408 | 105 | 3.0 | 11 |
| 4992/896 | 105 | 3.0 | 11 |
| -1408/1408 | 46 | 4.0 | 11 |
| 3456/1408 | 46 | 4.0 | 11 |

Heights are the explorers' own ground samples and the creatures' positions; a square counts only where an explorer or creature stood, so a flat square is flat where it was sampled, not necessarily across all 256 m. No-build circles around towns and POIs are not checked here.
