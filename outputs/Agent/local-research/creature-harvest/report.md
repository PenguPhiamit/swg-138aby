# Harvesting Mechanics Report

## 1. Short answer
Harvesting a dead creature is performed by a player who is the killer or a group member, within 7 units of the corpse. The player selects a resource type (meat, hide, bone) via the `harvestcorpse` command; the server calculates the amount based on the creature’s maximum resource values, the player’s `creature_harvesting` skill, the local resource density, and any group harvest modifier. The harvested resource is added to the player’s inventory, a system message is sent, and the player gains scout experience. A corpse can be harvested once per player; the server tracks this with `addAlreadyHarvested`.

## 2. How it works
- **Eligibility**: The server calls `CreatureManagerImplementation::harvest` when a player issues the harvest command. The function first checks that the target is a creature corpse (`canHarvestMe`) and that the player is within 7 units (`isInRange`, line 928‑929). The eligibility logic is encapsulated in `canHarvestMe` (not shown) and is assumed to allow the killer or a group member.
- **Range**: 7 units (line 928‑929).
- **Resource selection**: The `selectedID` determines the resource type:
  - `112` picks one of hide, meat, or bone at random, using the creature’s max values (lines 936‑958).
  - `234` forces meat (lines 962‑963).
  - `235` forces hide (lines 964‑965).
  - `236` forces bone (lines 966‑967).
- **Base quantity**: `quantity` is the creature’s max resource amount for the chosen type (lines 940‑956, 962‑970). If the creature has no resource of that type, a system error is sent (lines 972‑975).
- **Skill modifier**: The player’s `creature_harvesting` skill mod (percentage) scales the base quantity (line 976). The result is floored to an integer and capped at a minimum of 3 (lines 976‑978).
- **Resource density**: The server queries the current resource spawn for the type and adjusts the quantity based on density (lines 979‑1002). Density thresholds:
  - >0.75 → ×1.25, quality `creature_quality_fat` (lines 990‑992).
  - >0.50 → ×1.00, quality `creature_quality_medium` (lines 993‑995).
  - >0.25 → ×0.75, quality `creature_quality_scrawny` (lines 996‑998).
  - ≤0.25 → ×0.50, quality `creature_quality_skinny` (lines 999‑1002).
- **Group modifier**: If the player is in a group, the group harvest modifier is applied (lines 1007‑1011). The modifier values are 1.2, 1.3, or 1.4, corresponding to group harvest bonus messages (lines 1030‑1034).
- **Parent check**: If the creature has a parent object, the quantity is forced to 1 (lines 1013‑1015).
- **Harvest transaction**: The server creates a `TransactionLog` (line 1016), calls `harvestResourceToPlayer` to add the resource to the player’s inventory (line 1017), and commits the transaction (line 1018).
- **System messages**: A harvest message is sent with the quantity, resource type, and quality (lines 1021‑1027). If a group bonus applies, an additional message is sent (lines 1030‑1034). If the player is grouped, a group spam message is broadcast to the group (lines 1036‑1047).
- **Experience**: The player receives scout experience equal to `level * 5 + 19` (lines 1051‑1054).
- **Post‑harvest state**: The server records that the player has harvested the corpse (`addAlreadyHarvested`, line 1056) and notifies observers (line 1058). If the corpse has no loot, no credits, and the group cannot harvest it, the corpse is despawned after a delay (lines 1060‑1068).

## 3. What a bot test should check
1. **Setup**:
   - Spawn a creature of a known type (e.g., a `rockmite`) with defined max hide, meat, and bone values.
   - Ensure the creature is dead and the player is the killer or a group member.
   - Place the player within 7 units of the corpse.
   - Set the player’s `creature_harvesting` skill to a known value.
   - Optionally set a group with a known harvest modifier.
2. **Actions**:
   - Issue the `harvestcorpse` command with `selectedID` 112, 234, 235, or 236.
3. **Observables**:
   - System messages: verify the harvest message contains the correct quantity, resource type, and quality string.
   - Group bonus messages if applicable.
   - Group spam broadcast if the player is grouped.
   - Inventory: confirm a new resource container appears with the expected type and quantity.
   - Experience: check the player’s scout experience increased by `level * 5 + 19`.
   - Post‑harvest state: the corpse should no longer be harvestable by the same player (check `addAlreadyHarvested`).
   - If the corpse has no loot or credits, verify that a despawn task is scheduled (observe the despawn delay).

## 4. Likely reasons a test sees no effect
- The player is not within 7 units of the corpse (range check fails, line 928‑929).
- The player does not satisfy `canHarvestMe` (e.g., not the killer and not a group member) (inferred).
- The selected resource type has a max value of 0 for that creature (system error sent, lines 972‑975).
- The resource spawn for the type cannot be found (error message, lines 981‑983).
- The player’s `creature_harvesting` skill is 0, resulting in a quantity less than 3 but still sent; however, the test may not notice the minimum.
- The corpse has already been harvested by the player (`addAlreadyHarvested` check, inferred).
- The test does not wait long enough for the system messages or inventory updates to propagate.

## 5. Open questions
- The implementation of `canHarvestMe` is not shown; its exact criteria (killer vs. group member) remain unknown.
- The function `playerManager->canGroupMemberHarvestCorpse` is referenced but its logic is not visible.
- The handling of multiple harvests by different group members is not explicitly documented in these files.
- The exact mapping of `selectedID` values to in‑game command arguments is not shown.
- The code that triggers `CreatureManagerImplementation::harvest` from a client command is not present.

---
