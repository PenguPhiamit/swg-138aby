# C4e — reviewed by ChatGPT

14 October 2026. **Changes requested before promotion: one P1 and one P2.** Reviewed exported dev commits `5b2a858f`, `421adb15`, `9ac7cdcd`, and the later Hoth creatures patch `c402e480`. No server edits, builds, restarts, merges or deployment approval.

## C4e-F1 — P1: two missing floor triangles are accepted as a proved indoor route

`files/LeashCommand.h:249–250` calls `getFloorPath` and accepts result `-1` as proof. However, `files/context/PathFinderManager.cpp:697–700` compares the two floor triangles for equality **before** checking either for null. Two failed triangle lookups compare equal and return `-1`.

Concrete counterexample: follower and leader retain the same cell ID, but both positions are outside that cell's floor triangles (for example an invalid/off-floor placement). `findPathWithinCell` at `PathFinderManager.cpp:1246` also interprets `-1` as a direct `[start,end]` path. The new leash proof accepts that segment as on-floor, and a sufficiently long segment can pass progress checks and teleport the follower into invalid floor space. This is the exact failed-lookup case the new proof must reject, not a request to reject valid two-point paths.

Fix: require non-null source and destination floor triangles before the equality shortcut, ideally in the shared helper so both planning and proof benefit. Add controls for two null triangles, one null triangle, one valid shared triangle, distinct connected triangles and disconnected floor components. Verify on a disposable test map before promotion. `offline_checks.py` asserts the exported branch ordering and demonstrates the null/null outcome in a small Python decision model. **No C++ executable, real map or in-game reproduction was run by this review.**

Disposition of C4d-F1: **partly resolved**. Outdoor synthetic fallback paths now require explicit recast evidence and a checked prefix; the indoor null/null loophole remains. Short same-building cross-cell steps are additionally trusted by proximity (12 m), not independently proved against portal connectivity. The normal planner does supply portal-graph nodes, so proximity alone is a hardening concern rather than a separately reproduced exploit here. Preserve that graph provenance if the helper is reused on arbitrary segments.

## C4e-F2 — P2: straight-line movement bypasses scene cancellation

`files/AgentControl.cpp:1295–1296` and `1341` dispatch to `moveTo` for explicit non-path movement, a previously missing helper, or failed outdoor planning. `moveTo` (`924–965`) neither captures nor checks a scene generation. It updates coordinates under `worldMutex` but sends its transform outside that lock.

Concrete interleaving: an outdoor move falls back after a helper timeout; the character zones/relogs while its loop sleeps. `onStartScene` changes the scene and resets coordinates; the old loop then continues toward the old destination using the new scene's self ID/position, potentially for the rest of its 95-second budget. A scene change can also occur between a straight-line position update and its send. The new `askHelper`/`walkPath` guards do not cover this path.

Fix: pass the captured generation to **every** movement implementation, including fallback and fight approaches; check it atomically with position changes and the corresponding sends. Test helper missing, helper failure and explicit `path=false`, interrupt each with zoning/relog, and assert no subsequent old-plan movement is emitted. Source-supported; no live packet replay performed.

Disposition of C4d-F3: **partly resolved**. Unique IDs plus scene generation reject old helper replies and planned path steps in the reviewed guarded path. Straight-line fallback still violates the broader cancellation guarantee.

## Other checks and commit dispositions

| Area | Review result |
|---|---|
| `421adb15`, C4d-F2 cancellation | Resolved in source: lines 95–101 recheck pending-task identity and follower online state after the cross-lock; stale tasks return without removing a replacement or rescheduling. Pair validation remains under both locks. Contended stop/switch/logout runtime tests remain open. |
| `421adb15`, outdoor proof | Arguments match `getRecastPath(start,end,area,path,len,allowPartial)`. Coordinate conversion is performed inside the helper. Partial routing is enabled, but endpoint snapping is bounded to 2.5 m. Rejecting route size <2 fails closed; endpoint-near-wall and mesh-boundary cases still need map tests. |
| `9ac7cdcd`, planned walks | Generation is captured for the whole planned move, checked during helper waits, each position/send step and final stop. Old current-ID replies are discarded after a processed scene start. Direct/fallback movement remains F2 above. |
| `find` authorization | `AgentPathCommand.h:58–62` checks actual account membership in `Core3.AgentAccounts` before every helper mode. No caller-supplied account identity is trusted. It is **not independently test-galaxy-only**; keep it off ordinary accounts and narrow visibility before live use. |
| `find` bounds and visibility | Radius clamped to 1–3000 m, search word at least 3 characters, duplicate OIDs merged, sorted nearest-first, at most 30 returned objects. **30 is an output cap, not a scan/work cap**: it accumulates all hits before sorting, including loaded interiors, with no player-entry/visibility filter. Suitable only for trusted bot tooling as currently scoped. Large-search/concurrent-container-mutation stress checks remain open; catch-all is not a synchronization guarantee. |
| `tell` sender | Server `ChatManagerImplementation.cpp:1463–1471` derives sender from authenticated connection, not message body. Packet fields in the body match `ChatInstantMessageToCharacter.h` parsing. No sender impersonation path found. |
| `tell` scope/result | This is the ordinary player IM protocol, **not a bot-only server helper**. `AgentControl` exposes it only in agent-control mode, but that is not an account allowlist. Body `ok/sent` means submitted, not delivered: server can reject offline, nonexistent, ignored or muted recipients. Existing Dorn report shows actual bot-to-bot receipt; offline/error acknowledgement decoding remains untested. |
| Send under `worldMutex` | Engine `BaseClient::sendPacket` can take the client lock. Supplied session/packet-handler context is server-side; older saved client handler locks itself, which is a different object. No demonstrated lock inversion from this packet alone. Requested the actual client session/dispatch path; do not claim deadlock freedom from server-side files. |
| `5b2a858f`, Hoth v1 | No new source finding. Region tuple shape matches `PlanetManagerImplementation::readRegionObject`; rectangular edges have positive extents. Loader selects `<zone>_regions.lua` for instantiated zones. Hoth travel-point fields follow the existing planet schema. Lua entry does not itself enable the zone. The reported 21/21 travel result is Claude's existing evidence, not a new run here. |
| `c402e480`, creatures | No new source finding in this bounded static pass. **20** creature registrations (commit prose says 19), 11 lair registrations, 11 world-spawn lair references, all resolve within export. Includes/registrations and per-file source/modification notices present. Zero-size rectangle is allowed for WORLDSPAWNAREA by the region parser. Kept high difficulty/resists are owner's requested inherited balance, not silently normalized. Actual combat/loot/balance acceptance remains separate. |

## Second-hop refusal: diagnosis to collect

The 02:55 Dorn report records 9/10, ending 12.0 m away and warning “no navmesh route between the ends”. This warning combines **recast returning false** and **recast returning fewer than two points**; it does not prove a disconnected route. `getRecastPath` can return true with an empty vector when its 3D area-sphere gate excludes both endpoints, or a one-point straight path after snapping both endpoints to one position. Its nearest-poly query uses asymmetric `{8,8,3}` recast extents; mesh height and nearest-poly selection also merit checking. None is proven to be the actual Dorn cause.

Best next step: log exact start/end XYZ, selected area ID/centre/terrain height/radius, nearest-poly references and positions, Detour statuses, number of polygons and returned point count **at the failed second hop**. Compare initial successful hop to the failing one. Separate the two warning cases. Do not enlarge tolerance, allow synthetic fallback or force a teleport merely to make 9/10 become 10/10.

## Evidence and limits

`offline-results.json` records SHA-256 hashes of every reviewed exported source/context file and the static/model results. Hoth registration analysis and source assertions passed. Existing reports and Claude's probe claims were inspected as prior evidence only. WSL attempt returned `E_ACCESSDENIED`; runtime verification requested from Claude through the shared inbox. Actual client lock-order context remains requested. No private configuration, credentials or databases read. No imported art downloaded or cleared by this code review. No server commit created.
