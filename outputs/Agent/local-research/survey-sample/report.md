Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(Finished by Claude Opus 5.5 after the run was interrupted. Server HEAD checked: 90044b8e.)

Path keys (relative to MMOCoreORB/): SS = src/server/zone/objects/player/sessions/survey/SurveySessionImplementation.cpp; RSp = src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp; ST = src/server/zone/objects/tangible/tool/SurveyToolImplementation.cpp; RT = src/server/zone/managers/resource/resourcespawner/resourcetree/ResourceTree.cpp; RSI = src/server/zone/objects/resource/ResourceSpawnImplementation.cpp; RSC / RCS = src/server/zone/objects/creature/commands/RequestSurveyCommand.h / RequestCoreSampleCommand.h; RML = bin/scripts/managers/resource_manager.lua; TL = bin/scripts/object/tangible/survey_tool/.

## 1. Short answer
When you use a survey tool, it sends a list of the spawns on the current planet that are in shift and whose survey tool type matches the tool's type. A survey reads density at a grid of points around the player. A core sample reads the density where the player stands, gives a result after 3 s and repeats every 25 s. **The organic tool can never list anything.** Its template sets `toolType = 0`, and no resource class is ever given type 0. The gas, moisture (water) and wind tool types are correct (4, 7 and 8), matching the resource tree. So an empty list for them means one of two things: the bot's planet has no in-shift spawn of that class, or the list message never arrived (the range pop-up path). "[null, 0]" means every survey returned 0% or no result at all. Running out of mind, or a sample loop that is still running, both cause that.

## 2. How it works
**Tools and range**
- Tool types are SOLAR 1, CHEMICAL 2, FLORA 3, GAS 4, GEOTHERMAL 5, MINERAL 6, WATER 7, WIND 8, FUSION 9 and INORGANIC 10 (src/server/zone/objects/tangible/tool/SurveyTool.idl:26-35).
- Templates: mineral 6, liquid 2 (surveyType "chemical"), moisture 7 ("water"), gas 4, wind 8, solar 1, lumber 3 ("flora_resources") (TL survey_tool_*.lua:73-76). Inorganic is 10 and organic is 0 (TL survey_tool_inorganic.lua:46, survey_tool_organic.lua:46).
- Resource classes get these types: energy containing "geothermal" 5, "solar" 1, "unlimited_wind" 8, any other energy -1; chemical 2; flora_resources 3; gas 4; mineral 6; water 7; everything else -1 (RT:169-201).
- Using the tool (radial 20) needs the "survey" ability, otherwise the player gets @error_message:insufficient_skill (ST:45-47). If the range is 0 or above 384, the tool opens the range list instead of sending resources (ST:51-56).
- Range options by "surveying" mod: 20 gives 64m x3, 35 gives 128m x4, 55 gives 192m x4, 75 gives 256m x5, 100 gives 320m x5, 120 gives 384m x5 (ST:97-113). The range is capped to the skill (ST:121-130). Grid points are 3, 4 or 5 (ST:150-161). Range is a member of each tool (SurveyTool.idl:15), so each new tool asks once (inferred).
- The list holds only spawns in the planet's zone map that are in shift, meaning their despawn time is in the future (RSI:24-26). The spawn type must equal the tool type; type 10 takes any "inorganic" (RSp:876-885). With no zone map the player sees "The tool fails to locate any resources" (RSp:867-869).

**Survey**
- Refused inside a structure (survey_in_structure), while swimming (survey_swimming), when not upright (survey_standing) and when mounted in water (survey_cant) (SS:83-103). Refused with survey_mind if mind is below 100 - focus/15 (SS:106-112). A spawn of another tool type gives survey:wrong_tool (SS:119-124).
- Ignored silently while a survey is pending. Refused with survey:survey_sample while a sample loop is live (RSC:40-51).
- Costs 100 - focus/15 mind (RSp:906-908). The grid is points x points, spaced range/(points-1) and centred on the player (RSp:934-960). The player sees survey:start_survey %TO (RSp:985-987), and the results are sent 3 s later (SS:367-368, SurveyTask.h:37). If the best density is at least 0.1, the player gets a blue "Resource Survey" waypoint and @survey:survey_waypoint (RSp:964-982, SurveyTask.h:39-43).
- Density is 0 where the spawn has no map for the planet or is out of shift (RSI:191-200). Peak density is high for chemical, gas_inert and JTL, low for ore, water, solar and wind, and medium for everything else (RSI:144-158).

**Sampling**
- Refused in combat (sample_cancel_attack), inside a structure and while swimming. The player is forced off a mount (SS:168-192). If action is below 124 - quickness/12.5, the player gets sample_mind and stands up (SS:195-201). Radioactive spawns ask for confirmation first (SS:210-216). The player kneels (SS:219-221) and sees survey:start_sampling %TO (SS:227-229).
- One time in 51 (`random(50)==7`), a node pop-up appears instead of a sample (SS:231-244). In the cnode pop-up, option 1 sets a waypoint and stands the player up (SS:292-318). In the gnode pop-up, option 1 costs 300 action for a 50% chance of 5x units (SS:347-356, RSp:1101-1110).
- Each sample costs the action and reads the density at the player (RSp:1011-1027). The result comes 3 s later (SS:392-394), and the next sample 25 s later (SS:381-382) through SampleTask and reSample (SampleTask.h:34-40, SurveySession.idl:59-61). Asking for another sample early gives survey:tool_recharge_time %DI (RCS:39-56). Asking while a survey is pending gives sample_survey (RCS:60-64).
- Results (RSp:1060-1139):
  - Density below 0.10 gives efficiency_too_low and the player stands.
  - Density x100 below 32 - (skill/20)x6 gives density_below_threshold and the player stands.
  - skill x density + random(100) + private_spec_samplerate below 40 gives sample_failed.
  - Units = density x (25+random(3)) x skill/100 x samplingMultiplier x (1 + private_spec_samplesize/100). Below 2 units gives trace_amount.
  - Otherwise the player sees survey:sample_located %TO %DI, and the units go into the inventory, merging into a matching stack (RSp:1171-1176). XP is resource_harvesting_inorganic, up to 40, or 50 with a gamble or node (RSp:1099-1153).
  - Radioactive samples add wounds (RSp:1160-1167).

**Spawns**
- The random pool holds 27 spawns. Gas has weight 16 and water weight 2, among others (RML:154-156). Native spawns, one per planet, include water_vapor, solar and wind (RML:165). A galaxy-wide spawn goes to a random subset of planets (RSI:160-189), scaled by poolScaleZones (RML:66, RSp:107-116). Inorganic spawns stay in shift 6-11 days and organic spawns 6-22 days (RSp:723-736, RML:74).

## 3. What a bot test should check
**Setup:**
- The bot has a surveying mod of 20 or more and the survey ability.
- It is outdoors, upright and not mounted.
- Mind and action are above the costs.
- The range has been set once for each tool.
- Before calling an empty list a bug, get evidence that the planet has an in-shift spawn of the tool's class, for example from the server's resource dump (RSp:472).

besh-harvest.py covers corpse harvesting only, not surveying.

**Checks:**
1. The list message arrives, and every entry's class fits the tool. Report "no message" separately from "empty list".
2. After requestSurvey:
   - start_survey arrives with the name.
   - Results arrive within about 4 s, with points² values (9, 16 or 25).
   - Mind drops by about 100 - focus/15.
   - The waypoint and survey_waypoint appear only when the best point is 10% or more.
3. requestCoreSample at a spot of 10% or more:
   - start_sampling arrives, the bot is crouched and action drops by about 124 - quickness/12.5.
   - About 3 s later, exactly one of these arrives: sample_located (%DI equals the units gained in inventory), trace_amount, sample_failed, efficiency_too_low or density_below_threshold.
   - Another result follows about 25 s later.
   - Asking again early gives tool_recharge_time.
4. Standing up ends the loop, so no result arrives 25 s later (inferred).
5. Handle the node pop-up, which appears one time in 51.

## 4. Likely reasons a test sees no effect
- **Organic:** `toolType = 0` (TL survey_tool_organic.lua:46) matches no class (RT:169-201, RSp:882), so its list is always []. This is a template bug. Flora needs survey_tool_lumber instead.
- **Gas, moisture, wind:** their types match the tree (TL :73 against RT:179, 190, 197). An empty list then means no in-shift spawn of that class is mapped to the bot's planet (inferred). Gas comes only from the random pool, water mostly from native water_vapor, and wind from natives. Another possibility is that the merged resource_tree.iff does not put those natives under "water" or "unlimited_wind" (RT:32, RML:47-50) (inferred).
- **Range pop-up:** besh-gather.py:86-92 answers the last dataList page after 4 s. A wrong or stale page leaves the range at 0, so no list is sent. The scenario also reports that as [] (inferred).
- **[null, 0]:** possible causes (inferred):
  - Five surveys per tool across several tools with no mind check (besh-gather.py:97-102) lead to survey_mind.
  - A sample loop left over from the previous tool gives survey_sample (RSC:43-51).
  - Every point reads 0, for example low-density water or wind at 64 m (RSI:153).
  - Only positive percents count (besh-gather.py:99-101).
- **Labels:** besh-gather.py:145 "liquid" is the chemical tool (TL survey_tool_liquid.lua:73-76), not water.
- The 'sample' text wait (besh-gather.py:107) also matches start_sampling, so it proves nothing (inferred). Receipt rests on the units check (besh-gather.py:15-33).

## 5. Open questions
- Which classes Tatooine has in shift right now (database and merged resource_tree.iff, not source).
- Whether the water_vapor and wind natives carry the "water" or "energy" + "unlimited_wind" classes in the merged tree.
- getRichSampleLocation returns a member (SurveySession.idl:98-101). If it is never null, the sample_failed branch (RSp:1086) never runs (inferred).
- Where samplingMultiplier is set, and its value.
- The POSTURECHANGED handler registered at src/server/zone/managers/resource/ResourceManagerImplementation.cpp:242 was not read, so exactly how standing cancels sampling is unknown.
- Whether random(3) gives 0-3 or 0-2, and the shape of SpawnDensityMap (not read).
- What the bot harness's "survey_resources" and "survey_results" events carry (not read).
