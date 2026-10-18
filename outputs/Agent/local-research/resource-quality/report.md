Written by Claude Opus (run started on Claude Haiku), 15 Oct 2026, from Core3-dev 90044b8e.

# Resource quality and crafting results (resource lab, pre-CU)

## 1. Short answer

Each experimental line on an item (for example min damage) has a list of resource attributes with integer weights, written in the item's target object template. At assembly the server averages each attribute over the schematic's resource slots, weighting each slot by its quantity, then combines them by weight into one "weighted sum" between 0 and 1000. The weighted sum alone sets the line's ceiling (sum / 1000 of the way from min to max). The starting point is a curve of the same sum, multiplied by a random assembly-roll factor (0.4 to 1.05). Each experimentation point then moves the line by a fixed step that depends on the roll (+8% for amazing down to -7% for barely), and the line is capped at the ceiling. One slot holds only one resource spawn, so mixing only happens across slots.

## 2. How it works (paths relative to MMOCoreORB/)

**Where the weights come from.** The draft schematic Lua lists only the slots and points to a target template (`bin/scripts/object/draft_schematic/weapon/pistol_blaster_dl44.lua:66-75`). The weights are in the target object template, in `numberExperimentalProperties`, `experimentalProperties`, `experimentalWeights`, group and subgroup titles, min, max, precision and combine type (`bin/scripts/object/weapon/ranged/pistol/pistol_dl44.lua:125-133`). `SharedTangibleObjectTemplate.cpp:441-457` turns them into one ResourceWeight per line. `ResourceWeight.h:46-71` keeps each weight modulo 16 (weight 0 for "XX") and turns them into fractions, weight / sum of weights. The attribute codes are CR=1, CD=2, DR=3, HR=4, FL=5, MA=6, PE=7, OQ=8, SR=9, UT=10 (`src/server/zone/managers/crafting/CraftingManager.idl:26-35`). There is no ER code.

**Averaging across slots.** `SharedLabratory::getWeightedValue` (`src/server/zone/managers/crafting/labratories/SharedLabratory.cpp:73-142`) works like this for one attribute:
- It sums stat × slot quantity over the resource slots and divides by the total quantity (lines 128-139).
- Slots whose resource has that stat at 0 are left out of both the sum and the divisor (131-135).
- Component slots count only if the component is a CustomIngredient (85-110).
- `ResourceSlot.h:56-57` refuses a second, different spawn in a slot that already has one, so you cannot mix two resources inside one slot.

**Start value and ceiling** (`ResourceLabratory.cpp:59-101`):
- weightedSum = Σ getWeightedValue(type) × fraction (lines 77-87). Lines with weightedSum ≤ 0 are skipped (90).
- maxPercentage = weightedSum / 1000 (line 93).
- currentPercentage = assemblyPct(weightedSum) × assemblyModifier (96), where assemblyPct(v) = v × (0.000015v + 0.015) / 100 (`SharedLabratory.cpp:68-72`). That gives 0.1125 at 500 and 0.30 at 1000.
- assemblyModifier = 1.05 for amazing, otherwise 1.1 − 0.1 × result code (`SharedLabratory.cpp:59-66`). The codes are 0 amazing, 1 great, 2 good, 3 moderate, 4 success, 5 marginal, 6 ok, 7 barely, 8 critical (`CraftingManager.idl:37-45`). So great gives 1.0 and barely gives 0.4.
- The value is min + pct × (max − min). If max < min (lower is better, for example attack speed), it is max + (1 − pct) × (min − max) (`craftingvalues/CraftingValues.cpp:91-95`).
- Components then add their own stats × slot contribution, according to the line's combine type (`ResourceLabratory.cpp:252-333`).

**Assembly roll** (`SharedLabratory.cpp:143-208`):
- The roll is toolMod × (random(100) + city bonus + luck + assembly skill / 2) (lines 174-187). A roll above 95 is amazing (176).
- Thresholds: >70 great, >60 good, >50 moderate, >40 success, >30 marginal, >20 ok, otherwise barely (189-207).
- toolMod = 1 + tool effectiveness / 100 (161), raised further by the food craft buff (164-171).
- The CRITICALFAILURE return is commented out (182-183).

**Experimentation** (`CraftingManagerImplementation.cpp:43-132`; `CraftingSessionImplementation.cpp:1102-1106`):
- Each line attempted gets failure = 50 + (weighted MA − 500) / 40 + expSkill/10 − 5 × points (`CraftingManagerImplementation.cpp:53`).
- That number is passed in as the "effectiveness", so toolMod = 1 + failure / 100 (83). Malleability therefore helps every experiment roll (inferred from the call chain).
- roll = toolMod × (luck + expSkill / 10 × 4) (111). Amazing needs luck above 95 − food bonus − force skill (99). The other thresholds are the same as for assembly (113-131).
- Step per point: amazing +0.08, great +0.07, good +0.055, moderate +0.015, success +0.01, marginal 0, ok −0.04, barely −0.07, critical −0.08 (`SharedLabratory.cpp:21-58`).
- The step applies to every attribute in the experimented group, each clamped to between 0 and its own maxPercentage (`ResourceLabratory.cpp:127-152`).
- A critical failure only happens when more points are spent than the player has, and that also cancels the session (`CraftingSessionImplementation.cpp:1115-1121`).

**Worked example: DL44 pistol.**
- Slots: frame 20 metal, receiver 8 metal, grip 4 metal, then a power handler, barrel and scope as components (`pistol_blaster_dl44.lua:67-70`).
- The mindamage line is weighted CD 1, OQ 1, so 50/50. Its range is 14 to 26, precision 0 (`pistol_dl44.lua:126-132`).
- Assume a great assembly roll (×1.0) and component stats left aside:

| Metal in all 3 slots | weightedSum | start % | start min dmg | ceiling |
|---|---|---|---|---|
| CD 500, OQ 500 | 500 | 11.25% | 15.35 | 20 |
| CD 500, OQ 1000 | 750 | 19.69% | 16.36 | 23 |
| /resource perfect (all 1000) | 1000 | 30% | 17.6 | 26 |

- Mixing across slots: frame OQ 1000 with receiver and grip OQ 500 (all CD 500). OQ averages to (1000×20 + 500×8 + 500×4) / 32 = 812.5, so weightedSum = 656.25 and the ceiling is 21.9.
- One great experiment point adds +0.07 × 12 = +0.84 damage, until the line reaches its ceiling.
- Rounding to precision 0 for display was not verified.

## 3. What a bot test should check

**Setup.**
- Fix the crafter's `weapon_assembly`, `weapon_experimentation` and `luck`. Remove food buffs and city bonuses, and use a tool whose effectiveness is known.
- Get resources with known stats:
  - `/resource perfect <type>` creates a spawn with every applicable stat at 1000 (`src/server/zone/objects/creature/commands/ResourceCommand.h:56-60,77`).
  - `/resource create <name> [quantity]` gives an existing spawn, and `/resource info <name>` reads its stats (lines 50-51, 61-62, 76).
- Use the same spawn in every resource slot for the basic case, and a different spawn per slot for the averaging case.

**Observations that do not depend on the random roll.**
- (a) After many experiment points on a group, no line goes past min + (max − min) × weightedSum / 1000.
- (b) With perfect resources, the ceiling equals the template max.
- (c) The starting value lies between assemblyPct × 0.4 and assemblyPct × 1.05 of the range. Compare the reported assembly result against its exact value.
- (d) A second, different resource cannot be added to a filled slot.

**Observations that depend on the roll.** The experiment result message and the change in value, which should equal step × points × range. The result tier itself is random, so assert on the formula for the tier that was reported, not on a fixed tier.

## 4. Likely reasons a test sees unexpected values

- The assembly modifier is random. City bonus, luck, force skills, food buffs and tool effectiveness all shift the rolls.
- Malleability changes the experiment roll through the failure-rate shortcut.
- A resource that lacks a weighted stat is left out of that stat's average instead of counting as 0. If no slot has the stat, it adds 0 to the sum.
- Components add their stats on top of the resource-based value (`ResourceLabratory.cpp:269`).
- Lines that share a group move together.
- Lines where max < min run in reverse (DL44 attack speed 4.4 → 3.1).
- ok, barely and critical results lower the line, and it can fall back to 0%.
- `/resource perfect` sets only the stats that apply to its type, as its help text says. A weighted stat the type lacks therefore drops out of the average.

## 5. Open questions

- ER is not in the attribute codes and is not set by `/resource perfect`. How (or whether) entangle resistance takes part was not found.
- How the draft schematic gets the target template's resource weights (by `targetTemplate`, inferred).
- How total experimentation points are calculated.
- Whether `setCurrentPercentage` clamps the starting percentage to the ceiling.
- Which AttributesMap constant each combine-type number (0, 1) stands for.
- Rounding or precision in the values shown to the player.
- Whether a bot can create resources with chosen values other than 1000.
- Stimpack (genetic or other labs) and factory runs were not checked.


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** nonzero quantity-weighted per-stat averages, CustomIngredient participation, single spawn per resource slot, weightedSum/1000 ceiling, curved initial percentage, 0.4-1.05 reachable assembly factors and row experiment steps hold (SharedLabratory.cpp:21-141; ResourceLabratory.cpp:59-101,127-152; ResourceSlot.h:43-61; CraftingValues.cpp:86-98). The report's 500/750/1000 arithmetic and 656.25 mixed-slot example are consistent with those formulas before components/display rounding.

**Corrections:**
- 'A roll above 95 is amazing' wrongly suggests the final tool/skill-modified assemblyRoll. The early test is luckRoll=random(100)+cityBonus >95-craftbonus, BEFORE low-roll adjustment, luck/force_luck, toolModifier and assembly-skill contribution (SharedLabratory.cpp:164-187). Force assembly is included in assemblySkill (148-151).
- Low luck can subtract random(100); failMitigate depends on assembly skill, city bonus and force_failure_reduction (152-180). Do not use the draft's shortened equation for distribution assertions.
- Exp-roll amazing is also an early luck threshold; ordinary rolls include city, force, food multiplier and low-luck penalty (CraftingManagerImplementation.cpp:66-111). Increasing MA improves ordinary rolls through effectiveness, but does not change that early amazing threshold.
- On an overspent-points branch, CriticalFailure is assigned and the session returns after cancel BEFORE experimentRow (CraftingSessionImplementation.cpp:1115-1121). That is not a reachable -8% applied row outcome on this path.
- Tool force-amazing counters can override outcomes (CraftingSessionImplementation.cpp:777-780,1108-1114); comparisons must control them too. Total points are int(experimentation skill/10) at 764.
- Component contributions can change final attributes after resource percentages; the advertised ceiling applies to the resource-based component, not an unconditional final-item bound. Ordinary blank-group attributes use fixed endpoints (CraftingValues.cpp:86-90).

**Not established:** displayed rounding, all specialty labs, concrete DL44 template data against client archives, or in-game behavior. No staff resource command was used.

**Verdict:** Weighted-quality model and arithmetic hold; fix amazing-roll semantics, omitted roll branches, critical cancellation and unconditional final-item ceilings.
