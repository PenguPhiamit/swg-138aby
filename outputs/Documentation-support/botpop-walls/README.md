# BotPop bots walking through walls: cause and fix

16 Oct 2026, Claude (side session). The owner reported (about 7 PM) that many bots were running through walls. This folder holds the cause and a patch, `botpop-walls.patch`, against `/opt/swg/Core3-dev` HEAD `c5d713b8`.

**Status: untested in game.** `git apply --check` passes against HEAD (run in WSL as root, read-only). A syntax-only clang compile of `CommandConfigManager.cpp` passes too. It used the dev build's own flags from `build/dev/compile_commands.json`, with the patched headers in an overlay in `/tmp`. Nothing under `/opt/swg` was edited.

## Cause

BotPop moves a bot by setting its position one step at a time along straight lines. Only one of its movement paths asks the engine's pathfinder, and even that one gets a straight line back whenever the leg is long.

1. **Hunters and explorers walk one straight leg, hundreds or thousands of metres long.**
   - Hunters: `BotPopLaunchBrain.h:813-823` (`launchHunt`) pushes one goal, `cityRadius + 40 + up to huntRadius (3,000 m)` from the city centre, into `state->path`.
   - Explorers: `BotPopLaunchBrain.h:1682-1708` (`launchExplore`) does the same with a goal anywhere on the planet.
   - `walk()` (`BotPopManager.h:545-579`) then moves the bot straight at that point. It sets only the height (`floorNear`), so the bot crosses every building, wall and city structure between its start in town and the goal.
   - Hunters are most of the launch population, and every one of them starts in a city and walks out, so this is most of what the owner saw.
2. **Every chase or approach is a straight step.** `stepToward` (`BotPopLaunchBrain.h:37-60`) moves straight at its target with no collision check. It has nine callers:
   - the fight target (`:556`) and the corpse (`:575`);
   - back to the town centre to rest (`:658`), and medics and entertainers going back to the centre (`:838`, `:971`);
   - a medic's patient (`:877`);
   - the mission point (`:1479`), the lair (`:1533`) and the mission terminal (`:1552`). The terminal is in town, so bots walk through buildings to reach it.
3. **Why the existing pathfinder call doesn't help with long legs.** `startWalk` (`BotPopManager.h:510-541`, the wander) does call `PathFinderManager::findPath`, and its short in-town legs do go round buildings. But `findPathFromWorldToWorld` looks for navmeshes only at the **midpoint** of the leg (`PathFinderManager.cpp:339`, `getInRangeNavMeshes(mid…)`). `GroundZoneImplementation.cpp:646` makes that a point query on the area tree. A leg from inside a city to 500 m+ outside has its midpoint in open country, finds no mesh, and `PathFinderManager.cpp:461-465` returns the straight line from start to end. So switching the hunters to plain `findPath` would not have fixed them.

## Fix (the patch)

The fix reuses the engine's own `PathFinderManager::findPath` (Recast navmesh, the same call AI uses) and adds nothing new to the engine.

- **`planRoute`** (new, `BotPopLaunchBrain.h`) handles the midpoint problem:
  - It looks up the navmesh at each **end** of the leg: two area-tree point queries.
  - If neither end is in a navmesh, it returns the straight line as before, with no other work.
  - If both ends are in the same city, it makes one `findPath`. The midpoint is then inside the mesh.
  - Otherwise each end that is in a city gets its own leg, from that end to 2 m inside the mesh's edge. The edge is found by halving the line 12 times against `NavArea::containsPoint`. That leg's midpoint is inside the mesh, so `findPath` routes it round the buildings. The open ground in between stays straight, as before.
- **`startRoute`** replaces the single-point legs of hunters and explorers. Their legs now leave town round the buildings.
- **`chaseToward`** replaces the nine `stepToward` calls and keeps the same contract (it returns true within `stopAt`).
  - It follows a `planRoute` route and aims the last waypoint at the target's live position.
  - It plans again only when the target has moved 4 m or a quarter of the remaining distance. That is the AiAgent rule: `findNextPosition` re-plans a follow at 4 m, `AiAgentImplementation.cpp:2780-2784`.
  - It plans at most every 2 s, unless the target jumps more than 30 m.
- **Rest target:** `launchRest` no longer adds ±10 m of random jitter to the town centre every step. A new target every step would force a re-plan every 2 s. Bots still stop 25 m out, on whichever side they came from.
- **Budget and stats:**
  - `ROUTES_PER_PASS = 200` navmesh routes per pass (one pass a second) across all workers.
  - When the budget is spent, a hunter or explorer waits one step before leaving, and a chase steps straight for up to 2 s.
  - The 60-second stats line gains `routes N (M deferred)`.

Unchanged: the wander (`startWalk`), travel and teleports, and the movement of the bot itself (`move`, `floorNear`). Bots still don't enter building interiors; `startWalk` already stops routes at cells, and `planRoute` drops cell points.

## CPU cost

| Case | Cost per call | How often |
|---|---|---|
| Neither end in a navmesh (open country: most hunting and exploring, every outdoor chase) | 2 `getInRangeNavMeshes` point queries (zone read lock + quadtree), a few µs | Once per leg; once per 2 s per chasing bot |
| An end in a city | 1-2 `findPath`: `findNearestPoly` ×2, A* over at most 4,096 nodes (`MAX_QUERY_NODES`, `PathFinderManager.cpp:25`), `findStraightPath`, plus one floor ray per mesh | Once per hunter or explorer leg leaving town; a chase in town re-plans at most every 2 s, only while the target moves |

- **Estimate (not measured):**
  - A city `findPath` is roughly 0.1-1 ms in an optimised build and several times that in Debug.
  - With the 200-route cap, the worst case is about 0.2 s of CPU per second in RelWithDebInfo, or about 0.5-1 s per second in Debug.
  - That is spread over the workers that already run the steps.
  - In steady play it should be far lower. A hunter leaves town once per hunt leg (minutes), and only bots in town (medics, entertainers, terminal and rest trips) plan routes there.
- **Measure it** on the galaxy with the existing stats line:
  - Compare `steps X ms per second across workers` and `slowest chunk` before and after.
  - Read `routes N (M deferred)` from the new field.
  - If `deferred` stays high after the first minutes, the cap is binding. Raise `ROUTES_PER_PASS` if steps have headroom.

## How to test on the test galaxy (lock holder only)

1. After the optimised build has finished, apply the patch in `/opt/swg/Core3-dev` as swgemu, then rebuild:
   ```
   runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/botpop-walls/botpop-walls.patch
   ```
   Then run `dev_build.py`, or `--release` for the devrel build.
2. Start the galaxy with `--dev-server` and launch a small population in one walled or dense city first, for example `botpop launch 50 <planet>`. Watch from a client at the city edge: hunters should leave along the streets and through the gates, not through buildings.
3. Watch medics and entertainers going back to the centre, and hunters walking to the mission terminal. They should go round buildings.
4. Check the server log's BotPop stats line for `routes`, `deferred`, `steps … ms per second` and `slowest chunk`. Then do the full 1,700-bot run and compare against the last run's numbers.
5. `no path` counts only the wander's failures, as before. It should not change.

## Risks and limits

- **Cities without a loaded navmesh** (`isNavMeshLoaded()` false) still get straight lines. So do player cities before their mesh is built. The same applies to buildings outside any city mesh, such as lone outposts or POIs, and to the open-ground part of a leg that clips another town's edge.
- **Paths in a city can be partial.** `findPathFromWorldToWorld` passes `allowPartial = true`, so if Recast can't reach the edge point, the leg ends early and the rest is straight. That is rare at a city edge.
- **Chases inside a city follow the route as planned for up to 2 s** while the target moves less than 4 m or a quarter of the distance. In a corner case the bot heads for an old waypoint briefly.
- **Explorers count a square as visited** (`exploreVisits`) even when the route is deferred and they pick again the next step. This only matters while the cap binds, and it skews the census slightly.
- **Thread safety.** `findPath` already runs from many AI threads; the Recast query object is thread-local (`PathFinderManager::getNavQuery`). `planRoute` runs inside the bot's step with only the bot locked, as AI pathing does.
- **Untested in game.** A walk-through in the client (step 2) is the real check.

## Follow-up: bots sunk to the waist under raised floors (Claude, 16 Oct 2026, 8:05 PM)

- **Owner, run 14, 7:59 PM** (a tell to the test bot): "I JUST SAW BOT RUN THROUGH THE FLOOR AT WAIST HEIGHT".
  - The owner had just been round the Mos Eisley starport and taken the shuttle to Bestine.
- **Cause.** `floorNear` set a walking bot's height to the floor **nearest its current height**. A bot on the ground that walks under a raised plaza or platform stays on the ground, because the terrain is nearer than the platform. Its body then shows through the platform surface, from the waist up.
  - This predates the walls fix: `walk()` and `stepToward` both had it.
  - The walls fix sends more bots along streets and plazas, so the owner may simply see it more often.
- **Fix** (dev `5bf55669`; copy: `botpop-stepup.patch`):
  - `floorNear` now takes the **highest floor at most `stepUp` above** the current height, and the terrain when none qualifies.
  - `stepUpFor(length)` is 0.6 × the step's length, kept between 1.2 and 2.5 m. That climbs kerbs, plazas, ramps and stairs, but not roofs or upper storeys.
  - Walking off an edge still drops the bot to the next floor or the terrain.
- **Risk:** a low roof that has floor collision, less than 2.5 m above a bot taking a long step, could be climbed. That is rare: canopies and tents are usually higher, and usually have no floor mesh.
- **Status:** built into the optimised core3; it starts at the next test-galaxy restart. Check: watch bots cross the Mos Eisley starport plaza and the Bestine shuttleport.
