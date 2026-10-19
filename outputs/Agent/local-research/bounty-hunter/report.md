# Bounty Hunting Mechanics Report

## 1. Short Answer

Bounty hunting has two branches: NPC bounties (spawning a target creature) and player bounties (tracking an online player). For NPC missions, the player speaks to an informant who sets the objective status through INITSTATUS → HASBIOSIGNATURESTATUS → HASTALKED based on informant level. The player then uses a droid item: CALLDROID summons an Arakyd probe from orbit over 20 seconds; TRANSMITBIOLOGICALSIGNATURE sends it to search; FINDTARGET or FINDANDTRACKTARGET deploys a Seeker droid. Success depends on skill mods (droid_find_chance, droid_track_chance) minus one-third of the target level, clamped 5–95. Visibility for player bounties is tracked separately by VisibilityManager: nearby creatures within 32 m add 0.25–1.0 visibility per tick; it decays over a configurable number of days via a scheduled task. When a bounty target dies and the hunter loots it, the mission completes and XP equals (reward + bonus) / 50.

## 2. How It Works

### Mission acceptance and informant levels
- The objective status starts at INITSTATUS (BountyMissionObjective.idl:47).
- updateMissionStatus() advances the status based on informantLevel: level 1 sets HASBIOSIGNATURESTATUS and updates the waypoint; level > 1 sets HASTALKED and updates the waypoint (BountyMissionObjectiveImplementation.cpp:205-239).
- The waypoint is updated with the target zone name and position, and at mission level 1 the player receives "@mission/mission_generic:target_location_received" (BountyMissionObjectiveImplementation.cpp:241-263).

### Activating the objective
- activate() checks whether the target is a player or NPC. For player targets it verifies the bounty hunter is in the target's bounty list and adds PLAYERKILLED observers; for NPC targets it starts BountyHunterTargetTask (BountyMissionObjectiveImplementation.cpp:35-51).
- BountyHunterTargetTask runs every 10 seconds, moves toward a destination (for level > 2 missions it first travels to a random starport), and spawns the NPC target when the player is within 256 units of the destination (BountyHunterTargetTask.h:49-117).

### Droid actions and requirements
- performDroidAction() checks playerHasMissionOfCorrectLevel(): FINDTARGET requires mission level ≥ 2; FINDANDTRACKTARGET requires level ≥ 3 (BountyMissionObjectiveImplementation.cpp:302-315).
- BountyHunterDroid::performAction() validates the action against mission level and objective status. If objectiveStatus is INITSTATUS it sends "@mission/mission_generic:bounty_no_signature" ("You must go speak with your informant before you can track your target.") (BountyHunterDroid.cpp:62-65).
- The player cannot use any droid while mounted; it sends "@error_message:survey_on_mount" (BountyHunterDroid.cpp:67-70, 130-133, 179-182).

### CALLDROID (Arakyd probe)
- Requires mission level ≥ 2 and objective not in INITSTATUS (BountyHunterDroid.cpp:100-115).
- Checks the player is not in a city region; if so, sends "@mission/mission_generic:probe_droid_bad_location" (BountyHunterDroid.cpp:122-128).
- Creates CallArakydTask with a 20-second countdown. Messages sent:
  - At t=20: "@mission/mission_generic:probe_droid_launch_prep" (CallArakydTask.h:57)
  - At t=3,2,1: "@mission/mission_generic:probe_droid_arrival_N" (CallArakydTask.h:70-73)
  - At t=0: "@mission/mission_generic:probe_droid_arrival", then spawns a "probot" NPC at calculated landing coordinates (CallArakydTask.h:74-86).
- The Arakyd droid remains for up to 300 seconds before despawning and clearing the objective's activeDroid reference (CallArakydTask.h:86-99).

### TRANSMITBIOLOGICALSIGNATURE (using the Arakyd)
- Requires mission level ≥ 2, objective not INITSTATUS, no existing Arakyd find task, and not mounted (BountyHunterDroid.cpp:161-183).
- Cancels any pending CallArakydTask, then creates a FindTargetTask with arakyd=true (BountyHunterDroid.cpp:184-190).

### FINDTARGET / FINDANDTRACKTARGET (Seeker droid)
- Requires mission level ≥ 2 (or ≥ 3 for tracking), objective not INITSTATUS, and not mounted (BountyHunterDroid.cpp:54-70).
- Spawns a "seeker" AI creature at the player's position, marks it STATIC, then creates a FindTargetTask with arakyd=false (BountyHunterDroid.cpp:72-83).

### FindTargetTask mechanics
- States: Init → DroidSent → Searching/Tracking → Completed (FindTargetTask.h:33).
- On init the droid sits; if arakyd the player sees "@mission/mission_generic:probe_droid_takeoff", otherwise "Biological scan received. Commencing planetary search pattern." (FindTargetTask.h:46-50).
- The droid despawns after 5 seconds, then enters Searching or Tracking (FindTargetTask.h:60-72).
- **Success calculation** (getSuccess()):
  - Skill used: droid_find_chance (max mod 155) for searching; droid_track_chance (max mod 125) for tracking (FindTargetTask.h:169-174).
  - successChance = skillMod + buffSkillMod − (targetLevel / 3), clamped to [5, 95] (FindTargetTask.h:176-190).
  - random(100) < successChance determines success (FindTargetTask.h:192-194).
- **Time calculation** (calculateTime()):
  - Skill used: droid_find_speed (max mod 115) for searching; droid_track_speed (max mod 105) for tracking (FindTargetTask.h:197-203).
  - time = 150 − checkedSkillMod + random(time / 2), in seconds (FindTargetTask.h:214-216).
- **On success**:
  - For Arakyd: sends "@mission/mission_generic:target_located_" + zoneName (FindTargetTask.h:133).
  - For Seeker on same planet: if AnonymousBountyTerminals config is true, shows "Analyzing biological signature... Target: FirstName LastName"; otherwise sends "@mission/mission_generic:assassin_target_location" with distance and direction (FindTargetTask.h:136-162).
  - If target is not on the same planet, sends "@mission/mission_generic:target_not_on_planet" (FindTargetTask.h:159-162).
- **On failure**: sends "@mission/mission_generic:target_not_found_N" (random 1-5) (FindTargetTask.h:78-80, 109-111).
- **Tracking mode** (track=true): if success and trackingsLeft > 0, sends "@mission/mission_generic:target_continue_tracking", reschedules, decrements trackingsLeft; when trackingsLeft reaches 0, sends "@mission/mission_generic:target_track_lost" (FindTargetTask.h:92-104).
- trackingsLeft comes from the player's droid_tracks skill mod (FindTargetTask.h:314).
- If the player leaves the zone during a Seeker task, success is set to false (FindTargetTask.h:339-342).

### Visibility for player bounties
- VisibilityManager loads configuration from scripts/managers/jedi/visibility_manager.lua (VisibilityManager.cpp:193).
- Configurable values: maxVisibility, terminalVisThreshold, falloffThreshold, pvpRatingDivisor, totalDecayTimeInDays, tickRateInSeconds (VisibilityManager.cpp:195-201).
- visDecayPerTick = maxVisibility / (totalDecayTimeInDays × 86400 / visDecayTickRate) (VisibilityManager.cpp:203).
- **Increasing visibility** (increaseVisibility): calls calculateVisibilityIncrease() which scans creatures within 32 m. For each valid creature (not dead, not incapacitated, not in same group if disabled):
  - If the player has no faction or the nearby creature has no faction: +0.5 (VisibilityManager.cpp:63-64).
  - Same faction: +0.25; different faction: +1.0 (VisibilityManager.cpp:67-73).
  - The result is multiplied by visibilityMultiplier and capped at maxVisibility (VisibilityManager.cpp:151-152).
- **Decay** (decreaseVisibility): uses elapsed time since last update, decays by visDecayPerTick per tickRateInSeconds seconds. If visibility drops to zero, clearVisibility() is called (VisibilityManager.cpp:82-102).
- performVisiblityDecay() iterates the visibilityList and calls decreaseVisibility on each entry (VisibilityManager.cpp:177-185).
- A player with visibility ≥ terminalVisThreshold appears on bounty hunter terminals; below falloffThreshold they are removed (VisibilityManager.h:25-30).

### Completing a bounty
- **NPC target killed**: handleNpcTargetKilled() checks if the loot owner is the bounty hunter or their group. If so, it calls complete() (BountyMissionObjectiveImplementation.cpp:530-546).
- **Player target killed**: handlePlayerKilled() is called via PLAYERKILLED observer; the code for this is not in the provided files (BountyMissionObjectiveImplementation.cpp:198-199, 205-239 shows status updates but not the kill handler body).
- **complete()** awards XP: expGain = (mission->getRewardCredits() + mission->getBonusCredits()) / 50, awarded as "bountyhunter" experience (BountyMissionObjectiveImplementation.cpp:129-131). It also calls completePlayerBounty() on the MissionManager (BountyMissionObjectiveImplementation.cpp:133).
- **clearVisibility()** is called when a player bounty target is killed, setting visibility to 0 and removing from the visibility list (VisibilityManager.h:152-156, VisibilityManager.cpp:163-175).

## 3. What a Bot Test Should Check

### Setup
- Accept a bounty mission of at least level 2 (for CALLDROID/FINDTARGET) or level 3 (for FINDANDTRACKTARGET).
- Speak to the informant until objectiveStatus reaches HASTALKED (informantLevel > 1).
- Ensure the player is not mounted and, for Arakyd droids, is not in a city region.

### Observable results to verify
1. **Waypoint**: After speaking to informant level 1+, check that a waypoint exists with the correct planet and position, and the system message "@mission/mission_generic:target_location_received" was sent (BountyMissionObjectiveImplementation.cpp:261).
2. **CALLDROID countdown**: Use an Arakyd droid item; verify 20-second countdown messages at t=20, 3, 2, 1, and arrival. Confirm a "probot" NPC spawns at the landing coordinates and objective's activeDroid is set (CallArakydTask.h:57-86).
3. **TRANSMITBIOLOGICALSIGNATURE**: After Arakyd arrives, use this action; verify the droid sits briefly then despawns, and a search/tracking result message appears within the calculated time (FindTargetTask.h:46-116).
4. **FINDTARGET / FINDANDTRACKTARGET**: Use Seeker droid items; verify the "seeker" NPC spawns at the player, sits for 5 seconds, then despawns. Check that success/failure messages appear and, on success, distance/direction or target name is shown (FindTargetTask.h:133-162).
5. **Skill impact**: Test with varying droid_find_chance / droid_track_chance skill mods to confirm the success formula (skillMod − targetLevel/3, clamped 5–95) and time formula (150 − skillMod + random) (FindTargetTask.h:168-216).
6. **Mission completion**: Kill the spawned NPC target and verify the bounty hunter receives the loot; check that complete() is called, XP is awarded as "bountyhunter" with value (rewardCredits + bonusCredits) / 50, and the mission status updates to TARGETELIMINATEDSTATUS (BountyMissionObjectiveImplementation.cpp:129-136, BountyMissionObjective.idl:50).
7. **Visibility for player bounties**: Have a target player perform actions near other creatures to increase visibility; verify they appear on bounty hunter terminals when visibility ≥ terminalVisThreshold and disappear when below falloffThreshold. After killing the target, verify clearVisibility() sets visibility to 0 (VisibilityManager.cpp:163-175, VisibilityManager.h:25-30).

### Test setup notes
- The test must ensure the mission object's objectiveStatus is not INITSTATUS before using droids.
- For player bounty testing, the target player must be online and have visibility > 0; the MissionManager must have them in the player bounty list (BountyMissionObjectiveImplementation.cpp:39).

## 4. Likely Reasons a Test Sees No Effect

1. **Objective status is INITSTATUS**: The informant has not been spoken to, or the mission level was insufficient to advance past INITSTATUS. Droid actions will fail with "@mission/mission_generic:bounty_no_signature" (BountyHunterDroid.cpp:62-65).
2. **Mission level too low**: CALLDROID and FINDTARGET require level ≥ 2; FINDANDTRACKTARGET requires level ≥ 3. The player will receive "@mission/mission_generic:bounty_no_ability" (BountyHunterDroid.cpp:100, BountyMissionObjectiveImplementation.cpp:309-314).
3. **Player is mounted**: All droid actions check isRidingMount() and fail with "@error_message:survey_on_mount" (BountyHunterDroid.cpp:67-70, 130-133, 179-182).
4. **Arakyd in a city region**: CALLDROID checks active areas for isCityRegion() and rejects the action (BountyHunterDroid.cpp:122-128).
5. **Target not on same planet**: If the Seeker droid searches and the target zone differs from the player's current zone, it sends "@mission/mission_generic:target_not_on_planet" and returns false (FindTargetTask.h:159-162).
6. **Visibility below threshold**: For player bounties, if the target's visibility is below terminalVisThreshold they will not appear on bounty hunter terminals. The test must ensure the target has performed actions near other creatures to build visibility (VisibilityManager.cpp:63-73).
7. **NPC target failed to spawn**: BountyHunterTargetTask moves toward a destination over 10-second ticks and spawns the target only when the player is within 256 units. If the player never gets close enough, or if the zone name is invalid (returns "dungeon1" as a fallback), the target will not spawn (BountyMissionObjectiveImplementation.cpp:389, BountyHunterTargetTask.h:82-114).
8. **Arakyd droid already active**: Calling CALLDROID again while one is active sends "@mission/mission_generic:probe_droid_too_many" (BountyHunterDroid.cpp:117-120).

## 5. Open Questions

1. **handlePlayerKilled() implementation**: BountyMissionObjectiveImplementation.cpp declares and calls handlePlayerKilled(arg1, arg2) at lines 198-199, but the function body is not in the provided files. It likely handles player bounty completion when the target player is killed.
2. **VisibilityManager::calculateReward()**: Declared in VisibilityManager.h:94 but not defined in the provided .cpp file. It presumably calculates the reward for a player bounty.
3. **scripts/managers/jedi/visibility_manager.lua**: The actual Lua configuration file that sets maxVisibility, terminalVisThreshold, falloffThreshold, pvpRatingDivisor, totalDecayTimeInDays, and tickRateInSeconds is not provided. Without it, exact visibility thresholds and decay rates are unknown.
4. **MissionManager::completePlayerBounty()**: Called at BountyMissionObjectiveImplementation.cpp:133 but its implementation is in an external file not provided. Its exact side effects (e.g., removing the target from the bounty list) are unclear.
5. **ObserverEventType::PLAYERKILLED handler details**: The code for when the bounty hunter themselves is killed (handlePlayerKilled) or when the NPC target receives damage (handleNpcTargetReceivesDamage, declared at BountyMissionObjective.idl:144 but body not in provided files) is missing.
6. **AnonymousBountyTerminals config behavior**: When true, the Seeker droid reveals the target's name; when false, it only gives distance/direction. The default value and how to toggle it are not specified in the provided files (FindTargetTask.h:136).
7. **Group visibility disable flag**: ConfigManager reads "Core3.PlayerManager.DisableGroupVisibility" at VisibilityManager.cpp:34, but its default behavior and interaction with group members is only partially described.

## ChatGPT's review (2026-10-18 22:33)

Checked Saluki disputed leads, matching snapshots and current Core3-dev 9d08e265. Source only.

**Holds:** level gates for droids, first five-second deployment delay (FindTargetTask.h:52), subsequent calculated search/track delays, level>2 starport movement and <256 m **currentPosition** spawn gate (BountyHunterTargetTask.h:85-116), capped skill and level-based success formula, and integer XP baseline (reward+bonus)/50. Saluki's deployment and tracking objections miss earlier lines or strip >; the original tracking paragraph says >0 correctly. Config tickRateInSeconds is a real Lua key; terminalVisThreshold is the member populated by key termThreshold (VisibilityManager.cpp:195-203).

**Corrections:**
- Status transitions to HASBIOSIGNATURESTATUS then HASTALKED are unconditional within their respective switch cases; informantLevel gates **waypoint updates**, not the transitions (BountyMissionObjectiveImplementation.cpp:214-235). The message key is @mission/mission_bounty_informant:target_location_received (261), as Saluki correctly notes.
- Completion is on OBJECTDESTRUCTION with loot **ownership rights**, not a requirement to loot the corpse (194-199,530-547). The short answer/test must not add that extra action.
- Visibility needs LOS as well as <=32 m and excludes god-mode witnesses (VisibilityManager.cpp:50-64). The +0.5 case is subject neutral OR witness faction is neither Imperial nor Rebel, not merely witness neutral. Increases are invoked events multiplied by visibilityMultiplier, not automatically every decay tick.
- Success rolls random(100)<chance have chance/101 probability, not exactly chance percent; failure message suffix random(5)+1 can be 1..6 (FindTargetTask.h:78,176-194; inclusive System.h:93). Speed skill+buff sum is clamped before time calculation (205-216).
- handlePlayerKilled and handleNpcTargetReceivesDamage are implemented in the supplied C++ at582 and556 onward; reject the missing-native-handler claims. The report is not a diagnosis of terminal offer availability.

Verdict: Droid/target framework useful after correcting status gates, message, loot-rights completion, visibility and probability details; gameplay untested.
