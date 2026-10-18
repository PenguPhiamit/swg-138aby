# Harvesting Report: Meat, Hide, and Bone from Creatures

## 1. Short Answer

Harvesting a dead creature requires the player to be within 7 meters of the corpse and call the `harvestcorpse` command with a resource type (meat, hide, or bone). The base quantity comes from the creature's max meat/hide/bone values, modified by the player's `creature_harvesting` skill mod and the corpse's density (health condition), then multiplied by any group bonus. Each corpse can be harvested once per player via `addAlreadyHarvested`, after which it despawns after 1 second if it has no loot or credits. Novice players near starting cities should target low-level creatures (level ≤ 5) such as rockmites, womprats, kreetles, or rills, since higher-level or unknown-level prey is blocked from harvest testing.

## 2. How It Works

### Conditions
- **Range**: The player must be within 7 meters of the corpse (`isInRange(creature, 7)`) [929].
- **Permission**: `creature->canHarvestMe(player)` must return true [926].
- **Corpse state**: The creature must be dead; the bot checks `posture == 'dead'` [besh-harvest.py:71].

### Skill Modifiers and Numbers
- **Base quantity**: Taken from the creature's max values (`getMeatMax()`, `getHideMax()`, `getBoneMax()`) [943, 950, 957, 964, 967, 970].
- **Skill mod**: `creature_harvesting` skill mod is applied as a percentage multiplier: `quantity * (skillMod / 100.0f)` [977].
- **Minimum**: The result is clamped to a minimum of 3 [978].
- **Density/health bonus**: Based on corpse density at the player's position:
  - > 0.75: quantity × 1.25 (fat) [991-993]
  - > 0.50: quantity × 1.00 (medium) [994-996]
  - > 0.25: quantity × 0.75 (scrawny) [997-999]
  - ≤ 0.25: quantity × 0.50 (skinny) [1000-1002]
- **Group modifier**: If the player is grouped, `getGroupHarvestModifier(player)` multiplies the quantity further [1008-1012].
- **Tamed creatures**: If the creature has a parent (is tamed), quantityExtracted is forced to 1 [1014-1015].

### Timings
- **Despawn**: After harvesting, if the corpse has no loot, no bank credits, no cash credits, and no group member can harvest it, a despawn task is rescheduled for 1 second (1000 ms) [912-916, 1062-1068].
- **One-time per player**: `addAlreadyHarvested(player)` marks the corpse so the same player cannot harvest it again [907, 1057].

### Messages the Player Sees
- **Success**: A system message using `skl_use` string table with the creature health state (creature_quality_fat/medium/scrawny/skinny), quantity extracted, and resource type [1022-1027].
- **Group bonus**: If group modifier > 1.0, a bonus message is sent:
  - 1.2: `@skl_use:group_harvest_bonus` [1030-1031]
  - 1.3: `@skl_use:group_harvest_bonus_ranger` [1032-1033]
  - 1.4: `@skl_use:group_harvest_bonus_masterranger` [1034-1035]
- **Group chat**: Group members receive a broadcast message showing who harvested what and how much [1038-1048].
- **Errors**: If the creature has no resource of the requested type, the player sees "Tried to harvest something this creature didn't have, please report this error" [974]. If the resource manager cannot find a spawn for that resource type, the player sees "Error: Server cannot locate a current spawn of <resource>" [983].

### Resource Selection
- **Random (selectedID 112)**: Randomly picks hide, meat, or bone with equal probability [937-960].
- **Specific (selectedID 234/235/236)**: Directly requests meat (234), hide (235), or bone (236) [962-971].

## 3. What a Bot Test Should Check

### Setup
1. **Location**: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020) [besh-harvest.py:8].
2. **Target creatures**: Low-level (≤ 5) ordinary wild prey such as rockmite, womprat, kreetle, or rill [besh-harvest.py:9, 61-63].
3. **Fresh kill**: Ensure the creature is freshly killed with `posture == 'dead'` and has not been harvested before [besh-harvest.py:71].
4. **Player state**: Guard character should have ≥ 80% HAM (health, action, mind) before attempting harvest [besh-harvest.py:56-59].

### Observable Results to Verify
- **System message**: A success message containing the quantity extracted and resource type (e.g., "You extract 12 units of meat from the rockmite").
- **Inventory**: A new resource container appears in inventory with a name matching the harvested type (meat, hide, or bone) [besh-harvest.py:17-19].
- **Corpse state**: The corpse despawns after ~1 second if it has no loot/credits and no group members can harvest it.
- **XP award**: Scout XP equal to `creature level × 5 + 19` is awarded [1052-1055].
- **Group messages**: If grouped, bonus messages and group chat notifications appear with the correct modifiers [1030-1048].

### What NOT to Expect
- Multiple harvests of different types from the same corpse by the same player (one-time per player) [907, 1057].
- All three resource types from one kill unless using random selection multiple times with different players.
- Existing-stack quantity visibility (BLOCKED in current body) [besh-harvest.py:5, 106-108].

## 4. Likely Reasons a Test Sees No Effect

- **Prey level unknown or above 5**: The bot blocks testing on creatures with unknown or high levels to avoid dangerous encounters [besh-harvest.py:61-63].
- **No 'ordinary wild prey' near Mos Eisley**: The harvest bot found no suitable low-level creatures in that area, possibly due to spawn tables or zone restrictions.
- **Prey already injured**: If the creature was damaged before the kill, harvest rights may not be established [besh-harvest.py:51-53].
- **Guard below 80% HAM**: The bot stops the hunt if health, action, or mind is below 80% [besh-harvest.py:56-59].
- **Resource spawn not found**: If `ResourceManager::getCurrentSpawn()` returns nullptr for the requested resource type, harvesting fails silently with an error message [982-984].
- **Corpse already harvested by this player**: `addAlreadyHarvested()` prevents re-harvesting [907, 1057].
- **Tamed creature**: If the corpse has a parent (is tamed), quantity is forced to 1, which may appear as no effect if the player expects more [1014-1015].

## 5. Open Questions

- **`canHarvestMe()` logic**: The source file does not show what `Creature::canHarvestMe()` checks (e.g., killer rights, group membership, faction restrictions). This function is called at line 926 but its implementation is not in the provided files.
- **`getHideType()`, `getMeatType()`, `getBoneType()`**: The specific resource type strings returned by these functions are not defined in the source excerpt.
- **`getGroupHarvestModifier()` values**: The exact modifier values (1.2, 1.3, 1.4) are shown in the code, but the conditions for each tier (e.g., skill ranks, group size) are not explained.
- **Density calculation**: How `ResourceSpawn::getDensityAt()` computes density from corpse health is not visible in this file.
- **`addAlreadyHarvested()` implementation**: The mechanism that tracks which players have harvested a corpse is not shown; it may use a set or flag on the Creature object.
- **String table files**: The `skl_use` and `group` string tables referenced in system messages are not included in the provided files, so exact message text cannot be confirmed.
