# Fable: Hoth batch B, staged (14 Oct 2026)

B1 camps and patrol posts, B2 the mynock den as a spawned ice cave (server screenplay + client terrain patch), B3 the names TSV. Staged for Claude to review, apply and test; nothing has been loaded by Core3 or seen in game. Sources read as text: Bellum Gero's Hoth static spawns and POI generator (AGPL-3.0), Core3-dev, MTG's `hoth.trn`/`hoth.ws` (our own readers). No git run. Numbers below are mine unless a source is named.

## Folder

| Path | What |
|---|---|
| `staged/MMOCoreORB/bin/scripts/screenplays/poi/hoth_camps.lua` | B1: 6 sites, 35 static objects, 43 NPCs (new) |
| `staged/.../screenplays/poi/hoth_mynock_den.lua` | B2: spawns the cave and its 23 mynocks by cell number (new) |
| `staged/.../screenplays/screenplays.lua` | dev's current file (sha256 `d8f9b5f7…`, after the caves batch) + 2 include lines in the `poi/` block, alphabetical (changed) |
| `staged/client/terrain/hoth.trn` | B2: MTG's `hoth.trn` + one layer (flatten + mouth exclusion at the den); **for `local_planets.tre`, not for `apply.sh`** |
| `names.tsv` | B3: 22 string keys (stf, key, English, used by) |
| `apply.sh`, `apply-manifest.tsv` | hash-checked (same script as before); `--check` ran clean: 1 to change, 2 new, 0 refused |
| `checks.json`, `luac.txt`, `work/dev_check.txt` | placements with ground heights, terrain patch checks, template checks, luac5.3 passes |
| `tools/stage_batchB.py` (generator), `tools/dev_check.sh` (read-only dev checks), `tools/luac_staged.sh`, `work/screenplays.lua.orig` | |

Apply order: pack `staged/client/terrain/hoth.trn` into `local_planets.tre` (test sessions; the test galaxy reads it too, since `local_planets.tre` is first in its `TreFiles`), then `bash .../Fable-hoth-batchB/apply.sh --check` and `apply.sh`. Without the terrain patch the den screenplay still runs, but the cave mouth is buried in snow (see B2).

## B1. Camps and patrol posts

Bellum's "POIs" (`gen_hoth_pois.py`) are only named map regions; its camps are the NPC rings in `static_spawns/hoth_static_spawns.lua` (troopers at the Imperial outpost, rebels at the Rebel outpost, scavengers and a junk dealer at the Scavenger outpost, salvage techs, two trooper-versus-rebel lines, a raider ring; no props). Re-sited into the batch A zones on flat ground (ground heights from the Core3 height port; 100 m steps at each site under 12 m), each dressed with stock props whose client templates are in `local_planets.tre`'s merged CRC table and whose server templates exist in Core3-dev (`work/dev_check.txt`; the Imperial half-corral has no server template, so the Imperial camp uses four Imperial wall sections instead):

| Site | Centre (ground) | Zone | Props | NPCs (respawn 300 s; vendors 60 s) |
|---|---|---|---|---|
| imperial_forward_camp | 2600, -3900 (33.5 m) | hoth_imperial_zone_east | 4 Imperial walls, tent, crate, campfire, supply pallet | 6 snowtroopers, sergeant, imperial_recruiter |
| rebel_forward_camp | -2800, 1200 (23.3 m) | hoth_rebel_zone_northwest | Rebel corral, 2 Rebel walls, 2 tents, campfire, cot | 6 rebel snow soldiers, sergeant, rebel_recruiter |
| scavenger_camp | -1400, -3300 (10.0 m) | hoth_scavenger_zone_southwest | 2 tents, campfire, spit, cot, 2 stools, pallet, AT-ST wreck | 5 scavengers, junk_dealer |
| raider_camp | -1200, -3600 (12.5 m) | hoth_scavenger_zone_southwest | tent, campfire, 2 crates | 6 scavenger raiders in a ring |
| contested_ground | 2400, 200 (23.5 m) | between the Imperial and Rebel zones | AT-ST wreck, 2 crates | 4 + 1 snowtroopers facing 4 + 1 rebels, 28 m apart |
| salvage_detail | -100, -1960 (0 m) | the outpost's debris field (MTG's Lucky Despot wreck) | none (MTG's debris is there) | 3 salvage techs, 2 snowtroopers |

Style: `spawnSceneObject("hoth", template, x, z, y, 0, heading)` and `spawnMobile(...)`, guarded by `isZoneEnabled("hoth")`, like `screenplays/poi/dathomir_crash_site.lua`. Every object's x, z, y is in `checks.json` → `placed_objects`. Scripted spawns ignore NOSPAWNAREA, so the salvage detail inside the outpost city works like Bellum's outpost rings did. Not done: Bellum's `myswg_vendor` (its own vendor system) and loot containers.

## B2. The mynock den

**Option 1 (staged): spawn the stock ice cave server-side.** Verified offline:
- `DirectorManager::spawnSceneObject` creates the object, sets position and direction and, for a building, calls `building->createCellObjects()` (DirectorManager.cpp:3098); `BuildingObjectImplementation` takes the cell count from the template or the portal layout (`floor meshes - 1`), and Lua has `BuildingObject(p):getCell(n)` (1-based, as `screenplays/tutorial/tutorial.lua:91` uses it) and `getTotalCellNumber()`.
- `object/building/general/cave_06_flatland_s01_ice.iff` exists as a server template in dev and in the merged CRC table; its portal layout `appearance/thm_all_cave_flatland_s01_ice.pob` is stock (`patch_00.tre`): 13 portals, 12 cells including the exterior, so cells 1–11, exactly Bellum's 11 cell ids (6453175–6453185 = building + 1..11). The 23 rows keep their cell-local coordinates and respawn times.
- Site (-2000, -4800) in `hoth_mynock_fields_south`: ground 44.8 m, 100 m steps under 14 m within 250 m, 3.4 km from the outpost, 7.6 km from the caves, heading 0.
- **Terrain:** every stock cave relies on two terrain rules in `hoth.trn` (its "cave entrance" layer: a 9–10 m exclusion disc about 12 m in front of the building, plus the massif's flatten), otherwise the terrain surface runs through the cave mouth. The patch adds one layer to MTG's file with our terrain tools: a feathered flatten disc (r 160 m, smoothstep feather 0.45) to 44.8 m and a 12 m exclusion disc at (-2000, -4788). Checks (`checks.json` → `terrain_patch`): byte round trip identical, Core3-order re-read with the same 22 notes as the original, 13 top layers instead of 12, heights unchanged at the starport pad, 500 m north of it and at cave_03, the den centre and mouth now exactly 44.8 m, 250 m north unchanged. The mouth offset is inferred from the four stock caves' exclusion discs relative to their buildings and headings (three of four fit "12 m ahead of the origin"); the first real-client look should confirm the mouth is open.

**Option 2 (explained, not staged): an outdoor den in the mynock fields.** A `hoth_mynock_den` spawn region (CIRCLE 300 m at the same site, SPAWNAREA, mynock pack + lair) with the broodmother as a single scripted outdoor spawn beside a few stock snow stalagmites (`shared_cave_stalagmite_snow_style_*`, in the CRC table). No client change at all, but the den loses its interior and the 22 cell-local positions; it is the fallback if the cave's mouth or interior looks wrong in the client.

## B3. Names

`names.tsv`: 22 rows, all for `string/en/hoth_region_names.stf` (MTG's file holds only `hothstarport` and `world_spawner`): the ice-cave area, the four cave dens, the mynock den, the rancor grounds, the six B1 sites, the Lucky Despot wreck, and optional names for the batch A areas. The region files still use plain names; switch a region to `@hoth_region_names:<key>` once the key is in `local_planets.tre`. Planetary-map markers need the map-POI region flag, which Core3-dev's `regions.lua` lacks (Bellum added `MAPPOI = 0x020000` with a PlanetManager change); until then named regions show on `/find`-style lookups only. Cave den names are ours, not Bellum's.

## Owner questions

1. Mynock den: stage option 1 (cave + terrain patch in `local_planets.tre`) as proposed, or option 2 (outdoor den, no client change)?
2. Should the six camps and the four cave dens get map names (needs the stf keys plus the MAPPOI flag work)?
3. Recruiters and a junk dealer at wilderness camps, or keep vendors at the starport only?

Untested in Core3 and the client; Claude applies and tests (test galaxy, then a bot visit to each site; `um win` for the den mouth).
