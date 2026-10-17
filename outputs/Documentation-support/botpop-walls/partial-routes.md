# Why almost every BotPop route has a leg that stops short

Claude, 17 Oct 2026, 12:30 AM. Read-only on /opt/swg: run 19's logs, a copy of the test galaxy's `navareas.db`, and
Core3-dev HEAD `69f5c879`. Nothing was built, restarted or sent to the galaxy. Patch: `botpop-partial-routes.patch`
(passes `git apply --check` on 69f5c879; syntax-checked with clang, not built or run).

## Answer

**(d) something else, and it is a real problem.** Most travellers who land at a starport never leave its landing pad.
The pad is walled in, and it is a separate piece of the town's navmesh, 32 to 43 m from the rest, with no navmesh way
out. The only way out is through the terminal building, and BotPop's own routes never go through buildings (they
never fall back to a straight line since `8edfd13f`). So every route from the pad stops at the pad's edge, and the
bot plans it again a few seconds later, for good.

- At 12:26 AM, 849 of the 1,295 bots standing in a town's navmesh (66%) were on a starport pad. Another 135 (10%)
  were on other small cut-off pieces, 49 (4%) on a cut-off piece at a launch centre (Tyrena, Bestine, Mos Eisley),
  and only 226 (17%) on the town's main mesh.
- Of the 768 bots that had landed on a cut-off pad 10 minutes or more earlier, 615 were still within 100 m of the
  landing point. 104 had left again by shuttle, and 49 got further than 100 m. Of the 222 that landed on a town's main
  mesh (Theed, Bela Vistal, Anchorhead), 201 had walked away.
- The stats line counts a stuck bot's re-plans, not distinct routes. Since 12:06 AM the route budget has been at its
  cap: 12,000 routes a minute, 11,400 partial legs a minute, and about **38,000 route requests deferred a minute**.
  That last number hurts the bots that are not stuck: their walks wait behind the trapped ones.

The other candidates, measured on the same replay (12:26 AM, 17,370 legs from every bot's real position and height):

| Candidate | Partial legs it explains | Of 14,437 partial |
|---|---|---|
| (a) counting artefact: the partial end is already within 2.5 m of the goal | 87 | 0.6% |
| (c) Detour runs out of its 8,192 nodes on a leg it could finish with 65,535 | 169 | 1.2% |
| (b)/(d) start and end on unconnected pieces of the mesh | 14,268 | 98.8% |

The last row is mostly (d), the pads. Real dead ends of type (b) exist but are small: with the pads taken out (11:51
PM, before most bots had travelled), 15.8% of legs were partial. A 15 m pocket hop (fix 2) brings that to 7.7%. The
rest are ends on other cut-off pieces, which I didn't examine one by one.

## How it was measured

Run 19 (1,700 bots, dev `69f5c879`) has no per-route log, so the routes were replayed off-line with the same code:

1. **The navmeshes.** I copied `navareas.db` and carved the 108 saved meshes out of its Berkeley DB overflow pages.
   Each page's data starts at byte 32, not 26: with 26 the tiles look right for a few hundred and then go wrong. Each
   mesh was loaded into Core3's own Detour sources (`src/pathfinding/recast`) and its pieces were labelled by flood
   fill over the polygon links, with BotPop's filter (`SAMPLE_POLYFLAGS_ALL` minus disabled and swim).
2. **The bots.** Each bot's last `snap` row in `botpop-launch.jsonl` (planet, x, y, z, state, role). The live map's
   `botpop-positions.json` has no height. My first pass guessed a height from the mesh, which put bots in a
   building's footprint up on its roof. That is why the early numbers in this session's notes are off.
3. **The legs.** For every bot in a town's mesh (about 1,300), four kinds of leg, each through a copy of `meshPath`:
   to the town edge (a hunter going out), from the edge to the bot's spot (coming back), to the launch centre
   (medics, entertainers, resting), and to a random point of the mesh (terminals, trainers). Same nodes, extents and
   snapping as the server. Each partial leg was checked for `DT_OUT_OF_NODES`, for start and end on different pieces,
   for the end's distance to the goal, and again with 65,535 nodes.
4. **The landings.** Each `travel_done` row's x, y, z (the planet is `to_planet`; `planet` in that row is the old
   one). Then, from the later `snap` rows, the bot's furthest distance from the landing.

Scripts: `partial-routes-replay/` (`run.sh` repeats all of it inside WSL, in `/root/pr`, reading /opt/swg only).

### The starport pads

The landing point of each starport bots came down at (one per town), the piece it is on, and the nearest point of
the town's main piece within 4 m up or down:

| Town | Landing piece | To the town's mesh |
|---|---|---|
| Moenia, Restuss, Doaba Guerfel, Keren, Kaadara, Narmle, Bestine, Coronet, Nashal, Tyrena, Mos Entha, Mos Espa, Kor Vella, Dearic, Bilbousa | 79 to 92 polygons | 32 to 43 m |
| Mos Eisley | 156 polygons | 34 m |
| Theed, Bela Vistal, Anchorhead | the town's own piece | 0 m |

A town's own piece has 1,391 (Anchorhead) to 25,239 (Kor Vella) polygons. `tripWalk` already knew that starports are
cut out of the town mesh (its run 17 comment). It walks *in* through the building's path graph, and onward trips
from a pad work: 104 bots left again by shuttle. Nothing walks a staying bot *out*.

### The launch centres

Bestine's centre (-1204, -3692) is on a 55-polygon piece 4 m from the town's mesh, and Tyrena's (-5217, -2456) on an
85-polygon piece 12 m away. Bots end up there because launch bots spawn and are revived around the centre, and
chaseToward's last straight 15 m carries a chasing bot onto the piece. Many stood at the exact centre coordinates,
which suggests the spawn fallback (`request.center`, then `snapToMesh` to the nearest polygon). That part is inferred. Every route out stops at the piece's edge.
At 11:51 PM, all but one of Bestine's 498 replayed legs were partial, and all but one of Tyrena's 345.

## What a bot does after a stopped leg

- **Route walks** (`startRoute`: hunters going out, explorers, wanderers). ROUTE_SHORT is walked to its end, then the
  bot is IDLE and `launchHunt` plans again at once with a new random goal (it doesn't wait for `nextActionMs`). On a
  pad, that means a new partial route every few seconds while it shuffles about the pad. ROUTE_NONE waits 5 s.
- **Chases** (`chaseToward`: town centre, mission terminal, lair, patient, shuttle). The bot walks to the end. Within
  `stopAt` + 15 m it steps the rest straight (C60 F1). Otherwise it stands and plans again every 2 s. Only fights
  (120 s), trip steps (5 minutes) and lairs give up. The centre and terminal chases never do.
- **The goal** is kept by chases and swapped by route walks. Neither moves a bot off a pad, so a stuck bot stays
  stuck: no hunting, no XP, no missions, no planet data beyond the pad. The `travels` counter (1,788) still counts it
  as a successful arrival.

For the run's purpose this matters twice. Most bots stop testing anything once they have travelled. And the route
budget is spent on them, so the bots that could move wait.

## The fix (`botpop-partial-routes.patch`, 4 files, +201 −1)

1. **Out of the starport after landing** (`BotPopTravel.h`: `tripArrived`, new `tripExit`). When a trip ends at a
   travel point whose terminal is inside a building, and the bot stays (not a connection), it gets an exit errand
   before anything else (`L->exitTerminalID`):
   - It walks to the hall's travel terminal with `tripWalk`, the building's own path graph, the way an onward trip
     already goes from the pad.
   - As soon as it is inside a cell, it plans again with `tripWalk` toward the town's outdoor mission terminal
     (`launchFindTerminal`), which leads out of the hall's front door.
   - The errand ends when the bot steps outdoors, or after 3 minutes. A failure leaves the cell by the door the bot
     came in, as a failed trip does. Fights interrupt it, and death clears it (`launchRevive`).
   - One new `exit` row each time: `how` (`out`, `timeout`, `no terminal`, `no path into the hall`, `no town
     terminal`, `no way out`), `secs`, x, y, z.
2. **Off a small cut-off piece** (`BotPopLaunchBrain.h`: `meshPath`, new `meshOutOfPocket`). Before the main search,
   a 512-node probe from each end toward the other tells a small piece from a town's own. The probe runs out of mesh,
   not nodes, only on a piece of fewer than 512 polygons that doesn't hold the other end. That end then moves to the
   nearest polygon within 15 m across and 4 m up or down that is on a bigger or joined piece (it tries the 4 nearest
   other pieces), and the hop to it is straight. Replay: Bestine 369 → 6 partial legs, Tyrena 220 → 3; all legs at
   11:51 PM 15.8% → 7.7%. It can't reach the starport pads (32 m and more), which is fix 1's job. Cost: two probes of
   at most 512 nodes per leg, against 8,192 for the main search. The replay was at most 6% slower (21.2 s against
   20.0 s for 17,362 legs).
3. **A counter**: `, pocket hops N` after `snapped N` on the stats line (`legPocket`). `botpop_findings.py`'s regex
   isn't anchored, so it still parses the line, but it doesn't read the new field yet.

Left as they are: `MESH_NODES` (raising it would fix 1.2% of partial legs, those partials still make progress toward
the goal, and it would cost the most where the end can't be reached anyway), and the "partial" counter's meaning.

## How to verify (next run with the patch)

From the stats line, once bots have been travelling for 30 minutes or more (run 19's line from 12:06 AM on is the
baseline):

- `routes` well under the 12,000 cap, with `deferred` near 0 (run 19: about 38,000 a minute). This is the main check.
- `partial` no longer close to `routes` (run 19: 11,400 of 12,000).
- `pocket hops` a few hundred a minute at most. Thousands would mean bots go back into pockets as fast as they leave.

From `botpop-launch.jsonl`:

- `exit` rows: almost all `out`, each a few seconds to a minute after its `travel_done`. Many `no path into the hall`
  or `timeout` rows mean the building's path graph doesn't serve the pad at that starport; the row's position names
  it.
- Rerun `partial-routes-replay/run.sh`. `join.py`'s "cut-off piece / still there" should fall from 615 to near 0, and
  `classify.py`'s "starport landing piece" from 849 to the few bots waiting for a shuttle.
- An `exit` row with `how: out` whose x, y lies on the pad (check with `LANDINGS=1` or `PIECES=1`) means
  `findPath(cell → town)` went out the pad-side door. That is the first thing I'd check, because I couldn't test it.

## Limits

- The patch is not built or run. It was syntax-checked by compiling `CommandConfigManager.cpp` (which includes the
  BotPop headers) with the dev build's flags and the patched headers first on the include path. The check really read
  the patched copies: a planted `static_assert` fired.
- Fix 1 rests on `findPath` from the pad into the hall (onward trips show it works) and from the hall to the town
  (how departures come in). Neither has been watched from the pad side.
- The replay uses the meshes as saved in `navareas.db` at 11:51 PM and treats each NavArea's circle as the mesh's
  square bounds less a tile at most. Goals for centre, edge and random legs are standard ones, not each bot's real goal.
- Bilbousa has 56 more bots on small pieces that are not its pad, and Kor Vella 33. I didn't look at what is there.

## Follow-ups

- `botpop_findings.py`: read `pocket hops`, and report `exit` rows by `how` and by town (ChatGPT's tool).
- C60 F2, still open: back off re-plans that come back with the same short end. That bounds the cost of whatever
  dead ends are left.
