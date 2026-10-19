# Report: Food, Drink and Spice Mechanics

## 1. Short Answer

Food and drink each have separate stomach capacities tracked on the player's ghost (food filling and drink filling). Eating or drinking adds a `filling` value from the item template to the appropriate pool; if the amount would exceed the max, the action is blocked with a "too full" message. Buffs are applied based on the item's `effectType`: attribute buffs, skill buffs, spice buffs, healing, duration buffs, delayed buffs, or instant effects. Attribute and skill buffs replace any existing buff with the same CRC unless the item is foraged food. Spice items trigger a 120-second downer debuff when they expire, which reduces attributes and triggers periodic vomiting animations.

## 2. How It Works

### Conditions to Eat/Drink
- The player must not be dead or incapacitated (ConsumableImplementation.cpp:154).
- Species restrictions are checked first: pet-only food sends `@error_message:pets_only` (line 133); race-restricted items send `@error_message:race_restriction` for non-matching species (lines 139-142).
- Spice items check if the player is already spiced; if so, they send `@spice/spice:sys_already_spiced` ("You are already under the influence of spices.") and abort (lines 144-147).
- For non-spice consumables, if the player already has a buff with the same CRC as the item's `buffCRC`, the action is blocked unless it is an attribute effect AND foraged food; the message sent is `@combat_effects:already_affected` ("You are already under the influence of that food. Eating more won't enhance the effect.") (lines 149-152).
- Filling check: for food, available space is `ghost->getFoodFillingMax() - ghost->getFoodFilling()` (line 165); for drink, `ghost->getDrinkFillingMax() - ghost->getDrinkFilling()` (line 168). If the item's `filling` exceeds available space, the action is blocked with `@error_message:full_food` or `@error_message:full_drink` ("You are too full to eat/drink that.") (lines 170-178).

### Skill Mods and Numbers
- The `filling` value loaded from the template determines how much stomach capacity is consumed (ConsumableImplementation.cpp:33). Crafting can modify filling via `add_filling` experimental attribute (lines 77-79).
- Duration comes from the template (`duration = consumableTemplate->getDuration()`, line 32). Twi'leks receive a 10% duration bonus when `newDuration > 0` (lines 183-185).
- Modifiers are applied via `setModifiers(buff, skillModifiers)` (line 395). For attribute effects, the value used is `newNutrition` unless the item is spice or foraged food (lines 402-404). Skill modifiers use the raw template values.
- The `fillAttributeList` method shows examine info: stomach filling as `stomach_food` or `stomach_drink` (lines 453-457, 473-478), duration in minutes/seconds format (lines 486-493), and per-modifier nutrition strings (lines 504-512).

### Timings
- Buff duration is set from the template at load time (ConsumableImplementation.cpp:32) and can be modified by crafting's `flavor` attribute (line 108) and `add_flavor` (line 111).
- Spice buffs, when deactivated, immediately create a `SpiceDownerBuff` with a hardcoded 120-second duration (SpiceBuffImplementation.cpp:20). The downer applies negative attribute modifiers derived from the spice's `attributeModifiers` (lines 34-53), capping at the creature's remaining HAM capacity.
- Spice downers trigger a `heavy_cough_vomit` animation immediately and then every 15 seconds via `SpiceDownerAnimationTask` (SpiceBuffImplementation.cpp:28-30).
- The SpiceDownerBuff duration can be reduced by the `reduce_spice_downtime` skill modifier if the player has a buff with CRC `BuffCRC.FOOD_REDUCE_SPICE_DOWNTIME` (SpiceDownerBuff.idl:26-36).

### Messages the Player Sees
- **Too full:** `@error_message:full_food` or `@error_message:full_drink` ("You are too full to eat/drink that.") — ConsumableImplementation.cpp:172, 175.
- **Already buffed (non-foraged):** `@combat_effects:already_affected` ("You are already under the influence of that food. Eating more won't enhance the effect.") — line 150.
- **Already spiced:** `@spice/spice:sys_already_spiced` ("You are already under the influence of spices.") — line 145.
- **Skill mod applied:** `@combat_effects:skill_mod_buffed` with the stat name for each modifier — lines 206-212.
- **Healing:** "You heal yourself for X health/action/mind." — lines 250-275.
- **DOT reduction:** `@combat_effects:slow_dot_done` ("The remaining duration of DOTs affecting you have been reduced by X%.") — line 332.
- **Consumption confirmation:** `base_player:prose_consume_item` ("You consume %TT.") — lines 357-359.
- **Spice consume:** `@spice/spice:<buffName>_consume` sent in SpiceBuff.activate() (SpiceBuff.idl:24).
- **Spice downer activate:** `@spice/spice:<buffName>_downer` (SpiceDownerBuff.idl:24).
- **Spice downer done:** `@spice/spice:<buffName>_done` (SpiceDownerBuff.idl:44).

## 3. What a Bot Test Should Check

### Setup Needed First
1. Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max).
2. Verify no conflicting buff exists on the target CRC unless testing foraged food override.
3. For spice tests, ensure `hasSpice()` returns false before consumption.
4. Have a consumable item in inventory with known template values (filling, duration, effectType, modifiers).

### Observable Results to Check After Eating/Drinking
- **System messages:** Confirm the correct message was sent (consumption confirmation, skill mod messages, healing amounts, or error messages if blocked).
- **Buffs present:** Call `hasBuff(buffCRC)` and iterate buffs to verify the new buff exists with correct type (`BuffType::FOOD` for attribute/skill, `BuffType::SPICE` for spice), correct duration (accounting for Twi'lek bonus if applicable), and correct modifiers.
- **Filling values:** Check `ghost->getFoodFilling()` or `ghost->getDrinkFilling()` increased by the item's `filling` value.
- **Attributes/skills:** Verify attribute modifiers (HAM pools) and skill mods were applied via the buff.
- **For spice items only:** After the spice buff expires, verify a `SpiceDownerBuff` was added with 120-second duration (reduced by any `reduce_spice_downtime` modifier), negative attribute modifiers matching the spice's `attributeModifiers`, and that the periodic vomiting animation task is scheduled.
- **For healing items:** Verify HAM pools increased by the expected amounts and the healing message was sent.
- **Inventory:** Confirm the item's use count decreased (or the item was destroyed if it reached zero).

## 4. Likely Reasons a Test Sees No Effect

1. **Player already has the buff** on that CRC — the code returns early at ConsumableImplementation.cpp:149-152 unless the item is foraged food and an attribute effect.
2. **Stomach full** — filling exceeds available capacity; blocked at lines 170-178 with a "too full" message.
3. **Already spiced** — `hasSpice()` returns true; blocked at line 144-147.
4. **Dead or incapacitated** — early return at line 154.
5. **Species/race restriction** — pet food or race-restricted items send error messages and abort (lines 132-142).
6. **Item has zero use count** — `decreaseUseCount()` is called after effects; if already zero, the item may be destroyed before use or have no effect.
7. **Healing item with no damage** — sends "You have no damage to heal" and returns at lines 243-246.

## 5. Open Questions

1. **How does stomach filling empty over time?** None of the provided files describe a timer, periodic decay, or skill-based reduction of food/drink filling. This logic likely resides in `PlayerObject` or `CreatureObject` (not included).
2. **What are the default max filling values for food and drink?** The source reads `getFoodFillingMax()` and `getDrinkFillingMax()` but does not define their defaults; these would be in `PlayerObject` or template data.
3. **What specific attribute/skill modifiers do individual foods/drinks provide?** The source shows the mechanism (`modifiers` VectorMap) but the actual values depend on per-item template data (Lua files), which are not included.
4. **How does the `EATCOMMAND.h` relate to consumption?** It only contains a stub `doQueueCommand` that checks state and locomotion masks; the actual consumption logic is in `ConsumableImplementation::handleObjectMenuSelect`. The command likely delegates to the item's radial menu handler, but the bridge is not shown.
5. **What triggers stomach filling reduction via skills or items?** The code references a `food_reduce` instant effect (Tilla Tilla) at line 324-328, but general skill-based or passive reduction mechanics are not present in these files.

## ChatGPT's review (2026-10-18 22:30)

Checked Saluki lead, matching snapshots and Core3-dev 9d08e265. Source only.

**Holds:** separate stomach space, species/dead/incap gates, consumption messages, item charge reduction and 120-second base spice downer with HAM floor protection and 15-second animation scheduling (ConsumableImplementation.cpp:132-178,350-390; SpiceBuffImplementation.cpp:13-51).

**Corrections:**
- Duplicate gate is hasBuff(buffCRC) && (!isAttributeEffect() || isForagedFood()) (ConsumableImplementation.cpp:149). Thus an existing **ordinary attribute** food can be reapplied; existing foraged attribute food is blocked. The report reverses this exception. Saluki flags the right issue but its paraphrase loses the !, so use the actual expression.
- setModifiers replaces the modifier value with newNutrition for **both attribute and skill effects** whenever !isSpice() && !isForagedFood() (395-410), not only attributes. Raw template skill values are not generally what is applied.
- Twi'lek's newDuration bonus is used for ordinary attribute/skill buffs (180-203), but the spice constructor uses duration directly (216-225); do not apply the 10% claim universally. Spice returns through its own branch before generic stomach/consume processing.
- The downer is created only when deactivate(removeModifiers) receives true (SpiceBuffImplementation.cpp:13-31). Downtime reduction uses the named food buff's skill value and only applies when 1-mod/100 > 0 (SpiceDownerBuff.idl:26-34); >=100% does not yield a zero-duration downer here.
- Zero charges causing an early failure is not demonstrated by a decreaseUseCount call after the effect; trace the caller/item lifecycle before using that diagnosis. EatCommand's empty handler does not establish automatic delegation to the radial implementation.

Verdict: Consumption skeleton holds; fix reversed duplicate-food rule, nutrition scaling and spice duration/control-flow assumptions; gameplay untested.
