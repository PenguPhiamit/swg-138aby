# Research topic: Where scout experience comes from

## 1. Short answer

In Core3, scouts earn experience through three methods:

- **Harvesting corpses**: Using `HarvestCorpseCommand`, scouts gain XP_TYPE_HARVEST (lines 58-63) by harvesting meat/hide/bone from dead creatures. XP is calculated via `CreatureManager::harvest` (line 103), with a per-corpse limit (line 200).
- **Traps**: `ThrowTrapCommand` (lines 25-30) requires a trapping skill ≥1 and valid targets (line 75). Deploying traps via `DeployTrapCommand` (empty) grants XP_TYPE_TRAP, but no XP amount or conditions are defined in the provided files.
- **Foraging**: `ForageCommand` (line 25) grants XP_TYPE_FORAGE, but no specific mechanics or limits are detailed.

Bots must throw traps first (line 50) then deploy them (line 130) to earn trapping XP, but the exact XP calculation is missing.

## 2. How it works

### Harvesting corpses
- **Conditions**: Must target dead creatures (line 91), have valid resources (lines 70-82), and meet skill requirements (line 25).
- **Skill mods**: `trapping` skill ≥1 (line 25) affects trap use.
- **XP**: Calculated via `CreatureManager::harvest` (line 103), with a per-corpse limit (line 200).
- **Messages**: "This creature has no resources" (line 85), "@skl_use:nothing_to_harvest" (line 99).

### Traps
- **Conditions**: Must throw a trap (line 50) and target valid creatures (line 75). Skill ≥ trap's required level (line 119).
- **XP**: XP_TYPE_TRAP is assigned (line 90), but no amount or calculation is defined in the provided files.
- **Messages**: "@trap/trap:trap_no_skill" (line 26), "@trap/trap:sys_not_ready" (line 47).

### Foraging
- **Conditions**: Requires the `ForageCommand` (line 25) and valid setup.
- **XP**: XP_TYPE_FORAGE is granted, but no specific mechanics or limits are detailed.

## 3. What a bot test should check

- **Harvesting**: Verify system messages (lines 66, 85), inventory changes, and XP gain via `CreatureManager::harvest` (line 103).
- **Traps**: Ensure traps are thrown (line 50) and deployed (line 130), check for valid targets (line 75), and confirm XP_TYPE_TRAP is awarded.
- **Foraging**: Confirm XP_TYPE_FORAGE is granted and no errors (line 25).

## 4. Likely reasons a test sees no effect

- Missing prerequisites: No trapping skill (line 25), invalid targets (line 75), or expired cooldowns (line 46).
- Missing trap deployment logic: `DeployTrapCommand` is empty (line 25), so XP calculation is undefined.
- Invalid resource types: No meat/hide/bone on the corpse (lines 70-82).

## 5. Open questions

- **Missing trap XP calculation**: `DeployTrapCommand` (line 25) lacks XP logic, and no file defines XP_TYPE_TRAP amounts.
- **Foraging limits**: No details on XP caps or resource availability.
- **Trapping skill mods**: How do skill mods affect trap success rates (line 119)?

(inferred)
