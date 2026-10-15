# C40: roof-ledge walk height

2026-10-15, ChatGPT. Source/offline fix prepared; **unbuilt and untested in-game**.
Server commit: `7c68e39f` on `gpt/work`, after merging dev `398744b5` in `7df4f2c7`.
Claude reviews/cherry-picks the fix commit, builds and performs runtime acceptance.
No bots, client actions, server build, restart, deployment or downloads were run here.

## Cause and call chain

Paths below are relative to `MMOCoreORB/src/` in Core3 unless prefixed `tools/`.
Original line numbers refer to dev `398744b5`; fixed line numbers refer to the fix commit.

- `server/zone/objects/creature/commands/AgentPathCommand.h:237` (original): omitted z calls the four-argument `getWorldFloorCollision(x,y,zone,false)`.
- `server/zone/managers/collision/CollisionManager.cpp:436-486`: this overload casts down from 16384 and keeps the highest surface above terrain. A ledge at 9.5 beats terrain at 5 regardless of the walker's height. The other overload at line 378 starts at reference z+2; that still permits a different nearby overhead floor, so the fix compares all surfaces instead.
- `AgentPathCommand.h:255,301` (original): the building-exit waypoint and inserted outdoor samples independently repeat the highest-surface lookup. Fixing only the destination leaves the second roof-entry route open.
- `client/agent/AgentControl.cpp:1526-1528` (original): only sends z to the helper when cell is nonzero. Explicit outdoor z was discarded during path planning. `walkPath:1225`, especially 1249 and 1277, consumes the planned z; it does not independently pick the roof.
- `server/zone/managers/collision/PathFinderManager.cpp:71-78,313,459-462`: dispatches world/cell routes, emits navmesh heights, and can return a straight start/end pair when mesh planning cannot evaluate a route. Its shared NPC implementation is unchanged. Mesh-boundary height lookups at 357/411/413 remain shared behavior; acceptance must inspect actual routes crossing mesh boundaries.
- `tools/bots/bot.py:83`: raw JSON transport writes commands unchanged. It never chooses z. Its movement documentation now explains omission and recovery.
- `tools/bots/squad.py:386,398,410,421` (fixed): move and new read-only path wrapper preserve explicit zero/negative/positive z and omit absent outdoor z; walk retains arguments across retries; go keeps local object z indoors and omits object z outdoors.
- `tools/bots/escort.py:277,289,299` (fixed): indoor follow replays the player's cell/local trail height; outdoor formation and out-of-sight catch-up omit z. Outdoor buff approach likewise omits it. New `walk_trail:146` refuses an unknown indoor height instead of silently substituting zero. Interior buff approach uses it too.

## Fix

`AgentPathCommand.h:216` selects the surface nearest a reference height, with terrain as a candidate and lower-floor tie breaking. Below-terrain object intersections are excluded as in the former world-height contract. This is for world coordinates only; dungeon cells never pass through this selector.

At line 256, an omitted destination z uses the bot's current **world** z. At line 280, an intermediate building-exit goal uses the start's world z. At lines 327-328, inserted samples select the floor nearest the interpolated route height. Original navmesh and indoor path points retain their heights. This preserves legitimate ramps, plateaus and upper-floor routes instead of imposing a global maximum z or always selecting terrain. The 256-point cap and replan behavior remain intact.

`AgentControl.cpp:1532` forwards explicit outdoor z as `path x y z 0`; the helper now accepts cell ID zero as world space. Cell targets require an explicit local z (`1527`), protecting multi-level rooms from a guessed zero. Omitted-z moves require the helper (`1525`), and helper failure no longer falls through to NPC-height blending (`1573`). This deliberately changes the failure behavior: unavailable helpers return an error rather than an ungrounded straight walk. Explicit `path:false` with explicit z keeps its existing behavior.

## Getting off a roof

Use the same next-walk rule: select a nearby **clear-ground point beyond the roof footprint**, inspect `bot.path(x,y)` without z, then `bot.move(x,y)` without z. With no roof at that target, terrain wins even when current z is 9.5. Do not target the same covered x/y without z: nearest-floor selection intentionally keeps a bot already on the roof there. This is walking recovery, not a vertical teleport or a blanket terrain snap that breaks the Warren/bunker.

No recovery was sent to the stranded bot in this task. Claude must choose and inspect a real clear-ground target; the synthetic test coordinate is not a verified safe destination. If the navmesh cannot route off the roof, report that failure and use an owner-authorized recovery, rather than claiming the fixture proves reachability.

## Offline verification

- `python -I outputs/tools/bots/test_movement_height.py`: **6/6** passed; move/path omission, explicit world and cell heights, retries, go frame choice, escort positive/zero/negative trail heights and unknown-height refusal.
- Existing `test_escort.py` under `python -I` with its directory explicitly inserted and `runpy.run_path(...,run_name='__main__')`: **11/11** passed.
- WSL as swgemu: `python3 -I .../tools/bots/check_c40_floor.py /opt/swg/Core3-gpt`: extracted the actual C++ selector and compiled it with synthetic collision/terrain stubs using `g++ -std=c++17 -Wall -Wextra -Werror`; **7 assertions** passed. Old highest-surface rule reproduced 9.5 versus ground 5 at the reported x/y; fixed selection returns 5 from ground and 9.5 from roof, breaks ties down, descends at an uncovered destination, retains stacked floors, handles negative world floors and real terrain at 180.
- Diff whitespace checks passed. These fixtures do not load the Mos Eisley terrain, real collision assets, navmeshes or dungeon portals; they are not an in-game reproduction or full server compilation.

## Claude acceptance still required

1. Review/cherry-pick `7c68e39f`, build both server/helper and core3client; start/relog under Claude's lock and the owner's runtime rules.
2. On ground near the starport, inspect path then walk to 3536,-4796 without z. Record starting z, every route point and final z; a 9.5 ledge must not replace a roughly 5 ground floor.
3. From the current roof, inspect and walk to an actually verified clear-ground spot. Record route, descent and corrections; do not just assert arrived from x/y proximity.
4. Walk along/under the ledge, across mesh boundaries and uphill to a real plateau. Inspect original and inserted route points for discontinuities.
5. In both the bunker and Warren, follow a player down and up between cells/floors, including zero and negative local z; repeat stay/follow and buff approaches. Confirm the crew uses the player's trail floor. A missing trail z should hold with an error, never target zero.
6. Run outdoor escort formation/catch-up/buff approaches around the starport and check explicit outdoor z, helper-unavailable errors, long capped routes and building exits. No blanket claim that all navigation regressions are closed until these pass.
