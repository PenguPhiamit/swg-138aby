# Group Loot Rules Report

## 1. Short Answer

Group loot rules are set by the group leader via `/grouploot` and control who may take items from a corpse. FREEFORALL lets any member loot; MASTERLOOTER restricts looting to one designated player; LOTTERY opens a client-side lottery window for members within 128 units, while RANDOM auto-picks a random eligible member per item. Credits are always split equally among all group members within 128 units of the corpse, with the initial looter receiving a bonus from their `force_luck` skill mod. For a single player not in a group, `/loot` opens the corpse container and `/lootall` transfers everything directly to their inventory.

## 2. How It Works

### Conditions and Setup
- The `/grouploot` command requires the player to be in a group and be the leader (GroupManager.cpp.lines-596-900 lines 36-41, 46-68).
- Changing the loot rule sends an SUI box to non-leader members with options to stay or leave the group (GroupManager.cpp.lines-596-900 lines 638-661).
- The leader receives a system message confirming the new rule (GroupManager.cpp.lines-596-900 lines 632-636).

### FREEFORALL
- Any group member may loot items from the corpse (GroupLootTask.h lines 45-46).
- No special restrictions beyond normal looting requirements.

### MASTERLOOTER
- Only the designated master looter may loot items; others see "Only the Master Looter is allowed to loot!" (GroupLootTask.h lines 47-53).
- The master looter defaults to the group leader when switching to this rule (GroupManager.cpp.lines-596-900 line 607).
- The leader can change the master looter via an SUI list box showing all group members (GroupManager.cpp.lines-596-900 lines 689-722).
- When the master loots all items, the group sees "[GROUP] The master looter has looted all items from the corpse." (GroupLootTask.h lines 106-108).

### LOTTERY
- If other group members are within 128 units of the corpse, a lottery session is created (GroupLootTask.h lines 74-80).
- Members outside 128 units receive "You are too far away from the creature to participate in the lottery." and cannot join (GroupManager.cpp.lines-596-900 lines 787-789).
- If no other members are in range, the corpse acts as FREEFORALL (GroupLootTask.h lines 74-75).
- While the lottery is running, attempting to loot shows "Still waiting for your group members..." (GroupLootTask.h lines 65-68).
- The server blocks theft by setting deny permissions on all items in the corpse's inventory (GroupManager.cpp.lines-596-900 lines 766-777).
- Each eligible member receives an `OpenLotteryWindow` packet to open their client-side lottery window (GroupManager.cpp.lines-596-900 lines 796-797).

### RANDOM
- Eligible members must be within 128 units of the corpse (GroupManager.cpp.lines-596-900 lines 817-827).
- Each item is assigned to a random eligible member using `System::random()` (GroupManager.cpp.lines-596-900 line 847).
- If the winner's inventory is full, they see "Your Inventory is full." and "There was a problem transferring items to your inventory. You may pick them up from the corpse." (GroupManager.cpp.lines-596-900 lines 889-893).
- Items left on the corpse are marked with owner permissions so only that player can take them (GroupManager.cpp.lines-596-900 lines 874-882).
- If the corpse has no items, the player sees "This corpse has no items in its inventory." (GroupLootTask.h lines 84-86).

### Credit Splitting (applies to all rules)
- Credits are split among all group members within 128 units of the corpse (GroupLootTask.h lines 143-153).
- The initial looter receives a bonus: `lootCredits += (lootCredits * force_luck) / 20` (GroupLootTask.h lines 135-138).
- Base share per member = total credits / eligible count, with odd credits distributed randomly (GroupLootTask.h lines 174-186).
- Messages:
  - Looter sees: "You loot %DI credits from %TT." (GroupLootTask.h lines 159-162)
  - Group sees: "[GROUP] %TU looted %DI credits from %TT." (GroupLootTask.h lines 165-169)
  - Each member sees: "[GROUP] You receive %DI credits as your share." or for the looter "[GROUP] You split %TU credits and receive %TT credits as your share." (GroupLootTask.h lines 208-216).

### Single Player Behavior (/loot and /lootall)
- `/loot` checks that the target is a dead AiAgent within 16 units (LootCommand.h lines 52-58).
- If the player owns the corpse or their group owns it, they can loot; otherwise they see "You do not have permission to access this corpse." (LootCommand.h lines 104-109).
- `/loot` opens the corpse container to the player if items remain (LootCommand.h lines 95-97).
- `/lootall` calls `PlayerManagerImplementation::lootAll()` which transfers all credits and items directly to the player's inventory without group splitting (PlayerManagerImplementation.cpp.lines-4241-4306).
- The player sees "You loot %DI credits from %TT." for credits and "You have completely looted the corpse of all items." when done (PlayerManagerImplementation.cpp.lines-4241-4306 lines 4270-4274, 4301).
- LootAllCommand.h is a stub that returns SUCCESS without implementing anything (LootAllCommand.h lines 15-25).

## 3. What a Bot Test Should Check

### Setup Required
- Form a group with multiple bot players.
- Ensure one bot is the group leader.
- Change the loot rule to each type via `/grouploot`.
- Kill a creature that drops items and credits.

### Observable Results to Verify

**For each loot rule:**
- System messages received by each member (confirm correct rule name, master looter notifications).
- Who can successfully loot items (verify permissions).
- Inventory contents after looting (items should be in the correct player's inventory).
- Credit balances after splitting (verify amounts match expected split).

**Range checks:**
- Move one member beyond 128 units and verify they cannot join lottery or receive credits.
- Verify the "too far away" message appears.

**Master Looter specific:**
- Non-master members attempting to loot should see the restriction message.
- Master looter can loot all items.

**Lottery specific:**
- Eligible members should have a lottery window open.
- While lottery is running, non-winners cannot access the corpse.

**Random specific:**
- Items should be distributed to random eligible members.
- Verify winner receives items; others do not.

**Single player (no group):**
- `/loot` opens the corpse container.
- `/lootall` transfers everything directly.
- No credit splitting occurs.

## 4. Likely Reasons a Test Sees No Effect

- Player is not in a group (GroupManager.cpp.lines-596-900 lines 37-41).
- Player is not the group leader when trying to change loot rules (GroupManager.cpp.lines-596-900 lines 46-68).
- Target corpse is out of range (16 units for `/loot`, LootCommand.h line 55).
- Corpse has already been looted or destroyed.
- Master Looter rule prevents non-master players from accessing the corpse (GroupLootTask.h lines 47-53).
- Lottery is still running; members must wait for it to finish (GroupLootTask.h lines 65-68).
- Player's inventory is full, preventing item transfer (GroupManager.cpp.lines-596-900 lines 889-891).

## 5. Open Questions

- **How does the lottery winner get determined?** The server creates a `LootLotterySession` and sends an `OpenLotteryWindow` packet to each eligible member (GroupManager.cpp.lines-596-900 lines 756-798), but the actual lottery calculation appears to happen client-side. The files do not show how the winner is selected or how items are distributed after the lottery finishes.
- **What happens when a lottery finishes?** The server sets deny permissions to prevent theft (GroupManager.cpp.lines-596-900 lines 766-777), but there is no visible code here showing how the winner receives items or how non-winners can access remaining loot.
- **Where is the actual `/lootall` implementation?** `LootAllCommand.h` is a stub that returns SUCCESS without doing anything (LootAllCommand.h lines 15-25). The real behavior comes from passing "all" as an argument to `/loot`, which triggers `LootCommand` to call `playerManager->lootAll()` (LootCommand.h lines 87-88, PlayerManagerImplementation.cpp.lines-4241-4306).
- **What is the exact format of the lottery window?** The server sends an `OpenLotteryWindow` packet (GroupManager.cpp.lines-596-900 line 796), but the client-side UI and interaction model are not described in these files.
