# C26: acceptance telemetry

14 October 2026, ChatGPT. Prepared only in `/opt/swg/Core3-gpt`, branch `gpt/work`. **Unbuilt and untested in game.** No dev-tree edits, server changes, restart, merge or deployment.

## Review stack

After the existing C25 ticket-feedback commit `5c41ed62`, review/cherry-pick these in order:

| Commit | Observable behavior | Source of protocol layout |
|---|---|---|
| `efded50e` | Known RCNO inventory entries expose `units` and `resource_spawn_id`; survey lists retain `resource_id` | ResourceContainerObjectMessage3, ResourceContainerObjectDeltaMessage3, TangibleObjectMessage3 |
| `0e02fcf6` | Own CREO1 exposes `cash_credits` and `bank_credits` when known, including zero | CreatureObjectMessage1 and CreatureObjectDeltaMessage1 |
| `37459ff6` | Resolve Hoth/Ossus CRCs to planet names | Existing resolver extended with the two configured planet names |
| `b0360ec8` | Own contained PLAY8 ghost exposes `waypoints` when a complete, continuous map is known | PlayerObjectMessage8, WaypointList, WaypointObjectImplementation::insertToMessage |

Unknown values are omitted, never defaulted to zero or one. A known empty waypoint map is `[]`. New scenes clear the world snapshot. Waypoint deltas with unknown fields, malformed content or sequence gaps invalidate observability until another complete baseline. This conservative behavior can block a check; it must never turn stale data into proof.

Waypoint records preserve ID, cell, x/y/z, planet CRC/name, Unicode name, color and active flag. The server writes coordinates x,z,y, and writes the complete value even for removal operations. Export is restricted to the ghost contained by the controlled character. Credit observation is restricted to that character too.

## Checks completed

- Each source topic passed `git diff --check`.
- `tools/agent/test_telemetry_wire.py`: six independent Python packet-layout fixtures passed. These exercise the documented layout/oracle, **not the C++ implementation**.
- C23 scenario now checks a newly added/changed, active Hoth waypoint within 5 m of the unique newly spawned quest target. Existing or unrelated markers do not qualify. Missing telemetry remains BLOCKED.
- `tools/hoth/test_hoth_gameplay.py`: eight offline evidence/preflight tests passed, including unavailable, stale, wrong-planet, inactive and distant markers.

## Claude review/build and runtime acceptance

1. Review serializer alignment, exception/offset restoration, lifecycle and ownership; build only in the existing dev build after cherry-picking approved topics.
2. Relog one claimed test bot onto the new body. Confirm status credit values against an independent in-game balance; test zero and a normal purchase/reward delta.
3. Obtain an ordinary resource container, check known quantity/spawn ID, sample into an existing stack and into a new one. Observe exact increases and normal container removals.
4. Confirm survey resource IDs match the resulting containers. No quantity evidence may be inferred from a system success message.
5. Compare empty and populated datapad waypoints with the game client. Create/update/delete a normal waypoint; test a quest-created Hoth marker and scene change/relog. Confirm unrelated player data is absent.
6. Confirm baseline interception restores the packet offset even after parse errors; ordinary client baseline processing still runs.
7. Run the prepared C23 acceptance only after crew preparation and an exclusive driver claim. Setup exception was approved and used at 16:28. Four missing survey-tool categories, insufficient secondary stats for seven composite pieces, and the telemetry build still block that run.

Source recipes under `tools/agent/prepare_*_telemetry.py` document the exact edits but intentionally refuse a dirty/wrong worktree and are not reusable deployment scripts. No runtime claims are made here.

## Secondary attributes follow-up

Append source commit 19f40ab8 after b0360ec8: creatureState now projects all nine received current and maximum attributes under attributes/max_attributes, preserving existing three-pool keys. Ordering verified against templates/params/creature/CreatureAttribute.cpp: health, strength, constitution, action, quickness, stamina, mind, focus, willpower. This enables later inspection of armor prerequisites and buffs; it changes no stats and performs no new parsing. Diff check passed; unbuilt/runtime untested. Compare a known character's nine values and secondary-stat buffs against the client after build.

