# BotPop navigation: options for making bots move like players

16 Oct 2026, about 8:30 PM, Claude (side session). This answers the owner's request to "research ways to have the bots actually navigate better".

- Code read: `/opt/swg/Core3-dev` HEAD `5bf55669`, read-only, with the walls patch (`724809fa`) and the step-up fix (`5bf55669`) applied.
- Every file:line below is at that commit.
- Draft first step: `botpop-lanes.patch`. It passes `git apply --check` against `5bf55669`, and a syntax-only clang compile with the dev build's flags passes too. It is **untested in game**.

## Where things stand

- **Bots move by setting their position.** BotPop sets each bot's position step by step: `move()`, `BotPopManager.h:497-512`. It never runs Core3's player movement validation, so a bot can't get physically stuck. It goes exactly where its path says.
- **Paths:**
  - A navmesh path inside cities, and in the POIs that have a mesh. This comes from `planRoute` / `chaseToward`, which call `PathFinderManager::findPath`.
  - Straight lines everywhere else.
- **Measured CPU (run 14, 1,700 bots):** 1,158 routes a minute, 0 deferred, 0.76 CPU-seconds per second for all bot steps. So there is headroom for a little more pathing, but not for a per-step collision check on every bot.
- **Which areas have navmeshes:**
  - Every city region: `CityRegionImplementation.cpp:523-640`, named `<planet>_city_<name>`, built at startup on the `NavMeshBuild` queue (`GroundZoneImplementation.cpp:818`).
  - Player cities, when the city hall is placed: `PlaceCityHallComponent.cpp:75`.
  - GCW bases: `StructureObjectImplementation.cpp:216`.
  - A fixed list of POIs per planet, from the `navAreas` tables in `bin/scripts/managers/planet/planet_manager.lua`, for example lines 86-93 and 123-131. These are loaded by `PlanetManagerImplementation.cpp:452-500`.
  - The test galaxy's log of 15 Oct shows how many areas loaded per planet, cities and POIs together: tatooine 15, naboo 16, rori 13, dathomir 28, lok 8, endor 8, corellia 6, talus 3, dantooine 3.
  - Meshes are built for a 0.5 m agent radius and a 0.75 m climb: `RecastTileBuilder.cpp:53-70`.
- **Core3's own NPCs are no better outdoors.** `AiAgentImplementation::findNextPosition` (`:2765-2800`) uses the same `findPath`. Outside a navmesh, `findPathFromWorldToWorld` returns the start and end points only (`PathFinderManager.cpp:461-465`). So creatures and NPCs also walk straight through anything that has no mesh.
- **Rocks and trees aren't solid on the server.** Terrain flora is parsed by the terrain code (`src/terrain/…Flora*`), but `CollisionManager` never uses it. No grep hit for flora in `managers/collision/`. A player sees NPCs walk through those rocks too. The flora affectors mark many of them non-collidable anyway (`AffectorNoncollideFloraConstant.h`).

## Options

Ranked by how much better bots look to a watching player, against CPU, effort and risk.

### 1. Spacing: lanes and queues (draft patch included)

**What the player sees now:**
- Since the walls patch, bots that share a navmesh route follow exactly the same polyline. Two hunters leaving town by the same street walk inside each other in a conga line.
- Every launch bot in a city uses that city's one mission terminal (`terminalByCity`, `BotPopManager.h` around line 150). All of them stop 3 m from it, on the side they came from, so they stack on one spot.
- Bots returning to the centre stop at the same 25 or 30 m mark along their route, so the ones that came by the same route end up on the same spot.

**The fix (`botpop-lanes.patch`):**
- **Lanes:** each bot has a fixed lane of -0.4 to 0.4 m, derived from its object ID (`laneOf`). From the second waypoint of a route on, it walks that far to the right of the route line, in both `walk()` and `chaseToward`. The 0.4 m limit is below the 0.5 m the meshes keep from walls, so bodies don't go into walls.
- **Queues:** a fixed spacing (`spacingOf`) staggers where bots stop.
  - At the terminal: 3, 4 or 5 m out, which reads as a queue. 5 m stays inside the 6 m that `handleMissionListRequest` allows (`MissionManagerImplementation.cpp:170`).
  - At the centre: 25-33 m for resting, 30-38 m for medics and entertainers.
  - All of these stay below the distances that trigger the return trip: 40, 60 and 45 m.

**Cost:** a few multiplications per step and no extra pathing. **Effort:** done; 98 lines of patch. **Risk:** low.
- The first leg of a route has no offset, because there is no previous waypoint to offset from.
- On a 1 m wide navmesh gap, a 0.4 m lane could brush a wall edge.

### 2. Navmeshes the open-ground part of a leg crosses

`planRoute` checks for meshes only at the two ends of a leg. A hunter's or explorer's 3-8 km leg can cross a POI that has a mesh, or another town, and then go straight through its buildings.

**Fix:**
- Sample the straight line every 25 m with `Zone::getInRangeNavMeshes`, the same point query planRoute already uses.
- For each mesh the line enters and leaves, add an entry leg and an exit leg, the same way the end legs work now.
- Enumerating meshes directly isn't possible without an IDL change: `PlanetManager` exposes only `getNavArea(name)`, at `PlanetManager.idl:168-177`. Sampling avoids that change.

**Cost:** up to 320 point queries per 8 km leg (explorers), 120 per 3 km hunter leg; each is a few µs. That is roughly 10 ms per second at run 14's route rate. A crossed mesh adds two `findPath` calls, under the existing `ROUTES_PER_PASS` budget.

**Effort:** small, about 40 lines in `planRoute`. **Risk:** low. A line that only clips the edge of a mesh between two samples is missed, as it is today.

### 3. Partial paths and unreachable goals in cities

`findPathFromWorldToWorld` allows partial paths (`PathFinderManager.cpp:473-477`). When Recast can't reach the goal, the route ends at the nearest reachable polygon (`getRecastPath`, around `:285-295`). The bot then walks the rest in a straight line, through whatever is in the way. Wander goals come from `getSpawnPointInArea` with `checkPath=false` (`BotPopManager.h:524`), so some are unreachable, for example inside a walled yard.

**Fix:**
- In `planRoute`, when the last route point is more than 3 m from a goal inside a mesh, end the route there, or drop it and pick another goal.
- In `startWalk`, pass `checkPath=true`. That makes `getSpawnPointInArea` test the path itself (`PathFinderManager.cpp:1285-1361`), though it costs a Recast query per candidate.

**Cost:** none for the first part; one extra query per wander for the second. **Effort:** small. **Risk:** low.

### 4. More POIs with navmeshes

Core3 already supports two ways of adding meshes:
- **The `navAreas` tables** in `planet_manager.lua`: name, x, y, radius. Meshes are built at startup and kept in `navareas.db`.
- **A per-template config key**, `Core3.StructureManager.CreateNavMesh.<template path>` (`StructureObjectImplementation.cpp:219-223`). It meshes every structure of that template.

**To do:**
- Add the POIs where bots are seen crossing buildings: outposts, camps, the bigger ruins.
- `botpop-positions.json` and the explorer census can show where bots actually walk, which tells us which POIs matter.

**Cost:** startup only. Each mesh is built once on the `MaxNavMeshJobs = 6` queue (`bin/conf/config.lua:238`) and then cached in `navareas.db`; runtime cost is the same as option 2. **Effort:** data work (coordinates and radii per POI); Lua only. **Risk:** low.
- The change touches world data, so it goes through the usual review.
- Startup is slower on the first build.
- Live NPC pathing changes there too, which mostly improves it.

### 5. Going into buildings: cantinas, the starport, the medical centre

Bots never enter interiors: `startWalk` cuts routes at the first cell point (`BotPopManager.h:536-544`), and `planRoute` drops cell points.

**What Core3 already has:**
- `findPath` handles world-to-cell, cell-to-world and cell-to-cell paths over the building's portal layout and floor meshes: `PathFinderManager.cpp:479`, `:740`, `:942`, `:1173`.
- AiAgent moves into a cell by calling `updateZoneWithParent(cell…)` when the next point has a cell (`AiAgentImplementation.cpp:2551-2560`).

**What BotPop would need:**
- `move()` would need a parent cell.
- It would also need cell-local coordinates and the `updateZoneWithParent` / `transferObject` step.
- Walking out would need the reverse.

**What players would see:** entertainers dancing in the cantina, medics in the med centre, crowds at the starport. That is the biggest step towards bots that read as players.

**Cost:** cell paths are A* over small floor graphs, which is cheap. Each cell entry locks the building to transfer the bot.

**Effort:** medium to large, with testing in the client.

**Risk:** medium.
- Cell transfers need the stock lock order; the helper droid hit the same issue (C55 F1).
- Bots that die or log out inside a building need handling.
- `floorNear` must use the cell floor (`CollisionManager::getCellFloorCollision`, `:324`), not the world floor.

### 6. Small player-like touches

- **Arrivals:** a bot that reaches the end of a wander already idles 3-12 s (`BotPopManager.h:586-590`). Hunters and explorers don't idle; a 1-5 s look around at some waypoints would look more natural.
- **Speed:** walk (1.5 m/s) in town and run (5-6 m/s) outside are already split by role. Ramping the speed over a second when starting and stopping would avoid instant sprints.
- **Turning:** the heading snaps to each segment (`move()` → `setDirection`). Real clients snap too, and the client smooths it, so this is low priority.
- **Terminals:** after option 1's queue, a short pause at the terminal before leaving.

**Cost:** none. **Effort:** small each. **Risk:** low.

### Not recommended: AiAgent's movement for bots

Bots are player creatures (`PlayerObject` ghosts), not `AiAgent`s. AiAgent movement (`findNextPosition`, `updateCurrentPosition`, the behaviour trees) is tied to the AiAgent class. Reusing it means rewriting it for creatures or making bots AiAgents, and outdoors it gives the same straight lines (see "Where things stand"). BotPop already uses the same pathfinder AiAgent does, so there is nothing to gain.

### Not recommended now: line-of-sight checks on every step or leg

`CollisionManager::checkLineOfSight` ray-tests the objects near a creature (`:538-668`). Running it on each step for 1,700 bots would cost far more than the whole current step budget. It also can't see flora (see "Where things stand"). Where buildings matter, navmeshes (options 2 and 4) solve the same problem at a fraction of the cost.

## Recommended order

1. **Lanes and queues** (option 1): the patch is ready; apply, rebuild, watch one city.
2. **Partial-path handling** (option 3) and **mid-leg mesh crossings** (option 2): both small, together one patch.
3. **More POI meshes** (option 4): pick POIs from where bots actually walk.
4. **Player-like touches** (option 6): pauses and speed ramps, cheap.
5. **Interiors** (option 5): the biggest visible gain, but a project of its own. Start with entertainers in one cantina.

## Testing the first step on the test galaxy (lock holder only)

1. Apply the patch as swgemu in `/opt/swg/Core3-dev`, then rebuild:
   ```
   runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/botpop-walls/botpop-lanes.patch
   ```
2. In Mos Eisley or Bestine, watch:
   - hunters leaving by one street: they should walk side by side, not merged;
   - the mission terminal: bots should stand 3-5 m out in a small cluster;
   - the centre: medics and entertainers should be spread over a 30-38 m ring.
3. Check the log for mission requests failing with "too far away". There should be none.
4. The stats line (`steps … ms per second`) should not change.

## Option 2 drafted: `botpop-crossings.patch` (16 Oct, about 9 PM)

The patch is against Core3-dev HEAD `b6059d7a` and changes `BotPopLaunchBrain.h` only, inside `planRoute`. It passes `git apply --check` and the same syntax-only clang compile as before. It is **untested in game**.

**How it works:**
- `planRoute` takes the open stretch of each route: from the start's mesh edge, or the start, to the goal's mesh edge, or the goal.
- It samples that stretch every 25 m with `getInRangeNavMeshes`.
- For each other mesh the line enters, it finds the entry and exit points 2 m inside the edge, using the same 12-halving `edge` search the end legs use, and adds a `findPath` leg between them. The ground between meshes stays straight.
- It handles at most 4 crossings per route.
- **Budget:** a route spends one unit of `ROUTES_PER_PASS` for its ends and one per crossing. If there aren't enough units left, it spends none and is deferred, as before.

**CPU estimate (not measured):**
- At run 14's rate of about 19 routes a second, plus straight calls (hunter legs, and outdoor chases every 2 s), I expect a few thousand point queries a second.
  - A 3 km hunter leg is 120 samples; an 8 km explorer leg is up to 320.
  - Each query is a zone read lock plus a quadtree lookup, a few µs.
- Total: about 5-10 ms of CPU per second. That is about 1% of run 14's 0.76 s per second for bot steps.
- Each crossing adds one `findPath`, under the budget. Watch `routes N (M deferred)`: a rise in `deferred` means the cap of 200 units is binding.

**What a player should see:**
- Hunters and explorers crossing a POI that has a mesh, or another town, on their way out should go round its buildings and walls, not through them.
- Examples: a Tatooine camp from the `navAreas` list, or a hunter from Mos Eisley crossing Bestine's edge.
- Nothing changes in open country, or for POIs without a mesh. Option 4 (more POI meshes) is what widens the coverage.
