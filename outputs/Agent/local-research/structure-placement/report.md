# Structure Placement Report (Core3)

## 1. Short Answer

A player places a house or harvester by using a StructureDeed, which triggers the `/placestructure` command with arguments `deedID x y rotation`. The server validates the player's state, location, city rules, lot count, and deed possession. If all checks pass, the deed is destroyed and a PlaceStructureSession creates the structure at the target coordinates on the world floor. The new structure is owned by the player who used the deed, and no credits are refunded on failure because the deed is consumed before the final placement step (PlaceStructureCommand.h:131; StructureManager.cpp:470-473).

## 2. How It Works

### Command Invocation
The client sends `/placestructure <deedID> <x> <y> <rotation>` where rotation is 0–3 (multiples of 90°) (PlaceStructureCommand.h:54-63).

### Pre-placement Checks (PlaceStructureCommand.h)
1. **Mounted check**: If riding a mount, sends `@player_structure:cant_place_mounted` and returns (line 24).
2. **State mask**: Returns INVALIDSTATE if player is in an invalid state (line 29).
3. **Locomotion check**: Returns INVALIDLOCOMOTION if movement is restricted (line 32).
4. **Inside building**: If `creature->getParent() != nullptr`, sends `@player_structure:not_inside` and returns (lines 35-36).
5. **City client region**: If in a city client region, sends `@player_structure:city_too_close` with the city name and returns (lines 41-46).
6. **Distance/height validation**: Calculates distance from player to placement location; if >100m or height difference >10m, logs an error and sends `@system_msg:out_of_range` (lines 73-88).
7. **No-build ActiveAreas**: Iterates active areas at the target; if any is a no-build zone, sends `@player_structure:not_permitted` and returns (lines 94-104).
8. **PlanetManager no-build conflict**: Calls `planetMan->findObjectInNoBuildZone()`; if a conflict exists, sends `@player_structure:city_too_close` with the conflict name and returns (lines 111-121).

### Deed Placement Logic (StructureManager.cpp)
After passing PlaceStructureCommand checks, the deed's `placeStructure()` method is called (PlaceStructureCommand.h:131), which delegates to `StructureManager::placeStructureFromDeed()`:

1. **Session check**: If player already has a PLACESTRUCTURE session, returns 1 (line 274).
2. **Faction deed checks**: For non-neutral deeds, verifies player faction matches and is not neutral/on leave; sends `@faction_perk:prose_not_neutral` or `@faction_perk:prose_wrong_faction` (lines 280-305).
3. **Planet template check**: If the structure template is not allowed on this planet, sends `@player_structure:wrong_planet` and returns (lines 312-315).
4. **Building permitted check**: Calls `planetManager->isBuildingPermittedAt()`; if false, sends `@player_structure:not_permitted` (lines 317-320).
5. **City region re-check**: Re-validates city regions; sends `@player_structure:not_permitted` if in a client region (lines 322-342).
6. **Footprint overlap check**: Computes the structure's footprint with rotation and checks for overlaps with nearby objects within 128m; sends `@player_structure:no_room` on overlap (lines 344-398).
7. **City rank requirement**: If the structure requires a city rank and player is not in a city, sends `@city/city:build_no_city` (lines 401-406).
8. **Zoning rights**: If in a city with zoning enabled and player lacks rights, sends `@player_structure:no_rights` (lines 409-412).
9. **City rank check**: If city exists but player's rank is insufficient, sends `@city/city:rank_req` with required rank (lines 414-421).
10. **Civic structure mayor check**: If the structure is civic and player is not mayor, sends `@player_structure:cant_place_civic` (lines 423-426).
11. **Unique structure check**: If the city already has this unique structure type, sends `@player_structure:cant_place_unique` (lines 428-431).
12. **Deed possession**: Verifies deed is still a sub-child of creature; sends `@player_structure:no_possession` if not (lines 437-440).
13. **Ability/skill check**: Gets `abilityRequired` from the template and checks `ghost->hasAbility()`; sends `@player_structure:<abilityRequired>` on failure (lines 445-450).
14. **Lot count check**: Gets `lots` from `serverTemplate->getLotSize()` and checks `ghost->hasLotsRemaining(lots)`; sends `@player_structure:not_enough_lots` with the lot count needed (lines 452-459).

### Structure Creation
If all checks pass:
1. A `PlaceStructureSession` is created and added to the creature (lines 466-467).
2. `session->constructStructure(x, y, angle)` is called (line 470). This creates the actual structure object via `StructureManager::placeStructure()` (lines 478-573):
   - Gets terrain height at (x, y) (line 491).
   - Creates the structure object from the template (line 525).
   - Grants ADMIN permission and sets owner to the creature (lines 541-542).
   - Adds the structure to the player's owned structures list (lines 546-547).
   - Initializes position and rotation (lines 561-562).
   - Transfers the object to the zone (line 566).
   - Creates child objects (line 568).
   - Calls `notifyStructurePlaced(creature)` (line 570).
3. The deed is destroyed from the world (line 473).

### What the Player Sees
- **Success**: No explicit success system message is sent by this code path; the structure appears in the world and the deed disappears from inventory.
- **Failure messages** (by category):
  - `@player_structure:cant_place_mounted` — riding a mount
  - `@player_structure:not_inside` — inside a building
  - `@player_structure:city_too_close` — too close to a city (sent twice in different code paths)
  - `@system_msg:out_of_range` — placement location too far or height difference too large
  - `@player_structure:not_permitted` — no-build zone or building not permitted
  - `@faction_perk:prose_not_neutral` / `@faction_perk:prose_wrong_faction` — faction deed mismatch
  - `@player_structure:wrong_planet` — deed invalid on this planet
  - `@player_structure:no_room` — footprint overlap
  - `@city/city:build_no_city` — must be in a city
  - `@player_structure:no_rights` — no zoning rights
  - `@city/city:rank_req` — insufficient city rank
  - `@player_structure:cant_place_civic` — must be mayor for civic structure
  - `@player_structure:cant_place_unique` — city already has this unique structure
  - `@player_structure:no_possession` — deed no longer in inventory
  - `@player_structure:<abilityRequired>` — missing required skill/ability
  - `@player_structure:not_enough_lots` with lot count — insufficient lots

## 3. What a Bot Test Should Check

### Setup Required
1. Ensure the bot character is not riding a mount and is outside any building (PlaceStructureCommand.h:23-37).
2. Verify the bot has the required deed in inventory (StructureManager.cpp:437).
3. Confirm the bot has sufficient lots for the structure (StructureManager.cpp:452-459).
4. If testing a faction deed, ensure the bot's faction matches the deed's faction (StructureManager.cpp:280-305).
5. If testing city requirements, ensure the bot is in the correct city with sufficient rank and zoning rights (StructureManager.cpp:401-431).

### Observable Results to Verify
1. **System messages**: Capture all system messages sent during the test and compare against expected message string IDs listed in section 2.
2. **Deed removal**: Confirm the deed is no longer in the bot's inventory after a successful placement (StructureManager.cpp:473).
3. **Structure appearance**: Verify a structure object exists at the target coordinates with the correct template, rotation, and owner (StructureManager.cpp:541-562).
4. **Owner verification**: Check that `structureObject->getOwnerObjectID()` matches the bot's object ID (StructureManager.cpp:542).
5. **Lot deduction**: Verify the bot's remaining lots decreased by the structure's lot size (StructureManager.cpp:452-459; inferred: lots are consumed during session creation).
6. **No-build zone test**: Attempt placement in a no-build zone and confirm `@player_structure:not_permitted` is received (PlaceStructureCommand.h:101; StructureManager.cpp:318).

### Log Confirmation Line
A bot or log can confirm success by checking for the absence of error messages plus the presence of the new structure object at the expected coordinates with the correct owner. A failure confirmation line would be the specific system message string ID received (e.g., `@player_structure:not_enough_lots`).

## 4. Likely Reasons a Test Sees No Effect

1. **Deed not in inventory**: If the deed was moved, destroyed, or never spawned, the possession check fails (StructureManager.cpp:437-440).
2. **Wrong planet template**: The deed's generated template may not be allowed on the test planet (StructureManager.cpp:312-315).
3. **No-build zone**: The target coordinates fall within a no-build ActiveArea or PlanetManager conflict zone (PlaceStructureCommand.h:100; StructureManager.cpp:317).
4. **City restrictions**: The location is too close to a city, or the bot lacks zoning rights/city rank for civic/unique structures (PlaceStructureCommand.h:41; StructureManager.cpp:409-431).
5. **Footprint overlap**: Another structure's footprint overlaps the placement area (StructureManager.cpp:383-397).
6. **Insufficient lots**: The bot does not have enough lots remaining for the structure size (StructureManager.cpp:454-458).
7. **Missing skill/ability**: The bot lacks the required ability from the template (StructureManager.cpp:447-449).
8. **Faction mismatch**: For faction deeds, the bot's faction does not match (StructureManager.cpp:289-304).
9. **Already placing**: A previous placement session is still active (StructureManager.cpp:274).

## 5. Open Questions

1. **PlaceStructureSession::constructStructure()**: The actual construction logic (terrain validation, structure spawning details, credit charging) is in `PlaceStructureSession`, which is not included in the provided files. Its implementation is referenced at StructureManager.cpp:470 but the class definition and method body are missing.
2. **Credit refund on failure**: The code destroys the deed before calling constructStructure (StructureManager.cpp:473), so no credits are refunded if construction fails. However, it is unclear whether credits are charged during `constructStructure()` or beforehand, since that logic is in the missing PlaceStructureSession file.
3. **Lot consumption timing**: It is inferred that lots are consumed when the session is created (StructureManager.cpp:466-470), but the exact mechanism is not visible in the provided files.
4. **PlaceStructureSession header**: The file `server/zone/objects/player/sessions/PlaceStructureSession.h` (or .cpp) referenced at StructureManager.cpp:23 and 466 is not available in the provided source copy, so its full API and behavior are unknown.


## ChatGPT's review (2026-10-18 02:30)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) and available `src/` snapshots; no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** deed arguments, mounted/interior/no-build/range checks, faction/planet/footprint/zoning/ability/lot admission and ownership on creation hold (PlaceStructureCommand.h:23-131; StructureManager.cpp:270-477,478-570). The snapshot command/manager files match current source apart from final blank lines.

**Corrections:**
- The draft contradicts source order: constructStructure is called at StructureManager.cpp:470 BEFORE destroyObjectFromWorld at 473. World removal is not database destruction of the deed. A conclusion of permanent deed loss/no refund cannot follow from this.
- The session implementation exists: src/server/zone/objects/player/sessions/PlaceStructureSessionImplementation.cpp:26-86 schedules construction; completeSession:150-163 attempts final placement and transfers the deed back to inventory if creation returns nullptr. That explicitly contradicts the blanket no-refund/deed-consumed claim. It does not guarantee recovery if inventory transfer itself fails.
- Placement is asynchronous: 100 ms fallback, or lotSize*3000 ms when a barricade is created; faction_perk can use a GCW delay (49-84). The structure need not appear in the same command call. Completion also creates a waypoint and construction-complete mail (176-201), so world appearance is not the only success signal.
- Rotation input rejects angle>3, but the cited command does not reject negative angles (PlaceStructureCommand.h:60-63). Do not claim full 0-3 validation. Height check is signed playerZ-placementZ>10, not abs height difference (73-77); the 100 m distance is 3D.
- The rank requirement compares CITY rank, not the player's personal profession/rank (StructureManager.cpp:401-419).
- Lots are checked at admission, but owned-structure registration occurs on actual creation (StructureManager.cpp:544-547); the report's lot consumption at session creation is unsupported. Final z may use highest terrain over footprint when appropriate (491-515), not always one floor point.

**Not established:** ordinary placement credit charging, exact lot accounting and cancellation edge cases. No structure was placed and no galaxy touched.

**Verdict:** Admission/ownership overview holds; reject deed-loss/no-refund claim, correct asynchronous placement, signed height/city rank and unproven lot timing.
