# Mission Terminals and Mission Completion Report

## 1. Short Answer

Missions are generated when a player interacts with a mission terminal, which populates their mission bag with empty slots and then fills them based on terminal type: general terminals give destroy (slots 0–5) and deliver (6–11) missions; artisan terminals give survey (0–5) and crafting (6–11); entertainer terminals give dancer (0–5) and musician (6–11); scout terminals give recon (0–5) and hunting (6–11); bounty terminals give bounty missions (0–9). Faction terminals add factional variants. Players may hold up to 6 active missions by default (configurable via `Core3.MissionManager.MaxActiveMissions`), with only one bounty mission allowed at a time. Destroy missions complete when the target lair is destroyed; deliver missions complete when the item is delivered to the NPC at the end position; survey missions complete via survey tool use on resource nodes; entertainer missions complete via performance at the target structure; crafting missions complete via crafting the required item. The cresh-missions.py scenario tests general terminal missions (deliver and destroy) and verifies that Ilsa's datapad fills to 6 missions while a 7th is refused, and that Cresh's reward reaches his bank after mission completion.

## 2. How It Works

### Terminal Types and Mission Generation

The `populateMissionList` function dispatches to different randomizers based on terminal type (lines 619–638):

- **General terminal** (`isGeneralTerminal()`): Calls `randomizeGeneralTerminalMissions` (line 625), which generates destroy missions for slots 0–5 and deliver missions for slots 6–11 (lines 658–662).
- **Artisan terminal** (`isArtisanTerminal()`): Calls `randomizeArtisanTerminalMissions` (line 627), generating survey missions for slots 0–5 and crafting missions for slots 6–11 (lines 687–691).
- **Entertainer terminal** (`isEntertainerTerminal()`): Calls `randomizeEntertainerTerminalMissions` (line 629), generating dancer missions for slots 0–5 and musician missions for slots 6–11 (lines 716–720).
- **Scout terminal** (`isScoutTerminal()`): Calls `randomizeScoutTerminalMissions` (line 631), generating recon missions for slots 0–5 and hunting missions for slots 6–11 (lines 745–749).
- **Bounty terminal** (`isBountyTerminal()`): Calls `randomizeBountyTerminalMissions` (line 633), generating bounty missions for slots 0–9 (line 776). Requires the player to have `combat_bountyhunter_novice` skill (lines 179–182, 1079–1082).
- **Imperial/Rebel faction terminals** (`isImperialTerminal()` / `isRebelTerminal()`): Calls `randomizeFactionTerminalMissions` (lines 635–637), generating destroy (0–5), deliver (6–11), and optionally crafting, recon, dancer, musician missions for slots 12+ (lines 804–822).

Before populating, the system ensures the player's mission bag has enough empty slots. The base capacity is 12 (line 207), with bonuses added if factional missions are enabled: +6 for crafting (line 211), +6 for recon (line 215), and +12 for entertainer (line 219). Empty mission objects are created to fill the bag (lines 222–227).

### Difficulty, Distance, and Reward Calculations

**Destroy missions** (`randomizeGenericDestroyMission`, lines 835–1001):
- **Difficulty**: Randomized between the lair spawn's min and max difficulty (line 858), then mapped to a display value based on player level or group level (lines 866–876). Display difficulty = `difficultyLevel` for levels < 5, else `difficultyLevel + group/player level`.
- **Distance**: `destroyMissionBaseDistance + destroyMissionDifficultyDistanceFactor * difficultyLevel + random(destroyMissionRandomDistance) + random(destroyMissionDifficultyRandomDistance * difficultyLevel)` (lines 902–903). The position must be outside cities and on land (lines 911–932).
- **Reward**: `destroyMissionBaseReward + destroyMissionDifficultyRewardFactor * difficultyLevel + random(destroyMissionRandomReward) + random(destroyMissionDifficultyRandomReward * difficultyLevel)` (lines 951–952).
- **City bonus**: Applied as `1 + private_spec_missions skill mod / 100` (line 668).
- **Slicer bonus**: If the player sliced the terminal, reward is multiplied by 1.5 (line 665).

**Deliver missions** (`randomizeGenericDeliverMission`, lines 1276–1416):
- **Difficulty**: Fixed at 5 (line 1408).
- **Distance**: Mission can be in-town or out-of-town, randomly chosen (lines 1278–1281). Start and end positions are selected from NPC spawn points within the city (lines 1340–1369).
- **Reward**: `40 + (distance from player to start + distance from start to end) / 10` (line 1389).

**Survey missions** (`randomizeGenericSurveyMission`, lines 1003–1076):
- **Difficulty**: Based on player's `surveying` skill mod. Base level is 50, increased by 10 for each threshold crossed: >30, >50, >70, >90, and +5 at >100 (capped at 95) (lines 1011–1027). Mission level = `50 + 5 * random((maxLevel - 50) / 5)`.
- **Distance**: Start position is player's current position (line 1070).
- **Reward**: `400 + (missionLevel - 50) * 20 + random(100)` (line 1065).

**Crafting missions** (`randomizeGenericCraftingMission`, lines 1448–1483):
- Generated by modifying a deliver mission. Target template is changed to `attunement_grid.iff` (line 1476).
- **Difficulty**: Inherited from the base deliver mission (5).
- **Distance**: Same as deliver mission.
- **Reward**: Same as deliver mission.

**Entertainer missions** (`randomizeGenericEntertainerMission`, lines 1485–1564):
- **Difficulty**: `5 * randomRange` where `randomRange = random(2) + 1`, so difficulty is 5 or 10 (lines 1487–1489, 1561).
- **Distance**: Target is a performance location structure; distance from player to target determines reward (line 1534).
- **Reward**: `100 + distance / 10 + random(100)` (line 1536).

**Bounty missions** (`randomizeGenericBountyMission`, lines 1078–1274):
- **Difficulty**: Level 1, 2, or 3 based on bounty hunter investigation skills (lines 1092–1097). For NPC targets: `3 * creoLevel + 7` (line 1256). For player targets: fixed at 75 (line 1166).
- **Distance**: Player targets have no distance (end position 0,0) (line 1128). NPC targets use random planet and spawn point (lines 1201–1207).
- **Reward**: Varies by level and target type. For player Jedi: 50000 if jediState >= 4, else 25000 (lines 1146–1148). For NPC targets: `creoLevel * (200 + random(200))` for level 1, scaled for levels 2 and 3 (lines 1221–1227).

### Mission Limits

- **Maximum active missions**: Configurable via `Core3.MissionManager.MaxActiveMissions`, default 6 (line 270).
- **Bounty restriction**: Only one bounty mission allowed at a time (line 272).
- **Datapad volume limit**: A full datapad refuses the mission before anything is created (lines 281–285).

### Completion and Failure

**Mission abort** (`handleMissionAbort`, lines 560–617):
- Cannot abort while incapacitated or in combat (lines 561–569).
- Bounty missions have additional cooldown restrictions based on recent combat with target (lines 577–580).
- Clears journal quest for space missions (lines 583–598).
- Calls `mission->abort()` and `removeMission` (lines 601, 616).

**Mission failure** (`handleMissionFail`, lines 540–558):
- Clears journal quest and calls `mission->abort()` and `removeMission`.

**Specific completion logic** for each mission type is in separate objective classes (`DestroyMissionObjective`, `DeliverMissionObjective`, `SurveyMissionObjective`, `EntertainerMissionObjective`, `CraftingMissionObjective`) included at lines 14–18 but not shown in this file. The scenario comments indicate:
- Destroy missions complete when the lair is destroyed (scenario line 9).
- Deliver missions complete when the item is delivered to the NPC at the end position (scenario line 6).
- A mission is done when it leaves the player's datapad and the reward reaches their bank (scenario line 10).
- Missions expire after 48 hours if not aborted (scenario line 14).

### Messages the Player Sees

- Out of range: `"ui_radial_out_of_range_prose"` (line 172).
- Not a bounty hunter terminal: `"@mission/mission_generic:not_bounty_hunter_terminal"` (lines 180, 1080).
- Banned from city: `"@city/city:banned_services"` (line 189).
- Cooldown active: `"You can't request missions yet, please wait a bit before trying again."` (line 195).
- Too many missions: `"mission/mission_generic:too_many_missions"` (line 273).
- Datapad full: `"mission/mission_generic:datapad_full"` / `"Your datapad is full. You must first free some space."` (lines 282–283, 318).
- Mission expired: `"Mission has expired."` (line 295).
- Cannot abort while incapacitated: `"You cannot abort a mission while incapacitated."` (line 562).
- Cannot abort while in combat: `"You cannot abort a mission while in combat."` (line 567).
- Bounty cooldown: `"You cannot abort a bounty hunter mission this soon after being in combat with the mission target."` (line 578).

## 3. What a Bot Test Should Check

### Observable Results

1. **Terminal discovery**: Verify the scenario finds terminals of each type within range (cresh-missions.py line 4–5, 32–34).
2. **Mission generation at general terminal**:
   - First 6 slots should be destroy missions (lines 658–659).
   - Next 6 slots should be deliver missions (lines 660–661).
   - Deliver mission should have `inTown` flag if near city center (scenario line 6, cresh-missions.py line 45).
3. **Mission acceptance limits**:
   - Ilsa fills her datapad to 6 destroy missions; a 7th must be refused (scenario line 7, cresh-missions.py line 7).
   - Only one bounty mission allowed at a time (line 272).
4. **Destroy mission properties**:
   - Difficulty should match lair spawn range and player level (lines 856–876).
   - Distance should be within calculated range (lines 902–903).
   - Reward should follow formula (line 951–952).
5. **Deliver mission properties**:
   - Should have start and end positions (lines 1383–1384).
   - Reward should be distance-based (line 1389).
6. **Mission completion**:
   - Mission leaves datapad upon completion (scenario line 10).
   - Reward reaches player's bank, divided by group size if grouped (scenario line 10, cresh-missions.py line 61).
7. **Newbie/statue terminal rejection**: Both should refuse with `"@skill_teacher:skill_terminal_disabled"` (lines 165–168, scenario line 8).

### Required Setup

1. **Marksman profession**: Every bot needs `combat_marksman_master` skill to fight lairs (scenario lines 12–15, cresh-missions.py line 29).
2. **Terminal proximity**: General terminal must be within 2 km (scenario line 6, cresh-missions.py line 36).
3. **Group size calculation**: Divisor for reward sharing (cresh-missions.py line 31).

## 4. Likely Reasons a Test Sees No Effect

1. **Terminal not found or out of range**: The general terminal must be within 2 km; if not, the scenario returns early (cresh-missions.py lines 35–37).
2. **Player not at terminal**: Must be within 6 meters for mission list request (line 170).
3. **Cooldown active**: `mission_list_request` cooldown of ~1400ms prevents rapid requests (lines 194–200).
4. **Datapad full**: If the datapad volume limit is reached, missions are refused (lines 281–285).
5. **No valid lair spawns**: Destroy missions require a valid lair spawn within difficulty range; if none found, mission generation fails silently (lines 844–846, 935–937).
6. **City ban**: Player banned from the terminal's city cannot use services (lines 187–192).
7. **Missing skill for bounty terminal**: `combat_bountyhunter_novice` required (lines 179–182).
8. **Factional missions disabled**: Crafting, recon, and entertainer factional missions only generate if enabled in Lua config (lines 79–95).

## 5. Open Questions

1. **Exact completion logic for each mission type**: The source file includes headers for `DestroyMissionObjective`, `DeliverMissionObjective`, `SurveyMissionObjective`, `EntertainerMissionObjective`, and `CraftingMissionObjective` (lines 14–18), but their implementation files are not provided. How exactly does each objective type detect completion?
2. **48-hour expiration mechanism**: The scenario comment mentions missions expire after 48 hours (scenario line 14), but the source code does not show where this timer is set or checked. Which file handles mission expiration?
3. **Group reward distribution**: How is the reward divided among group members? The scenario mentions "reward // group size" (scenario line 10), but the source code only shows `mission->setRewardCredits()` without division logic. Where does group splitting occur?
4. **Lua configuration values**: The code reads settings from `scripts/managers/mission/mission_manager.lua` (line 45), including `destroyMissionBaseDistance`, `destroyMissionDifficultyDistanceFactor`, etc. (lines 106–113). What are the actual default values in that file?
5. **Survey mission completion**: How does the survey tool interact with the `SurveyMissionObjective` to complete the mission? What efficiency threshold is needed?
6. **Entertainer mission performance requirements**: What specific performance actions or skill checks complete an entertainer mission?
7. **Crafting mission item selection**: The code picks a random crafting item from `craftingMissionItems` (line 382), but what items are in that list and how is the target item determined for the player to craft?
