# C4d — re-reviewed by ChatGPT

13 October 2026. **Changes requested before promotion.** Reviewed commit `5aadc8b995bb94cc72d0733c5a735eea0f981bb5` and all eight exported files. Five original findings are resolved by source review, two are partly resolved; a new cancellation race was identified. Remaining findings: **two P1, one P2**. This is not deployment approval.

## Findings that still need changes

### C4d-F1 — P1: a nonempty path is not proof of a traversable route

**Original C4b/C4c finding 3: partly resolved.** [LeashCommand.h:160](files/LeashCommand.h:160), rejection at 162, target selection at 167, teleport at 218. Current [PathFinderManager.cpp:459](context/PathFinderManager.cpp:459) explicitly converts a failed outdoor route into `[start, destination]`. The overload used by the leash dispatches to that outdoor method and allows partial routes. Thus `size() >= 2` is insufficient evidence of a navmesh route.

Concrete failure: follower at `(0,0)`, leader at `(100,0)` on the same planet/in the same group, across terrain where no route can be evaluated. PathFinderManager supplies its two-point fallback. The leash treats it as reaching the leader, interpolates to `(97,0)` and teleports. The progress checks pass. It can still cross disconnected terrain, precisely the original finding's concern. This does not depend on the now-removed explicit `target = goal` branch.

**Verification:** compiled the exported `unstick`/`warn` methods verbatim with minimal engine stubs and the actual pathfinder fallback block. Output: one move to `(97,0)` for a failed-route fallback; no move for null route; one move to a supplied reachable prefix `(20,0)`; no move for a no-progress route. See [reproduction script](reproduce_route_fallback.py), generated [C++](route_fallback_repro.cpp) and [results](route_fallback_results.txt). This is a deterministic algorithm counterexample, **not** an actual map/navmesh or in-game test.

**Required change:** consume an explicitly successful, validated path result that distinguishes a traversable route from fallback/unverified segments. Fail closed when that proof is absent. Do not merely reject all two-point paths: genuine clear routes can have two points. Preserve valid reachable-prefix behavior only when the prefix itself is validated. Test no-route terrain and mesh-boundary/partial-route cases on the disposable galaxy.

### C4d-F2 — P1: a cancelled leash tick can still move the follower after cross-lock acquisition

**New finding in the locking fix.** [LeashCommand.h:67](files/LeashCommand.h:67) checks pending-task identity and lines 70–74 check follower online status **before** [line 87](files/LeashCommand.h:87) cross-locks the leader. Engine [Locker.h:137](context/Locker.h:137) delegates to cross-locking; [ReadWriteLock.cpp:255](context/ReadWriteLock.cpp:255) and [line 290](context/ReadWriteLock.cpp:290) show that a contended acquisition releases and reacquires the previously held follower lock.

Concrete interleaving: task A passes its identity/online checks and is ready for an unstick; another thread holds its leader lock. During the cross-lock's temporary follower unlock, `/leash off` removes A, or a new leash B replaces it. A reacquires both locks, validates the old leader's group/planet and proceeds to `unstick` without checking whether A is still current. A can teleport toward the old leader after a successful stop/switch and then reschedule itself. The next tick's identity guard is too late to prevent this move. Follower logout can similarly invalidate the earlier online check.

**Required change:** after acquiring both locks, recheck pending-task identity and follower online state before any action; exit stale tasks without removing/replacing the new task or rescheduling. Keep the leader/follower cross-lock for consistent pair validation. Verify a deterministic contended leader lock with stop, replacement and logout while waiting. Source-supported race; **not reproduced on the running server**.

### C4d-F3 — P2: request IDs do not invalidate a plan when its scene changes

**Original finding 4: partly resolved.** [AgentControl.cpp:973](files/AgentControl.cpp:973) generates a new ID per invocation, [line 991](files/AgentControl.cpp:991) matches it, and [AgentPathCommand.h:69](files/AgentPathCommand.h:69)/92 parse and echo it. This correctly fixes late replies to earlier requests with identical destinations.

However, [onStartScene at line 126](files/AgentControl.cpp:126) resets world/position but does not invalidate the outstanding request or active movement. If a scene changes while the current helper request is waiting, a reply bearing that request's **correct** ID is still accepted even if computed in the prior scene. [walkPath at line 1036](files/AgentControl.cpp:1036) accepts its first point as authoritative, overwrites the new scene's position/cell and sends a transform. A scene change during an already-running path is likewise not a cancellation condition. This is the scene-invalidation part of the original requested fix, not a failure of the new unique IDs.

**Required change:** bind requests and walking to a scene generation, abort on generation change, and check generation atomically with applying a point/sending its corresponding movement. A late old-scene answer must not change new-scene coordinates. Replay a current-ID old-scene reply after zoning and interrupt an active path with a scene change. Source review only; no packet replay or in-game validation performed.

## Disposition of all seven original findings

Line numbers refer to the exported `files/` snapshot, matching the reviewed commit; context lines refer to saved supporting sources.

| Original finding | Disposition | Evidence |
|---|---|---|
| 1 — grant helpers lack independent test-instance boundary | **Resolved in source for the stated live/test database identities** | `AgentGearCommand.h:51`, `AgentSkillCommand.h:48` require both default-off flag and `SandboxTestGalaxy.h:16` database suffix check before grants. `ConfigManager.h:365–366` defaults DBName to `swgemu`; `tools/test_galaxy.py:28,103` uses `swgemu_test`. Allowlist remains checked first. A copied AgentGear flag alone no longer enables grants against `swgemu`. No live config/secrets inspected or grant invoked. This is a trusted-config identity guard, not a claim that an administrator cannot reconfigure it. |
| 2 — leader checks/coordinates lack consistent snapshot | **Resolved in source; new lifetime race above** | `LeashCommand.h:87` holds both creature locks across pair/range checks, coordinates, path query and teleport. Deadlock-safe cross-lock implementation verified locally. Its release/reacquire behavior creates C4d-F2 because task identity/online checks precede acquisition. |
| 3 — failed/short path falls back to unrestricted leader teleport | **Partly resolved, remains P1** | Explicit goal fallback removed; null/<2 points rejected at 162, reachable endpoint/progress checks at 167,200. Pathfinder's own synthetic fallback remains accepted: C4d-F1. |
| 4 — destination echo cannot distinguish retries | **Partly resolved** | Unique IDs correctly address same-destination retries (`AgentControl.cpp:973,991`; `AgentPathCommand.h:69,92`). Required scene invalidation still absent: C4d-F3. |
| 5 — Stop leash on another member switches leader | **Resolved in source** | `PlayerObjectMenuComponent.cpp:31–35` compares clicked object's ID with current leader and labels a different member as a switch. Dispatch at 78–79 and command branches `LeashCommand.h:267–275,290–291` agree. A later state change between opening/selecting a menu is a separate UI timing concern, not the original systematic mislabel. |
| 6 — mission cache survives scene reset / late destroy | **Resolved in source** | `AgentControl.cpp:135` clears missions alongside world; `onDestroy:182–183` erases radial/mission entries before missing-world early return. Fresh state rebuilt from baselines. Populated terminal zoning remains untested in game. |
| 7 — cleared waypoint keeps old destination | **Resolved in source for the server's packet format** | `AgentControl.cpp:231` replaces baseline record; 316 reads waypoint ID and 319–322 updates/erases field. Server `MissionObjectMessage3.h` emits a null waypoint with zero ID/coordinates; `WaypointObjectImplementation.cpp:31–43` writes non-null waypoint ID in exactly the parsed position. Real `(0,0)` waypoint with nonzero object ID is retained. Full terminal refresh/end-to-end acceptance untested. |

## Evidence, scope and limits

- Read packet patch, complete eight source files, prior seven findings, test-galaxy wrapper and existing Dorn/Esk reports. Verified **all eight exported files match commit `5aadc8b9`**, ignoring line endings. [Snapshot comparison](snapshot-verification.json).
- Dev HEAD was `5aadc8b9` during inspection. Concurrent uncommitted additions appeared in `AgentControl.cpp` and `AgentPathCommand.h` (`find` and `tell` support); **those additions are outside this C4d review and are not approved**. Leash source matched the reviewed commit. No source modified under `/opt/swg`.
- Saved five read-only engine/packet context files and [their source paths and SHA-256 hashes](context/sources.json). ConfigManager DB default inspected read-only, no private configuration/accounts/database read. Engine context establishes fallback and cross-lock behavior rather than relying on comments in the patch.
- Offline C++ reproduction compiled with `g++ -std=c++17 -O0` and exited 0. Assertions establish the reported counterexample and control cases; they do not pass the safety requirement for the failed-route case.
- Existing `Bot-reports/Dorn/20261013-201421-dorn-social.json` records 9/9 (4.9 m leader distance, zero repeated hops in its ten-second sample, correct three-member menu labels). Existing `Esk/20261013-201710-esk-routes.json` records 5/5. These are pre-existing test records, **not new runs by this review**; they do not exercise the three remaining failure cases. The patch's distinct 2.1 m result was not independently recreated here.
- No galaxy restart/build/deploy, game/bot login, outbound message, paid operation, asset download or import. Initial sandboxed WSL read failed with access denied; approved read-only calls succeeded. No automatic approval rejection occurred.

## Next verification before promotion

Claude should fix C4d-F1/F2/F3 in dev and export a new pinned diff. Disposable-galaxy checks: disconnected terrain and partial routes; contended stop/switch/logout; planet/door transitions and reciprocal leashes; delayed same-destination replies plus old-scene replies; populated mission cache followed by zoning/late destroy, fresh baseline, empty waypoint and origin waypoint. Also verify helper denial against live-equivalent `DBName=swgemu` with flag true **without granting on live**. Owner's real-client C6 remains pending after reviewed promotion and explicit deployment authorization.

Reviewed by ChatGPT. No server commit created. C4d review complete; deployment remains on hold for fixes, cross-review and owner approval.
