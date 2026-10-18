# Report: Buying and Surrendering Skills at Trainers (Core3)

## 1. Short Answer

A player learns a skill by having the server call `SkillManager::awardSkill`, which first verifies prerequisites (species, required skills, Jedi state, admin level), then checks that the player has enough XP of the skill's type and enough free skill points (default cap 250 from config key `Core3.Sandbox.SkillPoints`). On success it deducts XP and skill points, adds the skill to the creature, applies all skill-modifier bonuses, grants associated abilities and draft schematics, updates XP caps, recalculates Force Power, awards badges for master skills, and syncs the player's level. The `/surrenderskill` command reverses this: it removes the skill and its modifiers/abilities/schematics, refunds skill points, updates limits and level, and handles pilot-skill retirement via a confirmation dialog. `/findmytrainer` only applies to Jedi rank-2+ players; it scans all zones for trainers matching six subcategories, picks one that is not in a tutorial or player-city zone, and creates a waypoint. The provided files do not show what the trainer NPC says when prerequisites are missing, nor how credits are charged (if at all).

## 2. How It Works

### Conditions checked before learning
- **Prerequisites** (`SkillManager.cpp:899-952`): `fulfillsSkillPrerequisites` checks admin level for `admin_` skills (line 906), required species (lines 910-922), required prerequisite skills (lines 924-937), and Jedi state requirement from the skill object (line 940). Force-sensitive skills delegate to `JediManager::canLearnSkill` (line 948).
- **XP check** (`SkillManager.cpp:858-862`): `canLearnSkill` verifies `ghost->getExperience(skill->getXpType()) >= skill->getXpCost()` unless `noXpRequired` is true.
- **Skill-point check** (`SkillManager.cpp:864-867`): `ghost->getSkillPoints() < skill->getSkillPointsRequired()` blocks learning.
- **Already has the skill** (`SkillManager.cpp:847-849`): returns false immediately.

### Skill mods and numbers applied on learn
- **Deducts skill points** (`SkillManager.cpp:365`): `ghost->addSkillPoints(-skill->getSkillPointsRequired())`.
- **Deducts XP** (`SkillManager.cpp:371`): `ghost->addExperience(..., skill->getXpType(), -skill->getXpCost(), true)`.
- **Adds skill to creature** (`SkillManager.cpp:374`): `creature->addSkill(skill, notifyClient)`.
- **Applies skill modifiers** (`SkillManager.cpp:379-382`): iterates `skill->getSkillModifiers()` and calls `creature->addSkillMod(SkillModManager::SKILLBOX, key, value, notifyClient)` for each.
- **Grants abilities** (`SkillManager.cpp:386-387`): `addAbilities(ghost, *abilityNames, notifyClient)`.
- **Adds draft schematics** (`SkillManager.cpp:400-401`): `SchematicMap::instance()->addSchematics(...)`.
- **Updates XP limits** (`SkillManager.cpp:404`): `updateXpLimits(ghost)` recalculates per-type caps from all skill-box `xpCap` values and defaults from `datatables/skill/xp_limits.iff` (lines 203-227).
- **Recalculates Force Power** (`SkillManager.cpp:408`): `ghost->recalculateForcePower()`.
- **Awards badges for master skills** (`SkillManager.cpp:412-424`): looks up badge by skill name in `BadgeList::instance()`.
- **Syncs skill-point sanity** (`SkillManager.cpp:426-439`): computes `totalSkillPointsWasted` from config default (250) minus sum of all owned skills' `getSkillPointsRequired()`, then forces `ghost->setSkillPoints(totalSkillPointsWasted)` if mismatched.
- **Updates player level** (`SkillManager.cpp:442`): `creature->setLevel(playerManager->calculatePlayerLevel(creature))`.
- **Sends speed/acceleration update** (`SkillManager.cpp:471-482`): `CreatureObjectDeltaMessage4` with terrain negotiation fields.
- **Verifies skill-box mods** (`SkillManager.cpp:484`): `SkillModManager::instance()->verifySkillBoxSkillMods(creature)`.

### Timings / side-effects
- Jedi tree completion triggers `JediManager::onFSTreeCompleted` for skills matching `force_sensitive*04` (line 445).
- Bounty-list updates for `force_title_jedi_rank_02` and `force_discipline` skills (lines 450-456, 654-659).
- Squadleader skills update group modifiers asynchronously via `Core::getTaskManager()->executeTask` (lines 459-466, 664-672).

### Messages the player sees
The provided files do **not** contain trainer dialogue or system messages for prerequisite failures. The only explicit message in these files is a god-only ability-grant message (`SkillManager.cpp:391-395`): `"ui", "skill_command_acquired_prose"` with TU set to the ability name.

### How `/surrenderskill` works
- **Command handler** (`SurrenderSkillCommand.h:28`): calls `skillManager->surrenderSkill(arguments.toString(), creature, true)`.
- **Validation** (`SkillManager.cpp:501-572`):
  - Returns false if skill not in map (line 504).
  - Returns true (no-op) if player doesn't have the skill (line 511).
  - Blocks surrender if any owned skill lists this one as required (`checkSkill->isRequiredSkillOf(skill)`, lines 517-523).
  - Force skills check `JediManager::canSurrenderSkill` (line 531).
  - Pilot skills show a SUI confirmation dialog with faction-specific text and a "Get Waypoint" button to the recruiter (lines 538-569); returns false until confirmed.
- **Removal** (`SkillManager.cpp:574-693`):
  - Removes related missions (line 574).
  - Calls `creature->removeSkill(skill, notifyClient)` (line 576).
  - Removes skill modifiers (lines 579-585).
  - Refunds skill points (`ghost->addSkillPoints(skill->getSkillPointsRequired())`, line 588).
  - Removes abilities only if no remaining skill grants them (lines 593-614).
  - Removes draft schematics (line 618).
  - Updates XP limits (line 621).
  - Handles FRS skill revocation if enabled (lines 625-627).
  - Recalculates Force Power (line 630).
  - Re-syncs skill-point sanity (lines 632-645).
  - Updates player level (lines 648-650).
  - Handles bounty-list and group-modifier updates for special skills (lines 652-673).
  - Sends speed/acceleration update (lines 677-688).
  - Verifies skill-box mods (line 690).
  - Calls `JediManager::onSkillRevoked` (line 691).

### How `/findmytrainer` works
- **Command handler** (`FindMyTrainerCommand.h:13-72`):
  - Requires player state, valid locomotion, player creature status, Jedi state >= 2, and `force_title_jedi_rank_02` skill (lines 14-29).
  - Uses `ghost->getTrainerZoneName()`; if empty or zone invalid, calls `setJediTrainer` (lines 36-51).
  - `setJediTrainer` (`FindMyTrainerCommand.h:74-151`) scans all zones for planetary objects with subcategory matching one of six trainer types: `trainer_brawler`, `trainer_artisan`, `trainer_scout`, `trainer_marksman`, `trainer_entertainer`, `trainer_medic` (line 79).
  - Filters out tutorial-zone trainers and player-city trainers (lines 132-142), picks one at random, stores coordinates and zone name in the ghost (lines 149-150).
  - Creates a waypoint with custom name `@jedi_spam:trainer_waypoint_name` at those coordinates (lines 59-67) and sends system message `@jedi_spam:waypoint_created_to_trainer` (line 69).

## 3. What a Bot Test Should Check

### Setup needed first
1. Ensure the test creature is a player creature with a valid `PlayerObject` ghost.
2. Verify the creature has the prerequisite skill(s) and species required by the target skill.
3. Confirm the creature has enough XP of the skill's type (check via `ghost->getExperience(skill->getXpType())`).
4. Confirm the creature has enough free skill points (`ghost->getSkillPoints() >= skill->getSkillPointsRequired()`).
5. For Jedi skills, ensure Jedi state >= skill's required level and any Jedi-tree prerequisites are met.
6. For pilot skills, note that `/surrenderskill` will block with a SUI dialog; test must handle or avoid this path.

### Observable results to verify after learning
- **System messages**: none explicit in these files for success (inferred: client likely shows its own UI message).
- **Skill list**: `creature->hasSkill(skillName)` returns true.
- **XP balance**: `ghost->getExperience(skill->getXpType())` decreased by `skill->getXpCost()`.
- **Skill points**: `ghost->getSkillPoints()` decreased by `skill->getSkillPointsRequired()`.
- **Skill modifiers**: verify via `creature->getSkillMod(SkillModManager::SKILLBOX, modifierKey)` that each key from `skill->getSkillModifiers()` is present with the expected value.
- **Abilities**: `ghost->hasAbility(abilityName)` returns true for each ability in `skill->getAbilities()`.
- **Draft schematics**: check via `SchematicMap` (not directly observable without its API; inferred: schematics should be granted).
- **XP type caps**: `ghost->getXpTypeCapList()` reflects updated caps from `updateXpLimits`.
- **Force Power**: `ghost->getForcePowerMax()` recalculated.
- **Player level**: `creature->getLevel()` updated via `playerManager->calculatePlayerLevel`.
- **Badges**: for master skills, check `BadgeList` or player badge inventory (not directly observable from these files).

### Observable results after surrendering
- `creature->hasSkill(skillName)` returns false.
- Skill modifiers removed (verify via `getSkillMod`).
- Abilities removed only if no other skill grants them.
- Skill points refunded (`ghost->getSkillPoints()` increased by `skill->getSkillPointsRequired()`).
- XP caps updated, Force Power recalculated, level updated.
- For pilot skills: the SUI dialog must be accepted; otherwise the skill is not surrendered.

## 4. Likely Reasons a Test Sees No Effect

1. **Missing prerequisites**: the test creature lacks a required species, prerequisite skill, or Jedi state (inferred from `fulfillsSkillPrerequisites` checks).
2. **Insufficient XP or skill points**: `canLearnSkill` returns false before any deduction occurs (lines 858-867).
3. **Already has the skill**: `awardSkill` returns true without changes if the creature already owns it (line 358).
4. **Pilot-skill SUI block**: `/surrenderskill` for pilot skills returns false and shows a dialog; bot must accept it or test won't see removal (lines 534-571).
5. **Force skill JediManager gate**: `JediManager::canSurrenderSkill` may reject surrender (line 531); the file is not provided.
6. **Required-skill dependency**: another owned skill lists the target as required, blocking surrender (lines 517-523).
7. **Trainer menu not invoked**: these files do not show how a trainer NPC's radial menu selects and calls `awardSkill`; if the bot doesn't trigger the correct menu item, nothing happens.
8. **Admin privilege bypass**: privileged players skip some checks (`ghost->isPrivileged()` returns true at line 944), which may mask expected failures in tests.

## 5. Open Questions

1. **What does the trainer say when prerequisites are missing?** The provided files contain no trainer dialogue or system messages for failure cases. This logic is likely in the trainer NPC's object template, a Lua script, or a different C++ file not included here.
2. **How are credits charged?** None of the five files mention credits or currency deductions during skill learning. Credits may be handled by the trainer menu component (not provided) or not at all in Core3.
3. **Which file handles the trainer radial menu and calls `awardSkill`?** `TrainerMenuComponent.cpp` only handles city-mayor removal; it does not contain training logic. The actual trainer menu selection code is missing.
4. **What is the maximum skill-point cap beyond the default 250?** The default comes from config key `Core3.Sandbox.SkillPoints` (line 428), but there is no visible per-skill or global cap override in these files.
5. **How does `JediManager::canLearnSkill` and `canSurrenderSkill` work?** These are delegated to a separate manager not included here; the exact Jedi-tree rules are opaque.
6. **What happens with the "apprenticeshipEnabled" flag?** It is loaded from `scripts/managers/skill_manager.lua` (line 63) but never used in these files. Its effect is unknown without that Lua file or other C++ code.
