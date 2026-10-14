# C4e: re-review of the C4d fixes, find/tell, and Hoth v1

Three dev commits after `5aadc8b9` (branch `dev`, LF endings), one patch each. `files/` holds the full current versions of the changed C++ files and `hoth_regions.lua`.

| Patch | Commit | What |
|---|---|---|
| 0001 | `5b2a858f` | Hoth v1 server scripts: planet entry, travel point, regions (test galaxy only) |
| 0002 | `421adb15` | `/leash`: answers C4d F2 (re-check after the cross-lock) and F1 (move only along a proved route prefix, with the reason in the warning) |
| 0003 | `9ac7cdcd` | Agent body: `find` and `tell`; C4d F3 (a scene generation counter, so replies or walks from before a zone change return `scene_changed`); `/agentpath path` carries the leash's proof |

**Effort: High** (C4-style code review), GPT-6.1 Sol.

## What to check

1. **F2 (patch 0002):** after `Locker clocker(leader, follower)`, is the re-check of the pending task and the leader's online state enough, or can a tick still act after cancellation? Anything else read before the lock that must be read again?
2. **F1 (patch 0002):** `walkable()`, `whyNotWalkable()`, `onNavMesh()` and `onFloor()`. Is the proof sound? Outdoors: both ends within 2.5 m of the mesh and `getRecastPath` succeeds. Same cell: `getFloorPath` returns -1 or 0. Doorway: same building and 12 m at most. Does unstick only ever move to the proved prefix? **Known open bug:** some outdoor second hops are refused with "no navmesh route between the ends" where a path exists (Dorn, 11.7 m). Please look for the cause too: the recast call's arguments, `allowPartial`, or the mesh area chosen.
3. **F3 (patch 0003):** `sceneGeneration` in AgentControl. Are helper replies and walk steps from an old scene always discarded? Is sending under `worldMutex` safe, given that packet handlers run on task threads without the client lock?
4. **find (patch 0003, `AgentPathCommand.h`):** bot accounts only (`Core3.AgentAccounts`)? Bounded work: radius cap, 30 results, de-duplication via `seen`? Does any path leak objects a player couldn't know about? It reports buildings' contents, which is fine for bots on the test galaxy, but say if it should be narrower before any live use.
5. **tell:** confirm it can't send as another character, and that it's limited to bot accounts.
6. **Hoth (patch 0001):** the Lua matches the current Core3 region and travel-point schema. `hoth_regions.lua` is loaded only where `ZonesEnabled` lists hoth.

## Evidence (test galaxy, Claude)

- **Hoth:** `Bot-reports/Esk/20261014-021846-esk-hoth.json`, 21/21 checks: travel both ways, the starport's objects, the terrain read. See also `Documentation-support/hoth-port-log.md`.
- **find:** used by every starport leg in `esk-hoth.py` (terminals indoors, with cell and local position).
- **Leash:** the earlier runs are in `Bot-reports/Dorn` (9/10, with the 11.7 m refusal above).

Not exercised yet: a planet change mid-leash; scene change during a long walk (F3) on purpose; `tell` to an offline name. Live deploy needs this review plus the owner's OK.
