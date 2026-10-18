# Structure Maintenance and Permissions Report

## 1. Short Answer

In Core3, a structure's maintenance pool (`surplusMaintenance`) is measured in credits that deplete at an hourly rate (`getMaintenanceRate()`). The maximum condition equals four weeks of base maintenance cost (line 193: `maxCondition = getBaseMaintenanceRate() * 24 * 7 * 4`). When the pool runs out, condition damage increases proportionally to the deficit (line 587: `setConditionDamage(-surplusMaintenance, true)`). The structure is destroyed after 30 days of being on maintenance (line 810: `getDelayDestroyHours()` returns `30.0f * 24.0f`). Admin and entry permissions are stored in `structurePermissionList` with separate ADMIN, ENTRY, HOPPER, BAN, and VENDOR lists; privileged (GM) players bypass all checks (lines 816, 833, 854, 871).

## 2. How It Works

### Conditions, Skill Mods, and Numbers

- **Maximum condition** is set once when the structure enters the zone: `maxCondition = getBaseMaintenanceRate() * 24 * 7 * 4` (line 193), representing four weeks of maintenance credits.
- **Hourly maintenance cost** is calculated in `getMaintenanceRate()` (lines 318-330):
  - Base rate from template: `getBaseMaintenanceRate()` (line 797)
  - Multiplied by config key `Core3.Sandbox.StructureMaintenanceMultiplier` (default 1.0f, line 319)
  - Reduced by 20% if the owner has the maintenance skill mod (`maintenanceReduced` flag, lines 325-327)
  - Rounded to nearest integer (line 329)
- **Maintenance display**: `getMaintenanceMods()` returns "-20%" when reduced, otherwise "-" (lines 332-338).

### Timings and Decay

- **Maintenance depletion** occurs in `updateStructureStatus()` (lines 523-591):
  - Time since last check: `timeDiff = ((float) lastMaintenanceTime.miliDifference()) / 1000.0f` (line 544)
  - Maintenance due: `maintenanceDue = (getMaintenanceRate() / 3600.0f) * timeDiff` (line 545), i.e., rate per second × seconds elapsed
  - City property tax added if applicable: `cityTaxDue = city->getPropertyTax() / 100.0f * maintenanceDue` (line 562)
  - Total deducted: `surplusMaintenance -= (maintenanceDue + cityTaxDue)` (line 579)
- **Condition damage** applied when pool is negative: `setConditionDamage(-surplusMaintenance, true)` if `surplusMaintenance < 0` (lines 586-590)
- **Decay percentage** shown to players: `(maxCond - getConditionDamage()) * 100 / maxCond`, clamped 0-100 (lines 644-652)
- **Destroy timer**: Structures are destroyed after 30 days on maintenance (line 810: `getDelayDestroyHours()` returns `30.0f * 24.0f`)

### Maintenance Scheduling

- **Task scheduling** in `scheduleMaintenanceExpirationEvent()` (lines 364-438):
  - If `surplusMaintenance` is exhausted, scheduled immediately (line 400: `secondsRemaining = 1`)
  - If more than 24 hours remain, randomized to run every ~12 hours (lines 401-404)
  - Uses `StructureMaintenanceTask` (line 456) which calls `updateStructureStatus()` periodically

### Permission Lists

- **Storage**: `structurePermissionList` holds five lists: ADMIN, ENTRY, HOPPER, BAN, VENDOR (lines 175-189 for civic structures; cleared on insert to zone)
- **Admin check** (`isOnAdminList()`, lines 813-828): Returns true if player is privileged (line 816), on ADMIN list (line 818), or their guild is on ADMIN list (line 823)
- **Entry check** (`isOnEntryList()`, lines 830-849): Returns true if player has god mode (line 833), or is on ADMIN/ENTRY/VENDOR list (lines 835-837), or their guild is on those lists (lines 842-844)
- **Ban check** (`isOnBanList()`, lines 851-866): Returns true if player is on BAN list (line 856) or guild is on BAN list (line 861); god mode players are never banned (line 854)
- **Hopper check** (`isOnHopperList()`, lines 868-885): Returns true if player is privileged (line 871), on HOPPER or ADMIN list (lines 873-874), or guild is on those lists (lines 879-880)
- **General check** (`isOnPermissionList()`, lines 887-905): Privileged players bypass BAN list but pass all others; otherwise checks player and guild membership

### Messages the Player Sees

The source file does not define system message string IDs or SUI window text for maintenance/permission operations. It only logs errors internally (e.g., line 261: "destroyOrphanCivicStructure failed to get chat or struture manager."). The `getDebugStructureStatus()` function returns a debug string like "Next maintenance check in Xd Yh Zm Ws" (lines 594-628) but this is not shown to players.

## 3. What a Bot Test Should Check

### Observable Results

1. **Maintenance rate**: Verify `getMaintenanceRate()` returns expected value based on template base rate, config multiplier, and skill mod
2. **Condition damage**: After waiting for maintenance pool to deplete, check structure condition decreases proportionally (line 587)
3. **Decay percentage**: Query `getDecayPercentage()` and confirm it matches `(maxCond - conditionDamage) * 100 / maxCond` (lines 644-652)
4. **Permission checks**: Test `isOnAdminList()`, `isOnEntryList()`, `isOnBanList()`, `isOnHopperList()` for players on each list, guild members, and privileged players
5. **Credit deduction**: Verify `payMaintenance()` subtracts from cash first (if `cashFirst=true`), then bank (lines 670-686)

### Required Setup

1. A structure with known `getBaseMaintenanceRate()` > 0
2. Config key `Core3.Sandbox.StructureMaintenanceMultiplier` set to known value (default 1.0f, line 319)
3. Owner creature with/without maintenance skill mod (`maintenanceReduced` flag, lines 325-327)
4. Permission lists populated via `structurePermissionList.addToList()` (not shown in this file)
5. A credit object with known cash/bank balance for testing `payMaintenance()`

## 4. Likely Reasons a Test Sees No Effect

1. **Maintenance rate is zero**: If `getBaseMaintenanceRate()` returns 0, no decay occurs (line 441: early return in `scheduleMaintenanceTask()`)
2. **Structure is civic**: Civic structures skip maintenance updates entirely (line 531-536: early return in `updateStructureStatus()`)
3. **Config multiplier is zero**: `Core3.Sandbox.StructureMaintenanceMultiplier` set to 0 disables all maintenance cost (line 319)
4. **DEBUG_STRUCTURE_RAPID_DECAY not enabled**: Without this define, decay is too slow to observe in a test (lines 321-323, 451-453)
5. **Structure has no owner**: `getOwnerObjectID() == 0` causes early returns in multiple functions (lines 367, 442, 621)
6. **Maintenance task not scheduled**: If `structureMaintenanceTask` is null and maintenance rate > 0, a warning is logged but no decay occurs (line 619-620)

## 5. Open Questions

This single file does not answer:

1. **Client interaction flow**: No radial menu IDs, command names, or SUI window codes for depositing maintenance or managing permissions
2. **Permission list manipulation**: How players add/remove themselves and others from ADMIN/ENTRY/BAN lists (likely in a separate StructureManager or permission management class)
3. **System message string IDs**: The file references `StringIdManager` but does not define the actual message strings shown to players for maintenance events
4. **Structure status report format**: How the server sends structure condition and maintenance info to clients
5. **Credit object interaction**: Whether `payMaintenance()` is called by a terminal, radial command, or direct client action (the file shows the payment logic but not the trigger)
6. **Guild permission inheritance**: While guild membership is checked (lines 821-824, 840-845), the mechanism for guilds to manage structure permissions is not shown

Missing files likely needed: `StructureManager.cpp`, a StructureTerminal implementation, SUI window handler files, and string ID definition files.
