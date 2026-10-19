# Force-Sensitive Unlock Path (Village of Aurilia) — Report

## 1. Short Answer

The Force-sensitive village path begins when a player meets an old man NPC who gives them a force crystal if they do not already have one. The village runs on rotating phases lasting three weeks each, with four total phases cycling continuously. In Phase 1 the player completes twenty patrols through Sarguillo, which unlocks the `force_sensitive_combat_prowess_ranged_accuracy` branch and rewards a banner pole item. An experience converter NPC lets players trade standard XP into Force-sense XP at category-specific ratios (e.g., 5:1 for bountyhunter combat XP). The server uses the same VillageJediManager screenplay that checks eligibility via `VillageJediManagerCommon.isVillageEligible` and gates skill learning behind a `VillageUnlockScreenPlay:` state value.

## 2. How It Works

### Meeting the Old Man
- The old man's conversation handler (`old_man_conv_handler.lua`) decides which screen to show based on whether the old man "belongs" to the player (lines 7-13). If he does not belong, the player sees `nothing_to_discuss`.
- When the player selects the option that triggers `"here_is_the_crystal"` (line 25), the handler calls `OldManIntroEncounter:giveForceCrystalToPlayer(pPlayer)` (line 31) and schedules the old man to despawn.
- The actual crystal item is defined in `elder_conv_handler.lua` as `CRYSTAL_OBJECT = "object/tangible/loot/quest/force_sensitive/force_crystal.iff"` (line 3). The elder handler checks whether the player already has this item in their inventory before giving a new one (lines 16-22).

### Village Phases
- `village_jedi_manager_township.lua` defines four total phases (`VILLAGE_TOTAL_NUMBER_OF_PHASES = 4`, line 9) with each phase lasting three weeks (`VILLAGE_PHASE_DURATION = 7 * 24 * 60 * 60 * 1000`, line 12).
- Phase changes occur at 18:00 server time (`phaseChangeTimeOfDay = { hour = 18, min = 0 }`, line 10).
- The township screenplay spawns/despawns mobiles and scene objects per phase (lines 277-372) and tracks the current phase via quest status keys `Village:CurrentPhase` and `Village:phaseID` (lines 101-128).
- During a phase switch, active quests are failed for online players (`doOnlinePhaseChangeFails`, lines 404-418), which calls phase-specific fail handlers like `FsPhase1:doPhaseChangeFails` (line 406).

### Phase 1 Patrols (Sarguillo)
- The Sarguillo conversation handler (`sarguillo_phase1_conv_handler.lua`) tracks patrol completion via the stored value `FsPatrolCompletedCount` (lines 10, 48).
- When the count reaches 20, the handler completes `FS_PATROL_QUEST_20` and `FS_PATROL_QUEST_FINISH`, clears the current quest ID, marks the phase quest complete, gives the player a banner pole item (`object/tangible/item/quest/force_sensitive/fs_village_bannerpole_s01.iff`, lines 97-110), and unlocks the branch `force_sensitive_combat_prowess_ranged_accuracy` (line 95).
- The handler also checks eligibility: the player must be in Phase 1 and pass `VillageJediManagerCommon.isVillageEligible(pPlayer)` (line 16).

### Experience Converter
- Located in `convohelpers/experience_converter.lua`, the converter defines XP conversion tables for four categories: combat, senses, reflex, and crafting (lines 12-67).
- Each entry is a `{skillName, minimumXP}` pair. For example, combat requires `bountyhunter` ≥ 5 XP, `combat_general` ≥ 3 XP, etc. (lines 14-24).
- The converter opens a SUI list (`sendConversionSUI`, lines 94-143), then a transfer box (`convertXpTransferCallback`, lines 229-318) where the player selects how much XP to convert.
- Conversion uses a ratio: `convertedXp = math.floor(xpToConvert / ratio)` (line 275). The system checks caps via `getExperienceCap("fs_" .. conversionType)` (lines 283-298) and awards the converted amount with `awardExperience("fs_" .. conversionType, convertedXp, false)` (line 312).
- System messages use string IDs like `@quest/force_sensitive/utils:convert_not_enough_for_conversion` (line 125) and `@quest/force_sensitive/utils:xp_convert_gain` (line 314).

### Skill Gating & Unlock States
- `village_jedi_manager.lua` line 58-60: on login, if the player is village eligible and lacks `force_title_jedi_novice`, it awards that skill.
- Line 107: learning any skill matching `force_sensitive_` requires `getScreenPlayState("VillageUnlockScreenPlay:" .. skillNameFinal) >= 2`. State values are documented in `experience_converter.lua` lines 6-9: 0 = not qualified, 1 = qualified but not unlocked, 2 = branch unlocked.
- Line 155-158: when a player completes enough force trees (six, defined by `NUMBEROFTREESTOMASTER` on line 9), the manager sets the completed state and calls `FsOutro:startOldMan(pPlayer)`.

### Old Man Outro
- When the outro old man conversation reaches `"where_camp"` (line 32 in `old_man_conv_handler.lua`), it updates FS progression step to 3, completes `OLD_MAN_FINAL`, and starts `MellichaeOutroTheater:start(pPlayer)` (lines 34-44).

## 3. What a Bot Test Should Check

### Setup
1. Ensure the zone `dathomir` is enabled (line 135 in township checks this).
2. Verify the player has no force crystal (`force_crystal.iff`) in inventory before talking to the elder or old man.
3. Confirm the village is in Phase 1 for Sarguillo patrols (check `Village:CurrentPhase` quest status).

### Observable Results
- **Old Man / Elder interaction**: After selecting the appropriate option, the player should receive a system message confirming item creation or an "inventory full" error (`@error_message:inv_full`, line 32 of elder_conv_handler.lua). The old man should become non-conversable (option bit cleared, lines 23-28 of old_man_conv_handler.lua) and despawn.
- **Patrol completion**: After 20 patrols, check that `FsPatrolCompletedCount` equals 20, the player has completed `FS_PATROL_QUEST_FINISH`, and the banner pole item exists in inventory. The branch unlock state should be set to 2 for `force_sensitive_combat_prowess_ranged_accuracy`.
- **Experience conversion**: After using the converter, verify that standard XP decreased by the converted amount (line 305), `fs_<category>` XP increased by `convertedXp` (line 312), and system messages about conversion appear. Check that the SUI windows close properly.
- **Skill gating**: Attempting to learn a `force_sensitive_` skill before the unlock state reaches 2 should fail silently or show an error; after unlocking, it should succeed.

### States to Query
- `Village:CurrentPhase` (quest status)
- `VillageUnlockScreenPlay:<branchName>` (screenplay state)
- `FsPatrolCompletedCount` (stored village value)
- Inventory for `force_crystal.iff` and `fs_village_bannerpole_s01.iff`
- Skills: `force_title_jedi_novice`, any unlocked `force_sensitive_` skills

## 4. Likely Reasons a Test Sees No Effect

- **Wrong phase**: The village may be in Phase 2, 3, or 4, so Sarguillo patrols are unavailable (`VillageJediManagerTownship:getCurrentPhase() ~= 1`, line 16 of sarguillo handler).
- **Zone disabled**: If `dathomir` is not enabled, the township screenplay skips initialization entirely (line 135).
- **Not village eligible**: `VillageJediManagerCommon.isVillageEligible(pPlayer)` may return false for the test character; this function is not defined in the provided files.
- **Already has the crystal**: The elder checks inventory first (lines 16-22 of elder_conv_handler.lua) and will not give another one.
- **Inventory full**: The elder sends `@error_message:inv_full` if the container is full (line 32).
- **XP below threshold**: The converter only lists skills meeting their minimum XP requirement (lines 117-122); if no skills qualify, it shows `convert_not_enough_for_conversion` (line 125).
- **FS XP cap reached**: If the player already has max FS XP in the target category, conversion is blocked with `convert_at_fs_skill_cap` (line 287).
- **Old man already despawned or not assigned**: The old man conversation handler checks `doesOldManBelongToThePlayer` (lines 7-9); if false, only `nothing_to_discuss` is shown.

## 5. Open Questions

- **`VillageJediManagerCommon.isVillageEligible`**: This function is called in multiple files (e.g., township line 16, sarguillo line 16, village_jedi_manager line 58) but its implementation is not in the provided files. It likely checks race, faction, or other prerequisites.
- **`VillageJediManagerCommon.forceSensitiveBranches`**: The array of branch names used by `getBranchLearnList` (experience_converter.lua line 77) is referenced but not defined here.
- **`VillageJediManagerCommon.hasUnlockedBranch`**: Similarly, the unlock-check function is called but its logic is missing.
- **`OldManIntroEncounter.giveForceCrystalToPlayer`** and **`doesOldManBelongToThePlayer`**: The old man handler references these methods (lines 7-8, 31 of old_man_conv_handler.lua) but the encounter class file is not included.
- **`FsOutro:startOldMan`**, **`FsPatrol:start`**, **`FsPatrol:completeFsPatrol`**: These phase-specific screenplay objects are called but their source files are absent.
- **Exact XP cap values** for each `fs_<category>` experience type — the code checks caps (line 283) but does not define them.
- **How `VillageUnlockScreenPlay:` states are set to 1 or 2** — the converter comments explain the values (lines 6-9 of experience_converter.lua) but no file in this set shows where state transitions occur.

## ChatGPT's review (2026-10-18 22:36)

Checked all six supplied snapshots against current Core3-dev 9d08e265 (matching), with the common eligibility/unlock helper. No Saluki disputed lead. Source only; no Jedi progression or account changes.

**Holds:** four rotating phases,old-man ownership dialogue,elder replacement crystal path,XP conversion ratios/caps and six-tree outro trigger appear in the supplied code.

**Corrections:**
- **Phase duration is seven days**, not three weeks: VILLAGE_PHASE_DURATION=7*24*60*60*1000; the trailing '3 weeks' comment is stale (bin/scripts/screenplays/village/village_jedi_manager_township.lua:12). Initial scheduling uses this duration; the18:00 alignment belongs to later scheduling helpers, not an unconditional first-switch wall-clock guarantee (16-52).
- Sarguillo unlocks ranged_accuracy at **10 patrols**, not20. Twenty grants final quest completion/banner (bin/scripts/screenplays/village/convos/phase1/sarguillo_phase1_conv_handler.lua:88-110). Those are separate milestones.
- unlockBranch sets state2 when current state0 (village_jedi_manager_common.lua:82-90); this is an actual state transition source missing from the report's open-question list. Eligibility is village-access progression bit **and completed FS_VILLAGE_ELDER**, not speculative species/faction conditions (62-67).
- Converter entries are XP conversion **ratios**, which also serve minimum-XP listing checks. Standard XP debit is convertedXp*ratio after rounding/remainder removal and cap adjustment, not the same numerical amount as the FS XP gain (convos/convohelpers/experience_converter.lua:258-312).
- The force_sensitive skill gate shown applies only when its name contains '0', strips the last3 characters and requires branch state>=2 (bin/scripts/managers/jedi/village_jedi_manager.lua:102-111), not every matching novice/master name indiscriminately. Unlocking is only one prerequisite; XP/skill points and other skill-tree gates still apply.
- This is a village-path excerpt, not the complete initial Force-sensitive unlock/old-man scheduling eligibility. Elder crystal replacement does not establish the old-man grant's duplicate/inventory behavior; those separate functions need their own checks.

Verdict: Material corrections required for one-week phases,10-patrol unlock,XP debit units and scoped skill eligibility; gameplay/progression untested.
