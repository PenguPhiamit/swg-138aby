# Report: Village Jedi Progression Mechanics

## 1. Short Answer

Under VILLAGEJEDIPROGRESSION, a character becomes "glowing" (force-sensitive) by earning five specific badge types in required quantities: 3 exploration_jedi, 2 exploration_dangerous, 5 exploration_easy, 1 master, and 5 content badges. The server checks this condition each time a badge is awarded and also on player login. Once glowing, the player enters an intro sequence with timed delays: first an old man encounter (12–36 hours) that grants a force crystal, then a Sith shadow attack (1–12 hours), then a waypoint to Dathomir that awards village access and the `force_title_jedi_novice` skill. The holocron is a force-replenishment item usable once per day by Jedi. Visibility rises through NPC sightings and decays over 21 days; a Jedi appears on bounty terminals at 1500 visibility points. A bot test can verify states, quests, inventory items, and system messages without needing a real Jedi, though the exact badge template IDs and message string keys are not listed in these files.

## 2. How It Works: Conditions, Skill Mods, Numbers, Timings, and Messages

### Becoming "Glowing" (Force-Sensitive)

**Required badges** (glowing.lua lines 5–11):
- exploration_jedi: 3 badges
- exploration_dangerous: 2 badges
- exploration_easy: 5 badges
- master: 1 badge
- content: 5 badges

The server checks these conditions in two places:
1. **Badge award event** (glowing.lua lines 59–71): When any badge is awarded, `badgeAwardedEventHandler` calls `hasRequiredBadgeCount`. If all five badge types are met and the player lacks `force_title_jedi_novice`, it sets the state `VILLAGE_JEDI_PROGRESSION_GLOWING` (value 1, from village_jedi_manager_common.lua line 43) and calls `FsIntro:startPlayerOnIntro`.
2. **Player login** (glowing.lua lines 82–91): `onPlayerLoggedIn` re-checks the badge count if the player is not already glowing.

The check function `getCompletedBadgeTypeCount` iterates through each required badge type and counts how many distinct badge templates of that type the player has earned (glowing.lua lines 14–42).

### The Intro Sequence

**Step 1: Old Man Visit (FsIntro state OLDMANWAIT = 1)**
- Delay: 12–36 hours (fs_intro.lua line 15). Additional days are added based on `FsIntroOldManVisits` count (lines 60–69).
- When the delay passes, `OldManIntroEncounter:start(pPlayer)` is called (fs_intro.lua lines 181–184).
- The old man spawns within 64–96 units and follows the player (old_man_intro_encounter.lua line 17).
- When the player enters range (16 units), the old man speaks: `@quest/force_sensitive/intro:oldman_greeting` with the player's first name (old_man_intro_encounter.lua lines 34–36).
- State changes: step set to OLDMANMEET (2), quest `OLD_MAN_INITIAL` activated (old_man_intro_encounter.lua lines 38–39).
- After conversation ends, the old man despawns after 10 seconds (old_man_intro_encounter.lua line 6).

**Step 2: Force Crystal**
- When the encounter finishes, the player receives a force crystal item: `object/tangible/loot/quest/force_sensitive/force_crystal.iff` (old_man_intro_encounter.lua line 78).
- System message: `@quest/force_sensitive/intro:crystal_message` (old_man_intro_encounter.lua line 87).
- State changes: `VILLAGE_JEDI_PROGRESSION_HAS_CRYSTAL` set (value 2, village_jedi_manager_common.lua line 44), quests `OLD_MAN_INITIAL` and `OLD_MAN_FORCE_CRYSTAL` completed.
- The visit counter `FsIntroOldManVisits` is incremented (old_man_intro_encounter.lua lines 157–165).

**Step 3: Sith Shadow Attack (FsIntro state SITHWAIT = 3)**
- Delay: 1–12 hours (fs_intro.lua line 16).
- `SithShadowEncounter:start(pPlayer)` is called (fs_intro.lua lines 189–193).
- The player receives a waypoint datapad (`object/tangible/loot/quest/force_sensitive/waypoint_datapad.iff`) during this phase (village_jedi_manager.lua line 32 references `SithShadowEncounter:useWaypointDatapad`).

**Step 4: Go to Dathomir**
- After the Sith encounter, `GoToDathomir:start(pPlayer)` is called (fs_intro.lua lines 225–228).
- The player receives a waypoint to Dathomir at coordinates (5306, -4145) with description `@quest/force_sensitive/intro:goto_dath_sum` (go_to_dathomir.lua lines 9–10).
- When the player arrives in the active area: quest `FS_VILLAGE_ELDER` is completed (go_to_dathomir.lua line 26).
- System message: `@quest/force_sensitive/intro:force_sensitive` (go_to_dathomir.lua line 47).
- State changes: `VILLAGE_JEDI_PROGRESSION_HAS_VILLAGE_ACCESS` set (value 4, village_jedi_manager_common.lua line 45), Jedi state set to 1 via `PlayerObject(pGhost):setJediState(1)` (go_to_dathomir.lua lines 49–51), and skill `force_title_jedi_novice` awarded (go_to_dathomir.lua line 53).

**Completion of Village Phase:**
- After completing the village phase, `VILLAGE_JEDI_PROGRESSION_COMPLETED_VILLAGE` (value 8) is set when the player masters 6 force-sensitive branches (village_jedi_manager.lua lines 155–157).
- The number of branches required is defined as `NUMBEROFTREESTOMASTER = 6` (village_jedi_manager.lua line 9).

### Skill Prerequisites

**canLearnSkill checks** (village_jedi_manager.lua lines 102–122):
- Force-sensitive skills require the corresponding `VillageUnlockScreenPlay:<branch>` state to be >= 2 (lines 103–110).
- `force_title_jedi_rank_01` requires at least 24 force-sensitive skills (line 113).
- `force_title_jedi_rank_03` requires `villageKnightPrereqsMet` to return true (lines 117–119).

**canSurrenderSkill checks** (village_jedi_manager.lua lines 125–142):
- Cannot surrender `force_title_jedi_rank_02` or `force_title_jedi_novice`.
- Cannot surrender force-sensitive skills if player has `force_title_jedi_rank_02` and skill count drops to 24 or below.

### The Holocron

The holocron (`village_jedi_manager_holocron.lua`) provides force power replenishment:
- **Usage check** (lines 11–19): Player must be a Jedi (`PlayerObject(pGhost):isJedi()`) and not on cooldown for `USEDHOLOCRON` (24-hour cooldown, line 4).
- **Force check** (lines 24–32): Player's current force power must be less than maximum.
- **On use** (lines 37–51): Sets force to maximum, sends message `@jedi_spam:holocron_force_replenish`, adds cooldown, and destroys the holocron item.
- **If not Jedi**: Sends `@jedi_spam:holocron_no_effect` ("The holocron hums briefly, but otherwise does nothing.") (line 64).
- **If at max force**: Sends `@jedi_spam:holocron_force_max` ("You are already at your maximum Force power.") (line 57).

## 3. What a Bot Test Should Check

### Observable Results

**States and flags to verify:**
1. `VILLAGE_JEDI_PROGRESSION_GLOWING` state (value 1) on the player after badge requirements are met (village_jedi_manager_common.lua line 43).
2. `VILLAGE_JEDI_PROGRESSION_HAS_CRYSTAL` state (value 2) after old man encounter (village_jedi_manager_common.lua line 44).
3. `VILLAGE_JEDI_PROGRESSION_HAS_VILLAGE_ACCESS` state (value 4) after Dathomir arrival (village_jedi_manager_common.lua line 45).
4. `FsIntroStep` screen play data: values 1 (OLDMANWAIT), 2 (OLDMANMEET), 3 (SITHWAIT), etc. (fs_intro.lua lines 5–12, 20–33).
5. `FsIntroOldManVisits` counter in screen play data (old_man_intro_encounter.lua line 88).

**Quests to check:**
- `OLD_MAN_INITIAL` activated during old man encounter (old_man_intro_encounter.lua line 39).
- `OLD_MAN_FORCE_CRYSTAL` completed after receiving crystal (old_man_intro_encounter.lua line 86).
- `FS_VILLAGE_ELDER` activated when waypoint is given and completed upon Dathomir arrival (go_to_dathomir.lua lines 26, 45).

**Inventory items:**
- Force crystal: `object/tangible/loot/quest/force_sensitive/force_crystal.iff` (old_man_intro_encounter.lua line 78).
- Waypoint datapad: `object/tangible/loot/quest/force_sensitive/waypoint_datapad.iff` (fs_intro.lua line 250).

**System messages to capture:**
- `@quest/force_sensitive/intro:crystal_message` after old man encounter (old_man_intro_encounter.lua line 87).
- `@quest/force_sensitive/intro:force_sensitive` when going to Dathomir (go_to_dathomir.lua line 47).
- `@jedi_spam:holocron_force_replenish` when using holocron (village_jedi_manager_holocron.lua line 45).

**Skills:**
- `force_title_jedi_novice` awarded after Dathomir arrival (go_to_dathomir.lua line 53, also fs_intro.lua line 373).

### Setup Required for Bot Test

1. Ensure the player character has earned all five required badge types in the specified quantities (glowing.lua lines 5–11).
2. Verify the player does not already have `force_title_jedi_novice` skill before triggering the progression.
3. The bot must wait through the timed delays: 12–36 hours for old man, then 1–12 hours for Sith shadow (fs_intro.lua lines 15–16).

## 4. Likely Reasons a Test Sees No Effect

1. **Badge requirements not met**: The player lacks one or more of the five required badge types in sufficient quantity (glowing.lua lines 5–11). Without all five types, `hasRequiredBadgeCount` returns false and no glowing state is set.
2. **Already has force_title_jedi_novice**: If the skill exists, the progression is skipped entirely (village_jedi_manager.lua line 58, glowing.lua line 64).
3. **Timed delays not elapsed**: The old man encounter waits 12–36 hours and the Sith shadow waits 1–12 hours (fs_intro.lua lines 15–16). A test that does not wait will see no encounters.
4. **Player is dead, incapacitated, or out of position**: Encounters reschedule if the player is not in a valid state when the delay expires (fs_intro.lua lines 87–90).
5. **Quest already completed**: If `FS_VILLAGE_ELDER` is already complete, the intro sequence is considered finished (fs_intro.lua line 36).
6. **Player lacks Jedi state for holocron**: The holocron only works if `PlayerObject(pGhost):isJedi()` returns true (village_jedi_manager_holocron.lua line 18).

## 5. Open Questions

The provided files do not answer:

1. **Exact badge template IDs**: The code references badge types (exploration_jedi, exploration_dangerous, etc.) but does not list the specific badge template numbers or names that count toward each type (glowing.lua lines 5–11).
2. **Force-sensitive branch skill names**: While `village_jedi_manager_common.lua` lists 16 force-sensitive branch skills (lines 6–21), the files do not explain how a player unlocks each branch or what quests/activities grant them.
3. **Old Man and Sith Shadow NPC templates**: The old man uses template "old_man" (old_man_intro_encounter.lua line 17), but the Sith shadow template name is not specified in these files.
4. **The `villageKnightPrereqsMet` function**: Referenced in village_jedi_manager.lua line 117, but its implementation is not in the provided files.
5. **GM tool in village_gm_sui.lua**: This file is listed in TASK.md's file list but was not found in the src/ directory. No GM tool for forcing progression is shown in the available code.
6. **Exact string ID definitions**: The system messages use string keys like `@quest/force_sensitive/intro:oldman_greeting` and `@jedi_spam:holocron_force_replenish`, but their actual text content is not defined in these files.
7. **How the `VillageUnlockScreenPlay:<branch>` states are set**: The code checks for state value >= 2 to allow learning force-sensitive skills (village_jedi_manager.lua line 107), but does not show what sets these states initially.

## Claude's review (18 Oct 2:53 AM)

Checked against the copies in `src/`. Accurate on the main points:
- the five badge types and amounts (glowing.lua:5-11);
- all five needed (`== #requiredBadges`, 44-46), checked on each badge award and at login (59-91);
- the 12-36 h and 1-12 h delays (fs_intro.lua:14-17);
- the Dathomir waypoint at (5306, -4145) (go_to_dathomir.lua:9-12);
- the holocron: Jedi only, a 24 h cooldown, refills the Force and is destroyed (village_jedi_manager_holocron.lua:3-64);
- the terminal threshold of 1500 (visibility_manager.lua via VisibilityManager.cpp:196).

**One correction: the Dathomir rewards come when the waypoint is given, not on arrival.**
- `onSuccessfulSpawn` (go_to_dathomir.lua:33-55) does all of the following:
  - activates FS_VILLAGE_ELDER;
  - sets the village-access state;
  - sends `@quest/force_sensitive/intro:force_sensitive`;
  - sets Jedi state 1;
  - awards `force_title_jedi_novice`.
- Arriving (`onEnteredActiveArea`, 21-28) only completes FS_VILLAGE_ELDER.
- So a test sees the skill and the message as soon as the waypoint appears.

Not covered: `village_gm_sui.lua` was named in the question but left out of the sources by Claude, so the GM tool is still unread. Verdict: usable for the Jedi scenario with this correction.
