# GCW Base Shutdown Mechanic Report

## 1. Short Answer

Faction bases cycle through a vulnerability window every ~48 hours that lasts 2 hours (configurable via `vulnerabilityFrequency` and `vulnerabilityDuration`). During vulnerability, attackers can jam the base's uplink band by narrowing it down to the correct channel, then identifying it. Once jammed, an attacker interacts with the HQ terminal to start a shutdown countdown of 10 minutes (`destructionTimer`). Defenders can abort this countdown within the window, triggering a reboot sequence. If the countdown completes, the base is destroyed (static bases flip faction; player-placed bases refund a unit). The entire cycle repeats automatically after each vulnerability ends.

## 2. How It Works

### Vulnerability Cycle

- **Frequency & Duration**: The server configures `vulnerabilityFrequency` (default 172800 s = 48 h) and `vulnerabilityDuration` (default 7200 s = 2 h) in GCWManager.idl lines 149-150.
- **State machine**: A base's `DestructibleBuildingDataComponent` tracks states: `INVULNERABLE`, `VULNERABLE`, `JAMMED`, `BAND`, `SHUTDOWNSEQUENCE`, `REBOOTSEQUENCE` (referenced in GCWManager.idl line 20 and throughout the .cpp files).
- **Checking**: `performGCWTasks()` iterates all bases every `gcwCheckTimer` seconds (default 3600 s, line 148) and calls `checkVulnerabilityData()` to advance timers [lines 1184-1214]. If the next vulnerable time has passed but the end time hasn't, it calls `startVulnerability()` [line 1200].
- **`isBaseVulnerable()`**: Returns true when state > `INVULNERABLE` or when the base lacks the `OVERT` flag [line 1247].

### Starting Vulnerability

When the scheduled time arrives, `StartVulnerabilityTask` runs `startVulnerability()` [lines 973-1004]:
1. Calls `renewUplinkBand()` to randomize the uplink channel [line 976].
2. Verifies minefields, scanners, and turrets [lines 994-996].
3. Spawns base terminals (HQ terminal, security terminal, override terminal) via `spawnBaseTerminals()` [line 998].
4. If the base is OVERT, schedules `EndVulnerabilityTask` for `vulnerabilityDuration` seconds later [line 1001].
5. Broadcasts updated cell permissions [line 1003].

### Jamming the Uplink Band

Attackers use the security terminal to jam the uplink:
1. **Narrowing**: The player selects a band; `verifyUplinkBand()` checks if it matches the current band. If not, it gives directional hints ("search higher/lower") or white noise with ~3% failure chance [lines 1541-1549]. On match, state changes to `BAND` and the player sees "You narrow the carrier signal down to Band #X" [line 1536].
2. **Identifying**: Once on the correct band, the next attempt identifies it: state becomes `JAMMED`, and the player receives "You isolate the carrier signal to Channel #X" and "Jamming complete! You disable the uplink..." [lines 1518-1520]. The player also gets 1000 bounty hunter slicing XP [line 1521].
3. **PVE bases**: If the base is not OVERT, a `UplinkTerminalResetTask` resets the jam after 24 hours [lines 1524-1531].

### Starting Shutdown

Once jammed, an attacker interacts with the HQ terminal:
1. `startAbortSequenceDelay()` checks the `declare_overt_cooldown` (default 300 s / 5 min from `overtCooldown`, line 168) [lines 2283-2290].
2. Sends "Structure shutdown request received. Please stand by..." [line 2292].
3. Schedules a `BaseShutdownTask` after 60 seconds and registers observers for parent change / destruction to detect aborts [lines 2294-2299].

### Base Destruction Countdown

After the shutdown task completes, `scheduleBaseDestruction()` runs:
1. Checks vulnerability or `force` flag; skips if already has a destroy task or facility is rebooting [lines 2154-2165].
2. Broadcasts to all players within 64 m: "COUNTDOWN INITIATED: estimated time to detonation: X minutes" where X = `destructionTimer / 60` (default 10 min, line 155) [lines 2169-2172].
3. Sets state to `SHUTDOWNSEQUENCE` [line 2173].
4. Schedules `BaseDestructionTask` to run every 60 seconds, decrementing the countdown and broadcasting updated messages [lines 2176-2178, 2202-2208].
5. Activates `DESTRUCTALARM` [line 2180].

### Aborting Shutdown (Defenders)

A defender calls `abortShutdownSequence()` while the base is vulnerable and has a destroy task:
1. Cancels and drops the destroy task [lines 2304-2308].
2. Sets state to `REBOOTSEQUENCE` [line 2317].
3. Broadcasts "COUNTDOWN ABORTED: FACILITY SHUTTING DOWN!!" [lines 2319-2320].
4. Schedules `BaseRebootTask` after 60 seconds [lines 2322-2323].
5. Deactivates alarms [line 2325].

### Base Destruction (Final)

When the countdown reaches zero, `doBaseDestruction()` executes:
- **Static bases**: Notifies `FACTIONBASEFLIPPED` observer event; structure remains [lines 2223-2225].
- **Player bases**: If owner is online, sends a refund message ("A faction base you placed has been destroyed...") based on remaining base count [lines 2229-2243]. Then unregisters the GCW base and calls `StructureManager::destroyStructure()` to remove it [lines 2246-2248].

### End of Vulnerability

When `vulnerabilityDuration` expires, `EndVulnerabilityTask` runs `endVulnerability()`:
1. Despawns terminals [line 1018].
2. Advances `lastVulnerableTime` and calculates next cycle: adds `vulnerabilityFrequency` to find the next start time, then adds `vulnerabilityDuration` for the end time [lines 1020-1030].
3. Sets state to `INVULNERABLE` [line 1031].
4. Cancels any pending destroy task [lines 1039-1044].
5. Reschedules the next vulnerability start [line 1047].
6. Deactivates alarms and broadcasts cell permissions [lines 1053-1054].

### Resetting Vulnerability Timer

A faction leader can call `resetVulnerability()` to force a new cycle early:
- Requires the `resetTimer` (default 604800 s = 7 days) to have passed since last reset [lines 2339-2340, 151].
- Resets `lastResetTime`, advances all vulnerability timers by one cycle, cancels pending start task, and reschedules [lines 2346-2367].
- Sends "The vulnerability for this structure has been reset" to the caller [line 2370].

## 3. What a Bot Test Should Check

### Setup Required
1. Place or locate an OVERT player faction base (check `ObjectFlag::OVERT` via `getPvpStatusBitmask()`).
2. Ensure the base is in the `VULNERABLE` state (`baseData->getState() > INVULNERABLE`). If not, wait for the cycle or use `resetVulnerability()` if 7 days have passed since last reset.
3. Confirm terminals are spawned (HQ terminal, security terminal, override terminal) by checking child objects of the building.

### Observable Results to Verify

**Uplink Jamming:**
- Before jamming: uplink band is unknown; player gets directional hints when guessing wrong bands.
- After narrowing to correct band: state = `BAND`; message "You narrow the carrier signal down to Band #X".
- After identifying: state = `JAMMED`; messages "You isolate the carrier signal to Channel #X" and "Jamming complete! You disable the uplink..."; verify 1000 bounty hunter slicing XP awarded.

**Shutdown Initiation:**
- After jamming, interact with HQ terminal as attacker faction.
- Check `declare_overt_cooldown` is cleared (or test after waiting 5 min).
- System message: "Structure shutdown request received. Please stand by..."
- Wait ~60 s for the BaseShutdownTask to complete.
- Verify state changes to `SHUTDOWNSEQUENCE`.
- Broadcast messages within 64 m: "COUNTDOWN INITIATED: estimated time to detonation: X minutes" (X starts at 10, decrements each minute).
- Verify `DESTRUCTALARM` is active.

**Abort by Defenders:**
- Defender interacts with HQ terminal during countdown.
- Destroy task is cancelled; state changes to `REBOOTSEQUENCE`.
- Broadcast: "COUNTDOWN ABORTED: FACILITY SHUTTING DOWN!!".
- After ~60 s, reboot completes and base returns to a functional state (state should eventually cycle back).

**Full Destruction:**
- Let the 10-minute countdown complete without abort.
- Verify state transitions through countdown messages until zero.
- For static bases: verify `FACTIONBASEFLIPPED` observer event fires; faction changes.
- For player bases: verify owner receives refund message (if online); base structure is destroyed and unregistered from GCW manager.

**End of Vulnerability:**
- Wait for `vulnerabilityDuration` (default 2 h) to expire.
- Verify state returns to `INVULNERABLE`.
- Terminals are despawned.
- Alarms deactivated.
- Next vulnerability cycle is scheduled correctly.

## 4. Likely Reasons a Test Sees No Effect

1. **Base not OVERT**: The base lacks the `OVERT` flag (`getPvpStatusBitmask() & ObjectFlag::OVERT` is false). Many mechanics, including vulnerability scheduling and terminal spawning, skip non-OVERT bases [lines 1000-1001, 1008, 1247].
2. **Not in vulnerable state**: The base is `INVULNERABLE`; terminals are not spawned and jamming/shutdown cannot proceed. The test must wait for the cycle or force a reset (7-day cooldown applies).
3. **Cooldown on overt declaration**: The attacker has used `declare_overt` recently; `overtCooldown` (default 300 s) blocks shutdown initiation [lines 2283-2290].
4. **Already has destroy task**: If a destroy task is already scheduled, `scheduleBaseDestruction()` returns early [line 2154].
5. **Facility rebooting**: During `REBOOTSEQUENCE`, `isFacilityRebooting()` returns true and shutdown is blocked [lines 2160-2165].
6. **Wrong faction**: The attacker must be of the opposing faction to use terminals; `canUseTerminals()` and `areOpposingFactions()` enforce this (function bodies not in provided files).
7. **PVE base auto-destruction**: If `allowPveBases` is false and the base is not OVERT, it gets scheduled for destruction immediately [lines 354-358].

## 5. Open Questions

1. **How terminals are spawned**: `spawnBaseTerminals()` and `despawnBaseTerminals()` are declared native in GCWManager.idl lines 325-326; their implementation is not in the provided files. We don't know which terminal templates are used or where they spawn.
2. **`canUseTerminals()` logic**: Declared native at line 247; the faction/permission checks that determine who can interact with each terminal are missing.
3. **`areOpposingFactions()` logic**: Native at line 248; we don't know how it defines "opposing" for jamming vs. shutdown permissions.
4. **Uplink band renewal**: `renewUplinkBand()` is native (line 254); the range of possible bands and the randomization algorithm are unknown.
5. **`isBandIdentified()` / `isUplinkJammed()`**: Native at lines 236-237; we don't know if these check state or a separate flag.
6. **BaseShutdownTask completion**: The task that runs after the 60-second delay is not in the provided files; we assume it calls `scheduleBaseDestruction()`, but this is inferred.
7. **`isFacilityRebooting()` implementation**: Native at line 243; unclear if it checks state == `REBOOTSEQUENCE` or a separate timer.
8. **Exact terminal interaction flow**: The menu/SUI flow for selecting bands and initiating shutdown is not visible in these files; the client-side protocol is unknown.

## ChatGPT's review (2026-10-18 22:33)

Checked supplied matching snapshots and current Core3-dev 9d08e265, including the HQ radial and task/callback. No Saluki disputed lead was listed. Source only.

**Holds:** vulnerability task cycle, two-stage uplink game, countdown scheduling, defender cancellation/reboot, static flip observer and player-base destruction are present (GCWManagerImplementation.cpp:973-1054,1506-1538,2153-2248,2302-2325).

**Corrections:**
- Active Lua vulnerabilityDuration is **10800 seconds = three hours**, not the IDL fallback two hours; frequency172800, destruction600 and overtCooldown300 are configured (bin/scripts/managers/gcw_manager.lua:5-8,26,54; GCWManagerImplementation.cpp:92-104).
- **Jamming alone cannot start attacker overload.** HQMenuComponent.cpp:74-76,166-175 requires power-overloaded state and outdoors_squadleader_novice. Intermediate security/DNA/power progression is omitted. The report's test is therefore incomplete.
- startAbortSequenceDelay/BaseShutdownTask is the **defender abort** confirmation path, not attacker detonation initiation: after60 seconds it opens confirmation (BaseShutdownTask.h:38-78), and BaseShutdownSuiCallback.h:53 calls abortShutdownSequence. Attacker uses ShutdownSequenceTask from HQMenuComponent.cpp:174. Correct this reversed flow before writing scenarios.
- Non-OVERT bases are treated vulnerable; they do spawn terminals and can reset the uplink after24 hours. Non-OVERT alone is not a reason all mechanics are skipped (GCWManagerImplementation.cpp:1247,1524-1531).
- canUseTerminals is implemented, requires alive/conscious, same cell, <=5 m and overt status for PvP/covert-or-higher for PvE, unless privileged after spatial/state checks (1394-1428). areOpposingFactions is both nonzero and unequal (1431-1435). State helpers and terminal spawning are implemented in this same file (1260-1357,3580 onward), not missing because IDL says native.
- A refunded base unit is placement capacity; no deed/item/credit refund is shown (2229-2248). Static faction flip requires its observer implementation; notification alone is not proof the faction changed.

Verdict: Reject the shutdown test as written: attacker/defender paths are reversed, prerequisite stages omitted and active duration wrong; retain corrected lifecycle facts; gameplay untested.
