# Local model: test-index (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 62 input lines. A local model's draft: check each item before acting on it.

Steps drafted from section 3 of each research report. Check a step against its report before a scenario uses it.

## badges

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player character is logged in and has a valid PlayerObject ghost slot. | Use the server console command `/grantBadge [badgeId]` to award a new badge. | A system message under the `badge_n` category with prose key `prose_grant`. |
| Ensure the player character has already been awarded the specific `[badgeId]`. | Use the server console command `/grantBadge [badgeId]` again to attempt a duplicate award. | A system message under the `badge_n` category with prose key `prose_hasbadge`. |
| Ensure the player character has been awarded a badge with non-'NONE' music. | Observe client-side network traffic after the award. | A `PlayMusicMessage` is received on the client side. |
| Ensure the player character has been awarded a new badge. | Query the player's PlayerObject (slotted as 'ghost' on CreatureObject) and call `hasBadge(badgeId)`. | `hasBadge(badgeId)` returns true, confirming the specific badge is set. |
| Ensure the player character has been awarded a new badge. | Query the player's PlayerObject and call `getNumBadges()` before and after the award. | `getNumBadges()` verifies total count increased by 1. |
| Ensure the player character has been awarded a new badge of a specific type. | Query the player's PlayerObject and call `getTypeCount(type)` before and after the award. | `getTypeCount(type)` verifies the correct type counter incremented. |
| Award badges to the player until a milestone count is reached. | Check the player's badge ownership for the corresponding ` |  |

## bank-tips

| Setup | Bot does | Expect |
|---|---|---|
| Place two bot characters on the same planet, within 8 m of a bank terminal and/or within 190 m of each other. | Ensure both bots have non-zero cash and/or bank credits using `getCashCredits()` / `getBankCredits()`. | Bots have valid credit balances. |
| Ensure both bots are online to take the cash-tip path. | Send `/tip <other_bot> 100` from the sender bot. | Sender's cash decreases by exactly 100, receiver's cash increases by exactly 100, and both receive system messages matching prose IDs `prose_tip_pass_self` and `prose_tip_pass_target`. |
| Set sender bot to have insufficient cash (e.g., only 500 cash). | Send `/tip <other_bot> 999999`. | The tip is rejected due to insufficient funds. |
| Position bots more than 190 m apart. | Send `/tip <other_bot> 100`. | The tip is rejected due to distance > 190 m. |
| Ensure one bot is offline to force the bank-tip path, or use online bots if bank transfer is supported while online. | Send `/tip <other_bot> 100 bank` from the sender bot. | A confirmation SUI box appears on the sender with title `"Confirm Bank Transfer"` and the appropriate prompt (5 % surcharge or no-fee message if same account). |
| Have the confirmation SUI box open for a bank tip. | Press Cancel in the SUI box. | Balances remain unchanged. |
| Have the confirmation SUI box open for a bank tip. | Press OK in the SUI box. | Sender's bank credits are deducted, receiver's cash (or bank) is added, and both receive success messages. |
| Set sender bot to have insufficient bank funds. | Send `/tip <other_bot> 100 bank`. | The tip is rejected due to insufficient bank funds. |

## bazaar-flow

| Setup | Bot does | Expect |
|---|---|---|
| Ensure player has a valid CreatureObject reference and a valid bazaar terminal TangibleObject exists and is accessible. | Verify the vendor object type by calling `vendor->isBazaarTerminal()`. | `vendor->isBazaarTerminal()` returns true. |
| Player initiates an auction query via the bazaar terminal. | Observe the incoming response message from the server. | A response message with opcode `0xFA500E52` is received. |
| Player performs a search that returns multiple items. | Inspect the item list in the query response headers. | Item list contains expected entries with correct prices, expiration times, and owner names matching the structure defined in AuctionQueryHeadersResponseMessage.h:94-138. |
| Player performs a search with pagination parameters. | Check the pagination fields in the `AuctionQueryHeadersResponseMessage`. | Pagination offset and continues flag work correctly as defined in AuctionQueryHeadersResponseMessage.h:149-151. |
| Player lists an item for immediate sale via the bazaar terminal. | Check the byte indicating auction type in the response or internal state. | The isAuction byte distinguishes instant sale (1) from auction (0) at lines 103-106. |

## bounty-hunter

| Setup | Bot does | Expect |
|---|---|---|
| Accept a bounty mission of at least level 2. Speak to the informant until objectiveStatus reaches HASTALKED (informantLevel > 1). Ensure the player is not mount | Check for the existence of a waypoint with the correct planet and position. | The system message "@mission/mission_generic:target_location_received" was sent. |
| Use an Arakyd droid item. | Observe the countdown messages at t=20, 3, 2, 1, and arrival. | A "probot" NPC spawns at the landing coordinates and objective's activeDroid is set. |
| After Arakyd arrives, use the TRANSMITBIOLOGICALSIGNATURE action. | Observe the droid sitting briefly then despawning. | A search/tracking result message appears within the calculated time. |
| Use Seeker droid items for FINDTARGET / FINDANDTRACKTARGET. | Observe the "seeker" NPC spawning at the player, sitting for 5 seconds, then despawning. | Success/failure messages appear and, on success, distance/direction or target name is shown. |
| Test with varying droid_find_chance / droid_track_chance skill mods. | Verify the success formula (skillMod − targetLevel/3, clamped 5–95) and time formula (150 − skillMod + random). | The calculated success and time values match the observed outcomes. |
| Kill the spawned NPC target. | Verify the bounty hunter receives the loot. | complete() is called, XP is awarded as "bountyhunter" with value (rewardCredits + bonusCredits) / 50, and the mission status updates to TARGETELIMINATEDSTATUS. |
| Have a target player perform actions near other creatures to increase visibility. | Verify they appear on bounty hunter terminals when visibility ≥ terminalVisThreshold and disappear when below falloffThreshold. | After killing the target, clearVisibility() sets visibility to 0. |

## camps

| Setup | Bot does | Expect |
|---|---|---|
| Player has 'camp' skill mod at or above target level, is in outdoor non-city non-water location, not in combat/sitting/riding/in cell, and no other camps/buildi | Attempt to place a camp. | System message "@camp:starting_camp" appears. |
| Camp placement initiated. | Wait for completion. | System message "@camp:camp_complete" appears, a camp structure object exists at player position, and a terminal child object exists with custom name "FirstName LastName's Camp". |
| Player is inside the placed camp. | Observe system messages upon entering. | System message with prose_camp_enter containing terminal name appears, and system message "@camp:sys_camp_heal" appears. |
| Player is inside the camp. | Trigger a heal event on the player. | Verify currentXp increments by (campStructureData->getExperience() / 180) per heal. |
| Owner exits the camp. | Wait approximately 60 seconds. | Terminal name changes to "Abandoned Camp", campFire object changes appearance to "campfire_smoldering.iff", and owner receives "@camp:sys_abandoned_camp". |
| Camp is abandoned. | Interact with the abandoned terminal. | "assume ownership" menu option appears. |
| Player assumes ownership of the camp. | Verify state changes. | Terminal name reverts to owner's name, abandoned flag is false, and owner receives "@camp:assuming_ownership". |
| Owner interacts with terminal. | Select disband option. | Camp structure and active area are destroyed. |

## combat-states

| Setup | Bot does | Expect |
|---|---|---|
| Ensure attacker has appropriate accuracy skills for state-only attacks. | Attack a target with varying levels of defense skill mods. | Verify system messages and flytexts appear on both attacker and target at the correct times. |
| Target is in an upright posture before the attack. | Perform a knockdown/posture test attack. | Monitor via getPosture() for CreaturePosture::KNOCKEDDOWN or other posture values. |
| Target has been subjected to state-inducing attacks. | Check target's state bitmask using hasState() or hasBuff(). | Verify presence of CreatureState::DIZZY, STUNNED, BLINDED, INTIMIDATED, IMMOBILIZED, FROZEN. |
| Target is in a posture state (e.g., knocked down). | Check cooldown timers for posture recovery. | Verify cooldown timers are active and counting down correctly. |
| Target has an active state with a known duration. | Check state bitmask over time after the expected duration passes. | Confirm states wear off (bitmask no longer contains the specific CreatureState flags). |

## containers-inventory

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the creature has a valid zone and parent hierarchy. | Confirm the destination container is reachable within 16.5 distance units (unless it is a building or cell object). | The path to the container is valid. |
| For wearable items, verify the creature's race/faction and skill list match the item's requirements. | Attempt to transfer the item. | The transfer succeeds if requirements are met, or fails with appropriate error if not. |
| Fill the destination inventory to capacity. | Attempt to transfer an item to the full inventory. | The creature receives system message "@container_error_message:container03". |
| Before attempting a transfer, call canAddObject on the inventory with containmentType = -1. | Check the return value of canAddObject. | A return value of TransferErrorCode::CONTAINERFULL confirms the limit is reached; a return of 0 means space exists. |
| Query the destination container's current state. | Call sceneObject->getContainerObjects()->size() and compare to sceneObject->getContainerVolumeLimit(). | The difference represents the remaining slots available. |
| For equipment slots (containmentType >= 4), ensure the slot descriptor is already taken. | Call canAddObject for the item targeting that slot. | canAddObject returns SLOTOCCUPIED. |
| Ensure there is insufficient space in the destination container. | Use removeObject on the destination container to free slots, or move items to another container (e.g., bank). | Subsequent call to canAddObject returns 0 (space exists). |

## contraband-scans

| Setup | Bot does | Expect |
|---|---|---|
| Create an AI agent scanner with FACTIONIMPERIAL faction. | Have a player creature (not in combat, not dead) carrying contraband items initiate a scan multiple times to test the 1/12 chance. | Cooldowns 'crackdown_scan' are set on both player and scanner. |
| Player is riding a mount when scanned. | Initiate a contraband scan. | Player dismounts and receives a system message. |
| Player has sufficient smuggler skills. | Initiate a contraband scan. | Player receives '@base_player:smuggler_scan_success' and no further scan messages. |
| Player is a Padawan or higher with Jedi mind trick ability. | Initiate a contraband scan and attempt to use mind trick. | On success, player sees 'probe_scan_done' system message and scanner leaves. |
| Player belongs to the opposite faction of the scanner (e.g., Rebel vs Imperial). | Initiate a contraband scan. | Player receives 'discovered_imperial' or 'discovered_rebel', status changes to COVERT/OVERT, and Lambda shuttle combat begins. |
| Player is carrying contraband items. | Initiate a contraband scan and accept the fine via SUI window. | SUI window appears with correct credit amount; credits are deducted from cash/bank with TransactionLog FINES entries. |
| Player is carrying contraband items. | Initiate a contraband scan and refuse or time out on the fine. | Faction standing decreases. |
| Contraband scan results in discovery for opposite faction. | Wait for reinforcement spawn logic to trigger. | Lambda shuttle spawns at nearest valid spawn point and starts combat. |

## core3-bug-comments

| Setup | Bot does | Expect |
|---|---|---|
| Player character in a ship, initiate hyperspace travel. | Monitor client connection status during hyperspace. | Client remains responsive (no crash) |
| Complete zone transition scenarios for the ship. | Observe the ship's appearance and object instances in the new zone. | Ship appears correctly in new zone, no duplicate objects visible |
| Board/unboard ships during zone transitions. | Execute pilot insertion commands. | Pilot insertion succeeds without errors |
| Place city decorations near POI entrances/exits. | Observe NPC pathing to the POI area. | NPCs and players can still access the POI area, pathfinding works correctly around decorations |
| Initiate tank vs tank combat scenarios. | Monitor damage calculations between tanks. | TanO vs TanO damage calculations occur |
| Engage in unskilled player combat encounters. | Check skill modifiers applied to the unskilled player. | Unskilled players receive appropriate combat penalties |
| Attempt to slice an object with an active lock. | Wait for lock expiration and attempt slicing again. | Lock duration functions correctly (1 hour), slicing succeeds after lock expires |
| Make multiple login attempts and admin connection scenarios. | Verify API responses and monitor for crash reports. | Login completes without crashes, clear error messages displayed on failure |

## crafting

| Setup | Bot does | Expect |
|---|---|---|
| Equip skills granting schematic group plus assembly/experimentation mods; place matching tool in inventory (not busy/finished); ensure station of same type with | Set Core3.Sandbox.CraftSeconds to shorten wait time. | System configured with reduced craft seconds. |
| Use forceCriticalAssembly / forceCriticalExperiment on the tool. | Initiate assembly or experimentation. | Tool state reflects forced critical roll for repeatable results. |
| Perform an assembly action. | Observe the result code. | Result code is 0x109. For Amazing quality, verify start = W x (0.000015W + 0.015) x 0.01 x 1.05. |
| Perform an experimentation action. | Observe the result and remaining points. | Result code is 0x105; observe the specific experiment result value and remaining points. |
| Complete a successful craft or experiment. | Check for system messages. | Receive message "@system_msg:prototype_transferred". |
| Inspect the resulting item in inventory. | Verify item properties. | Item carries crafter's name, a "(xxxxxxxx)" serial, and a custom name. |
| Check attribute values of the crafted/experimented item. | Verify attribute bounds and percentages. | Attributes are within min/max; percentage never above W/1000. |
| Check XP gain after crafting. | Compare gained XP to expected amount. | XP gained equals xpAmount, or x1.05 for practice runs. |

## crafting-factories

| Setup | Bot does | Expect |
|---|---|---|
| Place a factory object in the world with ingredient_hopper and output_hopper slotted. Ensure player has a valid ManufactureSchematic in datapad (non-null protot | Insert the schematic into the factory. | System message containing '@manf_station:schematic_added' with schematic name. |
| Schematic inserted into factory. | Observe system messages after insertion. | Second system message: 'This schematic limit is: <N>' where N = schematic->getManufactureLimit(). |
| Schematic inserted into factory. | Check the factory container state. | Factory container now has 1 object in slot 0 (the schematic). |
| Schematic inserted and valid ingredients present. | Toggle the factory to start production. | System message '@manf_station:activated'. |
| Factory toggled to start. | Check system messages after activation. | Second system message with limit again. |
| Factory toggled to start. | Check factory state and pending tasks. | Factory isActive() returns true and Pending task 'createFactoryObject' exists with timer * 1000ms delay. |
| Factory is running production. | Wait for each timer interval during production. | Objects appear in output_hopper (check getContainerObjectsSize() > 0). |
| Factory is running with crateSize > 1. | Check the type of objects in output_hopper. | FactoryCrate objects with correct prototype and incrementing useCount. |

## creature-harvest

| Setup | Bot does | Expect |
|---|---|---|
| Position near Mos Eisley (coords 3500-3800, -4800 to -5020) with a guard character having ≥ 80% HAM. | Kill a low-level (≤ 5) wild prey creature (e.g., rockmite) and ensure it is fresh (`posture == 'dead'`) and unharvested. | A system message appears containing the quantity extracted and resource type (e.g., "You extract 12 units of meat from the rockmite"). |
| Ensure the target creature is freshly killed (`posture == 'dead'`) and unharvested. | Perform the harvest action on the corpse. | A new resource container appears in inventory with a name matching the harvested type (meat, hide, or bone). |
| Harvest a corpse that has no loot/credits and where no group members can harvest it. | Wait approximately 1 second after the harvest completes. | The corpse despawns. |
| Harvest a creature of level N. | Check the player's experience points immediately after the harvest. | Scout XP equal to `creature level × 5 + 19` is awarded. |

## cure-poison

| Setup | Bot does | Expect |
|---|---|---|
| Use `/agentgear afflict poison` on a partner player to apply a POISONED DoT (strength 30, HEALTH pool, 120 s). Ensure the tester has a cure pack in inventory an | Use the cure pack on the poisoned partner within 120 s of affliction. | Tester sees system text matching "You apply poison antidote to ". Partner's states lose `poisoned`. Tester's mind drops by about 100. Pack's use count drops by 1. |
| Wait 4-20 s after the successful cure. | Attempt to use the cure pack on the same partner again. | Bot sees string-table message "@healing_response:healing_must_wait". |

## datapad-tools

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot character is an admin/privileged player. | Obtain the datapad item `object/tangible/sandbox/tools_datapad` and use it with a non-admin character (if possible) or verify access control logic. | System message "The test datapad only works for admins." and no menu/action. |
| Be outdoors (not inside a cell). | Select a named planet destination from the datapad menu. | The player's zone name changes to that planet and coordinates match the preset (e.g., Mos Eisley at 3528, -4804). |
| Perform a prior jump to a different location. | Select the "back" teleport option in the datapad menu. | The player returns to the recorded location. |
| Have no prior jump history recorded. | Select the "back" teleport option in the datapad menu. | An error message is displayed (line 183). |
| Be outdoors. | Select a disabled zone destination from the datapad menu. | System message "X is not enabled on this galaxy." (line 204). |
| Be outdoors. | Select a creature from the spawning list in the datapad menu. | A mobile with that template appears ~6m east at world floor. |
| Be indoors (inside a cell). | Select a creature from the spawning list in the datapad menu. | System message "Step outside first: creatures spawn outdoors only." (line 308). |
| Be outdoors. | Select a test kit category from the datapad menu. | All listed items appear in the player's inventory (check slotted object "inventory"). |
| Have just used a test kit category. | Observe the system messages returned by the datapad. | Message reports correct count of given/failed items (line 346). |
| Be outdoors. | Select the "Heal" option from the test kits menu. | HAM pools 0,3,6 are at max, wounds on all pools 0–8 are 0, shock wounds is 0, and no state bits are set. |
| Be outdoors with full HAM pools. | Select the "Damage" option from the test kits menu. | HAM pools 0,3,6 are halved (floor 1). |
| Be outdoors. | Select the "Wounds" option from the test kits menu. | All pools 0–8 have exactly 100 wounds. |
| Be outdoors. | Select the "Fatigue" option from the test kits menu. | Shock wounds equals 200. |
| Be outdoors. | Select the "Poison" or "Disease" option from the test kits menu. | The corresponding state bit (`POISONED` or `DISEASED`) is set and persists for ~120 seconds with tick damage of 100 every 30 seconds. |
| Be outdoors. | Select the "Fire" or "Bleeding" option from the test kits menu. | `ONFIRE` or `BLEEDING` state bit set for ~60 seconds, tick damage 100 every 30 seconds. |
| Perform any of the above actions. | Observe the system messages returned by the datapad. | System message "Test datapad: <description>." appears (line 392). |

## doctor-enhance-wounds

| Setup | Bot does | Expect |
|---|---|---|
| Doctor has `healenhance` command, carries packs with medicine use <= `healing_ability`, has >= 150 mind, stands in any cell of the hospital building. Patient is | Doctor uses `healenhance` on patient to enhance Health. | Doctor sees message "You enhance <name>'s Health by N"; Patient sees message "enhances your". |
| Same setup as above, first buff application. | Doctor uses `healenhance` on patient. | Patient's max HAM rises by the full buff value (inferred from fill-on-buff attribute modifier). |
| Same setup as above, doctor has sufficient mind. | Doctor uses `healenhance` on patient. | Doctor's mind drops by about 150. |
| Patient has wounds. Doctor is within 6 m with line of sight. | Doctor uses `healenhance` to enhance wounds. | Patient's wounds in that pool drop by min(power, wounds). |
| Wait for cooldown to expire after a previous enhancement. | Doctor uses `healenhance` on patient. | System message `healing_response_59` is received. |
| Doctor and patient are outdoors in a city, out of combat. | Doctor attempts to use `healenhance` on patient. | Error message `must_be_near_droid` is returned. |
| Doctor used `healenhance` less than 20 seconds ago. | Doctor attempts to use `healenhance` on patient again. | Error message `enhancement_must_wait` is returned. |
| Patient has already received a Health enhancement buff (re-apply scenario). | Doctor uses `healenhance` on patient to enhance Health again. | No change in patient's max HAM. |

## droid-storage-quality

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player has sufficient crafting skill to craft a droid component and have the correct template (object/tangible/component/droid/item_storage_module_1. | Craft the droid storage module using the specified template. | A system message or crafting preview showing mechanism_quality as a valid positive integer (0 to 15 range based on template lines 52-53), NOT -999999. |
| Craft the droid storage module using the specified template. | Inspect the crafted droid component's attribute list. | The droid component's attribute list includes "mechanism_quality" with a value >= 0 (DroidComponentImplementation.cpp line 63). |
| Craft the droid storage module using the specified template. | Check the storage module rating and its final display-capped value. | The storage module rating is between 1 and 10, and the final display-capped value is <= 10 (DroidItemStorageModuleDataComponent.cpp line 64). |

## easy-destroy

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the group is at a known level and verify effective group level via `getGroupLevel`. | Confirm the terminal's planet zone name matches an expected destroy mission spawn list (e.g., `tatooine_destroy_missions`). | The terminal is valid for destroy missions. |
| Accept a destroy mission from the terminal. | Read `mission->getMissionDifficulty()`. | The difficulty is ≤ 10 and reflects the group level addition. |
| Have an active destroy mission. | Read `mission->getStartPosition()` and compare it to the terminal's position. | The distance is within the expected range for the difficulty. |
| Have an active destroy mission. | Verify `mission->getTargetOptionalTemplate()` matches a lair whose min/max difficulty overlaps the group level ±5. | The target template is valid for the current group level. |
| Interact with the terminal. | Check the mission offer title/description keys. | The keys contain `_easy`/`_medium`/`_hard`. |

## entertainer-buffs

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the patron is grouped with the performer using /group command. | Position the patron within ~10m of the performer with clear line of sight. | The entertainer has private_buff_mind > 0 and healing_dance_mind > 0 as skill mods. |
| Have the patron watch the performer for 60+ seconds while the performer stops. | Check for system messages on the patron confirming watch started (not 'no_line_of_sight'). | A system message confirming watch started is received. |
| Wait for the buff application after 60+ seconds of watching. | Check for a system message containing performance_enhance_dance_mind on the patron. | A system message containing performance_enhance_dance_mind is received. |
| After the buff message appears. | Check that Nima has a buff with CRC STRING_HASHCODE("performance_enhance_dance_mind") using creature->getBuff(). | Nima has the buff and its strength and duration match expectations. |
| During the watching session. | Check via entertainer->getSkillMod("private_buff_mind") and entertainer->getSkillMod("healing_dance_mind"). | Dorn has private_buff_mind > 0 and healing_dance_mind > 0 as skill mods. |
| During the watching session. | Verify Nima is in Dorn's patronDataMap via the entertaining session. | Nima is present in Dorn's patronDataMap. |

## entertainer-xp-sources

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot has `social_entertainer_novice` skill and relevant healing skill mods. | Start an entertaining session with a dance performance (`startDancing(perfIndex)`). | System message: "You begin dancing." |
| Have audience members within range who are watching/listening for at least 60 seconds. | Perform a dance tick without healing. | Check that "dance" XP is awarded per tick (not "music" or "entertainer_healing"). |
| Have audience members within range who are watching/listening for at least 60 seconds. | Wait for 60 seconds of continuous watching. | Audience members gain `performance_enhance_dance_mind` buff. |
| Perform with 0 audience. | Perform a dance tick. | Verify base XP only is awarded. |
| Perform with 50 audience members watching. | Perform a dance tick. | Verify XP is approximately double compared to 0 watchers (audienceMod = 1.0). |
| Be in the middle of a dance tick. | Issue flourish command multiple times within one tick. | Verify only the first flourish adds to `flourishXp` (dance cap = 1). |
| Have an audience member with battle fatigue. | Heal the audience member's battle fatigue during a performance. | Verify "entertainer_healing" XP is awarded. |

## factions

| Setup | Bot does | Expect |
|---|---|---|
| Ensure bot character has no Jedi skills and is neutral (faction = 0) with at least 200 faction standing. | Join the target recruiter's faction. | System message confirming covert status, getFaction() returns recruiter's faction hash, getFactionStatus() returns 1, OVERT PVP flag is not set. |
| Bot is in covert status. | Wait for the 30s timer to expire or trigger overt status. | System message about being attackable, OVERT PVP flag is set, hasCooldown('declare_overt_cooldown') returns true. |
| Bot is in overt status. | Wait for the 5min timer to expire or trigger covert status. | System message about hidden affiliation, OVERT PVP flag removed, covert status confirmed. |
| Ensure bot has combat_smuggler_underworld_04 skill and sufficient credits (20k or 100k). | Perform a bribe action. | Standing increases by bribe amount (250 or 1,250) with system message confirming change, getFactionPointsCap() verifies standing does not exceed rank cap. |
| Ensure bot's current rank is less than max rank. | Select the promotion option and confirm. | System message with rank name on confirmation, getFactionRank() returns new rank, faction points decrease by getRankCost(rank + 1). |
| Create a bot character with Jedi skills. | Attempt to select covert/resign options. | Jedi characters see restriction messages and cannot select covert/resign options. |
| Initiate a resignation process to create a pending task. | Select the cancellation option. | Pending task canceled, changingFactionStatus data removed. |

## fishing

| Setup | Bot does | Expect |
|---|---|---|
| Equip a FishingPoleObject in the right hand slot (`hold_r`). Load a FishingBaitObject into the pole's container. Stand on land adjacent to water at a valid fish | Call `startFishing()`. | Receive system message `@fishing:start_fishing`. Player mood string is set to "fishing". Fishing session state is WAITING. SUI fishing window opens with correct status text. |
| Wait for FishingEvent ticks (every 7 seconds) during an active fishing session. | Monitor the state progression. | State transitions through WAITING → SNAGGED/NIBBLE → BITE → CATCH → REELING → REELGAME. Corresponding system messages and fly text appear at each transition. SUI window updates with current state, bai |
| Reach the REELGAME state with the player within 2.0 of the marker. | Succeed in the reel game. | A FishObject is created and transferred to player inventory. Fish attributes (name, zone, time, length) are set. Receive system message `fishing:prose_notify_catch` with item name. Marker container op |
| Trigger a mishap (e.g., line snap or lost bait). | Observe the outcome. | Receive appropriate `@fishing:` system message (e.g., `line_snap`, `lost_bait`). Fishing session ends; state returns to NOTFISHING. If bait lost, pole container is empty or bait use count decreased. |
| Attempt to fish without a pole. | Call `startFishing()`. | Receive system message `@fishing:must_have_pole`. |
| Attempt to fish with a pole but no bait. | Call `startFishing()`. | Receive system message `@fishing:bait_your_pole`. |
| Attempt to fish while swimming. | Call `startFishing()`. | Receive system message `@fishing:bad_cast`. |
| Attempt to cast from a bad location (too far or invalid). | Call `startFishing()`. | Receive system message `@fishing:too_far` or `@fishing:invalid_location`. |

## food-drink-spice

| Setup | Bot does | Expect |
|---|---|---|
| Ensure player is alive, not incapacitated, and has sufficient stomach capacity by checking `getFoodFilling()` / `getDrinkFilling()` vs max. | Consume a food item with known template values (filling, duration, effectType, modifiers). | System message confirming consumption or skill mod/healing amounts appears. |
| Player has consumed a food item. | Call `hasBuff(buffCRC)` and iterate buffs to verify the new buff exists. | Buff type is `BuffType::FOOD`, duration is correct (accounting for Twi'lek bonus if applicable), and modifiers are present. |
| Player has consumed a food item. | Check `ghost->getFoodFilling()` or `ghost->getDrinkFilling()`. | Value increased by the item's `filling` value. |
| Player has consumed a food item with attribute/skill effects. | Verify attribute modifiers (HAM pools) and skill mods. | Modifiers were applied via the buff. |
| Ensure `hasSpice()` returns false before consumption. | Consume a spice item. | System message confirming consumption appears. |
| Player has consumed a spice item and the spice buff has expired. | Check for `SpiceDownerBuff`. | A `SpiceDownerBuff` was added with 120-second duration (reduced by any `reduce_spice_downtime` modifier), negative attribute modifiers matching the spice's `attributeModifiers`, and a periodic vomitin |
| Player has consumed a healing item. | Verify HAM pools and messages. | HAM pools increased by expected amounts and the healing message was sent. |
| Player has consumed an item. | Check inventory for the consumed item. | Item's use count decreased (or item was destroyed if it reached zero). |

## foraging

| Setup | Bot does | Expect |
|---|---|---|
| Ensure player has 'foraging' skill, is on foot outside a structure in an unexhausted area, not mounted, not in combat, and has sufficient ACTION HAM. | Initiate forage action. | Correct start message appears. |
| Wait 8.5 seconds after initiating forage. | Observe system messages. | Either a success or failure message per the loot table outcomes appears. |
| Ensure forage action succeeded. | Check player inventory. | Items from expected loot group (e.g., 'forage_food' or 'forage_bait') appear with count matching expectations (up to 3 uses per area). |
| Perform forage 3 times in the same 10x10 area. | Attempt to forage again in that area. | 'nothing to forage' message appears. |
| Initiate forage action and wait until delay begins. | Move more than 2 meters during the 8.5-second delay. | Move-fail message appears. |
| Initiate forage action and wait until delay begins. | Enter combat during the delay. | Combat-distracts message appears. |
| Initiate forage action but do not let it complete. | Attempt to forage again before the pending task completes. | Busy message appears. |

## fs-village

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the zone `dathomir` is enabled. | Verify player has no `force_crystal.iff` in inventory and talk to the elder. | System message confirming item creation or `@error_message:inv_full`. |
| Player has interacted with the old man/elder. | Check the state of the old man NPC. | Old man is non-conversable (option bit cleared) and despawned. |
| Confirm village is in Phase 1 for Sarguillo patrols via `Village:CurrentPhase` quest status. | Complete 20 patrols. | `FsPatrolCompletedCount` equals 20, `FS_PATROL_QUEST_FINISH` completed, and `fs_village_bannerpole_s01.iff` exists in inventory. |
| After patrol completion. | Check the branch unlock state for ranged accuracy. | State set to 2 for `force_sensitive_combat_prowess_ranged_accuracy`. |
| Player uses the XP converter. | Check standard XP and `fs_<category>` XP values. | Standard XP decreased by converted amount, `fs_<category>` XP increased by `convertedXp`, and system messages about conversion appear. |
| Player uses the XP converter. | Observe the UI state. | SUI windows close properly. |
| Attempt to learn a `force_sensitive_` skill before unlock state reaches 2. | Check for success or failure. | Action fails silently or shows an error. |
| Unlock state for `force_sensitive_combat_prowess_ranged_accuracy` is set to 2. | Attempt to learn a `force_sensitive_` skill. | Skill learning succeeds. |

## gambling

| Setup | Bot does | Expect |
|---|---|---|
| Position the bot character within 20 units of a gambling terminal object. Ensure the bot is not incapacitated, in combat, swimming, riding, dead, or meditating. | Open the radial menu on the terminal while not playing. | Radial menu shows "Join Station" |
| Bot has joined the Slots station. | Observe the radial menu state after joining. | Radial menu changes to "Leave Station" |
| Bot selects Slots from the terminal. | Verify the SUI window appearance. | SUI window appears with title "@gambling/game_n:slot_standard" and five menu items |
| Slots SUI is open. | Press "Bet One" button. | 1 credit is added to the bet |
| Slots SUI is open with current bet less than max. | Press "Bet Max" button. | Bet fills to max bet (3 for slots) |
| Bot's bet reaches max for Slots. | Observe the terminal behavior after bet is placed. | Game auto-starts and the terminal sends "Slot Machine Pay Line" messages showing rolling digits |
| Slots game has ended (state is SLOTGAMEENDED). | Attempt to interact with the terminal again. | Player can rejoin |
| Bot selects Roulette from the terminal. | Verify the SUI window appearance. | SUI window appears with title "@gambling/game_n:roulette" and betting instructions |

## gcw-bases

| Setup | Bot does | Expect |
|---|---|---|
| Place or locate an OVERT player faction base and ensure it is in the VULNERABLE state. | Attempt to jam the uplink by guessing bands until the correct one is found. | State changes to BAND with message 'You narrow the carrier signal down to Band #X', then to JAMMED with messages 'You isolate the carrier signal to Channel #X' and 'Jamming complete! You disable the u |
| Ensure the base is jammed and interact with the HQ terminal as the attacker faction. | Check if declare_overt_cooldown is cleared or wait 5 minutes, then initiate shutdown. | System message 'Structure shutdown request received. Please stand by...' appears. |
| Wait ~60 s for the BaseShutdownTask to complete after initiating shutdown. | Check the base state and broadcast messages within 64 m. | State changes to SHUTDOWNSEQUENCE, DESTRUCTALARM is active, and broadcast 'COUNTDOWN INITIATED: estimated time to detonation: X minutes' appears (X starts at 10). |
| Have a defender interact with the HQ terminal during the countdown. | Observe the result of the defender's interaction. | Destroy task is cancelled, state changes to REBOOTSEQUENCE, and broadcast 'COUNTDOWN ABORTED: FACILITY SHUTTING DOWN!!' appears. |
| Let the 10-minute countdown complete without abort for a static base. | Verify the observer event and faction status. | FACTIONBASEFLIPPED observer event fires and the faction changes. |
| Let the 10-minute countdown complete without abort for a player base. | Check if the owner is online and verify the base's registration status. | Owner receives refund message (if online), base structure is destroyed, and it is unregistered from GCW manager. |
| Wait for vulnerabilityDuration (default 2 h) to expire. | Check the base state, terminal presence, and alarm status. | State returns to INVULNERABLE, terminals are despawned, alarms are deactivated, and next vulnerability cycle is scheduled correctly. |

## group-loot

| Setup | Bot does | Expect |
|---|---|---|
| Form a group with multiple bot players and ensure one bot is the group leader. | Change the loot rule to 'master' via `/grouploot`. | System message confirming the loot rule name is set to master looter. |
| Group with loot rule set to 'master'. | Kill a creature that drops items and credits. | Items appear in the corpse container accessible only by the group leader. |
| Group with loot rule set to 'master'. | Non-master member attempts to loot items from the corpse. | Restriction message appears for the non-master member. |
| Group with loot rule set to 'master'. | Master looter loots all items from the corpse. | Items are transferred to the master looter's inventory. |
| Group with loot rule set to 'lottery'. | Kill a creature that drops items and credits. | Eligible members have a lottery window open. |
| Group with loot rule set to 'lottery' and lottery running. | Non-winner attempts to access the corpse. | Non-winner cannot access the corpse. |
| Group with loot rule set to 'random'. | Kill a creature that drops items and credits. | Items are distributed to random eligible members; winner receives items, others do not. |
| Move one group member beyond 128 units from the corpse. | Attempt to join lottery or receive credits for a dropped item. | Member cannot join lottery or receive credits; 'too far away' message appears. |

## groups

| Setup | Bot does | Expect |
|---|---|---|
| Ensure bot character has no existing group (`getGroup() == nullptr`) and have a second test character available. | Send invite command to the target character. | Inviter receives system message `@group:invite_leader` with target name; Target receives system message `@group:invite_target` with inviter name; Target's `getGroupInviterID()` equals inviter's object |
| Target character has received an invite. | Send accept command from the target. | Leader sees `@group:formed_self`; New member sees `@group:joined_self`; A GroupObject with ID `0x13dcb432` is created; Both characters' `getGroup()` returns it; Both receive a `GroupObjectDeltaMessage |
| Bot character attempts to invite itself. | Send invite command to self. | Inviter sees `@group:invite_no_target_self`. |
| Bot character is not the group leader. | Attempt to invite another player. | Non-leader sees `@group:must_be_leader`. |
| Target character is already in a group. | Send invite command to the target. | Inviter sees `@group:already_grouped`. |
| Group is full (≥20 members). | Attempt to invite a new player. | Joining player sees "The group is full.". |
| Bot and another player are in a group and damage the same creature. | Kill the creature. | Both characters receive XP; Server checked `isInRangeZoneless(attacker, 80)` before distributing. |
| Pet owner has `outdoors_creaturehandler_novice` within 80 feet of a killed creature. | Kill the creature. | Pet owner receives creaturehandler XP. |

## guilds

| Setup | Bot does | Expect |
|---|---|---|
| Create two bot characters (Bot A and Bot B). Place a GuildTerminal object in the zone. Ensure both bots are online, not in any guild, and Bot B is within 32 met | Have Bot A interact with the GuildTerminal to create a new guild by completing name/abbrev input. | Bot A's `isInGuild()` returns true, `getGuildObject()` is non-null, a system message confirming creation appears, and Bot A is in the guild chat room. |
| Ensure Bot B is not in a guild and within 32 meters of Bot A (who is now in a guild). | Have Bot A sponsor Bot B for guild membership. | Bot B receives a SUI dialog (`GUILD_SPONSOR_VERIFY`) with accept/decline buttons. |
| Ensure Bot B has received the `GUILD_SPONSOR_VERIFY` SUI dialog. | Have Bot B accept the sponsorship via the SUI dialog. | Bot B's `isInGuild()` returns true, guild object is set, system messages appear on both bots, and a guild mail is delivered to Bot B. |
| Ensure Bot A is the leader of the guild containing Bot B. | Have Bot A kick Bot B from the guild. | Bot B's `isInGuild()` returns false, guild object is null, both bots receive system messages, a guild mail is sent to Bot B, and Bot B is removed from chat rooms. |
| Ensure Bot A is in the guild. | Have Bot A leave the guild. | Bot A's `isInGuild()` returns false, guild object is null, a system message appears, a guild mail is sent to Bot A, and Bot A is removed from chat rooms. |
| Ensure election is not enabled and Bot A is the leader of the guild. | Have Bot A leave the guild as the leader. | An election is triggered (observable via terminal options). |
| Ensure Bot A is the leader of a guild with at least one other member. | Have Bot A disband the guild. | The guild no longer exists in the server's guild list, all members receive a disband mail, and native `destroyGuild` logic executes (870). |

## ham

| Setup | Bot does | Expect |
|---|---|---|
| Measure the regeneration tick interval. | Damage the bot's health and stand still out of combat. | Read current/max on consecutive regen ticks; per-tick gain = ceil(con x 13/2100 x latency/1000 x posture factor), at least 1. |
| Stand, then kneel, then sit out of combat. | Read current/max on consecutive regen ticks in each posture. | The sitting/standing ratio should be about 1.75 (not exact, because of ceil). |
| Bring a primary pool to N <= 0. | Observe the bot's state during incapacitation recovery. | Posture is incapacitated; timer is max(5, min(60, \|N\|/5)); the pool is at 1 if it was below 0 at recovery. |
| Incapacitate the bot twice within 600 seconds. | Trigger a third incapacitation. | The bot dies. |
| Record base, max, wounds and shock values. | Apply a wound by taking hits from a weapon with a known wound ratio. | Max unchanged; current at most max minus wounds; the secondaries' current equal to max minus wounds; shock +1 per wounded pool. |
| Have active wounds on the bot. | Heal the wounds. | The cap comes back, but no automatic refill of the primary. |
| Read the armor's `cat_armor_encumbrance` values. | Equip the armor. | The max of the two matching secondaries drops by exactly that value; current follows; regen slows. |
| Have the encumbering armor equipped. | Unequip the armor. | The values are restored. |

## harvester-operation

| Setup | Bot does | Expect |
|---|---|---|
| Place a harvester deed and construct it on a zone with an active resource node (spawn "inShift") nearby. Ensure the bot character is the owner (on admin list).  | Right-click the harvester to open the radial menu. | The radial menu shows item ID 78 with label "@harvester:manage". |
| Harvester is constructed and owned by the bot. | Select item 78 from the radial menu to open the SUI window, select a resource, and confirm activation. | The client receives ResourceHarvesterActivatePageMessage. |
| Activation confirmed in the SUI window. | Observe the harvester's state changes immediately after confirmation. | The bot receives InstallationObjectDeltaMessage3 and InstallationObjectDeltaMessage7 packets showing operating=true. |
| Harvester is activated with sufficient power/maintenance. | Observe the hopper contents shortly after activation. | The bot receives HarvesterObjectMessage7 and InstallationObjectDeltaMessage7 packets showing the selected resource container in the hopper. |
| Harvester is operating with a resource node nearby. | Monitor the hopper quantity for the active resource over time. | The hopper quantity increases at a rate matching extractionRate × spawnDensity per minute. |
| Harvester has sufficient power and maintenance. | Attempt to activate the harvester without depositing enough credits for power. | System message with string ID "player_structure:power_deposit_incomplete" appears. |
| Harvester has sufficient power but insufficient maintenance credits. | Attempt to activate the harvester. | System message with string ID "shared:harvester_no_maint_4" appears. |
| Harvester is operating and the hopper fills up to capacity. | Wait for the hopper to reach hopperSizeMax. | The harvester shuts down and broadcasts "harvester_resource_depleted" if the resource is depleted, or stops due to capacity. |

## hoth-content

| Setup | Bot does | Expect |
|---|---|---|
| Ensure zone "hoth" is enabled. | Verify the bot is on planet "hoth". | planetName = "hoth" |
| Teleport to each cave center. | Check for wampa spawns within cell-local coordinates. | wampa spawns exist |
| Locate boss variants in ice caves. | Check respawn timer for boss vs regular wampas. | 1800 s respawn timer for bosses, 420 s for regular wampas |
| Locate a boss variant in ice caves. | Count accompanying elder_wampa guards. | two elder_wampa guards accompany each boss |
| Check cave building object location. | Verify spawn coordinates for mynock den. | spawns at -2000, 44.8, -4800 |
| Scan cells 1–11 in the mynock den. | Count mynock-type mobs. | 23 mynock-type mobs exist |
| Locate hoth_mynock_broodmother in cell 11. | Check respawn timer. | 1800 s respawn |
| Locate hoth_glacial_rancor. | Verify spawn coordinates and respawn timer. | at 600, 26.4, -4600 with 1800 s respawn |

## image-design

| Setup | Bot does | Expect |
|---|---|---|
| Ensure designer creature has `social_entertainer_novice` skill. | Attempt image design without the skill. | System message for skill check failure. |
| Target creature is dead or invisible. | Attempt image design on the target. | System message for dead/invisible target. |
| Designer and target are in different groups. | Attempt image design. | System message for group mismatch. |
| Target has insufficient credits. | Attempt image design. | System message for insufficient credits. |
| Designer and target are in a `SALONBUILDING`. | Start an image design session. | Both creatures have `SessionFacadeType::IMAGEDESIGN` active. |
| Image design session is active. | Complete or cancel the session. | `SessionFacadeType::IMAGEDESIGN` is dropped for both creatures. |
| Perform hair changes during image design. | Complete the session. | Old hair slot is removed and new hair object is transferred to target; body/color customization variables update on target. |
| Complete an image design session with modifications. | Check credits and XP. | Target's cash/bank decreases by payment amount; designer's cash increases by same amount; designer receives XP via `PlayerManager::awardExperience` with skill "imagedesigner". |

## jedi-unlock

| Setup | Bot does | Expect |
|---|---|---|
| Set jediProgressionType to HOLOGRINDJEDIPROGRESSION in Lua global before loadConfiguration. | Award badges for 6 different professions from getGrindableProfessionList() via registerObservers(pCreatureObject). | BADGEAWARDED observer triggers for each of the 6 professions. |
| Player has mastered 6 professions from the grindable list. | Attempt to unlock Jedi status. | System message from SUI window: "Perhaps you should meditate somewhere alone...". |
| Player has completed the Jedi unlock process. | Check player's skill list. | Presence of force_title_jedi_novice skill in player's skill list. |
| Player has completed the Jedi unlock process. | Call PlayerObject(pGhost):isJedi() in hologrind_jedi_manager.lua line 118. | Returns true. |

## jedi-unlock-village

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player character has earned all five required badge types in the specified quantities. | Verify the player does not already have `force_title_jedi_novice` skill before triggering the progression. | The player lacks the `force_title_jedi_novice` skill. |
| Meet all badge requirements to trigger the initial state change. | Check the player's states after badge requirements are met. | The `VILLAGE_JEDI_PROGRESSION_GLOWING` state has value 1. |
| Wait for the timed delay of 12–36 hours for the old man encounter. | Trigger and complete the old man encounter. | The `VILLAGE_JEDI_PROGRESSION_HAS_CRYSTAL` state has value 2. |
| Complete the old man encounter. | Check if the quest `OLD_MAN_INITIAL` is activated. | The quest `OLD_MAN_INITIAL` is activated. |
| Complete the old man encounter and receive the crystal. | Check if the quest `OLD_MAN_FORCE_CRYSTAL` is completed. | The quest `OLD_MAN_FORCE_CRYSTAL` is completed. |
| Complete the old man encounter. | Check the player's inventory for the Force crystal. | The player has the item `object/tangible/loot/quest/force_sensitive/force_crystal.iff`. |
| Complete the old man encounter. | Capture system messages after the encounter. | The message `@quest/force_sensitive/intro:crystal_message` is displayed. |
| Wait for the timed delay of 1–12 hours for the Sith shadow. | Trigger the event that leads to Dathomir arrival and receive the waypoint datapad. | The player has the item `object/tangible/loot/quest/force_sensitive/waypoint_datapad.iff`. |

## lairs-spawning

| Setup | Bot does | Expect |
|---|---|---|
| Target a creature-type lair with known difficulty level and spawn limit, ensuring `hasBossMobs()` is true and it is not a destroy mission lair. | Approach the lair to trigger initial passive mobiles. | Initial passive mobiles are present and `spawnNumber` is effectively 1. |
| Have the lair active with initial wave triggered. | Deal enough damage to exceed 0 condition damage. | Within ~1–10 seconds, new creatures appear (check system messages or creature count increase). |
| Continue damaging the lair from Wave 1 state. | Deal damage until `conditionDamage > maxCondition / 2`. | Another wave spawns within 1–10 seconds. |
| Continue damaging after both waves have spawned (`spawnNumber >= 3`). | Deal damage until `(difficultyLevel * (maxCondition / 5)) <= conditionDamage`. | A boss mobile appears after ~500 ms, and only one boss spawns per normal cycle. |
| Engage in combat with the lair. | Observe creature behavior during combat. | Any healer creature stops attacking and moves toward the lair to heal it (blackboard `"healTarget"` set to lair). |
| Damage the lair until condition reaches zero. | Observe the destruction event. | A heavy damage client effect plays, XP is distributed to attackers, and the lair object no longer exists. |
| Destroy a lair and wait for it to be removed from the zone. | Approach an intact creature lair with living creatures and condition damage above half max, ensuring no players are in range for 10 seconds. | The lair repopulates: heals to full, resets `spawnNumber` to 0, and allows new spawns. |
| Kill a single creature from an active lair. | Wait for the individual respawn timer. | The creature respawns after 2–4 minutes (random between 120–240 seconds). |

## leash

| Setup | Bot does | Expect |
|---|---|---|
| Create two player characters on the same planet, group them together, and ensure neither is in combat, dead, incapacitated, or mounted. | Issue `/leash <leader name>` from the follower character. | Receive system message: "Leashed to X: keep using /follow; if it gets stuck you'll be moved closer. /leash off to stop." (lines 437-438). |
| Ensure the follower is `/follow`ing the leader and has a pending task named "leash". | Move the follower more than 10 m away from the leader. Wait at least 6 seconds without closing the gap by 0.5 m. | The follower is teleported closer to the leader and receives system message: "Leash: you were stuck, so you've been moved closer to X." (line 364). |
| Ensure the follower is currently leashed to a leader. | Issue `/leash off` from the follower character. | Receive system message: "Leash off." (line 419). |
| Ensure the follower is already leashed to a specific leader. | Issue `/leash <current leader>` again from the follower character. | Receive system message: "Already leashed to X. /leash off to stop." (line 413). |
| Identify a non-group member, an offline player, and a player on another planet. | Attempt to leash each of these invalid targets from the follower character. | Receive appropriate "Can't leash: ..." message (line 431) for each attempt. |
| Mount one of the player characters or enter combat state. | Attempt to trigger an unstick event while in this busy state. | No teleport occurs. |

## mail-friends-tells

| Setup | Bot does | Expect |
|---|---|---|
| Log in Bot A and Bot B. Ensure both have valid player objects. | Bot A sends a tell to online Bot B. | System message IM_SUCCESS received by sender. |
| Log out Bot B (offline). | Bot A sends a tell to Bot B. | System message IM_OFFLINE received by sender. |
| Bot B adds Bot A to ignore list. Log in both bots. | Bot A sends a tell to Bot B. | System message IM_IGNORED received by sender. |
| Ensure no player named 'InvalidName' exists. | Bot A sends a tell to 'InvalidName'. | System message: "There is no person by the name '%TU' in this Galaxy." |
| Log out Bot B. | Bot A sends mail with body size > PM_MAXSIZE to Bot B. | System message IM_TOOLONG received by sender. |
| Log out Bot B. | Bot A sends valid mail to Bot B. Log in Bot B and call loadMail(). | Mail appears in Bot B's inbox. |
| Log in both Bot A and Bot B. | Bot A sends mail to Bot B. | Mail is delivered immediately to Bot B. |
| Bot B has unread mail with status NEW. | Bot B reads the mail. | Mail status transitions to UNREAD/READ. |

## medic-xp-healing

| Setup | Bot does | Expect |
|---|---|---|
| Bot has Medic discipline trained, relevant skill mods set, and appropriate pharmaceutical items in inventory. | Use HealDamage on a willing ally player creature with HEALTH/ACTION damage. | Bot sees "You heal <name> for X health and Y action damage."; target sees "<name> heals you …"; target's HAM bars increase. |
| Bot has private_medical_rating > 0 or is near a surgical droid/hospital/campsite. Target has wounds in a specific pool. | Use HealWound on the ally. | Bot sees "You heal <name> for X <pool> wound damage."; target's wound count decreases by woundHealed; bot's MIND HAM decreases by mindCost. |
| Target has one of the four states to be healed. | Use HealState on the ally. | Bot sees "You remove the <state> state from <name>."; target's state bitmask no longer contains the healed state; target's state buff removed. |
| Perform a successful HealDamage on an ally. | Check bot's medical skill progress after the heal. | Medical XP gain equals (healthHealed + actionHealed) × 0.25. |
| Perform a successful HealWound on an ally. | Check bot's medical skill progress after the heal. | Medical XP gain equals woundHealed × 2.5. |
| Perform a successful HealState on an ally. | Check bot's medical skill progress after the heal. | Medical XP gain equals 50. |
| Successfully perform a heal (e.g., HealDamage). | Attempt to heal again immediately. | Action fails with "You must wait before you can do that." until cooldown expires. |
| Bot targets itself for healing. | Perform a self-heal (HealDamage, HealWound, or HealState). | No medical XP awarded. |

## mercenaries

| Setup | Bot does | Expect |
|---|---|---|
| Position the bot character near the broker at coordinates tatooine x=3552.0, y=-4782.0. | Initiate conversation with the NPC named "Dax Venn (a mercenary broker)" and select "Hire a mercenary." | The initial greeting appears, followed by the confirmation message. |
| After selecting "Hire a mercenary," | Check for a new creature object of type "sandbox_mercenary". | It spawns near the player within ~3 meters (random offset -3 to +3 on x and y) at the player's current floor height. |
| After the mercenary spawns, | Inspect the spawned mercenary's state. | It has AI flags `AI_ESCORT` and `AI_FOLLOW`, and its follow target is set to the player. |
| Repeat hiring process two more times. | Verify the total count of mercenaries. | There are exactly 3 mercenaries. |
| With 3 mercenaries active, | Attempt to hire a fourth mercenary. | The "already got three" message appears instead of spawning a new one. |
| Enter combat with an enemy. | Observe the behavior of all alive mercenaries. | All mercenaries call `engageCombat()` on the same target. |
| Select "Dismiss my mercenaries." | Check for mercenary objects and player data. | All mercenary objects are destroyed and no mercenary IDs remain in player data. |
| After dismissal, | Initiate conversation with the broker again and select "Hire a mercenary." | A new mercenary spawns successfully. |

## missions

| Setup | Bot does | Expect |
|---|---|---|
| Bot has `combat_marksman_master` skill and is within 2 km of a general terminal. | Interact with the general terminal to generate missions. | First 6 slots are destroy missions. |
| Bot has interacted with the general terminal. | Check the next 6 mission slots. | Next 6 slots are deliver missions. |
| Bot is near city center and interacts with the general terminal. | Inspect a generated deliver mission. | Deliver mission has `inTown` flag set. |
| Bot's datapad has 6 destroy missions from Ilsa. | Attempt to accept a 7th destroy mission. | Mission is refused. |
| Bot has no active bounty mission. | Accept a bounty mission, then attempt to accept another. | Second bounty mission is refused; only one allowed at a time. |
| Bot accepts a destroy mission. | Check the mission properties. | Difficulty matches lair spawn range and player level. |
| Bot accepts a destroy mission. | Check the mission distance property. | Distance is within calculated range. |
| Bot accepts a destroy mission. | Check the mission reward property. | Reward follows formula. |

## npc-conversations

| Setup | Bot does | Expect |
|---|---|---|
| Ensure NPC has a valid conversation template registered in CreatureTemplateManager with the correct CRC and player is within conversation range. | Initiate conversation with the NPC. | Player receives an NpcConversationMessage packet with dialog text followed by a StringList packet containing option texts. |
| Conversation initiated. | Check player session state. | Player has an active session with SessionFacadeType::CONVERSATION and lastConversationScreen is updated. |
| Conversation screen specifies animations. | Trigger the conversation screen. | Both NPC and player play the specified animations, verifiable via creature state queries. |
| Conversation initiated with stopConversation=true condition met. | End the conversation. | Player receives a StopNpcConversation packet. |

## pets-droids

| Setup | Bot does | Expect |
|---|---|---|
| Player has `outdoors_creaturehandler_novice` skill mod and a valid PetControlDevice in inventory. Player is outdoors, not in combat, dead, taming, or in private | Use radial menu on PetControlDevice to select call (ID 44). | System message: "Calling pet in 15 seconds. Combat will terminate pet call." followed by a 15 second delay before spawn. |
| Pet has spawned at player position ±2-3 m. | Check the ghost's active pets list. | `ghost->hasActivePet(pet)` returns true. |
| Player is in a city or camp. | Use radial menu on PetControlDevice to select call (ID 44). | Pet spawns immediately without delay. |
| Pet is resting. | Use radial menu on pet to select follow (or chat "pet follow"). | Pet sets movement state to FOLLOWING. No system message is displayed. |
| Player moves away from the pet. | Observe the pet's behavior at various distance intervals. | Pet follows the player. Note: no server-side distance enforcement is visible. |
| Pet is moving. | Use radial menu on pet to select stay (or chat "pet stay"). | Pet stops moving. No system message is displayed. |
| No target is specified for the pet. | Use radial menu on pet to select guard (or chat "pet guard"). | Pet guards the player. No system message is displayed. |
| Pet is active. | Use radial menu on PetControlDevice to select store (ID 59) or chat "pet store". | Pet disappears from the world and reappears in the PetControlDevice. For faction pets, system message "Storing pet in 60 seconds" appears before storage. |

## player-cities

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the test planet has an entry in `CitiesAllowed` Lua config. | Have the bot character use a City Hall deed at a valid location (not within 1024 meters of another city). | A 'New City Established!' mail to the mayor. |
| After using the deed. | Check for the creation of a new CityRegion object. | The CityRegion object is created and persisted. |
| After city creation. | Check the city rank. | The city is at OUTPOST rank. |
| Have citizens register with the city. | Check for mail sent to the mayor. | Mayor receives 'City Growth: Added Citizen' mail. |
| After citizen registration. | Check for mail sent to the new citizen. | New citizen receives 'Welcome, Citizen!' mail. |
| After citizens register. | Call `city->getCitizenCount()`. | `city->getCitizenCount()` increases. |
| Wait for grace period to expire with enough citizens. | Check for mail sent to the mayor. | Mayor receives 'New City Approved!' mail. |
| After city approval. | Check `city->hasAssessmentPending()`. | `city->hasAssessmentPending()` becomes false. |

## player-vendors

| Setup | Bot does | Expect |
|---|---|---|
| Create a vendor with ownerId set to a valid player object ID and place it in a zone. | Attempt registration on an empty vendor. | System message @player_structure:register_vendor_not appears. |
| Create a non-empty vendor owned by a player with sufficient credits (bankCredits + cashCredits >= value). | Register the vendor. | vendorData->registered becomes true and vendor appears on planetary map. |
| Open the registration SUI for a valid vendor. | Check the SUI list box contents. | SUI list box contains 13 category items with correct string IDs. |
| Owner has sufficient credits and vendor is registered. | Pay maintenance with a valid value. | Owner's bank/cash credits decrease, vendorData->maintAmount increases, and system message @player_structure:vendor_maint_accepted appears. |
| Owner has sufficient credits and vendor is registered. | Attempt to pay maintenance with a value > 100,000. | System message @player_structure:vendor_maint_invalid appears. |
| Owner has sufficient credits and vendor is registered. | Attempt to pay maintenance with a value <= 0. | System message @player_structure:amt_greater_than_zero appears. |
| Owner has insufficient credits (bankCredits + cashCredits < value) and vendor is registered. | Attempt to pay maintenance. | System message @player_structure:vendor_maint_denied appears. |
| Vendor has maintAmount > 0 and owner has bank space. | Withdraw a valid amount from maintenance. | vendorData->maintAmount decreases, owner's bank credits increase, and system message @player_structure:vendor_withdraw appears. |

## pvp-tef-duels

| Setup | Bot does | Expect |
|---|---|---|
| Ensure both bots are CreatureObjects and players. Position them within 25 meters of each other. Verify neither is in a no-duel area via `getActiveAreas()`/`isNo | Bot A challenges Bot B. | Bot A receives system message `duel/challenge_self` with Bot B's object ID. Bot B receives system message `duel/challenge_target` with Bot A's object ID. `areInDuel(A, B)` returns false. |
| Ensure the challenge from the previous step is pending. | Bot B accepts the challenge. | Both bots receive `duel/accept_self` and `duel/accept_target` messages respectively. Both bots' PVP status bitmasks include `ObjectFlag::ATTACKABLE \| ObjectFlag::AGGRESSIVE`. `areInDuel(A, B)` returns |
| Ensure a valid duel exists between Bot A and Bot B. | Either bot ends the duel. | Both bots receive `duel/end_self` and `duel/end_target` messages. PVP status bitmasks no longer include ATTACKABLE/AGGRESSIVE for each other. Duel lists are empty (`getDuelListSize() == 0`). `areInDue |
| Ensure a valid duel exists between Bot A and Bot B. | Bot A performs a combat action against Bot B. | The attacker's parent CreatureObject has `ObjectFlag::TEF` set in its PVP status bitmask. `hasTef()` or the specific TEF type function returns true on the attacker's PlayerObject. |
| Ensure the TEF flag is currently set from the previous step. | Wait for the TEF timer to expire. | The TEF flag is cleared (or `schedulePvpTefRemovalTask` has run). |

## quests

| Setup | Bot does | Expect |
|---|---|---|
| Ensure Tatooine is enabled and the character has no 'tutorial_one' state. | Stand near Han Solo at Tatooine x 3565, y -4795 and converse with him. | The first screen 'first_screen' appears with options 'Why' and 'What if I don't want to?' |
| Converse with Han Solo. | Select the options in order: 'Why', 'It's what i need to do, count me in!', 'What's the deal', 'Go on', 'I'm on my way'. | The screen 'accept_task_one' appears, the conversation closes, bit 1 of tutorial_one is set, sound ui_npe2_quest_received.snd plays, and system message 'Quest received: Checking the Falcon.' arrives. |
| Walk within 40 m of the Falcon static at coordinates x 3863, y -4856. | Enter the active area. | System message '<Communicator> Ok Kid, looks like she's all in one piece...' appears, sound ui_quest_waypoint_patrol.snd plays, bit 1 is cleared and bit 2 is set. |
| Return to Han Solo and converse with him. | Complete the conversation sequence for quest completion. | Cash increases by exactly 10000, sound ui_npe2_quest_credits.snd plays, system message 'Quest completed: Checking the Falcon.' appears, state becomes 4, and screen is task_one_complete. |
| Converse with Han Solo again after completing the quest. | Initiate conversation. | The screen is quest_complete with the text 'Did you ever meet Lando in Theed?' |

## resource-quality

| Setup | Bot does | Expect |
|---|---|---|
| Fix crafter's weapon_assembly, weapon_experimentation and luck. Remove food buffs and city bonuses. Use a tool with known effectiveness. | Use `/resource perfect <type>` to create a spawn with all stats at 1000. | A resource spawn is created with every applicable stat at 1000. |
| Have a crafter with fixed stats and no buffs, using a known tool. | Perform experiments on a group of resources using the perfect resource spawn in every slot. | No stat line goes past min + (max − min) × weightedSum / 1000. |
| Have a crafter with fixed stats and no buffs, using a known tool. | Perform experiments on a group of resources using the perfect resource spawn in every slot. | The ceiling of the result equals the template max. |
| Have a crafter with fixed stats and no buffs, using a known tool. | Perform an experiment and observe the starting value relative to assemblyPct. | The starting value lies between assemblyPct × 0.4 and assemblyPct × 1.05 of the range. |
| Have a crafter with fixed stats and no buffs, using a known tool. | Attempt to add a second, different resource to a filled slot. | The action fails; the resource cannot be added. |
| Have a crafter with fixed stats and no buffs, using a known tool. | Perform an experiment and observe the result message and value change. | The change in value equals step × points × range. |

## resources

| Setup | Bot does | Expect |
|---|---|---|
| Place tre archive in zone; ensure zone is in activeZones. | Check server log and resource pool status. | Server log shows 'Resource Map Built with N resources' (ResourceSpawner.cpp:309-311) and pool lines with Spawned > 0. |
| Use a survey tool on the planet. | Check the resource list displayed by the tool. | List shows only in-shift spawns of that tool's type (:858-895). |
| Be on Hoth or Ossus with minimum-pool entries configured. | Check for spawn objects corresponding to each minimum-pool entry. | One `*_hoth` / `*_ossus` spawn per minimum-pool entry. |
| Set `averageShiftTime` low or call the despawn path (ResourceManagerImplementation.cpp:461-474). | Check the zone list for the old resource name and the pool slot. | Old name is gone from the zone list; same pool slot has a new name. |
| Locate the resource that was shifted/despawned. | Attempt to resolve the old name globally. | The old name still resolves globally. |
| Place harvester at a point with survey density ≥ 0.10; select spawn; add power and maintenance; activate. | Wait T seconds, then read the hopper quantity via operator's delta updates (updateHopperSize / updateExtractionRate, :143-147, 192-196). | Hopper quantity is about `T/60 * density * extractionRate`. |
| Monitor the harvester operator during operation. | Check power and maintenance levels after some hours of operation. | Power and maintenance drop by rate × hours. |
| Sample the same spawn twice. | Check for containers resulting from the samples. | One container whose quantity equals the sum of the samples. |

## sandbox-creatures

| Setup | Bot does | Expect |
|---|---|---|
| Place player character on Corellia with sufficient skill/permissions to use the sandbox spawn menu. | Use the sandbox test datapad interface to spawn a 'corellian butterfly'. | A system message confirming creature spawn success. |
| Player character on Corellia with access to sandbox spawn menu. | Spawn a 'corellian butterfly' via the datapad menu. | The spawned creature has level 7. |
| Player character on Corellia with access to sandbox spawn menu. | Spawn a 'corellian butterfly' via the datapad menu. | Inventory or state changes indicating the creature was successfully spawned. |

## scout-xp-sources

| Setup | Bot does | Expect |
|---|---|---|
| Kill a creature and wait for it to become dead (posture DEAD). Verify corpse has resources by checking `getMeatType()`, `getHideType()`, or `getBoneType()` are  | Call HarvestCorpseCommand with argument "meat". | System message showing quantity extracted and resource type (e.g., "@skl_use:creature_quality_fat" with DI=quantity, TU=resource class). |
| Kill a creature and wait for it to become dead (posture DEAD). Verify corpse has resources. Position within 7 meters of corpse. | Call HarvestCorpseCommand with argument "hide". | System message showing quantity extracted and resource type. |
| Kill a creature and wait for it to become dead (posture DEAD). Verify corpse has resources. Position within 7 meters of corpse. | Call HarvestCorpseCommand with argument "bone". | System message showing quantity extracted and resource type. |
| Kill a creature and wait for it to become dead (posture DEAD). Verify corpse has resources. Position within 7 meters of corpse. | Call HarvestCorpseCommand with empty argument. | System message showing quantity extracted and resource type. |
| Kill a creature and wait for it to become dead (posture DEAD). Verify corpse has resources. Position within 7 meters of corpse. Call HarvestCorpseCommand once. | Call HarvestCorpseCommand again on the same corpse. | Failure with message "This creature has no resources" or similar, as `addAlreadyHarvested(player)` was called. |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill mod >= 1. Obtain a trap item (TangibleObject with isTrapObject() == true) in inventory. | Target a living, attackable, non-pet monster AI agent within trap's max range and call ThrowTrapCommand with the trap's object ID as argument. | Trap successfully thrown (no error messages). |
| Ensure scout has `outdoors_scout_novice` skill but trapping skill < 1. Obtain a trap item in inventory. | Target a living monster and call ThrowTrapCommand with the trap's object ID as argument. | System message "@trap/trap:trap_no_skill". |
| Ensure scout has `outdoors_scout_novice` skill and trapping skill >= 1 but < trap's required skill. Obtain a trap item in inventory. | Target a living monster and call ThrowTrapCommand with the trap's object ID as argument. | System message "@trap/trap:trap_no_skill_this". |

## secure-trade

| Setup | Bot does | Expect |
|---|---|---|
| Ensure both bot characters are within trade range and have no existing active trade session. | Send `BeginTradeMessage` with the target player's ID. | The target receives a trade window prompt (system message or SUI window). |
| Target accepts the trade. | Observe both players' trade windows. | Both players see an open trade window showing empty item slots and credit fields. |
| Have a test item in inventory with a valid object ID. | Add the item via `AddItemMessageCallback` with the valid object ID. | The item appears in that player's side of the trade window on both clients. |
| Have credits in inventory. | Send `GiveMoneyMessageCallback` with a credit amount. | The credit field updates on both sides and the sender's credit balance decreases. |
| Both players have added items/credits and clicked 'Accept'. | Observe the trade window buttons. | The 'Verify' button becomes active for both players. |
| Both players click 'Verify'. | Wait for trade completion. | Items and credits are transferred to final destinations. |
| Either player clicks 'Abort' during an active trade. | Observe the trade window and inventories. | The trade window closes, all items return to original inventories, credits restore, and a system message indicates the trade was aborted. |
| Trade is in progress or completed. | Check `TradeSession` fields. | `tradeTargetPlayer` matches the other player's ID, `itemsToTrade` contains added objects, `moneyToTrade` matches sent amount, `acceptedTrade` and `verifiedTrade` flags are true when expected. |

## skills-training

| Setup | Bot does | Expect |
|---|---|---|
| Ensure test creature is a player with valid PlayerObject ghost, has prerequisite skills/species, sufficient XP (`ghost->getExperience(skill->getXpType())`), and | Bot attempts to learn the target skill. | `creature->hasSkill(skillName)` returns true. |
| Verify initial state before learning. | Bot learns the skill. | `ghost->getExperience(skill->getXpType())` decreased by `skill->getXpCost()`. |
| Verify initial state before learning. | Bot learns the skill. | `ghost->getSkillPoints()` decreased by `skill->getSkillPointsRequired()`. |
| Verify initial state before learning. | Bot learns the skill. | `creature->getSkillMod(SkillModManager::SKILLBOX, modifierKey)` shows expected value for each key in `skill->getSkillModifiers()`. |
| Verify initial state before learning. | Bot learns the skill. | `ghost->hasAbility(abilityName)` returns true for each ability in `skill->getAbilities()`. |
| Verify initial state before learning. | Bot learns the skill. | `creature->getLevel()` is updated via `playerManager->calculatePlayerLevel`. |
| Creature has the skill to surrender. | Bot surrenders the skill. | `creature->hasSkill(skillName)` returns false. |
| Creature has the skill to surrender. | Bot surrenders the skill. | `ghost->getSkillPoints()` increased by `skill->getSkillPointsRequired()`. |

## slicing

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher. | Place a Precision Laser Knife (`SceneObjectType::LASERKNIFE`) in the player's inventory and place the target object in the player's inventory. | The SUI menu appears with correct options for the phase. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target object in inventory. | Perform a successful slice with the correct cable sequence. | A success system message appears, the container is unlocked, and XP is awarded for the "slicing" experience type. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target object in inventory. | Perform a failed slice with the wrong first cable selection. | A failure system message appears and the Laser knife charge is consumed. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target object in inventory. | Perform a failed slice with the wrong second cable selection. | A failure system message appears and the Laser knife charge is consumed. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, but no Precision Laser Knife in inventory. | Attempt to slice a target object. | The "no_knife" message appears. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target weapon/armor in inventory, but no upgrade  | Attempt to slice the weapon/armor. | An appropriate message indicating the missing upgrade kit appears. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target object in inventory. | Use Molecular Clamp to reveal the correct cable, then perform the slice with the correct sequence. | A success system message appears and XP is awarded for the "slicing" experience type. |
| Ensure the smuggler bot has the skill `combat_smuggler_slicing_01` or higher, a Precision Laser Knife, and the target object in inventory. | Use Flow Analyzer to reveal the correct cable, then perform the slice with the correct sequence. | A success system message appears and XP is awarded for the "slicing" experience type. |

## structure-placement

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the bot character is not riding a mount and is outside any building. | Verify the bot has the required deed in inventory. | The deed is present in the bot's inventory. |
| Ensure the bot has sufficient lots for the structure. | Record the bot's current lot count before placement. | A specific number representing available lots is recorded. |
| If testing a faction deed, ensure the bot's faction matches the deed's faction. | Verify faction alignment. | The bot's faction ID matches the deed's required faction. |
| If testing city requirements, ensure the bot is in the correct city with sufficient rank and zoning rights. | Verify location and permissions. | The bot is in the correct city with valid zoning rights. |
| Execute the structure placement command at target coordinates. | Observe system messages sent during the test. | Capture all system messages and compare against expected message string IDs. |
| After successful placement, check inventory. | Verify if the deed is still in the bot's inventory. | The deed is no longer in the bot's inventory. |
| Check the target coordinates after placement. | Verify a structure object exists at the target coordinates. | A structure object exists with the correct template, rotation, and owner. |
| Retrieve the structure object's owner ID. | Check that `structureObject->getOwnerObjectID()` matches the bot's object ID. | `structureObject->getOwnerObjectID()` equals the bot's object ID. |
| Check the bot's lot count after placement. | Verify the bot's remaining lots decreased by the structure's lot size. | The remaining lots are reduced by the specific lot size of the placed structure. |
| Attempt placement in a no-build zone. | Observe the system message received. | The message `@player_structure:not_permitted` is received. |

## structure-upkeep

| Setup | Bot does | Expect |
|---|---|---|
| Create a structure with known getBaseMaintenanceRate() > 0 and set config key Core3.Sandbox.StructureMaintenanceMultiplier to a known value. | Call getMaintenanceRate() on the structure. | The returned value matches the expected calculation based on template base rate, config multiplier, and skill mod. |
| Wait for the structure's maintenance pool to deplete. | Check the structure's condition after depletion. | Structure condition decreases proportionally (line 587). |
| Have a structure with known maxCond and current conditionDamage. | Query getDecayPercentage() on the structure. | The result matches (maxCond - conditionDamage) * 100 / maxCond (lines 644-652). |
| Populate permission lists using structurePermissionList.addToList() for players on admin, entry, ban, and hopper lists, guild members, and privileged players. | Test isOnAdminList(), isOnEntryList(), isOnBanList(), and isOnHopperList() for each respective player group. | Each method returns true for players on the corresponding list and false otherwise. |
| Create a credit object with known cash and bank balance. Set cashFirst=true in payMaintenance(). | Call payMaintenance() on the structure. | Credits are subtracted from cash first, then bank (lines 670-686). |

## survey-sample

| Setup | Bot does | Expect |
|---|---|---|
| Bot has surveying mod >= 20 and survey ability; is outdoors, upright, not mounted; mind/action above costs; range set for tool; verify planet has in-shift spawn | Call survey list. | List message arrives; every entry's class fits the tool. Report 'no message' separately from 'empty list'. |
| Bot has valid surveying setup and range set. | Call requestSurvey. | start_survey arrives with the name; results arrive within about 4 s with points² values (9, 16 or 25); mind drops by about 100 - focus/15; waypoint and survey_waypoint appear only when the best point  |
| Bot is at a spot of 10% or more. | Call requestCoreSample. | start_sampling arrives, bot is crouched, action drops by about 124 - quickness/12.5; about 3 s later exactly one of: sample_located (%DI equals units gained in inventory), trace_amount, sample_failed, |
| Bot has completed a core sample request. | Wait approximately 25 seconds. | Another result follows about 25 s later. |
| Bot is in the middle of a sampling loop (before 25s elapsed). | Call requestCoreSample again early. | tool_recharge_time message arrives. |
| Bot is crouched during sampling. | Stand up. | The loop ends, so no result arrives 25 s later (inferred). |
| Perform multiple surveying actions to trigger node pop-ups. | Observe node pop-up occurrences. | Handle the node pop-up, which appears one time in 51. |

## travel-shuttles

| Setup | Bot does | Expect |
|---|---|---|
| Ensure server has been up longer than BootDelay. Position bot ≤8 m from the starport terminal (indoors). Ensure bot has enough credits, free inventory slots, an | Locate the terminal using esk-hoth.py:23-41 logic and select a route with underscores or 'single' in its name (cresh-travel.py:27, esk-hoth.py:46). | The route is allowed for purchase. |
| Bot is at the terminal with valid route selected. | Purchase a one-way ticket. | Exactly one new ticket item appears in inventory; credits decrease by fare plus tax; pay-success message is displayed; ticket_purchase_complete SUI is shown. |
| Bot has purchased a ticket and is ≤25 m from the shuttle. | Use collector option 20 to board. | Zone or position changes to within landingRange of the arrival point; ticket is removed from inventory. |
| Bot receives 'ready to board in N' message while near the shuttle. | Wait N+6 seconds and attempt to use collector option 20 again. | Boarding succeeds (zone/position changes within landingRange; ticket removed). |

## vehicle-mount

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the player has a datapad slotted (`getSlottedObject("datapad")`) and a vehicle deed in inventory. Be outdoors, not in combat, not inside a building. | Generate the vehicle deed using the datapad. | Datapad contains a new VehicleControlDevice object; deed no longer exists in inventory or world. |
| Be outside any city region and not privileged to trigger the 15-second delay. | Call the vehicle using the datapad. | System message: `"pet/pet_menu:call_vehicle_delay"` with "15" seconds. |
| Wait for the 15-second delay to expire after calling the vehicle outdoors. | Check for the appearance of the vehicle. | A VehicleObject appears at player position; Player state remains unchanged during delay; no `RIDINGMOUNT` yet. |
| Be indoors or inside a city region. | Call the vehicle using the datapad. | System message: none (instant spawn); VehicleObject appears immediately. |
| Have the vehicle spawned and accessible. | Mount the vehicle. | Player state changes to `RIDINGMOUNT`; `getParent()` on player returns the vehicle object; Vehicle state is `MOUNTEDCREATURE`. |
| Be mounted on a vehicle. | Check player attributes and buffs. | Player's run speed and acceleration mods change (check via attribute list or speed queries); Restricted buffs are removed from player. |
| Be mounted on a vehicle. | Dismount the vehicle. | Player state reverts from `RIDINGMOUNT`; `getParent()` returns nullptr (or previous parent); Vehicle state changes from `MOUNTEDCREATURE`. |
| Have a spawned vehicle and a valid datapad with control device. | Store the vehicle using the datapad. | VehicleObject is destroyed from world; Control device remains in datapad. |

## veteran-rewards

| Setup | Bot does | Expect |
|---|---|---|
| Create an account with known age and ensure it has reached at least one milestone threshold (e.g., 30+ days simulated). Have a player character logged in. | Run `/getVeteranRewardTime` | A system message showing account age in days appears. |
| Ensure the account is eligible for a reward milestone. | Run `/getVeteranRewardTime` | A system message with the milestone number and claim prompt appears. |
| Ensure the account is not yet eligible for a new milestone. | Run `/getVeteranRewardTime` | A 'not_eligible' message plus next milestone countdown appears. |
| Have a player character logged in. | Run `/getVeteranRewardTime` | A character play time message appears at the end. |
| Ensure the account is eligible for a reward milestone. | Run `/claimVeteranReward` and select a reward from the SUI list box, then confirm | The reward item appears in the player's inventory or is delivered via mail. |
| Ensure the account has claimed a reward where `oneTime` is true. | Run `/getVeteranRewardTime` | No new eligible milestone for that day count is shown. |
| Have an account with 180+ days of age logged in. | Run `/getVeteranRewardTime` | A JTL yacht announcement message appears. |

## weather

| Setup | Bot does | Expect |
|---|---|---|
| Ensure player is on a planet with hasDamagingSandstorms=1 (e.g., Tatooine), wearing no protective clothing, not in shelter/camping/riding, and admin level >= 15 | Execute `/server weather change 4` to force EXTREMESTORM. | System message: "The weather around you quickly becomes damaging, seek shelter immediately." |
| Player is in the EXTREMESTORM state as established by previous step. | Check player status effects. | Player blinded state is set to 60 seconds. |
| Player is in the EXTREMESTORM state as established by previous step. | Check player posture. | Player posture is KNOCKEDDOWN. |
| Player is in the EXTREMESTORM state as established by previous step. | Observe HAM bar changes after damage tick. | HEALTH, ACTION, and MIND attributes are decreased by `sandstormDamage - totalCoverings`. |
| Player is in the EXTREMESTORM state as established by previous step. | Execute `/server weather info`. | Output shows the current Weather ID has changed to reflect the storm. |
| Player is in the EXTREMESTORM state as established by previous step. | Wait for the storm duration to expire or manually end it if possible. | System message: "The storm has subsided." |

## world-bosses

| Setup | Bot does | Expect |
|---|---|---|
| Ensure the server has been running for > 120 seconds or manually trigger slot filling. | Verify that the zone containing the target planet is enabled using `isZoneEnabled` check at line 99. | The zone is confirmed as enabled. |
| Locate the big game hunter NPC on tatooine at the expected coordinates. | Confirm the NPC exists at those coordinates. | The big game hunter NPC is present. |
| Kill a spawned world boss while having damaged players nearby. | Check the system messages received by the damaged players. | Players receive the message: "You receive 25000 credits for helping bring down [boss name]." (line 164). |
| Observe a boss spawn, death, and escape event. | Verify the galaxy broadcast text format at these events (lines 143, 172, 210). | The color code `\#ffcc66` renders as orange in the broadcast. |
| Have a player interact with the credit reward system after a boss kill. | Check if `addBankCredits(25000, true)` was called (line 163). | The player's bank balance increased by exactly 25,000. |
| Spawn a world boss. | Check the spawned boss's custom object name and HAM pools. | The name ends with `(world boss)` (line 127) and HAM pools are multiplied correctly (e.g., ham 4 boss has 4× base template maxHAM for health, action, mind) (lines 129–133). |
| Talk to the big game hunter NPC. | Check the player's datapad for waypoints. | Orange waypoints appear pointing to the boss's approximate location (line 231). |
| Kill a boss or wait for it to expire, then wait for `respawnAfterKill` or `respawnAfterEscape` delay. | Check for new boss spawns and roster entries. | A new boss fills the slot and no duplicate roster entries exist simultaneously (lines 82–91, 175–178, 208–211). |


## Claude's review (18 Oct 6:28 AM)

**A checklist skeleton, not a test plan.**
- Each row only restates section 3 of a draft research report. The corrections that reviews add at the end of those reports (Claude's, and ChatGPT's C63/C63b/C63c) never reach section 3, so a rerun would not pick them up either.
  - Example: entertainer-xp-sources still expects dance XP without a flourish.
- **Before a scenario uses a row:** read that report's review section.
- **Drop the rows a bot can't do.** Many say "call `hasBadge()`", "query the PlayerObject" or "observe network traffic". The bot sees only system messages, its own status, inventory and the agent commands.

Not checked row by row (about 560 rows).
