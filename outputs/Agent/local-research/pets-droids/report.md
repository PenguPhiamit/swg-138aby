# Pet and Droid Mechanics Report (Core3 / Pre-CU)

## 1. Short Answer

In Core3, a player calls a pet by selecting radial menu option **44** on the PetControlDevice; the server checks combat, dead/taming state, private buildings, FRS enclave, cooldowns, and skill limits before spawning the pet at the player's position ±2-3 m random offset. The pet automatically follows the owner (setFollowObject) with no configurable follow distance exposed in these files—distance is enforced client-side by the AI movement code, which is not present here. Storing uses radial option **59** or the "store" command, triggering PetControlDeviceStoreTask; faction pets delay 60 s unless forced. The bot test failure (pet 12.0 m from owner after leash) likely stems from client-side pathfinding/leash tolerance rather than server state—the server only records that the pet should follow, not a hard distance cap.

## 2. How It Works

### Calling a Pet

**Radial trigger:** `PetControlDeviceImplementation.cpp:347-365` — selectedID == 44 queues `callObject()` in a task.

**Preconditions checked (all early-return with system messages):**

| Check | File:Line | Message / Result |
|-------|-----------|------------------|
| Player dead or taming | `PetControlDeviceImplementation.cpp:43-46` | `"@pet/pet_menu:cant_call"` — "You cannot call this pet right now." |
| Private building | `PetControlDeviceImplementation.cpp:57-60` | `"@pet/pet_menu:private_house"` — "You cannot call pets in a private building." |
| FRS enclave | `PetControlDeviceImplementation.cpp:73-76` | `"@pet/pet_menu:cant_call"` |
| Pet not AI agent | `PetControlDeviceImplementation.cpp:80-82` | Silent return |
| Already active pet | `PetControlDeviceImplementation.cpp:92-94` | Silent return |
| Missing default weapon | `PetControlDeviceImplementation.cpp:96-101` | "This pet does not have a proper default weapon, attempting to create one. Please call your pet again." |
| Dead pet (vitality ≤ 0) | `PetControlDeviceImplementation.cpp:104-107` | `"@pet/pet_menu:dead_pet"` — "This pet is dead..." |
| Call cooldown on pet | `PetControlDeviceImplementation.cpp:109-115` | Droid: `"@pet/droid_modules:droid_maint_on_maint_run"`; Creature: `"@pet/pet_menu:cant_call"` |
| No-pet active area | `PetControlDeviceImplementation.cpp:135-138` | `"@pet/pet_menu:cant_call"` |
| Combat/incap (non-bomb droid) | `PetControlDeviceImplementation.cpp:143-146` | `"@pet/pet_menu:cant_call"` |
| Mounted (non-bomb droid, non-initial) | `PetControlDeviceImplementation.cpp:149-152` | `"@pet/pet_menu:mounted_call_warning"` — "You cannot call a pet while mounted or riding a vehicle." |
| Faction mismatch | `PetControlDeviceImplementation.cpp:156-181` | `"@faction_perk:prose_be_declared"` or `"@faction_perk:prose_be_declared_faction"` |
| Already calling (pending task) | `PetControlDeviceImplementation.cpp:183-192` | `"pet/pet_menu:call_delay_finish_pet"` — "Already calling a Pet: Call will be finished in %DI seconds." |
| Invalid creature template | `PetControlDeviceImplementation.cpp:218-221` | "Invalid creature to spawn!" |
| Control level exceeded | `PetControlDeviceImplementation.cpp:236-239, 267-270` | `"@pet/pet_menu:control_exceeded"` — "Calling this pet would exceed your Control Level ability." |
| Lack tame_aggro skill for vicious | `PetControlDeviceImplementation.cpp:241-244` | `"@pet/pet_menu:lack_skill"` — "You lack the skill to call a pet of this type." |
| Max pets reached | `PetControlDeviceImplementation.cpp:260-263, 272-275, 283-286, 288-291` | `"@pet/pet_menu:at_max"` — "You already have the maximum number of pets of this type that you can call." |
| Trade session active | `PetControlDeviceImplementation.cpp:297-301` | Trade aborted silently |

**Timing:**
- **In city/camp or bomb droid from deed:** immediate spawn, then 1 s cooldown (`PetControlDeviceImplementation.cpp:318-329`).
- **Otherwise (outdoors, non-bomb):** 15 s delay task `CallPetTask` with message `"pet/pet_menu:call_pet_delay"` — "Calling pet in %DI seconds. Combat will terminate pet call." (`PetControlDeviceImplementation.cpp:303-315`). Combat start cancels via `PetControlObserver` (`PetControlDeviceImplementation.cpp:317, 460, 543-545`).

**Spawn:**
- Position: player X/Z ± random(5) − 2 → range [−2, +3] m offset (`PetControlDeviceImplementation.cpp:416`).
- Pet set to follow owner: `setFollowObject(player)` (`PetControlDeviceImplementation.cpp:507`).
- Last command set to FOLLOW (`PetControlDeviceImplementation.cpp:532`).
- For droids: power/skill mod tasks scheduled (120 s / 3 s) (`PetControlDeviceImplementation.cpp:484-488`).

### Making Pet Follow, Stay, Guard

**Radial menu:** The pet's radial menu (ObjectMenuComponent "PetMenuComponent" set at `PetControlDeviceImplementation.cpp:425`) contains commands like follow, stay, guard, attack. Selecting one sends a queue command.

**Command routing:** `PetManagerImplementation.cpp:162-282` — `handleChat()` maps trained command strings to hash codes and enqueues them via `EnqueuePetCommand`. Chat commands also work (e.g., "pet follow", "pet stay").

**Follow command specifics:** `PetFollowCommand.h:17-116`
- Validates control device, pet, target.
- Checks droid power (`PetFollowCommand.h:82-85`).
- If target is not player and is attackable/dead/no LOS, falls back to player as target (`PetFollowCommand.h:92-95`).
- Sets follow object: `pet->setFollowObject(targetCreature)` and `pet->storeFollowObject()` (`PetFollowCommand.h:106-107`).
- If pet resting, sets movement state to FOLLOWING (`PetFollowCommand.h:109-111`).

**Stay/Guard:** Enqueued via `PetManagerImplementation.cpp:220, 228` with hash codes `STRING_HASHCODE("petstay")` and `STRING_HASHCODE("petguard")`. The actual stay/guard distance logic is **not in these files**.

### Storing a Pet

**Radial trigger:** selectedID == 59 (`PetControlDeviceImplementation.cpp:366-392`). If pet not active (status == 1), calls `callObject()` (re-call); otherwise creates `PetControlDeviceStoreTask`.

**Command trigger:** `PetStoreCommand.h:14-37` — validates control device and pet, then executes `PetControlDeviceStoreTask`.

**Store logic:** `PetControlDeviceImplementation.cpp:547-624`
- Checks combat/dead (unless force) (`PetControlDeviceImplementation.cpp:558-561`).
- 1 s cooldown (`PetControlDeviceImplementation.cpp:564-567, 586`).
- Dismounts player if riding pet (`PetControlDeviceImplementation.cpp:574-583`).
- Clears training commands and friends list (`PetControlDeviceImplementation.cpp:592-595`).
- **Faction pets:** 60 s delay with message "Storing pet in 60 seconds" or "Pet will store in %DI seconds." (`PetControlDeviceImplementation.cpp:608-623`).
- **Non-faction/forced:** immediate execute (`PetControlDeviceImplementation.cpp:606-607`).

**Observable results of store:** Pet disappears from world, returns to PetControlDevice (intangible) in player's inventory/datapad. System message on successful store is not in these files (likely in `PetControlDeviceStoreTask` which is not provided).

### Follow Distance and Leash

**What these files show:**
- The server sets the follow target (`setFollowObject`) but **does not enforce a distance**.
- No follow-distance constant, leash radius, or catch-up threshold appears in any of the four files.
- Pet spawns within ~5 m of player (`PetControlDeviceImplementation.cpp:416`).

**What is missing:** The AI movement code (likely `AiAgent.cpp` or `Creature.cpp`) that implements:
- Desired follow distance (varies by pet type, skill mods?)
- Leash radius (max distance before forced return)
- Catch-up speed/behavior when pet exceeds leash
- Client-side pathfinding delays

**Why the test saw 12.0 m:** The server considers the pet "following" as long as `setFollowObject` is set and the AI agent hasn't been commanded otherwise. The client's AI movement code determines when to stop or catch up. A 12 m gap suggests either:
1. The client's leash tolerance is ≥12 m for this pet type.
2. Pathfinding obstacles prevented immediate catch-up.
3. The test stopped checking before the client finished moving the pet closer.

The server does **not** send a "pet is too far" message or forcibly teleport the pet in these files.

## 3. What a Bot Test Should Check

### Setup Required
1. Player with `outdoors_creaturehandler_novice` (or god mode) to call creature pets.
2. A valid PetControlDevice (creature or droid type) in player inventory.
3. Player not in combat, not dead, not taming, not in private building/FRS enclave.
4. For creature pets: sufficient `tame_level` skill mod for pet's adult level.

### Step-by-Step Bot Actions and Expected Results

| Step | Client Action | Server Response / Observable Result |
|------|--------------|-------------------------------------|
| 1 | Radial menu on PetControlDevice → select call (ID 44) | If outdoors: system msg "Calling pet in 15 seconds. Combat will terminate pet call." + 15 s delay. If in city/camp: immediate spawn. |
| 2 | Wait for spawn (or skip if city) | Pet appears at player position ±2-3 m. Pet faces owner (`PetControlDeviceImplementation.cpp:528`). Pet has default weapon. Ghost has active pet (`ghost->addToActivePets` at `PetControlDeviceImplementation.cpp:468`). |
| 3 | Radial menu on pet → select follow (or chat "pet follow") | Pet sets movement state to FOLLOWING if was resting. No system message expected. |
| 4 | Move away from pet | Pet follows. **Check:** distance at various intervals. Note: no server-side distance enforcement visible in these files. |
| 5 | Radial menu on pet → select stay (or chat "pet stay") | Pet stops moving. No system message expected in these files. |
| 6 | Radial menu on pet → select guard (or chat "pet guard") | Pet guards target (player if none specified). No system message expected. |
| 7 | Radial menu on PetControlDevice → select store (ID 59) or chat "pet store" | Pet disappears from world, reappears in PetControlDevice. For faction pets: "Storing pet in 60 seconds" then stores. System message on completion not in these files. |

### Key Assertions for Bot
- After call: `ghost->hasActivePet(pet)` returns true (`PetControlDeviceImplementation.cpp:92`).
- After store: pet is no longer active, PetControlDevice contains pet again.
- Cooldowns: 1 s after call/store (`PetControlDeviceImplementation.cpp:328, 586`); pet-specific call cooldown (`PetControlDeviceImplementation.cpp:109`).
- Skill checks: `tame_level` limits max pet level; `tame_aggro` required for vicious pets (`PetControlDeviceImplementation.cpp:233, 241`).

## 4. Likely Reasons a Test Sees No Effect

1. **Missing prerequisites:** Player lacks `outdoors_creaturehandler_novice` → cannot call creature pets or issue follow/attack/guard commands (skill checks at `PetControlDeviceImplementation.cpp:229-244, PetControlDeviceImplementation.cpp:1298-1313`).
2. **Combat state:** Player in combat prevents calling non-bomb droids (`PetControlDeviceImplementation.cpp:143-146`) and storing (`PetControlDeviceImplementation.cpp:560`).
3. **Cooldown:** 1 s cooldown on call/store (`PetControlDeviceImplementation.cpp:320-323, 564-567`) causes immediate re-attempt to fail with `"@pet/pet_menu:cant_call_1sec"` or `"@pet/pet_menu:cant_store_1sec"`.
4. **Private building/FRS enclave:** Prevents calling (`PetControlDeviceImplementation.cpp:57-60, 73-76`).
5. **Max pets reached:** Exceeds `keep_creature` skill mod limit or level cap (`tame_level`) → `"@pet/pet_menu:at_max"` or `"@pet/pet_menu:control_exceeded"`.
6. **Droid without power:** Bomb droids and other droids require power; low power shows flytext "*Low Power*" (`PetFollowCommand.h:82-85`).
7. **Pending call task:** If already calling, message "Already calling a Pet: Call will be finished in %DI seconds." prevents duplicate (`PetControlDeviceImplementation.cpp:183-192`).

## 5. Open Questions

These files do **not** answer:

1. **What is the server-side follow distance or leash radius?** No constant, config value, or skill mod for follow distance appears in any provided file. This logic must be in `AiAgent.cpp`, `Creature.cpp`, or a movement/leash manager not included here.
2. **How does catch-up work when pet exceeds leash?** The server sets `setFollowObject` but does not enforce distance; client AI handles movement speed and pathfinding.
3. **What system messages confirm successful follow/stay/guard?** None appear in these files. Messages may be client-side or in a separate UI manager.
4. **What is the exact radial menu structure for pets?** The pet's radial menu uses "PetMenuComponent" (`PetControlDeviceImplementation.cpp:425`) but the menu definitions (command IDs, strings) are not in these files.
5. **How does PetControlDeviceStoreTask complete the store?** The task class is referenced (`PetControlDeviceImplementation.cpp:600, 386`) but its implementation is not provided.
6. **What determines the 12 m gap in the test?** Without the AI movement code, it is impossible to determine whether this is expected leash tolerance, pathfinding delay, or a bug.

**Missing files needed for complete answer:** `AiAgent.cpp` (or equivalent AI movement file), `Creature.cpp` movement logic, `PetControlDeviceStoreTask.cpp`, radial menu definition files, and any config/datatable files for follow distance constants.
