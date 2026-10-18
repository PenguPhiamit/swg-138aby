# Group Mechanics Report (Core3)

## 1. Short Answer

In Core3, a group forms when one player invites another and the target accepts; the inviter becomes leader automatically if no group exists, and groups cap at 20 members (GroupManager.cpp:67, GroupObjectImplementation.cpp:584). Combat XP is distributed to all attackers within 80 feet of the killed creature, with each member receiving a share based on their damage contribution; the server retrieves each attacker's group via `getGroup()` but the full split formula is cut off in the provided excerpt (PlayerManagerImplementation.cpp.lines-1941-2140:2131). Loot depends on the group's loot rule (FREEFORALL, MASTERLOOTER, LOTTERY, or RANDOM), with lottery and random modes requiring members to be within 128 feet of the corpse (GroupManager.cpp:787, GroupManager.cpp:823). The group's calculated level—based on member levels using a weighted formula—affects mission generation via `getGroupLevel()`, though the exact MissionManager usage is not in the provided files.

## 2. How It Works

### Forming a Group (Invite → Accept)

**Invitation checks and messages:**
- Self-invite is rejected: sends system message `@group:invite_no_target_self` (GroupManager.cpp:48).
- If the inviter is already in a group but not the leader, invite is rejected with `@group:must_be_leader` (GroupManager.cpp:62).
- If the target is already in a group, the inviter sees `@group:already_grouped` with the target's displayed name or object ID depending on the `Core3.PlayerManager.GalaxyWideGrouping` config (GroupManager.cpp:77-89).
- If the target already has a pending invite, the inviter sees either `@group:considering_your_group` (if the pending inviter is you) or `@group:considering_other_group` (GroupManager.cpp:94-121).
- On success, the inviter sees `@group:invite_leader` with the target's displayed name (GroupManager.cpp:126-128). The server sets `target->updateGroupInviterID(inviter->getObjectID(), !targetIsPet)` (GroupManager.cpp:131).
- For player targets, the target receives `@group:invite_target` with the inviter's displayed name (GroupManager.cpp:135-137).

**Accepting / joining:**
- The client sends an accept command; the server calls `joinGroup(creature)` (GroupManager.cpp:161).
- If the inviter has no group, a new group is created via `createGroup(leader, creature)` (GroupManager.cpp:200).
  - A GroupObject is created with object ID `0x13dcb432` (GroupManager.cpp:292).
  - Leader and first member are initialized; chat room is started for the leader (GroupManager.cpp:306, GroupManager.cpp:313).
  - Baselines are sent to both (GroupManager.cpp:316, GroupManager.cpp:333).
  - Leader sees `@group:formed_self`; new member sees `@group:joined_self` (GroupManager.cpp:324, GroupManager.cpp:336).
  - A `GroupObjectDeltaMessage6` with `initialUpdate()` is broadcast to all group members (GroupManager.cpp:359-366).
- If the inviter already has a group and is the leader, the new member is added via `group->addMember(creature)` (GroupManager.cpp:235).
  - The member sees `@group:joined_self` (GroupManager.cpp:242).
  - If loot rule is MASTERLOOTER, the member also sees a message identifying the master looter (GroupManager.cpp:245-249).
  - The member is added to the group chat room (GroupManager.cpp:258-264).
  - A `GroupObjectDeltaMessage6` with `updateMembers()` is broadcast (GroupObjectImplementation.cpp:171-178).
- If the group is full (≥20 members), the joining player sees "The group is full." and their inviter ID is cleared (GroupManager.cpp:210-215).
- If the inviter is in the group but not the leader, the joiner sees `@group:prose_leader_changed` ("%TU has abdicated group leadership to %TT.") and the join fails (GroupManager.cpp:218-228).

**Group size limit:** 20 members total (GroupManager.cpp:67, GroupManager.cpp:210).

### Combat Experience Split

- XP distribution happens in `PlayerManagerImplementation::disseminateExperience` (PlayerManagerImplementation.cpp.lines-1941-2140:1941).
- Only attackers within 80 feet of the destructed object receive XP: `destructedObject->isInRangeZoneless(attacker, 80)` (PlayerManagerImplementation.cpp.lines-1941-2140:2121).
- For each attacker in the threat map, the server retrieves their group via `attackerCreo->getGroup()` (PlayerManagerImplementation.cpp.lines-1941-2140:2131). The full split formula is not visible in the provided excerpt (file ends at line 2140).
- Pet owners with `outdoors_creaturehandler_novice` within 80 feet receive creaturehandler XP calculated as `levelRatio * 500.f`, capped at `attacker->getLevel() * 50.f`, divided by total active creature pets (PlayerManagerImplementation.cpp.lines-1941-2140:2103-2119).
- GCW bonus is applied if the winning faction matches the attacker's faction (PlayerManagerImplementation.cpp.lines-1941-2140:2113-2114).

### Loot Rules

The group has one of four loot rules, set by the leader via radial menu or SUI:

- **FREEFORALL**: Default rule; all members can loot freely (GroupManager.cpp:612).
- **MASTERLOOTER**: Leader designates a master looter; only that player can distribute items (GroupManager.cpp:615, GroupManager.cpp:664).
  - Leader sees a SuiListBox (`GROUP_LOOT_PICK_LOOTER`) with member names and object IDs to choose from (GroupManager.cpp:704-721).
  - When changed, non-leader members receive an SUI box titled `@group:loot_changed` with prompt text for the selected rule and buttons "@group:ok" / "@group:leave_group" (GroupManager.cpp:652-661).
  - Leader receives a system message confirming the change (GroupManager.cpp:633-636).
  - All members are notified of the new master looter via `@group:new_master_looter` or `@group:set_new_master_looter` (GroupManager.cpp:731-745).
- **LOTTERY**: Server creates a `LootLotterySession`; only members within 128 feet of the corpse are eligible (GroupManager.cpp:787). Eligible members receive an `OpenLotteryWindow` packet (GroupManager.cpp:796-797). Members too far away see "You are too far away from the creature to participate in the lottery." (GroupManager.cpp:788-789).
- **RANDOM**: Server picks a random eligible member within 128 feet for each item and transfers it via `transferLoot` (GroupManager.cpp:801, GroupManager.cpp:847, GroupManager.cpp:854).

**Loot transfer:** When transferring to a winner, the server sets the item's owner permission and denies other players from opening/moving it if left on the corpse (GroupManager.cpp:874-882). If the winner's inventory is full, they receive "Your Inventory is full." and "There was a problem transferring items to your inventory. You may pick them up from the corpse." (GroupManager.cpp:890-893).

### Group Level Calculation

- `calculateGroupLevel()` iterates all group members (GroupObjectImplementation.cpp:584).
- For player creatures, it tracks the highest player level seen so far (`highestPlayer`):
  - If a member's level exceeds `highestPlayer`: adds `(memberLevel - highestPlayer + highestPlayer / 5.f)` to `newLevel`, then sets `highestPlayer = memberLevel` (GroupObjectImplementation.cpp:607-609).
  - Otherwise: adds `memberLevel / 5.f` to `newLevel` (GroupObjectImplementation.cpp:611).
- For pets: adds `memberLevel / 5.f` to `newLevel` (GroupObjectImplementation.cpp:605).
- Final group level is `round(newLevel)` (GroupObjectImplementation.cpp:624).
- The group level is recalculated whenever a member is added or removed (GroupObjectImplementation.cpp:167, GroupObjectImplementation.cpp:260).

### Squad Leader Buffs

- If the group leader has the skill `outdoors_squadleader_novice`, all members receive a "squadleader" buff with 300-second duration (GroupObjectImplementation.cpp:439, GroupObjectImplementation.cpp:486).
- The buff applies skill modifiers from the leader: `slope_move`, `private_group_ranged_defense`, `private_group_melee_defense`, `burst_run` (GroupObjectImplementation.cpp:497-501).

### Mission Updates

- When a member joins or leaves, the server schedules an `UpdateNearestMissionForGroupTask` on a 10-second delay (GroupObjectImplementation.cpp:161, GroupObjectImplementation.cpp:254, GroupObjectImplementation.cpp:741-762).
- The task updates waypoints with special type `SPECIALTYPE_NEARESTMISSIONFORGROUP` for all members (GroupObjectImplementation.cpp:236, GroupObjectImplementation.cpp:412).

## 3. What a Bot Test Should Check

**Setup:**
- Ensure the bot character has no existing group (`getGroup() == nullptr`).
- Have a second test character available to invite.

**Invite flow checks:**
1. Send invite command to target. Verify:
   - Inviter receives system message `@group:invite_leader` with target name (GroupManager.cpp:126-128).
   - Target receives system message `@group:invite_target` with inviter name (GroupManager.cpp:135-137).
   - Target's `getGroupInviterID()` equals inviter's object ID (GroupManager.cpp:131).

2. Send accept command from target. Verify:
   - If no prior group exists: leader sees `@group:formed_self` (GroupManager.cpp:324), new member sees `@group:joined_self` (GroupManager.cpp:336).
   - A GroupObject with ID `0x13dcb432` is created and both characters' `getGroup()` returns it (GroupManager.cpp:292, GroupManager.cpp:368-369).
   - Both receive a `GroupObjectDeltaMessage6` with initial update (GroupManager.cpp:359-366).
   - If group already existed and inviter was leader: new member sees `@group:joined_self` (GroupManager.cpp:242) and receives a `GroupObjectDeltaMessage6` with `updateMembers()` (GroupObjectImplementation.cpp:171-178).

3. Test rejection cases:
   - Invite self: inviter sees `@group:invite_no_target_self` (GroupManager.cpp:48).
   - Invite when not leader: non-leader sees `@group:must_be_leader` (GroupManager.cpp:62).
   - Invite already-grouped target: inviter sees `@group:already_grouped` (GroupManager.cpp:77-89).
   - Invite when group is full (≥20): joining player sees "The group is full." (GroupManager.cpp:213).

**XP checks:**
- Kill a creature while in a group with another player who also damaged it.
- Verify both characters receive XP and that the server checked `isInRangeZoneless(attacker, 80)` before distributing (PlayerManagerImplementation.cpp.lines-1941-2140:2121).
- Verify pet owners with `outdoors_creaturehandler_novice` within 80 feet receive creaturehandler XP (PlayerManagerImplementation.cpp.lines-1941-2140:2073, PlayerManagerImplementation.cpp.lines-1941-2140:2119).

**Loot checks:**
- Set loot rule to LOTTERY via radial menu/SUI. Kill a creature. Verify eligible members (within 128 feet) receive an `OpenLotteryWindow` packet (GroupManager.cpp:796-797), and those outside 128 feet see "You are too far away from the creature to participate in the lottery." (GroupManager.cpp:788-789).
- Set loot rule to MASTERLOOTER. Verify leader receives a SuiListBox (`GROUP_LOOT_PICK_LOOTER`) with member names and object IDs (GroupManager.cpp:704-721). Non-leader members receive an SUI box titled `@group:loot_changed` (GroupManager.cpp:652-661).
- Verify loot transfer sets item owner permission and denies other players from opening/moving it on the corpse (GroupManager.cpp:874-882).

**Group level checks:**
- Add members of different levels to a group. After each addition, verify `getGroupLevel()` reflects the weighted calculation (GroupObjectImplementation.cpp:607-612, GroupObjectImplementation.cpp:624).
- Verify group level is recalculated on member removal (GroupObjectImplementation.cpp:260).

**Squad Leader checks:**
- Give the leader the skill `outdoors_squadleader_novice`. Verify all members receive a "squadleader" buff with modifiers for `slope_move`, `private_group_ranged_defense`, `private_group_melee_defense`, and `burst_run` (GroupObjectImplementation.cpp:439, GroupObjectImplementation.cpp:497-501).

## 4. Likely Reasons a Test Sees No Effect

- **Distance:** XP requires attackers within 80 feet of the corpse (PlayerManagerImplementation.cpp.lines-1941-2140:2121); lottery loot requires members within 128 feet (GroupManager.cpp:787, GroupManager.cpp:823). Bots standing too far will see no XP or lottery window.
- **Not in threat map:** If the bot did not deal damage to the creature, it will not appear in the threat map and receives no XP share.
- **Group full:** Groups cap at 20 members (GroupManager.cpp:67, GroupManager.cpp:210). A join attempt on a full group silently fails with "The group is full."
- **Inviter not leader:** If the inviter is not the group leader, invites are rejected with `@group:must_be_leader` (GroupManager.cpp:62), and joins from non-leader inviters fail with `@group:prose_leader_changed` (GroupManager.cpp:218-228).
- **Target already grouped:** Inviting a player who is already in a group sends `@group:already_grouped` and does nothing (GroupManager.cpp:77-89).
- **Loot rule not set:** If the loot rule is FREEFORALL (default), no lottery or master looter UI appears; all members can simply take items.
- **Inventory full:** When loot transfer fails due to a full inventory, the winner sees "Your Inventory is full." and must manually pick up items from the corpse (GroupManager.cpp:890-893).
- **Missing skill for squad buffs:** The leader must have `outdoors_squadleader_novice` for buffs to apply (GroupObjectImplementation.cpp:439). Without it, no buff is added.
- **Pet type restrictions:** Only creature pets (`PetManager::CREATUREPET`) award creaturehandler XP; other pet types are skipped (PlayerManagerImplementation.cpp.lines-1941-2140:2059).

## 5. Open Questions

- **Full XP split formula:** The provided excerpt of `PlayerManagerImplementation.cpp` ends at line 2140, cutting off before the actual group XP distribution logic. The file `MissionManagerImplementation.cpp` (referenced in the task as using `getGroupLevel()` around line 1912) is not included in the provided files, so the exact relationship between group level and mission generation cannot be determined from these sources.
- **GalaxyWideGrouping config behavior:** The code checks `ConfigManager::instance()->getBool("Core3.PlayerManager.GalaxyWideGrouping", false)` to decide whether to use displayed names or object IDs in messages (GroupManager.cpp:45, GroupManager.cpp:80-84, GroupManager.cpp:98-102, GroupManager.cpp:112-116, GroupObjectImplementation.cpp:371-377). The actual config file value is not provided.
- **Loot lottery resolution:** The code creates a `LootLotterySession` and adds eligible players (GroupManager.cpp:756-793), but the selection algorithm and how the winner is determined are in the separate `LootLotterySession` class, which is not included.
- **Random loot distribution details:** While `doRandomLoot` picks a random candidate per item (GroupManager.cpp:847), the exact probability weighting or tie-breaking behavior is unclear from this excerpt alone.
- **Group chat room lifecycle:** The code creates and destroys chat rooms for groups (GroupObjectImplementation.cpp:45-68, GroupManager.cpp:390-402), but the exact conditions for room destruction beyond group disband are not fully detailed.
