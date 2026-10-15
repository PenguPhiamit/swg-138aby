# Browser bot monitor: planet maps and squad video

14 October 2026. Owner proposes a TortoiseBots-style browser monitor: actual video preferred for small squads; planet maps and moving markers sufficient at fleet scale. **Scoped design, not a working dashboard or video feed.** C28 / F100.

## Views

| View | Purpose | Suggested contents |
|---|---|---|
| Galaxy overview | Where the fleet is and what needs attention | One card per planet, online/stale counts, squad distribution, active incidents |
| Planet map | Watch many bots at once | Squad-colored markers, short trails, destinations when known, points of interest, search/filter and clustering |
| Selected squad | Understand a small group's behavior | Member markers, HAM/posture, current scenario/objective and recent events; optional live game video alongside |
| Bot detail | Investigate a particular bot | Last update, observed position, target/objective if available, recent path, current task and linked incident/report IDs |
| Incident/replay | Understand an earlier failure | Timestamped movement/events and available clips; link to C27 report and retest status |

Clicking a marker selects a bot; follow mode centers the view. Filters include squad, planet, movement/combat/gathering/dead state and active issues. Fleet mode uses map markers by default. Video runs only for selected squads/observer sessions, with an explicit disabled/disconnected indicator when unavailable. This is a browser view for owner/developers; testers can later get a separately approved restricted view.

## What exists now

- `tools/live_status.py` writes saved status every **five minutes**. Its `bots` field is formatted text, and during an active round it uses activity records instead of querying bodies. This is useful for availability and historical triage, not smooth live positions.
- `tools/bots/run_control.py` publishes group/scenario/state/detail/time activity records. These do not provide a complete structured per-bot position stream.
- Bot body status can expose planet, position, cell, HAM and posture when requested by its existing driver. Additional C26 credit/waypoint/secondary-attribute source is prepared but unbuilt; do not assume those keys exist in the running body.
- The existing `core3client --agent-control` bot is a protocol client, not a rendered SWG game window. Its telemetry cannot itself supply gameplay video.

The monitor therefore needs a telemetry producer before its map is live; adapting only today's saved status would make a sparse snapshot viewer.

## Telemetry architecture

Use **one producer/collector -> bounded local snapshots/event buffer -> read-only browser feed**. The existing driver/body publishes observations while it is already operating. The browser never acquires a bot driver or sends extra status/movement commands, and opening more tabs does not increase bot polling. A later implementation may use SSE or WebSocket delivery; no localhost server or externally reachable endpoint is started here.

Each observation needs a schema version, galaxy/environment ID, server-session epoch, bot-session ID, monotonically increasing sequence, observed timestamp, bot/squad ID, connected state, planet, cell, coordinate space, position and explicitly known HAM/posture/activity. Destinations, targets, paths and objectives are optional observed fields, never fabricated defaults. Only controlled bots are included initially; human players are outside this scope.

Reject older epochs and out-of-order samples; show the age of the last real observation. A restart/relog/zone change ends the old trail. Do not animate a line across planets or join unrelated interior/world coordinate frames. Any smooth marker interpolation is display-only, not a new measurement. Show stale/disconnected as separate states from idle/dead. Standing still while sampling, crafting or waiting for a shuttle is not sufficient evidence of being stuck.

Initial update targets for benchmarking: roughly 1–2 Hz for a selected squad, slower batched fleet updates, and a bounded trail window. These are proposals, not measured capacity. Publish once and fan out to viewers; use visible-region filtering/clustering and a Canvas renderer if fleet size warrants it. Prove CPU/RAM/bandwidth cost against a measured baseline before increasing rates. Never log an unbounded history per browser or per bot.

## Planet maps and interiors

Start with original coordinate grids and known points of interest. Use per-planet map bounds, axis orientation and projection metadata; do not assume every planet shares one square size. Calibrate using at least three known landmarks and real client positions before treating a marker as accurate.

Client map backgrounds may improve the view, but local extraction and remote web distribution are different uses and need the project's art-rights review. No client images are exported or distributed in this proposal. Keep an original grid fallback for incomplete planets/maps.

Indoor positions need an authenticated building/cell transform or a separate floor view. If only local cell coordinates are known, show an indoor badge at the last verified building/world position rather than plotting local x/y as planetary coordinates. Travel/space/unknown scenes must be labelled rather than silently placed on a ground map.

## Actual video for small squads

A graphical SWG observer client must render the scene for each independent view. One observer following a squad can cover that squad; it does not produce every bot's first-person view. Capture only that game window, with audio off initially. Camera tracking and switching are separate features that need in-game verification.

Proposed first experiment: one selected squad and one modest-resolution, low-frame-rate feed; measure its effect on the test server and existing client/GPU/RAM workload. Stream on demand, stop capture when no authorized viewer needs it, and retain only owner-approved incident clips. Browser live video transport and any encoder dependency still need selection/approval. No client launched, account created, capture/recording performed or streaming service installed here.

Agents may operate `um win` only after the owner is logged in and confirms they are at the PC. Any new observer account, software installation or remote exposure follows the existing owner-consent rules. The source design does not grant those permissions.

## Incidents and bug reports

Use evidence gates for possible-stuck, repeated action, prolonged death and unreachable target episodes. Unknown/stale telemetry is its own problem and cannot prove a game bug. Preserve legitimate waiting/gathering states. Deduplicate repeated detections into one episode.

C28 can attach a bounded position/event replay and any available clip to a **local C27 incident draft**. The agent reviews it before relaying a sanitized report to Discord. A monitor anomaly is not automatic permission to post, change server state or deploy a fix. Persist report evidence separately from disposable world restores, with bounded retention.

## TortoiseBots reference and ownership

The already-collected TortoiseBots source at `bc914eb3b5f484ede0d5161a68711f995161627d` documents map markers/trails, bot profiles, state census and gated incidents in `docs/guides/observability-dashboard.md`. See [prior source study](tortoisebots-study.md) and [version-specific brief](tortoisebots-prior-WoW-and-SWG-brief.md). This is source-snapshot evidence, not a new hosted-release audit. Use its design ideas; no code/assets ported or program executed in this session. Its code has component-specific GPL/AGPL/attribution terms requiring selected-file review if reuse is later chosen.

ChatGPT can own the outside-server collector/UI/replay tools. Claude reviews/implements or builds needed body/server telemetry under the shared slice rules. Implement a local owner-only, map-first prototype before remote developer access and a video experiment. A read-only monitor should not grow server-control buttons as part of this task.

## Acceptance and effort

1. Replay fixtures prove epoch/sequence rejection, stale labels, disconnect/reconnect, zone changes, non-moving legitimate work and indoor coordinates.
2. A test squad's real route agrees with map landmarks; the monitor cannot command a bot or compete with the driver.
3. A restart and planet transfer leave no false trails; multiple viewers share one producer and do not amplify collection.
4. Measure fleet-rate overhead and bounded memory/disk use; no performance claim based only on a small mocked demo.
5. One actual squad video agrees with the associated telemetry timestamp; hidden windows/disconnected observers are reported honestly.
6. Prove incident evidence survives reset and is sanitized before an approved Discord relay. Remote access/authentication is separately reviewed.

Maturity: **scoped with saved-source feasibility**. Difficulty: **Medium** for local map/status/replay; **High** for reliable low-overhead video/camera following; **Medium–High** for measured fleet scale and remote access. No implementation/game test/deployment claimed.
