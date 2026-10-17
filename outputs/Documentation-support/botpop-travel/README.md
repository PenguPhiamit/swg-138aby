# BotPop travel by ticket and shuttle

16 Oct 2026, Claude (side session). Gap 9 of the [functional test plan](../functional-test-plan.md) and finding 3 of [FINDINGS-2026-10-16](../../Bot-reports/FINDINGS-2026-10-16.md): BotPop's travel was a teleport (`switchZone`), so the shuttle network has never been tested at scale, and run 13 reports "Travel: none".

This folder holds `botpop-travel.patch` against `/opt/swg/Core3-dev` HEAD `8edfd13f`, a check script and a report script.

**Status: untested in game.**
- `check_patch.sh` passes: `git apply --check` against HEAD, and a syntax-only clang 19 compile of `CommandConfigManager.cpp` (the file that includes BotPop) with the dev build's flags from `build/dev/compile_commands.json`, the patched headers in a `/tmp` overlay. 0 errors, 0 BotPop warnings; all 8 BotPop headers came from the overlay.
- Nothing under `/opt/swg` was edited, and the galaxy and bots were not touched.

## What a bot does now

Launch bots (hunters, medics, entertainers; explorers only when forced) travel the way a player does.

| Step | What the bot does | Server code it uses |
|---|---|---|
| Plan | Picks a destination (below). Departure: its town's travel point (a starport for another planet). Arrival: the destination town's travel point. | `PlanetManager::getNearestPlanetTravelPoint` |
| Terminal | Finds the departure point's travel terminal (outdoors, or inside the starport's terminal hall) and walks to it. Outdoors it uses BotPop's routes (`chaseToward`). For the last 60 m into a building it uses `findPath`, which goes in through the door and from cell to cell. | `TravelTerminal::getPlanetTravelPoint`, `PathFinderManager::findPath`, `updateZoneWithParent` |
| Buy | Within 3 m of the terminal, runs the **`purchaseTicket`** command with the arguments the client's purchase window sends (`planet point planet point single`). | `PurchaseTicketCommand::doQueueCommand` |
| Collector | Walks out to the point's ticket collector. | as above |
| Wait | Checks the shuttle every 5 s and waits until it has landed (`checkShuttleStatus`). If the shuttle stands more than 25 m away, the bot steps up to it. | `PlanetManager::checkShuttleStatus` |
| Board | Runs **`boardShuttle`** with the ticket, which is what the collector's radial runs. That command moves the bot. | `BoardShuttleCommand::doQueueCommand` |
| Arrive | Checks the bot is on the ticket's planet and within the landing range + 30 m of the arrival point. It then lives at the destination town, as the old jump did. | — |

**Destinations:**
- When a bot has outgrown its planet or found nothing to hunt for a while, it goes to another planet by tier, as before (`travelOptions`).
- Every 20-30 minutes a bot also makes a trip of its own ("trip"), when it is between things: no target, corpse, mission, rest or dance.
  - One trip in three goes to another city on the same planet (the planet's shuttles).
  - From Tatooine, one trip in four goes to **Nal Hutta** (Bilbousa Starport). It goes only when the `hutta` zone is loaded. Bots on Nal Hutta fly back to a Tatooine city.
- A town with no starport (Anchorhead, for example) first takes the shuttle to the planet's nearest starport. The next trip leaves 30 s after arrival.

**Fallback:** `Core3.BotPopTravel = "teleport"` restores the old jump exactly. In that mode bots make no trips of their own.

## Rows (bin/log/botpop-launch.jsonl)

Every row carries the usual launch fields, plus `from_planet`, `from_point`, `to_planet`, `to_point`, `to_city`, `reason` and `secs` (time since the try).

- **`travel_try`**: one per trip, with `lvl` and `connecting`.
- **`travel_done`**: the bot arrived. Adds `fare`, `topup` (credits added so the bot could pay), `waited` (seconds at the collector), `snaps` (times it was put back outdoors) and `z`.
- **`travel_fail`**: exactly one per failed trip. Adds `step`, `why` (the server's reason), `bought` and `topup`.

| step | Meaning | Example `why` |
|---|---|---|
| `plan` | BotPop found no travel point for the trip. This is not a server fault, but it shows gaps in the destination list. | no starport in or near this town; no travel point at the destination |
| `terminal` | No terminal, or the bot could not reach it within 5 minutes. | no travel terminal for Bestine Starport; no path to the terminal |
| `offer` | **No ticket offered**: the purchase window would not list the route. | route not permitted; no fare for this route; no such destination |
| `purchase` | **Purchase refused.** | short of funds; inventory full; travel coupon window; purchaseTicket refused (code 1, tickets 0 -> 0) |
| `shuttle` | **No shuttle**: none at either end, no collector, or the shuttle never became boardable in 10 minutes. | no shuttle at the destination; never landed in 10 minutes |
| `board` | **Ticket rejected.** | ticket not valid for this shuttle; the nearest travel point is X; boardShuttle refused (code 1) |
| `landing` | **Landing missing**: the bot boarded but came down on the wrong planet or far from the point. | boarded but came down on corellia; came down 140 m from Bilbousa Starport |
| `died` | Killed on the way (the trip ends; the bot revives as before). | killed on the way |

The commands send their reasons as system messages, and a bot has no client to receive them. So the patch makes the same checks each command makes, in the command's order, just before running it (`tripWhyNotBuy`, `tripWhyNotBoard`). A refusal those checks did not predict is logged with the command's return code and the ticket count before and after. That is how the "first purchase after a start fails silently" case (the C7 finding, also seen three times on 15 Oct) will show up.

`/botpop status` adds `travel_tries` and `travel_fails` under `launch`; `travels` now counts arrivals.

## How to test on the galaxy (main session, lock holder)

1. Apply and build: `runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/botpop-travel/botpop-travel.patch`, commit (Agent: Claude), then `tools/dev_build.py`. If HEAD has moved past `8edfd13f`, run `check_patch.sh` first.
2. Start the test galaxy with `--dev-server`, with Nal Hutta loaded, in **all** mode (`Core3.BotPopMode = "all"`). In throttled mode, bots that are not stepped stall mid-trip and end on the 5- and 10-minute timeouts.
3. **Smoke test, about 30 minutes:**
   - Run `botpop launch 60 tatooine`, wait about 2 minutes, then `botpop travel 60`. Forced travel skips the 20-30 minute wait.
   - Expect 60 `travel_try` rows, and within about 10 minutes one `travel_done` or `travel_fail` for each.
   - Run `python3 Documentation-support/botpop-travel/travel_map.py <galaxy bin>/log/botpop-launch.jsonl`.
   - Watch one trip from a client at the Mos Eisley starport: the bot walks into the terminal hall, comes out to the collector, waits, and is gone when the shuttle leaves.
4. **Scale run:** the usual launch run (1,500-1,700 bots, several hours). Each bot makes a trip every 20-30 minutes, about 60-80 trips a minute across the population. `travel_map.py --md` gives the route table for the report.
5. **Pass line** (test plan section 17): every route in the table has arrivals and no `offer`, `purchase`, `shuttle`, `board` or `landing` failures. Each failure row names the route and the reason to fix.

What this cannot cover: what the client shows (shuttle animations, loading screens, the purchase window itself). That stays with Squad (`cresh-travel.py`, `esk-hoth.py`) and the owner's ride.

## Risks

- **Bots now step into buildings (the starport terminal hall).** This is the first BotPop code that changes a bot's parent cell.
  - **Lock order:** it follows `AiAgent::updateCurrentPosition`. The cell-local position is set, then `updateZoneWithParent(cell)` runs (it takes the zone's lock, then the cell's `transferObject`) with only the bot locked.
  - Leaving a cell is `updateZone` through `move()`, which transfers the bot back to the zone.
  - The commands' own cross-locks (inventory, ticket, city) run with only the bot locked, as for a player. No BotPop mutex is held across any object call.
  - This is the C55 F1 lesson: a cross-lock gives the bot's lock back while it waits, so nothing else may be held then. Even so, cell transfers are a new path for BotPop. Watch the first runs for stalls and use the stack-dump routine if the server hangs.
- **A bot inside a building:**
  - While a bot is in a cell, BotPop reads its position as cell-local. Only the trip code runs for it during that time, but `snap` and `travel_*` rows show local x/y while it is indoors.
  - A trip that fails indoors puts the bot back on the spot it walked in from (`tripLeaveCell`, counted in `snaps`).
  - A bot that dies indoors is moved out by the revive.
- **Starport terminals or collectors not found.** `tripFindNear` looks at objects within 150 m of the shuttle and inside nearby buildings' cells. If the snapshot places them differently, the row says `terminal: no travel terminal for …`, and the route table shows it at once.
- **The command's own quirks run for real.**
  - A bot that carries a new-player travel coupon gets the coupon window and no ticket. This is logged as `purchase: travel coupon window`.
  - Tickets from failed trips stay in the inventory, as a player's would.
- **Money:** with `Core3.BotPopTravelTopUp = true` (the default), a bot short of the fare gets the difference in the bank before buying, logged as `topup`. The run then tests the routes, not the bots' savings, but bank totals in the economy numbers include these top-ups. Set it to false to see how often new characters can't afford a ticket (gap 9's stranded player).
- **Nal Hutta:**
  - Its travel point is new (PL-03), and its fares are placeholders. Whether a shuttle and collector exist at Bilbousa depends on its snapshot.
  - Expect `shuttle: no shuttle at the destination` or `terminal: …` rows on that route until the starport objects are in. That is the finding this route is there to produce.
- **Landing elsewhere:** if a bot comes down on the wrong planet, the patch logs it and sends the bot back with the old jump, so it is not stranded. If it lands on the right planet but far from the point, it is logged and the bot stays.
- **Not covered:** group travel, mounts and vehicles (bots have none), player-city shuttleports (none on the test galaxy), round-trip tickets and travel coupons as a feature.

## CPU cost (estimate, not measured)

| Part | Cost | How often |
|---|---|---|
| Trip planning | 2 `getNearestPlanetTravelPoint` scans of the planet's point list (about 10-20 points) | Once per trip |
| Terminal and collector lookup | 1 `getInRangeObjects` (150 m) plus a scan of nearby buildings' cells | Once per travel point for the whole run (cached in `objectByPoint`) |
| Walking | Outdoors: the existing `chaseToward` routes, under the existing 200-routes-per-pass budget. Indoors: 1 `findPath` world→cell and 1 cell→world. | Per trip |
| Purchase and boarding | One command each, the same work as a player's (ticket object creation, `switchZone`) | Once per trip |
| Waiting at the collector | A posture read, then `checkShuttleStatus` (the planet manager's lock) when the shuttle stands | Every 5 s per waiting bot |

- **At 1,700 bots:** one trip per bot every 20-30 minutes gives about 60-80 trips a minute.
- **Trip length:** a trip takes about 3-10 minutes, mostly waiting for the shuttle, so about 200-600 bots are on a trip at any time. Most of them are standing at a collector, and a waiting bot costs less per step than a hunting one.
- **Planet manager lock:** about 40-120 `checkShuttleStatus` calls a second across the galaxy. Each one is a map lookup under that planet's manager lock.
- **Zone switches:** about 1-2 a second, each costing the same as a player's loading-screen jump. The old teleport made about as many when bots outgrew a planet, but far fewer overall.
- **To measure:** compare the `[BotPop]` minute line (`steps X ms per second`, `slowest chunk`, `routes N (M deferred)`) with run 15. Raise `Core3.BotPopTravelMinutes` if steps lose headroom.

## Config (config-local.lua)

```lua
Core3.BotPopTravel = "ticket"       -- or "teleport": the old jump
Core3.BotPopTravelTrips = true      -- a trip of their own every 20-30 minutes
Core3.BotPopTravelMinutes = 20      -- shortest time between two trips of one bot (plus 0-10 minutes)
Core3.BotPopTravelTopUp = true      -- a bot short of the fare gets the difference first
```

`BotPopTravel`, `BotPopTravelTrips` and `BotPopTravelMinutes` are read once, the first time they are needed, so changing them needs a restart. `BotPopTravelTopUp` is read at each purchase.

## Files

- `botpop-travel.patch`: changes `BotPopLaunch.h` (trip state, the Bilbousa city), `BotPopManager.h` (includes, counters, status, config notes, declarations) and `BotPopLaunchBrain.h` (`launchTravel` dispatches to the ticket path, `travelOptions` is shared, and `launchStep` runs trips). Adds the new `BotPopTravel.h`.
- `check_patch.sh`: the two checks. Run it as swgemu: `wsl -d Debian -u swgemu -- bash .../check_patch.sh`.
- `travel_map.py`: the route pass/fail table from a run's log. It is read-only.
