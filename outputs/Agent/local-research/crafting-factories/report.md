# Factory Manufacture Schematic Report (Core3)

## 1. Short Answer

In Core3, a crafter inserts a manufacture schematic from their datapad into an empty factory via a radial menu and SUI list. The server validates the schematic's prototype, calculates a timer from the schematic's complexity (complexity × 8 × FactoryTimeMultiplier), and schedules a background task to produce items at that interval. Each batch run checks power consumption against surplusPower, maintenance status, ingredient availability in the input hopper, and the schematic's manufactureLimit. Items are placed in the factory's output hopper as either crates or individual objects depending on the draftSchematic's factoryCrateSize. The process stops when the limit is reached, power/maintenance runs out, ingredients are missing, or the player manually deactivates the station.

## 2. How It Works

### Inserting a Schematic into an Empty Factory
- **Server sends SUI**: `sendInsertManuSui` (FactoryObjectImplementation.cpp:192) creates a SuiListBox with window type FACTORY_SCHEMATIC2BUTTON and prompt "Choose a schematic to be added to the factory." (line 197). It filters schematics from the player's datapad by matching the factory's craftingTabsSupported (lines 234-246), adding each valid schematic's name and objectID as a menu item (line 255).
- **Player selects and confirms**: The server uses InsertSchematicSuiCallback (line 259) to handle the selection.
- **Server inserts schematic**: `handleInsertFactorySchem` (line 407) first checks the object is a ManufactureSchematic via `isManufactureSchematic()` (line 412). If valid, it transfers the schematic to container slot -1 (line 427) and sends system message "manf_station:schematic_added" with the schematic name (lines 428-435), plus a second message showing the limit: `"This schematic limit is: " + String::valueOf(schematic->getManufactureLimit())` (line 437). If transfer fails, it sends "manf_station:schematic_not_added" (lines 441-448).

### Starting the Factory
- **Player uses radial menu on factory**: Server calls `handleOperateToggle` (line 509).
- **Checks for schematic**: If no schematic in slot 0, sends "No schematic, unable to start" (lines 510-520).
- **If not active**: Sets currentUserName to player's firstName and currentRunCount = 0 (lines 523-524), calls `startFactory()` (line 526), sends "@manf_station:activated" system message (line 527), and repeats the limit message (line 528).
- **If already active**: Calls `stopFactory("manf_done", ...)` (line 531) and sends "@manf_station:deactivated" (line 532).

### startFactory() Validation and Timer Setup
`startFactory()` (line 537) performs these checks in order:
1. **Schematic exists**: `getContainerObjectsSize() == 0` returns false (lines 538-540).
2. **Schematic is ManufactureSchematic**: Casts to ManufactureSchematic, returns false if nullptr (lines 546-549).
3. **Prototype exists**: Gets prototype via `schematic->getPrototype()`, returns false if nullptr (lines 551-554).
4. **Prototype not sliced or has anti-decay kit**: Returns false if `prototype->isSliced()` or `prototype->hasAntiDecayKit()` (line 556).
5. **Weapon without powerup**: If prototype is a WeaponObject with a powerup, returns false (lines 559-564).
6. **Timer calculation**: `timer = Math::max(1, (int)(((int)schematic->getComplexity()) * 8 * ConfigManager::instance()->getFloat("Core3.Sandbox.FactoryTimeMultiplier", 1.f)))` (line 570). The default multiplier is 1.0, so base timer = complexity × 8 seconds.
7. **Populate blueprint**: Calls `populateSchematicBlueprint(schematic)` (line 573), which sets the input hopper on each BlueprintEntry and calls `collectMatchesInInputHopper` to find matching items in the ingredient_hopper (lines 593-598).
8. **Schedule task**: Creates CreateFactoryObjectTask and schedules it with delay `timer * 1000` milliseconds (lines 577-578).
9. **Set active**: Calls `setActive(true, true)` (line 580).

### Batch Production Loop (createNewObject)
The scheduled task calls `createNewObject()` (line 656), which runs each interval:
1. **Schematic still exists**: Checks `getContainerObjectsSize() == 0`, stops with "manf_error" if missing (lines 663-666).
2. **Schematic is ManufactureSchematic**: Stops with "manf_error_4" if not (lines 670-672).
3. **Prototype exists**: Stops with "manf_error_2" if nullptr (lines 675-680).
4. **Power and maintenance check**: Calls `updateMaintenance(timeToWorkTill)` (line 684). If shutdownAfterWork is true, calculates energy consumption: `energyAmount = (elapsedTime / 3600.0) * getBasePowerRate()` (line 691). If energyAmount > surplusPower, stops with "manf_no_power" (lines 692-694). Otherwise stops with "manf_done_sub" (line 697).
5. **Ingredient check**: Calls `schematic->canManufactureItem(type, displayedName)` (line 706). If displayedName is non-empty, stops with that type and name via `stopFactory(type, displayedName)` (lines 708-710). The implementation of canManufactureItem is not in these files.
6. **Crate size check**: Gets crateSize from `schematic->getFactoryCrateSize()` (line 713), which returns draftSchematic's factoryCrateSize (ManufactureSchematicImplementation.cpp:594-599). If <= 0, stops with "manf_error" (lines 715-718).
7. **Create output**:
   - If crateSize > 1: Locates existing crate in output_hopper matching prototype and useCount < maxCapacity via `locateCrateInOutputHopper` (line 723), or creates new crate via `createNewFactoryCrate` (line 726). Checks if output_hopper is full (line 800), stops with "manf_output_hopper_full" if so. Creates FactoryCrateObjectDeltaMessage3 and broadcasts to operators (lines 736-740).
   - If crateSize == 1: Clones prototype via ObjectManager::cloneObject and transfers to output_hopper (lines 830-839). Checks if hopper is full (line 825), stops with "manf_output_hopper_full" if so.
8. **Increment counter**: `currentRunCount++` (line 751).
9. **Check limit**: If `schematic->getManufactureLimit() < 1`, destroys schematic from world and database (lines 754-755) and stops with "manf_done" (line 756).
10. **Reschedule or stop**: Reschedules the task with `timer * 1000` ms delay (line 763), or stops with "manf_error" if pending task is null (line 765).

### Collecting Output
- **Open output hopper**: Server sends output_hopper contents via `sendOutputHopper` (line 308), which opens the container and sends each FactoryCrate or item to the player.
- **Factory attributes for admin view**: `fillAttributeList` shows manufacture_object, manufacture_time, manf_limit, and manufacture_count when factory is active and player is on admin list (lines 135-162).

### Stopping Conditions Summary
| Condition | Message/Result | Source |
|-----------|---------------|--------|
| No schematic in factory | "No schematic, unable to start" | FactoryObjectImplementation.cpp:511 |
| Prototype sliced | Returns false (no message) | FactoryObjectImplementation.cpp:556 |
| Prototype has anti-decay kit | Returns false (no message) | FactoryObjectImplementation.cpp:556 |
| Weapon with powerup | Returns false (no message) | FactoryObjectImplementation.cpp:562 |
| No power | "manf_no_power" email + stop | FactoryObjectImplementation.cpp:693 |
| Ingredients missing | "manf_no_unknown_resource"/"manf_no_named_resource"/"manf_no_component" email + stop | FactoryObjectImplementation.cpp:647-653, 708-710 |
| Output hopper full | "manf_output_hopper_full" email + stop | FactoryObjectImplementation.cpp:801, 826 |
| Limit reached (limit < 1) | Schematic destroyed, "manf_done" email with count | FactoryObjectImplementation.cpp:753-757 |
| Manual deactivation | "@manf_station:deactivated" message + "manf_done" email | FactoryObjectImplementation.cpp:531-532 |

## 3. What a Bot Test Should Check

### Required Setup
1. **Factory object**: Must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template).
2. **ManufactureSchematic**: Player must have a valid manufacture schematic in their datapad with:
   - A non-null prototype
   - Prototype not sliced, no anti-decay kit
   - If weapon, no powerup equipped
   - draftSchematic with factoryCrateSize > 0
   - Appropriate craftingTab matching the factory's supported tabs
3. **Ingredients**: Required ingredients must be placed in the factory's ingredient_hopper (slotted object "ingredient_hopper").

### Observable Results to Check
1. **After schematic insertion**:
   - System message containing "@manf_station:schematic_added" with schematic name
   - Second system message: `"This schematic limit is: <N>"` where N = schematic->getManufactureLimit()
   - Factory container now has 1 object in slot 0 (the schematic)

2. **After toggle to start**:
   - System message "@manf_station:activated"
   - Second system message with limit again
   - Factory isActive() returns true
   - Pending task "createFactoryObject" exists with timer * 1000ms delay

3. **During production** (after each timer interval):
   - Objects appear in output_hopper (check getContainerObjectsSize() > 0)
   - If crateSize > 1: FactoryCrate objects with correct prototype and incrementing useCount
   - If crateSize == 1: Individual cloned items matching prototype
   - currentRunCount increments each batch

4. **When limit reached**:
   - Schematic destroyed from world and database (no longer in factory slot 0)
   - System message "@manf_done" with run count
   - Factory isActive() returns false

5. **Power failure test**:
   - Set surplusPower to low value, let factory run until energyAmount > surplusPower
   - Email received with "manf_no_power" body
   - Factory stops, isActive() = false

6. **Output hopper full test**:
   - Fill output_hopper to capacity before starting or during production
   - Email received with "manf_output_hopper_full" body
   - Factory stops

### Log/Bot Confirmation Lines
- FactoryObjectImplementation.cpp:428-435 for schematic_added message
- FactoryObjectImplementation.cpp:527 for activated message
- FactoryObjectImplementation.cpp:693 for manf_no_power
- FactoryObjectImplementation.cpp:801, 826 for manf_output_hopper_full
- FactoryObjectImplementation.cpp:756 for manf_done with count

## 4. Likely Reasons a Test Sees No Effect

1. **No schematic in datapad matching factory tabs**: `sendInsertManuSui` filters by craftingTab (lines 234-246). If no schematics match, the SUI list is empty and player cannot select one.
2. **Prototype is sliced or has anti-decay kit**: `startFactory()` returns false silently at line 556 without sending a message to the player.
3. **Weapon prototype with powerup**: Returns false silently at line 562-564.
4. **Ingredients not in input hopper**: `canManufactureItem` (line 706) checks ingredients but its implementation is not in these files. If ingredients are missing, factory stops with email notification but no immediate system message to player during operation.
5. **Output hopper full**: Factory stops silently except for email; items never appear in output.
6. **Schematic limit already reached (limit < 1)**: Schematic is destroyed immediately on first run without producing items.
7. **Factory not active**: If `isActive()` returns false and player tries to operate, nothing happens until toggle is used.
8. **Timer too short for test observation**: With complexity × 8 seconds as base timer, low-complexity schematics may produce items very quickly, making it hard to observe intermediate states.

## 5. Open Questions

1. **canManufactureItem implementation**: Called at FactoryObjectImplementation.cpp:706 but not defined in either source file. This function determines ingredient availability and returns the type/displayedName of missing ingredients. Without this code, we cannot verify exact ingredient checking logic or which BlueprintEntry fields are validated.
2. **updateMaintenance implementation**: Called at FactoryObjectImplementation.cpp:684 to check power and maintenance status. The function is not in these files, so we don't know the exact maintenance decay rate, how surplusPower is calculated, or what triggers shutdownAfterWork.
3. **Radial menu IDs**: The source files show server-side handling but do not specify which radial menu ID or command name the client sends to trigger `handleOperateToggle` or `sendInsertManuSui`.
4. **InsertSchematicSuiCallback details**: Included at line 11 but implementation not in these files. We don't know the exact SUI button handling logic or what happens if player cancels.
5. **FactoryCrate object structure**: The code creates FactoryCrate objects (line 805) and broadcasts delta messages (line 736), but we don't know the crate's internal capacity, useCount behavior across sessions, or how clients interact with crates versus individual items.
6. **Power rate configuration**: `getBasePowerRate()` is called at line 691 but its source is not in these files. We don't know if it comes from template data or is hardcoded.
7. **Manual ingredient addition**: The code shows `populateSchematicBlueprint` collects matches from input_hopper (line 596), but there's no visible mechanism for players to manually add ingredients to the hopper during operation—only before starting.
