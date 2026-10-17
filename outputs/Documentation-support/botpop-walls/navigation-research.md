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

## Bots running through whole buildings in Coronet: `botpop-nofallback.patch` (16 Oct, about 10 PM)

The owner saw this in run 15 at about 9:20 PM. The patch applies to Core3-dev `e7512cb8` and to `665bea04`, the current HEAD; `git apply --check` passes on both. A syntax-only clang compile passes too. It is **untested in game**.

**Cause (confirmed in the code, not yet counted in game):**
- My `planRoute` legs called `PathFinderManager::findPath`. Whenever Core3's Recast query fails, `findPathFromWorldToWorld` returns the straight line from start to end (`PathFinderManager.cpp:461-465`), and `leg()` took it as a route. So did `startWalk` and `chaseToward`.
- The query fails or comes up short in these cases:
  - **Start or end off the mesh.** `getRecastPath` looks for the nearest polygon within extents `{8, 8, 3}` in Recast order (x, height, z): only 3 m north-south (`:228`). A bot or goal in a building's footprint, a town centre inside a building, or a point that `getSpawnPointInArea` pulled back inside its radius (`:1335-1344`) finds no polygon.
  - **Partial paths are accepted.** `findPathFromWorldToWorld` passes `allowPartial = true` (`:476`). On a big mesh, the A* search stops at 4,096 nodes (`MAX_QUERY_NODES`, `:25`), and Coronet's mesh has 0.15 m cells. The route then ends partway, and the rest was walked straight.
  - **A disconnected part of the mesh**, such as a roof or a walled yard, gives the same partial path.
- Spawns: `getSpawnPointInArea` falls back to the city centre itself, which can be inside a building (`BotPopManager.h:482-485`).

**Step CPU (1,335-1,389 ms per second) is not a regression.** Run 14's log shows the same rise:
- run 14: 769 ms/s at 5 minutes, 1,431 ms/s at 10 minutes;
- run 15: 752 ms/s at 5 minutes, then 1,277-1,433 ms/s.

The 761 ms/s figure was read in the first minutes, before the bots spread out to hunt.

**The fix:**
- **`meshPath`:** BotPop's own Detour query, using the same Detour library and the mesh's own `dtNavMesh`, with one query object per worker thread.
  - It snaps the start to the nearest polygon within 10 m. It snaps the end within 10 m, then 40 m. Both search only 2.5 m up or down (4 m for the 40 m search), so a roof isn't chosen.
  - It allows 8,192 nodes, twice Core3's limit.
  - A partial path is reported as partial, and the route ends at the reachable point nearest the goal.
- **Failure handling:**
  - Every `planRoute` leg uses `meshPath`. When a leg fails, the route ends at the last point reached (`ROUTE_SHORT`), or there is no route at all (`ROUTE_NONE`). It is never a straight line across the mesh.
  - `startRoute` retries a failed route after 5 s; hunters and explorers then pick a new goal.
  - `startWalk` (the wander) now goes through `startRoute`.
  - `chaseToward` waits instead of stepping straight while it has no route: budget spent, no route, or at the end of a short route. It plans again after 2 s.
- **Spawns** are snapped to the mesh (`snapToMesh`).
- **The stats line** adds `routes N (M deferred, K none), legs stopped: no start, no end, no path, partial, unloaded mesh, snapped`. Those counters are the in-game check. The patch counts failures instead of falling back, so they show where the mesh doesn't reach.
- **`no path`** (the wander) now also counts wanders refused because the budget was spent or there was no route.

**What a player should see:**
- In Coronet and other towns, bots keep to the streets.
- A bot whose goal can't be reached stops where the street ends and turns away, instead of walking through the building.
- A bot found inside a footprint hops at most 10 m to the street. Watch for that hop.

**Risks:**
- A bot whose start is more than 10 m from any walkable polygon stays put. It retries every 5 s, and the `no start` counter shows it.
- A large `partial` count would mean the 8,192-node limit is too low for the biggest cities.
- **CPU:** a failing search can now run to 8,192 nodes instead of 4,096, but failures retry only every 5 s (routes) or 2 s (chases). Snapping adds one or two cheap nearest-polygon lookups per leg. I expect step CPU to stay about the same; compare the stats line.

### Planetary map landmarks as destinations (described, not in the patch)

- The M-key map image has no walkability data. But Core3 keeps the map's locations by category: `Zone::getPlanetaryObjectList(category)` (`GroundZone.idl:141`). Core3 already uses it for `"cloningfacility"` (`PlayerManagerImplementation.cpp:1640`) and `"trainer"` (`FindMyTrainerCommand.h:88`).
- Wandering and idle bots could pick a cantina, starport, shuttleport, bank or terminal in their own city as a goal, a few metres in front of the building, snapped to the mesh. Then they would go where players go instead of to random points.
- It needs the category names and a per-city filter (within the city radius), and goals must stay outside the buildings until interiors (option 5) exist.
- **Effort:** small, about 40 lines. **CPU:** a list lookup per goal.
- It's best done after the counters above show the routes are clean.
