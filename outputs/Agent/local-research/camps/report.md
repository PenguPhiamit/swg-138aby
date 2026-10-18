# Scout Camp Mechanics Report

## 1. Short Answer

A scout places a camp kit from inventory (selected via menu option 20) after meeting placement conditions: the player must have the "camp" skill mod at or above the camp's required level, not be in combat, standing still, outside cities/water/cells, and far enough from other camps, buildings, and lairs. The placed camp creates an active area that applies template skill mods to anyone who enters, provides wound healing via a HEALINGRECEIVED observer hook, and tracks XP. After the owner leaves for 60 seconds (ABANDONTIME), or immediately on combat, the camp is abandoned (fire changes, terminal renamed). If unused for 55 minutes (DESPAWNTIME), it despawns and awards XP to the owner based on uptime, visitors, and healing done. The terminal offers status, disband, assume ownership, and faction requisition options.

## 2. How It Works

### Placement Conditions

- **Skill check**: player's "camp" skill mod must be >= campStructureData->getSkillRequired() (CampKitMenuComponent.cpp:95-101).
- **Not in combat**: player->isInCombat() blocks placement (CampKitMenuComponent.cpp:103-106).
- **Location restrictions**:
  - Cannot be inside a cell object (CampKitMenuComponent.cpp:108-111).
  - Must be standing and not riding a mount (CampKitMenuComponent.cpp:118-121).
  - Cannot be in a city region (CityRegion* check, CampKitMenuComponent.cpp:123-128).
  - Cannot be swimming or in water (CampKitMenuComponent.cpp:131-134).
  - Camping must be permitted at the coordinates via planetManager->isCampingPermittedAt() (CampKitMenuComponent.cpp:197-200).
- **Ownership**: the camp kit must be a sub-child of the player (inventory check, CampKitMenuComponent.cpp:40-41, 113-116).
- **One camp per player**: ghost->getTotalOwnedStructureCount() loop checks no existing camp structure (CampKitMenuComponent.cpp:137-146). Player also cannot be inside another camp (player->getCurrentCamp() != nullptr, CampKitMenuComponent.cpp:149-152).
- **Proximity to other objects**:
  - Other camps must be outside noBuildRadius + camp radius (CampKitMenuComponent.cpp:161-164).
  - Other structures must be > 100 distance (CampKitMenuComponent.cpp:166-169).
  - Lairs must be outside noBuildRadius + camp radius, detected via OBJECTDESTRUCTION and CREATUREDESPAWNED observers (CampKitMenuComponent.cpp:171-193).

### Timings

- **ABANDONTIME**: 60000 ms = 1 minute (CampSiteActiveArea.idl:55).
- **DESPAWNTIME**: 3300000 ms = 55 minutes (CampSiteActiveArea.idl:52).

### Camp Creation Flow

1. Player selects menu option 20 on the camp kit (CampKitMenuComponent.cpp:48).
2. All placement checks run; if any fail, a system message is sent and function returns.
3. On success: player sees "@camp:starting_camp" (CampKitMenuComponent.cpp:202).
4. StructureManager::instance()->placeCamp() creates the camp structure (CampKitMenuComponent.cpp:208).
5. Terminal custom name set to "FirstName LastName's Camp" (CampKitMenuComponent.cpp:248-254).
6. CampSiteActiveArea created, initialized with camp data, radius set from template (CampSiteActiveAreaImplementation.cpp:36-39), owner/terminal/camp linked, abandoned=false (CampKitMenuComponent.cpp:277-303).
7. Active area added to camp object (CampKitMenuComponent.cpp:305).
8. Player sees "@camp:camp_complete" (CampKitMenuComponent.cpp:307).
9. Camp kit use count decreased (CampKitMenuComponent.cpp:312).

### Healing and Regeneration Inside the Camp

- When a player enters the active area, notifyEnter() is called (CampSiteActiveAreaImplementation.cpp:65).
- camp->addTemplateSkillMods(player) applies skill mods from the camp template to the player (CampSiteActiveAreaImplementation.cpp:77).
- Player receives system message "@camp:sys_camp_heal" with text "While in the camp, medics and entertainers can heal your wounds." (CampSiteActiveAreaImplementation.cpp:99).
- A prose message "prose_camp_enter" with the terminal name is also sent (CampSiteActiveAreaImplementation.cpp:95-97).
- campObserver is deployed to listen for HEALINGRECEIVED events (CampSiteActiveAreaImplementation.cpp:107).
- When healing is received, notifyHealEvent() adds XP: currentXp += (campStructureData->getExperience() / 180) per heal event (CampSiteActiveAreaImplementation.cpp:148).

### Abandonment

- **Trigger by timer**: when the owner leaves the camp and abandonTask is not already scheduled, it is set to ABANDONTIME (60 seconds) (CampSiteActiveAreaImplementation.cpp:135-141).
- **Trigger by combat**: if the owner starts combat, notifyCombatEvent() immediately executes abandonCamp() (CampSiteActiveAreaImplementation.cpp:152-166).
- When abandoned: campFire is replaced with "campfire_smoldering.iff" (CampSiteActiveAreaImplementation.cpp:184-185), currentXp resets to 0 (CampSiteActiveAreaImplementation.cpp:208), terminal renamed to "Abandoned Camp" (CampSiteActiveAreaImplementation.cpp:222), owner receives "@camp:sys_abandoned_camp" ("Your camp has been abandoned.") (CampSiteActiveAreaImplementation.cpp:227).
- After abandonment, despawn timer is shortened: newTime = DESPAWNTIME / 6 = ~9.17 minutes (CampSiteActiveAreaImplementation.cpp:214).

### Despawning and XP Award

- despawnTask fires after DESPAWNTIME (55 minutes) or the shortened time if abandoned (CampDespawnTask.h:38, CampSiteActiveAreaImplementation.cpp:60, 214).
- XP calculation at despawn (CampSiteActiveAreaImplementation.cpp:242-253):
  - durationUsed = min(1.0, elapsed_time / (campStructureData->getDuration() / 4))
  - amount = campXp * durationUsed + (visitors.size() - 1) * (campXp / 30) * durationUsed + currentXp * durationUsed
  - XP is awarded to campOwner for the "camp" skill via playerManager->awardExperience() (CampSiteActiveAreaImplementation.cpp:253).
- Camp structure and active area are destroyed (CampSiteActiveAreaImplementation.cpp:280-289).

### Terminal Menu Options

Available by interacting with the camp terminal within 16 meters (CampTerminalMenuComponent.cpp:54, 189, 247, 296):

- **Status** (SERVER_MENU1): opens SuiListBox showing owner name, uptime in minutes/seconds, visitor count (CampTerminalMenuComponent.cpp:58, 144-146, 289-360).
- **Disband** (SERVER_CAMP_DISBAND): only for the owner when not abandoned; calls despawnCamp() immediately (CampTerminalMenuComponent.cpp:82-83, 138-140, 182-237).
- **Assume ownership** (SERVER_CAMP_ASSUME_OWNERSHIP): shown when abandoned and player has no camp; requires sufficient "camp" skill mod (CampTerminalMenuComponent.cpp:84-104, 141-143, 239-287). On success, resets timers, clears visitors, updates terminal name/faction (CampSiteActiveAreaImplementation.cpp:295-395).
- **Requisition** items (SERVER_MENU3/4/5): available only if player's faction matches the terminal's faction and status is OVERT; calls Lua function "recruiterScreenplay" with "sendPurchaseSui" for weapons or installations (CampTerminalMenuComponent.cpp:106-111, 148-174).

### Faction Handling

- If skillRequired >= MAP_REGISTER_MOD and camp faction is not NEUTRAL, terminal faction/PvP status is set from the camp object, and the camp is registered on the planetary map with imperial/rebel category (CampKitMenuComponent.cpp:256-272).

## 3. What a Bot Test Should Check

### Setup Required
- Player must have the "camp" skill mod at or above the target camp's required level (obtainable via skill-up or cheat commands).
- Player must be in an outdoor, non-city, non-water location where camping is permitted.
- Player must not be in combat, sitting, riding, or inside a cell.
- No other camps, buildings, or lairs within the proximity thresholds.

### Observable Results to Verify

1. **Placement success**:
   - System message "@camp:starting_camp" appears (CampKitMenuComponent.cpp:202).
   - System message "@camp:camp_complete" appears (CampKitMenuComponent.cpp:307).
   - A camp structure object exists at player position.
   - A terminal child object exists with custom name "FirstName LastName's Camp" (CampKitMenuComponent.cpp:248-254).
   - An active area is attached to the camp.

2. **Entering the camp**:
   - System message with prose_camp_enter containing terminal name (CampSiteActiveAreaImplementation.cpp:95-97).
   - System message "@camp:sys_camp_heal" ("While in the camp, medics and entertainers can heal your wounds.") (CampSiteActiveAreaImplementation.cpp:99).
   - Template skill mods from the camp are applied to the player (CampSiteActiveAreaImplementation.cpp:77).

3. **Healing while inside**:
   - Trigger a heal event on the player while inside the camp.
   - Verify currentXp increments by (campStructureData->getExperience() / 180) per heal (CampSiteActiveAreaImplementation.cpp:148). This is internal state; indirect verification via XP awarded at despawn is more practical.

4. **Leaving and abandonment**:
   - Exit the camp as owner.
   - After ~60 seconds, verify terminal name changes to "Abandoned Camp" (CampSiteActiveAreaImplementation.cpp:222).
   - Verify campFire object changes appearance to "campfire_smoldering.iff" (CampSiteActiveAreaImplementation.cpp:184-185).
   - Owner receives "@camp:sys_abandoned_camp" ("Your camp has been abandoned.") (CampSiteActiveAreaImplementation.cpp:227).

5. **Assuming ownership**:
   - Interact with the abandoned terminal.
   - Verify "assume ownership" menu option appears (CampTerminalMenuComponent.cpp:103).
   - After assuming, verify terminal name reverts to owner's name (CampSiteActiveAreaImplementation.cpp:385-391), abandoned flag is false (CampSiteActiveAreaImplementation.cpp:349), and owner receives "@camp:assuming_ownership" ("You assume ownership of the camp.") (CampSiteActiveAreaImplementation.cpp:394).

6. **Disbanding**:
   - Owner interacts with terminal, selects disband.
   - Verify camp structure and active area are destroyed.

7. **XP at despawn**:
   - Let camp exist for a known duration, then despawn (via timer or manual disband).
   - Verify XP awarded to owner's "camp" skill matches the formula: campXp * durationUsed + (visitors.size() - 1) * (campXp / 30) * durationUsed + currentXp * durationUsed (CampSiteActiveAreaImplementation.cpp:242-253).

8. **Proximity checks**:
   - Place a camp, then attempt to place another within the noBuildRadius + camp radius of the first; verify "@camp:error_camp_too_close" message (CampKitMenuComponent.cpp:162-163).
   - Place near a building (> 100 distance threshold); verify "@camp:error_building_too_close" (CampKitMenuComponent.cpp:167-168).

## 4. Likely Reasons a Test Sees No Effect

- **Insufficient camp skill mod**: player->getSkillMod("camp") < campStructureData->getSkillRequired() causes silent failure with "@camp:sys_nsf_skill" (CampKitMenuComponent.cpp:95-101).
- **In combat**: isInCombat() check blocks placement (CampKitMenuComponent.cpp:103-106).
- **Wrong location**: city region, water, cell interior, or planetManager->isCampingPermittedAt() returns false (CampKitMenuComponent.cpp:123-134, 197-200).
- **Already has a camp**: ghost->getTotalOwnedStructureCount() loop finds an existing camp (CampKitMenuComponent.cpp:137-146) or player is inside another camp (CampKitMenuComponent.cpp:149-152).
- **Proximity violations**: other camps, buildings, or lairs too close (CampKitMenuComponent.cpp:158-193).
- **Not standing/riding mount**: posture check fails (CampKitMenuComponent.cpp:118-121).
- **Camp kit not in inventory**: isASubChildOf() check fails (CampKitMenuComponent.cpp:40-41, 113-116).
- **Camp already despawned or broken**: active area null check causes error and camp destruction (CampTerminalMenuComponent.cpp:74-77, 318-329).

## 5. Open Questions

- **What exactly do addTemplateSkillMods/removeTemplateSkillMods modify?** The files reference these methods (CampSiteActiveAreaImplementation.cpp:77, 124) but the implementation is not in the provided files. We know the camp provides medical rating and wound regen rates (CampSiteActiveArea.idl:101-118), but the exact skill mods applied are unclear.
- **What is MAP_REGISTER_MOD?** Used at CampKitMenuComponent.cpp:258 to determine faction registration, but its value is not defined in these files.
- **How does campStructureData->getDuration() work?** Referenced in XP calculation (CampSiteActiveAreaImplementation.cpp:242) but the template structure definition is not included.
- **What are the exact noBuildRadius values for different terrain/planet types?** The code uses planetManager->isCampingPermittedAt() and object templates' getNoBuildRadius(), but the underlying logic is in missing files.
- **How do visitors.size() count work exactly?** Visitors are added on notifyEnter (CampSiteActiveAreaImplementation.cpp:102-103) but there is no corresponding removal on exit, so the count may accumulate incorrectly over time.
- **What happens to skill mods when a player exits the camp?** removeTemplateSkillMods is called (CampSiteActiveAreaImplementation.cpp:124), but without seeing that function's implementation, we cannot confirm what is removed or restored.
