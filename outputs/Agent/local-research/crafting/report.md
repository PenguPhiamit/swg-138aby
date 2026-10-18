Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(Run was interrupted and finished by Claude Opus 5.5. HEAD confirmed as 90044b8e. Paths are relative to MMOCoreORB/src/server/zone/. Abbreviations: CSI = objects/player/sessions/crafting/CraftingSessionImplementation.cpp, CMI = managers/crafting/CraftingManagerImplementation.cpp, SL = managers/crafting/labratories/SharedLabratory.cpp, RL = .../ResourceLabratory.cpp, COT = objects/player/sessions/crafting/events/CreateObjectTask.h, RCS = objects/creature/commands/RequestCraftingSessionCommand.h.)

## 1. Short answer
A session starts when the player uses a tool in their inventory, or a station within 7 m (RCS:77-88). The server then walks a state machine: 1 schematic list, 2 slots, 3 experimentation, 4/5/6 naming and finishing (CSI:177, 369, 848-853, 1335, 1355). Assembly rolls one of 8 outcomes from the assembly skill mod, the tool's effectiveness and luck. The resources' quantity-weighted stats set each attribute's starting % and its cap. Experimentation is only offered at a station. It spends int(experimentation skill mod / 10) points and moves each row by a fixed % per point, set by the roll's outcome. The item appears in the inventory after complexity x 2 seconds, with a system message. A practice run gives 5% more XP and no item.

## 2. How it works
**Start.** The tool must not be "finished" (@system_msg:crafting_tool_full) or busy (@system_msg:crafting_tool_creating_prototype) (RCS:97-107). Using a tool also finds a nearby station of the tool's type (RCS:115). The schematic list is filtered by the tool's tabs and complexity. A station's complexity replaces the tool's (CSI:130-138). Experimentation is enabled only when there is a station (CSI:142). Moving more than 7 m from the station closes the session with "@ui:sui_out_of_range_prose" (CSI:96-107).

**Choosing a schematic** creates the manufacture schematic and a transient prototype inside the tool, then sets state 2 (CSI:363-391, 409-491).

**Filling slots.** An ingredient must be under the crafter, or in the station, and its container must allow move-out (CSI:597-609). Each add sends back a slot result code (CSI:619-621, 324-336). The next stage needs every slot ready; otherwise PARTIALASSEMBLE is sent (CSI:708-711).

**Assembly** (CSI:744-990; SL:143-208):
- assemblyRoll = toolMod x (luckRoll + assemblySkill/10 x 5).
- toolMod = 1 + effectiveness/100 (a comment says 0.85-1.15).
- luckRoll = random(100) + private_spec_assembly. A luckRoll above 95 - craft_bonus is an Amazing Success at once.
- A random "luck" bonus is added. force_assembly also counts.
- Thresholds: >70 Great, >60 Good, >50 Moderate, >40 Success, >30 Marginal, >20 OK, else Barely (SL:189-207).
- Result codes are 0 Amazing to 8 Critical failure (managers/crafting/CraftingManager.idl:37-45).
- The Critical-failure return is commented out (SL:182-183). So the resource lab never returns it, and the "lose resources, back to stage 2" branch (CSI:960-978) cannot be reached for this lab (inferred).
- A tool counter, forceCriticalAssembly, forces Amazing (CSI:777-780).
- A non-critical assembly uses one charge of a limited-use schematic (CSI:979-981).
- Assembly also sets the crafter's name and a serial: 8 random lowercase letters or digits in parentheses (CSI:867-873; CMI:134-156). It adds the schematic's skill mods (wearable mods capped at 25) and weapon DoTs (CSI:1512-1577).

**Starting values** (RL:39-118; SL:59-141):
- For each resource weight: W = sum of (weighted stat x percentage).
- A weighted stat is the quantity-weighted average of that stat across the resource slots and custom-ingredient components. Stats of 0 are skipped.
- Cap = W/1000. Start = W x (0.000015W + 0.015) x 0.01 x the assembly modifier.
- Assembly modifier: Amazing 1.05; otherwise 1.1 - 0.1 x code. That is 1.0 Great, 0.9 Good ... 0.4 Barely.
- Worked example (inferred arithmetic): W=1000 gives a 100% cap and a 30% start before the modifier. W=500 gives a 50% cap and 11.25%.
- If W is 0, no percentage is set (RL:89-90). Component stats are then applied (RL:103-108).

**Experimentation** (CSI:1017-1214; CMI:43-132; SL:21-58; RL:120-158):
- Points = int(skillMod(experimentation skill)/10) (CSI:764).
- Failure = int(50 + (MA-500)/40 + expPoints - 5 x points), where MA is the weighted malleability (CMI:53).
- That failure value is passed in as the "effectiveness" of the experiment roll, so toolMod = 1 + failure/100 (CSI:1102-1106; CMI:83).
- expRoll = toolMod x (luckRoll + (skill + force_experimentation)/10 x 4). Same thresholds as assembly (CMI:111-131).
- Amazing if luckRoll > 95 - experiment_bonus - force_experimentation (CMI:97-100).
- Change per point: Amazing +8%, Great +7%, Good +5.5%, Moderate +1.5%, Success +1%, Marginal 0, OK -4%, Barely -7%, Critical -8%.
- The new value is clamped to between 0 and the cap (RL:138-152).
- Each row raises complexity by one (CSI:1129-1130). The client is shown the worst result of the rows tried (CSI:1124-1127, 1152).
- Too many points stops the loop (CSI:1083-1087). An invalid row count cancels the session (CSI:1060-1065).
- A tool counter, forceCriticalExperiment, forces Amazing (CSI:1108-1114).

**Naming.** "\#" colour codes are stripped, and an empty name falls back to the default name (CSI:1271-1286). The factory-run count is clamped: values below 0 or above 1000 become 1000 (CSI:1288-1292). Customization is offered only if the customization skill mod is above 0 (CSI:771-772, 927-928). This sets state 5 (CSI:1335).

**Create prototype** (CSI:1377-1455; COT:42-91):
- The schematic must be assembled and not yet completed.
- XP is the draft's xpAmount of its xpType. Practice gives round(xp x 1.05) and no item.
- Timer: complexity x 2 seconds, replaced by the config value Core3.Sandbox.CraftSeconds when it is above 0. The tool counts down in 5 s steps.
- When the timer ends, the item is persisted and moved to the inventory, with "@system_msg:prototype_transferred" and a PROTOTYPECREATED observer event.
- If the inventory is full or the tool is not on the crafter, the message is "@system_msg:prototype_not_transferred" and the tool is set to "finished".

**Factory schematic.** The schematic must allow factory runs. The manufacture schematic moves to the datapad, carrying the prototype (CSI:1457-1510).

**What the player sees.** No SUI windows were found in the session code. The client's crafting UI is driven by delta messages and object-controller messages:
- crafting state in PlayerObject delta 9;
- assembly result 0x109 (CSI:947-954);
- experiment result 0x105 (CSI:1190-1196);
- slot results 0x107.
System messages appear only on errors and on completion. With the player's debug flag on, the server sends craftingValues->toString() after assembly and after each experiment (CSI:983-985, 1207-1209).

## 3. What a bot test should check
**Setup**
- Skills that grant the schematic group, plus the assembly and experimentation skill mods.
- A tool of the matching type, in the inventory and neither busy nor finished.
- For experimentation, a station of the same type within 7 m.
- Resources with known stats in the inventory, of known spawns, enough to fill every slot.
- Free inventory space.
- Optional: set Core3.Sandbox.CraftSeconds to shorten the wait.
- Optional: use forceCriticalAssembly / forceCriticalExperiment on the tool for repeatable rolls.

**Observe**
- The assembly result code (0x109). For Amazing, expect start = W x (0.000015W + 0.015) x 0.01 x 1.05.
- The experiment result (0x105) and the remaining points.
- "@system_msg:prototype_transferred".
- An inventory item carrying the crafter's name, a "(xxxxxxxx)" serial and a custom name.
- Attribute values inside min/max, with % never above W/1000.
- XP gained equal to xpAmount, or x1.05 for practice.
- For a factory schematic: a new datapad object.
- Over many runs, assembly outcomes should follow the thresholds; assert distributions, not single rolls.

## 4. Likely reasons a test sees no effect
- No station within 7 m: no experimentation, and the session goes straight to state 4 (CSI:848-853).
- The schematic is missing from the list: wrong tool tab or too complex for the tool (CSI:138).
- The ingredient is not on the crafter, or its container blocks move-out, giving an INVALIDINGREDIENT slot code (CSI:597-609).
- A stat is 0 in every resource, so that attribute gets no percentage (RL:89-90). Experimentation then stops at the cap W/1000, which is low for poor resources.
- The test read the inventory before complexity x 2 s had passed. Or the inventory was full: the item stays in the tool and the tool reports "full".
- Practice mode: no item is made.
- Random rolls: a single run proves little without the force counters.
- The tool was busy or finished from an earlier run.

## 5. Open questions
- How CraftingValues::recalculateValues turns a % into the final number. min + (max-min) x % is inferred; that code was not read.
- Formulas in GeneticLabratory and DroidLabratory, and the rest of applyComponentStats (RL:260 onward), were not read.
- How forceCriticalAssembly/Experiment and the player debug flag are set (which command or admin tool) was not checked.
- How CraftingExperimentCallback and CraftingCustomizationCallback parse client input was not read.
- Whether random(100) includes 100. Which skills give "luck".
- The tool and station complexity values (they come from templates).
- RCS:128-129: initializeSession returns 1 even when validation fails. The failure message uses "@ui_craft@err_no_crafting_tool" (an '@' where ':' is expected), so a failed start may show raw text or no error (inferred).
- Factory production runs (manufacturing) were not covered.


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** station-enabled experimentation and 7 m validation, skill/10 point budget, weighted nonzero-resource averages, assembly curve and cap, experiment steps/clamping, practice +5% base XP and no retained item, prototype receipt and factory-schematic path hold (CraftingSessionImplementation.cpp:90-177,757-785,1377-1453; SharedLabratory.cpp:21-207; ResourceLabratory.cpp:39-158; CreateObjectTask.h:42-90). The cited resource-lab critical return is commented out.

**Corrections/qualifications:**
- Assembly has eight reachable tiers 0-7, while enum 0-8 has nine values including critical (CraftingManager.idl:37-45). Do not conflate these counts.
- Food affects BOTH the early amazing threshold and toolModifier multiplicatively (SharedLabratory.cpp:164-180; CraftingManagerImplementation.cpp:85-103); low luck can also subtract random(100), mitigated by skill/city/force_failure_reduction. The draft's short roll equations omit these branches.
- Practice XP is awarded when createPrototype schedules work (CraftingSessionImplementation.cpp:1396-1409), before timer completion. An XP delta alone does not prove receipt. awardExperience applies downstream modifiers; xpAmount/1.05 is the base request, not guaranteed final XP.
- The prototype timer override is an unconditional positive config lookup at CraftingSessionImplementation.cpp:1422-1424; the name Sandbox does not itself enforce a _test/allowlist gate. No config was changed here.
- Current CreateObjectTask.h:50-65 cleans persistent practice descendants and emits PROTOTYPECREATED with arg 1 for practice; the event alone is not proof of an inventory item (real transfer uses arg 0 at 79-82).
- Serial generation uses random(34), digits 0-8 and letters a-z (CraftingManagerImplementation.cpp:142-150), not every decimal digit.
- The short answer can sound like all available experiment points are spent per click; they form a budget, and pointsAttempted is per requested row (CraftingSessionImplementation.cpp:1100-1121).

**Not established:** genetic/droid lab formulas, rendered precision, tool template values and actual client flow remain outside this resource-lab review.

**Verdict:** Resource-lab formulas largely supported; qualify food/low-luck branches, base XP timing, practice observer and ungated timer override; runtime untested.
