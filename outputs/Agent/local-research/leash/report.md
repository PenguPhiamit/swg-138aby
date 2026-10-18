# Report: The /leash Command

## 1. Short answer

The `/leash` command is a follow-assist feature for group members, not a pet or crew mechanic. When enabled, it periodically checks whether the follower (the player who issued the command) has gotten stuck while using the client's `/follow` on a group leader. If the follower drifts more than 10 m from the leader and fails to close the gap after three consecutive 2-second checks, the server teleports the follower along a proven walkable path to a point up to 3 m behind the leader. The feature can be toggled with `/leash [name|target]` to start and `/leash off` to stop, or via right-click menu on a group member. It only works for player creatures in the same group on the same planet, and is disabled by default in config (`Core3.LeashEnabled = false`).

## 2. How it works

### Conditions to start a leash
- The issuer must be a player creature (line 386).
- The feature must be enabled in config; otherwise the server sends "The leash is turned off on this galaxy." and rejects the command (lines 389-392).
- The leader must be resolved from either a name argument (`/leash <name>`) or a target object ID passed by the right-click menu (lines 401-408).
- Both players must be in the same group, on the same planet, and both online; `checkPair()` returns reasons like "you are not in a group with X", "X is on another planet", or "X is offline" (lines 151-156).

### Arguments
- `/leash <group member name>` — start leashing to that player.
- `/leash <target>` — if no name is given but a target is selected (e.g., via right-click), use that target (lines 403-408).
- `/leash off` — stop the current leash (line 401).
- Naming the current leader again keeps the leash active; the server replies "Already leashed to X. /leash off to stop." (lines 412-415).

### Timings and thresholds
- The `LeashTask` runs every `INTERVAL = 2000 ms` (line 47).
- It considers the follower stuck when the distance exceeds `STUCK_RANGE = 10 m` and has not decreased by at least 0.5 m for `STUCK_CHECKS = 3` consecutive checks (lines 48, 125-128).
- When un-sticking, it teleports the follower to a point up to `BEHIND = 3 m` short of the leader along a proven walkable route (line 51, lines 290-316).
- The leash ends if distance exceeds `MAX_RANGE = 512 m` (lines 50, 112-115).
- Additional constants: `ON_MESH = 2.5 m` for navmesh tolerance (line 52), `DOOR_STEP = 12 m` for doorway checks (line 53).

### What the server does when stuck
- It calls `unstick()`, which finds a path via `PathFinderManager::findPath()` (line 277).
- Every step of the route is verified walkable by `whyNotWalkable()` (lines 168-195), which checks navmesh coverage, floor triangles inside cells, and doorway constraints.
- If no walkable path exists, the follower receives "Leash: there's no walkable way to X from here." (line 280).
- If the route gains less than 2 m or ends where the follower already is, it sends "Leash: you're already as close to X as the ground allows; keep following." (lines 345-349).
- If the leader is inside a building the follower cannot enter, it sends "Leash: X is inside a building you can't enter." (lines 357-359).
- On successful teleport, the follower receives "Leash: you were stuck, so you've been moved closer to X." (line 364).

### When the leash stops automatically
The `checkPair()` function and distance checks in `run()` end the leash with these messages via `stop()`:
- "no leader" — leader is null or same as follower (lines 82-85, 143-144).
- "X is offline" — leader's ghost is null or not online (lines 148-149).
- "you are not in a group with X" — group IDs differ (lines 151-152).
- "X is on another planet" — zones differ (lines 154-155).
- "you are too far from X" — distance > MAX_RANGE (lines 112-115).
- The task also stops if the follower logs out, is removed from the group, or changes planet (lines 73-78, inferred from zone/ghost checks).

### Busy-state blocking
While the follower or leader is riding a mount, or the follower is in combat, dead, or incapacitated, the leash does not attempt to unstick (line 117-118). The `stuckChecks` counter resets when distance drops back within STUCK_RANGE (lines 120-124).

### Skill mods and numbers
The source file contains no skill modifiers or stat calculations. All behavior is driven by the hardcoded constants above and navigation-path validation.

## 3. What a bot test should check

### Setup requirements
1. Two player characters on the same planet, in the same group.
2. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies).
3. Ensure neither character is in combat, dead, incapacitated, or mounted.

### Observable results to verify
- **Starting a leash**: Issue `/leash <leader name>` and confirm receipt of "Leashed to X: keep using /follow; if it gets stuck you'll be moved closer. /leash off to stop." (lines 437-438).
- **Stuck detection**: Move the follower more than 10 m away from the leader while keeping the client `/follow` active. Wait at least 6 seconds (3 checks × 2 s) without closing the gap by 0.5 m. Verify the follower is teleported closer and receives "Leash: you were stuck, so you've been moved closer to X." (line 364).
- **Stopping a leash**: Issue `/leash off` and confirm "Leash off." (line 419).
- **Already leashed**: Issue `/leash <current leader>` again and confirm "Already leashed to X. /leash off to stop." (line 413).
- **Invalid targets**: Try leashing a non-group member, an offline player, or someone on another planet; verify the appropriate "Can't leash: ..." message (line 431).
- **Busy states**: While mounted or in combat, attempt to trigger unstick and confirm no teleport occurs.

### State checks
- Before and after unstick: compare follower position relative to leader (should be closer, within BEHIND range if route reaches the leader).
- Verify the pending task "leash" exists while active and is removed after `/leash off` or automatic stop.

## 4. Likely reasons a test sees no effect

1. **Feature disabled**: `Core3.LeashEnabled` defaults to false in config-local.lua (line 37); the server rejects with "The leash is turned off on this galaxy." (line 390).
2. **Not in a group**: `checkPair()` requires matching group IDs (lines 151-152).
3. **Different planets**: Zone mismatch ends the leash immediately (lines 154-155).
4. **Busy states**: Combat, death, incapacitation, or either player mounted blocks unstick attempts (line 117-118).
5. **No walkable path**: If navmesh or floor data cannot connect the two positions, the server warns but does not teleport (lines 280, 337).
6. **Distance never exceeds threshold**: The follower must drift beyond 10 m and fail to close the gap for three consecutive checks; normal `/follow` behavior may keep distance within range.
7. **Target resolution failure**: If the name argument does not match an online player, `leader` remains null and the server shows usage help (lines 423-425).

## 5. Open questions

1. **The right-click menu implementation**: The comment mentions "right-click a group member → 'Leash (follow assist)' / 'Stop leash'" (line 33), but the menu handler code is not in this file.
2. **How `checkPair()` is called from the command vs. the task**: The command calls it once at startup (line 428); the task calls it every tick (line 103). It is unclear whether there is a separate registration mechanism that links the menu action to `LeashCommand`.
3. **What happens when the leash ends due to group change or planet switch**: The code removes the pending task and sends a message, but does not specify whether the leader's side receives any notification (inferred).
4. **Config file location**: The comment says "config-local.lua" (line 37), but this is a C++ header; the actual Lua config loading is in an unlisted file.
5. **Interaction with other follow-assist or pathing systems**: It is unclear whether `/leash` conflicts with or complements any existing server-side follow mechanics not described here.
