# C43: Battlefront II (2005) battles and AI for SWG

15 October 2026. **Research/design only. Unimplemented and untested in-game.**

Recommend a small Hoth infantry conquest exercise: three capturable posts, two protected staging areas, finite tickets and symmetric NPC squads. A server controller assigns objectives; existing Core3 AI handles movement and combat. Client bots join as test participants first; population bots follow after their objective strategy and activity policy exist.

## Evidence boundary

BF2 research used public documentation and community descriptions of **Star Wars: Battlefront II (2005)** and its officially released **2006 mod tools**. No installed BF2 files, assets, archives, mission files or binaries were opened/extracted. No tools package was downloaded or run; no leaked source was consulted. Steam ownership does not authorize asset reuse. No BF2 code, geometry, artwork, audio or prose is imported.

The [documentation index](https://sites.google.com/site/swbf2modtoolsdocumentation) identifies released documents but also permits community supplements. These readable transcriptions are strong documentation evidence, with provenance caveats: this pass did not independently authenticate them against a downloaded 2006 package. The index explicitly identifies its game overview as BF1-derived. Do not inherit its outdated hero/class details as BF2 rules.

KYBER in [the screenshot leads](screenshot-project-leads-20261014.md) concerns **BF2 2017**, a different game. It contributes nothing to this design.

Local inspection was read-only, including git as `swgemu`. Observed Core3-dev HEAD: `80895f63dc9d03900e7c840331c4beb29514befe`. Local references describe working files seen during this session, not a whole-tree cleanliness audit. No server/bot commands were sent.

## 1. Documented BF2 battle and bot systems

### Capture, tickets and deployment

A team wins by exhausting enemy reinforcements or holding all posts through a victory countdown. Friendly posts provide deployment; zero owned posts prevents deployment. Infantry occupation changes enemy ownership through neutral to friendly. More friendlies accelerate capture; enemy presence contests it. Vehicle occupants cannot capture. Permanent/destructible posts and mobile posts such as AT-ATs are special cases.

Each death removes one reinforcement. Reserve tickets differ from simultaneous soldiers. Multiplayer deploys on a shared reinforcement timer; single-player permits immediate redeployment. Majority post ownership causes automatic ticket loss. The manual describes a last-stand exception: automatic loss stops when tickets match remaining soldiers, and AI stops respawning. Thus ordinary bleed alone does not necessarily eliminate the last defenders. The manual does not establish universal capture, bleed or victory-countdown constants. [Official Steam-hosted manual, printed pp. 12–13](https://cdn.akamai.steamstatic.com/steam/apps/6060/manuals/BF2_Manual-English.pdf).

The mission guide separates `SetupTeams` active `units`, reserve `reinforcements`, and class minimum/maximum counts. Minimum allocations are filled before remaining slots. Its 20 units/150 reinforcements are examples, not universal limits. `SetSpawnDelay(10.0, 0.25)` is described as an initial delay; the two arguments are not a documented universal wave interval.

Mission Lua loads helpers with `ScriptCB_DoFile`; `ScriptInit` prepares the level and `ScriptPostLoad` starts objectives. Conquest explicitly registers posts with `ObjectiveConquest` and starts it. A placed, capturable post omitted from the objective need not affect victory. [Released-tools Mission Lua Guide](https://sites.google.com/site/swbf2modtoolsdocumentation/battlefront-ii-mission-lua-guide).

A spawn path is a named collection of deployment nodes attached to a post, not the march route soldiers subsequently follow. Capture regions and vehicle-control regions have separate jobs. This distinction is explained in the legacy overview, subject to its BF1 provenance caveat. [Released-tools game overview](https://sites.google.com/site/swbf2modtoolsdocumentation/game).

### Goals and weights

The AI debug documentation shows **Conquest**, **Defend**, **Destroy**, and **Deathmatch**. Conquest pursues post control; Defend/Destroy reference objective objects; Deathmatch provides a combat objective. `aigoals` shows weight, assigned unit count and target. A weight of 200 has twice the documented importance of 100; these are relative priorities, not percentages or damage multipliers.

Three controls must remain separate: **goal weights** allocate effort; **StrategicAttackValue/StrategicDefendValue** value individual posts; **spawn weights** influence deployment location. Example assigned-unit counts are not exact quotas guaranteed in every situation. [Released-tools console documentation](https://sites.google.com/site/swbf2modtoolsdocumentation/consoledebuggingcommands).

The mission guide documents `AddAIGoal(team, goal, weight)` and explains that two equally weighted goals divide team effort. The callback reference names `ClearAIGoals`, `DeleteAIGoal`, planning-arc and barrier controls, but is a declaration list rather than a complete argument guide. [Mission guide](https://sites.google.com/site/swbf2modtoolsdocumentation/battlefront-ii-mission-lua-guide), [callback reference](https://sites.google.com/site/swbf2modtoolsdocumentation/lua_callback_reference).

**Follow needs a distinction:** the released scripting reference documents `followchr` and `stopfollowchr` player AI commands. A public community [Free Camera add-on changelog](https://www.moddb.com/mods/mikes-battlefront-2-mods-maps-collection/addons/free-camera) lists an AI Goals Follow Player 0 control. This supports follow behavior and a community goal control, but this pass did **not** verify the exact stock `AddAIGoal(..., "Follow", ...)` target signature. Do not invent it or claim ordinary conquest automatically escorts a human. [Released scripting reference](https://sites.google.com/site/swbf2modtoolsdocumentation/battlefront2_scripting_system).

### Planning graph, hints and vehicle AI

ZeroEditor uses circular hubs joined by connection corridors. AI travels through intermediate hubs/waypoints and reevaluates its path. Connection filters restrict unit types; weights bias routes. Their default is documented as 100, but the guide supplies no portable numeric cost formula. These weights differ from goal/post/spawn weights.

Planning paths and barriers have infinite height; stacked floors require special authoring. This is inspiration for tactical lanes, not a replacement for SWG's floor/cell-aware navigation. Hint nodes describe local tasks including patrol, cover, sniping, mines and landing. [Released ZeroEditor guide](https://sites.google.com/site/swbf2modtoolsdocumentation/zeroeditor_guide).

AI notes describe vehicle-seeking distance (default 50 m), directed landing hints linked to posts, and transports picking up soldiers at friendly posts and deploying them at hostile ones. Designers must provide safe approaches. Defenders can occupy oriented Defend snipe hints, and nearby original owners can react to a lost post (documented 60 m radius). Movement sizes include SOLDIER, HOVER, SMALL, MEDIUM and HUGE, matched to graph/barrier filters.

The notes distinguish path computation, queue delay and time soldiers actually stand idle awaiting routes. Measure these separately before increasing think frequency. These capabilities do not prove reliable autonomous boarding on every map. [Released AI notes](https://sites.google.com/site/swbf2modtoolsdocumentation/ai_notes).

### Difficulty and scripting

Difficulty combines profile base, Lua adjustment and optional automatic balancing. `SetAIDifficulty(player, enemy)` adjusts each side, optionally for a named profile. `EnableAIAutoBalance`/`DisableAIAutoBalance` control balancing; `aidiff` reports it. The document describes a conquest score gap around 40 triggering adjustments, with infinite reinforcements potentially leaving balancing inactive. It does not enumerate all underlying aim/perception/reaction parameters. Fix difficulty during comparable SWG trials. [Released difficulty notes](https://sites.google.com/site/swbf2modtoolsdocumentation/difficulty).

Mission scripts use events: load callbacks do not imply a per-frame Lua update. Character death/spawn, capture/neutralization begin/abort/finish, regions and timers provide mission triggers. SWG should express the same organization through its own observers and scheduler. [Released scripting reference](https://sites.google.com/site/swbf2modtoolsdocumentation/battlefront2_scripting_system).

## 2. Mapping onto our server

Paths starting `MMOCoreORB/` are relative to `/opt/swg/Core3-dev`. Existing extension points below do **not** mean conquest already exists.

| Verified local piece | Reuse and gap |
|---|---|
| `MMOCoreORB/bin/scripts/ai/templates.lua:39`, `ai/default.lua:15,119,141,253,274,289` | AiAgent trees separate attack, equipment, healing, movement, assistance and root behavior. Reuse existing range, LOS, flee and healing checks. Add an opt-in battlefield goal/tree adapter; retain wildlife defaults. |
| `MMOCoreORB/bin/scripts/ai/eventControl.lua:1` | Patrol/destination checks plus MOVE socket offer event-controlled movement, not a complete squad commander. |
| `MMOCoreORB/src/server/zone/objects/creature/ai/LuaAiAgent.cpp:123,926,949` | Patrol-point/home-location bindings can direct NPCs. Add narrow bindings if objective state cannot be carried by existing ones. Never teleport living fighters to solve routing. |
| `MMOCoreORB/src/server/zone/managers/director/DirectorManager.cpp:433,441,445,466` | Screenplays can schedule events, create observers, spawn mobiles and active areas. A proposed HothConquest screenplay supplies presentation/placement; an authoritative controller owns scoring and roster. |
| `MMOCoreORB/bin/scripts/screenplays/battlefields/battlefield_spawner.lua:70` | Existing markers and no-build/no-spawn areas are placement examples. This file neither implements conquest nor lists Hoth/Ossus. |
| `MMOCoreORB/src/server/zone/managers/gcw/GCWManagerImplementation.cpp:536,943,973,1431` | GCW owns faction-base scoring, patrols, vulnerability and faction checks. Reuse appropriate validation; pilot tickets/post ownership must not flip permanent bases or planetary GCW control. |
| `MMOCoreORB/src/server/zone/managers/collision/PathFinderManager.h` | Tactical graph chooses a lane; existing pathfinder validates actual movement legs. A hub never authorizes walking through walls, roofs or doors. |
| `MMOCoreORB/src/server/zone/managers/botpop/{BotPopManager,BotPopRegistry,ClientlessLogin}.h` | Population bots are transient player creatures, not AiAgents or network clients. Existing batched scheduler needs enrollment, team/role/goal state and a battlefield strategy; attaching NPC trees directly is inappropriate. |
| `MMOCoreORB/src/server/zone/managers/botpop/BotPopLaunchBrain.h:287,390,956` | Current launch brain searches attackable outdoor AiAgents, approaches weapon reach and dispatches hunting/medic/entertainer roles. It is not a general opposing-player selector. Battlefield enrollment must override ordinary hunt/travel/replacement. |
| [squad.py](../tools/bots/squad.py), [crew_combat.py](../tools/bots/crew_combat.py), [escort.py](../tools/bots/escort.py), [gate.py](../tools/bots/gate.py) | Client bots already offer status/look/walk/fight/recovery, group scenarios, combat roles and escort commands. Future conquest scenarios use ordinary join/capture actions; the server owns truth. Client accounts and botpop remain distinct. |

**Activity trap:** `BotPopManager.h:852–905` selects throttled activity using real-player proximity, combat/death and a rotating subset. `BotPopRegistry.h` excludes throttled bots as AI/spawn observers. Separately, `AiAgentImplementation.cpp:3124,3936` can suspend AI without nearby players/follow targets. An NPC-only battle or a remote population-bot squad can freeze. Claude must add a bounded match-specific activity/observer lease and remove it on cleanup. Do not globally enable all-mode/load-testing to solve this.

The newest Claude inbox reports escort out-of-range attacks and uncertain server position corrections. These remain open evidence, not fixes made here. Record attack refusals, route failures and corrections during acceptance.

## 3. Test-galaxy design: Hoth relay exercise

All following numbers and mechanics are **our proposed SWG rules**, not BF2 constants. This is a Blue/Red tactical exercise in the owner's 138–139 ABY setting, not the historical Battle of Hoth or a new canonical battle. Original generic teams avoid asserting a new lore faction/event. A named lore encounter later requires Wookieepedia Legends research and a narrative decision.

### Site and command posts

Choose an outdoor site away from the starport, existing Echo Base tasks, caves and player structures. Read-only existing references: `screenplays/poi/hoth_echo_base.lua`, `hoth_camps.lua`, `hoth_outpost_terminals.lua`, `screenplays/tasks/hoth/`. Do not change those encounters for the pilot. Use already available SWG content only.

Layout is approximately 600 × 400 m. The offsets below are horizontal meters from a **surveyed center, not deployable world coordinates**. Exact location/heights/routes remain a placement deliverable.

| Position | Local offset (x,y) | Initial purpose |
|---|---|---|
| Blue staging | (-280,0) | Protected join/exit/redeployment; not capturable |
| West relay | (-150,0) | Blue post |
| Central relay | (0,0) | Neutral post, multiple approaches |
| East relay | (150,0) | Red post |
| Red staging | (280,0) | Protected join/exit/redeployment; not capturable |
| Four flank hubs | (-75,±100), (75,±100) | Northern/southern alternatives |

Connect West–Central–East, plus both flank routes West–flank–flank–East, with links from the flanks into Central. Survey every leg both ways. All three posts may be attacked at any time; no mandatory linear unlock. Staging counts toward neither majority nor all-post victory.

### Capture state

Lifecycle: disabled → registration → 60-second warm-up → active (20 minutes maximum) → results (30 seconds) → cleanup. One match, authorized test controller, test database/config guard, feature flag off by default.

Each post stores owner {Blue, Neutral, Red}, transition side, progress 0–100 and revision. Check a 12 m capture radius once per second using server positions, same outdoor cell/zone, <=4 m vertical separation and LOS to the post. Count only enrolled, alive, conscious, dismounted participants. Pets/helpers/spectators/ambient creatures do not add capture strength.

Uncontested attackers reduce enemy ownership from 100 to zero, making it neutral, then build their own progress from zero to 100. Rate: 5 points/second with one capturer, 7.5 with two, 10 with three or more. A solo enemy takeover takes 40 seconds; a neutral capture takes 20. Both sides present freezes progress regardless of advantage. Empty areas retain progress for 5 seconds, then decay toward stable ownership/neutral at 5 points/second. Opposing progress on a neutral post must first be erased; owner's defenders can restore damaged ownership at the same rate.

Disable spawns on enemy presence, including neutralization. Restore only after ownership is stable and no enemy is present for 5 seconds. Show owner/progress/contest through terminal/SUI, waypoints and rate-limited messages.

### Tickets, defeat and waves

Start at **180 tickets per side**. Initial deployment is free. Terminal death of any enrolled actor costs exactly one ticket regardless of killer; incap, revival before death, corpse cleanup, failed spawn and administrative removal cost none. Deduplicate by match/actor/life ID. Disable ordinary NPC auto-respawn; only the wave scheduler replaces casualties. Serialize scoring/capture/waves to prevent duplicate charges or post-defeat spawns.

Two or three uncontested owned posts bleed the opponent **one ticket every 10 seconds**. Contested/neutral posts do not count. Clamp bleed at the current living deployed count; at/below that floor stop automatic loss and AI redeployment. Death can still exhaust tickets. This is our simplified BF2-inspired last stand, not an exact implementation.

End at zero tickets or after holding all three posts uncontested for **45 continuous seconds**; any contest/neutralization resets that timer. At 20 minutes compare tickets, then uncontested posts, otherwise draw. Both teams exhausting tickets in the same scoring batch draws. Resolve victory before waves.

Waves share a **20-second clock**. Dead players queue through an event return option after normal death/clone handling; no duplicate living bodies. Choose owned spawn-enabled posts or staging. Staging remains available while tickets permit even with zero posts: an explicit comeback concession differing from BF2.

NPCs choose an enabled owned post with a valid route to their objective, else staging. Provide >=4 surveyed nodes per post/staging, with facing/clearance; never inside capture radii, blocked cells, or within 35 m/LOS of an enemy. Defer unsafe spawns to the next wave without charging tickets. Spawn protection lasts <=5 seconds and forbids attack/capture as well as incoming damage; it ends on leaving the protected node/area.

### Both armies and participation

Each side starts with **12 AiAgent soldiers**: three squads of two rifle, one close-assault and one support. Use symmetric existing SWG templates/equipment. Initially support is an ordinary soldier; enable healing only after its behavior is proven. Pre-CU levels/damage require measurement, not imported shooter values.

Replace at most four casualties per side per wave, maintaining 12 NPCs maximum. Allow **four additional player-creature slots per side**, shared by humans, client bots and later population bots. Hard cap: 32 living participants. First shakeout is 24 NPCs, then one client bot per side, then the owner. Exclude pets from these controlled trials; later pets follow normal combat but create no extra capture/ticket bodies.

Task weights: Capture 100, Defend 60, nearby counterattack 120 for 20 seconds after loss. Invalid tasks are excluded; no capture objective means defend. Normally one squad defends an owned post, others choose by reachable travel cost, threat and existing assignments. Commit for >=10 seconds unless invalid. Counterattack replaces an assignment, never creates extra squads. These are proposed SWG weights, not existing API names. Destroy and Follow remain optional later sabotage/escort objectives.

Humans use a test terminal to view rules/counts and join/leave a team; support group entry and keep player-creature side sizes within one. Do not change permanent faction, profession or accounts. First pilot is cooperative PvE against opposing NPCs. Two-sided player combat stays disabled until Claude builds/tests scoped attackability: roster colors alone cannot make same-faction characters legal targets.

Client bots join through the same interaction on dedicated accounts, with a board driver claim and removal from ordinary squad scheduling. No staff teleport/gear commands during scored play. Population bots join only after an opt-in adapter leases them out of hunt/travel and pins their bounded activity policy. Reject enrollment before that adapter exists; never enroll all transient players automatically.

Leaving/disconnecting immediately removes capture presence; reserve the slot for 30 seconds to reconnect. Never spawn a second life for a still-live object. Leaving forfeits rewards and applies a rejoin cooldown but does not count as death. Controller failure/restart aborts without rewards; match IDs fence stale callbacks. No partial-match persistence in this pilot.

### Rewards and cleanup

Milestone 1 awards only a scorecard. Later proposal: one nontradeable exercise commendation for >=5 active objective/support minutes, plus one for winning; at most one rewarded match per character/day. Bots receive telemetry only. Count capture/defense presence and effective healing of enrolled allies, not repeated attack commands or farmed kills. Idempotent character/match ledger prevents replay payments.

No pilot credits, faction points, rare drops, permanent stat rewards or planetary GCW score. Cosmetic redemption can follow balance work. Cleanup cancels timers/observers, removes event actors/areas, clears temporary combat/activity state and returns participants to a saved safe entry point out of combat, falling back to the existing Hoth arrival point. Never delete ordinary characters/items.

### What Claude must build

| Slice | Required implementation and proof |
|---|---|
| Site/config | Real (x,z,y)/cell placements, both routes and spawn nodes validated; reject invalid startup; preserve existing quests. |
| Controller | Roster, capture state, death ledger, tickets, waves, outcomes, generation fencing and abort. Screenplay handles placement/UI; narrow C++ manager/bindings handle locking/legality/event identity where Lua is insufficient. |
| Enrollment/combat | Join/leave/status UI, outsider exclusion, legal team attacks/support; no permanent faction/GCW mutation. Cooperative PvE first. |
| AiAgent strategy | Opt-in registered tree/goal adapter, squad destinations, bounded pursuit/home, range/LOS and reassignment. Including a Lua file alone does not wire a tree. |
| Activity/spawn | Match-only activity guarantee, bounded path/work budgets, override normal replacement/respawn, release every lease on cleanup. |
| Bot adapter | Authorized join/leave/return/status, post revisions and reason codes. Bots cannot set tickets/owners/progress. Population adapter comes after first acceptance. |
| Evidence/rollback | Death/capture/wave trace, route compute/queue/idle timings, active counts, resource use and correction/refusal counts. Flag plus abort removes encounter. |

ChatGPT's later slice is an offline-tested `tools/bots/scenarios/hoth-conquest.py` plus reports/gate integration, **not written here**. Claude retains dev/build/test-galaxy ownership; live promotion still needs cross-review and owner approval.

Acceptance must cover contest/vertical/LOS exclusion; neutralize/capture/recovery; duplicate deaths; simultaneous defeat; last-stand floor; post lost between spawn selection/execution; unsafe-node deferral; reconnect; cleanup/restart; outsider/pet exclusion; legal combat/support; full bot-only battle without humans. Then repeat seeded symmetric matches with sides swapped and a real-client session. Record ticket conservation, peak actors, denied attacks, capture participation, path idle time, memory/CPU and task growth. Target resolution within 20 minutes and no existing-content effects. No performance/balance result is claimed.

## 4. Behavior upgrades worth doing first

1. **Range/LOS before attacking.** Address reported escort refusals, refresh moving targets and back off bounded retries. Reuse AiAgent checks; improve client/population adapters without weakening server validation.
2. **Stable goals and route recovery.** Capture/defend/follow assignments, short commitment, route timeout and alternate lane. Creatures use den/patrol/return-home goals, not command-post obsession.
3. **Local defense/reaction.** Guards use reachable facing/patrol positions and bounded responses to threats. Creature equivalent: capped pack/den assistance and return leash. Existing notify-help/herd trees are starting points.
4. **Support and retreat by role.** Healers approach legal injured allies then resume tasks; fragile fighters retreat toward reachable home/cover with hysteresis. Preserve pre-CU skills/HAM/species differences.
5. **Visible decisions and bounded scheduling.** Report goal, refusal reason, path compute/queue/idle time and retry count. Guarantee activity for enrolled actors, then measure before scaling. Keep trial difficulty fixed.

Vehicles, transports, mobile posts and sabotage remain optional follow-ons needing separate SWG combat-vehicle, boarding/seat and navigation work. A rideable speeder does not establish tank AI support.

## Research record and open points

Queries: BF2 2005 mod tools AI goals AddAIGoal planning hubs connections; capture/reinforcement bleed/difficulty; exact AddAIGoal + Follow; site-restricted released-document searches. Final evidence is linked documents, not search snippets. No screenshots/game session occurred. `um` was unavailable on checked Windows/WSL PATH, so the skill's KB lookup could not run.

Confidence: official hosted manual is primary gameplay evidence; released-document transcriptions have mirror/supplement caveats; community changelogs establish their own add-on features only. Modern unofficial-extension claims were not used to infer stock internals. The failed Wookieepedia fetch supplied no evidence; this proposal asserts no new canonical encounter.

Open: exact stock Follow goal signature; retail capture/bleed/countdown constants/ties; map-specific vehicle reliability; actual Hoth site/routes; scoped team combat; measured pre-CU balance/activity budget. Do not fill gaps from memory. Further research needs a separate owner-requested pass. This checkpoint claims no implementation, build validation, gameplay success or live readiness.
