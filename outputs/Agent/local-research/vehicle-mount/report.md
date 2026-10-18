# Vehicle Deed to Mount Report

## 1. Short Answer

A player right-clicks a vehicle deed and selects "Generate" (radial menu item 20) to create a VehicleControlDevice in their datapad, which contains the actual vehicle. The device is then used from the datapad radial menu to call the vehicle: outside cities it waits 15 seconds before spawning; inside cities or for privileged players it spawns immediately. While mounted, the player's state changes to `RIDINGMOUNT`, they become a child of the vehicle object (the "rider" slot), and their speed/acceleration are modified by skill mods like `force_vehicle_speed`. The player can dismount via radial menu or store the vehicle back into the datapad. Combat, being indoors, distance over 7 meters, line-of-sight failures, disabled vehicles, cooldown timers, and max-vehicle limits all block actions at various stages.

## 2. How It Works

### Generating a Vehicle Deed (creating the control device)

**Conditions & checks:**
- The deed's radial menu item 20 ("Generate") is selected via `handleObjectMenuSelect` in `VehicleDeedImplementation.cpp:56`.
- If the player is already in combat or inside a building, the action is refused with message `"@pet/pet_menu:cant_call_vehicle"` (line 62).
- The player must have a datapad slotted; otherwise a plain error is sent (lines 68-70).
- The player's datapad is checked for existing VehicleControlDevice objects against `PlayerManager::getBaseStoredVehicles()` (lines 74-90); exceeding the limit sends `"@pet/pet_menu:has_max_vehicle"` (line 88).

**What happens:**
- A `VehicleControlDevice` object is created from the deed's template (line 92).
- A `VehicleObject` is created from the deed's `generatedObjectTemplate` (line 101), its child objects are initialized, max condition set to the deed's hit points, and damage cleared (lines 111-114).
- The control device is linked to the vehicle via `setControlledObject` (line 114).
- Both are transferred into the player's datapad; the deed is destroyed from world and database (lines 116-123).

**Bot confirmation:** After success, the datapad contains a new VehicleControlDevice; the deed no longer exists.

### Calling the Vehicle from the Datapad

**Conditions & checks in `VehicleControlDeviceImplementation::generateObject` (lines 22-125):**
- If the player is dead, incapacitated, indoors (`getParent() != nullptr`), or in combat, the call is refused with `"@pet/pet_menu:cant_call_vehicle"` (lines 29-32).
- Hutts can only call the A1 Deluxe Floater; other templates send `"A Hutt cannot ride this. Sell it, or give it to someone with legs."` (lines 40-45).
- If a trade session is active, it is aborted (lines 59-67).
- If a `call_mount` pending task already exists, the player receives `"pet/pet_menu:call_delay_finish_vehicle"` with seconds remaining and the call is refused (lines 69-78).
- The datapad is re-checked for existing spawned vehicles; if more than 2 are already on the ground, `"@pet/pet_menu:has_max_vehicle"` is sent (lines 86-103).

**Timings:**
- Outside cities and for non-privileged players, a `CallMountTask` is scheduled with a **15-second delay** (lines 105-112), and the player sees `"pet/pet_menu:call_vehicle_delay"` (line 108).
- Inside cities or for privileged players, `spawnObject` is called immediately (line 123).

**What happens on spawn (`spawnObject`, lines 127-184):**
- The player must be on a ground zone; otherwise the function returns silently (lines 143-147).
- If in a trade session, it is aborted again (lines 149-153).
- The vehicle is positioned at the player's world coordinates and transferred to the zone (lines 155-166).
- A `VehicleDecayTask` is started on the vehicle (lines 168-172).
- For jetpacks (server CRC `0x32F87A54`), a customization variable is set and `executeObjectControllerAction("mount")` is called automatically (lines 174-177).
- Status is updated via `updateStatus(1)` (line 179).

**Bot confirmation:** After the delay (or immediately indoors), a VehicleObject appears at the player's feet; the control device remains in the datapad.

### Mounting the Vehicle

**Conditions & checks in `MountCommand::doQueueCommand` (lines 27-199):**
- A cooldown on `"mount_dismount"` is enforced (line 30).
- If already riding a mount, issuing mount calls dismount instead (lines 34-39).
- The target must be a valid `VehicleObject` or `Mount` (lines 51-53).
- Hutts are restricted to the A1 Deluxe Floater template (lines 56-60).
- `checkStateMask` and `checkInvalidLocomotions` are called; failures return `INVALIDSTATE`/`INVALIDLOCOMOTION` (lines 70-74).
- The vehicle's creature link must match the player's object ID (line 76).
- The player and vehicle must be within **7 meters** and have line of sight (line 79).
- Neither the player nor the vehicle can be inside a parent object (lines 83-85).
- If the vehicle is disabled, incapacitated, or dead, mounting is refused; disabled vehicles send `"@pet/pet_menu:cant_mount_veh_disabled"` (lines 87-94).

**What happens on mount:**
- The vehicle's posture is forced to `UPRIGHT` if lying down or sitting (lines 96-98).
- The vehicle state changes to `MOUNTEDCREATURE` (line 102).
- The player is transferred into the vehicle as a child in the `RIDER` arrangement (line 104); this makes the player appear in the vehicle's "rider" slot.
- The player's state changes to `RIDINGMOUNT` (line 112).
- A **2-second cooldown** is set on `"mount_dismount"` (line 114).
- Restricted buffs (`burstrun`, `retreat`, Jedi force run buffs) are removed from the player; `gallop` is also cleared (lines 119-133).
- Speed modifiers are calculated: base vehicle speed, animal mount speeds via `PetManager::getMountedRunSpeed` if applicable, and Force-sensitive skill mods (`force_vehicle_speed`, `force_vehicle_control`) added for vehicles (lines 152-187).
- The player's turn scale, acceleration multiplier, and run speed are updated; mounted combat slow is applied (lines 189-194).

**Bot confirmation:** Player state becomes `RIDINGMOUNT`; `getParent()` returns the vehicle object; speed attributes change.

### Dismounting

Dismount can be triggered by:
- Radial menu dismount command, which calls `MountCommand` with the opposite logic (if riding, it calls dismount).
- `storeObject` on the control device, which checks `isRidingMount()` and calls `executeObjectControllerAction("dismount")` if force is true or cooldown allows (lines 209-217).

**What happens on dismount:**
- The player's state changes away from `RIDINGMOUNT`.
- The player is removed from the vehicle's rider slot and returned to the zone.
- Speed mods are reverted (inferred from the mount logic reversing).

### Storing the Vehicle Back

**Conditions & checks in `storeObject` (lines 197-251):**
- If not forced, the player cannot store while in combat or dead (line 206).
- If riding, dismount is triggered first if cooldown allows (lines 209-217).
- The vehicle's decay task is cancelled (lines 221-226).
- The vehicle is destroyed from the world; its creature link is cleared (lines 228-231).
- Status is updated to 0 (line 237).
- If it was a rental with zero uses left, the control device is also destroyed and `"pet/pet_menu:uses_complete"` is sent (lines 241-249).

**Bot confirmation:** Vehicle disappears from world; control device remains in datapad (unless rental expired).

## 3. What a Bot Test Should Check

### Setup
- Ensure the player has a datapad slotted (`getSlottedObject("datapad")`).
- Have a vehicle deed in inventory (or create one via test tools).
- Be outdoors, not in combat, not inside a building.
- For outdoor call testing, be outside any city region and not privileged to trigger the 15-second delay.

### Observable Results After Each Step

**After generating the deed:**
- System message: none (success is silent).
- Datapad contains a new VehicleControlDevice object.
- Deed no longer exists in inventory or world.

**After calling the vehicle (outdoors):**
- System message: `"pet/pet_menu:call_vehicle_delay"` with "15" seconds.
- After 15 seconds, a VehicleObject appears at player position.
- Player state remains unchanged during delay; no `RIDINGMOUNT` yet.

**After calling the vehicle (indoors/city):**
- System message: none (instant spawn).
- VehicleObject appears immediately.

**After mounting:**
- Player state changes to `RIDINGMOUNT`.
- `getParent()` on player returns the vehicle object.
- Vehicle state is `MOUNTEDCREATURE`.
- Player's run speed and acceleration mods change (check via attribute list or speed queries).
- Restricted buffs are removed from player.

**After dismounting:**
- Player state reverts from `RIDINGMOUNT`.
- `getParent()` returns nullptr (or previous parent).
- Vehicle state changes from `MOUNTEDCREATURE`.

**After storing:**
- VehicleObject is destroyed from world.
- Control device remains in datapad.
- If rental expired, control device is also gone and `"pet/pet_menu:uses_complete"` message appears.

### Setup Requirements for Bot
- Player must have a valid datapad.
- Player must not be in combat (`isInCombat()` returns false).
- Player must be outdoors (not inside a building) for deed generation.
- For outdoor call testing, player should be outside city regions.

## 4. Likely Reasons a Test Sees No Effect

1. **Player is indoors:** `getParent() != nullptr` blocks both deed generation and vehicle call with `"@pet/pet_menu:cant_call_vehicle"` (`VehicleDeedImplementation.cpp:61`, `VehicleControlDeviceImplementation.cpp:29`).
2. **Player is in combat:** Same message as above; also blocks storing while mounted (`VehicleDeedImplementation.cpp:61`, `VehicleControlDeviceImplementation.cpp:206`).
3. **Cooldown active:** The 2-second `"mount_dismount"` cooldown prevents rapid mount/dismount cycles (`MountCommand.h:30`, `VehicleDeedImplementation.cpp:114`).
4. **Max vehicles exceeded:** If the datapad already has the maximum number of control devices or spawned vehicles, `"@pet/pet_menu:has_max_vehicle"` is sent (`VehicleDeedImplementation.cpp:87`, `VehicleControlDeviceImplementation.cpp:96`).
5. **Distance/LOS failure:** Mounting requires being within 7 meters and having line of sight; otherwise it silently fails (`MountCommand.h:79`).
6. **Vehicle disabled/dead/incapacitated:** Disabled vehicles send `"@pet/pet_menu:cant_mount_veh_disabled"`; others fail silently (`MountCommand.h:87-94`).
7. **Hutt species restriction:** Hutts can only ride the A1 Deluxe Floater; other vehicles are refused (`VehicleControlDeviceImplementation.cpp:40`, `MountCommand.h:56`).
8. **Pending call task:** Calling again during the 15-second delay sends `"pet/pet_menu:call_delay_finish_vehicle"` and refuses (`VehicleControlDeviceImplementation.cpp:69`).
9. **Trade session active:** Aborts trade silently, may interfere with timing (`VehicleControlDeviceImplementation.cpp:59`).

## 5. Open Questions

- **What is the exact cooldown duration for `mount_dismount` after dismount?** The code sets it to 2000ms on mount (line 114), but the recovery check at line 30 doesn't show the default value; it may be defined elsewhere.
- **Where is `checkStateMask` and `checkInvalidLocomotions` implemented?** These are called in `MountCommand.h:70-74` but their logic (what states/locomotions are checked) is not in this file.
- **What is the max stored vehicles limit (`getBaseStoredVehicles()`)?** The value is retrieved from `PlayerManager` but not defined here; it may vary by player level or faction.
- **How does `CallMountTask` work internally?** It's referenced at `VehicleControlDeviceImplementation.cpp:106` but the task implementation is in a separate file (`tasks/CallMountTask.h`) not provided.
- **What does `updateStatus(1)` and `updateStatus(0)` do exactly?** These are called on the control device during spawn/store (lines 179, 237) but their effect on client-visible status icons or attributes is unclear without the parent class implementation.
- **How long does the `VehicleDecayTask` last before despawning an unmounted vehicle?** The task is scheduled at line 168 but its duration is not specified here.
- **What radial menu ID and command name does the client send to call/store a vehicle from the datapad?** The server handles radial item 20 for deeds (line 53), but the datapad control device's radial menu items and their IDs are not shown in these files.
