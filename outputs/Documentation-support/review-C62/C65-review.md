# C65: C62 fixes and H1 building range

Reviewed by ChatGPT, 18 October 2026. **Changes requested: F4 still needs an encounter anchor. F5's marker ownership is repaired, but its recovery is incomplete. H1 works for freshly spawned buildings; old saved radius fields bypass its calculation.** No new P0/P1 established.

Pinned revisions: C62 repair **`35e7dbe64c235befc3f1da3fd3aa0d0301c36a08`**, whose sole parent is `aa52cc647a2129096011eb122fe98c7794db4c2b`; H1 **`0262d8deb36c9ced07b9a226e0aa8614335ad3ee`**, immediately after `a27adc4d6a5d71ccd9a6afc24bdb3c1dd0c1b7dc`. This reviews those commits, not subsequent ghostfire/harvester/movement changes. Source paths below are relative to `Core3-dev/MMOCoreORB/`.

Source/offline evidence only. Git and server-source searches ran as WSL Debian `swgemu` through script files. No builds, C++ compilation, galaxy/bot commands, database reads, merges, deployments, downloads or writes under `/opt/swg`. Claude's concurrent working-tree edits were left alone. Gameplay, real relog and performance remain **untested by this review**; the owner's existing H1 screenshots/probe are separate evidence on the board.

## Verdicts on the six findings

| Finding | Original failing case | Completeness and regression verdict |
|---|---|---|
| F1: attacks heal Hoth bosses | **Fixed.** Rimefang/Old Echo no longer decode above 100% resistance. | Complete for the nine affected creatures and this NPC armor path. The wider data correction and defensive cap are sound; deliberate ordinary-wampa balance change detailed below. |
| F2: paid road hides ghostfire lead | **Fixed.** Both completed-road screens now offer the lead. | Lead-before-road, road-before-lead, paid-before-update and reconstructed persisted-state relog pass. No duplicate road payment/lead markers found. Real database relog untested. |
| F3: pet finishes yield no job credit | **Fixed.** Owned pets resolve to their player owner in both helpers. | Both Hoth kill jobs and both Kessoth kill steps covered: solo/grouped pets, direct solo/grouped players, unowned NPCs and invalid owners. Real pet finishing blows untested. No blocking regression found; solo/group range policy differs. |
| F4: other planet/stale endpoint gets paid | **Original cases fixed; repair incomplete.** | Zone guard covers both branches; stale destroy/hunting endpoint is excluded. Owner-relative eligibility loses an actual fighter when the owner retreats (**N1, P2**). Dead/alive inclusion is explicit policy, not an accidental bypass. |
| F5: jobs erase each other's markers | **Fixed for new/retracked markers.** | Simultaneous jobs, stock quest-task marker, travel, reward and reconstructed relog pass. Type 0 plus stored IDs is valid. Old markers intentionally linger; report-back retracking misses three cases (**N3, P3**). |
| F6: already-open bank transfer bypass | **Fixed in source.** | Submitted window rechecks both dead and incapacitated states before range/payment. Same-zone inclusive 8 m range and all-money radial guards retained. No demonstrated alternative normal-player callback bypass. |

### F1: all equivalent data and the cap

`CombatManager.cpp:2368-2407` selects all nine NPC damage-type resistances and caps only the upper bound at 100 before returning. `getArmorReduction:2464-2479` uses that result for the AI branch, including pets and the force-attack damage-type selection. The existing negative/vulnerability sentinel is preserved; valid special protection values such as 150 still decode to 50, rather than being mistaken for 150% and flattened. Player armor and vehicle reduction paths are unchanged. Search of literal mobile `resists={...}` arrays at the parent finds nine over-200 arrays; the repair leaves **zero** such arrays across that source tree. This is a literal-data scan, not a proof about future dynamically computed values; the engine cap covers those on this damage path.

| Creature(s) | Old encoded heat/electricity | New encoded | Actual resistance | Damage from 1,000 after piercing |
|---|---:|---:|---:|---:|
| Ordinary `hoth_wampa` | 200 | 180 | 80% | 200 |
| `hoth_elder_wampa` | 210 | 185 | 85% | 150 |
| Rimefang; matriarch, Snowblind, broodmother, Icemaw, patriarch, Frostfang | 220 | 190 | 90% | 100 |
| Old Echo | 230 | 195 | 95% | 50 |

The six older named cave bosses and elder had the same defect; correcting them is justified. Lowering the ordinary wampa from full heat/electricity immunity to 80% is an intentional balance adjustment, beyond eliminating negative damage. It establishes the stated resistance ordering, not a proof of overall encounter difficulty (HAM, attacks, armor tier and other resistances also matter). It does not alter kinetic/energy or the other entries. Kinetic/energy/heat/electricity arithmetic on all 18 loaded Hoth templates stays nonnegative. No replacement immunity or signed-damage regression found. The cap turns a future erroneous 120% into immunity rather than healing; it does not make bad data balanced.

### F2: every requested order/state

`mobile/conversations/sandbox/ossus_people_conv.lua:91-100` makes `road_reward` and `greet_done` nonterminal and adds `ghostfire_lead`; `greet` retains it. The selector/handler at `screenplays/sandbox/ossus_people.lua:549-573` still use persistent screenplay keys.

- **Lead before road:** choosing it from `greet` stores `ghostfire=lead`; later road completion/payment preserves it. Repeating the option does not add another set of lead markers.
- **Road before lead:** completed `roadStep=3`, unpaid, enters `road_reward`; its existing entry handler pays once and the new option remains reachable.
- **Paid before update:** seeded old `roadPaid=1`, complete road, empty ghostfire enters `greet_done`, now offers the lead without any migration or second payment.
- **Relog:** rebuilding the player wrapper from saved screenplay fields/waypoints preserves access and prevents extra payment/markers. This exercises the actual Lua selector and handlers; it does not exercise the database or conversation packets.

No remaining equivalent completed-road screen without the lead, new progression reset or credit duplication found.

### F3: actual API, targets and eligibility

Both repaired helpers use real registered bindings: `SceneObject:isAiAgent`, `AiAgent:isPet`, `CreatureObject:getOwner`. The last returns a creature pointer or nil, not an object ID. An AI needs pet status as well as a linked owner; nil/non-player owners are rejected by the subsequent player check. Merely linking an ordinary NPC to a player does not grant credit.

`hoth_world.lua:295-327` serves Rimefang (`onJobTargetKilled:190-205`) and Skarrel (`poi/hoth_echo_base.lua:121-128`). `hutta_life.lua:348-376` serves Vekk and Kreeg through `notifyNamedKilled:250-268`, steps 1 and 3. No pre-helper player-only gate remains on those four targets. Ossus's hunt records its quest owner separately; the world-boss observer uses damage dealers, so neither has this exact final-attacker filter.

The extended actual-Lua matrix checks each of those four job/step paths with solo owned pet, direct player, grouped pet and grouped direct player. Grouped cases include a member at exactly 128 m (allowed by `isInRange`), one at 129 m, wrong zone with identical coordinates, wrong quest state, reversed owner/helper ordering, and an out-of-range owner with an eligible nearby helper. Only eligible states advance; repeated solo kills do not advance again. Non-pet NPCs, nil attacker, ownerless pets, NPC owners and linked non-pets grant nothing.

The group uses the owner's group, filters each member against the body and the real range helper's same-zone horizontal distance. The **solo** list still seeds the owner without that range filter, as it did for direct players before the patch. Thus a source-model solo pet owner at 129 m advances while that owner in a group does not. Real pet retention/fighting at that separation was not demonstrated; this is a policy/acceptance edge, not evidence of a new reachable exploit. Do not early-return on owner distance when fixing it: that would lose eligible nearby group members.

### F4: zone, type, death policy and exact split

`MissionObjectiveImplementation.cpp:285-296` now requires the same zone in both branches, and disables the endpoint branch only for `DESTROY`/`HUNTING`. All nine objective-factory mission types were considered; the three escort CRC names have no normal factory branch here.

| Mission type | Completion anchor retained/used after repair | Result |
|---|---|---|
| Destroy | Owner only; original end is not updated when the lair moves | Original false recipients removed, but actual fighter can be lost (N1). |
| Hunting | Owner only; listed end was the list-request location | Removes stale location. Kill observer requires owner near the target, but owner position still differs from final kill position; edge-of-range companions are not guaranteed encounter-relative eligibility. |
| Deliver / crafting | Delivery destination plus owner | Appropriate destination preserved; crafting derives from delivery. |
| Dancer / musician | Performance building plus owner | Preserves the performance completion anchor. |
| Recon | Listed recon target plus owner | Preserved. |
| Survey | Override returns owner position | Near-owner flat branch preserves eligibility. |
| Bounty | Override returns current target position, plus owner | Target anchor retained; existing bounty flattening unchanged. Both recipient branches now require owner's zone. |

Other-planet matching-coordinate cases are denied for all nine. Same-zone members stranded at the old destroy/hunting endpoint are denied unless also near the owner. A nearby dead or incapacitated group member remains eligible **by the explicit comment/policy**; this does not implement a damage-participation test. Player distance is strictly `<128`, horizontal near-owner, unlike the inclusive Lua/bank helper. The retained endpoint calculation for other types remains 3D except bounty.

The divisor is unchanged: max(saved mission divisor, current full **player** group count, 1), not eligible recipients. For a 1,000-credit two-player job both eligible get 500; with one excluded, the other still gets 500. For reward 1,001, saved divisor 2 and current count 3, each eligible player gets 333, even if only two are eligible. Excluded shares are not redistributed. Pets are diagnostics, not paid player shares. No new duplication identified.

### F5: ownership, migration and recovery

`HothFillJobs:setWaypoint:244-265` stores one `job.."Waypoint"` ID per job; Kessoth's `setWaypoint:310-333` stores `waypoint`. Both remove only that ID from the requesting player's waypoint list, create type **0**, and save the returned ID. `LuaPlayerObject::addWaypoint` really returns an ID and defaults persistence to 1; the player engine only replaces matching **nonzero** special types. Decimal integer screenplay storage is compatible with these APIs. Both completion paths clear their own tracked marker only.

The substitute engine was corrected to model nonzero special-type replacement. The extended run keeps Echo Base, Rimefang, Pryce, Kessoth and a stock `WAYPOINTQUESTTASK` marker concurrently; after reconstructed relog/travel and all rewards, only the stock marker remains. Hoth pays 15,500 combined and Kessoth 6,000 in the fixture. Actual item creation, inventory and persistence were not tested; loot functions are stubs.

**Legacy policy:** an old quest-task marker has no saved ownership ID, so retracking creates a new owned marker and leaves the old one. It can remain stale even after reward, until manually removed or replaced by stock quest-task content. This is visible clutter, not deletion of another quest. Accepting this policy is safer than guessing ownership and clearing the shared type; there is no automatic clean migration in the commit. Recovery works for Hoth kill step 1, Pryce step 2, and Kessoth steps 1-3, including repeated calls after reconstructed relog. It misses Hoth kill step 2 and Kessoth report step 4 (N3).

### F6: submitted window and other bank actions

The new guard at `BankTerminalSuiCallback.h:43-46` executes after box/argument/bank validation and before range at 48 and `transferCredits` at 57. A window opened alive then submitted dead or incapacitated is rejected with `@error_message:wrong_state`. Walking away after opening still fails range. Alive/conscious at 7.99 or exactly 8 m is allowed; 8.01 m or another zone is denied. `SceneObjectImplementation::isInRange:1422-1439` rejects other zones and clears both Z values before its inclusive squared-distance test.

The existing radial condition (`BankTerminalMenuComponent.cpp:70-83`) covers ID 20 and 68-73: transfer, deposit all, withdraw all, join, quit, safety deposit. State and range precede those actions. The normal transfer-box creator at 87-94 installs this callback. SUI dispatch retrieves the stored box/callback under the player lock; a client does not choose the unguarded legacy callback-null `SuiManager::handleBankTransfer` branch. No second ordinary transfer-box creator was found. Already-open safety-deposit item transfers are outside this money-window finding; this is not a claim that all container operations now use this guard.

## H1: which stock buildings, and the cost

**Verdict:** the fresh-object formula is consistent with the existing general `TreeEntry` rule and fixes the reported Echo Base send-distance cause in source. The lifecycle is incomplete for pre-fix saved buildings (N2). No demonstrated new stock collision/placement failure; wider visibility has real resource costs that were not benchmarked.

`BuildingObjectImplementation.cpp:76-99` takes the maximum horizontal corner radius of every available floor triangle AABB, including the exterior floor. The loop size and `getFloorMesh` index both use portal cell properties; null floor/tree checks are safe. Floors are in the building frame, and layout X/Z maps to world horizontal X/Y. The conservative AABB corner may not be an actual vertex; that overestimates reach rather than omitting a floor. Rotation preserves this radius. Shapes without supported floors do not gain reach from this calculation; exterior-only mesh extent is not measured.

The setter runs for reach **strictly greater than 96 m**. `getOutOfRangeDistance:2023-2035` uses 192 + radius above that threshold, retaining max(768, 192 + radius) if `COV_BUILDING_QUAD_RANGE` is enabled. Exactly 96 stays at 192; just over 96 jumps above 288. This matches the existing general threshold; it is not a smooth LOD change.

The installed client inventory has **223 stock and 69 MTG winning portal layouts**. Of the stock layouts, **55** have supported floors reaching past 96 m. Every layout, range and matched client building template is listed in [H1-stock-buildings.md](H1-stock-buildings.md); this is the exhaustive measured list, not just examples. It includes:

- Ordinary cave styles 1/2/3, flatland, ice, damprock and mirrored variants; both Tatooine cave styles; their named quest/dungeon template aliases.
- Mad Bio/droid bunker, allum mine, Imperial prison/detainment, crimelord retreat, Warren, abandoned bunker, small outposts 1/2 and research facility, with all aliases in the inventory.
- Jabba's and Theed palaces, Great Massassi/Woolamander/Blueleaf temples, dark Jedi enclave, Theed hangar, Lucky Despot, Nym's stronghold and Corvette dungeon.
- General/Corellian/Naboo/Tatooine starports, all four guild theatres, both newbie halls. No ordinary stock player-house layout crosses the measured threshold.

"Stock" identifies the winning archive supplying the POB; the client includes later-era aliases, so their presence does not mean the pre-CU server spawns them. The inventory maps templates, not live instances. Empty Falcon/star-destroyer test POBs have no floors. Three old `PRTO 0001` layouts are excluded because the pinned engine rejects that version too. The parser completed with zero unexplained errors and byte-identical parse/build roundtrips of examined POB/FLR inputs. No assets were extracted or imported. **Existing database instances are subject to N2; the list does not assert all 55 immediately get enlarged at restart.**

| Example | Reach m | Normal range before → after | Ideal circular area multiplier |
|---|---:|---:|---:|
| Echo Base | 769.85 | 192 → 961.85 | 25.1× |
| Stock newbie hall | 1,604.91 | 192 → 1,796.91 | 87.6× |
| Jabba's palace | 483.01 | 192 → 675.01 | 12.4× |
| Four starport layouts | 126.53 | 192 → 318.53 | 2.75× |
| Guild theatres | 100.09-100.75 | 192 → 292.09-292.75 | about 2.32× |

Those are geometric ratios at uniform density, **not measured CPU/bandwidth multipliers**. Per-object loading now visits its already-loaded floor boxes. The larger radius can keep an object at a higher quadtree node (`TreeEntryImplementation::isInArea:300-310`) and increase candidate checks. Ground range queries use `QuadTree::safeInRange`, whose final filter reads the candidate's range (`GroundZoneImplementation:199`, `QuadTree:476-500`). More players retain building/child close-object references, receive baselines and subsequent updates, and keep client objects loaded. `BuildingObject::notifyInsert:498-598` traverses loaded cells and sends their contents for static buildings, so this can cost more than sending an exterior shell. Broadphase bounds may also become more conservative when transient bounds initialize from radius. Physical floor/portal geometry and template no-build radii are not rewritten by this patch. No latency, packet-count, memory or renderer benchmark was run; such costs must not be reported as zero.

## Ranked new findings

### N1 — P2: finishing fighter loses destroy-mission pay when owner retreats

**Location:** `src/server/zone/objects/mission/MissionObjectiveImplementation.cpp:292-295`. **New regression from F4's endpoint removal; original false-recipient cases are fixed.**

**Concrete case:** same planet, flat terrain: listed end E=(0,0), actual spawned lair L=(20,0), helper at L, mission owner retreats to (300,0). A 20 m spawn offset is allowed (`DestroyMissionObjectiveImplementation:96-108`); only start/waypoint move (`163-175`). Helper destroys the lair. Its destruction observer calls completion without checking owner distance (`300-305`), and base `complete:73-84` queues reward with only a non-null owner requirement. This is a reachable source path, not an assertion that a runtime test occurred.

Before the repair, helper is 20 m from E and qualifies. After it, DESTROY disables `nearEnd`; helper is 280 m from owner and gets zero. Owner qualifies at their own position. With reward 1,000 and divisor 2, the result changes from 500/500 to owner 500/helper 0, plus `group_too_far`; the missing share is not redistributed. The owner is being used as the encounter, although they left it.

**Required:** capture the actual lair position **and zone** before cleanup and use that completion anchor. Hunting should likewise preserve its final-kill anchor. Keep the cross-zone guard and chosen dead/alive policy; do not re-enable stale listing coordinates. The desired-helper acceptance assertion fails in `C65-checks.json`.

### N2 — P2: H1's calculated radius is overwritten when an old building loads

**Location:** `src/server/zone/objects/building/BuildingObjectImplementation.cpp:76-99` (calculation only in template load); `src/server/zone/TreeEntry.idl:37` (persistent radius); `src/server/zone/managers/object/ObjectManager.cpp:756-770,801-813` (template creation followed by saved-field restoration). **Incomplete coverage of persisted objects, not a new regression for fresh Echo Base.**

**Concrete case:** a pre-fix saved Jabba palace instance has radius 0.5. Template initialization now computes 483.01, but `loadPersistentObject` then calls `deSerializeObject`, restoring saved `TreeEntry.radius=0.5`. `getOutOfRangeDistance` therefore returns 192 rather than 675.01. A player 300 m from its centre still does not receive it through this range change. The same order exists for static-database objects (`ObjectManager:473-485`). Building transient initialization (`BuildingObject:44-53`) and inherited database-load callbacks do not recalculate reach. The current generated reader additionally confirms that `TreeEntry.radius` is serialized and parsed as a float; the pinned IDL is the authoritative declaration.

The model deliberately seeds an old saved field; **no private world database was inspected**, so this does not count affected deployed instances. Fresh screenplay-spawned Echo Base has no old field to overwrite and is not disproved by this case. A newly created building saved with the correct radius can retain it on later loads; the gap is pre-fix/stale saves.

**Required:** factor reach calculation into a safe post-deserialization/transient initialization path, before spatial insertion, or migrate/derive a separate nonpersistent visibility radius. Verify fresh creation, old save load and next reload, with a >96 m stock template and Echo Base. Do not reset unrelated non-building radii. Desired persisted-range acceptance fails in the source-derived lifecycle model.

### N3 — P3: retracking skips the report-back stages

**Location:** `screenplays/sandbox/hoth_world.lua:269-277`; `screenplays/sandbox/hutta_life.lua:415-419`. **Incomplete F5 recovery, not continued marker cross-deletion.**

**Concrete cases:** complete the kill for Echo Base or Rimefang (step 2), remove its return-to-giver waypoint, reconstruct/relog, and invoke the giver's retrack path: no marker is recreated because `j.target ~= nil` excludes the step-2 branch. Kessoth after its last kill (step 4) has the same failure: the conversation only resets markers for steps 1-3. Legacy players whose return marker was erased before the repair have the same state. Pryce is covered because its job has no target.

Three actual-Lua extended assertions fail. The job can still be rewarded if the player finds the giver; indeed invoking this conversation already means reaching the giver. This is a navigation/recovery omission, not a new reward lock or reason to reject the type-0 ownership design.

**Required:** Hoth step 2 should restore the giver marker for both target jobs; Kessoth step 4 should call its already-supported `setWaypoint(...,4)`. Preserve ID-specific removal and avoid restoring after completion. Verify repeated retrack, stock-marker coexistence and persisted reload in those states.

## Checks and remaining acceptance

`check_c62_fixes.py` now pins source using `git show`, keeps Claude's original actual-Lua assertions, corrects the substitute engine's special-type replacement behavior, and loads [c65_cases.lua](c65_cases.lua). Original assertions pass. The extended run is **36/41 PASS, five expected acceptance failures**, exit **1**: N1 once, N2 once, N3's three stage cases. Full case details are in [C65-checks.json](C65-checks.json). The first development run also caught an overly specific checker variable name (`obj` versus real `object`); that checker error was corrected, not reported as a bank defect.

Actual Lua is executed with substitute objects. Reconstructed relog copies persistent fields; reward item creation is stubbed. C++ checks extract predicates or inspect source contracts, with distance/divisor/range lifecycle models; **no C++ engine function, SUI request, real bank transaction or world database load was executed**. H1 archive audit separately succeeds with zero parse errors and records source fingerprints in the inventory. All 12 changed Lua files pass `luac5.3 -p` on their pinned contents. No compile/build was necessary for this review.

Before feature acceptance: fix N1; finish or explicitly accept N2/N3 scope; have Claude run real pet/group completion, all quest chains and rewards, bank state changes with an existing window, real relog, old/new building reload and range traversal. Measure visibility/child fanout on busy stock sites before describing H1 as cost-free. Hoth C23/C24 gates and the original test-only F7 remain open. This review does not authorize a deployment or reopen a planet.
