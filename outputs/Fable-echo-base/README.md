# Echo Base E0: the first look in the real client — Fable, 14 Oct 2026

Stage only. Read-only on /opt/swg (HEAD eccb53e1); own readers (swgfmt.trn_iff, a portal-layout parse in
`tools/fit_echo_base.py`, the Hoth terrain height port, our asset_refs scanner); no Bellum or downloaded code run.
Numbers are mine unless a source is named.

| path | what |
|---|---|
| `tools/fit_echo_base.py`, `out/fit.json` | 1: the fit of the NGE building to MTG's cut-outs, and the client-file closure |
| `patch/echo-base-e0.patch`, `tools/make_patch.py`, `work/gitcheck.sh` | 2: the dev patch (+5 lines in 4 files, 4 new files); `git apply --check` clean, `luac5.3 -p` ok on all 8 |
| `checks.json` | the numbers below |

## 1. The fit

`appearance/echo_base_pob.pob` (mtg_patch_016.tre, 51 KB) has 41 cells and 41 portal geometries; cell 0 (outside)
opens through five portals. Three of them are the openings MTG cut into `hoth.trn` (the `echobaseexclusions` layer):
the distances between them match the distances between the cut-out centres, which the earlier by-size guess did not:

| door | portal (geometry → cell) | portal size, local centre | cut-out centre, size | local vs world distance |
|---|---|---|---|---|
| hangar | 1 → cell 11 | 49.3 × 35.9 m at (−199.4, z 596.2), floor y 71.7 | (−5307.2, 5692.4), 59.8 × 45.8 m | hangar–main 382.3 vs 381.7 m |
| main door | 0 → cell 1 | 5.2 × 4.8 m at (59.4, 314.8), floor y 47.4 | (−5050.4, 5409.9), 19.2 × 18.3 m | hangar–tower 651.1 vs 645.9 m |
| tower | 4 → cell 40 | 6.3 × 10.0 m at (77.6, 6.9), floor y 149.8 | (−5036.4, 5106.0), 6.5 × 12.3 m | main–tower 308.5 vs 304.3 m |

Rigid fit (rotation + translation, mirror tested): **no mirror, heading −0.43° ≈ 0, origin (−5112.8, 5096.6), RMS 2.3 m**
(residuals 2.0 / 1.3 / 3.3 m): MTG placed the building unrotated. Height: terrain at the cut-outs 110.4 (hangar),
85.0 (main), 186.4 (tower) m minus the portals' floor heights gives **z = 38.7 / 37.6 / 36.6 m — 37.6 m, spread 2.1 m**,
three independent doors agreeing, so the pob's local frame and MTG's cut-outs are the same design. Two more exterior
portals (geometries 2 → cell 34, 37.6 × 20.4 m at (−109, −296), and 3 → cell 36, 19.8 × 22.8 m at (−402, 42)) have no
cut-out: they open at terrain 90–125 m above their floors + z, i.e. underground — expect those two doors to be buried
(the look will show whether the client draws them into rock).

## 2. The server patch

`screenplays/poi/hoth_echo_base.lua` (one `spawnSceneObject("hoth", "object/building/heroic/echo_base.iff", -5112.8,
37.6, 5096.6, 0, 0)`, our camps style, no NPCs), its include line in `screenplays.lua`, the server template pair
`object/building/heroic/{objects,echo_base,serverobjects}.lua` (Core3-dev had none: only custom_content's doors and
token) with their include lines in `object/allobjects.lua` and `object/building/serverobjects.lua`, and a 750 m
`NOBUILDZONEAREA + NOSPAWNAREA` circle at (−5113, 5097) in `hoth_regions.lua` (the building spans local x −402..+78,
z −296..+596). Teleports: `/teleport -5051 5440 hoth` (main door), `/teleport -5307 5750 hoth` (hangar),
`/teleport -5036 5120 hoth` (tower). Untested: that `spawnSceneObject` builds the 41 cells for a screenplay-placed
building the way snapshot buildings get theirs (dev has no screenplay that spawns an `object/building/` template; the
camps' statics are not buildings). If the building appears without an interior, the fallback placement is a node in
`snapshot/hoth.ws` in local_planets.tre with our ws_write (O2a's route) — half a day.

## 3. The client side

Nothing new for local_planets.tre. The closure from `object/building/heroic/shared_echo_base.iff` reaches **285 files,
0 missing**: 1 from mtg_patch_019 (the template), 85 from mtg_patch_016 (the pob, room meshes, props), 85 from
mtg_patch_018 and 95 from mtg_patch_014 (shaders and textures), 2 from mtg_patch_022, 17 stock. The template's CRC is in
the merged `object_template_crc_string_table.iff` already (local_planets.tre). The server reads the template and pob
through its TreFiles (the 23 MTG archives are listed there since 13 Oct).

## 4. Owner check (one client session, test galaxy, after the patch and a restart)

1. `/teleport -5051 5440 hoth`, face the mountain: a metal door set into rock at about (−5051, 5411), the massif rising
   behind it. No door → the building did not spawn (server log: "hoth_echo_base" / template errors) or you are inside
   the rock: `/teleport -5051 5380 hoth` and look back.
2. Walk through the main door (cell 1): a corridor interior, lit; the floor level with the terrain outside (within ~1 m).
   A fall through the floor or a black void → the cells did not load (go to the snapshot route above).
3. `/teleport -5307 5750 hoth`: the hangar mouth (49 m wide) in the north flank, open to the plain; walk in (cell 11).
4. `/teleport -5036 5120 hoth`: the tower opening near the top (cell 40); look at how the rock meets the structure.
5. Inside: cross a few of the 41 cells (hangar → corridors → the big rooms), note missing textures (flat white or
   purple surfaces), untextured props, doors that do not open (NGE doors are objects we have not placed), places you
   fall through or get stuck (collision), and lighting (fully dark cells = missing light data). `/dumpZoneInformation`
   or the coordinates on screen tell which cell.
6. Outside again: the two buried doors on the south and west sides (−5222, 4800 and −5515, 5139 in world terms): is
   the rock drawn through them or are there holes?

**Go** (building, doors and most cells draw and collide; a few bad textures are fine): E1 as planned — the NGE
building in `snapshot/hoth.ws`, props, the no-build region, names and markers. **No-go** (no interior, falls through
floors, client crash on approach): the stock set below, and the NGE assets stay as outside dressing only.

## 5. The stock-set fallback (if E0 says no-go)

Dig `general/shared_bunker_rebel_01.iff` (a stock Rebel bunker dungeon with its own cells) into the east flank at the
main cut-out (−5050, 5410, the same 37.6 m contact, heading east), put `military/shared_military_base_shed_rebel_style_01`,
`shared_military_base_gate_house_rebel`, `shared_military_outpost_guard_house_rebel` and `shared_rebel_fuel_depot` on
the 82–93 m plateau east of it as the outpost, close the hangar cut-out with MTG's `shared_hoth_generator_destroyed`
and the tower cut-out with stock rock props, keep the 750 m no-build circle, and run the E3 roster inside the bunker's
cells. All stock pre-CU buildings the client already draws; two days, no client change.
