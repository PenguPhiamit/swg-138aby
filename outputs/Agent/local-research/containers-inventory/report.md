# Report: Inventory and Container Limits (SWGEmu Core3, pre-CU)

## 1. Short Answer

A player's inventory is a volume container that limits items by counting entries in its internal map (`containerObjects->size()`) against a value returned by `getContainerVolumeLimit()` (ContainerComponent.cpp:146). When the limit is reached, `canAddObject` returns `CONTAINERFULL` and sets the message key `"@container_error_message:container03"` ("This container is full.") (ContainerComponent.cpp:147-148). The transfer command sends this message to the player via `sendSystemMessage` (TransferItemMiscCommand.h:297). Loot or rewards do not bypass this limit—`transferObject` only ignores it if its `allowOverflow` parameter is true, which the normal transfer path does not set. To check space before transferring, a test should call `canAddObject` on the destination container; to make room, it must remove items first using `removeObject` or equivalent.

## 2. How It Works

### Conditions and flow
- **Entry point**: The client command `TransferItemMiscCommand` parses arguments (destination ID, transfer type) and calls `doTransferItemMisc` (TransferItemMiscCommand.h:105).
- **Permission checks**: Before touching limits, the command verifies the player can move the source object out of its current parent (`MOVEOUT`, TransferItemMiscCommand.h:150) and into the destination (`MOVEIN`, TransferItemMiscCommand.h:335), using `checkContainerPermission` (ContainerComponent.cpp:160).
- **Limit check**: The command calls `destinationObject->canAddObject(objectToTransfer, transferType, errorDescription)` (TransferItemMiscCommand.h:295). If the return value is non-zero, the transfer is refused.

### Container types and what counts
- `ContainerType::VOLUME` (value 2) allows tangible items in any free slot; this is the inventory type (ContainerComponent.h:34-35).
- For volume containers (`containmentType == -1`), the limit check compares `containerObjects->size()` against `sceneObject->getContainerVolumeLimit()` (ContainerComponent.cpp:146). The size counts every object currently stored in the container's `VectorMap<uint64, SceneObject*>`.
- For slotted containers (`containmentType >= 4`), no item-count limit is enforced; instead each slot descriptor is checked for occupancy (ContainerComponent.cpp:130-144).

### Skill mods and numbers
- The player-specific `PlayerContainerComponent::canAddObject` adds wearable checks (race, faction, encumbrance, required skills) but delegates to `ContainerComponent::canAddObject` for the actual container limit (PlayerContainerComponent.cpp:114).
- The exact numeric value of `getContainerVolumeLimit()` is **not defined in these files**; it comes from `SceneObject` (or a subclass), so the default inventory capacity cannot be determined from this source alone.

### Timings
1. Command parses arguments and resolves objects (TransferItemMiscCommand.h:55-79).
2. Permission checks on source and destination (TransferItemMiscCommand.h:132-153, 330-338).
3. `canAddObject` evaluates the limit (TransferItemMiscCommand.h:295; ContainerComponent.cpp:146).
4. If allowed, `objectController->transferObject` moves the object (TransferItemMiscCommand.h:359). Inside `transferObject`, a second overflow check exists but is bypassed when `allowOverflow` is false and the container is full—however this branch returns `false` silently without setting an error message (ContainerComponent.cpp:304-305). The user-visible rejection always comes from step 3.

### Messages the player sees
- **Container full**: `"@container_error_message:container03"` ("This container is full.") set in `canAddObject` (ContainerComponent.cpp:147) and sent via `creature->sendSystemMessage(errorDescription)` (TransferItemMiscCommand.h:297).
- **Permission denied**: `"@error_message:perm_no_move"` when the player lacks `MOVECONTAINER`, `MOVEOUT`, or `MOVEIN` permissions (TransferItemMiscCommand.h:133, 175).
- **Slot occupied**: `"@container_error_message:container04"` ("This slot is already occupied.") for slotted containers (ContainerComponent.cpp:140).
- **Cannot add to itself**: `"@container_error_message:container02"` (ContainerComponent.cpp:16).

## 3. What a Bot Test Should Check

### Setup needed first
- Ensure the creature has a valid zone and parent hierarchy (the command requires `zoneServer` and resolves objects by ID; TransferItemMiscCommand.h:43-79).
- Confirm the destination container is reachable within the distance limit (`maxDistance = 16.5`) unless it is a building or cell object (TransferItemMiscCommand.h:195-285).
- If testing wearable items, verify the creature's race/faction and skill list match the item's requirements (PlayerContainerComponent.cpp:32-91).

### Observable results to verify
- **System message**: After a failed transfer to a full inventory, the creature should receive `"@container_error_message:container03"` via `sendSystemMessage` (TransferItemMiscCommand.h:297).
- **Inventory state**: Before the attempt, call `canAddObject` on the inventory with `containmentType = -1`. A return value of `TransferErrorCode::CONTAINERFULL` confirms the limit is reached; a return of `0` means space exists.
- **Container size**: Query `sceneObject->getContainerObjects()->size()` and compare to `sceneObject->getContainerVolumeLimit()` to compute remaining slots (ContainerComponent.cpp:146).
- **Slotted containers**: For equipment slots (`containmentType >= 4`), verify `canAddObject` returns `SLOTOCCUPIED` when the slot descriptor is already taken (ContainerComponent.cpp:140-141).

### Making room or checking space
- **Check first**: Call `destination->canAddObject(item, -1, errorDesc)` before attempting transfer. If it returns non-zero, do not proceed.
- **Make room**: Use `removeObject` on the destination container to free slots, or move items to another container (e.g., bank). The test should re-check `canAddObject` after removals.

## 4. Likely Reasons a Test Sees No Effect

- **Distance exceeded**: If the object's root parent or the destination is more than 16.5 meters from the creature and neither is a building/cell, the command returns `TOOFAR` before reaching the container check (TransferItemMiscCommand.h:202, 217, 237, 274).
- **Permission denied**: The player may lack `MOVEOUT` on the source or `MOVEIN` on the destination, causing an early abort with `"@error_message:perm_no_move"` (TransferItemMiscCommand.h:150-153, 335-338).
- **Wrong containment type**: Passing a slotted `containmentType` to a volume-only container (or vice versa) triggers a validation error and the generic `"@container_error_message:container28"` message (ContainerComponent.cpp:70-99).
- **NoTrade / building ownership**: Items marked no-trade or owned by another player's building are blocked with `container27` or `container28` (ContainerComponent.cpp:41, 49).
- **Inventory limit not the real cause**: The test may assume a full inventory but actually hit one of the above checks first. Always inspect the returned error code and the `errorDescription` string from `canAddObject`.

## 5. Open Questions

- **Default inventory capacity**: `getContainerVolumeLimit()` is called at ContainerComponent.cpp:146, but its implementation is not in any of the provided files. The default value for a player creature's inventory is unknown without the `SceneObject` or `CreatureObject` source.
- **Loot / reward overflow behavior**: The `allowOverflow` parameter exists in `transferObject` (ContainerComponent.h:53) and is checked at ContainerComponent.cpp:304, but none of these files show where it is set to `true`. It is unclear whether loot drops or quest rewards use `allowOverflow = true` to bypass the limit.
- **Nested container limits**: The code checks that no ancestor has `ContainerType::NONE` (ContainerComponent.cpp:104-111), but there is no logic here for propagating a parent container's item count into a child container's limit. Whether nested containers share or inherit limits is not answered by these files.
- **Exact error code enum**: The file `TransferErrorCode.h` is included (ContainerComponent.cpp:18) but not provided; the numeric values of `CONTAINERFULL`, `SLOTOCCUPIED`, etc., are unknown.
- **Encumbrance interaction**: `PlayerContainerComponent::canAddObject` calls `checkEncumbrancies` for armor (PlayerContainerComponent.cpp:63), which may impose additional restrictions beyond the item-count limit, but the encumbrance calculation logic is not in these files.

## ChatGPT's review (2026-10-18 22:32)

Checked Saluki disputed leads and matching snapshots against Core3-dev 9d08e265. Source only.

**Holds:** generic immediate-child volume limit, containment-type validation, occupied equipment slots and error forwarding (ContainerComponent.cpp:66-149; TransferItemMiscCommand.h:292-307). Saluki incorrectly rejects container03 merely because the caller forwards errorDescription: the callee sets that exact value at 147. container28 is likewise set after validationError at 114-122, and maxDistance really is 16.5 (TransferItemMiscCommand.h:195).

**Corrections:**
- MOVEOUT/MOVEIN failures at TransferItemMiscCommand.h:150-153,335-338 log/abort without sending perm_no_move. That message is explicit for MOVECONTAINER at 132-135. Saluki is right to distinguish these.
- Destination MOVEIN is checked **after canAddObject**, not before all limit checks (295 versus335). No universal permission-first ordering follows.
- transferObject's !allowOverflow && full branch enforces the limit and returns false; it does not bypass it (ContainerComponent.cpp:303-305). canAddObject and direct transfer are distinct layers.
- These files establish the generic local container check, not an absolute guarantee that every loot/reward caller forbids overflow or that recursive inventory checks are absent elsewhere. The short answer's universal no-bypass claim exceeds the evidence and conflicts with its own open question. Trace each reward caller and check its return value.
- Range has root/building/ship/cell-dependent branches, not just a single destination-distance rule (TransferItemMiscCommand.h:190-285). Equipment validation delegates to the generic layer (PlayerContainerComponent.cpp:114); those player slots are not the same object as the volume inventory.
- C++ canAddObject/removeObject are server APIs, not demonstrated bot control methods. Moving items through normal authorized commands should verify both old/new containment; raw removeObject is not an adequate end-to-end inventory test.

Verdict: Generic capacity/error mechanism holds; correct permission order/messages and overflow wording, and reject universal reward/nesting conclusions; gameplay untested.
