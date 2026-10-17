# "The server keeps putting us back": cause and fix

Claude, 17 Oct 2026 (functional test plan, section 4 and gap rank 2). Results of the rerun are at the end.

## What failed

On 15 Oct the gate lost three checks to the agent body's error "the server keeps putting us back (blocked, rooted or dead)": Besh's hide patrol (`besh-harvest.py`), Cresh's walk to the mission area (`cresh-missions.py`) and Tovan's walk to the plateau (`esk-routes.py`). On 17 Oct at 3:26 AM Dova's 268 m walk from the square into the cloning facility failed the same way (`besh-death-insurance.py`); two legs (outdoors to the building, then in) worked.

Every case in the reports (14 failed moves, 15 and 17 Oct) has the same shape: three corrections spread over one long walk, 2 to 20 seconds and up to 78 m apart, with the bot making progress in between. Outdoors the server put the bot back to z 5.0, the ground in and around Mos Eisley.

## Causes

1. **The body gave up after three corrections per move, however long the move** (`AgentControl.cpp`, `moveTo` and `walkPath`: `serverCorrections - correctionsAtStart >= 3`). A walk of 268 m sends about 120 positions; three isolated bounces anywhere in it failed the whole walk, while a short leg rarely collects three. That is why splitting a walk into two legs worked.
2. **Every server position message counted as a correction.** The server also echoes a still player's own position (`DataTransform::updateStatic`, the "synchronize" reply). Those moved the bot 0 m but counted towards the three.
3. **Posture.** The server bounces a step that is faster than the posture allows (`checkPlayerSpeedTest`: run speed × `speedMultiplierMod`, which the posture scales). A crouched or sitting bot walked at 5 m/s and was put back on every step: Forn's "rubber banding kinda bad" on 15 Oct (escort.py has stood bots up before walks since `dd9febe`; other scenarios did not).
4. **Why the server bounces a walking bot now and then: a server stall reads as speeding (confirmed on run 24).** The bodies walk at 5.0 m/s against an allowance of 5.376 × 1.056 ≈ 5.68 m/s. The server measures speed as client distance over *server* time since the last validated position (`PlayerManagerImplementation::checkSpeedHackTests`, `getServerMovementTimeDelta`), so when packets are held up and then handled together, the next window holds more distance than its server time allows. With the new log, the first stall after the restart showed it: at 211 s, while BotPop's 300 bots were logging in (BotPop tick up to 241 ms), five bots in three groups were bounced in the same second, all by the speed check: 8.41 m in 1,360 ms of server time (6.19 m/s), 8.41 m in 1,351 ms, 8.61 m in 1,351 ms, 11.49 m in 1,413 ms and 12.68 m in 1,367 ms (9.28 m/s). A bot walks 8.4 m in about 1.7 s. Under run 23's steady light load (300 BotPop bots, no logins) two probes had walked about 7 km with no correction at all:
   - `claude-probe-movement.py` (5:08 AM): 24 straight 200 m legs at 5.0, 4.6 and 4.2 m/s, 4,800 m, 0 corrections.
   - `claude-probe-pathwalk.py` (5:14 AM): 8 server-planned routes, among them Dova's failing walk into the cloning cell (arrived, 0 corrections) and the plateau trip; 0 corrections (5 long trips ran out the single-move 95 s cap, a scenario choice, not a push-back).

Not a cause: the roof-ledge height (C40) is fixed in dev since 15 Oct (`b587e530`), and BotPop's walls are a separate server-side walker (botpop-walls session, `ed2e828`).

## Fix (dev `b034d15f` server log, `7c2f2605` agent body)

Agent body (`src/client/agent/AgentControl.cpp`, `.h`):
- A correction is a server position that moved the bot (more than 5 cm, or into another cell). The event now carries `moved`.
- `moveTo`: give up only on three corrections with under 10 m walked between them (a real block: rooted, overloaded inventory, dead, a wall), or eight in one move. Replies report `corrections`.
- `walkPath`: a correction ends the leg, and the move command plans again from where the server put the bot (it may be back across a doorway). Same three-in-10-m and eight-per-move limits.
- Walk speed follows the server's limit: the body reads run speed and the speed multiplier from its own CREO4 deltas and walks at no more than 93% of their product (5.0 m/s upright, as before).
- `move` stands up first from crouched, prone, sneaking, sitting or lying down, and waits out a knockdown (up to 8 s).

Server diagnostic (`DataTransform.h`, `DataTransformWithParent.h`, `PlayerManagerImplementation.cpp`): every bounce writes one `[Movement] DT bounce: <check> at <position> back to <position>` line to the console log, and a failed speed check writes the measured speed, distance, server time and allowance. Until now the reasons were only visible in a debug build (`TRANSFORM_DEBUG`, `DEBUG_SPEED_HACK`). It logs for every player, the owner included, so a rubber-band in the real client can be traced too.

## Rerun: test galaxy run 24, 17 Oct

Restarted 5:24 AM on the dev build above (run 23's configs; BotPop back to 300 in "all" mode; all 24 squad bots logged in afresh on the new body).

| Check | Result |
|---|---|
| Gate (`Bot-reports/gate/20261017-052926.json`) | **PASS**, 47 of 56 at 5:38 AM, no regressions; none of the 9 failures is a movement failure: prey scarcity (2), Dorn's leash and dance buff (3), one doctor buff (flaky), and three new mission checks (deliver pickup, deliver waypoint, the destroy reward's bank share) |
| Besh hide patrol reached (`besh-harvest.py`) | PASS; two bounces mid-walk absorbed (8.6 m and 11.5 m back) |
| Cresh reaches the mission terminal (`cresh-missions.py`, renamed "Cresh reaches the general terminal" by the missions session) | PASS, all three bots; "reach the mission area" PASS |
| Esk plateau (`esk-routes.py`) | 5 of 5 at 5:33 AM and 5 of 5 at 5:50 AM; Tovan at z 178.9; one bounce absorbed (12.7 m) |
| Dova into the cloning cell, 268 m (failed 3:26 AM) | arrived both ways, 0 corrections (`claude-probe-pathwalk.py`, 5:46 AM) |
| Kneel, then walk 20 m | the body stood up (crouched to upright in 2.6 s), arrived, 0 corrections |
| All reports since the restart | 8 reports, 78 moves, 0 "putting us back" errors, 5 corrections absorbed |
| Server bounces (`[Movement]` lines) | 5, all from the speed check, all in the one stall at 211 s |

Not tested: `/sit` before a walk (the command left the bot upright, so the sitting case did not happen); a bot rooted or with an overloaded inventory (the three-in-10-m limit should still stop it in about 1.5 s); a real client's rubber-band against the new log.

## Still open

- **The server's speed check misfires during stalls, for real players too.** A stall (BotPop logins, a world save, heavy load) bounces anyone walking at full speed, and a real client runs at 5.376 m/s with only the 5.6% allowance, so it is more exposed than the bots. The body now rides it out; a player sees a rubber-band. A server change (for example, judging speed over two validation windows, so a late reference packet and the bunched window after it cancel out) touches the stock anti-cheat and needs the owner's decision and a review before it goes anywhere near live. The `[Movement]` log gives the numbers to decide on.
- **Stale bodies from before a restart** reconnect over and over (about 108 "netStatusTimeout" disconnects per 10 minutes on run 23, C41's packet problem): noise and load in the server log until `squad.py setup` replaces them.
