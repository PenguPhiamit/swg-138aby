# Bot cities: M1 disposable-town probe plan

16 Oct 2026 — ChatGPT, C52. **Plan only; unimplemented and untested.** Authority: the owner's Q1-Q13 answers of 16 Oct 05:40 in [the board](../SWG-handoff.md), recorded beside [the research questions](player-cities-research.md#owners-questions). Technical starting points are that research's Core3-dev `8b48a044` snapshot, sections 2 and 3; Claude must check the current source before implementing. The board reports a CitiesAllowed guard in run 10; verify that implementation rather than assuming it still needs writing.

## Scope and ownership

M1 proves one disposable town, starting with a mayor and four settlers, on one eligible planet. Persistent example towns wait for a later staff Town Keeper design. This plan does not authorize running commands, building, restarting, or deploying anything.

Claude alone holds the test galaxy and `/opt/swg/Core3-dev`; Claude performs all server integration, builds, bot commands and runtime probes. ChatGPT reviews the implementation and offline reports; any later assigned source work belongs in `/opt/swg/Core3-gpt`, never the dev tree. There are two agents only: Claude Opus 5.5 and GPT 6.1 Sol; Fable is retired. Run any later `/opt/swg` searches/git in WSL through script files as `swgemu`, never the network share. Any eventual build uses `nice -n 10`, at most `-j4`, under Claude's scheduling.

## Owner decisions as implementation constraints

| Answer | M1 requirement |
|---|---|
| Q1 | Disposable simulation towns and every associated object first; no persistent Town Keeper yet. |
| Q2 | One simulated week = 6 minutes in the test copy only. No shipped/live clock changes. |
| Q3 | At most 30% of city slots per planet; exclude the planet the owner is testing. Apply quotas to every cumulative rank cap, not merely founding slots. |
| Q4 | Political XP grants only in explicitly labeled accelerated runs. Baseline earns XP naturally; log every grant. Prefer XP plus normal training checks over directly granting ability flags. |
| Q5 | Bot donations and logged treasury top-ups; keep a no-top-up baseline. `maintenanceDiscount` stays 0.5. |
| Q6 | Monthly Home Show / Best Dressed City with a modest credit prize. Contest administration is later; no badge or posting is implied. |
| Q7 | Test `DecorationsPerRank = 30` (30/60/90/120/150), zero city-decoration upkeep. Keep other upkeep and placement prices unchanged. |
| Q8 | Clone Lab and Entertainment District must work using configured values, presently `private_spec_cloning` +20 and `private_spec_entertainer` +10 in the research snapshot. |
| Q9 | CitiesAllowed safety guard only; no player cities on Hoth or Ossus. Missing and zero entries safely refuse. |
| Q10 | No terrain edits. Select naturally suitable land and reject unsuitable sites. |
| Q11 | Pilot of 10 static event props per city. Keep its counter separate from city decorations. |
| Q12 | 138-139 ABY names/themes from our own lists; run normal name/uniqueness checks; no copied player or guild identities. |
| Q13 | No citations or implementation dependencies from the excluded city pages. The revised research retains the other evidence. |

## First three probes: gates before a town rollout

Run in this order, with isolated disposable fixtures and recorded cleanup. A failure stops dependent city work; it is a finding, not permission to skip the check.

| Order | Risk and test | Required evidence / pass condition |
|---|---|---|
| P1 | **Maintenance destroys transient owners' structures.** Research F7: `StructureMaintenanceTask::run` looks up a player name and credit object; transient bots may have neither. First reproduce with a bot-owned house, then exercise the proposed disposable path. Trigger the actual task in isolation; a six-minute city update does not prove weekly house maintenance. Include a normally owned control. | Record owner identity resolution without secrets, credit-object presence, structure IDs, task branch/reason, condition and balance before/after. Disposable structures survive while their owner is active; normal ownership/maintenance checks still apply to the control. Teardown removes the house and ownership references; a Claude-controlled test restart leaves no orphan objects or database rows. |
| P2 | **Update jitter overwhelms the six-minute week.** Research F2: rescheduling adds random 0-30 minutes, although the first update has no jitter. Test initial and at least six subsequent updates and a three-cycle election. | Exactly one update source per city; no stock-jitter delay, duplicate update or double charge. Log due/actual wall-clock times, simulation week, rank, XP, election and upkeep. Demonstrate rank 5 at update 4 when funded and eligible, and election at the configured cycle. |
| P3 | **Slot caps block humans or promotions.** Verify the existing guard, missing/zero keys, Hoth/Ossus refusals, total cap and cumulative rank caps; exercise boundary reservations and concurrent requests. Prefer isolated counter fixtures for exhaustion over filling a planet with towns. | Last permitted reservation succeeds; next refuses without consuming deed/credits/slot. Human occupancy still blocks physical caps; bot use never exceeds floor(0.30 x cap) at any rank. Promotion rechecks quotas; teardown/failure releases reservations. No planet is enabled to test a refusal. |

For P1, Claude should use a narrowly scoped test-only ownership/credit resolution path for registered disposable bot owners if the failure is confirmed. Do not globally ignore missing owners, disable maintenance, persist bot characters just to evade the check, or assume non-persistence alone fixes it. Unresolvable owners still trigger controlled cleanup. Probe bot logout/despawn separately from restart: none may leave houses behind.

For P2, prefer a test-only city-clock override that makes the interval six minutes and jitter zero for registered simulation towns, while preserving normal scheduling elsewhere. Keep settings in the disposable test copy and fail closed outside `isDisposableTestGalaxy()`. If manual updates are used instead, cancel/suppress the automatic timer first and prove one update/charge per week. Do not run both mechanisms. Clock mode and all overrides go in the run manifest.

Only the city week is approved for compression. Record founding assessment, specialization cooldown, election registration, residence changes and house maintenance as separate real-time clocks. Initially satisfy them naturally or use fresh isolated fixtures. The older research's suggested compression of grace periods and withdrawals is not an owner decision. If an additional override becomes necessary, surface it for a decision before using it. House maintenance remains real-time; its weekly equivalent is reported separately and P1 invokes the task explicitly.

## Slot budget and siting

Use the current server's cap table as authority; the snapshot provides these expected budgets. Count cities at rank r **or higher** for each rank-r cap.

| Planet group | Server caps, ranks 1-5 | Maximum bot occupancy, ranks 1-5 |
|---|---|---|
| Corellia, Naboo, Tatooine | 20 / 20 / 15 / 10 / 10 | 6 / 6 / 4 / 3 / 3 |
| Dantooine, Lok, Rori, Talus | 50 / 50 / 30 / 20 / 20 | 15 / 15 / 9 / 6 / 6 |
| Zero/missing entries; Hoth, Ossus | forbidden | 0 |

For each rank, require both bot-count-after <= floor(0.30 x configured cap) and total-count-after <= configured cap. Reservations count as occupancy until committed or released. Founding and promotion check under the appropriate lock so two requests cannot take the final slot. Actual human cities reduce physical free space; quotas do not guarantee bots a minimum allocation. Deny a town on the owner's current test planet; if that planet changes, pause and have Claude clean up that town before the human test.

Select one eligible planet with Claude after checking human activity. Reuse the census technique on that planet; Ossus sampling is a method reference only. Score natural ground through the rank-5 footprint, water, slope, approach paths, no-build regions, NPC/player-city spacing, lairs and actual building footprints. Keep the stock validation at placement. Try another natural site on rejection; never flatten terrain or add a CitiesAllowed entry. Use a small original frontier layout and names from our own lists, validated on the server.

## Ordered implementation handoff to Claude

Each step has a reviewable source change and its own evidence. No broad city fleet until steps 1-5 pass.

1. **Preflight and instrumentation, server first.** Recheck current `CityManagerImplementation.cpp`, `CityRegionImplementation.cpp`, `StructureManager.cpp`, placement sessions, `StructureMaintenanceTask.cpp`, `city_manager.lua` and `managers/botpop/`. Confirm the run-10 guard. Add a default-off disposable-test-only city flag, unique run/town IDs, bounded counts and an explicit teardown entry point. Record config/cap snapshots and object IDs without account secrets. Run all actions through queued tasks rather than inside a locked bot brain step; establish lock order from current source. Use no client SUI path for client-less bots.
2. **Disposable ownership lifecycle, then P1.** Build a placement variant that retains normal placement checks but creates the hall, houses, civic structures, city region/subregions and props non-persistently. Check construction-session persistence too; changing only the deed is insufficient. Register active transient owners and their credits in the narrow test path described above. Track every created object and task. Cleanup cancels timers, destroys the city plus all citizen houses/cell contents/deeds/props, removes residence/owner references, nav regions and quota reservations; `destroyCity` alone leaves houses. Cover failed construction, despawn, mayor death and explicit stop. Prevent silent replacement of mayor/settlers with new IDs. Pass P1 before proceeding.
3. **Test clock and trace, then P2.** Implement the six-minute/zero-jitter override or a single manual scheduler, with test-copy gating and timing logs. Preserve the normal interval/jitter outside it. Verify election cadence and no duplicate upkeep or political XP. Do not call ordinary force-update repeatedly while an automatic timer remains armed.
4. **Quota reservation and natural-site selector, then P3.** Add guarded founding/promotion checks, cumulative rank accounting and exclusion of the owner's test planet. Enforce Hoth/Ossus refusal in the common path as well as the bot wrapper. Implement bounded site retries, normal name/planet/footprint validation and rollback of partial placement. Pass P3 and a failed-placement cleanup probe.
5. **Bot city state machine and first town.** Add town-bound mayor/settler roles to the launch simulation: validate site -> train Novice Politician with accounted credits -> deed/place hall -> await completion -> open zoning or grant it -> serialize four house placements -> declare residence -> await assessment -> observe updates. Preserve skill, lot, rank and zoning checks; construction's temporary no-build circle must expire before nearby placement. Five citizens should progress one rank per update at the {1,2,3,4,5} thresholds. Keep initial grant/deed cost visible; never silently reset purses. Stop safely on failed gates or lost owners.
6. **Economy and paired modes.** Add logged donations, taxes, treasury sampling and an explicit top-up switch/floor. Verify `depositToCityTreasury` uses cash-left semantics and debit exactly the intended donation, including any bank-to-cash transfer. Run baseline and support variants below on matching sites/seeds and manifests. Retain upkeep x0.5. Log each top-up with source, amount, reason, before/after balance and simulated week. Never report support credits as earned income.
7. **Configured specialization consumers.** Find and review the intended gameplay units of cloning +20 and entertainment +10 in the current templates/client descriptions. Add actual server consumers in cloning/entertaining logic at their intended scope, remove effects on departure/spec change, and avoid double stacking. Do not reinterpret them as a new discount percentage, sickness duration or buff formula without evidence; unresolved semantics need a decision before coding that consumer. Use normal rank/ability/cooldown checks. Test otherwise matched off/on subjects, both configured values and a changed test fixture value, then removal and affordability failure. A skill mod appearing in a list is insufficient: cloning outcome and entertainer outcome must change as specified. Label XP-assisted fixtures accelerated.
8. **Decoration and static-prop pilot.** Test 30 city decorations per rank and zero **decoration** upkeep through a separate setting/consumer; keep terminals, trainers, civic structures and the 1,000-credit decoration placement price at their current values. Update the maintenance report to agree with deductions. Check the exact cap and one beyond, and preserve rank-demotion cleanup. For props allow at most 10 static event-prop instances per town from an approved template list, no actors/guards/games/recruiters; maintain separate counting, zoning/removal rules and footprint checks. Pin rental lifetime only for the registered test-town props; no global rental change. Verify prop 11 refuses, removal frees a slot, props survive their old expiry, and teardown removes them. Disposable means no persistence across restart even when pinned for a run.
9. **Reporting and acceptance.** Extend SimLog with city lifecycle, rejected actions, timing, rank/citizens, XP, grants, donations/taxes/top-ups, upkeep/decay, specialization outcomes, decorations/props, object counts, navmesh cost, process memory and step latency. Claude supplies the bot-city controller/events and runtime output; the offline Python reader produces a baseline/support comparison and cleanup inventory (ChatGPT may take that reader in a separately claimed implementation task). Claude runs a small in-game acceptance under the lock; ChatGPT cross-reviews the diffs and evidence. Persistent towns, shops, fleet scaling and a public contest remain later work.

## Run matrix and acceptance

Use matched initial credits/deeds, citizen count, site recipe and observation window. Start with one town at a time; record actual clocks and every departure from defaults.

| Run | Political progression | Donations | Treasury top-ups | Purpose |
|---|---|---|---|---|
| B: baseline | natural XP and paid training | on, logged policy | off | measure affordability, rank/ability lag and actual decay without support |
| T: treasury support | natural XP and paid training | same policy | on, logged floor | isolate treasury support from baseline |
| A: accelerated fixture | explicit logged political XP grants, normal skill checks | same policy | on, logged floor | reach civic/spec/decor/prop acceptance within a practical test; not an economy baseline |

Suggested donation policy: at each city update when treasury runway is below two weeks, offer 25% of each settler's available balance, with explicit funds-transfer accounting. Suggested support floor: two upcoming city-upkeep charges, topped up before the next charge. Both are proposed reproducible test parameters, not changes to the owner's upkeep setting. Record how estimated upkeep differs from actual deductions. Include a funded control when a baseline town decays; do not rescue the baseline silently. Never allow negative treasury just to force rank progression.

M1 passes only when P1-P3 pass; a funded eligible five-citizen town reaches rank 5 at update 4 with one update per six-minute week; the no-top-up baseline remains distinct; decorations and the 10-prop pilot satisfy caps/costs/cleanup; both specialization consumers demonstrate their configured effects; and explicit teardown plus a Claude-controlled restart leave no orphaned objects or changed normal-world clocks. Record a visual client check of placement, access and props when the owner is at the PC and has logged in. Until runtime/client checks exist, describe the implementation as untested or partially tested.

Measure navmesh generation, RSS/object count and bot step latency against the no-city control; choose scale limits from those measurements rather than inventing a performance pass threshold. Stop on ownership loss, unexpected persistence, duplicate updates, cap breach, forbidden placement or resource pressure. Claude decides when a restart fits the existing run and owner constraints; this plan never commands the galaxy.

Deliverables: reviewed server/bot commits, run manifests and JSONL, B/T/A comparison, the three first-probe results, specialization before/after outcomes, decoration/prop boundary results and a zero-orphan cleanup report. Next decision after M1: whether disposable-town results justify a persistent Town Keeper prototype. Monthly contest details and a modest prize can be drafted locally afterward; posting still needs the owner's explicit go.
