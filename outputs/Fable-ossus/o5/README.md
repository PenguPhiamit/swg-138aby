# Ossus O5: the first look on the test galaxy — Fable, 14 Oct 2026

Stage only; read-only on /opt/swg (dev HEAD 8f2072e7); nothing in h/tools or Local-content touched. Numbers are mine
unless a source is named. **Verified** = checked offline here; **staged** = written, not yet run on the galaxy or seen
in a client.

| path | what |
|---|---|
| `local_planets.tre` | the test-session archive: Hoth (as installed) + Ossus; **sha256 254d0e497497a78e86a27eac9b5d201e9527d8d5a3f3e3229ce12866f2fa1604**, 3,758,629 bytes, 38 entries |
| `build_test_archive.py` | the wrapper: runs `tools/hoth/hoth_client_build.main()` with STAGE/TRE pointed into `work/`, then `stage_ossus` (O4) on that folder, then packs with `swgfmt.tre_write` (the builder's writer and MD5 rule); writes `checks.json` |
| `patch/ossus-first-look.patch`, `tools/make_patch.py`, `work/gitcheck.sh` | the dev patch (2 files +27/−1, 1 new file); `git apply --check` clean, `luac5.3 -p` ok |
| `checks.json` | the numbers below |

## 1. Client (verified offline)

- The Hoth build inside the wrapper is byte-identical to the installed archive (aee83cc6…, 12 round trips exact,
  archive verified), so Ossus is added to exactly what the owner has.
- Of the installed 20 entries, **13 are byte-identical** (Hoth's 18 POIs and labels, the quest strings, the skill and
  CRC tables…) and **7 change only by Ossus rows**: `misc/planet_crc_string_table.iff` (+ossus), `datatables/travel/travel.iff`
  (+column/row: Corellia→Ossus 3000, Ossus→Corellia 1750, Ossus→Ossus 100, placeholders), `string/en/planet_n.stf` (+Ossus),
  `datatables/player/waypoint_planets.iff` (+ossus / ui_planet_sel_ossus.apt after hoth), the two UI includes (Ossus blocks
  after Hoth's, galaxy-map spot placeholder 425,290), `datatables/resource/resource_tree.iff` (777 → 822 rows: 52 Hoth, 45 Ossus).
  **18 new entries**: terrain + 3 TGAs + terrain environment, environment and clientregion tables, region and loading
  strings, the snapshot (87 nodes), the map, the globe chain, the loading tile and table.
- Registration carries both planets (planet CRC, travel columns `… yavin4, hoth, ossus` and rows, planet_n, waypoint rows).
- Closure from the Ossus seeds (terrain, snapshot, globe, map, tile, both environment tables): 859 files, 13 from our
  archive, the rest stock/MTG; the 12 "missing" `shader/<word>.sht` are words of our multi-word shader family names
  (the scanner's known artefact — Hoth's recorded `shader/rock.sht`/`snow.sht` are the same), every real shader the
  families name is in the client (checks.json `closure_note`).

## 2. Server (staged; git apply --check clean, luac ok)

- `managers/planet/planet_manager.lua`: the `ossus` block before `tutorial = {` (weather and GCW on, travel point
  **Knossa at 20.3, 50.3, −3582.2**, landingRange 3, a nav area at the pad). The shuttle, travel terminal and ticket
  collector come from the snapshot's `shared_outpost_starport` building at 0 −3600 (yaw 180), exactly as Hoth's
  Scavenger Starport gets its own (port log 13 Oct 23:05: the building's child objects create them); the pad offset is
  the same 20.3 / 17.8 m as Hoth and Yavin IV. Fares are the client table's placeholders (Q10).
- `managers/planet/ossus_regions.lua` (new): the four edge strips, Knossa as a CITY + NOSPAWNAREA circle (200 m) with a
  320 m no-build circle, no-build at the academy ruins (260 m, also no-spawn) and the three cave mouths (120 m).
  **No spawn areas, no world spawner**: no creatures for the first look; O2b's full file waits.
- `managers/resource_manager.lua`: `ossus` appended to `activeZones` (its 45 native types are in the merged tree).
- Snapshot: `snapshot/ossus.ws` is in the archive; the server reads it through TreFiles (local_planets.tre first).
  Without one, `PlanetManagerImplementation::loadSnapshotObjects` logs "Snapshot wasn't found." and goes on
  (line 622–629): the zone would load with bare terrain and no starport, so no shuttle.
- No C++ needed. **Your lines in `tools/test_galaxy.py`:** `TEST_ZONES = ['hoth', 'ossus']` (line 24) — it then adds both
  to `Core3.ZonesEnabled` and sets `backfillZones = "hoth,ossus"` (98ad1d1d makes that idempotent). Install the archive
  as `/opt/swg/tre/local_planets.tre` and `SWG-client/local_planets.tre`, restart.

## 3. Owner check (one test-session client visit)

1. Coronet Starport (−67, −4711): the ticket list offers **Ossus** at 3,000 credits; the galaxy map shows a new globe
   button below Hoth's (an olive world with grey poles). No Ossus in the list → the archive is not loaded (checker in
   `Fable-live-client/l1`); a blank globe → report "globe blank" (O3's 32-bit texture; a DXT1 encoder is the fallback).
2. Board. The loading screen shows our tile (an olive map, a lake, a dark road) and the text "Ossus, in the Adega
   system…". A crash here with `terrain/ossus.trn` in the crash file → report the exact FATAL line (the terrain's
   PTAT 0014 layout is Tatooine's; a family or bitmap name would be the suspect).
3. You land on the Knossa pad (21, −3582, 50 m up). Look around: a flat landing field with the starport, cloning facility
   and warehouse; the plain is olive scrub at 44–50 m with small ponds; the ground should not be flat grey (missing
   shaders show as white or purple), the sky Dantooine-like, the sun Tatooine's; weather on.
4. Walk off the pad to the south edge: the drop to the plain is a feathered ramp, not a wall. Then `/teleport 500 -1500 ossus`:
   the Knossa road (12 m, packed dirt) runs north; follow it with the camera or `/teleport 1300 1500 ossus`, then
   `/teleport 2016 2848 ossus`: the academy ruins on the benchland (170 m), 31 stone statics on a flat meadow.
5. `/teleport -3600 1200 ossus`: the lake (water at 38.5 m, Dantooine lake shader). `/teleport 4300 -700 ossus`: Imhar
   Canyon, floor 44.5 m between 100 m mesas. `/teleport -2976 -4940 ossus`: the western cave mouth facing north
   (stock ice-cave building reskinned? no — stock cave); walk in: a cell interior, floor at the apron height.
6. Open the planetary map: the rendered map (olive plains, the benchland, the canyon, the southern grey range, the
   lake, the road) with the Knossa label; the location line reads "Knossa" on the pad, "The Academy Benchland" at the
   ruins, "Imhar Canyon" in the canyon.
7. Report: any crash line; any white/purple ground (and where); floating or buried buildings at the pad, ruins or
   caves; a road that floats or cuts; missing water; a black sky; a map that is blank or shows Endor's.

## 4. Open questions (Q10, placeholders kept as they are)

Story point and era presence on Ossus; whether anyone garrisons Knossa (and who); Jedi presence at the academy ruins
(none placed); the fares (3000 / 1750 / 100 are the Hoth pattern); the look (environment family = Dantooine, sun =
Tatooine; the map's palette; the globe); the galaxy-map spot (425, 290). Fauna levels (O2b's 22–56 placeholder) and the
creature set wait with O2b.
