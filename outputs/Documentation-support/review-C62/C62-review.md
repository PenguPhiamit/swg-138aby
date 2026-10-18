# C62: release-track cross-review

Reviewed by ChatGPT, 18 October 2026. **Changes requested for an unrestricted dev release.** The 47-commit batch contains useful live fixes, but five commits need follow-up fixes before their affected features are released. Hoth is still NO-GO; Ossus and Nal Hutta should remain closed for the first release. BotPop, the agent client and test provisioning stay off on live.

Scope: **`a8ece12b6705158b1ec9706ba61077a4249be226..aa52cc647a2129096011eb122fe98c7794db4c2b`**, exactly **47 commits**, in chronological order below. Verdicts consider each diff and the final state at `aa52cc64`; a later correction can clear an earlier placement defect only when released together. All source paths in this report are relative to `Core3-dev/MMOCoreORB/`.

This is a source/offline review, not gameplay acceptance or permission to deploy. Reads and Git ran as `swgemu` inside WSL using script files. Dev remained at the pinned tip with a clean tracked status. No files under `/opt/swg` were changed; no builds, galaxy commands, attachments, bot commands, downloads, installations, merges or deployments occurred. Claude retains the server lock. No additional agents were used. The owner's instruction to leave both galaxies alone takes precedence over historical runtime descriptions on the board.

## Ranked findings

All seven findings are **P2**, ordered by player impact and release relevance. No new P0/P1 was established. F4 and F6 identify incomplete repairs of existing behavior; they are explicitly not claimed as newly introduced regressions. F7 affects test evidence only while BotPop remains disabled on live.

### F1 — Heat and electricity attacks heal two new Hoth bosses

**Commit:** `ac578315`. **Location:** `bin/scripts/mobile/hoth/hoth_fill_creatures.lua:83-90`, especially the resistance arrays at 85 and 89. **Needs a fix before Hoth opens.**

Rimefang has heat/electricity values **220**, and Old Echo **230**. Core3's values above 100 encode special protection: `CreatureTemplate.h:143-147,164-168,481-500` subtracts **100 once**, giving actual resistances **120% and 130%**. Ordinary values such as 150 correctly mean 50% special protection; the problem is the new values above 200. `AiAgentImplementation.cpp:4825-4879` does not cap a fresh NPC's result. `CombatManager.cpp:2459-2472` multiplies damage by `1 - resistance/100`, and `CreatureObjectImplementation.cpp:1194-1204` subtracts that signed damage from HAM.

**Failing case:** shoot a fresh Rimefang with a heat or electricity weapon. For a hit worth 1,000 after armor piercing, the armor calculation produces **-200 damage**; Old Echo produces **-300**. Subtracting that increases the targeted HAM pool. A group using those damage types can undo other members' damage instead of killing the boss. The checker loads the actual creature definitions and confirms these data/arithmetic results; the C++ call chain was inspected, not executed in-game.

**Required:** choose valid intended resistance percentages and encode them correctly; defensively prevent negative damage from over-range NPC resistance if that is taken as a separate engine fix. Check kinetic, energy, heat and electricity against both bosses in-game. Do not reduce every value above 100: that would break valid special-protection encoding.

### F2 — Completing the memorial road can permanently hide the ghostfire lead

**Commit:** `5191f9b0`, interacting with `742ace54`. **Location:** `bin/scripts/screenplays/sandbox/ossus_people.lua:549-573`; `bin/scripts/mobile/conversations/sandbox/ossus_people_conv.lua:79-95`. **Needs a fix before Ossus opens.**

The new `ghostfire_lead` option exists only on the archivist's `greet` screen. Walking the road makes the initial screen `road_reward`; collecting its payment stores `roadPaid=1`. All later conversations start at `greet_done`, a terminal screen with no options. Yet the ghostfire quest requires that road badge as well as the lead.

**Failing case:** a player walks the three memorial sites, receives badge 140, then collects the archivist's 500 credits before asking about Jedi light. Subsequent conversations offer no ghostfire lead. The spirit keeps directing that player to the archivist; normal play cannot repair the missing quest state. This also affects characters who completed the road before O10 was installed. The actual Lua handlers and conversation screens reproduce this offline.

**Required:** make the lead reachable from the completed-road state, including existing `roadPaid=1` characters. Check lead-before-road, road-before-lead, paid-before-update and relog cases.

### F3 — Pet kills do not advance the new Hoth or Kessoth kill jobs

**Commits:** `ac578315`, `ce3975db`. **Location:** `bin/scripts/screenplays/sandbox/hoth_world.lua:274-299`; `bin/scripts/screenplays/sandbox/hutta_life.lua:340-361`.

Both `creditKill` functions immediately return unless `pAttacker` is a player creature. `OBJECTDESTRUCTION` supplies the actual attacker: `AiAgentImplementation.cpp:4031-4047` forwards it through `CreatureObjectImplementation.cpp:4036-4050` to `TangibleObjectImplementation.cpp:1062-1063`. The separate highest-damage/XP handling in CreatureManager does not replace that argument with a pet's owner.

**Failing case:** a Creature Handler accepts Tavi's Rimefang job and their pet lands the killing blow. The boss dies and its respawn is scheduled, but the owner remains on step 1 and cannot collect the reward. The same occurs when a pet finishes Skarrel, Vekk Tano or Kreeg. Even nearby grouped players receive nothing because the function returns before considering the group. Offline calls to the actual handlers confirm that a pet attacker is ignored while a player attacker advances the job.

**Required:** resolve eligible owned combat pets to their player owner before applying the group/range rules, or use the established credited-player kill mechanism. Check solo pet, grouped pet and direct-player kills, plus a non-owned NPC kill that must not grant arbitrary credit.

### F4 — Group pay still pays a member on another planet at the old endpoint

**Commit:** `cbd85fdf`. **Location:** `src/server/zone/objects/mission/MissionObjectiveImplementation.cpp:277-288`. **Incomplete repair; the bad endpoint branch predates this commit.**

The new `nearOwner` branch correctly includes a same-zone check and fixes exclusion of nearby participants. The preceding endpoint branch remains ORed into it without a zone check. Thus this is a proximity expansion, not a replacement with the actual fight location. The commit also intentionally retains the old endpoint eligibility for someone left there.

**Failing case:** a destroy mission's old endpoint is E=(0,0,0), its lair and owner are at (250,0,0) on Tatooine, and a grouped member is at (0,0,0) on Naboo. `nearOwner` is false, but endpoint distance is zero, so that remote member is included in `players` and receives a share. A member left at E on Tatooine is also still paid, including the dead member from the original reported failure; no alive/participation check was added. The coordinate example is a source arithmetic counterexample, not a claim about a particular stock terrain site or a new runtime reproduction.

**Required:** apply zone eligibility to the entire expression. For destroy/hunting missions use the actual completed encounter position, rather than continuing to admit recipients solely near the stale listing/first waypoint; preserve suitable completion anchors for delivery and other mission types. Decide the dead-member policy explicitly. Check two nearby fighters, a distant same-zone member, a member on another planet at matching coordinates, and the exact split. The existing divisor remains based on the full group; this finding does not claim new credit duplication.

### F5 — The new jobs erase each other's navigation markers

**Commits:** `ac578315`, `ce3975db`. **Location:** `bin/scripts/screenplays/sandbox/hoth_world.lua:242-269,313-317`; `bin/scripts/screenplays/sandbox/hutta_life.lua:308-324,383-386`.

The handlers remove **every** waypoint of the shared `WAYPOINTQUESTTASK` type before adding one, and remove the same shared type on completion. The engine really removes all matches (`PlayerObjectImplementation.cpp:910-917`). Each Hoth job has independent progress and can be active alongside the others; none of its active-state conversations restores its lost marker. The Kessoth job uses the same global slot, including across planets and stock quest-task content.

**Failing case:** accept Hask's Echo Base job, then Tavi's Rimefang job. Both remain active, but the Echo Base marker disappears. Finish the word-of-mouth Pryce job while Rimefang remains active and its reward removes Rimefang's marker too. A Kessoth step can similarly remove a previously active quest-task marker. The actual Hoth acceptance/set-waypoint functions reproduce the first loss offline; completion's removal follows the same engine API.

**Required:** track and remove each job's own waypoint, or use distinct types/keys supported by the engine; offer a retrack action for existing progress. Check simultaneous jobs, a stock quest-task marker, travel, reward and relog without deleting another job's navigation.

### F6 — An already-open bank window bypasses the new alive/conscious requirement

**Commit:** `aa52cc64`. **Location:** `src/server/zone/objects/tangible/components/BankTerminalMenuComponent.cpp:70-84`; unchanged `src/server/zone/objects/player/sui/callbacks/BankTerminalSuiCallback.h:20-50`. **Incomplete repair of an existing submission path.**

The new checks correctly protect radial IDs 20 and 68-73: Deposit/Withdraw, Deposit all, Withdraw all, Join, Quit and Safety Deposit. `isInRange` also checks the zone (`SceneObjectImplementation.cpp:1422-1435`), so a cross-planet radial bypass was ruled out. However, the money-transfer callback checks range and balances but never checks death/incapacitation. `SuiManager.cpp:43-96` dispatches it under the player lock without a global alive check.

**Failing case:** open Deposit/Withdraw while alive within 8 m, become incapacitated while remaining there, then submit that existing window. The radial handler is not called again; the callback can still call `transferCredits`. The new radial checks do not enforce the stated requirement at the transaction. This is source-established and requires a game check; it is not a claim that the new 8 m check fails.

**Required:** repeat the state check when submitting the transfer. Retain the existing callback range check so walking away after opening stays rejected. Exercise both changes of state, both all-money radials, and inside/outside 8 m.

### F7 — BotPop's close-target fallback still walks through an impassable barrier

**Commit:** `98a74806`, with related travel fallbacks in `d4b9d9a1`. **Location:** `src/server/zone/managers/botpop/BotPopLaunchBrain.h:534-539,37-57`; `BotPopTravel.h:1056-1069`. **Test-galaxy only.**

`ROUTE_NONE` and `ROUTE_SHORT` are deliberately overridden when the target is within `stopAt + 15 m`: the bot takes a straight positional step. `stepToward` checks height but does not check the segment for wall collision. Travel has a similar final-20-metre straight finish. A disconnected platform and an actual wall are not distinguished.

**Failing case:** a terminal is 10 m away across a solid wall, stop distance 3 m, and Detour returns no route or a partial route ending on this side. Since 10 <= 18, the close-target branch moves directly toward it through the obstruction. This is a concrete source-path counterexample; no particular wall was exercised tonight.

**Required on test:** validate the final segment or restrict the exception to a proven traversable connection. Until then, a successful BotPop approach is not proof that a real client can reach a terminal, boss or cave. Keep this code disabled on live regardless of whether that test fix is taken.

## Verdict for every commit

**Fit for a live release** means fit in the inspected source, with dependencies and the release gates below. It does not mean tested in-game. For closed planets it permits dormant inclusion, not opening the planet or shipping an unmatched client archive. **Needs a fix** refers to an open finding above. **Test-galaxy only** code may remain compiled where its guard is proved inert on live; it is not a feature to enable there. Totals: **21 fit, 5 need a fix, 21 test-galaxy only**.

| # | Commit | Change and review result | Verdict |
|---|---|---|---|
| 1 | `c5d713b8` | Helper locks player → cross-locked droid → device; removes C55's retained-device/player cycle. Spawn gate now applies only below level 10, preserving solo-master krayt eligibility. Normal helper and novice/master runtime checks remain. | **Fit for a live release** |
| 2 | `724809fa` | Initial navmesh routing and per-pass budget; reviewed with its later routing replacements. | **Test-galaxy only** |
| 3 | `5bf55669` | Takes the highest floor within a bounded step; terrain/raised-floor client comparison still needed. | **Test-galaxy only** |
| 4 | `de9a825c` | Deterministic lanes and terminal spacing, within the existing BotPop driver. | **Test-galaxy only** |
| 5 | `b6059d7a` | Nal Hutta planet/weather/city declarations. Dormant while `hutta` is disabled; matching terrain, snapshot and travel data required to open. | **Fit for a live release** |
| 6 | `e7512cb8` | Samples long routes for intervening meshes, capped crossings and shared route budget; not a collision-complete route proof. | **Test-galaxy only** |
| 7 | `665bea04` | Once-per-minute lair diagnostics; no ordinary player-path change. | **Test-galaxy only** |
| 8 | `8edfd13f` | Per-thread Detour queries, area read locks and stop/partial semantics replace the earlier broad straight fallback. Later F7 still limits its guarantee. | **Test-galaxy only** |
| 9 | `fe399424` | Species starting skills/certifications granted during simulated-character setup. | **Test-galaxy only** |
| 10 | `d8e12a01` | C56 checks capacity before claiming a bounty, checks containment result before objectives, restores the list and rolls back the claim on failure. Full-datapad/relog gate remains unrun. | **Fit for a live release** |
| 11 | `98a74806` | Close-target bypass makes terminals reachable but reintroduces unvalidated wall crossings (F7). Needs test-side follow-up. | **Test-galaxy only** |
| 12 | `86cc85a1` | Ticket/collector/shuttle state machine and fare top-ups. Calls stock commands, but bot walking/recovery still differs from a real client. | **Test-galaxy only** |
| 13 | `d4b9d9a1` | Travel hubs, onward destinations, stall recovery and building path graph; final straight finishes share F7's evidence limitation. | **Test-galaxy only** |
| 14 | `ad7b5a9d` | O7 ruins/POI exclusion circles. Data-only and zone-scoped; use matching O7 client placements. | **Fit for a live release** |
| 15 | `742ace54` | Ossus people, three starter jobs, road badge and rare Jedi schedule. Use final O10/O11 corrections together; no standalone approval of the original bad Jedi placement. Badge 140 needs client data. | **Fit for a live release** |
| 16 | `69f5c879` | Regular-lair template maximum supplements the row gate, still inside the below-10 exemption. Unknown templates return 0; it does not suppress static spawns or attack-triggered bosses. | **Fit for a live release** |
| 17 | `8ec46ddf` | Threat-map defense and keeping queued lair attacks; 4 m melee approach. | **Test-galaxy only** |
| 18 | `fa5cab1d` | Starport exits and disconnected-mesh hops. Controlled bot exceptions, not client navigation acceptance. | **Test-galaxy only** |
| 19 | `07d9f61e` | Bot mission selection defaults to level + 2; does not change player mission generation. | **Test-galaxy only** |
| 20 | `fc3bb3e2` | Agent crafting packet support and `/agentgear resources`; resource grants remain behind account allowlist, flag and disposable-galaxy guard. | **Test-galaxy only** |
| 21 | `b034d15f` | Adds movement-bounce/speed diagnostics without relaxing validation. Logs are unconditional; assess volume in the rehearsal and keep diagnostics local. | **Fit for a live release** |
| 22 | `7c2f2605` | Agent stands before walking, tracks movement speed and replans after corrections. Does not alter real-client movement validation. | **Test-galaxy only** |
| 23 | `3b7620fd` | Nal Hutta home, vendors, destroy/delivery support and fauna; guards startup on zone enablement. Vendor checks money/space before giving an item and charges only after success. Needs client/quest/travel acceptance before opening. | **Fit for a live release** |
| 24 | `7be8837a` | Hoth den, ice rancor body, mission points/terminals, recruiter move and quartermaster badge/loot. Matching client cave/terrain/palette/badge data and existing Hoth gate remain required. `ac578315` supersedes rancor respawn/drop defaults. | **Fit for a live release** |
| 25 | `fd13513d` | O8 habitats, places, road patrol and One Sith dungeon. Include O11 floor corrections and O11c leash; no clearance of the original misplaced dungeon points alone. | **Fit for a live release** |
| 26 | `ce3975db` | Nal Hutta life, Kessoth quest, density and resource eligibility. F3 pet credit and F5 waypoint ownership remain. Zone closure can keep it dormant. | **Needs a fix** |
| 27 | `44c2933a` | Owned-pet teach-all radial and invalid-pet bypass require god mode at dispatch/call. Ordinary players retain validation. Staff behavior, not a blanket player bypass. | **Fit for a live release** |
| 28 | `393c5c25` | SuiListBox supplies the other-button boolean expected by PetFixSuiCallback; level repair no longer rejects >75. Normal CH control/vicious limits remain, so a repaired high-level pet need not be callable by an ordinary CH. | **Fit for a live release** |
| 29 | `91cf87ed` | Recalls an owned stale zoned vehicle through store before calling it; retains dead/combat/indoor, ownership, Hutt and delayed-call checks. Check reconnect/restart and relog persistence in-game. | **Fit for a live release** |
| 30 | `e5d13dfc` | Eight Vong armor templates, outfit and one zone-gated display warrior; requires the matching custom client artwork. This is appearance content, not a completed Vong combat encounter. | **Fit for a live release** |
| 31 | `ac578315` | Hoth fill, Echo Base interior and three jobs. F1 signed damage, F3 pet credit and F5 marker loss block opening this content. | **Needs a fix** |
| 32 | `5191f9b0` | Ghostfire sites/quest and fixed color 32 exception. Color handling preserves the normal 0-11 cap otherwise, but F2 blocks existing/completed-road characters. | **Needs a fix** |
| 33 | `a6a515c8` | Bot groups use queued invite/join/leave/disband with shared plans; percentage defaults to 0. Does not authorize real-player or live bot population. | **Test-galaxy only** |
| 34 | `b39ff477` | Ignores shape-free SPRT appearances in the existing unsupported/no-shape switch; no collision mesh is discarded from a parsed solid appearance. | **Fit for a live release** |
| 35 | `3cf3d88f` | Corrects Ood Bnar's local position/height/heading to the sanctuary floor. Closes the earlier placement defect in source; client conversation/reachability still needed. | **Fit for a live release** |
| 36 | `4906d2eb` | Corrects 23 cave spawns to floor-mesh points. Must accompany O8 and the corrected client terrain; floor coordinates alone do not prove connected gameplay routes. | **Fit for a live release** |
| 37 | `a48e1d7d` | Bare guard body replaces the clothed commoner under the Vong outfit; same dormant Ossus/client-art gates as `e5d13dfc`. | **Fit for a live release** |
| 38 | `22722efe` | Removes 25 nonworking vehicle entries from the sandbox builder catalogue; does not migrate existing deeds or repair vehicles. | **Test-galaxy only** |
| 39 | `25344120` | Swaps three broken Hoth deed rewards for registered Rebel/Imperial BARC and Tantive IV deed paths at unchanged weights. Needs actual loot → redeem → call → ride → store/relog checks; does not certify all 18 vehicles. | **Fit for a live release** |
| 40 | `cbd85fdf` | Nearby-owner fallback repairs excluded participants, but retains the cross-zone/stale-endpoint payout in F4. | **Needs a fix** |
| 41 | `4b113bb7` | Clones the stock move tree with prefixed node IDs and 80 m CheckRetreat condition. Applies to all O8 fighters using the helper, including camps; stock/global AI remains unchanged. Test cave pursuit/return. | **Fit for a live release** |
| 42 | `bcc9c90c` | Agent system-message parsing retains folders in STF names; corrects receipt evidence, not server behavior. | **Test-galaxy only** |
| 43 | `2ad8bcf9` | Agent skips CREO1 base-HAM/skill deltas without losing subsequent credit fields. Packet bounds/fallback retained. | **Test-galaxy only** |
| 44 | `a5430bc1` | Agent records building yaw and resolves cell-local position for find/height defaults and status world coordinates. No real-client or server position-rule change. | **Test-galaxy only** |
| 45 | `1be13676` | Agent sends/observes stock mission-abort packets. A request receipt is not proof the mission was aborted. | **Test-galaxy only** |
| 46 | `4bae9ab1` | Full delivery pickup keeps INITSTATUS/NPCs and reports inv_full; crafting preflights all draft slots before granting parts; conversation checks status. Late non-capacity crafting transfer failures still take the old abort path. Full/retry/complete acceptance remains. | **Fit for a live release** |
| 47 | `aa52cc64` | New radial checks cover all bank IDs and both state/range; pending window submission still has F6. | **Needs a fix** |

## What release 1 should now contain

The [release plan](../live-release-1.md) contains two historical routes: the small C55 cut and the later provisional friends launch. The owner's latest launch direction there is friends with thin planets restricted, with the planet list explicitly provisional. Its “Where live is” count and some staged/not-installed descriptions predate this range; they should not be treated as today's measured state. C62 does not silently choose to open a planet or lift the mission hold.

**Recommend a reviewed release candidate with stock worlds first and the new planets closed until their gates pass.** Prefer a deliberate release branch containing the reviewed player fixes; do not promote `aa52cc64` wholesale. This is a release recommendation only; no branch was created tonight. Integration against the actual live base needs its own build/diff check rather than blindly cherry-picking commits with missing dependencies.

The first candidate should contain:

- The previously reviewed name filter, per-type XP support with unchanged configured rates, and the **isolated** CitiesAllowed guard. Keep the already reviewed stock-world leash/pet-follow/vehicle/ticket fixes where their existing acceptance gates are met.
- The common helper lock-order repair from `c5d713b8`. C55 F1 is resolved in source; a normal unregistered new character must exercise it, since BotPop still bypasses helpers.
- The novice-only gate from `c5d713b8` plus `69f5c879` and the reviewed novice spawn-data fixes, **only after** novice, solo-master and group visits demonstrate the intended populations. Default boundaries are `<10`, base 10 and creature margin 7, cached until restart. Otherwise keep `LevelGateBase=0` for this release; do not reintroduce the C55 global gate.
- Mission containment/pickup hardening from `d8e12a01` and `4bae9ab1`, with the reviewed shared-recipe/one-item fixes if mission work is admitted to the release. Keep **`Core3.MissionManager.MaxActiveMissions = 2`** until the owner lifts the hold and its full acceptance set is passed. New source fixes do not clear that hold or C56's unrun full-datapad gate. Group-pay `cbd85fdf` needs F4 corrected and an exact-share run first.
- Vehicle stale-call recovery `91cf87ed`, pet repair UI `393c5c25`, and, if retained as the owner's staff feature, the god-mode-only changes `44c2933a`. Check ordinary-player paths with god mode off. Removing the repair ceiling does not implement expanded ordinary CH control limits.
- The bank radial restriction **together with F6's callback-state fix**, followed by transaction tests; do not advertise the current commit as complete alive-state enforcement.
- SPRT noise handling `b39ff477`. Movement diagnostics `b034d15f` are a reasonable support inclusion; assess log volume in rehearsal, and do not represent logging as a rubber-band fix.

For the friends package, distribute the matching reviewed C57 client patch for whatever is actually enabled. New planet/template code may remain dormant only after an exact-config rehearsal proves it loads quietly; closing a zone is not proof that global template includes can load without its archive. Keep privacy/credits/asset provenance with the package. No new rights clearance or client archive audit is supplied by this server-source review.

| Launch area | Recommendation after C62 | What must change before opening |
|---|---|---|
| Ten stock ground planets and existing stock instances | First release candidate, subject to regression/rehearsal | Complete the selected player-fix gates and retained older release gates. |
| Hoth | **Hold closed for now**, despite the plan's provisional “open” row | Fix F1/F3/F5; pass the existing [Hoth release gate](../hoth-release-gate.md), including actual access to Echo Base rooms, quest completion, resources and rewards. Carry the final rancor settings, working deed substitutions and matching cave/terrain/palette/badge data together. Keep it as the next optional opening, not discarded content. |
| Ossus | **Closed** | Owner's restriction remains. Fix F2, then test the full road/ghostfire chain, O7/O11 floors and cave connections, O11c pursuit, fauna and travel with the matching archive. The Vong pair is a display look, not encounter acceptance. |
| Nal Hutta | **Closed pending acceptance**, reassess rather than calling it empty | PL-04/06 now add substantial content, so the old “one city/no creatures” reason is obsolete. Fix F3/F5; test vendors and Hutt pricing, Kessoth end-to-end, resource surveying, swamp sites and return travel before asking to open it. |
| Space | Retain the plan's unresolved owner/acceptance decision | This review supplies no JTL sign-off. |

**Whole-dev blocker inherited from C55:** `64156084` installs T1/T2 and **224 scripted test creatures** in five stock cities without a disposable-galaxy guard. None of these 47 commits removes or guards that change; unchanged city files preserve the prior finding. `BotPop=false`, closed Hoth/Ossus/Hutta, and the absence of a custom archive do **not** hide those stock-city spawns. Split the city guard from that experiment or exclude/guard the experimental spawns before any whole-dev release candidate. Merely fixing C55's helper and krayt gate does not clear whole-dev promotion.

**Live test-code boundary:** BotPop console/command admission remains behind `isDisposableTestGalaxy()` plus its flag (`managers/botpop/BotPopConsole.h:19`, `BotPopCommand.h:36`). `/agentgear` also checks the account allowlist, `Core3.AgentGear` and disposable galaxy before its new resource kit (`commands/AgentGearCommand.h:495-518`). AgentControl/ZonePacketHandler changes belong to the separate client. In the candidate use the non-`_test` live database identity, BotPop off, groups 0, and test helpers off; do not install or run agent bodies on live as a result of C62. These observations are a source-boundary check, not a live-config inspection.

## Verification and required acceptance

Reproducible checker: [check_c62.py](check_c62.py); complete hashes, syntax results and offline counterexamples: [checks.json](checks.json).

```sh
wsl -d Debian -u swgemu -- nice -n 10 python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/review-C62/check_c62.py
```

- **118/118 changed Lua file-at-commit syntax checks passed**, plus **81/81 changed surviving Lua files at the final tip**: 199 checks total. Syntax does not validate engine bindings, assets, terrain, snapshot IDs or runtime registration.
- Loaded the actual pinned Lua definitions/handlers with substitute engine objects: confirmed F2, both F3 handlers and F5; loaded the actual Hoth creature arrays for F1's signed-damage arithmetic. These are offline counterexamples, not a simulated successful galaxy run. The checker also records F4's coordinate counterexample.
- Traced helper locking, spawn eligibility, mission containment/rollback, delivery/crafting retry, pet repair button dispatch, vehicle call/store, bank radial/SUI dispatch, damage/resistance decoding, quest state and test-code admission. Rejected a bank cross-zone hypothesis because the real range helper checks zones; valid special-protection values above 100 were not misreported as over-range damage resistance.
- `git diff --check` on the source range reports trailing whitespace in the new Vong template license comments; it does not pass. This is recorded as formatting only, not a release correctness finding.
- No C++ compilation, IDL generation, live config/database read, restore rehearsal, relog/persistence test, real-client art/collision check or gameplay run was performed by ChatGPT. Earlier owner/Claude observations in the board and [functional test plan](../functional-test-plan.md) are prior evidence only. That plan still records the full-datapad and exact group-pay gates open; the final two server fixes also need the build/retry acceptance described in their own notes.

Before deployment, Claude should fix the selected findings, produce the exact candidate diff, and run the non-`_test` restored-live dress rehearsal with the selected zone/archive config and two-mission cap. Check a real existing character and an unregistered new character, ordinary pet/vehicle behavior, full datapad, full-inventory pickup/retry and exact group receipts. Re-review the fixes, then follow the plan's backup/rollback and **owner's explicit live-deploy OK** gates. Nothing in this review authorizes a restart, merge or live promotion.
