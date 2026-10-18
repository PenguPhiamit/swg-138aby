# Harvester Operation Report (Core3, pre-CU)

## 1. Short Answer

In Core3, a player operates a harvester by right-clicking it and selecting "Operate Machinery" from the radial menu (radial ID 118, item ID 78). The server responds with an SUI window (`ResourceHarvesterActivatePageMessage`) that lets the player choose a resource to harvest, deposit power and maintenance credits, and start/stop operation. When activated, the harvester checks for sufficient surplus power and maintenance; if either is insufficient it broadcasts a system message and refuses activation. While running, the server periodically calls `updateInstallationWork()` which deducts power/maintenance from surplus reserves, extracts resources into the hopper at a rate of `extractionRate × spawnDensity` per minute, and shuts down when the hopper fills, power/maintenance runs out, or the resource node despawns. The owner can also add more power via a separate SUI transfer box (`STRUCTURE_ADD_ENERGY`).

## 2. How It Works

### Radial Menu & Activation Trigger
- Right-clicking a harvester adds radial menu item ID **118** with label `"@harvester:manage"` (Operate Machinery) at `HarvesterObjectImplementation.cpp:20`.
- When the player selects this item, `handleObjectMenuSelect` receives **selectedID 78** and sends `ResourceHarvesterActivatePageMessage(getObjectID())` to the client (`HarvesterObjectImplementation.cpp:64-67`). This message opens the harvester operation SUI window on the client side.

### Power Deposit
- The owner can add power via radial menu item ID **77** (inferred from `HarvesterObjectImplementation.cpp:69-71`), which calls `handleStructureAddEnergy(player)`.
- `handleStructureAddEnergy` creates a `SuiTransferBox` with window type `STRUCTURE_ADD_ENERGY`, prompt title `"@player_structure:add_power"`, and text showing current surplus power and total available energy from the player (`InstallationObjectImplementation.cpp:205-223`).
- The callback used is `InsertPowerSuiCallback` (`InstallationObjectImplementation.cpp:221`). (The callback implementation is not in the provided files.)

### Resource Selection & Activation Checks
- When the harvester is activated via the SUI window, the server eventually calls `setActive(true)` (`InstallationObjectImplementation.cpp:76-148`).
- **Activation checks** (all must pass for activation to proceed):
  - If not a factory and `currentSpawn == nullptr`, return without activating (`InstallationObjectImplementation.cpp:83-84`).
  - If `spawnDensity < 0.10`, return without activating (`InstallationObjectImplementation.cpp:88-90`).
  - If `getBasePowerRate() != 0` and `surplusPower <= 0`, broadcast system message with string ID `"player_structure:power_deposit_incomplete"` and return (`InstallationObjectImplementation.cpp:92-97`).
  - If `getMaintenanceRate() != 0` and `surplusMaintenance <= 0`, broadcast system message with string ID `"shared:harvester_no_maint_4"` and return (`InstallationObjectImplementation.cpp:100-105`).
- On successful activation: sets `active = true`, clears `extractionRemainder`, updates `lastStartTime`, unsets the `ACTIVATED` option bit, records `resourceHopperTimestamp`, broadcasts `InstallationObjectDeltaMessage3` and `InstallationObjectDeltaMessage7` with operating state and options bitmask to operators (`InstallationObjectImplementation.cpp:114-147`).

### Setting Active Resource
- The SUI window (sent by `ResourceHarvesterActivatePageMessage`) presumably lets the player select a nearby resource node. When confirmed, the server calls `changeActiveResourceID(spawnID)` (`InstallationObjectImplementation.cpp:505-611`).
- This function validates that the spawn exists and is `"inShift"` (active), looks it up in the resource manager's list for this installation type, sets `currentSpawn`, recalculates `spawnDensity` from the node's position, updates `resourceHopperTimestamp`, creates or retrieves a `ResourceContainer` for the spawn, adds it to the hopper via `addResourceToHopper`, and calls `setActiveResource(container)` (`InstallationObjectImplementation.cpp:584-603`).
- It broadcasts `InstallationObjectDeltaMessage7` with updated extraction rate and active resource spawn ID to operators (`InstallationObjectImplementation.cpp:605-610`).

### Extraction Rate Calculation
- The actual extraction rate is `extractionRate × spawnDensity` (`InstallationObjectImplementation.cpp:740`).
- `extractionRate` is set via template data or configuration; `spawnDensity` is retrieved from the resource node at the harvester's position (`InstallationObjectImplementation.cpp:86, 585`).

### Resource Hopper & Harvesting Loop
- The server periodically calls `updateInstallationWork()` which invokes `updateMaintenance()` and `updateHopper()` (`InstallationObjectImplementation.cpp:264-270`).
- **Power/maintenance deduction** (`updateMaintenance`, lines 272-328):
  - Calculates elapsed time since last maintenance tick.
  - Deducts maintenance cost proportional to elapsed time: `payAmount = (elapsedTime / 3600.0) × getMaintenanceRate()`.
  - If surplus maintenance is insufficient, limits work time and sets `shutdownWork = true`.
  - Similarly deducts power: `energyAmount = (elapsedTime / 3600.0) × getBasePowerRate()`.
  - If surplus power is insufficient, limits work time and sets `shutdownWork = true`.
- **Harvesting** (`updateHopper`, lines 330-452):
  - If hopper is empty and a current spawn exists, creates a zero-quantity `ResourceContainer` for it (`InstallationObjectImplementation.cpp:348-350`).
  - If `currentSpawn` is null or depleted (`!inShift()`), sets error string `"harvester_resource_depleted"` and shuts down (`InstallationObjectImplementation.cpp:365-368, 374-381`).
  - If no resource selected (no current spawn), sets error string `"harvester_no_resource"` and shuts down (`InstallationObjectImplementation.cpp:369-371`).
  - Calculates harvest amount: `harvestAmount = (elapsedTime / 60.0) × (spawnDensity × getExtractionRate())`, capped by available hopper capacity (`InstallationObjectImplementation.cpp:392-395`).
  - Carries over fractional remainder in `extractionRemainder` (`InstallationObjectImplementation.cpp:400-402`).
  - Extracts from the resource node and updates the container quantity (`InstallationObjectImplementation.cpp:410-415`).
  - Updates `resourceHopperTimestamp` (`InstallationObjectImplementation.cpp:418`).
  - If hopper is full or spawn is expiring, sets `shutdownAfterUpdate = true` and calls `setActive(false)` (`InstallationObjectImplementation.cpp:420-428`).

### Stopping Operation
- When `setActive(false)` is called, the server unsets the `ACTIVATED` option bit, records `lastStopTime`, broadcasts delta messages with operating state false to operators, and clears `resourceHopperTimestamp` (`InstallationObjectImplementation.cpp:118-147`).

### Operator Management
- When a player selects "Operate Machinery", they are added to the operator list via `addOperator(player)` in `synchronizedUIListen` (`HarvesterObjectImplementation.cpp:27`).
- The server sends `HarvesterObjectMessage7` to the player with hopper state and resource container data (`HarvesterObjectImplementation.cpp:31-42`).
- The server activates a synchronized UI task that schedules `SyncrhonizedUiListenInstallationTask` after 5 seconds (`InstallationObjectImplementation.cpp:632-647`).
- Players can stop operating via `synchronizedUIStopListen`, which removes them from the operator list (`HarvesterObjectImplementation.cpp:52-57`).

## 3. What a Bot Test Should Check

### Setup Required
1. Place a harvester deed and construct it on a zone with an active resource node (spawn `"inShift"`) nearby.
2. Ensure the bot character is the owner (on admin list) so radial menu options appear (`HarvesterObjectImplementation.cpp:15-16`).
3. Deposit sufficient credits for power and maintenance into the harvester's surplus reserves (via `handleStructureAddEnergy` or equivalent).

### Observable Results to Verify
- **Radial menu**: Right-clicking the harvester shows item ID 78 with label `"@harvester:manage"` (`HarvesterObjectImplementation.cpp:20`).
- **SUI window**: Selecting item 78 causes the client to receive `ResourceHarvesterActivatePageMessage` (`HarvesterObjectImplementation.cpp:65-66`). The bot should interact with this SUI to select a resource and confirm activation.
- **Activation success**: After confirming in the SUI, the harvester's operating state changes to true. The bot receives `InstallationObjectDeltaMessage3` and `InstallationObjectDeltaMessage7` packets showing operating=true (`InstallationObjectImplementation.cpp:124-147`).
- **System messages on failure**:
  - If power is insufficient: system message with string ID `"player_structure:power_deposit_incomplete"` (`InstallationObjectImplementation.cpp:93`).
  - If maintenance is insufficient: system message with string ID `"shared:harvester_no_maint_4"` (`InstallationObjectImplementation.cpp:101`).
- **Resource in hopper**: After activation, the bot receives `HarvesterObjectMessage7` and `InstallationObjectDeltaMessage7` packets showing the selected resource container in the hopper (`HarvesterObjectImplementation.cpp:31-42`, `InstallationObjectImplementation.cpp:605-610`).
- **Extraction progress**: The hopper quantity for the active resource increases over time. The rate should match `extractionRate × spawnDensity` per minute (`InstallationObjectImplementation.cpp:740, 392`).
- **Hopper full shutdown**: When hopper reaches `hopperSizeMax`, the harvester shuts down and broadcasts `"harvester_resource_depleted"` if the resource is depleted, or stops due to capacity (`InstallationObjectImplementation.cpp:420-428`).
- **Power/maintenance depletion**: When surplus power or maintenance reaches zero, the harvester shuts down and broadcasts `"harvester_no_maint_4"` or the power deposit incomplete message (`InstallationObjectImplementation.cpp:92-105, 365-371`).

### Log/Bot Confirmation Line
A bot can confirm successful operation by checking:
```
System message received: "player_structure:power_deposit_incomplete" → should NOT appear on success
OR
Harvester operating state changed to true (InstallationObjectDeltaMessage3/7 with operating=true)
AND
Hopper contains resource container with quantity > 0 (HarvesterObjectMessage7 or InstallationObjectDeltaMessage7)
AND
Resource quantity in hopper increases over time at expected rate
```

## 4. Likely Reasons a Test Sees No Effect

1. **Resource node not in shift**: If the resource node has been depleted (`!inShift()`), `changeActiveResourceID` rejects it and broadcasts `"harvester_resource_depleted"` (`InstallationObjectImplementation.cpp:525-528, 551-561`). The bot must target an active spawn.
2. **Insufficient surplus power**: If `surplusPower <= 0` and the harvester requires power (`getBasePowerRate() != 0`), activation is refused with `"player_structure:power_deposit_incomplete"` (`InstallationObjectImplementation.cpp:92-97`). The bot must deposit power first.
3. **Insufficient surplus maintenance**: If `surplusMaintenance <= 0` and the harvester requires maintenance (`getMaintenanceRate() != 0`), activation is refused with `"shared:harvester_no_maint_4"` (`InstallationObjectImplementation.cpp:100-105`). The bot must deposit maintenance credits.
4. **Spawn density too low**: If `spawnDensity < 0.10`, activation returns without effect (`InstallationObjectImplementation.cpp:88-90`). This may occur if the resource node is too far away or has low density.
5. **No operator added**: The harvester only sends updates to players in the operator list. If the bot doesn't successfully call `synchronizedUIListen` (by selecting "Operate Machinery" and confirming), it won't receive hopper updates (`HarvesterObjectImplementation.cpp:24-45`).
6. **Hopper already full**: If the hopper is at capacity, the harvester shuts down immediately (`InstallationObjectImplementation.cpp:420-428`). The bot should empty the hopper first.
7. **Resource node despawned**: If the resource node despawns while operating, `updateHopper` detects it and shuts down with `"harvester_resource_depleted"` (`InstallationObjectImplementation.cpp:365-368`).

## 5. Open Questions

1. **SUI window structure**: The files reference `ResourceHarvesterActivatePageMessage` (`HarvesterObjectImplementation.cpp:12, 65`) but do not include its implementation. We don't know what fields it sends to the client or what SUI window type it creates, nor how the client responds (which callback processes the response).
2. **Power/maintenance deposit amounts**: The files show `handleStructureAddEnergy` opens a transfer box for power (`InstallationObjectImplementation.cpp:201-229`) but don't reveal how maintenance deposits are made or what the default/required amounts are.
3. **Extraction rate source**: The base `extractionRate` value is set via `setExtractionRate` (`InstallationObjectImplementation.cpp:743-745`) but we don't know if it comes from the deed template, a config file, or player skill mods.
4. **Hopper size limits**: `hopperSizeMax` is set via `setHopperSizeMax` (`InstallationObjectImplementation.cpp:747-749`) but the source of this value (template, config, or skill) is not in these files.
5. **Skill modifiers**: No evidence of skill-based extraction rate or capacity modifiers in these files. It's unclear if skills like "Resourcefulness" or "Harvester Operation" affect rates.
6. **Maintenance credit deduction mechanism**: The code deducts from `surplusMaintenance` (`InstallationObjectImplementation.cpp:301`) but doesn't show how credits are initially deposited into this surplus or the conversion rate from credits to maintenance units.
7. **Synchronized UI task details**: `SyncrhonizedUiListenInstallationTask` is scheduled after 5 seconds (`InstallationObjectImplementation.cpp:642`) but its implementation is not in these files. We don't know what it does or if it's required for operation.
