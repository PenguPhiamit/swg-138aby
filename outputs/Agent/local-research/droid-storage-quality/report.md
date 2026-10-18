# Report: Droid Storage Compartment "Mechanism Quality -999999" Bug

## 1. Short Answer

The bug occurs because `DroidComponentImplementation::updateCraftingValues` (line 15) reads the crafting value `"mechanism_quality"` from the template's experimental properties, and when that value is missing or not yet calculated during crafting, it returns a sentinel constant (`AttributesMap::VALUENOTFOUND`, which appears to be -999999). The check on line 62 (`quality > AttributesMap::VALUENOTFOUND`) should prevent inserting this sentinel into the attribute list, but if the comparison fails or the sentinel is not exactly matched, the raw value gets sent to the client. The storage module template (item_storage_module_1.lua line 51) does define `mechanism_quality` at index 4 with a valid range of -10 to 15, so the property exists but may not be computed correctly during the crafting process for this specific module type.

## 2. How It Works

**Conditions and flow:**
- When a player crafts a droid component, `DroidComponentImplementation::updateCraftingValues` is called (line 12).
- Line 15 reads: `quality = values->getCurrentValue("mechanism_quality");` — this pulls the mechanism_quality value from the template's experimental properties.
- If the crafting system has not yet computed or assigned a valid mechanism_quality for this module, `getCurrentValue` returns a sentinel (likely -999999).
- Later, when the object's attributes are sent to the client via `fillAttributeList`, line 62 checks: `if (quality > AttributesMap::VALUENOTFOUND)` before inserting the attribute on line 63.

**Skill mods and numbers:**
- The storage module template (item_storage_module_1.lua) defines mechanism_quality at index 4 with `experimentalMin = -10` and `experimentalMax = 15` (lines 52-53).
- The storage module also has its own rating property (DroidItemStorageModuleDataComponent.cpp line 37: `rating = values->getCurrentValue("storage_module");`) which ranges from 1 to 10 based on the template's experimentalMin/Max at index 5.

**Messages the player sees:**
- If the sentinel value passes through, the client displays "Mechanism Quality -999999" in the object tooltip or crafting preview.
- The storage_module attribute is capped at 10 when displayed (DroidItemStorageModuleDataComponent.cpp line 64).

**Timings:**
- `updateCraftingValues` is called during the crafting process to populate the component's values from the template.
- `fillAttributeList` is called when the client requests object attributes (e.g., tooltip display).

## 3. What a Bot Test Should Check

**Observable results:**
1. System message or crafting preview showing mechanism_quality as a valid positive integer (0 to 15 range based on template lines 52-53), NOT -999999.
2. The droid component's attribute list should include "mechanism_quality" with a value >= 0 (DroidComponentImplementation.cpp line 63).
3. The storage module rating should be between 1 and 10, and the final display-capped value should be <= 10 (DroidItemStorageModuleDataComponent.cpp line 64).

**Setup needed first:**
- Ensure the player has sufficient crafting skill to craft a droid component.
- Have the correct template (object/tangible/component/droid/item_storage_module_1.iff) available in the crafting recipe.
- Verify the experimental properties are properly loaded from the Lua file (item_storage_module_1.lua lines 47-55).

## 4. Likely Reasons a Test Sees No Effect

1. **Template not loaded:** The Lua template file (item_storage_module_1.lua) may not be loaded by the server, so experimental properties are missing at runtime.
2. **Crafting calculation skipped:** The crafting system may skip mechanism_quality calculation for storage modules if certain conditions aren't met (e.g., missing skill mods or materials).
3. **Sentinel comparison bug:** If `AttributesMap::VALUENOTFOUND` is not exactly -999999, the check on line 62 might fail to catch the sentinel value.
4. **Order of operations:** If `updateCraftingValues` is called before the experimental properties are fully initialized, `getCurrentValue` returns the default sentinel.

## 5. Open Questions

1. **What is the exact value of `AttributesMap::VALUENOTFOUND`?** The files show it's used on line 62 but don't define it. Need to find the AttributesMap header or definition.
2. **How does `CraftingValues::getCurrentValue` behave when a property isn't found?** Does it always return the same sentinel, or can it vary?
3. **When exactly is mechanism_quality calculated during crafting?** The template defines min/max (item_storage_module_1.lua lines 52-53), but what code computes the actual value from skill mods and materials?
4. **Why does this affect only the storage module and not other droid components?** Other modules may have different experimental property configurations or calculation paths.
5. **Is there a separate initialization path for storage modules?** The `DroidItemStorageModuleDataComponent` has its own `updateCraftingValues` (line 36-38) and `copy` method (line 83-93), which may interact differently with the parent component's quality calculation.

## Claude's review (18 Oct 6:28 AM)

**Partly right; the bug is not found.**
- Right: `-999999` is the "value not found" sentinel, `AttributesMap::VALUENOTFOUND = -999999` (src/templates/crafting/AtributesMapImplementation.cpp:11), and `updateCraftingValues` reads `mechanism_quality` with `getCurrentValue` (DroidComponentImplementation.cpp:15).
- Contradicted: the finished module's tooltip can't show it. Line 62 inserts the attribute only when `quality > VALUENOTFOUND`, and the storage module's own list adds only `storage_module` (DroidItemStorageModuleDataComponent.cpp:62-65).
- The GitHub report says it appeared "while crafting", so the likely place is the crafting window's experimental values (CraftingValues and the manufacture schematic), which were not in the sources.

**Worth noting:** the template gives `mechanism_quality` a range of -10 to 15 (item_storage_module_1.lua:51-53). Even when it works, a storage module can show a negative mechanism quality.

**Next:** a rerun with `CraftingValues.cpp` and the crafting session's attribute code, or ChatGPT's C64, which covers GitHub issue 11.
