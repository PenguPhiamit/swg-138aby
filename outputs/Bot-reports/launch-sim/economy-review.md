# New-player economy review

15 Oct 2026, Claude. Read-only: nothing under `/opt/swg` was written. Not committed.

Question: the launch simulation ([FINDINGS.md](FINDINGS.md) section 3) saw about 0.3 credits per kill and almost no affordable training. What does the server really give a new character, and what should the starter economy be?

**Legend for every number below:**
- **R** = read from source, Lua or game data (file:line given).
- **S** = read from the simulation reports (`numbers-run3.md`, `FINDINGS.md`).
- **C** = computed by me from R and S numbers.
- **A** = my assumption (stated where used).

**Sources read:**
- Core3-dev `/opt/swg/Core3-dev/MMOCoreORB`. Its HEAD moved from `cbb8fc10` to `41764180` to `17cacd70` while I read. The file:line numbers below are from `41764180` or later, and the commit after `41764180` only touches `BotPopLaunchBrain.h`.
- The test galaxy's `bin/conf/config-local.lua`, economy keys only. Nothing secret is quoted here.
- The test galaxy's economy scripts (`mission_manager.lua`, `loot_manager.lua`, `player_manager.lua`, `player_creation_manager.lua`, the junk dealer, the trainer handler, the Tatooine and Rori destroy-mission lists) are byte-identical to Core3-dev's (`diff`, C).
- Skill costs come from `datatables/skill/skills.iff` in `/opt/swg/tre/local_planets.tre`. That archive is first in the load order (`config-local.lua:59`), so it wins.

## Summary

1. **A real new character starts with 10,000 cash plus 100,000 bank (110,000 credits)** (R). Stock Core3 is 100 + 1,000. The sandbox raised it on 13 Oct.
2. **The simulation's bots start with 0 credits** (R: `BotPopLaunchBrain.h:131-135` sets only skill points and the novice box). That is the main reason almost nothing was affordable. At the sandbox settings, one profession to master costs 11,275 (C), against a real purse of 110,000.
3. **Wildlife never drops credits** (R). Only humanoid NPCs do: about 41-73 credits per kill at level 1-10 (C), plus about 7 credits of expected junk. The bots killed almost only wildlife, so the 0.3 credits per kill is expected.
4. **Missions pay far more than hunting.** A destroy mission pays 375 credits per lair difficulty point (R), about 2,400 on average at level 1 and 4,100 at level 10 (C). An in-town delivery pays about 81 (C). A between-city delivery pays about 916 (C).
5. **Training costs 25 / 250 / 500 / 750 / 1,000 / 1,250 credits per box** (novice / tier 1 / 2 / 3 / 4 / master) at the sandbox's ×0.25 (R, C). The stock prices are four times that.
6. **Recommendation (the owner's call):** Option 2 below. Give new characters the stock purse of 100 + 1,000 and keep training at ×0.25. The four first-tier boxes (1,000) are covered at creation. The next tier needs about one hour of missions.

## 1. What a new character starts with

| Item | Value | Evidence |
|---|---|---|
| Cash credits | 10,000 (stock 100) | `bin/scripts/managers/player_creation_manager.lua:4`; read in `PlayerCreationManager.cpp:268`; granted at `:424` |
| Bank credits | 100,000 (stock 1,000) | `player_creation_manager.lua:7`; `PlayerCreationManager.cpp:269`, `:428`. The compiled-in stock defaults are at `:41-42`. |
| Skill points | 1,000 (stock 250) | `player_creation_manager.lua:10`; `PlayerCreationManager.cpp:435` |
| Free skill | `<profession>_novice`, no payment | `PlayerCreationManager.cpp:774` |
| Common inventory items | maroj melon, survival knife, X31 landspeeder deed | `player_creation_manager.lua:60`; added at `PlayerCreationManager.cpp:747-754` |
| Profession items | brawler: stone knife, heavy-duty axe, wooden lance staff | `player_creation_manager.lua:50-58` |
| | marksman: pistol, carbine and rifle (cdef) | |
| | artisan: generic tool, mineral and chemical survey tools | |
| | scout: generic tool | |
| | medic: food tool | |
| | entertainer: slitherhorn | |
| Clothes | from `creation/default_pc_equipment.iff` and `creation/profession_defaults.iff` (not decoded here) | `PlayerCreationManager.cpp:116`, `:184` |
| Tutorial | off by default (no tutorial rewards) | `PlayerCreationManager.cpp:400` |

- The sandbox commit `4357970d` changed these from 100 / 1,000 / 250 (R: `git show`).
- The file's own comment says "changed during test phase, normal value is 100".
- **Server-made bots get none of this.** The launch code (`BotPopLaunchBrain.h:129-135`) sets only the skill points and the novice box, and says "a server-made character has none". The only credit write in `botpop/` is the junk sale (`:497`). Mission pay arrives through the normal mission code (bank).

## 2. Mission rewards

**How a mission list is built.**
- The general terminal fills 6 destroy and 6 deliver missions (`MissionManagerImplementation.cpp:631-633`).
- Artisan, entertainer and scout terminals have their own types (same file, `:660-720`).
- A player holds up to 6 active missions. This is a sandbox setting, `Core3.MissionManager.MaxActiveMissions` (`:268-272`); stock is 2. It is not in `config-local.lua`, so the code default of 6 applies.
- Terminals need no skill (except bounty). Level only changes which lairs qualify.

**How the reward is paid.**
- The whole reward goes to the **bank** (`MissionObjectiveImplementation.cpp:320`, `:364`).
- A group splits it (`:308`).
- There is **no config multiplier**.
- Two multipliers exist: the city-bonus skill mod `private_spec_missions` (`MissionManagerImplementation.cpp:641`, 0 for a new character) and the slicer ×1.5 (`:638`, needs `combat_smuggler_slicing_01`).

### Destroy missions (the big one)

- **Formula (R):** `reward = 0 + 375 × difficultyLevel + rand(0) + rand(15 × difficultyLevel)` (`mission_manager.lua:91-94`; `MissionManagerImplementation.cpp:924-926`).
- **Difficulty level:** `difficultyLevel` is a random integer between the lair's `minDifficulty` and `maxDifficulty` (`:831`). The numbers are creature levels, for example kreetle lair 1-5, gorg lair 4-8.
- **Which lairs qualify:** the player level `L` is `min(25, weaponCombatDifficultyMod / 100 + 1)` (`PlayerManagerImplementation.cpp:4403-4419`). A lair qualifies if `minDifficulty <= L + 5` and `maxDifficulty >= min(L - 5, ceiling)` (`MissionManagerImplementation.cpp:1896-1902`). The lists are `mobile/spawn/destroy_mission/<planet>_destroy_missions.lua`.
- **Distance:** the lair is 1,000 to 2,000 m from the terminal (`mission_manager.lua:83-86`). It spawns when the owner arrives. The mission pays when the lair is destroyed.
- **Mean list reward (C):** I replayed the selection over the five launch planets' lists. I assumed `random(n)` covers 0..n. Mean by player level `L`, averaged over Tatooine, Corellia, Naboo, Talus and Rori:

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mean reward of the whole list (C) | 2,428 | 2,684 | 2,957 | 3,089 | 3,310 | 3,465 | 3,652 | 3,846 | 3,997 | 4,133 |
| Level-matched mission (difficulty = L), 382.5 × L (C) | 382 | 765 | 1,148 | 1,530 | 1,912 | 2,295 | 2,678 | 3,060 | 3,442 | 3,825 |

- **Range at level 1, by planet (C):**

| Planet | Mean | Range |
|---|---|---|
| Tatooine | 2,136 | 375-3,900 |
| Corellia | 2,623 | 1,500-3,900 |
| Naboo | 2,518 | 750-3,900 |
| Talus | 2,295 | 1,125-3,510 |
| Rori | 2,568 | 1,500-3,900 |

- **What the bots will do:** since `41764180` they take the best-paying destroy mission whose difficulty is at most `2 × level + 6` (`BotPopLaunchBrain.h:1288`). A level-1 bot can take difficulty 8, which pays about 3,000. They abort after 20 minutes (`:1180-1181`).

### Other mission types (all R formulas; the numbers are C)

| Type (terminal) | Formula | Evidence | Concrete numbers |
|---|---|---|---|
| Deliver (general) | `40 + (player to pickup + pickup to drop) / 10` | `MissionManagerImplementation.cpp:1361-1364` | In town about 81 on average (42-148). Between cities about 916 (229-1,559). I sampled 18 launch cities with the NPC spawn points (`mission_npc_spawn_points.lua`), the player at the city centre. Level does not matter. |
| Crafting (artisan) | same as deliver | `:1421-1455` (it calls the deliver generator) | 81 in town, 916 between cities |
| Survey (artisan) | `400 + 20 × (level - 50) + rand(100)` | `:1038` | 400-500 with no surveying skill (level fixed at 50). Rises to at most about 1,400 at maximum skill. |
| Entertainer, dancer or musician | `100 + distance to the theatre / 10 + rand(100)` | `:1509` | 100-200 plus 1 credit per 10 m. The distance was not sampled. |
| Recon (scout) | `50 + distance / 5`, target 1,000-4,000 m away | `:1641`, `:1670` | 250-850, mean 550 |
| Hunting (scout) | `500 + difficulty × 100 × lair minDifficulty + rand(100)`; difficulty 1 (50%), 2 (33%), 3 (17%) | `:1619-1620` | Lair minDifficulty 1: 600-800. Lair minDifficulty 5: 1,000-2,000. |
| Bounty | `creatureLevel × (200 + rand(200))` at level 1 | `:1195` | Needs a bounty hunter skill, so not for new characters. |

**Rate rule of thumb (C, with A).**
- Deliver pays 1 credit per 10 m of walking. Running at 5.376 m/s (R: `CreatureObjectImplementation.cpp:98`) is at most 1,935 credits per hour, and the real figure is lower.
- Every character also carries an X31 speeder deed (R), which I did not model.
- **Time per mission is not in the code.**
  - The only timing data points are the 20-minute bot abort (R) and one 8.2-minute run of the old `cresh-missions` scenario with 4 of 6 checks passing (S: `Bot-reports/TIMINGS.md:15`). The handoff (C9) says that scenario's target was 2 km away and its walk timed out.
  - I assumed 4 minutes per in-town delivery and 20 minutes per destroy mission (A).

## 3. Creature credits, loot and junk

### Credits

- **Only humanoid NPCs drop credits** (R).
  - `CreatureManagerImplementation.cpp:689-691` pays `calculateLootCredits(level)` only when `isNonPlayerCreatureObject()` is true.
  - `ObjectManager.cpp:109-110` registers the class `Creature` for type `CREATURE` (animals) and `NonPlayerCreatureObject` for `NPCCREATURE` (humanoids).
  - Animals are type `CREATURE` and so the `Creature` class, so a kill adds no credits. This follows from the class registration; I did not decode each template's object type. It matches the simulation (S).
- **The formula (R: `LootManagerImplementation.cpp:301-308`):**
  - `max = round(0.03 L² + 3 L + 50)`
  - `min = round(max / 2 + 2 L)`
  - credits are a uniform roll between min and max.
- **Credits per humanoid NPC kill (C):**

| Level | 1 | 3 | 5 | 7 | 10 |
|---|---|---|---|---|---|
| Credits | 29-53 | 36-59 | 43-66 | 50-72 | 62-83 |
| Mean | 41 | 47.5 | 54.5 | 61 | 72.5 |

- The player takes the cash with `loot all` (R: `PlayerManagerImplementation.cpp:4226-4243`).

### Wildlife loot

- Wildlife loot tables are empty, for example `mobile/tatooine/kreetle.lua:33`, `lootGroups = {}`. That is the reason the bots found "almost no sellable loot".
- Of 1,970 creature templates at level 10 or below that declare `lootGroups`, 1,587 (81%) have an empty table (C: scan of `bin/scripts/mobile`; the count includes wildlife and some NPCs).

### Humanoid loot

- An NPC without an explicit `lootChance` rolls 20% plus 0.2% per level (R: `LootGroupCollectionEntry.h:39-42`).
- Example (R): the evil settler (level 5, `mobile/tatooine/evil_settler.lua:32`) uses `thug_tier_1`. 24% of that group is "junk" and 88.5% of the junk group is single junk items (`loot/groups/npc/thug/thug_tier_1.lua`, `loot/groups/junk.lua`).
- Expected junk per kill is about 0.21 × 0.24 × 0.885 × 151, so **about 6.7 credits** (C).

### Junk dealer prices

- Junk dealers pay the item's full junk value (R: `junk_dealer.lua:157-161`).
- The value is `rand(min..max) × junkValueModifier` (R: `LootManagerImplementation.cpp:280-299`). `junkValueModifier = 5` (`loot_manager.lua:79`).
- Each loot item's lua gives the base min and max (R: 594 items under `loot/items/`).
- The 31 single items of the junk group have a mean value (min and max averaged, then ×5) of 150-175 credits each, **about 151 weighted across the group** (C).
- Individual sales vary between each item's min and max ×5. Run 3's median sale was 119 (S).
- Items with `junkDealerTypeNeeded` of 2 or more get an extra `level × 1%` (R: `:287-289`).

### Why the simulation saw 0.3 credits per kill (C)

- The bots made 15,967 kills per hour in total, which is 10.6 per bot-hour (S).
- Wildlife pay 0. Humanoid NPCs pay about 61 at level 5.
- Evil settlers were 234 of 20,737 kills, about 1% (S).
- 1% of 61 credits is about 0.6 per kill, the same order as the observed 0.3. The observed 3.7 credits per bot-hour is also consistent.
- Even if every kill were a humanoid NPC at level 5, the pace would be about **650 credits per hour** (C).

## 4. Training costs

**Where the number comes from.**
- Each box has a base price in `skills.iff`, column 7 (R: `Skill.h:102`).
- `getMoneyRequired()` multiplies it by `Core3.Sandbox.TrainingCostMultiplier` (R: `Skill.h:314-315`). The sandbox sets 0.25 (`config-local.lua:20`; stock 1.0).
- The multiplier is applied per box and truncated to an integer.
- The trainer charges cash first, then bank (R: `trainerConvHandler.lua:221-254`).
- The `force_persuade` skill mod gives a discount (`:165-167`), which only Jedi have.
- Nothing else charges for a skill (`SkillManager::awardSkill` does not).

**Costs per box (R from the effective `skills.iff`, C for the sandbox column).** All six professions I checked have the same cost structure: `combat_brawler`, `combat_marksman`, `crafting_artisan`, `outdoors_scout`, `science_medic` and `social_entertainer`.

| Box | Count | Base price | Sandbox price (×0.25) | Stock price (×1.0) |
|---|---|---|---|---|
| novice | 1 (free at creation) | 100 | 25 | 100 |
| tier 1 (`_01`) | 4 | 1,000 | 250 | 1,000 |
| tier 2 (`_02`) | 4 | 2,000 | 500 | 2,000 |
| tier 3 (`_03`) | 4 | 3,000 | 750 | 3,000 |
| tier 4 (`_04`) | 4 | 4,000 | 1,000 | 4,000 |
| master | 1 | 5,000 | 1,250 | 5,000 |

- **Whole profession, sandbox (×0.25):**
  - tier 1: 1,000
  - tiers 1-2: 3,000
  - tiers 1-3: 6,000
  - all 18 paid boxes: 11,250 (11,275 with novice)
- **Whole profession, stock (×1.0):** 4,000 / 12,000 / 24,000 / 45,000 (45,100 with novice).
- The simulation's 3,280 boxes cost 945,500, an average of 288 credits per box, or 630 per bot (C from S).
- **Experience, not credits, is the long pole above tier 2.** The cost column of `skills.iff` (R) gives the XP for the four boxes of a tier:

| Profession | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|
| brawler | 4,000 | 20,000 | 60,000 | 280,000 |
| marksman | 3,300 | 17,250 | 51,000 | 232,000 |
| scout | 4,000 | 20,000 | 40,000 | 65,000 |
| medic | 3,500 | 16,000 | 33,000 | 51,000 |
| entertainer | 4,000 | 20,000 | 50,000 | 130,000 |
| artisan | 2,000 | 5,500 | 14,000 | 28,000 |

- The sandbox's 5× XP gain applies on top (`player_manager.lua:60`, `PlayerManagerImplementation.cpp:2634`). Stock is 1.0 (R: `git show 4357970d`).
- **Pacing (S).** Median time to the first box: brawler 4.6 min, entertainer 8.6, marksman 21.0, medic 24.2, scout 45.4. Boxes per bot-hour: 2.82, 1.53, 1.64, 1.9 and 0.44.
- **Spend rate needed to keep pace (C).** Boxes per hour × the tier-1 price:

| Price level | brawler | entertainer | marksman | medic | scout |
|---|---|---|---|---|---|
| ×0.25 | 705 | 382 | 410 | 475 | 110 |
| ×0.5 | 1,410 | 765 | 820 | 950 | 220 |
| ×1.0 | 2,820 | 1,530 | 1,640 | 1,900 | 440 |

## 5. Sandbox settings that touch the economy

| Setting | Sandbox value (stock) | Where | Effect |
|---|---|---|---|
| `Core3.Sandbox.TrainingCostMultiplier` | 0.25 (1.0) | `config-local.lua:20`; applied at `Skill.h:315` | skill-box prices ×0.25 |
| `Core3.Sandbox.SkillPoints` | 1000 (250) | `config-local.lua:16` | more boxes fit before points run out |
| `startingCash` / `startingBank` | 10,000 / 100,000 (100 / 1,000) | `player_creation_manager.lua:4,7` | start purse |
| `globalExpMultiplier` | 5.0 (1.0) | `player_manager.lua:60` | boxes 5× faster |
| `Core3.MissionManager.MaxActiveMissions` | 6 by code default (2) | `MissionManagerImplementation.cpp:268-272` | three times the missions in progress |
| `Core3.Sandbox.StructureMaintenanceMultiplier` | 0.5 (1.0) | `config-local.lua:21` | cheaper upkeep |
| `maintenanceDiscount` | 0.5 (1.0) | `city_manager.lua`, commit `4357970d` | cheaper city upkeep |
| `FactoryTimeMultiplier` / `CraftSeconds` | 0.25 / 1 | `config-local.lua:18-19` | faster crafting |
| Shuttle timings and vehicle speeds | faster than stock | `planet_manager.lua`; vehicle Lua | travel cheaper in time |
| `junkValueModifier` | 5 | `loot_manager.lua:79` | junk sells ×5 of its base value (not sandbox-labelled; no stock value known) |
| Mission reward formulas | stock | `mission_manager.lua:91-94` | no local change since the first import |

`config-local.lua` has no mission-reward, loot-credit or vendor key. Test-galaxy-only keys (`TameAnything`, `MedicalAnywhere`, `AgentGear`, `BotPop*`) do not affect the economy.

## 6. Options for the starter economy

**Common assumptions for all options.**
- XP stays at 5×, so the sim's box pace holds.
- "Time to afford" means play hours beyond the starting purse. Higher boxes also need XP, which is separate.
- Income lines (hourly rates):
  - **Level-matched destroy** (a level-2 character, 765 per mission, 3 per hour; A: 20 minutes each): about 2,300 per hour.
  - **Best-of-list destroy**, as the bots will take them (2,700 per mission, 3 per hour; A): about 8,100 per hour.
  - **Between-city deliveries** (running, no downtime): at most 1,935 per hour.
  - **In-town deliveries** (81 each, 15 per hour; A: 4 minutes each): about 1,215 per hour.
  - **Hunting humanoid NPCs only** (sim pace): about 660 per hour.
  - **Hunting wildlife** (S): 3.7 per hour.
- All times are C.

| | **Option 1: keep the sandbox purse** | **Option 2: stock purse, cheap training** | **Option 3: stock purse, stock prices** |
|---|---|---|---|
| Purse after creation | 110,000 | 1,100 | 1,100 |
| Training multiplier | ×0.25 | ×0.25 | ×1.0 |
| Mission rewards | stock | stock | stock |
| Cost: 4 tier-1 boxes | 1,000 | 1,000 | 4,000 |
| Cost: tiers 1-2 (8 boxes) | 3,000 | 3,000 | 12,000 |
| Cost: whole profession (18 boxes) | 11,250 | 11,250 | 45,000 |
| **Time to afford the 4 tier-1 boxes** | 0 (affordable at creation) | 0 (1,000 of 1,100) | level-matched destroy 1.3 h; between-city deliveries 1.5 h; in-town deliveries 2.4 h; NPC hunting 4.4 h |
| **Time to afford tiers 1-2** | 0 | level-matched destroy 0.8 h; best-of-list destroy 0.2 h; between-city deliveries 1.0 h; in-town deliveries 1.6 h | level-matched destroy 4.7 h; best-of-list destroy 1.3 h; between-city deliveries 5.6 h; in-town deliveries 9.0 h |
| **Time to afford the whole profession** | 0 | level-matched destroy 4.4 h; best-of-list destroy 1.3 h; between-city deliveries 5.2 h; in-town deliveries 8.4 h | level-matched destroy 19 h; best-of-list destroy 5.4 h; between-city deliveries 23 h; in-town deliveries 36 h |
| Does income keep pace with the sim's box pace? | credits never gate | yes, all roles: brawler spends 705 per hour against 1,215 per hour from in-town deliveries | brawler needs 2,820 per hour, so only destroy missions keep up (2,300-8,100 per hour); the other roles (440-1,900 per hour) need between-city deliveries or destroy |
| Pressure on a new player | none; money means nothing for weeks | low; the first tier is free of grind, the second needs about an hour of missions | high; the player has to run missions in the first hour |
| Config change | none | `player_creation_manager.lua:4,7` only (Lua, no rebuild) | the same, plus delete `TrainingCostMultiplier` in `config-local.lua:20` |

**A variant with a middle price (×0.5, purse 1,100)** costs 2,000 / 6,000 / 22,500 for the same three goals. The extra time is 0.4 / 2.1 / 9.3 hours on level-matched destroy missions (C).

**A mission reward multiplier** divides every time in the table by the multiplier. For example ×2 turns Option 3's whole-profession time on level-matched destroy missions from 19 h to 9.5 h.
- The destroy missions can be scaled in Lua (`mission_manager.lua:91-94`).
- Every other mission type is hard-coded (lines listed in section 2). A single multiplier would be a small C++ change next to the city-bonus lines (`MissionManagerImplementation.cpp:633-641` and the other terminals).

**My recommendation: Option 2** (the owner decides):
- It fits the sim's pace, since the player trains the first box every 5-20 minutes and the tier-1 set costs 1,000.
- It gives new players a reason to use the mission terminals (tier 2 and above).
- Credits stop mattering well before XP does.
- If the owner wants a "friends' launch" with no grind, Option 1 is already in place.
- If the owner wants the pre-CU feel, Option 3 is the route, and it needs missions to be reliable income. A mission multiplier would then be worth the C++ edit.

## 7. What this means for the simulation

- **Give the server bots the creation purse** (10,000 + 100,000, or whichever option wins). Do it at spawn in `BotPopLaunchBrain.h` near `:131`. Otherwise the bots can never be affordable, which is not what a real player experiences.
- **Charge the training** in the next run, so affordability is measured rather than recorded.
- **The `41764180` mission code is the first source of bot income.** Compare its `mission_done` rows (reward and credits actually paid) with section 2 before changing anything.
- **Humanoid targets.** Hunters rarely meet humanoid NPCs near the starting cities. A sim that wants hunting income has to send some bots to them. Wildlife will stay at zero.

## 8. Not checked

- Mission time per type (the 4 and 20 minutes are assumptions; the code has no timing).
- The X31 speeder's speed and whether the sandbox changed it (its Lua has no speed line; the stock value is in client data).
- Vendor, bazaar and entertainer-tip income; ticket prices; cloning and insurance costs; repair costs. Each is a credit source or sink for a new player and none was read.
- Quests that pay credits (starter or theme-park quests). I looked at the creation code only.
- Whether `System::random(n)` includes `n`. I assumed 0..n; the effect on the means is under 1%.
- Dantooine, Lok, Yavin 4 and the other tier-1 outpost destroy lists. I only did the five launch planets.
- The live galaxy (`swg-local`) and its own config. This review covers Core3-dev and the test galaxy only.
