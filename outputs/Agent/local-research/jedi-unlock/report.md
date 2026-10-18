# Jedi Progression Report

## 1. Short Answer

The server is configured for VILLAGEJEDIPROGRESSION (value 2) by default in jedi_manager.lua line 14, though this can be changed at runtime via the C++ loadConfiguration function (JediManager.cpp lines 45-73). Under hologrind progression (which is not currently active), a character unlocks Jedi by mastering NUMBEROFPROFESSIONSTOMASTER (6) random professions from a predefined list of 37 options, triggering an SUI window with the message "Perhaps you should meditate somewhere alone..." and awarding the force_title_jedi_novice skill while setting jedi state to 1. Jedi visibility is capped at maxVisibility (8000), decays every tickRateInSeconds (3600 seconds) over totalDecayTimeInDays (21 days), shows on terminals above termThreshold (1500), and disappears below falloffThreshold (100). A bot test should verify the mastery count triggers the progression, check for system messages, skill acquisition, and jedi state changes. The village_jedi_manager.lua file is missing from the provided sources, so its exact mechanics cannot be determined from these files alone.

## 2. How It Works

### Conditions
- For hologrind progression, a player must master NUMBEROFPROFESSIONSTOMASTER (6) professions from getGrindableProfessionList() (hologrind_jedi_manager.lua lines 18-66). The list contains 37 professions with their string IDs and badge numbers.
- The check happens when a badge is awarded via badgeAwardedEventHandler (hologrind_jedi_manager.lua line 160), which calls checkIfProgressedToJedi (line 149).
- checkIfProgressedToJedi verifies: getNumberOfMasteredProfessions(pCreatureObject) >= NUMBEROFPROFESSIONSTOMASTER and not isJedi(pCreatureObject) (line 149).
- getNumberOfMasteredProfessions iterates through PlayerObject(pGhost):getHologrindProfessions() and counts how many haveBadge() returns true (lines 91-106).

### Skill Mods and Numbers
- When progression triggers, awardSkill(pCreatureObject, "force_title_jedi_novice") is called (hologrind_jedi_manager.lua line 142).
- PlayerObject(pGhost):setJediState(1) is executed (line 143).
- The getGrindableProfessionList() returns 37 professions with their badge numbers (lines 19-64).
- MAXIMUMNUMBEROFPROFESSIONSTOSHOWWITHHOLOCRON equals NUMBEROFPROFESSIONSTOMASTER - 2 = 4 (lines 7-8).

### Timings
- Visibility decays every tickRateInSeconds (60*60 = 3600 seconds, visibility_manager.lua line 5) over totalDecayTimeInDays (21 days, line 4).
- The holocron item check uses ITEMHOLOCRON constant (jedi_manager.lua line 9, hologrind_jedi_manager.lua line 235).

### Messages the Player Sees
- When unlocking Jedi via hologrind, the player receives a SUI window with "@quest/force_sensitive/intro:force_sensitive" and "Perhaps you should meditate somewhere alone..." (hologrind_jedi_manager.lua line 130).
- Using a holocron when mastered < MAXIMUMNUMBEROFPROFESSIONSTOSHOWWITHHOLOCRON shows system messages with profession names via sendSystemMessageWithTO (lines 218-219).
- When mastered >= MAXIMUMNUMBEROFPROFESSIONSTOSHOWWITHHOLOCRON, it sends "@jedi_spam:holocron_quiet" (line 205) and the holocron is destroyed from world and database (lines 240-241).

## 3. What a Bot Test Should Check

### Observable Results
- System message from SUI window ("Perhaps you should meditate somewhere alone...").
- Presence of force_title_jedi_novice skill in player's skill list.
- PlayerObject(pGhost):isJedi() returning true (hologrind_jedi_manager.lua line 118).
- The player having mastered NUMBEROFPROFESSIONSTOMASTER (6) professions from the grindable list.

### Setup Needed First
- Ensure jediProgressionType is set to HOLOGRINDJEDIPROGRESSION (jedi_manager.lua line 5). This requires modifying the Lua global before loadConfiguration runs, or changing the C++ configuration.
- Award badges for NUMBEROFPROFESSIONSTOMASTER (6) different professions from getGrindableProfessionList() (hologrind_jedi_manager.lua lines 19-64), triggering the BADGEAWARDED observer (line 173).
- The observer must be registered via registerObservers(pCreatureObject) which creates an observer for BADGEAWARDED events (line 173).

## 4. Likely Reasons a Test Sees No Effect

- jediProgressionType is not set to HOLOGRINDJEDIPROGRESSION (it defaults to VILLAGEJEDIPROGRESSION at line 14 of jedi_manager.lua).
- The player has not mastered exactly NUMBEROFPROFESSIONSTOMASTER (6) professions from the hologrind list.
- The BADGEAWARDED observer was not registered via registerObservers() (line 173), so checkIfProgressedToJedi is never called on badge awards.
- The holocron item type does not match ITEMHOLOCRON (hologrind_jedi_manager.lua line 235).
- The player already has jedi state set, so isJedi() returns true and the progression check fails (line 149).

## 5. Open Questions

- What are the exact mechanics of village_jedi_manager.lua? This file is referenced at line 57 of JediManager.cpp but was not provided in the source list.
- How does the visibility system interact with jedi state changes? The visibility_manager.lua only defines constants (lines 1-6) but no logic for how these values are used or applied.
- What does CUSTOMJEDIPROGRESSION require? custom_jedi_manager.lua only sets jediManagerName = "CustomJediManager" (line 1) with no progression logic.
- How is the force_title_jedi_novice skill structured and what abilities does it grant? This information is not in the provided files.
- What happens when a player surrenders a prerequisite skill? canSurrenderSkill returns true by default (jedi_manager.lua line 81), but the actual enforcement logic for Jedi skills is missing from these files.
- How are hologrind professions assigned to a player? onPlayerCreated randomly selects NUMBEROFPROFESSIONSTOMASTER (6) professions from the list and adds them via addHologrindProfession (hologrind_jedi_manager.lua lines 71-86), but it is unclear if this affects gameplay or is purely cosmetic.

## Claude's review (18 Oct 2:30 AM)

Checked against the copies in `src/`.

**Right:**
- The galaxy is set to the village progression (jedi_manager.lua:14). The C++ loader runs the matching Lua file (JediManager.cpp:50-64).
- The hologrind rules hold: 6 professions to master (hologrind_jedi_manager.lua:6), the check on each badge award (160-168), the SUI text (130), and `force_title_jedi_novice` plus Jedi state 1 (142-143).
- The visibility constants hold (visibility_manager.lua:1-6).

**Wrong:**
1. The list has **32** active professions, not 37. Lines 21-24 and others are commented out.
2. Only the **6 professions given to the character at creation** count, not any 6 from the list (71-86 and 98-104). This is not cosmetic, as the open question suggests.
3. A **quiet holocron is not destroyed.** When 4 or more of the 6 are mastered, `sendHolocronMessage` returns true and `useItem` returns before the destroy (203-206 and 236-238). Only a holocron that names the missing professions is destroyed (239-241).

**The main gap:**
- The topic's sources had no village files, so the report describes the hologrind progression, which is off.
- How a character unlocks Jedi on this galaxy is unanswered.
- The rerun `jedi-unlock-village` was queued 18 Oct with `village_jedi_manager.lua`, `screenplays/village/` (common, holocron, intro/glowing, fs_intro, old man, Dathomir) and `VisibilityManager.cpp`.
