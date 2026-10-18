# Slicing Mechanic Report (SWGEmu Core3, pre-CU)

## 1. Short Answer

Slicing is a smuggler activity that lets the player open locked containers, modify weapons and armor, or hack mission terminals. The player must have a Precision Laser Knife in inventory, plus a WeaponUpgradeKit or ArmorUpgradeKit when slicing those item types. A random correct cable (0=blue, 1=red) is chosen at session start; the player picks two cables in sequence, matching both to succeed. Molecular Clamps and Flow Analyzers are optional tools that can reveal the correct cable. Success unlocks containers or applies stat mods; failure destroys the knife charge and ends the session.

## 2. How It Works

### Conditions & Prerequisites
- The target object must be sliceable (`isSliceable()`) or the session must be flagged as base/keypad slice (SlicingSession.idl:73-85).
- The player must have a Precision Laser Knife in inventory; otherwise `@slicing/slicing:no_knife` is shown (SlicingSessionImplementation.cpp:68-71).
- For weapons, the player must also have a WeaponUpgradeKit (`@slicing/slicing:no_weapon_kit`) (SlicingSessionImplementation.cpp:85-88).
- For armor, the player must have an ArmorUpgradeKit (`@slicing/slicing:no_armor_kit`) (SlicingSessionImplementation.cpp:90-93).
- The object must be in the player's inventory for normal slicing; base/keypad slices are exceptions (SlicingSessionImplementation.cpp:78-83, 168-173).
- If the target already has an active slicing session, `@slicing/slicing:slicing_underway` is shown and the menu is not opened (SlicingSessionImplementation.cpp:63-66).

### Skill & Mods
- Slicing skill level is determined by checking for skills in order: `combat_smuggler_novice`, `combat_smuggler_slicing_01` through `_04`, then `combat_smuggler_master` (SlicingSessionImplementation.cpp:244-266). Levels 0-5 are returned.
- For weapon slicing, skill level sets the percentage range for random mods:
  - Level 3/4: min+5, max+5
  - Level 4: min+10, max+10 (cumulative with case 5)
  - Level 5: min+15, max+15 (cumulative)
  - Levels 2 and below get no weapon mods (SlicingSessionImplementation.cpp:518-533).
- Armor slicing uses a similar skill-based range (SlicingSessionImplementation.cpp:542-576).

### Slicing Session Steps & Menu
1. **Initialize**: `initalizeSlicingMenu()` creates a `SuiListBox` with type `SLICING_MENU` and adds the session to both player and object (SlicingSessionImplementation.cpp:96-112).
2. **Phase 0** (progress=0): Menu shows "blue_cable", "red_cable", "use_clamp", "use_analyzer" options (SlicingSessionImplementation.cpp:136-142). The correct cable is randomly chosen as `firstCable` (0 or 1) at session init (SlicingSessionImplementation.cpp:33).
3. **Phase 1** (progress=1): After one cable is correctly selected, the menu shows both cables again; selecting the wrong one triggers failure (SlicingSessionImplementation.cpp:147-149, 213-216).
4. **Tools**: 
   - Molecular Clamp can be used in phase 0 to reveal the correct cable; it is consumed from inventory (SlicingSessionImplementation.cpp:376-403).
   - Flow Analyzer calculates success rate based on its effectiveness stat; if successful, `nodeCable` is set to `firstCable`, revealing the correct cable (SlicingToolImplementation.cpp:75-84, SlicingSessionImplementation.cpp:426-433).
5. **Success**: When both cables match `firstCable`, `handleSlice()` is called (SlicingSessionImplementation.cpp:448-505).
6. **Failure**: Wrong cable selection calls `handleSliceFailed()` which destroys the laser knife charge and ends the session (SlicingSessionImplementation.cpp:182, 192, 216).

### Results by Object Type
- **Containers** (`isContainerObject()` or `PLAYERLOOTCRATE`): Opens the container; a `RelockLootContainerEvent` is prepared for later relocking (SlicingSessionImplementation.cpp:471-473). Awards 250 XP to "slicing" (SlicingSessionImplementation.cpp:473).
- **Mission Terminals**: Adds the player as slicer, shows `@slicing/slicing:terminal_success`, applies a 2-minute cooldown on terminal slicing (SlicingSessionImplementation.cpp:474-478, 236). Awards 100 XP (SlicingSessionImplementation.cpp:476).
- **Weapons**: Calls `handleWeaponSlice()` which randomly applies damage or speed mods based on skill level; consumes a WeaponUpgradeKit (SlicingSessionImplementation.cpp:507-540, 85-88). Awards 250 XP (SlicingSessionImplementation.cpp:481).
- **Armor**: Calls `handleArmorSlice()` which randomly applies encumbrance or effectiveness mods; consumes an ArmorUpgradeKit (SlicingSessionImplementation.cpp:542-576, 90-93). Awards 250 XP (SlicingSessionImplementation.cpp:484).
- **Base Slice** (`isBaseSlice()`): Executes a `SecuritySliceTask` via GCWManager; awards 1000 XP (SlicingSessionImplementation.cpp:485-497).

### Messages the Player Sees
- `@slicing/slicing:no_knife` - no Precision Laser Knife (SlicingSessionImplementation.cpp:69, 186, 196, 219)
- `@slicing/slicing:no_weapon_kit` / `@slicing/slicing:no_armor_kit` - missing upgrade kit (SlicingSessionImplementation.cpp:86, 91)
- `The object must be in your inventory in order to perform the slice.` - wrong location (SlicingSessionImplementation.cpp:81, 170)
- `@slicing/slicing:slicing_underway` - session already active (SlicingSessionImplementation.cpp:64)
- `@slicing/slicing:used_clamp` / `@slicing/slicing:no_clamp` - clamp usage (SlicingSessionImplementation.cpp:369, 402)
- `@slicing/slicing:used_node` / `@slicing/slicing:no_node` - flow analyzer usage (SlicingSessionImplementation.cpp:439, 445)
- `@slicing/slicing:terminal_success` - terminal hack success (SlicingSessionImplementation.cpp:478)

## 3. What a Bot Test Should Check

### Setup Required
- Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher (SlicingSessionImplementation.cpp:259).
- Place a Precision Laser Knife (`SceneObjectType::LASERKNIFE`) in the player's inventory (SlicingSessionImplementation.cpp:286).
- For weapon slicing, include a WeaponUpgradeKit (`SceneObjectType::WEAPONUPGRADEKIT`) in inventory (SlicingSessionImplementation.cpp:318).
- For armor slicing, include an ArmorUpgradeKit (`SceneObjectType::ARMORUPGRADEKIT`) in inventory (SlicingSessionImplementation.cpp:345).
- Place the target object in the player's inventory (SlicingSessionImplementation.cpp:79).

### Observable Results to Check
- **System messages**: Verify correct success/failure messages appear (see section 2).
- **SUI menu**: Confirm the slicing menu appears with correct options for the phase (SlicingSessionImplementation.cpp:136-149).
- **Inventory changes**: Laser knife charge is consumed on failure; upgrade kits are destroyed on weapon/armor slice success (SlicingSessionImplementation.cpp:292, 320-321, 347-348).
- **Object state**: Containers should be unlocked after successful slice; weapons/armor should have modified attributes.
- **Cooldown**: Mission terminal slicing applies a "slicing.terminal" cooldown (SlicingSessionImplementation.cpp:236).
- **XP award**: Verify XP is awarded for the "slicing" experience type (SlicingSessionImplementation.cpp:473, 476, 481, 484, 486).

### Test Scenarios
1. Successful slice with correct cable sequence.
2. Failed slice with wrong first cable selection.
3. Failed slice with wrong second cable selection.
4. Slice without Precision Laser Knife (should show no_knife message).
5. Weapon/armor slice without upgrade kit (should show appropriate message).
6. Use Molecular Clamp to reveal correct cable, then succeed.
7. Use Flow Analyzer to reveal correct cable, then succeed.

## 4. Likely Reasons a Test Sees No Effect

- Player lacks `combat_smuggler_novice` or higher skill (SlicingSessionImplementation.cpp:261-262).
- No Precision Laser Knife in inventory (SlicingSessionImplementation.cpp:68-71).
- Target object not in player's inventory (for non-base/keypad slices) (SlicingSessionImplementation.cpp:79-83).
- Target already has an active slicing session (SlicingSessionImplementation.cpp:63-66).
- Missing WeaponUpgradeKit or ArmorUpgradeKit for the respective item type (SlicingSessionImplementation.cpp:85-93).
- Wrong cable selected during the sequence (SlicingSessionImplementation.cpp:182, 192, 216).
- Base/keypad slicing flags not set when attempting those slice types (SlicingSession.idl:38-39).

## 5. Open Questions

- The exact implementation of `handleSliceDamage()`, `handleSliceSpeed()`, `handleArmorSlice()`, `handleSliceEncumbrance()`, and `handleSliceEffectiveness()` is not visible in the provided files (declared as native in SlicingSession.idl:128-138).
- The `RelockLootContainerEvent` class is included but its behavior is not shown (SlicingSessionImplementation.cpp:18).
- How base slicing and keypad slicing differ from normal container slicing beyond the XP amount is unclear; the files reference these flags but do not show their full setup logic.
- The exact attribute modifications applied to weapons and armor are not visible in these files.
- The `handleSliceFailed()` implementation is native and not shown (SlicingSession.idl:106).
