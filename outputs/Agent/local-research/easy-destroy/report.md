# Report: How a group gets an easy, near destroy mission (for the group-pay check)

## 1. Short answer

A destroy mission's difficulty is chosen by first picking a LairSpawn from the planet's spawn list whose difficulty range overlaps the player's level ±5, then randomizing within that lair's min/max range and normalizing to a 1-4 scale (MissionManagerImplementation.cpp.lines-835-1002:856-862; lines-1850-1991:1923-1987). For groups the group level replaces the player level, so adding members raises difficulty. Distance from the terminal is `base + factor × difficulty + random`, capped by 20 retries that reject city positions and water (lines-835-1002:898-933). To get an easy, near lair a group can lower its level, reduce member count, or switch to a different terminal/planet with a lower-level spawn list; the code shows the first two, the third is inferred from how spawn lists are keyed by zone name.

## 2. How it works: conditions, skill mods and numbers, timings, and messages

### Lair selection (getRandomLairSpawn)
- The function picks a mission group string based on faction and planet (lines-1850-1991:1862-1879). For neutral missions it uses `zone->getZoneName() + "_destroy_missions"`.
- It retrieves the spawn list from that group via `CreatureTemplateManager::instance()->getDestroyMissionGroup()` (lines-1850-1991:1882-1888). The list is planet-specific.
- `minLevelCeiling` defaults to 20 but can be overridden by the mission group's own ceiling (lines-1850-1991:1857, 1889). This caps how low the minimum difficulty can go for high-level players.
- Player level is fetched with `calculatePlayerLevel()` (lines-1850-1991:1908). If the player is grouped, the group level replaces it (lines-1850-1991:1910-1918). The code shows this directly; skill mods are not mentioned here.
- `minLevel = Math::min(playerLevel - 5, minLevelCeiling)` (lines-1850-1991:1923). This prevents high-level players from accessing very low-difficulty lairs on a planet.
- The function first tries to pick randomly from lairs where `getMinDifficulty() <= playerLevel + 5 && getMaxDifficulty() >= minLevel` (lines-1850-1991:1926-1945). If none found, it iterates all lairs for the same condition (lines-1850-1991:1947-1967). If still none, it picks the first lair with `getMinDifficulty() <= playerLevel + 5` (lines-1850-1991:1969-1987).
- The selected LairSpawn's min/max difficulty define the range for the mission's base difficulty.

### Difficulty calculation (randomizeGenericDestroyMission)
- `difficultyLevel = System::random(maxDiff - minDiff) + minDiff` picks a value within the lair's range (lines-835-1002:858).
- It is normalized to 1-4 via `(difficultyLevel - minDiff) / ((maxDiff > (minDiff + 5) ? maxDiff - minDiff : 5) / 5)` (lines-835-1002:859). If the result is 5 it is forced to 4 (lines-835-1002:861-862).
- `diffDisplay` starts as `difficultyLevel < 5 ? 4 : difficultyLevel` (lines-835-1002:864), then adds the group level if grouped (lines-835-1002:870-873) or player level if solo (lines-835-1002:875). This is used for display, not further calculation.
- The mission title/description uses `_easy` for difficulty < 2, `_medium` for 2, `_hard` otherwise (lines-835-1002:968-973).

### Distance from terminal
- Base distance formula: `destroyMissionBaseDistance + destroyMissionDifficultyDistanceFactor * difficultyLevel` (lines-835-1002:902). These are server config constants; their values are not in these files.
- Random offset: `+ System::random(destroyMissionRandomDistance) + System::random(destroyMissionDifficultyRandomDistance * difficultyLevel)` (lines-835-1002:903). Again, config constants.
- Position is generated relative to the player's world coordinate at that distance and a random angle 0-360° (lines-835-1002:904).
- The position must pass validation within 20 retries: inside zone boundaries, not underwater (waterHeight <= height), and outside any city region (lines-835-1002:898-933). If all retries fail the function returns without setting a mission.

### Messages the player sees
- The code sets mission title/description keys like `mission/mission_destroy_neutral_easy_npc` but does not send messages directly in these files. The actual system message to the player is likely sent by the terminal or mission offer logic elsewhere (not shown).

## 3. What a bot test should check

### Setup needed first
- Ensure the group is at a known level (use master combat boxes as the test kit does, but verify the effective group level via `getGroupLevel`).
- Confirm the terminal's planet zone name matches an expected destroy mission spawn list (e.g., `tatooine_destroy_missions`).

### Observable results to check
1. **Mission difficulty**: After accepting a destroy mission, read `mission->getMissionDifficulty()` and verify it is ≤ 10. The displayed difficulty should reflect the group level addition (lines-835-1002:870-876).
2. **Mission distance**: Read `mission->getStartPosition()` and compare to the terminal's position. Distance should be within the expected range for the difficulty (inferred from lines-835-1002:902-903).
3. **Lair template**: Verify `mission->getTargetOptionalTemplate()` matches a lair whose min/max difficulty overlaps the group level ±5 (lines-1850-1991:1929).
4. **System messages**: Check that the terminal offers the mission with `_easy`/`_medium`/`_hard` in its title/description keys (lines-835-1002:968-973, 980-981).

### Test variations
- Run the same group at different levels and confirm difficulty changes.
- Add/remove group members and verify the group level affects both difficulty and distance.
- Try multiple terminals on the same planet to see if spawn list differences matter (inferred).

## 4. Likely reasons a test sees no effect

1. **No qualifying lairs in the spawn list**: If all lairs in `tatooine_destroy_missions` have minDifficulty > groupLevel + 5, the fallback at lines-1850-1991:1969-1987 picks the lowest available, which may still be too hard. The test kit's level 1-25 bots with master combat boxes may result in a group level that exceeds what the planet's spawn list supports.
2. **minLevelCeiling capping**: If the mission group has `minLevelCeiling` < 20 (lines-1850-1991:1889), high-level groups cannot access low-difficulty lairs because `minLevel = Math::min(playerLevel - 5, minLevelCeiling)` pushes the floor up.
3. **Position validation failures**: All 20 retries may fail if the planet has limited valid terrain (lines-835-1002:898-933). The function silently returns without offering a mission.
4. **Spawn list empty or null**: If `getDestroyMissionGroup()` returns nullptr or an empty list (lines-1850-1991:1884-1886, 1902-1904), no lair is selected and the mission offer fails.
5. **Faction filtering**: If bots have a faction status that routes to `factional_imperial_destroy_missions` or `factional_rebel_destroy_missions` (lines-1850-1991:1875-1878), those lists may not contain easy lairs.

## 5. Open questions

- **Config constant values**: The base distance, difficulty factors, and random ranges (`destroyMissionBaseDistance`, `destroyMissionDifficultyDistanceFactor`, `destroyMissionRandomDistance`, `destroyMissionDifficultyRandomDistance`, `destroyMissionBaseReward`, etc.) are not defined in these files; they are likely in a config header or ini file.
- **Group level calculation**: The code calls `group->getGroupLevel(includeFactionPets)` (lines-1850-1991:1916, lines-835-1002:872) but does not show how group level is computed from member levels or skill mods. That logic is in GroupObject, which is not included here.
- **LairSpawn difficulty vs. player level**: The files show that LairSpawn has `getMinDifficulty()` and `getMaxDifficulty()`, but the mapping between those values and actual creature levels or lair condition is not visible. The LairTemplate file would be needed.
- **Mission offer trigger**: These files handle mission generation after a terminal request, but not how/when the terminal decides to offer a destroy mission versus other types. That logic is in the terminal class (not shown).
- **Faction pet inclusion**: `includeFactionPetsForMissionDifficulty()` is called from ConfigManager (lines-1850-1991:1867, 1911), but its default and behavior are not defined here.

## Claude's review (18 Oct 2:18 AM)

Checked against the copies in `src/` and, for what the client is sent, Core3-dev's mission object.

**Right:**
- the lair choice from `<planet>_destroy_missions` within the group or player level ±5, with its two fallbacks (1859-1987);
- the group level replacing the player's (1910-1918);
- the distance formula and its 20 placement tries that avoid water and cities (898-933);
- easy/medium/hard by `difficulty` < 2, == 2, else (968-973).

**Wrong:**
1. **The number a bot sees includes the group's own level, and this decides the group-pay check.**
   - `setMissionDifficulty(difficultyLevel, diffDisplay, difficulty)` (955) sends the client `difficultyDisplay` (MissionObjectImplementation.cpp:133-146; MissionObjectMessage3.h:40).
   - `diffDisplay` is the lair's level (at least 4) **plus the group's level**, or the player's level when solo (864-876). It is not "for display only".
   - So the scenario's "difficulty 10 or less" can only match a group of level 6 or under. With master combat boxes from the test kit it never matches. That is why none of the 6 offers fitted.
   - The test should compare the shown difficulty with the group's level plus a margin, or read the lair's own level as shown minus group level.
2. **`difficulty` runs 0-4, not 1-4.** It is 0 when the random level equals the lair's minimum (859-862).
3. **The level ceiling works the other way round.**
   - `minLevel = min(level - 5, minLevelCeiling)` caps the *floor* (1922-1923).
   - A lower ceiling lets a high-level group still get lairs at or above it. It does not push the floor up.

**Not shown:** how `getGroupLevel` adds up the members (GroupObject is not in the sources), and the distance and reward constants.
