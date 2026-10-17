# C60: review of the BotPop movement commits (run 16)

Reviewer: Claude (side session, 16 Oct, about 9:50 PM), taking GPT's queued task C60 while GPT is out until 22 Oct.
Scope: `/opt/swg/Core3-dev` at `8edfd13f`, the six commits `724809fa` walls, `5bf55669` step-up, `de9a825c` lanes,
`e7512cb8` crossings, `665bea04` lair_check and `8edfd13f` no-fallback. Read-only: `git show` and source copies made
inside WSL, plus run 16's `core3.log` stats lines (9:35 to 9:46 PM) and `botpop-launch.jsonl` (to 9:46 PM).
Line numbers are `BotPopLaunchBrain.h` / `BotPopManager.h` at `8edfd13f`.

## Verdict for tonight

**Nothing found that can crash or deadlock run 16.** It is safe to leave running overnight. Two things will get worse
as the night goes on, but both are bounded: about 110 hunters are stuck for good at the Tyrena and Bestine mission
terminals (F1), and route CPU is climbing (F2). The per-pass route budget caps that cost, and the tick skips a pass
rather than queueing work behind a slow one.

Watch the stats line in the morning. If `deferred` or `skipped` is above 0, the 200-route budget is saturated and
healthy bots are waiting behind the stuck ones.

## Locking and lifetime (checked, no finding)

- **Lock order.** A bot step holds the bot (write). `meshPath` (line 100) and `snapToMesh` (line 170) take
  `ReadLocker(area)` under it. That is the stock order: `AiAgent` → `PathFinderManager::getRecastPath` holds the agent and
  takes `ReadLocker rLocker(area)` (PathFinderManager.cpp:241). Nothing takes a NavArea and then a creature:
  - the rebuild's `setNavMeshLambda` takes only `Locker(area)` (NavMeshManager.cpp:229);
  - `NavArea::updateNavMesh` takes `Locker(area)` with the entering object locked (NavAreaImplementation.cpp:73), but
    creatures and lairs return before it (line 114), and BotPop's order is creature → area anyway.
- **Area, then zone.** `snapToMesh` calls `floorNear` (CollisionManager, zone read lock) while it holds the area read
  lock. The zone's write lockers (`insert`/`remove`/`update`, GroundZoneImplementation.cpp:154-196) lock nothing else, and
  `clearZone` releases the zone before it locks objects (line 116). So there is no cycle.
- **Mesh lifetime.** The rebuild frees the old `dtNavMesh` under `Locker(area)` (NavMeshManager.cpp:242-245).
  `8edfd13f` reads `getNavMesh()` and runs the whole query inside the read lock, so a rebuild can't free the mesh
  mid-query. An initial build (`dtNavMesh` still null) is counted as `unloaded mesh` and skipped. That counter is 0 all
  run.
- **thread_local query** (line 72). There is one per worker thread. It is `init`ed on the mesh at hand inside the lock on
  every call and not used after the lock is released. Nothing re-enters it, and it is separate from PathFinderManager's
  own query. It is never freed: one small allocation per worker for the life of the process, which is fine.
- **Bounded loops.** `walk` (BotPopManager.h:572) either uses up its step budget or advances a waypoint on each
  iteration. The `chaseToward` waypoint loop either returns or advances. The crossings sampler runs at most
  `length / 25` times (about 900 on a planet-wide explore leg). The `edge` bisection runs 12 times. Detour is capped at
  8,192 nodes, 2,048 polys and 256 points, using about 12 KB of stack, the same as Core3's own `getRecastPath`.
- **lair_check** (line 1926) reads the lair without locking it: `checkLineOfSight`, `isAttackableBy` and the condition
  getters, once a minute. These are read-only and are the same reads stock combat makes from the attacker's thread.
- **C55 F1 (the helper droid lock order) doesn't apply here.** Bots are marked so they get no helper droid
  (`Registry::markBot`, BotPopManager.h:508).

## Run 16's numbers: what the route counters mean

At 9:39 PM (the line quoted as "9:41"): 3,875 routes a minute, 1,423 none, 2,896 partial legs, no start 111, no end 51,
snapped 94. The trend since then, one line a minute:

| Time | Steps (ms/s, all workers) | Slowest chunk | Routes | None | Partial legs | No start | No end | Deferred |
|---|---|---|---|---|---|---|---|---|
| 9:36 PM | 782 | 161 ms | 1,985 | 149 | 861 | 0 | 96 | 0 |
| 9:39 PM | 706 | 133 ms | 3,875 | 1,423 | 2,896 | 111 | 51 | 0 |
| 9:44 PM | 1,370 | 219 ms | 5,947 | 2,906 | 4,909 | 482 | 240 | 0 |
| 9:46 PM | 1,470 | 343 ms | 6,506 | 3,186 | 5,263 | 533 | 303 | 0 |

**The partial routes are mostly stuck bots, not chunked progress.** The 60 s `snap` rows show it directly. At 9:46 PM,
99 bots in `walking` and 149 in `idle` had not moved 1.5 m over their last three snaps (2 minutes), and they stand in
clusters:

| Where | Still bots | Missions taken | What is there |
|---|---|---|---|
| Tyrena, about (-5200, -2450) | 43 walking + 14 idle hunters (and 10 medics and entertainers a few metres away) | 0 | the mission terminal (-5213, -2451) |
| Bestine, about (-1230, -3665) | 42 walking + 13 idle hunters | 0 | the mission terminal (-1222, -3677) |
| Bestine (-1200, -3690), Mos Entha, Theed, Kor Vella, Dearic | 3 to 16 each, mostly medics and entertainers | 0 | the town centre (some of these may simply have arrived) |

So these are hunters that walked a route which stopped short of the terminal and are now waiting there. `chaseToward`
re-plans every 2 s, each re-plan is partial again (or `none` when the reachable end is where they already stand), and
nothing times out a terminal chase (F1). At about 30 re-plans a minute each, roughly 100 stuck bots account for about
3,000 of the 5,263 partial legs and most of the 3,186 `none`. That count grows as more hunters reach those two
terminals, and stops growing when they have all arrived.

**Mission bots do reach their lairs** in the cities whose terminals work. By 9:46 PM there were:

- 814 `mission_take` rows;
- 384 bots that reached the lair (median 5 minutes after taking the mission);
- 430 still on the way (median distance 1,634 m at take, about 5.5 minutes at 5 m/s);
- 12 `mission_done`, all brawlers.

Bestine and Tyrena hunters show 0 missions taken.

**The lair_check rows can't tell us about ranged bots yet.** There were 324 rows. All 194 ranged rows have LOS true,
attackable true, a distance of 5 m and posture upright. That is new evidence: line of sight to the lair passes at 6 m.
But every one of those rows is the bot's first check, which is written before its first shot (F5), so their damage of 0
means nothing yet. Only 6 bots had a second check by 9:46 PM, all melee, and 5 of those show the lair's damage rising.
Read this again after midnight.

## Findings, most severe first

### F1 (high, behaviour; no crash): a chase that stops short never gives up, and about 110 hunters stand at two terminals all night

- **Where.** `chaseToward`'s wait branch (`BotPopLaunchBrain.h:441`), together with the terminal chase
  (line 1963: `if (!chaseToward(... terminal ...)) return true;`) and the town-centre chases (lines 1050, 1228, 1361).
  `8edfd13f` replaced the straight-line fallback with "walk to where the mesh stops, then wait". That is right for
  walls, but nothing ever ends the wait.
- **Failing case.** Tyrena's and Bestine's general mission terminals are not reachable on their navmesh from where the
  bots come from. The reachable end is about 10 to 15 m away (an island, a raised platform or a footprint).
  `launchMission` keeps calling the terminal chase with no deadline, because `nextMissionTryMs` is only set on a mission
  result. Run 16 has 57 hunters at Tyrena's terminal and 55 at Bestine's with 0 missions between them, re-planning every
  2 s. Before `8edfd13f`, `findPath`'s fallback would have walked them the last 13 m through whatever was there.
- **Fix** (any one of these is enough for the next run):
  1. Allow a final straight hop when the short route ends within 15 m of the target and the target is a terminal or the
     town centre. This is the old behaviour, limited to the last few metres.
  2. Give each chase target a deadline. Record `chaseSinceMs` when the target changes. After 60 s of SHORT or NONE on
     the same target, the terminal chase sets `nextMissionTryMs = now + 30 min` and the bot goes hunting without a
     mission, and a centre chase counts the current spot as arrived.
  3. Log one `chase_stuck` row per bot and target (position, target, route result) so the unreachable spots get named
     rather than inferred.

  I'd do 1 and 3: 1 restores missions in those two cities, and 3 finds the next such spot.

### F2 (medium, CPU): stuck bots re-plan every 2 s with a full 8,192-node search

- **Where.** `chaseToward`'s re-plan gate (line ~404: `stale && lastStepMs >= chasePlannedMs + 2000`). After a SHORT
  route has been walked, `chaseNext >= chase.size()` makes the route stale at every step. A partial search on a
  disconnected island expands nodes until the 8,192 cap.
- **Evidence.** From 9:39 to 9:46 PM, steps rose from 706 to 1,470 ms per second across workers and the slowest chunk
  from 133 to 343 ms, while routes rose by 2,631 a minute. That is roughly 17 ms of worker time per extra route (Debug
  build). The budget (`ROUTES_PER_PASS` 200 × 60 passes) caps routes at 12,000 a minute, about 3.4 s of worker time per
  second at that rate. The tick skips a pass whose steps are still running, so this can't pile up into a hang. But at
  the cap, `deferred` rises and healthy bots wait behind the stuck ones.
- **Fix.** Back off on a repeat: if the new route's result and end point equal the last one's (SHORT or NONE, same
  target within 1 m), double the re-plan interval up to 30 s. F1's deadline removes most of it anyway.

### F3 (medium): `no start` rises through the run (0 → 533 a minute), and a bot off the mesh is stuck for good

- **Where.** `meshPath` looks for the start polygon within 10 m across and 2.5 m up or down only (line 120). The end
  gets a second try at 40 m (line ~126).
- **Failing case.** A bot that ends up off the mesh can never get a route again: `chaseToward` waits forever, and
  `startRoute` retries every 5 s (line 379). Ways off the mesh include a straight open-ground leg ending in a footprint,
  or step-up (F6) lifting it onto something more than 2.5 m above the street mesh. The count went from 0 at 9:36 PM to
  533 a minute at 9:46 PM. At 2 to 12 re-plans a minute per bot, that is several dozen bots.
- **Fix.** Give the start the same 40 m / 4 m second try, with the hop to it first in `out`. The bot is already off the
  mesh, so a hop of up to 40 m is the lesser evil. Log a sample `no_start` row once a minute (position, z, terrain
  height) to find out how they got there.

### F4 (low): crossing areas are kept as raw `NavArea*` after their references are dropped

- **Where.** `struct Crossing { NavArea* area; ... }` (line 292). It is filled from `here`, a
  `SortedVector<ManagedReference<NavArea*>>` that goes out of scope at the end of each sample (line 304). The pointers
  are used later by `edge` and `meshPath` in the same call.
- **Failing case.** Only a NavArea destroyed during that call: a player city's area dropped mid-route. Static city and
  POI areas are also held by the PlanetManager. This isn't reachable on run 16.
- **Fix.** Make it `ManagedReference<NavArea*> area` in `Crossing` (and in `inside`).

### F5 (low): the first lair_check of each visit is written before the first shot

- **Where.** Line 1926. `nextLairCheckMs` starts at 0, so the row is written on arrival, before `enqueueCommand("attack")`.
- **Effect.** Its `damage` is always the lair's damage before this bot has fired. The question "do ranged shots land?"
  depends on the second row, 60 s later. Run 16 has 194 first rows from ranged bots and no second ones yet.
- **Fix.** Set `nextLairCheckMs = now + 30000` on arrival, so the first row comes 30 s into the attack. Or add a
  `shots` count since arrival to the row.

### F6 (low): step-up may climb up to 2.5 m in one step

- **Where.** `stepUpFor(length) = clamp(0.6 × length, 1.2, 2.5)` (BotPopManager.h). `floorNear` takes the highest floor
  at or below `referenceZ + stepUp` (line 23).
- **Failing case.** A bot at 5 m/s with 1 s steps gets 2.5 m every step, enough to land on a crate, a low wall top, a
  bridge deck it is walking under, or a market-stall roof. From there it can be off the street mesh (F3). The commit's
  "ramps and kerbs yes, roofs no" holds for roofs of buildings, not for 2 m props.
- **Fix.** Climb about 0.6 m per metre walked, with a fixed cap of about 1 m per step regardless of step length:
  `Math::min(1.f, Math::max(0.5f, 0.6f * length))`. A long ramp is climbed over several steps anyway.

### F7 (low, CPU): the crossings sampler runs before the budget check

- **Where.** Lines 304-345. The samples (one `getInRangeNavMeshes`, so one zone read lock, each 25 m) are taken before
  `spend`. A `ROUTE_DEFERRED` result throws them away and the next step samples again.
- **Effect.** Nothing today (0 deferred all run). Once the budget saturates (F2), each deferred explorer re-samples up
  to about 900 points per step.
- **Fix.** Check that the budget has at least one unit before sampling, or keep the samples when deferred.

### Does each commit do what it says?

- **724809fa walls.** Yes: one leg per mesh at each end and an `edge` bisection. Superseded by `8edfd13f`'s own query.
- **5bf55669 step-up.** Yes. The step size is generous (F6).
- **de9a825c lanes.** Yes. A lane is ±0.4 m, inside the meshes' 0.5 m agent radius, so a lane point is never inside a
  wall. On sharp corners the offset segment can clip the corner by up to 0.4 m, which is cosmetic. Terminal and centre
  spacing is applied.
- **e7512cb8 crossings.** Yes. The budget counts one unit per crossing. See F4 and F7.
- **665bea04 lair_check.** Yes. See F5 on timing.
- **8edfd13f no-fallback.** Yes: no straight line across a mesh, and the lock is taken before the mesh pointer. The
  missing piece is giving up (F1 to F3).

## What I could not check

- **Whether the Tyrena and Bestine terminals are on a mesh island, a platform or inside a footprint.** That needs a
  position query or a `chase_stuck` row (F1 fix 3), and I ran no galaxy or bot commands.
- **The worker count, and how much of the CPU rise is route planning versus combat and other step work.** There is no
  per-function timing; the 17 ms per route is an inference from two stats lines.
- **Ranged damage on lairs**: too early in the run (F5).
- **Whether Detour's `closestPointOnPoly(..., endPos, endPos, ...)` with the same input and output array is safe in
  Core3's bundled Detour version.** In the upstream versions I know, the function copies before it writes. The worst
  case is a wrong end point, not a crash.
- **Behaviour under a navmesh rebuild during run 16.** `unloaded mesh` stayed at 0, so no rebuild happened in the window
  I read.
