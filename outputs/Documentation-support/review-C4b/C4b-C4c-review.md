# C4b + C4c — re-reviewed by ChatGPT

14 October 2026. **Review complete; changes requested before promotion.** The original C4 F1–F3 are addressed, but the findings below remain. This review is not deployment approval.

Reviewed the exported `01-cde59ec5.patch`, `02-3797430a.patch`, and `03-leash-helpers-missions-net.diff`, with the full files in `files/`. C4c is a review of the final net state through `2970b47e`, with attribution from the supplied commit messages; separate intermediate C4c patches are not present. All file:line references below use the full exported files in `files/`, not patch line numbers. Their server paths begin `MMOCoreORB/src/server/zone/objects/creature/commands/`; `AgentControl.cpp` is under `MMOCoreORB/src/client/agent/`, and `PlayerObjectMenuComponent.cpp` under `MMOCoreORB/src/server/zone/objects/player/components/`.

Only local files under `h/` were used. The earlier C4 packet supplied the existing point-cap harness and supplementary `WorldCoordinates.h`/`PathFinderManager.cpp` context; those older references are not asserted to be a fresh server snapshot. No WSL, game connection, server build, deployment, external research, or private account/config/database inspection was performed. No reviewed source was edited. Runtime behavior remains **untested by ChatGPT**; test-galaxy results in commit messages remain Claude's results.

## Findings

1. **P1 — No independent test-galaxy boundary for the grant helpers.** `AgentGearCommand.h:49`; `AgentSkillCommand.h:46` — `f25c90f9`.

   Both handlers correctly require the caller's actual account to be in `Core3.AgentAccounts` and require `Core3.AgentGear` to resolve true, defaulting false. Both checks precede item creation or skill awards. However, neither handler checks which galaxy/database it is modifying, and the commands are registered unconditionally in the exported command-manager diff. Thus the stronger requirement that these commands *can never act on live* is not established by this code.

   **Concrete failure scenario:** the live configuration acquires `Core3.AgentGear = true` during a test-config copy or mistaken enablement, while a live bot account is allowlisted for `/agentpath`. That account's `/agentgear boss` reaches persistent `createObject(..., 1)` at line 115; `/agentskill <valid box>` reaches `awardSkill` at line 63. The caller need not be staff, and neither handler rejects the live instance. This is a configuration-dependent exposure, not a demonstrated bypass with the flag false or the caller absent from the allowlist.

   **Change:** enforce an independently verified disposable-galaxy identity before registration and/or mutation, failing closed for the live instance even when the grant flag is true. Have Claude verify both commands on live-equivalent configuration without performing grants on live. Keep the present account and enablement checks as well.

2. **P1 — Leader validation and teleport coordinates are not one consistent snapshot.** `LeashCommand.h:62`, `LeashCommand.h:125`, `LeashCommand.h:139` — `09a56205`, retained in `220e0f39`.

   `run()` locks only the follower. It validates the leader's group/zone, separately reads distance and mount state, and later constructs `goal(leader)` and another world-position value. A managed reference protects the leader's lifetime, not consistency across those reads. There is no leader lock or final validation tying the goal to the validated zone and range.

   **Concrete failure scenario:** on a tick that will unstick the follower, `checkPair` sees both characters in zone A. The leader changes planet before `WorldCoordinates goal(leader)` is captured. Pathfinding still receives the follower's zone A with the leader's new coordinates/cell; the direct-goal fallback can then feed those coordinates to the follower's teleport in zone A. A doorway transition can similarly mix position frames between separate reads. The same race invalidates the claimed 512 m/group boundary if the leader moves or leaves the group after validation.

   **Change:** obtain a consistent leader/follower validation and coordinate snapshot using the engine's deadlock-safe cross-object locking pattern, retain referenced cells, and revalidate relevant state before teleporting after pathfinding. Do not introduce reciprocal-leash deadlocks by acquiring two arbitrary locks in opposite order. Exercise planet/door transitions and reciprocal leashes on the disposable galaxy.

3. **P1 — Failed or short paths authorize an unrestricted direct-goal teleport.** `LeashCommand.h:142`; `LeashCommand.h:173` — initial fallback in `09a56205`, additional fallback in `220e0f39`.

   `target` starts as the leader's position even when `findPath` returns null, empty, or one point. The follow-up fix also replaces a path-derived target with the leader's position whenever the target remains more than 10 m away. Neither case requires a usable route to the destination. The building-entry check is useful, but outdoor targets have no such check and building-wide permission does not establish that a route or scripted doorway is traversable.

   **Concrete failure scenario:** two grouped players are 100 m apart across an impassable outdoor wall/cliff, with the leader already on the far side. Pathfinding returns no route, or a partial route ending over 10 m short. After the stuck threshold, the follower is teleported directly to the leader anyway. The same-planet, group and 512 m tests all pass; no destination building exists to reject entry. This turns a walking assist into a way across disconnected terrain. This scenario follows the fallback branches; no specific map location was tested.

   **Change:** refuse an unstick when there is no validated traversable path/eligible destination. Retain a safe reachable prefix or report why it cannot proceed; do not treat a short path as permission to jump to its unreachable goal. Test disconnected terrain and gated interiors separately from the raised-ground regression.

4. **P2 — Argument echo cannot distinguish retries to the same destination.** `AgentControl.cpp:984` — `3797430a`, paired with the echo added in `cde59ec5`.

   Replies are matched only by destination argument text. That text is reused across replans/retries and does not identify the request or its start position. An older answer arriving during a new wait with identical arguments is accepted. `walkPath` subsequently overwrites the local position with the plan's first point at lines 1029–1036.

   **Concrete failure scenario:** a move toward an indoor target times out waiting for request A while the bot is still outdoors. The bot makes an outdoor straight-line move with `path:false`, then retries the original indoor destination as request B. A delayed A reply arrives during B's wait. Its echoed arguments match B, so a route beginning at the old position is accepted and the body emits that stale first-point transform. The server may correct it, but the client correlation guard has failed.

   **Change:** send a unique request ID for every helper invocation and echo/match that ID; also invalidate outstanding plans on a scene change. Test a delayed same-destination reply after movement, alongside the already-handled different-destination case.

5. **P2 — “Stop leash” can switch the follower to a different leader.** `PlayerObjectMenuComponent.cpp:30`; `PlayerObjectMenuComponent.cpp:73` — `09a56205`, retained after `220e0f39`.

   Every other group member is labelled “Stop leash” whenever any leash task exists. Selection always passes the clicked member as a new target with empty arguments. `LeashCommand.h:230` stops only when that target is absent or is the current leader; otherwise lines 248–249 replace the task.

   **Concrete failure scenario:** A is leashed to B, right-clicks group member C, and chooses the offered “Stop leash.” A is now leashed to C and can be teleported toward C after becoming stuck, despite having requested a stop.

   **Change:** make a displayed stop action explicitly execute `leash off`, or label the action according to whether the clicked member is the current leader and keep label/dispatch semantics consistent. Check a three-person group.

6. **P2 — Mission cache survives the scene reset that discards its ownership context.** `AgentControl.cpp:132`; `AgentControl.cpp:1196` — `f25c90f9` integration with the scene reset in `3797430a`.

   `onStartScene` clears `world` but not the newly introduced `missions` map. `missions` returns every cached entry, including IDs absent from `world`, assigning them container 0. Moreover, `onDestroy` returns early for IDs absent from `world` at lines 180–186, before erasing their mission cache entries.

   **Concrete failure scenario:** a terminal's mission objects are cached on planet A, then a scene change clears the world before individual destroy callbacks are processed (or without such callbacks). On planet B, `missions` still offers those stale entries as uncontained missions; a later destroy of an old ID does not clear them. Automation can choose an obsolete mission or report the wrong terminal inventory.

   **Change:** clear mission state with the scene reset and rebuild it from fresh baselines; erase mission/radial cache entries on destroy even when the world entry is already absent. Test a populated terminal list followed by a scene change and a late destroy.

7. **P2 — A cleared waypoint retains the previous mission's destination.** `AgentControl.cpp:317` — `f25c90f9`.

   Waypoint decoding only writes a value when x or y is nonzero. It never removes an existing `waypoint` when the incoming field is empty. Baselines also populate the existing JSON object rather than replacing it. This conflicts with the explicitly supported reuse of mission objects during terminal refreshes.

   **Concrete failure scenario:** mission object M first has a waypoint at (100, 200). A terminal refresh reuses M and sends an empty waypoint (0, 0). Titles/rewards update, but `missions` still reports (100, 200) as the new mission's waypoint, sending automation to the old destination. A legitimate origin waypoint is also silently omitted by this coordinate test.

   **Change:** replace or erase the waypoint on every waypoint-field update, using protocol validity/identity fields rather than nonzero coordinates to determine presence. Reset a mission record on a fresh full baseline. Replay populated-to-empty and origin-coordinate cases.

## Per-commit disposition

| Commit | Result |
|---|---|
| `cde59ec5` | **No findings in this commit's reviewed changes.** Original F3 closed: every point append is capped, truncation marks a continuous prefix partial, path results use `unique_ptr`, and inputs/cell zone are checked. Argument echo works for different requests; finding 4 concerns the client's insufficient matching key and requires a protocol follow-up. |
| `3797430a` | Original F1/F2 closed by source review: one total move budget capped at 95 s is passed through planning/replans/walking, and shared dead/incap checks cover straight and path movement, including frame transitions. **Finding 4** remains in request correlation. Mission-cache integration is finding 6, introduced later. Survey/indoor-look/scene changes were inspected; no additional finding beyond those listed. |
| `09a56205` | **Findings 2, 3 and 5** in the final net state. No approval to promote the leash. |
| `220e0f39` | **Finding 3** also applies to its new direct-goal fallback. Naming the current leader is correctly idempotent; the menu mismatch in finding 5 remains. Corrected error labels were inspected; no additional finding identified there. |
| `f25c90f9` | **Findings 1, 6 and 7.** Default-off + allowlist checks are correctly placed, but they provide conditional configuration protection, not unconditional test-instance isolation. Mission acceptance/decoding still needs a server-writer comparison and end-to-end test. |
| `2970b47e` | **No additional findings** in the supplied final net content. Packet describes LF normalization only; its isolated intermediate diff was not exported, so a separate byte-for-byte normalization audit was not possible. |

## Offline verification and remaining limits

The new loop was extracted verbatim from `files/AgentPathCommand.h:150` through line 180 into the earlier C4 reproduction's container/terrain stubs. Compiled locally with MSVC 19.44 in C++17 mode and executed successfully (exit 0). Reproduction source: `point_cap_repro.cpp`; runner: `run_point_cap_repro.cmd`. This is an algorithm reproduction, not a Core3 build or actual navmesh query.

| Synthetic route | Points | Partial | Last point |
|---|---:|---|---|
| (0,0) → (2048,0) | 256 | true | (2040,0) |
| (0,0) → (1600,0) → (1600,1000) | 256 | true | (1600,440) |
| (0,0) → (2032,0), below cap | 255 | false | (2032,0) |
| (0,0) → (2040,0), exactly at cap | 256 | false | (2040,0) |

Grant authorization was traced in both full handlers: non-player, missing player object, missing/non-allowlisted account, and false/missing flag all return before a grant. Only an allowlisted account with a true flag reaches the grant code; `target` cannot redirect grants to another character. No live configuration was inspected, so its actual flag value is **unverified**. No false-flag or non-allowlisted grant bypass was found. Finding 1 records the stronger live-isolation requirement explicitly requested for this review.

Leash lifetime: weak references avoid keeping disconnected players alive; a null follower exits, offline/missing pair removes the task, and the pending-task identity check rejects a stopped/replaced task on its next run. The follower lock serializes that check and teleport with properly locked command handling. No additional lifetime defect was established from this packet; task-manager internals and command execution locking were not exported. Rapid logout/relog, stop/replacement while a tick runs, and reciprocal leash behavior remain untested.

Teleport uses `target.getX(), target.getZ(), target.getY()` and the target cell ID, preserving the x/z/y API ordering and cell-local coordinate frame. Interpolation avoids blending different cells. The final target building is checked with `isAllowedEntry(follower)` before teleport. These are positive source checks, not proof of private-building denial, scripted door/cell eligibility, or behavior during concurrent building changes; those dependencies and runtime cases are not verified here.

No new external source, client asset, service, outbound message, credential, or excluded-source dependency was introduced by this review. Existing notices remain in the exported code. Claude should address the findings in dev and test them on the disposable galaxy; the owner must still explicitly authorize any live promotion.
