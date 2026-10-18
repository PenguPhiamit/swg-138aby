# Entertainer Buffs Report

## 1. Short Answer

Dancing and playing music give buffs to audience members (patrons) who are grouped with the performer or set as a target via `/setPerform`, within `HEAL_RANGE` distance, and who watch or listen for at least 60 seconds. The buff strength is built up over time by the entertainer's `healing_dance_mind` or `healing_music_mind` skill mod (capped at 125%), and the buff duration accumulates at a rate modified by `accelerate_entertainer_buff`. Flourishes increase both wound healing and buff strength multiplicatively via `(flourishCount + 1)`. The performer must have the `private_buff_mind` skill mod to grant buffs at all. Nima's test likely failed because Dorn lacked `private_buff_mind` (and possibly `healing_dance_mind`), or because line of sight was broken during the watch attempt.

## 2. How It Works

### Conditions to Grant Buffs
- **Performer requirement:** The entertainer must have `private_buff_mind > 0` to be able to give buffs at all (`EntertainingSessionImplementation.cpp:608-612`).
- **Patron eligibility:** The patron must be in the same group as the performer (`entertainer->isGrouped() && entertainer->getGroupID() != creature->getGroupID()` check inverted at line 989) or set as a target via `/setPerform` (`entPlayer->getPerformanceBuffTarget() != patron->getObjectID()`). The patron must also not be on the performer's deny service list (line 992-993), and must not be incapacitated or dead (line 862-864).
- **Distance:** Patrons must be within `PerformanceManager::HEAL_RANGE` of the performer to receive healing and buff ticks (`EntertainingSessionImplementation.cpp:102`). If they move out of range, their watch/listen is stopped and they are removed from the patron list (lines 106-120).
- **Minimum time:** Patrons must watch or listen for at least 60 seconds before receiving a buff (`EntertainingSessionImplementation.cpp:876-881`). If less than 60 seconds have elapsed, they receive the system message "You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs."

### Skill Mods and Numbers
- **Buff strength cap:** For dancing, capped at `healing_dance_mind` skill mod; for music, capped at `healing_music_mind` skill mod. The absolute maximum is 125% (`EntertainingSessionImplementation.cpp:716-722`).
- **Building faction perk:** If the performer is in a registered building of their faction, `private_faction_buff_mind` adds to the max buff strength (lines 724-735).
- **Buff duration cap:** Maximum 120.0f + (10.0f / 60.0f) = 2 hours 10 seconds (`EntertainingSessionImplementation.cpp:699-700`).
- **Buff acceleration rate:** Duration increases by `2.0f * buffAcceleration` per tick, where `buffAcceleration = 1 + (accelerate_entertainer_buff / 100.f)` (`EntertainingSessionImplementation.cpp:995-997`). The tick interval is 10 seconds (`EntertainingSessionImplementation.cpp:236`).
- **Wound healing:** Calculated as `ceil(performance->getHealMindWound() * (woundHealingSkill / 100.0f))` for mind wounds and `ceil(performance->getHealShockWound() * ((playerShockHealingSkill + buildingShockHealingSkill) / 100.0f))` for shock wounds, then multiplied by `(flourishCount + 1)` (`EntertainingSessionImplementation.cpp:82-85`).
  - For dancing: `woundHealingSkill = healing_dance_wound`, `playerShockHealingSkill = healing_dance_shock` (lines 60-61).
  - For music: `woundHealingSkill = healing_music_wound`, `playerShockHealingSkill = healing_music_shock` (lines 63-64).
  - `buildingShockHealingSkill = private_med_battle_fatigue` skill mod (line 56).
- **Battle fatigue removal:** Requires `private_med_battle_fatigue > 0` (`canHealBattleFatigue()` at line 602-606). Shock wounds are healed first if this is true (lines 158-161), then mind/focus/willpower wounds (lines 162-170).

### Flourishes
- **Dancing:** Plays animation `skill_action_<flourishNumber>` (`EntertainingSessionImplementation.cpp:666-667`).
- **Music:** Broadcasts a `Flourish` packet with the flourish number (`EntertainingSessionImplementation.cpp:669-670`).
- Flourishes can occur up to 5 times per tick. Each flourish adds buff strength equal to `performance->getHealShockWound()` and triggers `addEntertainerFlourishBuff()` for all patrons (lines 674-687, 614-627).
- Flourish XP is capped per loop: dance has a cap of 1 (`10 / 10s`), music has a cap of 2 (`10 / 5s`) (`EntertainingSessionImplementation.cpp:681`).

### Timings
- The entertainer session ticks every **10 seconds** via `EntertainingSessionTask` scheduled at line 236.
- Each tick calls `doEntertainerPatronEffects()` (line 220), which heals wounds and increases buff duration/strength for all patrons in range.
- Buffs are applied to the patron **when they stop watching/listening** or when the performer stops, via `activateEntertainerBuff()` being called at some point after the watch period ends. The code checks minimum 60 seconds of elapsed time (line 877-878).

### Messages the Player Sees
- **Performer starts:** "@performance:dance_start_self" ("You begin dancing.") or music equivalent (`EntertainingSessionImplementation.cpp:417`).
- **Patron starts watching/listening:** The system message depends on the watch/listen command result; if line of sight fails, "@healing:no_line_of_sight" is shown.
- **Buff granted:** When a patron's buff activates, they receive a system message containing "performance_enhance_dance_mind" (for dance) or "performance_enhance_music_focus"/"performance_enhance_music_willpower" (for music). The buff CRCs are defined at lines 896-918.
- **Buff not granted (too short):** "You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs." (`EntertainingSessionImplementation.cpp:879`).
- **Performer stops:** "@performance:dance_stop_self" ("You stop dancing.") or music equivalent (`EntertainingSessionImplementation.cpp:562`).

## 3. What a Bot Test Should Check

### Observable Results
1. **System messages on the patron (Nima):**
   - Watch success: A system message confirming watch started (not "no_line_of_sight").
   - Buff received: A system message containing `performance_enhance_dance_mind` after watching for 60+ seconds and the performer stops.
2. **Buff on the patron:** After the buff message, check that Nima has a buff with CRC `STRING_HASHCODE("performance_enhance_dance_mind")` (line 914) using `creature->getBuff()`. Verify its strength and duration match expectations.
3. **Performer state:** Dorn should have `private_buff_mind > 0` and `healing_dance_mind > 0` as skill mods. Check via `entertainer->getSkillMod("private_buff_mind")` and `entertainer->getSkillMod("healing_dance_mind")`.
4. **Patron list:** Verify Nima is in Dorn's `patronDataMap` (accessible via the entertaining session) while watching.

### Required Setup
1. **Grouping:** Ensure the patron is grouped with the performer (`/group` command).
2. **Line of sight:** Position the patron close enough to the performer with clear line of sight (within ~10m, avoiding clutter as noted in dorn-social.py lines 83-92).
3. **Performer skills:** The entertainer must have:
   - `private_buff_mind > 0` (required to grant any buffs)
   - `healing_dance_mind > 0` (for dance buff strength cap) or `healing_music_mind > 0` (for music)
   - Optionally `accelerate_entertainer_buff > 0` to speed up buff accumulation
4. **Watch duration:** The patron must watch for at least 60 seconds before the buff can activate.

## 4. Likely Reasons a Test Sees No Effect

1. **Missing performer skill mod `private_buff_mind`:** If Dorn does not have this skill mod (checked at line 608-612 and line 983-984), no buffs are granted to any patron, regardless of watch time. This is the most likely cause given the context note questioning whether Dorn has it.
2. **Missing performer skill mod `healing_dance_mind`:** Without this, the buff strength cap is 0 (line 716), so `buffStrength` remains 0 and no buff is applied (line 889-890 returns early if `buffStrength == 0`).
3. **Line of sight failure:** The patron must have line of sight to start watching. If the watch command fails with "@healing:no_line_of_sight" (as noted in the context), the patron is never added to the patron list and receives no buffs.
4. **Out of range:** `HEAL_RANGE` (defined in PerformanceManager but not shown in the provided code) must be satisfied for healing and buff ticks. If the patron moves out of range, they are removed from the patron list (lines 106-120).
5. **Insufficient watch time:** The patron must watch for at least 60 seconds (line 877-878). Testing before this threshold is met will show no buff.
6. **Patron on deny service list:** If the patron is on the performer's deny service list, buffs are skipped (line 992-993).
7. **Patron incapacitated or dead:** Buffs are not applied to patrons who are incapacitated or dead (lines 862-864).

## 5. Open Questions

1. **What is the value of `HEAL_RANGE`?** It is referenced at `EntertainingSessionImplementation.cpp:102` as `PerformanceManager::HEAL_RANGE`, but the constant's value is not defined in the provided files. It may be in `PerformanceManager.h`.
2. **When exactly does `activateEntertainerBuff()` get called?** The code shows it checks conditions and applies buffs, but the call site that triggers buff application after the watch period ends is not visible in these files. It may be triggered when the patron stops watching or when the performer stops dancing.
3. **What are the exact values of `performance->getHealMindWound()` and `performance->getHealShockWound()`?** These come from the `performance.iff` datatable (loaded at `PerformanceManager.cpp:42-64`) and vary by performance type. The specific values for "basic" dance are not in the provided source files.
4. **What is the loop duration for dancing vs. music?** The code references `performance->getLoopDuration()` at line 679 to calculate flourish XP cap (dance = 10s, music = 5s inferred), but the exact values per performance are in the datatable.
5. **How does `/setPerform target` work?** The code checks `entPlayer->getPerformanceBuffTarget()` (lines 859, 989) as an alternative to grouping, but the command implementation and its effect on buff targeting is not shown in these files.
