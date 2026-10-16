# C44: independent launch-simulation and mission review

15 October 2026, ChatGPT. **Changes requested before promoting the mission-limit change; bot fixes and measurement are also needed.** Read-only source review, not live approval or an in-game pass. No new crash was reproduced and the cause of the historical RSS growth is not established.

Reviewed `024a4bdc`, `cbb8fc10`, `41764180`, `17cacd70`, and `7bd915b6`, with `git log --oneline 8a00b08b..7bd915b6` for context. `/opt/swg/Core3-dev` was clean at full HEAD `7bd915b62e22df627a195e7044f85d0b5d262466`. Git and source searches ran as `swgemu` inside Debian through a script on the Windows filesystem. Nothing under `/opt/swg` was written; no build, debugger attachment, bot command, console command, restart, or galaxy operation was performed. Claude retains the server lock and driver claim.

Locations below are relative to `/opt/swg/Core3-dev/MMOCoreORB/`; `B/` abbreviates `src/server/zone/managers/botpop/`. They refer to the reviewed HEAD. P2 means a correctness/safety issue to fix; P3 means a bounded-impact maintenance issue. Findings are ranked by live impact, cleanup/safety impact, then simulation accuracy. Cases below are source-derived counterexamples, **not executed gameplay reproductions**.

## Ranked findings

### F1 — P2: more than two crafting missions can remove another mission's recipe

**Location:** `src/server/zone/managers/mission/MissionManagerImplementation.cpp:270`, with the two-mission assumption at `:340` and `:347`–`:359`.

The total-cap and bounty condition itself is sound for a positive setting of 5 or 6. However, `createCraftingMissionObjectives` remembers only the last other crafting mission's schematic and avoids that one recipe. Previously there could be only one other crafting mission. With six slots it can select a recipe used by an earlier mission.

**Failing case:** accept crafting missions A and B, then accept C when the random selection chooses A's recipe. The loop leaves B in `missionItem`, so C keeps A's recipe. Collect the resources/schematic for A and C, then abort one of them. `CraftingMissionObjectiveImplementation.cpp:83`–`:101` removes the schematic by template, and `PlayerObjectImplementation.cpp:1291`–`:1297` removes the whole entry. `objects/player/variables/SchematicList.cpp:55` adds duplicate mission quantities, but `:70` drops the whole rewarded-schematic entry. The surviving mission loses its available recipe. The use-count path also merits checking: `SchematicList.cpp:75` returns true after decrementing a shared quantity, and the caller removes the visible schematic on true.

**Suggested fix:** collect every active crafting schematic and choose from the unused set, handling exhaustion explicitly. Alternatively, keep a separate two-crafting-mission cap until recipe grants/removals are mission-scoped or correctly reference-counted. Keep the requested total of six. Test A/B/A, abort either A, craft both copies, and relog. This is a server-side live-change dependency; testing only six destroy missions will miss it.

### F2 — P2: despawning a bot can leave its mission lair and expiry task behind

**Location:** `B/BotPopManager.h:340` and `:332`–`:337`; lifecycle introduced into the launch workload by `B/BotPopLaunchBrain.h:1349`.

`ClientlessLogin.h:60`–`:63` unloads the bot. `PlayerObjectImplementation.cpp:345` deactivates missions; `MissionManagerImplementation.cpp:2316` calls objective `deactivate`. Destroy objectives inherit the base implementation (`objects/mission/MissionObjective.idl:103`), which only resets `activated`. Fifteen seconds later bot deletion recursively deletes mission database objects, but it does not call `mission->abort()`.

**Failing case:** a bot accepts a destroy mission, approaches until its lair spawns, then is despawned before finishing or aborting. `DestroyMissionObjectiveImplementation.cpp:222` disables the lair's no-player despawn. Its database destructor (`:28`–`:40`) destroys the spawn area, not the lair. Lair removal is in `abort` (`:259`–`:288`), which this teardown never invokes. Thus a permanently deleted owner can leave a live lair and its defender population. Destroying a mission observer's database entry only marks it for deletion (`MissionObserverImplementation.cpp:21`); it is not a lair teardown operation.

The objective's destruction also omits `clearFailTask`: the expiry task remains scheduled for up to two days (`MissionObjectiveImplementation.cpp:68`; `MissionObjective.idl:38`). **Its mission link is weak** (`events/FailMissionAfterCertainTimeTask.h:19`), so this is retained scheduled-task overhead, not proof that it pins the entire bot graph.

**Suggested fix:** after draining in-flight steps, explicitly abort/remove every datapad mission during permanent bot teardown, using the normal bot/mission locking convention. This administrative cleanup must work even when the bot is fighting; do not rely on the user-facing abort method silently succeeding. Cancel expiry tasks and verify mission lairs, defenders, spawn areas, and observer registrations disappear. Make objective destruction defensive/idempotent if appropriate. Ordinary player logout must retain its resumable missions.

**Measure:** after an authorized future teardown, compare world mission-lair IDs/owners, associated defenders, mission objectives/observers, expiry-task counts, and pending deletion counts before despawn, after the 15-second grace period, and after cleanup/GC. Repeat spawn/accept/despawn without restarting. This cannot explain runs 2/3, which predate missions; it can contaminate later runs in the resumed test world.

### F3 — P2: bots follow stale mission coordinates and can attack an unrelated lair

**Location:** `B/BotPopLaunchBrain.h:1235`–`:1265`, with the one-time coordinate capture at `:1343`–`:1344`.

The destroy objective relocates the actual lair after the owner reaches its spawn area. `DestroyMissionObjectiveImplementation.cpp:96` initially tries an offset of up to 256 m on each axis, can widen its search, and updates both the waypoint and mission start position at `:163`–`:175`. The bot never refreshes its cached coordinates. At the old point it accepts the first lair within 150 m, without relating that lair to its own objective.

**Failing case:** the bot stops 20 m from the original point; its own lair spawns 240 m on the opposite side. It waits at the old point until timeout. If another hunter's or a wild lair is within 150 m, it selects that instead. Destroying that lair does not complete this mission and can pay another owner. When a chosen lair vanishes, `:1277` overwrites the cached target with the bot's current position, compounding the problem.

**Suggested fix:** obtain a locked snapshot of the accepted mission/objective, refresh its actual waypoint, and resolve the actual objective-owned lair ID. Add a read-only accessor if needed; avoid identifying ownership by proximity or name. Revalidate parent, mission type, zone, and completion after lock transitions. Log mission ID plus objective/lair ID so distance and ownership can be audited.

### F4 — P2: the pass-overlap guard does not cover logout or deletion

**Location:** `B/BotPopManager.h:774`–`:823`, compared with the late `outstanding` check at `:871` and scheduling guard at `:945`.

The guard prevents scheduling another worker pass, but the tick first releases/deletes leaving bots and processes logouts. `runChunk` already holds references to its states. Bot locks serialize individual operations, but cross-locking operations can temporarily release that bot lock; there is no cancellation flag or drain barrier covering the rest of the step.

**Failing interleaving:** a worker enters mission processing while online, releases the bot lock while acquiring a terminal/mission cross-lock, and the tick logs that bot out. The worker then resumes its already-started step and can accept/create a mission objective after unload has deactivated existing missions. A queued chunk can also retain a state after removal from `bots`. The 15-second deletion grace is a time estimate, not proof that every worker has finished. Strong references protect allocation lifetime; they do not make an offline/deleted character valid for new work. No use-after-free or crash is claimed as reproduced.

**Suggested fix:** defer lifecycle mutations until the previous pass is drained, or mark a state as retiring before logout and make steps revalidate after cross-lock transitions. Deletion must await completion of all tasks that can act on that state. Do not wait while holding manager or creature locks. Validate with a deliberately stalled worker plus despawn, including a stall exceeding 15 seconds, on a future authorized test.

### F5 — P2: a refused abort is treated as successful and loses mission tracking

**Location:** `B/BotPopLaunchBrain.h:1225`–`:1232`.

`handleMissionAbort` returns void and refuses an incapacitated/in-combat player (`MissionManagerImplementation.cpp:534`–`:542`). The bot clears `missionID`/`lairID` regardless. Although the hunt path often leaves combat before reaching this branch, an attacker can put the bot back into combat during the mission cross-lock transition; the method's refusal remains a real possible outcome.

**Failing case:** the 20-minute timeout fires, the cross-lock releases the bot briefly, an AI attack establishes combat, then abort returns without removing the mission. The bot forgets it and later takes another. Forgotten objectives/lairs remain until completion, real expiry, or teardown; after six outstanding missions accepts fail even though the brain believes it has none. Forced travel also preserves `missionID` (`:894`–`:923`), so the brain can chase another planet's mission coordinates on its new planet.

**Suggested fix:** after abort, recheck that the mission actually left the datapad; preserve tracking and retry on refusal. Reconcile all active datapad missions rather than trusting a single scalar. Define travel behavior for an active mission and record the actual abort outcome. For permanent deletion use the cleanup described in F2.

### F6 — P2: trainer bank withdrawals turn successful missions into “mission_gone”

**Location:** `B/BotPopLaunchBrain.h:1191`–`:1206`, with training before mission reconciliation at `:1066`–`:1069` and bank charging at `:305`–`:309`.

The brain infers completion/payment from current bank balance minus the balance at acceptance. That balance also pays training in `7bd915b6`.

**Failing case:** a bot has exhausted its cash; between acceptance and reconciliation it spends 2,000 bank credits training and earns a 1,000 mission reward. The mission leaves the datapad correctly, but the brain sees -1,000, logs `mission_gone`, and never increments `missionsDone`. A smaller withdrawal understates payment even when the event is called complete. The actual server payment is unaffected; the overnight economy/completion report is wrong.

**Suggested fix:** record mission completion and reward transaction by mission ID. As a narrower interim correction, reconcile net balance with separately tracked bank training spending and label it an estimate; total training spending alone does not distinguish cash from bank. Validate a reward that coincides with a bank-funded training step.

### F7 — P2: census and position export read mutable peer state without synchronization

**Location:** `B/BotPopLaunchBrain.h:1099`–`:1108` and `:1387`–`:1415`; related peer observations are enumerated below.

`safeCopyTo` holds references and safely copies the close-object collection. It does not lock the returned objects. Generated `@read` accessors also do not acquire an object lock: `src/autogen/server/zone/objects/scene/SceneObject.cpp:1753` delegates directly, and Engine3 `utils/engine3/MMOEngine/src/engine/core/ManagedObject.cpp:426` simply returns `_impl`. Coordinates are ordinary mutable vectors (`utils/engine3/MMOEngine/src/engine/util/u3d/Coordinate.h:82`, `:117`).

**Failing case:** a position export starts while an outstanding worker switches a bot from planet A to B. It reads A's zone and B's coordinates, or coordinates from different steps. `writePositions` is invoked even on a skipped pass (`BotPopManager.h:939`). A census can likewise read a moving AI at mixed coordinates and insert a permanent wrong-square deduplication key. These are unsynchronized reads, not merely a guarantee of a whole snapshot one step old. The references prevent an immediate dangling-pointer diagnosis; no new assertion or crash is established by this finding.

**Suggested fix:** have the worker publish an immutable per-bot telemetry snapshot while the bot is locked; export that snapshot under its own brief synchronization. For census/peer selection take a cross-lock against the bot, revalidate zone/parent/liveness, and copy the required values before releasing it. Do not hold `launchShared` while acquiring creature locks. Collection locks alone are insufficient. A future TSan build or focused concurrent snapshot test can verify the fix.

### F8 — P3: launch-history sets never expire/reset during the manager's lifetime

**Location:** `B/BotPopLaunch.h:143`; `B/BotPopLaunchBrain.h:437`, `:904`, `:1407`; `B/BotPopManager.h:145`–`:148`.

Each bot's `skip` gains target IDs until travel or destruction, with no size/age cap; death and successful training do not clear it. The singleton's `censusSeen` persists even after every bot is despawned; nothing clears the three shared launch maps. `censusSeen` stores planet/name/square strings, not object references.

**Failing case:** a hunter stays on one planet while repeatedly abandoning newly spawned target IDs, or successive explorer runs encounter new name/square pairs. Despawning all explorers does not release their census history, and a later census silently omits previously recorded observations. With fixed names and map bounds the census has a finite world-dependent ceiling, but it has no explicit run or memory bound. `skip` can grow with newly allocated target IDs indefinitely on one planet.

**Suggested fix:** TTL/size-bound the per-bot skip set and reset it when the bot's capabilities change; scope census deduplication to a run (or explicitly persist it outside the server). Clear/reset shared run state only after steps are drained. Keep small terminal/visit caches if desired. Measure node counts and allocated string bytes before attributing gigabytes to them: at 30 give-ups per hunter/hour, roughly 40–64 bytes per set node, even 1,500 hunters add only about 2–3 MB/hour. That illustrative rate is not a measured rate and cannot explain 0.9–1.6 GB/hour by itself.

## Mission limit, client, and terminal compatibility

`handleMissionAccept` counts every mission object in the datapad, allows the sixth at count five, and rejects the seventh. The bounty restriction remains independent of the count: a second bounty is rejected even when other slots are free; one bounty plus five non-bounties is allowed. The setting applies globally, including live, as requested. Invalid zero/negative values disable all accepts; validate/log a positive setting rather than silently accepting an operator mistake. No configuration override of this key was found in the reviewed tracked configuration/source search; private configuration was not read.

| Area | What was checked | Result / remaining gate |
|---|---|---|
| Datapad and mission bag | Locally loaded shared client templates, `SceneObjectImplementation.cpp:189`, container transfer implementation | Both client template volume limits are 100, not 2. Six missions fit a sufficiently empty datapad. Pets, vehicles and other contents still share its capacity. |
| Full datapad | `MissionManagerImplementation.cpp:294` and `scene/components/ContainerComponent.cpp:304` | Existing code ignores a failed transfer and continues creating objectives. This predates these commits, but must be included in the live acceptance check. Check capacity and transfer success before activating an objective. |
| Offer lists | `MissionManagerImplementation.cpp:207`, `:619`, `:648`, `:677`, `:706`, `:735`, `:760` | Twelve offers initially, six per usual mission category; faction options enlarge the bag. These are offer counts, not active limits. Accepting removes that offer from the bag; refreshing replenishes it. No hard two-slot offer-array assumption found. |
| Terminal service rules | `:170`, `:185`, `:194`, `:593`, `:614` | Six-mission change leaves range/city-ban checks, request cooldown, terminal cross-lock, and one-refresh slicing bonus unchanged. More simultaneously active missions can still change payout/spawn load. Crafting has F1. |
| Mission waypoints | `MissionObjectImplementation.cpp:210`, mission message/delta classes, `PlayerObjectImplementation.cpp:828` | Each mission owns a waypoint; no two-entry server array found in these paths. Group nearest-mission scan processes every datapad entry. Its `numberOfMissionsForMember >= 2` at `group/tasks/UpdateNearestMissionForGroupTask.cpp:94` is **after** the complete inner scan and merely continues the outer loop: it does not truncate at two. |
| Client UI data | Loaded `ui/ui_mission.inc`, available PDA permission/waypoint monitor layouts | No active-two limit found in the layouts inspected. The text “2 two” at mission UI line 291 is sample datasource content alongside 1 and 3, not a limit. Waypoint monitor height/line constraints concern display, not mission ownership. `ui/ui_inventory.inc` is absent from the loaded index; the executable's datapad mediator was not audited. |
| Client strings | 273 loaded English STF files whose paths contain mission/datapad/waypoint | No two-active-mission requirement found in that scoped scan. `mission/mission_generic:too_many_missions` says “You cannot accept any more missions.” No wording patch needed for this rejection. |

Client checks used the existing read-only `tools/owner_content/swg_client_data.py` reader and the current client load order, entirely in memory. No client files were changed or imported. Winning files: mission layout and generic strings from `patch_12_00.tre`; waypoint monitor from `mtg_patch_017.tre`; datapad from `patch_01.tre`; mission bag from `data_other_00.tre`. SHA-256 of the loaded bytes:

| File | SHA-256 |
|---|---|
| `ui/ui_mission.inc` | `ef52b4242287a590f823066225a007a1f52f368ac635833b5c22fcaf50a20012` |
| `ui/ui_pda_waypointmon.inc` | `e099266f47beb0fc88e2cf7f930e3fd5149f12050a7d88c5cca7e02bdc80f4f4` |
| `object/tangible/datapad/shared_character_datapad.iff` | `f2c7526a0ff27a26950545d44550f26df75046de550612dcf6c7700b060f7434` |
| `object/tangible/mission_bag/shared_mission_bag.iff` | `244b5de2d601ebf3950f0d27588522744737e94ebeb6f4d340d5d3fe2e6886de` |
| `string/en/mission/mission_generic.stf` | `5dfe1eed6c96f8531e37c2ccb332edce39c9abbdf76d0c34f431c2b280dccad8` |

**Required future real-client check:** accept six mixed missions, reject a seventh, retain all six through refresh/relog, abort/complete each, toggle all waypoints, and check group nearest-mission behavior. Separately test one bounty plus five others, reject a second bounty, and exercise artisan/crafting, entertainer, scout and faction terminals. Include a full datapad and recipe collisions. No client source from excluded repositories was accessed; readable UI data cannot prove absence of a compiled client limit.

## Lock and lifetime audit

The normal object-controller dispatcher locks the player (`packets/object/ObjectControllerMessageCallback.cpp:67`). Bots have the equivalent outer creature lock in `B/BotPopManager.h:674`. The following covers the direct manager/object calls and queued gameplay operations in the four requested headers; it is not a whole-server lock proof.

| Bot call sites | Player path / actual synchronization | Assessment |
|---|---|---|
| Mission list, Brain `:1307` | `MissionListRequestCallback.h:64`; `populateMissionList:593` cross-locks terminal/player; each generated mission is locked at `:626` and equivalent loops | Same player lock and callee terminal/mission locks. No additional missing terminal lock established. Lifecycle gap F4 still applies. |
| Mission accept, `:1348` | `MissionAcceptCallback.h:74` cross-locks mission/player | **17cacd70 fixes the reported missing mission lock in source.** Objective creation explicitly locks the new objective. No runtime regression run by this reviewer. |
| Mission abort, `:1226` | `MissionAbortCallback.h:70`–`:73` locks player then mission/player | Same locking now; denial handling F5 remains. |
| `awardSkill`, `:142`, `:302`; learning/level/snapshot calculations | `SkillManager.cpp:333` locks the creature itself; bot already held. Skill metadata is shared immutable data for this workload | No missing manager/ghost lock established for these five starting professions. Group/Jedi side branches were inspected but are outside this workload. Training charge and award occur under the bot lock. |
| New gear/weapon transfers, `:153`, `:240`, `:245`; Manager `:379` | Item cross-locks plus bot; `ContainerComponent.cpp:265` takes the container lock | Existing/new items are locked for mutation; container transfer has its own list lock. Recheck transfer success where relevant; no missing inventory-object lock diagnosed merely from not locking the whole inventory. |
| Junk sale, `:508`–`:529` | Retains each item, then cross-locks it against bot before destruction. Normal Lua dealer also re-resolves inventory items and destroys them through its event path (`screenplays/junk_dealer/junk_dealer.lua:114`, `:134`) | Mutation lock present. Selection/value/ownership is read before cross-lock; revalidate item ownership/value after acquiring it if concurrent transfers become possible. This is a synthetic sale, bypassing dealer type/range/availability; it does not verify that a real dealer works. |
| Attack/harvest/loot, `:468`, `:487`, `:493`, `:1287` | Commands are queued through the normal dispatcher; `LootCommand.h:50` locks corpse/player; `HarvestCorpseCommand.h:48` locks creature/player; combat uses its normal target locking | No direct bypass of manager loot/harvest locks. Counts are attempted commands, not confirmed receipt/success. Retained local corpse reference protects lifetime; long-lived state stores IDs only. |
| Heal/watch/dance/flourish, `:589`, `:611`, `:786`, `:831`, `:839`, `:851` | Normal queued commands; `HealDamageCommand.h:400` cross-locks patient/player; `PlayerManagerImplementation.cpp:3458`, `:3488`, `:3549`, `:3576` handle watcher/entertainer locking | No additional missing mutation lock established. Selection reads before those commands can be stale; normal commands revalidate. |
| Target selection/fighting, `:363`–`:384`, `:401`–`:408`, `:434`, `:628`; corpse movement `:475`–`:482`; rest/medic selections `:579`–`:588`, `:759`–`:784`; attacker snapshot `:1056`–`:1060` | Lifetime held by managed references or copied close-object entries; peer position/posture/HAM/zone are read without peer object lock | Same unsynchronized peer-observation class as F7. Actual combat/heal/loot subsequently locks its target, which limits the mutation risk; selection is not a coherent state snapshot. |
| Census `:1385`; positions `:1099`; Manager player/activity selection `:859`–`:914` | Safe collection copy or state references, but no peer-state snapshot lock | F7. Preserve lifetime and synchronize values separately; avoid tick-wide multi-creature locking. |
| Movement/floor, Brain `:15`, `:22`; Manager `:478`–`:492`; terminal search Brain `:1142` | Bot held; floor query uses strong in-range entries and requests a zone read lock (`CollisionManager.cpp:499`–`:503`); terminal search passes readLockZone=true. Zone update owns its tree/container synchronization | No extra external manager lock identified. Ordinary collision peer reads remain a broader engine concern; do not add a coarse zone lock around movement without auditing object/zone order. |
| Travel, Brain `:922` | Bot held, standard `switchZone`; `scene/components/GroundZoneComponent.cpp:292`, `:302`, `:325` removes and inserts under its zone locks | No bot-specific missing destination lock found; active-mission bookkeeping is F5. This is teleport travel, not a shuttle/ticket test. |
| Revive/incap recovery, `:932`, `:1041` | Direct posture/HAM mutations concern the already locked bot. Does not call player cloner/cell operations | No unlocked cloner access: cloner is bypassed. Pools/posture reset is not verification of wounds, insurance, clone menus, or clone travel. |
| Shared state and console | `launchShared` protects terminal cache, visit vectors and census set; each bot's LaunchState is worker-owned; stats are atomic or tick-owned; console uses manager queue locks and `_test`/BotPop gates | No shared-map lock inversion found. SimLog mutex is separate and holds no creature/manager lock itself. Console gates remain present; launch-list race is F4, not console input parsing. |
| Logout/destruction | `ClientlessLogin` called with bot locked; recursive deletion locks child objects | Locks are present but lifecycle sequencing/semantic cleanup is incomplete: F2/F4. |

This audit found no second confirmed missing `@preLocked` mutation of the kind that crashed `setMissionObjective`. It does not certify race freedom or convert caught C++ exceptions into protection from `fatal`/assert aborts.

## Memory: evidence and discriminating measurements

Read [FINDINGS.md](../../Bot-reports/launch-sim/FINDINGS.md) and saved `host-*.jsonl` locally. The monitors continue across restarts: do **not** fit one slope from the first to last row of a whole file, or count overlapping monitors as independent runs. Restrict to stable-online windows and split process/restart boundaries.

| Saved sample window, local time | Online bots | RSS endpoints, recorded MB | Endpoint slope |
|---|---|---|---|
| `host-20261015-1734.jsonl`, 17:38–20:18 (160.5 min) | 1,500 | 5,185 → 7,533 | 878 MB/h |
| Same file, 20:27–21:44 (75.7 min) | 1,500 | 4,909 → 6,926 | 1,598 MB/h |

Other overlapping monitors give approximately the same windowed slopes. These agree with the findings document's approximate 0.9–1.6 GB/h. They prove increasing resident memory, **not** leaked live allocations. They also precede `41764180`, so missions/census cannot explain those old runs. New mission-list initialization is a separate large one-time allocation wave: each hunter can acquire roughly twelve persistent offers plus their waypoints (`MissionManagerImplementation.cpp:222`, `MissionObjectImplementation.cpp:210`) before considering objectives. Do not label that initial wave a steady leak.

All measurements below are **proposals for the lock holder after the overnight run**, not operations performed by this review. First collect a low-frequency counter line; use an offline heap profile in a later controlled run only if the counters do not explain growth.

| Candidate | Source/lifetime conclusion | How to measure it and distinguish a leak |
|---|---|---|
| SimLog | `BotPopLaunch.h:94`: serializes one temporary JSON row and writes directly to an ofstream; flushes every 200 rows or stats. No in-memory event history/queue found. Singleton allocation is once. Disk log is unbounded, RAM event history is not. | Log bytes written and row rate alongside live heap/RSS. Measure allocation backtraces for JSON/string/stream buffers; compare live bytes versus allocator retained/free arena bytes. Correlation with disk file size alone is not evidence of a RAM leak. |
| Shared maps/census | Terminal cache bounded by known launch cities (32); visits are 1,024 ints per encountered planet; census stores unique name/square strings for singleton lifetime, F8. | Under `launchShared`, report sizes, total key string capacities, visit vector capacities and set-node estimate. Record increments per minute and before/after a run reset. No world objects are held by these keys. |
| Positions | `Brain:1095` creates a local string and rewrites a temp file every 10 seconds; local buffer dies on return. No growing position-history container. F7 affects correctness. | Record output bytes/snapshot, serialization duration and heap live/retained bytes at fixed bot count. An increasing file size should track online count, not elapsed time. Check downstream map processes separately from core3 RSS. |
| BotState/LaunchState/paths | `BotPopManager.h:85` holds one strong creature ref per state; workers copy references for one pass. Paths clear/reuse capacity; launch hunter/explorer destinations have one point. `skip` is F8. Leaving refs normally expire after 15 seconds. | Count live states vs bots+leaving+in-flight retired states; path size/capacity, sum/max skip size, leaving age and outstanding chunks. After drain/despawn, all state/creature counts should return to baseline except intended caches. Bound/purge navmesh route capacity if measured high. |
| Mission/waypoint/objective/area/observer objects | Long-lived brain fields are IDs, not ManagedReferences. Server creates persistent offers/objectives/waypoints even for transient bots; ordinary abort/completion destroys them. F2/F5 can bypass that cleanup. Objective/observer back-links to mission/objective are weak, not proof of a strong cycle. | Count created/destroyed/live by class and parent/owner, with pending database deletion and dirty-object queue counts. Split mission-bag initialization from steady replacement. At fixed hunters, bag offers+active missions should plateau; capture orphan IDs after teardown. |
| Mission lairs/defenders | F2 permanent-owner cleanup; F3 can leave the correct lair unworked. Mission lairs disable no-player despawn. | Count objective-owned lairs, owner existence/online state, spawned defenders, ages and no-player-despawn flag. Join to mission/owner IDs. These are world counts; track zero-zone retained objects separately. |
| Wild spawns, terrain coverage | In all mode bots are ordinary player observers (`BotPopRegistry.h:18`). Spawn areas have population/per-type limits (`region/SpawnAreaImplementation.cpp:203`, `:242`). Moving 1,500 bots progressively opens more ground and can increase legitimate world population. Limits are per area/type, not an overall constant number of objects. | Per zone/area: live lairs, alive mobiles, dead mobiles, creation/despawn rates, spawn-count totals, occupied bot squares and AI observer counts. Compare fixed-location versus roaming cohorts and matched all/throttled runs with the same bots/seed as closely as possible. A plateau with stable explored coverage supports load growth; monotonic zero-zone retained objects suggests cleanup. |
| Corpses/loot/inventory | Creature deaths schedule 10 s or 300 s despawn (`CreatureManagerImplementation.cpp:722`); harvest can shorten it. `AiAgentImplementation.cpp:2202` cancels tasks and clears loot/threat/weapons. Scouts retain harvested resources; other loot remains in bounded inventories until sold/deleted. Command-attempt counters do not prove a corpse was emptied. | Histogram corpse ages and pending despawn deadlines; count corpses older than 5–10 min, nonempty loot containers, total loot items and bot inventory occupancy. At steady kill rate, ordinary corpses should approach kills/sec × lifetime. Count failed loot/full inventory separately. Verify expired/dequeued tasks actually execute. |
| Observers/herds/threat/close-object lists | Existing cleanup code must be measured: `AiAgentImplementation.cpp:2293` destroys weapons; `:2351` unhooks herds on final despawn; `SpawnObserverImplementation.cpp:54` covers lair teardown. Intact lairs intentionally retain their bounded spawnedCreatures list. Close-object vectors hold strong references (`CloseObjectsVector.h:22`); movement/recovery/removal normally prune them (`GroundZoneComponent.cpp:419`, `PlayerObjectImplementation.cpp:2379`). | Count observer registrations by event, herd membership, threat entries and close-object entries (sum/max) alongside world and zero-zone instance counts. Sample zero-zone objects retained past despawn and inspect actual reference paths; check COV entries for old-zone/far-away IDs after travel and for stale owners after despawn. Do not blame a strong cycle solely from two fields without checking weak annotations and cleanup branches. |
| Player menus/performance/recovery | Manual revive skips client menu interaction, but `sendActivateCloneRequest:1609` removes the old CLONE_REQUEST box before adding another: not an unlimited clone-menu-per-death leak. Watch/heal/performance use normal sessions. | Per bot: SUI box counts by type, patron memberships, pending recovery/treatment/command tasks and age. Counts should be bounded by bots/sessions, not cumulative deaths/heals. Check stop-watch and entertainer unload cleanup when a rest is interrupted. |
| Engine caches/allocator | Floor/path/appearance/terrain access can warm caches; repeated temporary JSON/path allocations can leave RSS high after free. No heap profile or cache-size census was available. | Pair `/proc/<pid>/smaps_rollup` anonymous/PSS/RSS with allocation/live-object counters, cache bytes and allocator stats from an approved diagnostic build. Record object-map size (`ObjectManager.cpp:1016`) but do not confuse it with complete reachable heap size. After quiescence/GC, distinguish falling live bytes with retained RSS from rising live counts. Do not attach a profiler or force allocator trimming to tonight's run. |

For a useful later comparison, capture baseline, post-spawn, post-first-terminal refresh, steady hourly samples, post-drain/despawn, and post-cleanup. Hold bot count, roles, mode, starting world and movement coverage comparable; use fresh process identity in every host sample. The existing resumed-world policy is valid, but its surviving populations must be counted instead of assuming a fresh baseline.

## What could not be checked

- No source fix, compilation, assertion reproduction, thread sanitizer, heap profile, database inspection, bot action, or in-game validation. Ranked findings need Claude's review and authorized runtime regressions.
- No access to legitimate compiled-client mission/datapad mediator implementation; no client run to prove six-slot display, acceptance, relog or waypoint behavior. Only locally owned client data was read. No excluded or leaked source was used.
- No measured byte attribution for the 0.9–1.6 GB/h growth, allocator-versus-live-heap separation, or post-despawn object census. No claim that a particular container caused the historical growth. F2 concerns later mission runs, not runs 2/3.
- No exhaustive audit of every mission type, every script-provided quest, engine-wide lock order, or every possible peer mutation. Bounty eligibility/payment internals were checked only as needed to preserve the one-bounty gate; bot launch hunters do not exercise bounty missions.
- No server `config-local.lua` or credentials were read. No live deployment/restart/merge approval is granted. The running overnight simulation was left untouched.

Next: Claude reviews F1–F8, fixes the live mission-limit dependency separately from bot behavior, and schedules the focused tests/counters after the current simulation ends and the owner's restart restriction permits it.
