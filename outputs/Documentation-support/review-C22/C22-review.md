# C22 independent review - 14 October 2026

Reviewed by ChatGPT. **Changes requested: 2 P2 findings and 1 P3; no P1 established.** This is a source/data review, not live-promotion approval. No `/opt/swg` edits, builds, restarts, downloads, bot commands, or client control were performed.

## Scope and evidence

| Repository | Reviewed commits |
|---|---|
| `/opt/swg/Core3-dev` | `c5f1ae06` ice caves; `69eb77fe` area spawners and rancor; `de1b679a` camps; `23014f39` spawn-area diagnostic locks; `90f60a81` movement scene/connection guard |
| Local `h` | `f0b192e` archive-builder fix |

Commit diffs and relevant source files were read with `git -C /opt/swg/Core3-dev show` as `swgemu`. Content registration context is pinned to `de1b679a`; movement and diagnostic context uses its respective reviewed commit. Later quest, den, species and NPC-static fixes are outside this review. Read the three Fable staging READMEs, generators and verification records, central credits, and the local Bellum reference source/licence. Existing engine3 locking and quaternion implementations were inspected read-only.

[check_c22.py](check_c22.py) reproduces the geometry, registration, appearance-chain and isolated archive checks; [offline-results.json](offline-results.json) records measurements and asset hashes without copying assets. Run from Windows: `python -I outputs/Documentation-support/review-C22/check_c22.py`. Its synthetic archive-failure fixture writes only into an OS temporary directory. Source reasoning about concurrency was not exercised in a running client/server.

## C22-F1 - P2: fight cancellation does not guard the attack dispatch

**Location:** `MMOCoreORB/src/client/agent/AgentControl.cpp:1147` in `90f60a81`; related `:1117`, `:1123`, `:1152`, `:1172`.

The new captured `scene` is checked only inside `moveTo`, and `fight` only handles its `scene_changed` return. The per-iteration target snapshot and the subsequent `sendCommand("attack", ...)` do not compare scene generation or connection state under the same lock as dispatch.

**Concrete failure:** an in-range target is sampled at lines 1123-1132; `onStartScene` runs after that block and before line 1152. Since distance is at most 3.5 m, there is no approach and no generation check: the old fight sends an attack using the new scene's `self`. An old-scene target may be rejected by the server; if the same target is present after a same-zone scene reload, the old request can resume attacking it. The same gap exists between a successful approach and attack dispatch. Clearing `world` on scene start does not invalidate the snapshot already copied into local variables.

A dropped connection is also not propagated: when an out-of-range approach returns `ok=false, error="not connected to the zone server"`, line 1147 ignores that response because it has no `scene_changed` flag. The fight still attempts the attack, increments `attacks`, and repeats against its retained target until timeout. Thus the added movement guard stops position updates, but does not cancel the enclosing reflex or make its attack count reliable.

**Fix:** under `worldMutex`, recheck the captured generation, connection and current target immediately before every attack, and hold that lock through dispatch. Stop/return the failure when the approach fails, preserving the reason. This is a remaining hole in the targeted C4e-F2 fix, not evidence that the patch introduced the older unguarded attack path. Verify cancellation both with an in-range target and while approaching, including disconnection; no further attack should be counted or sent after cancellation.

## C22-F2 - P2: rancor palette is selected on a non-customizable appearance

**Location:** `MMOCoreORB/bin/scripts/mobile/hoth/hoth_glacial_rancor.lua:39` in `69eb77fe` (`templates`), paired with `:40` (`hues`).

The template uses `object/mobile/rancor.iff` with `hues = {15}`. That server object derives from `shared_rancor`, whose client chain is:

`shared_rancor.iff` -> `rancor.sat` -> `rancor.lmg` -> `rancor_l0.mgn` -> `shader/rancor_asb13.sht`.

The shader is a static `SSHT`, using `texture/rancor.dds`, with no `palette/creature_rancor.pal` customization. The separate stock hue chain (`shared_rancor_hue.iff` -> `rancor_hue.sat` -> `rancor_hue.lmg` -> `rancor_hue_l0.mgn` -> `rancor_hue_hcsb21.sht`) ends in `CSHD` and explicitly binds `index_color_1` to that palette. This is confirmed from the owner's existing client data; both chain hashes are in the offline results.

**Concrete failure:** spawning the registered boss with the reviewed template cannot produce the promised pale palette-15 skin: it retains the static rancor appearance. Measuring the palette colour alone did not establish that this chosen body uses it. It is currently latent because the boss is registered but not wired to a spawn.

**Fix:** use the existing `object/mobile/rancor_hue.iff` server template, which derives from `object_mobile_shared_rancor_hue` (`object/mobile/rancor_hue.lua:44`), then confirm hue 15 in the real client. No new art is required. Shape/scale/rendering remain untested in-game.

## C22-F3 - P3: camp prop headings use degrees where the binding takes radians

**Location:** `MMOCoreORB/bin/scripts/screenplays/poi/hoth_camps.lua:27` in `de1b679a`; also nonzero headings at `:28`, `:36`, `:38`, `:40`, `:41`, `:44`, `:48`, `:50`, `:55`.

The seven-argument `spawnSceneObject(zone, template, x, z, y, parent, heading)` passes its last value directly into `Quaternion::setHeadingDirection` (`DirectorManager.cpp:3066`). That function takes radians (engine3 `engine/util/u3d/Quaternion.h:354`). Conversely, `spawnMobile` explicitly converts its heading from degrees (`DirectorManager.cpp:2715`). The staging generator treated both interfaces alike.

**Concrete failure:** the Imperial tent at line 27 receives 180 radians, which normalizes to approximately 233.24 degrees instead of the intended 180 degrees. The Rebel cot's 90 becomes approximately 116.62 degrees, and the crate's 30 becomes approximately 278.87 degrees. Ten props consequently face the wrong direction. Placement heights are correct; collision obstruction was not established, so this is P3 rather than a claimed navigation blocker.

**Fix:** convert scene-object headings to radians, or use the ten-argument quaternion form. Keep mobile headings in degrees. Apply the correction to the generator as well as the integrated screenplay, then visually check the camps.

## Checks without additional findings

### Spawn arguments, cells and terrain

- Every reviewed `spawnMobile` call has eight arguments in the binding's `zone, template, respawn, x, z, y, heading-degrees, parent` order; all 43 camp mobiles use world parent 0. Every camp prop has the valid seven-argument call shape; only its heading units are wrong.
- Independently reread MTG's `snapshot/hoth.ws`: all 129 cave spawns use cells in the four expected buildings. There are 62 distinct used cells; none references the missing fifth building. Cave totals are 23/23/23/60. Templates and parent-cell assignments resolve.
- Extended the staging check to the actual cave portal layouts and floor meshes. Parsed the `CELS/CELL/DATA` floor references in cell-index order and `FLOR/VERT/TRIS` using Core3's `CellProperty.cpp` and `FloorMesh.cpp` layouts. Every spawn's horizontal point lies inside a triangle in its assigned cell, and its height differs by at most **0.005933 m** from that triangle. Parsed IFFs round-trip byte-identically and triangle indices/counts validate. This closes the staging report's skipped floor-data check; it does not prove every cave doorway or AI route works in-game.
- Recomputed all camp point heights with the existing Core3 terrain-evaluator port: maximum error **0.049874 m**, consistent with one-decimal rounding; no point is outside the playable edges. The actual screenplay has **31 props and 43 mobiles**, rather than the README/commit message's 35 props.
- All eight area circles clear the 7640 m no-spawn edge boundary, the outpost's 300 m no-build disc, and the caves' 450 m no-build disc. All camp sites except the deliberate salvage detail are outside those discs. The salvage detail is inside the outpost city/no-build zone by design; `spawnMobile` does not call the random-spawn permission check, so that is not a rejected spawn.
- All 22 distinct used mobile names and 11 used lair names are registered in the pinned content context. The six new groups are registered/included, all eight region references resolve, and the Hoth lairs have their include entries. No nonexistent group/lair name was found.

### Region overlaps that affect behavior

Four pairs of area circles overlap. The numbers below are penetration along their centre line, not overlap area:

| Pair | Overlap depth |
|---|---:|
| West tauntaun plains / northwest Rebel zone | 450.49 m |
| West tauntaun plains / southwest scavenger zone | 432.84 m |
| East tauntaun plains / east Imperial zone | 346.28 m |
| South mynock fields / southwest scavenger zone | 423.69 m |

The overlaps let both groups attempt spawning around players in the shared region; there is no priority-based selection. In addition, every new circle has only `SPAWNAREA`, so the world spawner remains eligible inside it. `PlanetManagerImplementation.cpp:1338` excludes world spawning only for `NOWORLDSPAWNAREA`; ordinary `SPAWNAREA` does not imply that flag. Therefore the comment at `hoth_regions.lua:21` describing a fallback "everywhere else" is not the actual behavior: e.g. the world group can supply Rebels/wampas inside the Imperial area too.

This matters for theme and local density, but the staging notes explicitly disclose additive limits (1024 + 384 = 1408), with owner density decisions still open. No exclusive-biome requirement or concrete broken mission was supplied, so these are reported as design/acceptance decisions rather than an invented fourth defect. If exclusive area themes are intended, add `NOWORLDSPAWNAREA` to those circles and resolve the four shared boundaries deliberately. Actual spawn-rate/density acceptance remains untested.

### Lock order and fix disposition

- **C4f-F1 / `23014f39`: resolved in source.** Both commands use `Locker(area, creature)` while reading mutable counters/lists (`SpawnStatusCommand.h:73`, `ShowSpawnRegionCommand.h:68`). The command queue holds the creature before activation (`CommandQueue.cpp:182`, `:232`). Engine3's two-object `Locker` calls the cross-lock overload; `ReadWriteLock::wlock(ReadWriteLock*)` uses try-lock/release/reacquire of the cross lock on contention (`ReadWriteLock.cpp:230-266`), rather than blocking forever while retaining the creature. Each area's RAII scope ends before SUI construction/send, with no nested area lock held across iterations. No new lock-order cycle was established. Concurrent in-game spawn/despawn diagnostics remain untested here.
- **C4e-F2 / `90f60a81`: straight-line movement fixed in source, enclosing fight incomplete (F1).** `moveTo` performs generation/connection checks, position update and transform send under `worldMutex`, and guards its final stop by generation. Recursive locking in `groundNear` is compatible with the declared `recursive_mutex`. The send path goes through `ZoneClient::sendMessage`/BaseClient; incoming messages are handed to `ZoneMessageProcessorTask`, whose handler runs without retaining the network client lock while waiting for `worldMutex`. Thus no opposite client-lock -> world-lock cycle was established. This is static lock-path analysis, not a concurrency stress test.
- **C4f-F2 / `f0b192e`: reproduced input failure resolved.** With `local_planets.tre` artificially first in the load order, the pinned `winning()` selected `patch_14_00.tre` for skills. Two isolated Botanist generations were identical and matched installed staging; protected staging hashes did not change. A deliberately mismatched synthetic archive exercised the actual `main()` failure branch: returned 1 and preserved both previous stage and archive. No real complete archive was packed/published. Publication still consists of separate stage-directory and archive operations, so interruption/I/O failure during publication is not a transactional pair; this limitation was already recorded in C4f's follow-up and is not reclassified as a new regression.

## Provenance, credits and remaining gates

Bellum's permitted source is the local reference of [BellumGero-Live](https://github.com/Miphstoe/BellumGero-Live), revision `1f4438a129c0e07d05871fccfb2ed30b21da9539`, with AGPL-3.0 in its `COPYING`. The cave file retains source URL, revision, licence, adaptation date and a specific change list. Spawn-group headers identify the Bellum-derived lairs/weights; the camp header identifies its Bellum static-spawn layout origin and the re-siting/prop changes. No excluded-source import or new client-art payload was found in these six diffs.

The rancor uses existing stock references, a new name/text, stock-boss-derived stats and attacks, and project loot groups; it does not import Bellum's missing exotic body, per-player reward code, custom art, or original boss name. Its level 400 is expressly inherited from Bellum, so "clean-room" should be understood here as a source-informed replacement using existing permitted materials, not a certified independent two-team clean-room process. No extra rights to redistribute stock/MTG art are inferred from the server-code licence. F2 concerns technical appearance selection, not permission.

Central `Community-content/CREDITS-and-sources.txt` already pins Bellum and retains the licence/source notice, but its "Used for" list predates the cave/camp additions and says the rancor is not yet ported. Extend that inventory when addressing the findings; preserve the headers and licence with any shared source. This review and its source credits remain local; any publication needs the AGENTS.md name-redaction/licence-credit check and the owner's explicit authorization. No legal-compliance certification or outbound post is implied.

Next: Claude addresses F1-F3 in the owned slices and requests re-review. Retain the optional den/boss/encounter choices and owner gates; this report rejects none of those concepts. Real-client camp orientation/rancor appearance, cave traversal/AI, regional spawn composition, and cancellation/diagnostic concurrency still require the authorized gameplay checks. No live merge, deployment or restart is approved by this review.
