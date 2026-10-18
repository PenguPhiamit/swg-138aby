Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.

# Travel shuttles: tickets, shuttle cycle, boarding

Short names (paths under MMOCoreORB/): PTC = src/server/zone/objects/creature/commands/PurchaseTicketCommand.h, BSC = .../commands/BoardShuttleCommand.h, PMI = src/server/zone/managers/planet/PlanetManagerImplementation.cpp, SDT = src/server/zone/objects/building/tasks/ShuttleDepartureTask.h, SST = .../building/tasks/ScheduleShuttleTask.h, SZC = src/server/zone/objects/building/components/ShuttleZoneComponent.cpp, PML = bin/scripts/managers/planet/planet_manager.lua.

## 1. Short answer
A player within 8 m of a travel terminal sends /purchaseTicket with departure planet and point, arrival planet and point, and optionally "single". Without "single" it is a round trip: two tickets at double fare. Each shuttle stays landed for landed+landing seconds, then is away for the away time. This tree's Lua sets 600+2 s landed and 10 s away for both shuttleports and starports. Boarding (ticket collector option 20) needs a travel point within 128 m, the shuttle within 25 m, no mount, a ticket from this point loose in the inventory, and the shuttle in its landed window. Until a shuttle is first scheduled (default 5 min after a start), purchases get the new "temporarily unavailable" messages (commit 7267cf3c, 14 Oct). Boarding then fails with no message at all.

## 2. How it works
**Buying**
- Terminal option 20 sends EnterTicketPurchaseModeMessage. If the terminal has no travel point, there is only a server error log (TT = src/server/zone/objects/tangible/terminal/travel/TravelTerminalImplementation.cpp:13-28).
- Needs a travel terminal within 8 m, else "@travel:too_far" (PTC:34-48). Banned from the current city: "@city/city:city_cant_purchase_ticket". Player cities add a travel tax (PTC:55-62).
- Arguments: four tokens, with underscores turned into spaces. A fifth token "single" or "0" makes a one-way ticket (PTC:74-96). A parse error or an unknown planet fails with no message (PTC:89-91, 107-109).
- Unknown destination point: "@travel:no_location_found". Unknown departure point: "The given departure point was not found." (PTC:114-122).
- No shuttle linked at the departure point: "Travel from your departure point is temporarily unavailable. Please try again shortly." (PTC:126-129). No shuttle at the destination: "Travel to your destination is temporarily unavailable..." (PTC:137-142).
- Banned from the destination city: "@city/city:banned_from_that_city" (PTC:146-151). A route that is not permitted fails with no message (PTC:154-158). Permitted means: both points exist, the arrival point allows incoming travel, and both points are interplanetary if the planets differ (PMI:684-713). A fare of 0 gives "Invalid travel route specified." (PTC:160-165).
- Inventory: if (1 or 2) plus the recursive item count is over the limit, "@error_message:inv_full" (PTC:170-176).
- A one-way purchase with a new-player travel coupon opens a coupon SUI and returns a failure; the ticket comes from the SUI callback (PTC:180-221). The coupon loop never checks the last inventory slot (PTC:187).
- Funds: the bank pays first and cash pays the rest. If both are short: SUI "You do not have sufficient funds for that." and "@travel:short_funds" (PTC:224-242).
- Success: "@base_player:prose_pay_acct_success", then the ticket(s) arrive, then the city tax message if any, then SUI "@travel:ticket_purchase_complete" (PTC:274-323). Ticket template: base_travel_ticket.iff, which holds the departure zone and point and the arrival planet and point (PMI:1456-1478).

**Shuttle cycle**
- When a shuttle enters the zone, it is scheduled after 500 ms. During server load it is scheduled once BootDelay has passed since the start: config Core3.ShuttleZoneComponent.BootDelay, in ms, default 300000 (SZC:42-60). While loading, it retries every 1 s (SST:33-36).
- The task links the shuttle to the nearest point within 128 m: starport timing if the point is interplanetary, else shuttleport. A duplicate shuttle is destroyed. With no point within 128 m it only logs an error, and the shuttle is never scheduled (SST:76-96). Player-city shuttles always use shuttleport timing (SST:57-74).
- scheduleShuttle sets the shuttle upright (landed). Its first departure comes landed+landing seconds later (PMI:1579-1610). Each later run turns an upright shuttle prone (away) for the away time, and a prone one upright for landed+landing (SDT:53-59, 116-126).
- The Lua globals are read at load (PMI:158, 209-227); PML:44-53 sets away 10, landing 2, landed 600. The C++ fallbacks apply only when a value is ≤0: shuttleport 300/11/120, starport 60/14/120. The comments at SDT:117-129 still describe those old numbers. Config keys Core3.PlanetManager.*Time are read only under DEBUG_TRAVEL (PMI:229-236), and no define was found in src or bin/conf.

**Boarding (BSC)**
- The collector's option 20 runs boardShuttle with no ticket (TicketCollectorImplementation.cpp:42-43). A ticket's own option 20 and the selection list pass that ticket instead (TicketObjectImplementation.cpp:20-27, TicketSelectionSuiCallback.h:37-39).
- Checks run in this order:
  1. state and locomotion (37-41);
  2. no travel point within 128 m (2D, PMI:761): "There is no shuttle nearby." (53-60);
  3. no shuttle at the point: "Travel from this location is unavailable at this time." (62-71);
  4. shuttle more than 25 m away: "@player_structure:boarding_too_far" (73-76);
  5. mounted: "@travel:no_pets" (78-81);
  6. no top-level inventory ticket whose departure is this point: "@travel:no_ticket" (84-90, 257-283);
  7. shuttle status, skipped at Theed Spaceport (94-97).
- The shuttle status check (step 7) has three outcomes:
  - no task: fails with no message (PMI:1486-1489);
  - away: "The next shuttle will be ready to board in N minutes and N seconds." (PMI:1494-1513);
  - landing: "The shuttle is about to begin boarding." (PMI:1514-1516).
- Several tickets and no ticket chosen: "@travel:boarding_ticket_selection" plus a "Select Destination" list. The command reports success, but nobody travels (108-112, 288-316).
- A ticket owned by someone else, or one for another departure point: "@travel:no_ticket" (115-126). Arrival planet gone: "@travel:route_not_available". Arrival point not reachable from here: "@travel:wrong_shuttle" (131-143). City bans block it too (145-171).
- Success: the player changes zone near the arrival point. The spot is randomised within landingRange: 3 m at shuttleports, 6 m at starports (PML:61-73). The ticket is destroyed (232, 247-251). There is no success message.
- Landing window (inferred): seconds remaining = time to the next run + 1 (SDT:62-66, with Time::miliDifference = now minus t in utils/engine3/MMOEngine/src/system/lang/Time.h:423-424). By SDT:79-109, "about to begin boarding" then lasts about 2×landing+1 s after touchdown (about 5 s here). Boarding is open for the remaining ~597 s.

## 3. What a bot test should check
- **Setup:** the server has been up longer than BootDelay. The bot is ≤8 m from the terminal; starport terminals are indoors and need locate (esk-hoth.py:23-41). It has enough credits, free slots and no mount. Point names use underscores, plus "single" (cresh-travel.py:27, esk-hoth.py:46). The route is allowed.
- **Purchase:** exactly one new ticket item (two if a round trip); credits down by the fare plus any tax; the pay-success message; the ticket_purchase_complete SUI.
- **Boarding:** stand ≤25 m from the shuttle and use collector option 20. Success means the zone or position changed to within landingRange of the arrival point, and the ticket left the inventory. Both scenarios check only the position. With several tickets, answer the list. On "ready to board in N", wait N+6 s and retry.

## 4. Why a test sees no effect, and how to tell
- **No ticket and no text after purchaseTicket:** the route is not permitted, the planet name is wrong, a parse error, or the coupon SUI is open. Compare the SUI pages before and after, and look for a command_failed event (the scenarios read those, cresh-travel.py:36).
- **"...temporarily unavailable...":** the shuttle is not linked yet (inside BootDelay). If it persists, no shuttle is within 128 m of that point; the server log has "Planet Travel Point (travelPoint) has a nullptr".
- **Boarding with no message:** the shuttle has no task yet (inside BootDelay), or a state or locomotion failure.
- **"There is no shuttle nearby." vs "boarding_too_far":** more than 128 m from the point vs more than 25 m from the shuttle.
- **"no_ticket":** the ticket was bought at another point, is inside a bag, or the departure name does not match.
- **"ready to board in N" vs "about to begin boarding":** the shuttle is away vs landing. Both are timing; retry.
- **"wrong_shuttle" / "route_not_available":** the destination cannot be reached from this point.
- **"Select Destination" list but no travel:** the bot holds several tickets.

## 5. Open questions
- The 30 s first delay on the test galaxy: no BootDelay override exists in MMOCoreORB/bin/conf or src (grep, 15 Oct), so it must be set elsewhere. Even at 30 s it only delays linking; that gives about 30 s of "unavailable", and the first departure comes ~602 s later.
- Does the running server use this tree's PML (600/2/10)? The runtime copy was not checked.
- What the real client UI sends as /purchaseTicket arguments; the client-side text of the "@travel:..." strings.
- Not read: TravelCouponUseSuiCallback.h, and the radial-menu range of the collector and terminal.
- The landing-window arithmetic is not verified live.


## ChatGPT's review (2026-10-18 02:26)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** purchase argument parsing, 8 m terminal check, fare charged bank-first, coupon branch, availability messages, 612-second cycle components (600+2 landed/10 away), 128 m travel-point and 25 m shuttle checks, direct inventory ticket scan and zone-switch/ticket destruction hold (PurchaseTicketCommand.h:34-96,105-178,224-323; BoardShuttleCommand.h:53-171,232-283; planet_manager.lua:44-53). The old timing comments must not override Lua values.

**Corrections/qualifications:**
- The short answer says boarding during initial linking fails without any message; no linked shuttle actually sends 'Travel from this location is unavailable at this time' (BoardShuttleCommand.h:62-70). A linked shuttle without its departure task is the separate silent checkShuttleStatus path.
- Round-trip cost is 2*(baseFare+departureTax), not two base fares plus a single tax (PurchaseTicketCommand.h:178,224-225,308-315). Pay-success reports base fares only (274-276); tax is a separate message.
- Inventory scanning only finds loose tickets, but explicit chosen-ticket validation uses isASubChildOf(creature), not direct-parent equality (BoardShuttleCommand.h:114-126). A blanket claim that every nested ticket is always rejected is too strong.
- Landing duration arithmetic in ShuttleDepartureTask.h:62-109,116-125 supports the draft's roughly five-second landing exclusion under 600/2; this is source timing, not a measured service guarantee. Randomized arrival can fall back to the raw arrival point (BoardShuttleCommand.h:196-218).
- The BootDelay override's source is outputs/tools/test_galaxy.py (SHUTTLE_BOOT_DELAY_MS and the generated Core3.ShuttleZoneComponent config). Its absence from tracked bin/conf does not imply it is absent at runtime.

**Not established:** the running config, actual coupon/UI behavior, exact client text and current scenario coverage. Purchase text alone is insufficient: require ticket receipt and actual credit delta.

**Verdict:** Mostly supported; correct initial-boarding message, doubled tax, explicit ticket qualification and generated BootDelay configuration; runtime untested.
