# Local model: test-index (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 56 input lines. A local model's draft: check each item before acting on it.

Steps drafted from section 3 of each research report. Check a step against its report before a scenario uses it.

## badges

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Award a badge using the /grantBadge command or programmatically via awardBadge. | A system message with the prose key `prose_grant` (for first award) or `prose_hasbadge` (for duplicate) under the `badge_n` category is displayed. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Award a badge with non-'NONE' music. | A PlayMusicMessage is received on the client side. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Call hasBadge(badgeId) on the PlayerObject. | The specific badge is confirmed as set. |
| Ensure the player character is logged, has a valid PlayerObject ghost slot, and has been awarded a badge. | Call getNumBadges() on the PlayerObject. | The total badge count increases by 1. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Call getTypeCount(type) on the PlayerObject. | The correct type counter for the badge is incremented. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Reach a milestone badge count through accumulation triggers. | A corresponding "count_N" or "bdg_exp_M_badges" badge appears in ownership, and its system message/music is triggered. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Place or trigger entry into a BadgeActiveArea with a known areaBadge value. | The badge associated with the areaBadge is awarded to the player. |
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Use the /requestBadges <targetCreatureId> command to read badges remotely. | A response is sent to the targetCreatureId containing badge information. |

## bank-tips

| Setup | Bot does | Expect |
|---|---|---|
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 100` | Sender's cash decreases by exactly 100. |
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 100` | Receiver's cash increases by exactly 100. |
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 100` | Both bots receive system messages matching the prose IDs `prose_tip_pass_self` and `prose_tip_pass_target`. |
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 999999` with only 500 cash | Rejection when sender has insufficient cash (e.g., tip 999999 with only 500 cash). |
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 100` with distance > 190 m | Rejection when distance > 190 m. |
| Two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Send `/tip <other_bot> 100 bank` | A confirmation SUI box appears on the sender with title ` |

## bazaar-flow

| Setup | Bot does | Expect |
|---|---|---|
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Attempt to sell an item through the bazaar terminal. | System message confirming the item was listed, item removed from player inventory or placed in auction state, and credits deducted for listing fee. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Attempt to search for items in the bazaar terminal. | Response message with opcode `0xFA500E52` received, item list contains expected entries with correct prices, expiration times, and owner names. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Attempt to buy an item from the bazaar terminal. | Credits deducted from buyer, item transferred to buyer inventory or marked as sold. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Attempt to retrieve an item from the bazaar terminal. | Item appears in player inventory, or credits appear in player balance. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Verify the vendor is a bazaar terminal. | vendor->isBazaarTerminal() must return true. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Verify the response contains correct item data structure. | Response contains correct item data structure matching AuctionQueryHeadersResponseMessage.h:94-138. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Verify pagination offset and continues flag work correctly. | Pagination offset and continues flag work correctly as per AuctionQueryHeadersResponseMessage.h:149-151. |
| Player must have a valid CreatureObject reference and a valid bazaar terminal or vendor TangibleObject accessible by its object ID. | Verify the isAuction byte distinguishes instant sale from auction. | isAuction byte distinguishes instant sale (1) from auction (0) as per lines 103-106. |

## bounty-hunter

| Setup | Bot does | Expect |
|---|---|---|
| Accept a bounty mission of at least level 2 (for CALLDROID/FINDTARGET) or level 3 (for FINDANDTRACKTARGET). | Speak to the informant until objectiveStatus reaches HASTALKED (informantLevel > 1). | A waypoint exists with the correct planet and position, and the system message '@mission/mission_generic:target_location_received' was sent. |
| Use an Arakyd droid item and ensure the player is not mounted and not in a city region. | Wait for the 20-second countdown messages at t=20, 3, 2, 1, and arrival. | A 'probot' NPC spawns at the landing coordinates and the objective's activeDroid is set. |
| After Arakyd arrives, use the TRANSMITBIOLOGICALSIGNATURE action. | Wait for the calculated time for the search/tracking result. | The droid sits briefly then despawns, and a search/tracking result message appears. |
| Use Seeker droid items. | Wait for the 'seeker' NPC to spawn at the player. | The 'seeker' NPC sits for 5 seconds, then despawns, and success/failure messages appear. |
| Test with varying droid_find_chance / droid_track_chance skill mods. | Use the success formula (skillMod − targetLevel/3, clamped 5–95) and time formula (150 − skillMod + random). | The success formula and time formula are applied correctly. |
| Kill the spawned NPC target. | Verify the bounty hunter receives the loot. | The complete() method is called, XP is awarded as 'bountyhunter' with value (rewardCredits + bonusCredits) / 50, and the mission status updates to TARGETELIMINATEDSTATUS. |
| Have a target player perform actions near other creatures to increase visibility. | Verify the target appears on bounty hunter terminals when visibility ≥ terminalVisThreshold and disappears when below falloffThreshold. | The target appears on bounty hunter terminals when visibility ≥ terminalVisThreshold and disappears when below falloffThreshold. |
| After killing the target, call clearVisibility() method. | Verify the visibility is set to 0. | The visibility is set to 0. |

## camps

| Setup | Bot does | Expect |
|---|---|---|
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Attempt to place a camp. | @camp:starting_camp |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Complete the camp placement. | @camp:camp_complete |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Enter the camp. | System message with prose_camp_enter containing terminal name |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Enter the camp. | @camp:sys_camp_heal |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Trigger a heal event on the player while inside the camp. | currentXp increments by (campStructureData->getExperience() / 180) per heal |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Exit the camp as owner. | After ~60 seconds, terminal name changes to "Abandoned Camp" |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Exit the camp as owner. | campFire object changes appearance to "campfire_smoldering.iff" |
| Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands). Player must be in an outdoor, no | Exit the camp as owner. | @camp:sys_abandoned_camp |

## combat-states

| Setup | Bot does | Expect |
|---|---|---|
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with CreatureState::DIZZY. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with CreatureState::STUNNED. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with CreatureState::BLINDED. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with Creature. State::INTIMIDATED. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with CreatureState::IMMOBILIZED. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have state bitmask set with CreatureState::FROZEN. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | Target should have posture set to CreaturePosture::KNOCKEDDOWN. |
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack target with a state-only ability. | System messages and flytexts should appear on both attacker and target at the correct times. |

## containers-inventory

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the creature has a valid zone and parent hierarchy (the command requires `zoneServer` and resolves objects by ID; TransferItemMiscCommand.h:43-79). | Attempt to transfer an item to a full inventory. | The creature should receive the system message "@container_error_message:container03" via `sendSystemMessage`. |
| Before the transfer attempt, call `canAddObject` on the inventory with `containmentType = -1`. | Check the return value of `canAdd,object` to determine if the inventory is full. | The return value should be `TransferErrorCode::CONTAINERFULL` if the inventory is full; `0` if space exists. |
| Query `sceneObject->getContainerObjects()->size()` and compare to `sceneObject->getContainerVolumeLimit()`. | Calculate the remaining slots in the container. | The remaining slots should be computed correctly based on the container's size and volume limit. |
| For equipment slots (`containmentType >= 4`), verify `canAddObject` returns `SLOTOCCUPIED` when the slot descriptor is already taken. | Attempt to add an item to an already occupied equipment slot. | The `canAddObject` method should return `SLOTOCCUPIED`. |
| Call `destination->canAddObject(item, -1, errorDesc)` before attempting transfer. | Check the return value of `canAddObject` to determine if the transfer is possible. | If the return value is non-zero, the transfer should not proceed. |
| Use `removeObject` on the destination container to free slots, or move items to another container (e.g., bank). | Free up slots in the destination container. | The test should re-check `canAddObject` after removals to confirm space is available. |
| Ensure the destination container is reachable within the distance limit (`maxDistance = 16.5`) unless it is a building or cell object. | Attempt to transfer an item to a container that is out of range. | The transfer should fail due to the distance limit unless the container is a building or cell object. |
| If testing wearable items, verify the creature's race/faction and skill list match the item's requirements. | Attempt to transfer a wearable item to a creature that does not meet the item's requirements. | The transfer should fail due to mismatched race/faction or skill requirements. |

## contraband-scans

| Setup | Bot does | Expect |
|---|---|---|
| An AI agent (AiAgent) scanner with FACTIONIMPERIAL or FACTIONREBEL (or ensure `currentWinningFaction` is set). | Initiate a contraband scan. | The 1/12 chance is confirmed by running multiple scans; verify cooldowns 'crackdown_scan' are set on both player and scanner. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles. | Initiate a contraband scan. | Player dismounts if riding; system message received. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles. | Initiate a contraband scan. | Player with sufficient smuggler skills should receive '@base_player:smuggler_scan_success' and no further scan messages. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggand skills or Jedi titles. | Initiate a contraband scan. | Padawan+ player should see mind-trick chat; on success, 'probe_scan_done' system message and scanner leaves. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles. | Initiate a contraband scan. | Opposite-faction player should receive 'discovered_imperial'/'discovered_rebel', status change to COVERT/OVERT, and Lambda shuttle combat. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles. | Initiate a contraband scan. | If contraband found, SUI window appears with correct credit amount; accepting deducts from cash/bank with TransactionLog FINES entries; refusing/timing out decreases faction standing. |
| A player creature with known state: not in combat, not dead/incapacitated, optionally with smuggler skills or Jedi titles. | Initiate a contraband scan. | Lambda shuttle spawns at nearest valid spawn point, starting combat. |

## crafting

| Setup | Bot does | Expect |
|---|---|---|
| Skills that grant the schematic group, plus the assembly and experimentation skill mods. | Attempt to craft an item using the tool. | The assembly result code (0x109). |
| A tool of the matching type, in the inventory and neither busy nor finished. | Attempt to craft an item using the tool. | The assembly result code (0x109). |
| For experimentation, a station of the same type within 7 m. | Attempt to experiment with the tool. | The experiment result (0x105) and the remaining points. |
| Resources with known stats in the inventory, of known spawns, enough to fill every slot. | Attempt to craft an item using the tool. | The assembly result code (0x109). |
| Free inventory space. | Attempt to craft an item using the tool. | @system_msg:prototype_transferred. |
| An inventory item carrying the crafter's name, a "(xxxxxxxx)" serial and a custom name. | Attempt to craft an item using the tool. | An inventory item carrying the crafter's name, a "(xxxxxxxx)" serial and a custom name. |
| Attribute values inside min/max, with % never above W/1000. | Attempt to craft an item using the tool. | Attribute values inside min/max, with % never above W/1000. |
| XP gained equal to xpAmount, or x1.05 for practice. | Attempt to craft an item using the tool. | XP gained equal to xpAmount, or x1.05 for practice. |

## crafting-factories

| Setup | Bot does | Expect |
|---|---|---|
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | System message containing "@manf_station:schematic_added" with schematic name. |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Second system message: "This schematic limit is: <N>" where N = schematic->getManufactureLimit(). |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Factory container now has 1 object in slot 0 (the schematic). |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | System message "@manf_station:activated". |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Second system message with limit again. |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Factory isActive() returns true. |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Pending task "createFactoryObject" exists with timer * 1000ms delay. |
| Factory object must be placed in the world with ingredient_hopper and output_hopper slotted (created via CreateFactoryObjectTask or template). | Player must have a valid manufacture schematic in their datapad with a non-null prototype, not sliced, no anti-decay kit, draftSchematic with factoryCrateSize > | Objects appear in output_hopper (check getContainerObjectsSize() > 0). |

## creature-harvest

| Setup | Bot does | Expect |
|---|---|---|
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | System message: A success message containing the quantity extracted and resource type (e.g., "You extract 12 units of meat from the rockmite"). |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | Inventory: A new resource container appears in inventory with a name matching the harvested type (meat, hide, or bone). |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | Corpse state: The corpse despawns after ~1 second if it has no loot/credits and no group members can harvest it. |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | XP award: Scout XP equal to `creature level × 5 + 19` is awarded. |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature while grouped. | Group messages: If grouped, bonus messages and group chat notifications appear with the correct modifiers. |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | Multiple harvests of different types from the same corpse by the same player (one-time per player). |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | All three resource types from one kill unless using random selection multiple times with different players. |
| Location: Near a starting city (e.g., Mos Eisley area around coordinates 3500-3800, -4800 to -5020). Target creatures: Low-level (≤ 5) ordinary wild prey such a | Attempt to harvest the freshly killed creature. | Existing-stack quantity visibility (BLOCKED in current body). |

## cure-poison

| Setup | Bot does | Expect |
|---|---|---|
| Partner is poisoned with a DoT strength of 30, and the tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | Tester system text matches "You apply poison antidote to ". |
| Partner is poisoned with a DoT strength of 30, and the tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | Partner's states lose "poisoned". |
| Tester has a cure pack in inventory with healing_ability ≥ 30. | Tester uses cure pack on poisoned partner. | Tester's mind drops by about 100 after FOCUS adjustment. |
| Tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | Cure pack's use count drops by 1. |
| Tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner within 120 s. | Second cure within 4-20 s answers "@healing_response:healing_must_wait". |
| Tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | Bot sees string-table messages as "@file:key". |
| Partner is poisoned with a DoT strength of 30, and the tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | If power < 30, the cure is BLOCKED with reason "@healing_response:healing_must_wait". |
| Partner is poisoned with a DoT strength of 30, and the tester has a cure pack in inventory. | Tester uses cure pack on poisoned partner. | If partner is not in line of sight, the cure is BLOCKED with reason "@healing_response:healing_must_wait". |

## datapad-tools

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). | Use a non-admin character. | System message: "The test datapad only works for admins." and no menu/action. |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). | Select a named planet destination. | Player's zone name changes to that planet and coordinates match the preset (e.g., Mos Eisley at 3528, -4804). |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). | Test "back" teleport after a prior jump. | Return to recorded location. |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). | Test a disabled zone if applicable. | System message: "X is not enabled on this galaxy." |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). Obtain the datapad item `object/tangible/sandbox/tools_datap | Select a creature from the list. | A mobile with that template appears ~6m east at world floor. |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). Obtain the datapad item `object/tangible/sandbox/tools_datap | Test indoors. | System message: "Step outside first: creatures spawn outdoors only." |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). Obtain the datapad item `object/tangible/sandbox/tools_datap | Select a kit category. | All listed items appear in the player's inventory (check slotted object "inventory"). |
| Ensure the bot character is an admin/privileged player (the test galaxy's method for setting this). Obtain the datapad item `object/tangible/sandbox/tools_datap | Verify message reports correct count of given/failed items. | Message reports correct count of given/failed items. |

## doctor-enhance-wounds

| Setup | Bot does | Expect |
|---|---|---|
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | The doctor's message "You enhance <name>'s Health by N" and the patient's "enhances your". |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | The patient's max HAM rises (inferred from the fill-on-buff attribute modifier). The rise should be the full buff value on a first buff, not N on a re-apply. |
| The doctor has the `healen, |  |  |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | The doctor's mind drops by about 150. |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | The patient's wounds in that pool drop by min(power, wounds), plus the message. |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | healing_response_59 after the cooldown. |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | Error 2 means INVALIDLOCOMOTION, not a missing command (lines 68-71), if the harness passes the server codes through (inferred). |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | Treat "re-apply" as no change in max HAM. |
| The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750). | The doctor uses `healenhance` on a bot. | Use system messages as the primary signal. |

## entertainer-buffs

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the patron is grouped with the performer and has clear line of sight. | The patron watches the performer for at least 60 seconds. | A system message confirming the watch started. |
| Ensure the patron is grouped with the performer and has clear line of sight. | The patron watches the performer for at least 60 seconds and the performer stops. | A system message containing `performance_enhance_dance_mind`. |
| Ensure the performer has `private_buff_mind > 0` and `healing_dance_mind > 0`. | Check the patron's buffs after the buff message. | Nima has a buff with CRC `STRING_HASHCODE("performance_enhance_dance_mind")`. |
| Ensure the performer has `private_buff_mind > 0` and `healing_dance_mind > 0`. | Check the performer's skill mods. | Dorn has `private_buff_mind > 0` and `healing_dance_mind > 0`. |
| Ensure the patron is grouped with the performer and has clear line of sight. | The patron watches the performer while in the entertaining session. | Nima is in Dorn's `patronDataMap`. |
| Ensure the patron is grouped with the performer and has clear line of sight. | The patron watches the performer for at least 60 seconds. | The buff strength and duration match expectations. |
| Ensure the performer has `private_buff_mind > 0` and `healing_dance_mind > 0`. | Check the performer's skill mods. | Dorn has `healing_dance_mind > 0`. |
| Ensure the performer has `private_buff_mind > 0` and `healing_dance_mind > 0`. | Check the performer's skill mods. | Dorn has `healing_music_mind > 0`. |

## factions

| Setup | Bot does | Expect |
|---|---|---|
| Ensure bot character has no Jedi skills (`force_rank_light_novice` or `force_rank_dark_novice`) if testing covert/resign paths. | Attempt to join a faction covertly. | System message confirming covert status. |
| Verify bot is neutral (faction = 0) and has at least 200 faction standing with the target recruiter's faction before attempting to join. | Attempt to join a faction covertly. | `getFaction()` returns recruiter's faction hash. |
| For bribe tests, ensure bot has `combat_smuggler_underworld_04` skill and sufficient credits (20k or 100k). | Attempt to bribe a recruiter. | Bribe options only appear when skill and credit requirements are met. |
| Ensure bot character has no Jedi skills (`force_rank_light_novice` or `force_rank_dark_novice`) if testing covert/resign paths. | Attempt to join a faction covertly. | `getFactionStatus()` returns 1. |
| Verify bot is neutral (faction = 0) and has at least 200 faction standing with the target recruiter's faction before attempting to join. | Attempt to join a faction covertly. | OVERT PVP flag is not set. |
| Ensure bot character has no Jedi skills (`force_rank_light_novice` or `force_rank_dark_novice`) if testing covert/resign paths. | Wait 30 seconds and attempt to go overt. | System message about being attackable. |
| Verify bot is neutral (faction = 0) and has at least 200 faction standing with the target recruiter's faction before attempting to join. | Wait 30 seconds and attempt to go overt. | OVERT PVP flag is set. |
| Ensure bot character has no Jedi skills (`force_rank_light_novice` or `force_rank_dark_novice`) if testing covert/resign paths. | Wait 30 seconds and attempt to go overt. | "declare_overt_cooldown" cooldown exists (check via `hasCooldown`). |

## fishing

| Setup | Bot does | Expect |
|---|---|---|
| Equip a FishingPoleObject in the right hand slot (hold_r) and load a FishingBaitObject into the pole's container. Stand on land adjacent to water at a valid fis | Call startFishing() | System message @fishing:start_fishing received. Player mood string set to "fishing". Fishing session created with state WAITING. SUI fishing window opened with correct status text. |
| Equip a FishingPoleObject in the right hand slot (hold_r) and load a FishingBaitObject into the pole's container. Stand on land adjacent to water at a valid fis | Monitor FishingEvent ticks (every 7 seconds) during the fishing session. | State transitions through WAITING → SNAGGED/NIBBLE → BITE → CATCH → REELING → REELGAME. Corresponding system messages and fly text at each transition. SUI window updates with current state, bait statu |
| Equip a FishingPoleObject in the right hand slot (hold_r) and load a FishingBaitObject into the pole's container. Stand on land adjacent to water at a valid fis | When REELGAME succeeds (player within 2.0 of marker), complete the fishing action. | FishObject created and transferred to player inventory. Fish attributes set: name, zone, time, length. System message fishing:prose_notify_catch with item name. Marker container opened to player. XP a |
| Equip a FishingPoleObject in the right hand slot (hold_r) and load a FishingBaitObject into the pole's container. Stand on land adjacent to water at a valid fis | Simulate a lost line or mishap during the fishing session. | Appropriate @fishing: system message sent (e.g., line_snap, lost_bait). Fishing session ends; state returns to NOTFISHING. If bait lost, pole container is empty or bait use count decreased. |
| No FishingPoleObject equipped in the right hand slot (hold_r). | Call startFishing() | System message @fishing:must_have_pole received. |
| Equip a FishingPoleObject in the right hand slot (hold_r) but no FishingBaitObject loaded into the pole's container. | Call startFishing() | System message @fishing:bait_your_pole received. |
| Equip a FishingP,oleObject in the right hand slot (hold_r) and stand in water (swimming). | Call startFishing() | System message @fishing:bad_cast received. |
| Equip a FishingPoleObject in the right hand slot (hold_r) and stand on land adjacent to water but too far from the water. | Call startFishing() | System message @fishing:too_far or @fishing:invalid_location received. |

## food-drink-spice

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | System message confirming consumption. |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | Buffs present: Check `hasBuff(buffCRC)` and iterate buffs to verify the new buff exists with correct type (`BuffType::FOOD` for attribute/skill, `BuffType,::SPICE` for spice), correct duration (accoun |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | Filling values: Check `ghost->getFoodFilling()` or `ghost->getDrinkFilling()` increased by the item's `filling` value. |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | Attributes/skills: Verify attribute modifiers (HAM pools) and skill mods were applied via the buff. |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a spice item. | For spice items only: After the spice buff expires, verify a `SpiceDownerBuff` was added with 120-second duration (reduced by any `reduce_spice_downtime` modifier), negative attribute modifiers matchi |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a healing item. | For healing items: Verify HAM pools increased by the expected amounts and the healing message was sent. |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | Inventory: Confirm the item's use count decreased (or the item was destroyed if it reached zero). |
| Ensure the player character is alive, not incapacitated, and has sufficient food/drink stomach capacity (check `getFoodFilling()` / `getDrinkFilling()` vs max). | Consume a food/drink/spice item. | System messages: Confirm the correct message was sent (consumption confirmation, skill mod messages, healing amounts, or error messages if blocked). |

## foraging

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player character has the 'foraging' skill (or appropriate skill mod). | Initiate a forage action. | Receive the correct start message. |
| Position the player on foot, outside any structure, in an area that hasn't been exhausted (first forage or within 3 uses). | Wait 8.5 seconds after initiating the forage. | Receive either a success or failure message based on the loot table outcomes. |
| Confirm the player is not mounted and not in combat. | Initiate a forage action. | Receive the correct start message. |
| Verify sufficient ACTION HAM (at least actionCost + 1). | Initiate a forage action. | Receive the correct start message. |
| On success, confirm items from the expected loot group (e.g., 'forage_food' or 'forage_bait' for SCOUT). | Complete a successful forage. | Items from the expected loot group appear in the player's inventory. |
| Check item count matches expectations (up to 3 uses per area). | Complete a successful forage. | Item count matches the expected number. |
| After 3 forages in the same 10x10 area, verify the 'nothing to forage' message appears on the 4th attempt. | Attempt to forage for the 4th time in the same area. | Receive the 'nothing to forage' message. |
| Move more than 2 meters during the 8.5-second delay and confirm the move-fail message. | Move more than 2 meters during the 8.5-second delay. | Receive the move-fail message. |

## fs-village

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the zone `dathomir` is enabled (line 135 in township checks this). | Talk to the elder or old man and select the appropriate option. | Receive a system message confirming item creation or an "inventory full" error (`@error_message:inv_full`, line 32 of elder_conv_handler.lua). The old man should become non-conversable and despawn. |
| Ensure the village is in Phase 1 for Sarguillo patrols (check `Village:CurrentPhase` quest status). | Complete 20 patrols. | `FsPatrolCompletedCount` equals 20, the player has completed `FS_PATROL_QUEST_FINISH`, and the banner pole item exists in inventory. The branch unlock state should be set to 2 for `force_sensitive_com |
| Ensure the player has no force crystal (`force_crystal.iff`) in inventory before talking to the elder or old man. | Use the experience converter. | Standard XP decreased by the converted amount (line 305), `fs_<category>` XP increased by `convertedXp` (line 312), and system messages about conversion appear. Check that the SUI windows close proper |
| Ensure the player has no force crystal (`force_crystal.iff`) in inventory before talking to the elder or old man. | Attempt to learn a `force_sensitive_` skill before the unlock state reaches 2. | Attempting to learn a `force_sensitive_` skill before the unlock state reaches 2 should fail silently or show an error. |
| Ensure the player has no force crystal (`force_crystal.iff`) in inventory before talking to the elder or old man. | Attempt to learn a `force_sensitive_` skill after the unlock state reaches 2. | Learning a `force_sensitive_` skill should succeed. |
| Check `Village:CurrentPhase` (quest status). | Check `VillageUnlockScreenPlay:<branchName>` (screenplay state). | The state should reflect the current phase of the village. |
| Check `FsPatrolCompletedCount` (stored village value). | Check inventory for `force_crystal.iff` and `fs_village_bannerpole_s01.iff`. | The inventory should contain the banner pole item if patrols are completed. |
| Check skills: `force_title_jedi_novice`, any unlocked `force_sensitive_` skills. | Verify the unlock state for `force_sensitive_combat_prowess_ranged_accuracy`. | The branch unlock state should be set to 2 for `force_sensitive_combat_prowess_ranged_accuracy`. |

## gambling

| Setup | Bot does | Expect |
|---|---|---|
| Position the bot character within 20 units of a gambling terminal object. | Check radial menu for 'Join Station' option. | Radial menu shows 'Join Station' when not playing. |
| Position the bot character within 20 units of a gambling terminal object. | Join the gambling station. | Radial menu changes to 'Leave Station' after joining. |
| Position the bot character within 20 units of a gambling terminal object. | Open SUI window for slots. | SUI window appears with title '@gambling/game_n:slot_standard' and five menu items. |
| Position the bot character within 20 units of a gambling terminal object. | Press 'Bet One' in the slots menu. | Pressing 'Bet One' adds 1 credit. |
| Position the bot character within 20 units of a gambling terminal object. | Press 'Bet Max' in the slots menu. | Pressing 'Bet Max' fills to max bet (3 for slots). |
| Position the bot character within 20 units of a gambling terminal object. | Place a bet of 3 credits in slots. | Game auto-starts and the terminal sends 'Slot Machine Pay Line' messages showing rolling digits. |
| Position the bot character within 20 units of a gambling terminal object. | Wait for the slot game to end. | Player can rejoin if state is SLOTGAMEENDED. |
| Position the bot character within 20 units of a gambling terminal object. | Open SUI window for roulette. | SUI window appears with title '@gambling/game_n:roulette' and betting instructions. |

## gcw-bases

| Setup | Bot does | Expect |
|---|---|---|
| Place or locate an OVERT player faction base (check `ObjectFlag::OVERT` via `getPvpStatusBitmask()`). | Ensure the base is in the `VULNERABLE` state (`baseData->getState() > INVULNERABLE`). If not, wait for the cycle or use `resetVulnerability()` if 7 days have pa | Base is in the `VULNERABLE` state. |
| Ensure the base is in the `VULNERABLE` state (`baseData->getState() > INVULNERABLE`). | Confirm terminals are spawned (HQ terminal, security terminal, override terminal) by checking child objects of the building. | Terminals are spawned. |
| Before jamming | Interact with the uplink and guess wrong bands. | Player gets directional hints when guessing wrong bands. |
| After narrowing to correct band | Interact with the uplink and identify the correct band. | State = `BAND`; message 'You narrow the carrier signal down to Band #X'. |
| After identifying the correct band | Interact with the uplink to complete the jamming. | State = `JAMMED`; messages 'You isolate the carrier signal to Channel #X' and 'Jamming complete! You disable the uplink...'; verify 1000 bounty hunter slicing XP awarded. |
| After jamming | Interact with HQ terminal as attacker faction. | Check `declare_overt_cooldown` is cleared (or test after waiting 5 min). |
| After interacting with HQ terminal as attacker faction | Wait for the system message 'Structure shutdown request received. Please stand by...'. | System message: 'Structure shutdown request received. Please stand by...' |
| After the system message 'Structure shutdown request received. Please stand by...' | Wait ~60 s for the BaseShutdownTask to complete. | Verify state changes to `SHUTDOWNSEQUENCE`. |

## group-loot

| Setup | Bot does | Expect |
|---|---|---|
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to each type via `/grouploot`. Kill a creature that drops items | Check system messages received by each member. | System messages confirm correct rule name and master looter notifications. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to each type via `/grouploot`. Kill a creature that drops items | Verify who can successfully loot items. | Permissions verify that only eligible members can loot items. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot and credits loot rule via `/grouploot`. Kill a creature that drops i | Check inventory contents after looting. | Items are in the correct player's inventory. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to each type via `/grouploot`. Kill a creature that drops items | Check credit balances after splitting. | Credit amounts match expected split. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to each type via `/grouploot`. Kill a creature that drops items | Move one member beyond 128 units. | The member cannot join lottery or receive credits. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to each type via `/grouploot`. Kill a creature that drops items | Move one member beyond 128 units. | The 'too far away' message appears. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to Master Looter via `/grouploot`. Kill a creature that drops i | Non-master members attempt to loot. | Non-master members see the restriction message. |
| Form a group with multiple bot players. Ensure one bot is the group leader. Change the loot rule to Master Looter via `/grouploot`. Kill a creature that drops i | Master looter attempts to loot. | Master looter can loot all items. |

## groups

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send invite command to target. | Inviter receives system message `@group:invite_leader` with target name (GroupManager.cpp:126-128). Target receives system message `@group:invite_target` with inviter name (GroupManager.cpp:135-137).  |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send accept command from target. | If no prior group exists: leader sees `@group:formed_self` (GroupManager.cpp:324), new member sees `@group:joined_self` (GroupManager.cpp:336). A GroupObject with ID `0x13dcb432` is created and both c |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send accept command from target. | If group already existed and inviter was leader: new member sees `@group:joined_self` (GroupManager.cpp:242) and receives a `GroupObjectDeltaMessage6` with `updateMembers()` (GroupObjectImplementation |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send invite command to self. | Inviter sees `@group:invite_no_target_self` (GroupManager.cpp:48). |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send invite command from non-leader. | Non-leader sees `@group:must_be_leader` (GroupManager.cpp:62). |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send invite command to already-grouped target. | Inviter sees `@group:already_grouped` (GroupManager.cpp:77-89). |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Send invite command to target when group is full (≥20). | Joining player sees "The group is full." (GroupManager.cpp:213). |
| Ensure the bot character has no existing group (`getGroup() == nullptr`). Have a second test character available to invite. | Kill a creature while in a group with another player who also damaged it. | Both characters receive XP and the server checked `isInRangeZoneless(attacker, 80)` before distributing (PlayerManagerImplementation.cpp.lines-1941-2140:2121). |

## guilds

| Setup | Bot does | Expect |
|---|---|---|
| Two bot characters (Bot A and Bot B). One GuildTerminal object available in the zone. Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot | Bot A completes name/abbrev input for guild creation. | Bot A's `isInGuild()` returns true, `getGuildObject()` is non-null, a system message confirming creation appears, and Bot A is in the guild chat room. |
| Two bot characters (Bot A and Bot B). One GuildTerminal object available in the zone. Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot | Bot B receives a SUI dialog (`GUILD_SPONSOR_VERIFY`) with accept/decline buttons. After accepting. | Bot B's `isInGuild()` returns true, guild object is set, system messages appear on both bots, and a guild mail is delivered to Bot B. |
| Two bot characters (Bot A and Bot B). One GuildTerminal object available in the zone. Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot | After kicking, the target's `isInGuild()` returns false, guild object is null, both bots receive system messages, a guild mail is sent, and the target is remove | The target's `is,InGuild()` returns false, guild object is null, both bots receive system messages, a guild mail is sent, and the target is removed from chat rooms. |
| Two bot characters (Bot A and Bot B). One GuildTerminal object available in the zone. Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot | The leaving player's `isInGuild()` returns false, guild object is null, a system message appears, a guild mail is sent, and the player is removed from chat room | The leaving player's `isInGuild()` returns false, guild object is null, a system message appears, a guild mail is sent, and the player is removed from chat rooms. If the leader leaves without an elect |
| Two bot characters (Bot A and Bot B). One GuildTerminal object available in the zone. Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot | The guild no longer exists in the server's guild list, all members receive a disband mail, and native `destroyGuild` logic executes (870). | The guild no longer exists in the server's guild list, all members receive a disband mail, and native `destroyGuild` logic executes (870). |

## ham

| Setup | Bot does | Expect |
|---|---|---|
| Damage the bot's health. | Stand still and wait for regen ticks. | Per-tick gain = ceil(con x 13/2100 x latency/1000 x posture factor), at least 1. |
| Damage the bot's health. | Kneel and wait for regen ticks. | Per-tick gain = ceil(con x 13/2100 x latency/1000 x posture factor), at least 1. |
| Damage the bot's health. | Sit and wait for regen ticks. | Per-tick gain = ceil(con x 13/2100 x latency/1000 x posture factor), at least 1. |
| Damage the bot's health. | Stand still and wait for regen ticks. | The sitting/standing ratio should be about 1.75 (not exact, because of ceil). |
| Damage the bot's health. | Kneel and wait for regen ticks. | The sitting/standing ratio should be about 1.75 (not exact, because of ceil). |
| Damage the bot's health. | Sit and wait for regen ticks. | The sitting/standing ratio should be about 1.75 (not exact, because of ceil). |
| Damage the bot's health. | Stand still and wait for regen ticks. | Zero gain while incapacitated. |
| Damage the bot's health. | Stand still and wait for regen ticks. | No gain past max minus wounds. |

## harvester-operation

| Setup | Bot does | Expect |
|---|---|---|
| Place a harvester deed and construct it on a zone with an active resource node (spawn "inShift") nearby. | Ensure the bot character is the owner (on admin list) so radial menu options appear. | Radial menu: Right-clicking the harvester shows item ID 78 with label "@harvester:manage". |
| Ensure the bot character is the owner (on admin list) so radial menu options appear. | Select item 78 from the radial menu. | SUI window: The client receives `ResourceHarvesterActivatePageMessage`. |
| Select item 78 from the radial menu and interact with the SUI to select a resource and confirm activation. | Confirm the activation in the SUI. | Activation success: The harvester's operating state changes to true. The bot receives `InstallationObjectDeltaMessage3` and `InstallationObjectDeltaMessage7` packets showing operating=true. |
| After confirming in the SUI, the harvester's operating state changes to true. | Wait for the harvester to start extracting the selected resource. | Resource in hopper: The bot receives `HarvesterObjectMessage7` and `InstallationObjectDeltaMessage7` packets showing the selected resource container in the hopper. |
| The bot receives `HarvesterObjectMessage7` and `InstallationObjectDeltaMessage7` packets showing the selected resource container in the hopper. | Monitor the hopper quantity for the active resource over time. | Extraction progress: The hopper quantity for the active resource increases over time at the expected rate. |
| The hopper quantity for the active resource increases over time at the expected rate. | Wait for the hopper to reach `hopperSizeMax`. | Hopper full shutdown: The harvester shuts down and broadcasts "harvester_resource_depleted" if the resource is depleted, or stops due to capacity. |
| When the hopper reaches `hopperSizeMax`, the harvester shuts down. | Monitor the surplus power and maintenance levels. | Power/maintenance depletion: When surplus power or maintenance reaches zero, the harvester shuts down and broadcasts "harvester_no_maint_4" or the power deposit incomplete message. |
| The bot should check for system messages and harvester state changes. | Check for system messages and harvester state changes. | System message received: "player_structure:power_deposit_incomplete" → should NOT appear on success OR Harvester operating state changed to true (InstallationObjectDeltaMessage3/7 with operating=true) |

## hoth-content

| Setup | Bot does | Expect |
|---|---|---|
| Ensure zone 'hoth' is enabled | Check each screenplay's start function for 'hoth' zone | Zone 'hoth' is enabled in hoth_ice_caves.lua:22, hoth_glacial_rancor_den.lua:18, hoth_mynock_den.lua:46, hoth_outpost_terminals.lua:15, hoth_echo_base.lua:15 |
| Verify the bot is on the correct planet | Check planetName = 'hoth' in scavenger_quartermaster.lua | PlanetName is 'hoth' in scavenger_quartermaster.lua:85 |
| Teleport to each cave center | Verify wampa spawns exist within cell-local coordinates | Wampa spawns exist within cell-local coordinates in hoth_ice_caves.lua |
| Check boss variants spawn | Verify boss variants have 1800 s respawn timer vs 420 s for regular wampas | Boss variants have 1800 s respawn timer vs 420 s for regular wampas |
| Confirm two elder_wampa guards | Check for two elder_wampa guards accompanying each boss | Two elder_wampa guards accompany each boss in hoth_ice_caves.lua:61–62, 90–91, 131–132, 160–161 |
| Verify cave building object spawns | Check cave building object spawns at -2000, 44.8, -4800 | Cave building object spawns at -2000, 44.8, -4800 in hoth_mynock_den.lua:52 |
| Check 23 mynock-type mobs | Verify 23 mynock-type mobs exist across cells 1–11 | 23 mynock-type mobs exist across cells 1–11 |
| Confirm hoth_mynock_broodmother | Check hoth_mynock_broodmother is in cell 11 with 1800 s respawn | hoth_mynock_broodmother is in cell 11 with 1800 s respawn in hoth_mynock_den.lua:37 |

## image-design

| Setup | Bot does | Expect |
|---|---|---|
| Designer creature must have `social_entertainer_novice` skill. | Attempt to start an image design session with a target creature. | System message confirms skill check failure if the designer lacks the required skill. |
| Target creature must be alive and visible. | Attempt to start an image design session with a dead or invisible target creature. | System message confirms dead/invisible target error. |
| Both creatures must be in the same group if they differ. | Attempt to start an image design session with creatures in different groups. | System message confirms group mismatch error. |
| Both creatures must be inside a `SALONBUILDING` for stat migration testing. | Attempt to start an image design session outside of a `SALONBUILDING`. | System message confirms bypass warning or timeout. |
| Both creatures should have `SessionFacadeType::IMAGEDESIGN` active during the session. | Start an image design session and check the session state. | Session state is `SessionFacadeType::IMAGEDESIGN`. |
|  | Complete or cancel the image design session. | Session state is dropped to `SessionFacadeType::IMAGEDESIGN`. |
| If hair changes are made, verify the old hair slot is removed and new hair object is transferred. | Perform a hair customization during an image design session. | Old hair slot is removed and new hair object is transferred to the target. |
| Target's cash/bank credits decrease by the payment amount; designer's cash increases by the same. | Complete an image design session with a payment. | Target's cash/bank credits decrease by the payment amount; designer's cash increases by the same. |

## lairs-spawning

| Setup | Bot does | Expect |
|---|---|---|
| Target a creature-type lair (not NPC) with known difficulty level and spawn limit from its template. | Approach the lair and verify initial state. | Initial passive mobiles are present and `spawnNumber` is effectively 1 (initial wave already triggered). |
| Ensure the lair has boss mobs defined in its template (`hasBossMobs()` returns true). | Deal enough damage to exceed 0 condition damage. | New creatures should appear within ~1–10 seconds. Check system messages or creature count increase. |
| Continue damaging until `conditionDamage > maxCondition / 2`. | Deal damage to the lair until `conditionDamage > maxCondition / 2`. | Another wave should spawn within 1–10 seconds. |
| After both waves (spawnNumber >= 3), continue damage until `(difficultyLevel * (maxCondition / 5)) <= conditionDamage`. | Deal damage to the lair until `(difficultyLevel * (maxCondition / 5)) <= conditionDamage`. | A boss mobile should appear after ~500 ms. Verify only one boss spawns per normal cycle. |
| During combat, observe if any creature stops attacking and moves toward the lair to heal it. | Observe the lair during combat. | Healer's blackboard ` |
| When condition reaches zero, verify: a heavy damage client effect plays at the lair location. | Deal damage to the lair until condition reaches zero. | A heavy damage client effect plays at the lair location. |
| When condition reaches zero, verify: XP is distributed to attackers. | Deal damage to the lair until condition reaches zero. | XP is distributed to attackers (check system messages or XP log). |
| When condition reaches zero, verify: the lair object no longer exists in the world. | Deal damage to the lair until condition reaches zero. | The lair object no longer exists in the world. |

## leash

| Setup | Bot does | Expect |
|---|---|---|
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Issue `/leash <leader name>` | Receive "Leashed to X: keep using /follow; if it gets stuck you'll be moved closer. /leash off to stop." (lines 437-438) |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Move the follower more than 10 m away from the leader while keeping the client `/follow` active. Wait at least 6 seconds (3 checks × 2 s) without closing the ga | The follower is teleported closer and receives "Leash: you were stuck, so you've been moved closer to X." (line 364) |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Issue `/leash off` | Receive "Leash off." (line 419) |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Issue `/leash <current leader>` again | Receive "Already leashed to X. /leash off to stop." (line 413) |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Try leashing a non-group member, an offline player, or someone on another planet | Receive the appropriate "Can't leash: ..." message (line 431) |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | While mounted or in combat, attempt to trigger unstick | No teleport occurs |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Before and after unstick, compare follower position relative to leader | Follower position should be closer, within BEHIND range if route reaches the leader |
| Two player characters on the same planet, in the same group. Verify `Core3.LeashEnabled` is true in the server config (or that the default applies). Ensure neit | Verify the pending task "leash" exists while active and is removed after `/leash off` or automatic stop | Pending task "leash" exists while active and is removed after `/leash off` or automatic stop |

## mail-friends-tells

| Setup | Bot does | Expect |
|---|---|---|
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send a tell to an offline bot. | System message received by sender: IM_OFFLINE. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send a tell to a bot that ignores the sender. | System message received by sender: IM_IGNORED. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send a tell to a bot with an invalid name. | System message received by sender: There is no person by the name '%TU' in this Galaxy. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send a tell to an online bot. | No system message (or IM_SUCCESS) when tell succeeds to online player. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send a tell to an offline bot. | Verify tell does not appear in receiver's chat if they are offline. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log on/off and have valid player objects. | Send mail with body > PM_MAXSIZE to an offline recipient. | System message received: IM_TOOLONG. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send mail to an offline player. | Mail appears in their inbox after login via `loadMail()`. |
| Two bot accounts (Bot A and Bot B). Ensure both bots can log in/out and have valid player objects. | Send mail to an online player. | Mail is delivered immediately. |

## medic-xp-healing

| Setup | Bot does | Expect |
|---|---|---|
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot uses HealDamage on a willing ally player creature. | Bot sees "You heal <name> for X health and Y action damage."; target sees "<name> heals you …" |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot uses HealWound on a willing ally player creature. | Bot sees "You heal <name> for X <pool> wound damage." |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot uses HealState on a willing ally player creature. | Bot sees "You remove the <state> state from <name>." |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing, etc.) set to known values. | Bot heals a willing ally player creature and checks medical skill progress. | Medical XP gain: HealDamage: (healthHealed + actionHealed) × 0.25; HealWound: woundHealed × 2.5; HealState: 50 |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot attempts to heal again immediately after a successful heal. | Should fail with "You must wait before you can do that." until cooldown expires |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot heals themselves and checks medical XP gain. | No medical XP awarded |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot heals a pet and checks medical XP gain. | No medical XP awarded |
| Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values. | Bot targets a willing ally player creature who has damage/states to heal. | Bot ensures the target is within range and line of sight; for HealWound, ensures neither bot nor target is in combat |

## mercenaries

| Setup | Bot does | Expect |
|---|---|---|
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Initiate conversation with the NPC named 'Dax Venn (a mercenary broker)'. | System/dialog messages: Confirm the initial greeting appears, and after selecting 'Hire a mercenary,' the confirmation message appears. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Mercenary spawn: Verify a new creature object of type 'sandbox_mercenary' spawns near the player within ~3 meters (random offset -3 to +3 on x and y) at the player's current floor height. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Mercenary state: The spawned mercenary should have AI flags 'AI_ESCORT' and 'AI_FOLLOW', and its follow target should be set to the player. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Mercenary state: The spawned mercenary should have AI flags 'AI_ESCORT' and 'AI_FOLLOW', and its follow target should be set to the player. |
| Position the bot character near the broker at coordinates tatoo, x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Max limit: Attempting to hire a fourth mercenary should produce the 'already got three' message instead of spawning a new one. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Combat behavior: When the bot enters combat, verify all alive mercenaries call 'engageCombat()' on the same target. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Dismiss my mercenaries' in the conversation. | Dismissal: After selecting 'Dismiss my mercenaries,' verify all mercenary objects are destroyed and no mercenary IDs remain in player data. |
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Select 'Hire a mercenary' in the conversation. | Max limit: Attempting to hire a fourth mercenary should produce the 'already got three' message instead of spawning a new one. |

## missions

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot is within range of all terminal types. | Check for terminal discovery. | The scenario finds terminals of each type within range. |
| Ensure the general terminal is within 2 km. | Check the first 6 mission slots. | The first 6 slots should be destroy missions. |
| Ensure the general terminal is within 2 km. | Check the next 6 mission slots. | The next 6 slots should be deliver missions. |
| Ensure the bot is near the city center. | Check deliver mission properties. | Deliver mission should have `inTown` flag. |
| Ensure the bot has a full datapad with 6 destroy missions. | Attempt to accept a 7th mission. | The 7th mission must be refused. |
| Ensure the bot has an active bounty mission. | Attempt to accept another bounty mission. | Only one bounty mission is allowed at a time. |
| Ensure the bot is at the correct difficulty level. | Check destroy mission difficulty. | Difficulty should match lair spawn range and player level. |
| Ensure the bot is at the correct distance from the lair. | Check destroy mission distance. | Distance should be within calculated range. |

## npc-conversations

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the NPC has a valid conversation template registered with the correct CRC. | Start a conversation with the NPC. | Receive an `NpcConversationMessage` packet with the NPC's dialog text, followed by a `StringList` packet containing the option texts. |
| Ensure the player is within conversation range of the NPC. | Start a conversation with the NPC. | Have an active session with `SessionFacadeType::CONVERSATION` after starting. |
| Ensure the NPC has a valid conversation template registered with the correct CRC. | Select an option in the conversation. | The session's `lastConversationScreen` should be updated after each screen is sent. |
| Ensure the player is within conversation range of the NPC. | End the conversation via `stopConversation=true`. | Receive a `StopNpcConversation` packet. |
| Ensure the NPC has a valid conversation template registered with the correct CRC. | Start a conversation with the NPC. | If the screen specifies animations, both NPC and player should play them. |
| Ensure the player is within conversation range of the NPC. | Start a conversation with the NPC. | For Lua conversations, the `DirectorManager` must have the appropriate Lua class handler and screen scripts loaded. |
| Ensure the NPC has a valid conversation template registered with the correct CRC. | Start a conversation with the NPC. | The player should receive an `NpcConversationMessage` packet with the NPC's dialog text, followed by a `StringList` packet containing the option texts. |
| Ensure the player is within conversation range of the NPC. | Start a conversation with the NPC. | Have an active session with `SessionFacadeType::CONVERSATION` after starting. |

## pets-droids

| Setup | Bot does | Expect |
|---|---|---|
| Player has `outdoors_creaturehandler_novice` (or god mode) and a valid PetControlDevice in inventory. | Radial menu on PetControlDevice → select call (ID 44) | System message: 'Calling pet in 15 seconds. Combat will terminate pet call.' + 15 s delay if outdoors; immediate spawn if in city/camp. |
| Player is not in combat, not dead, not taming, not in private building/FRS enclave. | Wait for spawn (or skip if city) | Pet appears at player position ±2-3 m. Pet faces owner. Ghost has active pet (`ghost->addToActivePets` at `PetControlDeviceImplementation.cpp:468`). |
| Pet is spawned and visible. | Radial menu on pet → select follow (or chat 'pet follow') | Pet sets movement state to FOLLOWING if was resting. No system message expected. |
| Pet is in FOLLOWING state. | Move away from pet | Pet follows. Check distance at various intervals (no server-side enforcement visible in files). |
| Pet is in FOLLOWING state. | Radial menu on pet → select stay (or chat 'pet stay') | Pet stops moving. No system message expected. |
| Pet is in STAY state. | Radial menu on pet → select guard (or chat 'pet guard') | Pet guards target (player if none specified). No system message expected. |
| Pet is in GUARD state. | Radial menu on PetControlDevice → select store (ID 59) or chat 'pet store' | Pet disappears from world, reappears in PetControlDevice. For faction pets: 'Storing pet in 60 seconds' then stores. System message on completion not in these files. |
| Pet is stored in PetControlDevice. | Check PetControlDevice state | Pet is no longer active, PetControlDevice contains pet again. |

## player-cities

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Use the City Hall deed at a valid location. | A "New City Established!" mail to the mayor (line 218). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Use the City Hall deed at a valid location. | A new CityRegion object created and persisted (line 198). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Use the City Hall deed at a valid location. | The city at OUTPOST rank (line 204). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Have citizens register with the city. | Mayor receives "City Growth: Added Citizen" mail (lines 1423-1428). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Have citizens register with the city. | New citizen receives "Welcome, Citizen!" mail (lines 1430-1436). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Have citizens register with the city. | `city->getCitizenCount()` increases. |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Wait for the grace period to expire with enough citizens. | Mayor receives "New City Approved!" mail (lines 733-737). |
| Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus). Have the bot character use a City Hall deed at a valid location (not within  | Wait for the grace period to expire with enough citizens. | `city->hasAssessmentPending()` becomes false (line 739). |

## player-vendors

| Setup | Bot does | Expect |
|---|---|---|
| Owner must exist: The vendor's ownerId must be set to a valid player object ID. | Attempt to register the vendor. | System message @player_structure:register_vendor_not appears. |
| Vendor must be in a zone: The vendor's zone must not be null. | Attempt to register the vendor. | vendorData->registered becomes true. |
| Owner must have credits: The owner's bank and cash credits must be sufficient for maintenance payment. | Attempt to pay maintenance with a value greater than 100,000. | System message @player_structure:vendor_maint_invalid appears. |
| Vendor must not be empty for registration: The vendor must have items to register. | Attempt to register the vendor. | System message @player_structure:register_vendor_not appears. |
| Maintenance payment is successful. | Attempt to pay maintenance with a valid value. | Owner's bank/cash credits decrease by the paid amount. |
| Maintenance payment is successful. | Attempt to pay maintenance with a valid value. | vendorData->maintAmount increases by the paid amount. |
| Maintenance payment is successful. | Attempt to pay maintenance with a valid value. | System message @player_structure:vendor_maint_accepted appears with new maint amount. |
| Maintenance withdrawal is attempted. | Attempt to withdraw maintenance with a value greater than maintAmount. | System message @player_structure:vendor_withdraw_fail appears. |

## pvp-tef-duels

| Setup | Bot does | Expect |
|---|---|---|
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Neither bot is in a no-duel area (check `getActiveAreas()` for areas where `isNoDuelArea()` returns true). |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Neither bot ignores the other's first name. |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Bot A receives system message `duel/challenge_self` with Bot B's object ID. |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Bot B receives system message `duel/challenge_target` with Bot A's object ID. |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | `areInDuel(A, B)` returns false (neither side has accepted yet). |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Both bots receive `duel/accept_self` and `duel/accept_target` messages respectively. |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | Both bots' PVP status bitmasks include `ObjectFlag::ATTACKABLE \| ObjectFlag::AGGRESSIVE`. |
| Ensure both bots are CreatureObjects and players (not pets/vehicles). | Position bots within 25 meters of each other. | `areInDuel(A, B)` returns true. |

## quests

| Setup | Bot does | Expect |
|---|---|---|
| Tatooine is enabled. | Converse with Han. | The first screen is 'first_screen', with options 'Why' and 'What if I don't want to?' |
| Tatooine is enabled and the character has no 'tutorial_one' state. | Choose 'Why', 'It's what I need to do, count me in!', 'What's the deal', 'Go on', 'I'm on my way'. | The screen 'accept_task_one' closes the conversation, 'tutorial_one' bit 1 is set, sound 'ui_npe2_quest_received.snd' plays, and the system message 'Quest received: Checking the Falcon.' arrives with  |
| Tatooine is enabled and the character has 'tutorial_one' state 1. | Walk within 40 m of 3863, -4856. | The system message '<Communicator> Ok Kid, looks like she's all in one piece...' arrives, sound 'ui_quest_waypoint_patrol.snd' plays, 'tutorial_one' bit 1 is cleared and bit 2 is set. |
| Tatoo,ine is enabled and the character has 'tutorial_one' state 2. | Return to Han and converse. | +10,000 cash credits, sound 'ui_npe2_quest_credits.snd', the message 'Quest completed: Checking the Falcon.', state becomes 4, and the screen is 'task_one_complete'. |
| Tatooine is enabled and the character has 'tutorial_one' state 4. | Converse again. | The screen is 'quest_complete', 'Did you ever meet Lando in Theed?' |
| Tatooine is enabled and the character has 'tutorial_one' state 4. | Check cash credits. | Cash rises by exactly 10000. |
| Tatooine is enabled and the character has 'tutorial_one' state 1. | Talk to Han again. | The screen 'task_one_active' shows 'Have you checked the Falcon yet?' |
| Tatooine is enabled and the character has 'tutorial_one' state 2. | Check system messages. | The three system messages arrive in order: 'Quest received: Checking the Falcon.', '<Communicator> Ok Kid, looks like she's all in one piece...', 'Quest completed: Checking the Falcon.' |

## resource-quality

| Setup | Bot does | Expect |
|---|---|---|
| Fix the crafter's `weapon_assembly`, `weapon_experimentation` and `luck`. Remove food buffs and city bonuses, and use a tool whose effectiveness is known. | Use `/resource perfect <type>` to create a spawn with every applicable stat at 1000. | The resource spawn has every applicable stat at 1000. |
| Use `/resource create <name> [quantity]` to give an existing spawn, and `/resource info <name>` to read its stats. | Use the same spawn in every resource slot for the basic case, and a different spawn per slot for the averaging case. | The resource slots are filled with the same spawn for the basic case and different spawns for the averaging case. |
| After many experiment points on a group. | Observe the experiment results. | No line goes past min + (max − min) × weightedSum / 1000. |
| Use perfect resources. | Perform an experiment with perfect resources. | The ceiling equals the template max. |
| Use the same spawn in every resource slot. | Perform an experiment. | The starting value lies between assemblyPct × 0.4 and assemblyPct × 1.05 of the range. |
| Use a filled resource slot. | Attempt to add a second, different resource to a filled slot. | A second, different resource cannot be added to a filled slot. |
| Perform an experiment with resources. | Observe the experiment result message and the change in value. | The change in value equals step × points × range. |
| Perform an experiment with resources. | Observe the result tier reported. | The result tier is random, and the formula for the tier is reported. |

## resources

| Setup | Bot does | Expect |
|---|---|---|
| tre archive in place, zone in activeZones | Check server log for "Resource Map Built with N resources" and verify pool lines with Spawned > 0 | Server log shows "Resource Map Built with N resources" and pool lines with Spawned > 0 |
| tre archive in place, zone in activeZones | Use survey tool to check resource list on the planet | Survey tool's resource list shows only in-shift spawns of that tool's type |
| tre archive in place, zone in activeZones | For Hoth/Ossus, check for one `*_hoth` / `*_ossus` spawn per minimum-pool entry | One `*_hoth` / `*_ossus` spawn per minimum-pool entry is present |
| averageShiftTime set to low or despawn path called | Check that the old name is gone from the zone list and the same pool slot has a new name | Old name is gone from the zone list and the same pool slot has a new name |
| averageShiftTime set to low or despawn path called | Verify that the old name still resolves globally | Old name still resolves globally |
| Place harvester at a point with survey density ≥ 0.10, select the spawn, add power and maintenance, and activate | After T seconds, read the hopper quantity | Hopper quantity is about T/60 * density * extractionRate |
| Place harvester at a point with survey density ≥ 0.10, select the spawn, add power and maintenance, and activate | Check that power and maintenance drop by rate × hours | Power and maintenance drop by rate × hours |
| Sample twice the same spawn | Confirm there is one container whose quantity equals the sum | One container whose quantity equals the sum is present |

## sandbox-creatures

| Setup | Bot does | Expect |
|---|---|---|
| Access to the sandbox test datapad interface | Use the datapad menu to spawn a creature from the sandbox data | System message confirming creature spawn success |
| Player character in a valid location for spawning | Use the datapad menu to spawn a creature from the sandbox data | Creature attributes matching the listed levels |
| Sufficient skill/permissions to use the spawn menu | Use the datapad menu to spawn a creature from the sandbox data | Inventory or state changes indicating the creature was successfully spawned |

## scout-xp-sources

| Setup | Bot does | Expect |
|---|---|---|
| Kill a creature and wait for it to become dead (posture DEAD). | Verify corpse has resources: check `getMeatType()`, `getHideType()`, or `getBoneType()` are non-empty. | Corpse has resources (non-empty meat, hide, or bone type). |
| Position within 7 meters of corpse. | Call HarvestCorpseCommand with argument 'meat', 'hide', or 'bone' (or empty for random). | System message showing quantity extracted and resource type (e.g., '@skl_use:creature_quality_fat' with DI=quantity, TU=resource class). |
| Kill a creature and wait for it to become dead (posture DEAD). | Verify corpse has resources: check `getMeatType()`, `getHideType()`, or `getBone,Type()` are non-empty. | Scout XP awarded: verify via `playerManager->awardExperience` call at line 1055. |
| Kill a creature and wait for it to become dead (posture DEAD). | Verify corpse has resources: check `getMeatType()`, `getHideType()`, or `getBoneType()` are non-empty. | Corpse marked as harvested for player: `addAlreadyHarvested(player)` at line 1057 (subsequent harvest attempts should fail with 'This creature has no resources' or similar). |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1. | Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory. | System message '@trap/trap:trap_no_skill' if trapping skill < 1 or no outdoors_scout_novice (lines 26, 91). |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1. | Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory. | System message '@trap/trap:trap_no_skill_this' if trapping skill < trap's required skill (line 120). |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1. | Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory. | System message 'target_range_prose' if out of range (lines 111-114). |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1. | Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory. | System message '@trap/trap:sys_not_ready' if cooldown or pending task exists (line 47). |

## secure-trade

| Setup | Bot does | Expect |
|---|---|---|
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Send `BeginTradeMessage` with the target player's ID. | The target receives a trade window prompt (system message or SUI window). |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | The target accepts the trade. | Both players see an open trade window showing empty item slots and credit fields. |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Send `AddItemMessageCallback` with a valid object ID. | The item appears in that player's side of the trade window on both clients. |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Send `GiveMoneyMessageCallback` with a credit amount. | The credit field updates on both sides and the sender's credit balance decreases. |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Both players click 'Accept'. | The 'Verify' button becomes active for both players. |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Both players click 'Verify'. | The trade completes (items and credits are transferred to final destinations). |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Either player clicks 'Abort'. | The trade window closes, all items return to original inventories, credits restore, and a system message indicates the trade was aborted. |
| Ensure both bot characters are within trade range and have no existing active trade session. Have credits and test items in inventory before starting. | Verify `TradeSession` fields. | `tradeTargetPlayer` matches the other player's ID, `itemsToTrade` contains added objects, `moneyToTrade` matches sent amount, `acceptedTrade` and `verifiedTrade` flags are true when expected. |

## skills-training

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the test creature is a player creature with a valid `PlayerObject` ghost. | Attempt to learn the target skill. | System messages: none explicit in these files for success (inferred: client likely shows its own UI message). |
| Verify the creature has the prerequisite skill(s) and species required by the target skill. | Attempt to learn the target skill. | Skill list: `creature->hasSkill(skillName)` returns true. |
| Confirm the creature has enough XP of the skill's type (check via `ghost->getExperience(skill->getXpType())`) | Attempt to learn the target skill. | XP balance: `ghost->getExperience(skill->getXpType())` decreased by `skill->getXpCost()`. |
| Confirm the creature has enough free skill points (`ghost->getSkillPoints() >= skill->getSkillPointsRequired()`) | Attempt to learn the target skill. | Skill points: `ghost->getSkillPoints()` decreased by `skill->getSkillPointsRequired()`. |
| For Jedi skills, ensure Jedi state >= skill's required level and any Jedi-tree prerequisites are met. | Attempt to learn the target skill. | Skill modifiers: verify via `creature->getSkillMod(SkillModManager::SKILLBOX, modifierKey)` that each key from `skill->getSkillModifiers()` is present with the expected value. |
| For pilot skills, note that `/surrenderskill` will block with a SUI dialog; test must handle or avoid this path. | Attempt to surrender the skill. | Skill list: `creature->hasSkill(skillName)` returns false. |
| Check if the skill has abilities (`skill->getAbilities()`) | Attempt to learn the target skill. | Abilities: `ghost->hasAbility(abilityName)` returns true for each ability in `skill->getAbilities()`. |
| Check if the skill grants draft schematics via `SchematicMap` | Attempt to learn the target skill. | Draft schematics: check via `SchematicMap` (not directly observable without its API; inferred: schematics should be granted). |

## slicing

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Attempt a successful slice with the correct cable sequence. | System message confirms success and XP is awarded for the 'slicing' experience type. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Attempt a failed slice with the wrong first cable selection. | System message confirms failure and the Precision Laser Knife charge is consumed. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Attempt a failed slice with the wrong second cable selection. | System message confirms failure and the Precision Laser Knife charge is consumed. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Attempt a slice without a Precision Laser Knife. | System message shows 'no_knife' and the slicing action fails. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Attempt a weapon/armor slice without an upgrade kit. | System message shows an appropriate message and the slicing action fails. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher and the target object is in inventory. | Use Molecular Clamp to reveal the correct cable, then attempt a successful slice. | System message confirms success and XP is awarded for the 'slicing' experience type. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher and the target object is in inventory. | Use Flow Analyzer to reveal the correct cable, then attempt a successful slice. | System message confirms success and XP is awarded for the 'slicing' experience type. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher and the target object is in inventory. | Attempt a slice and observe the SUI menu for the slicing phase. | The slicing menu appears with correct options for the phase. |

## structure-placement

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot character is not riding a mount and is outside any building. | Attempt to place a structure using the PlaceStructureCommand. | System messages sent during the test match expected message string IDs. |
| Verify the bot has the required deed in inventory. | Attempt to place a structure using the PlaceStructureCommand. | The deed is no longer in the bot's inventory after a successful placement. |
| Confirm the bot has sufficient lots for the structure. | Attempt to place a structure using the PlaceStructureCommand. | The bot's remaining lots decreased by the structure's lot size. |
| If testing a faction deed, ensure the bot's faction matches the deed's faction. | Attempt to place a structure using the PlaceStructureCommand. | System messages sent during the test match expected message string IDs. |
| If testing city requirements, ensure the bot is in the correct city with sufficient rank and zoning rights. | Attempt to place a structure using the PlaceStructureCommand. | System messages sent during the test match expected message string IDs. |
| Attempt placement in a no-build zone. | Attempt to place a structure using the PlaceStructureCommand. | @player_structure:not_permitted is received. |
| Check for the absence of error messages and presence of the new structure object. | Attempt to place a structure using the PlaceStructureCommand. | A structure object exists at the target coordinates with the correct template, rotation, and owner. |
| Check that the structure's owner matches the bot's object ID. | Attempt to place a structure using the PlaceStructureCommand. | structureObject->getOwnerObjectID() matches the bot's object ID. |

## structure-upkeep

| Setup | Bot does | Expect |
|---|---|---|
| A structure with known `getBaseMaintenanceRate()` > 0 | Call `getMaintenanceRate()` | The returned value matches the expected value based on template base rate, config multiplier, and skill mod |
| A structure with known `getBaseMaintenanceRate()` > 0 | Wait for maintenance pool to deplete | Structure condition decreases proportionally as per line 587 |
| A structure with known `getBaseMaintenanceRate()` > 0 | Query `getDecayPercentage()` | The returned value matches `(maxCond - conditionDamage) * 100 / maxCond` as per lines 644-652 |
| Players on each list, guild members, and privileged players | Call `isOnAdminList()`, `isOnEntryList()`, `isOnBanList()`, `isOnHopperList()` | The method returns true for players on the respective list |
| A credit object with known cash/bank balance | Call `payMaintenance()` with `cashFirst=true` | The cash balance is deducted first, then the bank balance as per lines 670-686 |

## survey-sample

| Setup | Bot does | Expect |
|---|---|---|
| The bot has a surveying mod of 20 or more and the survey ability. | Call the surveying function. | The list message arrives, and every entry's class fits the tool. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestSurvey. | start_survey arrives with the name. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestSurvey. | Results arrive within about 4 s, with points² values (9, 16 or 25). |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestSurvey. | Mind drops by about 100 - focus/15. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestSurvey. | The waypoint and survey_waypoint appear only when the best point is 10% or more. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestCoreSample at a spot of 10% or more. | start_sampling arrives, the bot is crouched and action drops by about 124 - quickness/12.5. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestCoreSample at a spot of 10% or more. | About 3 s later, exactly one of these arrives: sample_located (%DI equals the units gained in inventory), trace_amount, sample_failed, efficiency_too_low or density_below_threshold. |
| The bot has a surveying mod of 20 or more and the survey ability. | Call requestCoreSample at a spot of 10% or more. | Another result follows about 25 s later. |

## travel-shuttles

| Setup | Bot does | Expect |
|---|---|---|
| The server has been up longer than BootDelay. The bot is ≤8 m from the terminal; starport terminals are indoors and need locate. The bot has enough credits, fre | Purchase a shuttle ticket. | Exactly one new ticket item (two if a round trip); credits down by the fare plus any tax; the pay-success message; the ticket_purchase_complete SUI. |
| The bot is ≤25 m from the shuttle and has a ticket in inventory. | Use collector option 20 to board the shuttle. | The zone or position changed to within landingRange of the arrival point, and the ticket left the inventory. |
| The bot has multiple tickets in inventory. | Answer the list of tickets when prompted. | The bot selects the correct ticket for boarding. |
| The shuttle displays 'ready to board in N'. | Wait N+6 s and retry boarding. | The shuttle is ready to board, and the bot can proceed with boarding. |

## vehicle-mount

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player has a datapad slotted (`getSlottedObject("datapad")`). | Check if the player has a vehicle deed in inventory. | Datapad contains a new VehicleControlDevice object. |
| Ensure the player has a datapad slotted (`getSlottedObject("datapad")`). | Generate a vehicle deed using the datapad. | System message: none (success is silent). |
| Ensure the player has a datapad slotted (`getSlotted,edObject("datapad")`). | Generate a vehicle deed using the datapad. | Deed no longer exists in inventory or world. |
| Ensure the player is outdoors and not in combat. | Call the vehicle using the datapad. | System message: "pet/pet_menu:call_vehicle_delay" with "15" seconds. |
| Ensure the player is outdoors and not in combat. | Call the vehicle using the datapad. | After 15 seconds, a VehicleObject appears at player position. |
| Ensure the player is indoors or in a city region. | Call the vehicle using the datapad. | System message: none (instant spawn). |
| Ensure the player is outdoors and not in combat. | Call the vehicle using the datapad. | VehicleObject appears immediately. |
| Ensure the player is outdoors and not in combat. | Mount the vehicle. | Player state changes to `RIDINGMOUNT`. |

## veteran-rewards

| Setup | Bot does | Expect |
|---|---|---|
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | System message showing account age in days (GetVeteranRewardTimeCommand.h:48) |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | If eligible: system message with milestone number and claim prompt (GetVeteranRewardTimeCommand.h:58) |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | If not eligible: 'not_eligible' message plus next milestone countdown (GetVeteranRewardTimeCommand.h:69,73-74) |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | Character play time message at the end (GetVeteranRewardTimeCommand.h:79) |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /claimVeteranReward | SUI list box appears with reward options |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /claimVeteranReward | Reward item should appear in player's inventory or be delivered via mail |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | If oneTime is true, subsequent checks should show no new eligible milestone for that day count |
| Create or use an account with known age (or manipulate test environment to simulate account age). Ensure the account has reached at least one milestone threshol | /getVeteranRewardTime | For 180+ day accounts: JTL yacht announcement message appears (GetVeteranRewardTimeCommand.h:65) |

## weather

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the planet has hasDamagingSandstorms=1 (e.g., Tatooine or Lok) and the player is not in shelter, camping, or riding a mount. | Use the /server weather change 4 command to force weather to EXTREMESTORM. | System message: "The weather around you quickly becomes damaging, seek shelter immediately." |
| Ensure the player is not wearing any protective clothing. | Wait for the storm to damage the player. | Player state: blinded state set to 60 seconds. |
| Ensure the player is not wearing any protective clothing. | Wait for the storm to damage the player. | Player posture: KNOCKEDDOWN. |
| Ensure the player is not wearing any protective clothing. | Wait for the storm to damage the player. | HAM bar damage: HEALTH, ACTION, MIND attributes decreased by `sandstormDamage - totalCoverings`. |
| Ensure the planet has hasDamagingSandstorms=1 (e.g., Tatooine or Lok). | Use the /server weather info command. | Weather ID change visible via /server weather info command output. |
| Ensure the player is not in shelter, camping, or riding a mount. | Use the /server weather change 4 command to force weather to EXTREMESTORM. | System message: "The storm has subsided." |
| Ensure the player is not in shelter, camping, or riding a mount. | Use the /server weather change 4 command to force weather to EXTREMESTORM. | Player state: blinded state set to 60 seconds. |
| Ensure the player is not in shelter, camping, or riding a mount. | Use the /server weather change 4 command to force weather to EXTREMESTORM. | Player posture: KNOCKEDDOWN. |

## world-bosses

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the server has been running long enough for at least one boss to spawn (wait > 120 seconds, or trigger slot filling manually if possible). | Wait for the server to spawn a boss. | A boss should spawn in the designated zone. |
| Verify that the zone containing the target planet is enabled (`isZoneEnabled` check at line 99). | Check if the zone is enabled. | The zone should be enabled. |
| Confirm the big game hunter NPC exists on tatooine at the expected coordinates. | Locate the big game hunter NPC on tatooine. | The big game hunter NPC should be present at the expected coordinates. |
| After a boss dies, check that damaged players receive the credit system message. | Kill a boss and observe the system message. | The system message ` |
| Verify the broadcast text format at spawn, death, and escape. | Observe the broadcast text during boss spawn, death, and escape. | The broadcast text should follow the format at spawn, death, and escape, with the color code `\#ffcc66` rendering as orange. |
| Confirm that `addBankCredits(25000, true)` increases the player's bank balance by exactly 25,000. | Use the `addBankCredits(25000, true)` command and check the player's bank balance. | The player's bank balance should increase by exactly 25,000. |
| Check that a spawned boss has a custom object name ending with `(world boss)`. | Inspect the spawned boss's object name. | The boss's object name should end with `(world boss)`. |
| Check that the boss's HAM pools are multiplied correctly. | Verify the HAM pools of the spawned boss. | The boss's HAM pools should be multiplied correctly, with ham 4 boss having 4× the base template's maxHAM for health, action, and mind. |

