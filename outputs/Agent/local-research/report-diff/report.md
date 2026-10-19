# Local model: report-diff (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 6 input lines. A local model's draft: check each item before acting on it.

## creature-harvest

| Point | report.previous.md | report.md |
|---|---|---|
| Despawn delay for empty corpses | despawned after a delay (lines 1060‑1068) | despawns after 1 second (1000 ms) [912-916, 1062-1068] |
| XP formula variable | level * 5 + 19 | creature level × 5 + 19 |
| Prey level restriction for testing | Not mentioned (implies any known type) | Novice players should target low-level creatures (level ≤ 5); higher-level or unknown-level prey is blocked from harvest testing |
| Player state requirement for testing | Not mentioned | Guard character should have ≥ 80% HAM before attempting harvest |
| Error message for missing resource type | system error is sent (lines 972‑975) | player sees 'Tried to harvest something this creature didn't have, please report this error' [974] |

## entertainer-buffs

| Point | report.previous.md | report.md |
|---|---|---|
| Buff duration cap calculation | Maximum 120 min 10 s (ES:995-997, ES:699-700) | Maximum 120.0f + (10.0f / 60.0f) = 2 hours 10 seconds |
| Buff strength cap logic | Strength grows by the performance's healShockWound column... The cap is healing_dance_mind or healing_music_mind, at most 125, plus private_faction_buff_mind in the faction case | The absolute maximum is 125% |
| Flourish mechanics | Each of the first 5 flourishes in a tick adds one more buff-growth step to every patron... The count resets every tick | Flourishes can occur up to 5 times per tick. Each flourish adds buff strength equal to performance->getHealShockWound() and triggers addEntertainerFlourishBuff() for all patrons |
| Buff application timing | The buff is applied only when the watching ends (the patron stops, the performer stops, or the patron goes out of range), and only after at least 60 s of watching | Buffs are applied to the patron when they stop watching/listening or when the performer stops... The code checks minimum 60 seconds of elapsed time |
| Healing calculation formula | woundHeal = ceil(healMindWound x healing_dance_wound/100)... Both amounts are multiplied by (flourishes this tick + 1) | Calculated as ceil(performance->getHealMindWound() * (woundHealingSkill / 100.0f))... then multiplied by (flourishCount + 1) |
| Patron eligibility check order/details | Checks, in order: 1. Deny list 2. Grouped or target 3. Incapacitated/Dead 4. Performer has private_buff_mind 5. Stored duration >= 10s 6. At least 60s passed 7. Strength > 0 | Performer requirement (private_buff_mind), Patron eligibility (grouped/target, not deny list, not incapacitated/dead), Distance, Minimum time |
| Message for insufficient watch time | You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs. | You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs. |

## factions

| Point | report.previous.md | report.md |
|---|---|---|
| Timer for going overt (recruiter change) | 30 s | 30 seconds |
| Timer for going covert (recruiter change) | 5 min | 5 minutes |
| Timer for resigning/on leave (recruiter change) | 5 min | 15 minutes (configurable default) |
| Resignation timer mechanism | 300 000 ms event | Configurable timer (default 15 min) via pending task |
| Overt cooldown duration | GCW manager overt cooldown, default 300 s | 300 seconds (configurable via GCWManager) |
| PvP broadcast channel addition | Not mentioned | Adds player to PVP broadcast chat room if enabled |

## medic-xp-healing

| Point | report.previous.md | report.md |
|---|---|---|
| XP calculation formulas | Caps and cooldowns unspecified; XP type depends on command but details lack. | HealDamage: (healthHealed + actionHealed) × 0.25; HealWound: woundHealed × 2.5; HealState: flat 50. |
| HealWound combat restriction | No explicit check mentioned in files for combat status. | Target and healer must NOT be in combat (critical requirement). |
| HealWound location requirement | No mention of location requirements. | Must be near a surgical droid or inside a hospital/campsite unless private_medical_rating > 0. |
| Cooldown formulas | Unspecified in files. | HealDamage/HealState: round(20 − modSkill/5) min 4s; HealWound: round(modSkill × −2/25 + 20) min 3s. |
| Range details | Line of sight and range required, no explicit cap mentioned. | HealDamage default 5m (dynamic for ranged); HealWound fixed 6m; HealState fixed 6m. |

## missions

| Point | report.previous.md | report.md |
|---|---|---|
| Maximum active missions limit | A player may hold 2 missions in the datapad | Players may hold up to 6 active missions by default (configurable via `Core3.MissionManager.MaxActiveMissions`) |
| Destroy mission distance range | Distance is 1000-2000 m from where the list was requested | Formula: `destroyMissionBaseDistance + destroyMissionDifficultyDistanceFactor * difficultyLevel + random(destroyMissionRandomDistance) + random(destroyMissionDifficultyRandomDistance * difficultyLevel |
| Destroy mission reward formula | Reward is 375xL + rand(15xL) | Formula: `destroyMissionBaseReward + destroyMissionDifficultyRewardFactor * difficultyLevel + random(destroyMissionRandomReward) + random(destroyMissionDifficultyRandomReward * difficultyLevel)` |
| Bounty terminal mission count | bounty terminals 10 bounty missions | generating bounty missions for slots 0–9 (which is 10 missions, but note OLD says 'at most 1 of them may be a bounty' while NEW implies standard limit applies to all types except the specific bounty r |

## scout-xp-sources

| Point | report.previous.md | report.md |
|---|---|---|
| Trapping and Foraging XP availability | Traps and Foraging grant XP (XP_TYPE_TRAP, XP_TYPE_FORAGE), though specific mechanics/limits are missing in provided files. | Trapping XP and foraging XP code are **not present** in the provided files; `ThrowTrapTask.h` and `ForageManager` implementation are missing. |
| DeployTrapCommand functionality | `DeployTrapCommand` is empty, so XP calculation is undefined. | `DeployTrapCommand.h` is an empty stub that does nothing. |
| Harvesting XP Formula | XP calculated via `CreatureManager::harvest` (line 103), no specific formula given. | Formula: `creature->getLevel() * 5 + 19`. |
| Harvesting Resource Types | Meat/hide/bone from dead creatures (lines 70-82). | Specific types: Meat (234), Hide (235), Bone (236). |
| Harvesting Range Requirement | No specific range mentioned in summary. | Player must be within 7 meters of the corpse. |
| Harvesting Quantity Calculation | No specific quantity calculation details provided. | Base quantity = `creature resource max * (creature_harvesting skill mod / 100.0)`, minimum 3 units, density modifiers applied. |
| Trapping Skill Requirement | `trapping` skill ≥1 (line 25). | Requires `outdoors_scout_novice` skill and `trapping` skill mod >= 1. |
| Trapping Target Conditions | Target valid creatures (line 75). | Target must be alive, attackable, not a pet, is a creature, and is a monster. |

## ChatGPT's review (2026-10-18 22:34)

Checked all six saved OLD/NEW inputs against corresponding report.previous.md/report.md bodies and source-corrected topic reviews. This is a **text comparison**, not validation of whichever version is newer. Source only.

**Holds:** six input pairs cover creature-harvest,entertainer-buffs,factions,medic-xp-healing,missions,scout-xp-sources. Harvest/despawn specificity, changed mission formulas, added scout detail and differing faction timer prose are real drafting differences.

**Corrections:**
- Several equal statements are presented as differences: level*5+19 versus creature level*5+19,30 s versus30 seconds, and120 min10 s versus2 hours10 seconds. They do not establish changed behavior.
- Harvest level<=5/80% HAM additions are **scenario policies**, not server harvesting prerequisites (tools/bots/scenarios/besh-harvest.py:56-63; CreatureManagerImplementation.cpp:920-1068). The table must not promote them to mechanic restrictions.
- New scout text claiming ThrowTrapTask is missing is false: src/server/zone/objects/creature/events/ThrowTrapTask.h:190-230,270-275 contains XP behavior. A report-to-report discrepancy does not settle source truth.
- New entertainer absolute125% cap omits faction addition; source grows duration in seconds and applies conversion/truncation, so comparing prose-equivalent durations does not validate units (EntertainingSessionImplementation.cpp:699-700,721-724; see entertainer-buffs human review).
- New medic wound combat gate is real (HealWoundCommand.h:131-139); its location phrasing is incomplete (115-128), and the table's summarized HealDamage cooldown omits the ranged branch. Follow the dated medic review before tests use it.
- Input is truncated to9000 characters per version and tables are also clipped (outputs/tools/agents/local/precheck.py:205-212); omitted changes are not evidence of equality. Baseline timing/config versus active configuration must be checked in source.

Verdict: Useful historical change index with redundant rows and incomplete context; neither OLD nor NEW is certified by this diff; use human mechanic reviews.
