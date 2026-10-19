# Forage Mechanic Report

## 1. Short Answer

The `/forage` command (SCOUT type) requires the player to be on foot, outside any structure, and have enough ACTION HAM. It costs a base of 50 ACTION adjusted by Quickness skill. After starting, an 8.5-second task runs `finishForaging`, which checks that the player hasn't moved more than 2 meters, isn't in combat, and is in a non-exhausted forage area. The success chance is `15 + (foraging skillMod * 0.8)`, capped at 100, compared against `System::random(80)`. On success, the player receives items from loot tables: ~80% food, ~20% bait (rare items are unreachable). Areas are 10x10 meter boxes that allow 3 uses before exhausting and expire after 30 minutes.

## 2. How It Works

### Conditions to Start
- Player must not be riding a mount: `ForageManagerImplementation.cpp` lines 38-41.
- Player must not be inside a structure (getParentID != 0): lines 44-50.
- For SHELLFISH only: player must be in water and not swimming: lines 53-62.

### Skill Mods and Numbers
- **SCOUT/LAIR**: skill mod "foraging" is used; chance = `15 + (skillMod * 0.8)`: lines 171-175.
- **MEDICAL**: skill mod "medical_foraging"; chance = `15 + (skillMod * 0.6)`: lines 176-179.
- **SHELLFISH**: defaults to skillMod 20, same formula as MEDICAL: lines 180-183.
- Chance is capped at 100 if it exceeds that value: lines 186-188.

### Action/Mind Costs
- **SCOUT/LAIR**: base 50 ACTION cost, adjusted by Quickness (CreatureAttribute::QUICKNESS): lines 22, 81-84.
- **SHELLFISH**: base 100 ACTION and 100 MIND costs, both adjusted by Quickness and Focus respectively: lines 23-24, 68-76.

### Cooldown / Timing
- The foraging task is queued with an 8500ms (8.5 second) delay: line 105.
- A pending "foraging" task prevents re-entry; appropriate busy message is sent: lines 27-35.

### Movement and Combat Checks (at finish)
- Player must not have moved more than 2 meters in X or Y from the start position, and must remain on the same zone: line 133.
- Player must not be in combat: lines 139-142.

### Forage Areas and Exhaustion
- Each `ForageArea` is a 10x10 meter box (SIZE = 10): `ForageArea.h` line 17.
- Each area expires after 30 minutes (EXPIRE = 30): line 18.
- Each area allows exactly 3 uses before becoming exhausted (uses < 3 check): line 59.
- The server tracks one `ForageAreaCollection` per player name, storing up to 120 areas: `ForageAreaCollection.h` lines 74-75.
- When a player forages in an existing valid area, its uses counter increments: line 71.

### Loot Tables (on success)

**SCOUT** (`forageGiveItems`, lines 277-292):
- `System::random(200)` dice:
  - 0-159 (80%): lootGroup "forage_food"
  - 160-199 (20%): lootGroup "forage_bait"
  - >= 200: unreachable with random(200); "forage_rare" is never awarded.

**MEDICAL** (lines 294-322):
- `System::random(200)` dice:
  - 0-39 (20%): lootGroup "forage_food"
  - 40-109 (35%): random flora resource via `forageGiveResource`
  - 110-169 (30%): lootGroup "forage_medical_component", level 1
  - 170-199 (30%): lootGroup "forage_medical_component", level 60 or 200 (exceptional)

**SHELLFISH** (lines 252-274):
- `System::random(100)` > 50: seafood_mollusk; else seafood_crustacean (50/50).

**LAIR** (lines 324-352):
- `System::random(109)` dice:
  - 0-39 (36.7%): lootGroup "forage_live_creatures"
  - 40-108 (63.3%): meat_egg resource

### Messages the Player Sees
- Start: "You begin to search the area for goods." (SCOUT) or "You begin to search the lair for creatures" (LAIR): lines 107-112.
- Already foraging: "@skl_use:sys_forage_already" or "@harvesting:busy": lines 31-33.
- Mounted: "@error_message:survey_on_mount": line 39.
- Inside structure: "@skl_use:sys_forage_inside" or "@harvesting:inside": lines 46-48.
- Not in water (shellfish): "@harvesting:in_water": line 60.
- Moved during forage: "@skl_use:sys_forage_movefail": line 134.
- In combat: "@skl_use:sys_forage_combatfail": line 140.
- Area exhausted: "There is nothing in this area to forage." or "There is nothing of interest remaining in the lair.": lines 152-156.
- Failed to find anything: "@skl_use:sys_forage_fail" or type-specific variants: lines 191-196.
- Success: "@skl_use:sys_forage_success": lines 303, 355.
- Inventory full: "@skl_use:sys_forage_noroom": lines 224, 241.

## 3. What a Bot Test Should Check

### Setup
1. Ensure the player character has the "foraging" skill (or appropriate skill mod).
2. Position the player on foot, outside any structure, in an area that hasn't been exhausted (first forage or within 3 uses).
3. Confirm the player is not mounted and not in combat.
4. Verify sufficient ACTION HAM (at least actionCost + 1).

### Observable Results to Check
- **System messages**: Verify the correct start message, then after 8.5 seconds check for either a success or failure message per the loot table outcomes.
- **Inventory**: On success, confirm items from the expected loot group (e.g., "forage_food" or "forage_bait" for SCOUT) appear in the player's inventory. Check item count matches expectations (up to 3 uses per area).
- **Area exhaustion**: After 3 forages in the same 10x10 area, verify the "nothing to forage" message appears on the 4th attempt.
- **Movement failure**: Move more than 2 meters during the 8.5-second delay and confirm the move-fail message.
- **Combat interruption**: Enter combat during the delay and confirm the combat-distracts message.
- **Cooldown enforcement**: Attempt to forage again before the pending task completes; verify the busy message.

### Additional Checks
- For MEDICAL forage: verify medical components of varying levels appear based on dice rolls.
- For SHELLFISH: verify player is in water and receives seafood_mollusk or seafood_crustacean.
- For LAIR search: verify live creatures or meat_egg items are awarded.

## 4. Likely Reasons a Test Sees No Effect

1. **Area exhaustion**: The player has already foraged 3 times in the same 10x10 area; it is exhausted until it expires after 30 minutes (`ForageArea.h` line 59).
2. **Moved during delay**: The player moved more than 2 meters from the start position during the 8.5-second task (`ForageManagerImplementation.cpp` line 133).
3. **Entered combat**: Combat state was set during the foraging delay (line 139).
4. **Inventory full**: The inventory container is at capacity, causing items to be discarded with a warning message (lines 223-226).
5. **Insufficient HAM**: Player's ACTION or MIND HAM is too low to afford the cost (lines 71-89).
6. **Wrong location for shellfish**: For SHELLFISH type, player must be in water and not swimming (lines 53-62).
7. **Mounted or inside structure**: Player is riding a mount or inside a building when attempting to start (lines 38-50).

## 5. Open Questions

1. **Exact loot group contents**: The files reference loot groups like "forage_food", "forage_bait", "forage_rare", and "forage_medical_component" but do not define what items belong to each group. This information is likely in external loot template files not included here.
2. **Medical forage resource bug**: In the MEDICAL section, `resName` is uninitialized when passed to `forageGiveResource` at line 302; it may default to an empty string, causing the function to pick a random flora from the planet instead of a specific type (lines 371-389).
3. **LAIR loot table logic**: The LAIR section always creates live creatures first (line 344) before checking for eggs (lines 331-342), meaning eggs are only awarded if creature creation fails. This may be unintended; the intended behavior is unclear without additional source files.
4. **Rare items unreachable**: The SCOUT loot table has a branch for "forage_rare" at dice >= 200, but `System::random(200)` returns 0-199, making this branch unreachable (lines 280-289).
5. **Foraging skill requirement**: The code checks the "foraging" skill mod but does not verify the player has the base "foraging" skill itself; it is unclear if a minimum skill level is required or if only the mod matters.
6. **Resource density calculation**: The `forageGiveResource` function uses `getDensityAt` to filter resources, but the exact threshold and how density varies by location are not defined in these files.

## ChatGPT's review (2026-10-18 22:30)

Checked supplied snapshots against Core3-dev 9d08e265; no Saluki disputed lead for this topic. Random API checked in utils/engine3/MMOEngine/src/system/lang/System.h:92-94 and System.cpp:13-15: integer random(n) includes n. Source only.

**Holds:** adjusted 50 action cost (must leave one), shellfish action/mind and water gates, 8500 ms task, per-axis 2 m/same-zone and combat finish checks, type-specific skill formulas and three-use exhaustion (ForageManagerImplementation.cpp:20-200).

**Corrections:**
- SCOUT rare loot is reachable at roll 200: food 160/201, bait 40/201, rare 1/201 (277-289). Medical rolls split 40/201 food,70/201 flora,60/201 level-1,30/201 level-60,1/201 level-200 components (294-320); the report's 30% for 170-199 and combined 60/200 range are wrong. LAIR eggs include 109 (324-342), so creatures 40/110 and eggs 70/110. Success is (chance+1)/81 until certainty, not a percent out of 100 (166-200).
- SIZE=10 is a coordinate half-width: abs(dx)<10 AND abs(dy)<10, on short/truncated coordinates, about a 20 m-wide box (ForageArea.h:31-60), despite its misleading side-length comment. Uses are consumed before the success/inventory check (ForageManagerImplementation.cpp:145-200); shellfish skips exhaustion. Three uses is not a three-item maximum: scout skills can add up to two items (228-241).
- resName is explicitly empty, not uninitialized (248), selecting random flora; zero density is rejected only while more than one candidate remains (371-388). This is no demonstrated bug.
- LAIR eggs return before createLoot; they are not conditional on failed creature creation (331-350). The open-question claim reverses execution order.

Verdict: Basic action and exhaustion flow supported; reject unreachable-rare, loot percentages, area size and invented medical/lair bug claims; gameplay untested.
