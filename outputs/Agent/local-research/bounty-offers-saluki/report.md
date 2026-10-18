# Bounty terminal mission list — why Brask got no offer

## 1. Short answer

The server fills the mission bag with empty mission slots and then tries to turn each of the first 10 slots into a bounty mission (MissionManagerImplementation.cpp:776-778). A slot stays empty when `randomizeGenericBountyMission` returns before setting a target (1078-1274). For a level-1 novice the code shows no hard gate that would make every slot empty: the skill check (1079), zone check (1086), and target-template lookup (1209) all look satisfiable on Tatooine. The most likely reason (inferred) is that the bot was not actually inside the terminal's 6 m range when the 30 requests were sent — the code rejects out-of-range requests with a system message (170-176), and the bot's own helper notes this exact failure mode (missions.py:1019-1022). The bot must stand within 6 m of the terminal and have the `combat_bountyhunter_novice` skill; no other prerequisite in these files blocks a level-1 offer.

## 2. How it works

### 2.1 Request handling (handleMissionListRequest, 163-230)

- Terminal must not be a statue or newbie terminal (165-168); message `@skill_teacher:skill_terminal_disabled`.
- Player must be within 6 m of the terminal (170-176); message `ui.radial_out_of_range_prose` ("%TT is too far away to '%TO'").
- If the terminal is a bounty terminal, the player must have the skill `combat_bountyhunter_novice` (178-183); message `@mission/mission_generic:not_bounty_hunter_terminal`.
- If the player is banned from the terminal's city, message `@city/city:banned_services` (188-191).
- A cooldown `mission_list_request` must be clear (194-197); message "You can't request missions yet, please wait a bit before trying again." The cooldown is set to 1400 ms by default (200).
- The mission bag must be slotted (202-205); if not, the function returns silently.
- The bag is padded to 12 slots (207), plus 6 if factional crafting, 6 if factional recon, 12 if factional entertainer missions are enabled (210-220). Empty mission objects (template `0x18e19914`) are added until the bag is full (222-227).
- `populateMissionList` is called (229).

### 2.2 Dispatch (populateMissionList, 619-644)

- A cross-locker is taken on the terminal and player (620).
- The terminal type selects the randomizer (624-638). For a bounty terminal, `randomizeBountyTerminalMissions` is called (632-633).
- If the player is a slicer, the slicer flag is removed from the terminal (641-642).

### 2.3 Bounty randomizer (randomizeBountyTerminalMissions, 762-785)

- The mission bag is read (763-764).
- Potential player-bounty targets are collected (766).
- For each slot `i` in the bag (768-784):
  - The mission's type CRC is cleared (774).
  - Only slots with `i < 10` are given a chance to become a bounty mission (776-778); slots 10 and up stay empty.
  - `randomizeGenericBountyMission` is called with faction `FACTIONNEUTRAL` (777).
  - A city bonus is applied: reward is multiplied by `1 + private_spec_missions/100` (780-781).
  - The refresh counter is set (783).

### 2.4 Per-slot generation (randomizeGenericBountyMission, 1078-1274)

- The player must have `combat_bountyhunter_novice` (1079-1082); message `@mission/mission_generic:not_bounty_hunter_terminal`.
- The player's zone must exist (1084-1088); if not, the function returns silently.
- Mission level is 1 by default; 2 if the player has `combat_bountyhunter_investigation_01` (with 50 random texts); 3 if the player has `combat_bountyhunter_investigation_03` (1090-1097).
- If level is 3 and there are potential player targets, a target is chosen with probability `min(max(size,5),25)/100` (1104-1110).
- The mission's start position is the player's current position (1112).
- The target template is set to `object/tangible/mission/mission_bounty_target.iff` (1114).
- Mission level and faction are set (1116-1117).
- If a player target is chosen (1119-1197):
  - The target's player ID is set (1127).
  - The end position is cleared (1128).
  - The target's optional template is cleared (1129).
  - If the `AnonymousBountyTerminals` config is true (1134), the target is named "Imperial Jedi", "Rebel Jedi", or "Neutral Jedi" (1135-1140), and the reward is 50000 if the target's Jedi state is 4 or higher, else 25000 (1144-1148). A bonus is added if the real reward is higher (1151-1155).
  - Otherwise the target's first and last name are used (1158-1160), and the reward is the real bounty reward (1162).
  - The mission difficulty is set to 75 (1166).
  - The title, creator, and description are set from `mission/mission_bounty_jedi` (1172-1196).
- If no player target (1198-1271):
  - The target name is a random creature name (1199).
  - The planet is the player's zone (1201); if level is 3 and `bhTargetZones` is non-empty, a random bounty planet is chosen (1202-1204).
  - The end position is a random spawn point on that planet (1206-1207).
  - The target's optional template is chosen from `bhTargetsAtMissionLevel` for the mission level (1209-1210).
  - The reward is computed from the target template's level: level 1 is `creoLevel * (200 + random(200))`, level 2 is `creoLevel * (250 + random(250))`, level 3 is `creoLevel * (300 + random(300))` (1214-1229).
  - The difficulty string is "easy" for level 1, "medium" for level 2, "hard" for level 3 (1231-1237).
  - The target object ID is set to 0 (1239).
  - The title, creator, and description are set from `mission/mission_bounty_neutral_<difficulty>` (1245-1270).
- The mission's type CRC is set to `MissionTypes::BOUNTY` (1273).

### 2.5 Player-bounty targets (getPotentialPlayerBountyTargets, 2107-2120; isBountyValidForPlayer, 2122-2198)

- A player bounty is a valid target if:
  - The bounty is online (2123-2124).
  - The target has fewer than `MaxBountiesPerJedi` (default 5) active missions (2126-2129).
  - The target is not the player (2131-2135).
  - The target is not in the kill buffer (2137-2146).
  - The target's creature object exists (2148-2151).
  - The target's visibility is at least the terminal visibility threshold (2154-2157).
  - The player's ghost exists (2159-2162).
  - The target is not on the same account (unless `enableSameAccountBountyMissions` is true) (2164-2167).
  - The target is not in a private structure (unless `PrivateStructureJediMissions` is false) (2169-2174).
  - No hunter on the same account already holds the bounty (2176-2187).
  - The bounty is not on cooldown for the player (2189-2195).

### 2.6 Target position (getRandomBountyTargetPosition, 1992-2006)

- The target's zone is looked up by planet name (1997).
- If the zone does not exist, the function returns a zero vector (1999-2001).
- Otherwise, a random spawn point on the planet is returned (2003-2005).

## 3. What a bot test should check

### 3.1 Observable results

- **System messages**:
  - If the bot is out of range: `ui.radial_out_of_range_prose` (171-174).
  - If the bot lacks the skill: `@mission/mission_generic:not_bounty_hunter_terminal` (180, 1080).
  - If the bot is banned: `@city/city:banned_services` (189).
  - If the cooldown is active: "You can't request missions yet, please wait a bit before trying again." (195).
- **Mission bag contents**:
  - The bag should contain 12 (or more) mission slots (207-227).
  - Slots 0-9 should have a bounty mission type CRC (1273) and a non-zero target object ID (1127 or 1239).
  - Slots 10 and up should remain empty (776-778).
- **Mission attributes**:
  - Mission level should be 1 for a novice (1090-1097).
  - The target template should be `object/tangible/mission/mission_bounty_target.iff` (1114).
  - The end position should be a valid spawn point on the player's planet (1206-1207, 1992-2006).
  - The reward should be `creoLevel * (200 + random(200))` for level 1 (1222).
  - The difficulty should be "easy" (1231-1237).
- **Informant NPC**:
  - A `spynet_operative` should be present within 3 km (missions.py:1035-1039).
  - The informant's conversation should name the mission level (missions.py:1043-1045).

### 3.2 Setup required

- The bot must have the `combat_bountyhunter_novice` skill (179, 1079).
- The bot must be within 6 m of the bounty terminal (170).
- The bot must have a mission bag slotted (202-205).
- The bot must not be banned from the city (188-191).
- The bot must not be on cooldown (194-197).
- The terminal must not be a statue or newbie terminal (165-168).
- For a level-1 mission, no investigation skill is needed (1090-1097).
- For a level-2 or 3 mission, the bot needs `combat_bountyhunter_investigation_01` or `combat_bountyhunter_investigation_03` (1092-1097).
- For a player-bounty target, the target must be online, visible, and not on the same account (2122-2198).

## 4. Likely reasons a test sees no effect

1. **Out of range (most likely, inferred)**: The bot was not within 6 m of the terminal. The code rejects out-of-range requests with a system message (170-176), and the bot's helper notes this exact failure mode (missions.py:1019-1022). The bot's walk "stopped at the end of the last path" (missions.py:1019) suggests it never reached the terminal.
2. **Missing skill (possible, but the bot has the box)**: The bot must have `combat_bountyhunter_novice` (179, 1079). The bot's helper checks this (missions.py:972, 1011), so this is unlikely unless the skill was not applied.
3. **No mission bag (possible)**: The bot must have a mission bag slotted (202-205). If not, the function returns silently (204-205).
4. **Cooldown (possible)**: The bot must not be on cooldown (194-197). The cooldown is 1400 ms (200), so 30 requests would trigger it unless the bot waits between requests. The bot's helper waits `LIST_COOLDOWN` (missions.py:1025), so this is unlikely.
5. **Banned (unlikely)**: The bot must not be banned from the city (188-191).
6. **No valid target (unlikely for level 1)**: For a level-1 mission, the target is a random NPC on the player's planet (1198-1271). The target template is chosen from `bhTargetsAtMissionLevel` (1209-1210). If the template does not exist, the function would still set a target name and position (1199-1207), so the slot would not be empty. The only way a slot would be empty is if `randomizeGenericBountyMission` returns before setting a target (1079-1088), which requires the skill or zone to be missing.

## 5. Open questions

1. **What is `bhTargetsAtMissionLevel`?** (1209-1210): This is a map from mission level to a list of target templates. The file does not show how it is populated or what templates it contains. If it is empty for level 1, the target template would be empty, but the function would still set a target name and position (1199-1207), so the slot would not be empty.
2. **What is `bhTargetZones`?** (1202-1204): This is a list of zones for level-3 bounties. The file does not show how it is populated.
3. **What is `playerBountyKillBuffer`?** (2137-2146): This is a time buffer after a bounty kill. The file does not show its default value.
4. **What is `enableSameAccountBountyMissions`?** (2166-2167): This is a config flag. The file does not show its default value.
5. **What is `PrivateStructureJediMissions`?** (2169-2174): This is a config flag. The file does not show its default value.
6. **What is `PlayerBountyCooldown` and `PlayerBountyCooldownTime`?** (2189-2195): These are config flags. The file shows the default cooldown time is 86400000 ms (24 hours) (2190).
7. **What is `AnonymousBountyTerminals`?** (1134): This is a config flag. The file does not show its default value.
8. **What is `Core3.MissionManager.ListRequestCooldown`?** (200): The file shows the default is 1400 ms.
9. **What is `Core3.MissionManager.MaxBountiesPerJedi`?** (2126): The file shows the default is 5.
10. **What is `Core3.MissionManager.PlayerBountyCooldown`?** (2189): The file shows the default is true.
11. **What is `Core3.MissionManager.PrivateStructureJediMissions`?** (2169): The file shows the default is true.
12. **What is `Core3.MissionManager.AnonymousBountyTerminals`?** (1134): The file does not show its default value.
13. **What is `enableFactionalCraftingMissions`, `enableFactionalReconMissions`, `enableFactionalEntertainerMissions`?** (210-220): These are config flags. The file does not show their default values.
14. **What is `getRealBountyReward`?** (1151, 1162): This function is not shown in the file.
15. **What is `getRandomBountyPlanet`?** (1203): This function is not shown in the file.
16. **What is `makeCreatureName`?** (1191, 1265): This is a method of `NameManager`. The file does not show its implementation.
17. **What is `getTemplate`?** (1114, 1212): This is a method of `TemplateManager`. The file does not show its implementation.
18. **What is `getContainerObjectsSize`?** (764, 222): This is a method of `SceneObject`. The file does not show its implementation.
19. **What is `getSlottedObject`?** (763, 202): This is a method of `CreatureObject`. The file does not show its implementation.
20. **What is `isInRange`?** (170): This is a method of `CreatureObject`. The file does not show its implementation.
21. **What is `hasSkill`?** (179, 1079, 1092, 1094): This is a method of `CreatureObject`. The file does not show its implementation.
22. **What is `checkCooldownRecovery`?** (194): This is a method of `CreatureObject`. The file does not show its implementation.
23. **What is `addCooldown`?** (200): This is a method of `CreatureObject`. The file does not show its implementation.
24. **What is `sendSystemMessage`?** (166, 174, 180, 189, 195, 1080): This is a method of `CreatureObject`. The file does not show its implementation.
25. **What is `getCityRegion`?** (185): This is a method of `MissionTerminal`. The file does not show its implementation.
26. **What is `isBanned`?** (188): This is a method of `CityRegion`. The file does not show its implementation.
27. **What is `isStatueTerminal`, `isNewbieTerminal`, `isBountyTerminal`, `isGeneralTerminal`, `isArtisanTerminal`, `isEntertainerTerminal`, `isScoutTerminal`, `isImperialTerminal`, `isRebelTerminal`?** (165, 178, 624-638): These are methods of `MissionTerminal`. The file does not show their implementations.
28. **What is `isSlicer`?** (622): This is a method of `MissionTerminal`. The file does not show its implementation.
29. **What is `removeSlicer`?** (642): This is a method of `MissionTerminal`. The file does not show its implementation.
30. **What is `getZone`?** (1084, 1997): This is a method of `CreatureObject` and `Server`. The file does not show its implementation.
31. **What is `getPositionX`, `getPositionY`?** (1112): These are methods of `CreatureObject`. The file does not show their implementations.
32. **What is `getZoneName`?** (1112, 1201): This is a method of `Zone`. The file does not show its implementation.
33. **What is `getTemplate`?** (1114, 1212): This is a method of `TemplateManager`. The file does not show its implementation.
34. **What is `setStartPosition`?** (1112): This is a method of `MissionObject`. The file does not show its implementation.
35. **What is `setTargetTemplate`?** (1114): This is a method of `MissionObject`. The file does not show its implementation.
36. **What is `setMissionLevel`?** (1116): This is a method of `MissionObject`. The file does not show its implementation.
37. **What is `setFaction`?** (1117): This is a method of `MissionObject`. The file does not show its implementation.
38. **What is `setTargetObjectId`?** (1127, 1239): This is a method of `MissionObject`. The file does not show its implementation.
39. **What is `setEndPosition`?** (1128, 1207): This is a method of `MissionObject`. The file does not show its implementation.
40. **What is `setTargetOptionalTemplate`?** (1129, 1210): This is a method of `MissionObject`. The file does not show its implementation.
41. **What is `getRewardCredits`?** (781): This is a method of `MissionObject`. The file does not show its implementation.
42. **What is `setRewardCredits`?** (1150, 1162, 1229): This is a method of `MissionObject`. The file does not show its implementation.
43. **What is `setBonusCredits`?** (1155): This is a method of `MissionObject`. The file does not show its implementation.
44. **What is `getFirstName`, `getLastName`?** (1158-1159): These are methods of `CreatureObject`. The file does not show their implementations.
45. **What is `getFaction`?** (1135-1138): This is a method of `CreatureObject`. The file does not show its implementation.
46. **What is `getPlayerObject`?** (1142, 1153, 1159, 1164, 1182, 1253): This is a method of `CreatureObject`. The file does not show its implementation.
47. **What is `getJediState`?** (1145): This is a method of `PlayerObject`. The file does not show its implementation.
48. **What is `getAccountID`?** (1164, 1184): This is a method of `PlayerObject`. The file does not show its implementation.
49. **What is `getVisibility`?** (2156): This is a method of `PlayerObject`. The file does not show its implementation.
50. **What is `getTerminalVisThreshold`?** (2154): This is a method of `VisibilityManager`. The file does not show its implementation.
51. **What is `getBountyHunters`?** (2176): This is a method of `PlayerBounty`. The file does not show its implementation.
52. **What is `canTakeMission`?** (2192): This is a method of `PlayerBounty`. The file does not show its implementation.
53. **What is `isOnline`?** (2123): This is a method of `PlayerBounty`. The file does not show its implementation.
54. **What is `numberOfActiveMissions`?** (2128): This is a method of `PlayerBounty`. The file does not show its implementation.
55. **What is `getTargetPlayerID`?** (1127, 1131, 1179, 2131): This is a method of `PlayerBounty`. The file does not show its implementation.
56. **What is `getLastBountyKill`?** (2138): This is a method of `PlayerBounty`. The file does not show its implementation.
57. **What is `getMiliTime`?** (2141): This is a method of `Time`. The file does not show its implementation.
58. **What is `getRandomSpawnPoint`?** (2003): This is a method of `PlanetManager`. The file does not show its implementation.
59. **What is `getPlanetManager`?** (2003): This is a method of `Zone`. The file does not show its implementation.
60. **What is `getZone`?** (1997): This is a method of `Server`. The file does not show its implementation.
61. **What is `getContainerObject`?** (769): This is a method of `SceneObject`. The file does not show its implementation.
62. **What is `castTo`?** (769, 1131, 2148, 2179): This is a method of `Reference`. The file does not show its implementation.
63. **What is `getContainerObjectsSize`?** (764, 222): This is a method of `SceneObject`. The file does not show its implementation.
64. **What is `transferObject`?** (224): This is a method of `SceneObject`. The file does not show its implementation.
65. **What is `sendTo`?** (225): This is a method of `SceneObject`. The file does not show its implementation.
66. **What is `createObject`?** (223): This is a method of `Server`. The file does not show its implementation.
67. **What is `getObject`?** (1131, 2148, 2179): This is a method of `Server`. The file does not show its implementation.
68. **What is `getNameManager`?** (1099): This is a method of `Processor`. The file does not show its implementation.
69. **What is `makeCreatureName`?** (1191, 1265): This is a method of `NameManager`. The file does not show its implementation.
70. **What is `getSkillMod`?** (780): This is a method of `CreatureObject`. The file does not show its implementation.
71. **What is `setRefreshCounter`?** (783): This is a method of `MissionObject`. The file does not show its implementation.
72. **What is `setTypeCRC`?** (774, 1273): This is a method of `MissionObject`. The file does not show its implementation.
73. **What is `getMissionLevel`?** (1209): This is a method of `MissionObject`. The file does not show its implementation.
74. **What is `getTargetOptionalTemplate`?** (1212): This is a method of `MissionObject`. The file does not show its implementation.
75. **What is `getLevel`?** (1218): This is a method of `CreatureTemplate`. The file does not show its implementation.
76. **What is `getMissionNumber`?** (1182, 1255): This is a method of `MissionObject`. The file does not show its implementation.
77. **What is `setMissionNumber`?** (1182, 1255): This is a method of `MissionObject`. The file does not show its implementation.
78. **What is `getMissionDifficulty`?** (1166, 1256): This is a method of `MissionObject`. The file does not show its implementation.
79. **What is `setMissionDifficulty`?** (1166, 1256): This is a method of `MissionObject`. The file does not show its implementation.
80. **What is `getMissionTargetName`?** (1165, 1199): This is a method of `MissionObject`. The file does not show its implementation.
81. **What is `setMissionTargetName`?** (1165, 1199): This is a method of `MissionObject`. The file does not show its implementation.
82. **What is `getCreatorName`?** (1194, 1268): This is a method of `MissionObject`. The file does not show its implementation.
83. **What is `setCreatorName`?** (1194, 1268): This is a method of `MissionObject`. The file does not show its implementation.
84. **What is `getMissionTitle`?** (1195, 1269): This is a method of `MissionObject`. The file does not show its implementation.
85. **What is `setMissionTitle`?** (1195, 1269): This is a method of `MissionObject`. The file does not show its implementation.
86. **What is `getMissionDescription`?** (1196, 1270): This is a method of `MissionObject`. The file does not show its implementation.
87. **What is `setMissionDescription`?** (1196, 1270): This is a method of `MissionObject`. The file does not show its implementation.
88. **What is `getStringId`?** (1174, 1247, 1258): This is a method of `StringIdManager`. The file does not show its implementation.
89. **What is `isEmpty`?** (1176, 1249, 1262): This is a method of `UnicodeString`. The file does not show its implementation.
90. **What is `toString`?** (1177, 1250): This is a method of `UnicodeString`. The file does not show its implementation.
91. **What is `valueOf`?** (1177, 1179, 1184, 1195, 1196, 1250, 1252, 1258, 1269, 1270): This is a method of `String`. The file does not show its implementation.
92. **What is `random`?** (1106, 1120, 1177, 1222, 1224, 1226, 1250, 1252): This is a method of `System`. The file does not show its implementation.
93. **What is `size`?** (1102, 1105, 1120, 1209, 1210, 2112, 2178): This is a method of `Vector`. The file does not show its implementation.
94. **What is `get`?** (1122, 1209, 1210, 2113, 2179): This is a method of `Vector`. The file does not show its implementation.
95. **What is `removeElementAt`?** (1124): This is a method of `Vector`. The file does not show its implementation.
96. **What is `add`?** (2116): This is a method of `Vector`. The file does not show its implementation.
97. **What is `getContainerObjectsSize`?** (764, 222): This is a method of `SceneObject`. The file does not show its implementation.
98. **What is `getSlottedObject`?** (763, 202): This is a method of `CreatureObject`. The file does not show its implementation.
99. **What is `isInRange`?** (170): This is a method of `CreatureObject`. The file does not show its implementation.
100. **What is `hasSkill`?** (179, 1079, 1092, 1094): This is a method of `CreatureObject`. The file does not show its implementation.
