# Bot control update — 14 October 2026

ChatGPT implemented outside-server Python changes authorized by the owner. No galaxy connection, runtime changes, C++ edit or deployment. No commit: the workspace is not a git checkout.

## Behavior

- `squad.py halt` is checked before issuing each body command and during Bot.idle, Bot.wait_for and the Hoth scenario's boarding waits. Cancellation raises RunStopped and is recorded as stopped, not a successful scenario.
- `--minutes` now also supplies a monotonic cooperative deadline to each scenario. Expiry stops at a checkpoint rather than waiting for another round.
- A command already sent to the body is allowed to reply or time out before cancellation. Abandoning a reply could let it be mistaken for a later request. No body cancellation API is assumed. Existing scenarios using direct time.sleep or CPU loops remain uninterruptible during those sections; migrate them to g.sleep as they are revised. This is not a hard deadline guarantee.
- `squad.py activity` reads per-group activity JSON without issuing game commands. Records include scenario, last command, state, time, PID and stop request. Records older than 120 seconds are explicitly stale. A finished record means the scenario ended; bots may still be logged in. Activity is observational, not proof that a process is alive or moving. Terminal states include finished, blocked, failed, error, stopped and no_checks.
- Hoth purchase assertions require a newly observed ticket object ID. That proves a new ticket object, not its route metadata; arrival remains a separate check. Existing tickets no longer establish purchase success.
- All four Hoth walking legs require both an arrival result and an observed outdoor Hoth position within eight metres of the target. Nearby terminal templates also count as outpost evidence when display names are missing.

## Offline verification

`check_run_control.py`: three passing tests covering STOP during a long cooperative wait, expired deadline/stale records and concurrent activity publication.

`check_hoth_scenario.py`: two passing tests covering old-ticket rejection and both failed/successful walking loops. These use fake bots and do not establish gameplay behavior.

Python compilation passed for the modified runner and scenario. Activity command executed locally and correctly reported no records/current activity unknown.

## Runtime review needed

Claude: under the existing test-galaxy ownership, run a short Hoth scenario; request halt during a boarding wait; confirm stopped state and no further commands. Repeat with a small minute budget and with halt during a body move, observing that the move completes/times out before stopping. Check normal travel still buys a fresh ticket and all four legs have real arrivals. Do not promote based on the offline fixtures.

AGENTS.md now records owner authorization for independent Python bot work and isolated C++ bot slices while Claude is unavailable. Server-lock coordination, cross-review and live approval remain. Codex WSL access is still unresolved.

Adaptive healing/sampling/assist routines are proposed in pre-cu-macro-bots-and-squad-routines.md; this update does not implement those routines. Coronet travel UI remains a separate reported diagnostic task.
