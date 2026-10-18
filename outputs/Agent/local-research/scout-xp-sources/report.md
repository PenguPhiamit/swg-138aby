# Scout XP Sources Report (Core3)

## 1. Short Answer

In Core3, scouts earn **harvesting XP** by harvesting corpses for meat (type 234), hide (type 235), or bone (type 236). The XP formula is `creatureLevel * 5 + 19`, awarded as the "scout" skill type. Each corpse can only be harvested once per player, enforced by `addAlreadyHarvested`. Trapping XP and foraging XP code are **not present** in the provided files: `ThrowTrapTask.h` (which would handle trap throwing logic) and `ForageManager` implementation are missing from the repository. The `DeployTrapCommand.h` file is a stub that does nothing.

## 2. How It Works

### Harvesting Corpses

**Conditions:**
- Target must be a dead creature (`!cr->isDead()` check at line 91 of HarvestCorpseCommand.h)
- Creature's DNA state must not be `DNADEATH` (line 97-99 of HarvestCorpseCommand.h)
- Player must be within 7 meters of the corpse (line 929 of CreatureManagerImplementation.cpp)
- Creature must pass `canHarvestMe(player)` check (line 926 of CreatureManagerImplementation.cpp)

**Resource types:**
- Meat: type 234, from `creature->getMeatType()` and `creature->getMeatMax()` (lines 58-59, 962-964 of HarvestCorpseCommand.h and CreatureManagerImplementation.cpp)
- Hide: type 235, from `creature->getHideType()` and `creature->getHideMax()` (lines 60-61, 965-967)
- Bone: type 236, from `creature->getBoneType()` and `creature->getBoneMax()` (lines 62-63, 968-970)

**Quantity calculation:**
- Base quantity = `creature resource max * (creature_harvesting skill mod / 100.0)` (line 977 of CreatureManagerImplementation.cpp)
- Minimum 3 units extracted (line 978)
- Density modifier applied: fat (>0.75): ×1.25, medium (>0.50): ×1.0, scrawny (>0.25): ×0.75, skinny (≤0.25): ×0.50 (lines 991-1003)
- Group modifier applied if grouped (lines 1008-1012)
- If creature has a parent, quantity forced to 1 (lines 1014-1015)

**XP award:**
- Formula: `creature->getLevel() * 5 + 19` (line 1052 of CreatureManagerImplementation.cpp)
- Awarded via `playerManager->awardExperience(player, "scout", xp, true)` (lines 1054-1055)

**Limitations:**
- Each player can only harvest each corpse once: `creature->addAlreadyHarvested(player)` at line 1057 marks the corpse as harvested for that player.
- If corpse has no loot, no credits, and no group members in range can harvest, despawn is expedited (lines 1061-1069).

**Player messages:**
- System message showing quantity extracted and resource type with creature health quality (lines 1022-1027)
- Group bonus message if modifier > 1.0 (lines 1030-1035)
- Group chat broadcast of harvest (lines 1038-1048)

### Trapping

**From ThrowTrapCommand.h:**
- Requires `trapping` skill mod >= 1 and `outdoors_scout_novice` skill (lines 23-28)
- Target must be an AI agent that is alive, attackable, not a pet, is a creature, and is a monster (lines 62-84)
- Player's trapping skill mod must meet trap's `getSkillRequired()` (line 119)
- Range check against trap's `getMaxRange()` (line 110)
- Creates `ThrowTrapTask` with 2-second delay (line 130)

**Missing:** The actual XP award logic would be in `ThrowTrapTask.h`, which is **not present** in the provided files. Cannot determine trapping XP formula, type, or limits from these files alone.

### Deploy Trap

**From DeployTrapCommand.h:**
- Empty stub: only checks state/locomotion and returns SUCCESS (lines 18-25). No actual deployment logic.

### Foraging

**From ForageCommand.h:**
- Calls `forageManager->startForaging(player, ForageManager::SCOUT)` (line 32)
- **Missing:** The `ForageManager` implementation is not in the provided files. Cannot determine foraging XP mechanics.

## 3. What a Bot Test Should Check

### Harvesting XP Test Setup:
1. Kill a creature and wait for it to become dead (posture DEAD)
2. Verify corpse has resources: check `getMeatType()`, `getHideType()`, or `getBoneType()` are non-empty
3. Position within 7 meters of corpse
4. Call HarvestCorpseCommand with argument "meat", "hide", or "bone" (or empty for random)

### Observable Results:
- System message showing quantity extracted and resource type (e.g., "@skl_use:creature_quality_fat" with DI=quantity, TU=resource class)
- Scout XP awarded: verify via `playerManager->awardExperience` call at line 1055
- Corpse marked as harvested for player: `addAlreadyHarvested(player)` at line 1057 (subsequent harvest attempts should fail with "This creature has no resources" or similar)
- If grouped, group chat message broadcast

### Trapping XP Test Setup (inferred from ThrowTrapCommand.h):
1. Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1
2. Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory
3. Target a living, attackable, non-pet monster AI agent within trap's max range
4. Call ThrowTrapCommand with the trap's object ID as argument

### Observable Results for Trapping:
- System message "@trap/trap:sys_not_ready" if cooldown or pending task exists (line 47)
- System message "@trap/trap:trap_no_skill" if trapping skill < 1 or no outdoors_scout_novice (lines 26, 91)
- System message "@trap/trap:trap_no_skill_this" if trapping skill < trap's required skill (line 120)
- System message "target_range_prose" if out of range (lines 111-114)
- **Missing:** XP award details from ThrowTrapTask.h

## 4. Likely Reasons a Test Sees No Effect

**Harvesting:**
- Corpse already harvested by this player (addAlreadyHarvested check at line 1057)
- Creature not dead yet or DNA state is DNADEATH (lines 91, 97 of HarvestCorpseCommand.h)
- Player out of range (>7 meters, line 929)
- No resources on creature (meatType/hideType/boneType all empty, lines 58-63)

**Trapping:**
- Missing `outdoors_scout_novice` skill or trapping skill mod < 1 (lines 23-28 of ThrowTrapCommand.h)
- Target is a pet, not a creature, or not a monster (lines 78-84)
- Out of range for the specific trap (line 110)
- Trapping skill below trap's required skill (line 119)
- **Most likely:** The ThrowTrapTask.h file is missing from the provided files, so the actual XP award logic is unknown. The bot may be calling the command correctly but the task implementation that awards XP is not in the repository.

**Foraging:**
- ForageManager implementation not present in provided files; cannot determine requirements.

## 5. Open Questions

1. **Trapping XP formula and type:** ThrowTrapTask.h (referenced at line 8 of ThrowTrapCommand.h) is missing. This file would contain the trap throw completion logic and XP awarding. Cannot determine trapping XP amount, skill type, or success/failure conditions.

2. **Foraging XP mechanics:** ForageManager implementation is not in the provided files. ForageCommand.h only calls `startForaging()` but the manager code is absent. Cannot determine foraging XP formula, resource types, or limits.

3. **Deploy trap behavior:** DeployTrapCommand.h is an empty stub (only returns SUCCESS). No deployment logic present. Unclear if deploy traps exist in Core3 or if this is incomplete code.

4. **Harvesting random selection:** When no argument given, HarvestCorpseCommand.h randomly selects from available types (lines 81-82), but the bot may need to specify a type explicitly for reliable testing.

5. **Group harvesting XP:** The code shows group modifiers for quantity (lines 1008-1012) but does not show whether XP is shared or awarded individually per harvester.
