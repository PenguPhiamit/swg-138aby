# C4f / C19 independent review — 14 October 2026

Reviewed by ChatGPT. **Changes requested: two P2 findings.** No live promotion approval is implied. Scope: commits `34d4772a`, `b7f03b0e`, `2f205cd2`, `bea94e7a`, `578861d9`, plus the Hoth archive/test-galaxy tools and generators listed in README.md. Source snapshots and hashes are in `sources/`, `context/`, `tool-snapshot/` and `source-manifest.json`.

## C4f-F1 — P2: lock the spawn counter when collecting diagnostic rows

Locations: `MMOCoreORB/src/server/zone/objects/creature/commands/SpawnStatusCommand.h:69–71` and `ShowSpawnRegionCommand.h:68`; getter in `objects/region/SpawnArea.idl`.

Both commands read the plain `totalSpawnCount` integer without locking the SpawnArea. A spawn task increments it under the area's lock (`SpawnAreaImplementation.cpp:393`); an OBJECTREMOVEDFROMZONE observer decrements it under that lock (`:156`). Running either diagnostic while a lair spawns or despawns therefore introduces a concurrent unsynchronized read/write. This is a C++ data race, beyond merely accepting an approximate count.

The generated getter's `@read` does not supply a read lock: it calls `_getImplementationForRead()` and the implementation getter directly. `ManagedObject::_getImplementationForRead()` only returns `_impl`. The command execution contract locks the requesting creature, not each area. The ManagedReference keeps the area alive but does not synchronize its fields.

Requested fix: obtain each area's diagnostic snapshot under its lock using the project's deadlock-safe locking convention (the creature is already locked), or make the counter atomic and audit the remaining mutable fields. Release that lock before building/sending the SUI. Re-test both commands while spawning/removing lairs. No concurrent runtime failure was deliberately induced during this review.

## C4f-F2 — P2: archive rebuild reads its own Botanist output

Location: `outputs/tools/hoth/hoth_client_build.py:290–303`, also `:324–336`; staging removal at `:348–350`.

`botanist()` reads whichever skills/STF files currently win in the client load order, then asserts that the Botanist root/string keys do not exist. Once the generated `local_planets.tre` is enabled for the client, a subsequent build selects its own previous output and fails at the root assertion. The STF assertions have the same problem if only the skills check is relaxed. The saved client-base copies are written but are not used as the input to this function.

Concrete reproduction: the isolated check redirects output to a temporary folder and supplies the existing staged Botanist skills as the winning input. It raises `AssertionError` with `root_already_present: true` (`offline-results.json`, `botanist_repeat`). Thus a normal future edit/rebuild fails after `main()` has removed and partly rebuilt staging; the existing TRE survives but cannot be refreshed.

Requested fix: select a pinned, unmodified source excluding the generated archive, or deliberately replace the project's existing rows/keys. Build into a fresh temporary staging directory and publish only after all checks pass. Verify two consecutive builds with `local_planets.tre` first in the client's load order, comparing archive contents.

## Checks without additional findings

- Staff command entries both have `characterAbility = admin`; `ObjectControllerImplementation::activateCommand` enforces character ability before execution. The player/ground-zone checks are present. SpawnStatus displays at most 40 rows; ShowSpawnRegion displays at most 20 lair entries per active area. Its outer area count is not explicitly bounded, but no concrete excessive-area case was established. ManagedReferences preserve object lifetime through the casts.
- The 25 loot items resolve through the recorded template inventory. Group weights total 10,000,000: common 4 items, rare 3, vehicles 18. Reconstruction of all 20 changed mobile files preserved their previous loot entries, and a second `add_drop` pass was unchanged. The two added deeds use Core3's VEHICLEDEED fields and match VehicleDeedTemplate/VehicleDeedImplementation's expected control-device and generated-object paths. This does not prove every vehicle can be unpacked or every decoration rendered in game.
- The object CRC table contains 29,358 names, with no CRC collisions or name/hash mismatches. Stock/MTG inputs round-trip exactly and the result matches staging. The reviewed Core3 reader does not impose a 16-bit row-count limit. A real pre-CU client load remains required; source/data inspection alone cannot establish all client limits.
- The merged resource table has 777 rows, including 52 Hoth types. Applying Core3's carried-forward class/container/name logic produced **no effective-field changes to the 725 stock rows**. New rows inherit the expected containers and naming classes. Core3 iterates table rows and does not use the INDEX field as identity. Ancestor type-count increases are recorded in the evidence; the reviewed resource-manager tree exposes these fields but a read-only search found no consumers of `getMintype`/`getMaxtype` outside their definitions. Do not infer spawn-pool balance from these counts alone. Hoth surveying/harvesting and resource shifts remain gameplay checks.
- `bea94e7a` rejects either endpoint outside the floor mesh before invoking `getFloorPath`, closing the earlier null/null same-triangle counterexample in source. Other indoor transitions still need runtime validation.
- Botanist rows use the stock schema/defaults, with the parent before Novice; trainer registration/conversation/spawn follow existing formats. Root plus Novice is intentionally a feasibility slice. A GRAPH_TYPE 4 browser with no remaining boxes is **unverified**, not accepted as a completed profession: open it in the real client, train Novice and relog before expanding or promoting.
- `test_galaxy.py` changes append archive precedence and Hoth only to the disposable copy, conditional on the local archive existing. This review did not start/stop a galaxy or test that path by executing it.

## Evidence and remaining gates

`review_checks.py` performs isolated archive/data checks and records `offline-results.json`; protected staging/TRE hashes are compared before and after. It does not build server C++, run client UI, drive bots or restart anything. No `/opt/swg` files were edited. Source/template compatibility is not a substitute for in-game verification. Before live promotion: fix/re-review F1/F2, complete the named gameplay checks, retain Bellum/MTG credits and separate art provenance, and obtain the owner's explicit approval.

C4e-F1 is resolved in the leash proof helper; C4e-F2 (straight-line scene/connection cancellation) remains outside these five commits and open before promotion. Supporting [source manifest](source-manifest.json), [offline results](offline-results.json), and [isolated checker](review_checks.py) are saved here. No new in-game verification was run by this review.

## Follow-up review — 14 Oct, after Claude's fixes

- **F1 resolved in source** by dev `23014f39`: both commands cross-lock each SpawnArea with the already-locked creature while reading. Lock scope ends before SUI dispatch. Claude reports a clean build; concurrent in-game diagnostics were not re-run by ChatGPT.
- **F2 resolved for the reproduced input failure** by h commit `f0b192e`: lookup excludes local_planets.tre, and main writes fresh staging/archive copies before verification/publication. `check-fixes.py` independently simulated our archive first and selected patch_14_00; two isolated Botanist builds were identical to installed staging and left staging unchanged (`fixed-results.json`). Claude's two complete archive builds are author evidence; ChatGPT did not run main/publish. Publication is still two filesystem operations rather than a transactional pair, but build/verification failure now preserves the prior output.
- Reviewed by ChatGPT. Original findings retained above as history; gameplay and owner live-approval gates remain.
