# Creature Handler: top-tier solo PvE, group PvE and PvP

14 October 2026 — ChatGPT. Owner explicitly chose **strong across all three**. Research/design only: no profession changes, pet creation, gameplay tests or server edits. We have not measured current CH performance and cannot honestly assign it a tier yet.

## Recommendation

Make CH an active pet commander with reliable combat uptime, distinct pet roles and worthwhile Master investment. Start by measuring and fixing control/AI/survival problems; then tune owner-plus-pet output. Increasing the pet-level cap alone risks creating a stronger passive add-on without fixing group or PvP usefulness.

Target: excellent solo sustain, a useful offensive/support slot in groups, and credible PvP pressure with ways to counter it. Being strongest at every activity simultaneously is a balance choice, not an achievable neutral tier ranking. We can instead make CH a top-tier option in each through different pet/loadout choices.

## Verified local build baseline

Read local `datatables/skill/skills.iff` with `tools/owner_content/ch_build_probe.py`; saved prerequisite closures and raw CH rows in [creature-handler-build-probe.json](creature-handler-build-probe.json). Missing login configuration limits claims about the running client's effective load order. These are local-table values, not confirmed deployed server skill definitions.

| Build, including prerequisite boxes | Points | Remaining from 250 | Proposed purpose |
|---|---:|---:|---|
| Master CH | 106 | 144 | Baseline cost, including Scout requirements |
| Master CH + Master Rifleman + Novice Medic | 213 | 37 | First ranged PvE/PvP benchmark; spend remainder on verified healing/defence needs |
| Master CH + Master TKA + Novice Medic | 213 | 37 | First durable melee/solo benchmark; do not assume this also wins ranged PvP |
| Master CH + Master Bio-Engineer | 198 | 52 | Pet production/exploration character; less room for a full personal combat profession |

Master CH modifiers sum to `tame_level=70`, `keep_creature=3`, `stored_pets=20`, with empathy/training/management skill mods each 50. Stored-pet modifier is not necessarily total datapad capacity: server base allowance must be checked. Skill-mod values are not direct percentage success claims. The script initially used an incorrect BE identifier, failed, then was corrected to `outdoors_bio_engineer_master` and rerun successfully; the saved report is valid JSON.

Recommendation for an actual first combat test: MCH/MRifleman/Novice Medic, compare with MCH/MTKA/Novice Medic. Master BE can live on a crafter so combat CH retains combat points. No single build is proven S tier by these costs.

## Primary implementation evidence

Read public SWGEmu Core3 `unstable` source on 14 Oct; this is a moving upstream branch, **not a pinned audit of our local dev revision**. Pin and compare before engineering.

- [PetControlDeviceImplementation.cpp](https://raw.githubusercontent.com/swgemu/Core3/unstable/MMOCoreORB/src/server/zone/objects/intangible/PetControlDeviceImplementation.cpp): creature-pet calls check owner skills, adult level, number active and combined active levels. Examine output includes resistances, attack speed, accuracy, damage and specials. This supports measuring real stats instead of picking the largest model or highest level.
- [PetManagerImplementation.cpp](https://raw.githubusercontent.com/swgemu/Core3/unstable/MMOCoreORB/src/server/zone/managers/creature/PetManagerImplementation.cpp): trained commands route through queued pet commands; speaker ownership/friend and building context matter. Incapacitation and vitality-loss paths exist. These are audit/test targets, not proof that our server is broken.
- [PetAttackCommand](https://github.com/swgemu/Core3/blob/unstable/MMOCoreORB/src/server/zone/objects/creature/commands/pet/PetAttackCommand.h) and [PetSpecialAttackCommand](https://github.com/swgemu/Core3/blob/unstable/MMOCoreORB/src/server/zone/objects/creature/commands/pet/PetSpecialAttackCommand.h): separate attack/special paths validate pet/target context. Measure command acceptance, target acquisition and actual hits separately.
- [CreatureImplementation.cpp](https://raw.githubusercontent.com/swgemu/Core3/unstable/MMOCoreORB/src/server/zone/objects/creature/ai/CreatureImplementation.cpp): tame eligibility and creature-knowledge inspection are explicit paths. Special availability and resistances need actual creature/template inspection before recommending individual species.

Public historical guides often mix eras. [Restoration explicitly describes its CH as heavily modified NGE Beast Master](https://swgr.org/wiki/creature_handler/); its pet abilities/attributes are not our pre-CU baseline. Its design may inspire original optional features, but no NGE system import is required. SWGEmu's old scrapbook guide could not be fetched; modern forum balance claims and secondary guides were not used as proof of current DPS. No excluded server material used.

## Proposed improvements, in priority order

| Change | Solo PvE benefit | Group/PvP role | Maturity and effort |
|---|---|---|---|
| Reliable follow, attack, recall, target switching, door/cell paths and clear failure feedback | Removes lost damage/time and avoidable deaths | Pets can respond to focus-fire and retreats | High priority hypothesis; test first. Medium–high engineering, especially indoor AI |
| Distinct tank, damage and control/support pet profiles within one total budget | Choose survival vs faster kills | Tank/off-tank PvE, pressure or utility PvP | Concept; medium Lua/data, high if new commands needed |
| CH-Master-gated pet combat scaling | Makes investment matter beyond a shallow dip | Budget owner+pet damage together; avoid a full fighter plus free full fighter | Concept; medium–high C++; no multipliers chosen |
| Useful active commands with real costs/cooldowns | Timed mitigation, recovery and burst | Short pressure windows, peel/support | First audit existing Embolden/Enrage/specials. New buff semantics high; don't assume missing functionality |
| Pet-specific sustain and encounter AoE survivability | Longer fights become feasible | Pets survive ordinary raid splash; deliberate enemy focus still works | Concept; medium–high. Keep PvE splash protection separate from PvP burst mitigation |
| Useful wild and BE pets with tradeoffs | Exploration and crafting both reward player | Multiple viable families instead of one required pet | Concept; medium template/BE audit and balancing |
| Endgame training/equipment/consumables with caps | Gradual bounded progression | Encounter-specific loadouts | Later optional feature; high new item/persistence/UI work; can connect Botanist supplies after basic CH works |

Do not start with higher pet count, universal immunity, unlimited stat inheritance, or universal PvP taunts. Increased population affects server AI cost, target clutter and player control. Any buff must affect the intended owned CH pets, not every wild creature sharing their template, droids/faction pets, or unrelated companions.

### Solo targets

One strong pet or a coordinated smaller pack should handle difficult single targets and ordinary packs with active healing/positioning. Test one level-70 budget against 35+35 and 24+23+23 configurations using eligible actual pets. Those are budget examples, not claims that specific pets with those levels exist. Compare armour/resist profile, hit rate, attack interval, specials, recovery time and acquisition cost. Keep boss scripts/phase mechanics meaningful.

### Group targets

Give a reason to invite a CH when other damage dealers are available: sustained damage plus one bounded utility role. Possible original abilities include a brief allied defensive effect, a target debuff, or a pet intercept. These are proposals, not existing commands. Cap duplicate effects and choose whether shared buffs consume pet damage budget. PvE threat tools must respect boss immunity rules and do not force player targets in PvP.

### PvP targets

Pets must reach a normally moving target and obey focus/recall promptly. They must also be susceptible to deliberate kiting, line of sight, crowd control or focused attacks. Threat is an NPC mechanism; PvP needs pressure, interrupt/peel or debuff effects. Separate PvP coefficients and shared control cooldowns may be needed so several pets cannot create permanent knockdown/disease chains. Resist/immunity duration rules must be audited first. Death or disengagement of the owner must not leave autonomous damage continuing indefinitely. Defeating a pet should buy a meaningful window; instant store/call healing or repeated fresh-pet rotation must not erase counterplay.

## How to prove S-tier viability

Measure **owner plus every controlled combat unit**, including any droids/faction/mercenary companions, and total consumable/buff cost. Record whether pet healing/buffs are allowed. A paper-DPS estimate ignores contact time, hit chance, mitigation and incapacitation downtime; use damage delivered per whole encounter and time between encounters.

| Test | Controls | Measurements |
|---|---|---|
| Commands/pathing | Open field, obstacles, interiors, target switching and moving targets | Acceptance/first-hit latency, time in contact, blocked commands, wrong targets and stuck events |
| Solo farming | Same enemy set, gear/buffs and elapsed session | Kills/minute, death rate, player/pet healing, resources consumed and downtime |
| Solo elite/boss | Same eligible encounters, at least five runs per setup | Completion rate, time, damage attribution, pet survival, phase failures |
| Group | Swap one party slot between CH and a benchmark build; same team/encounter | Completion time, utility effect, healer load, wipes and extra AI load |
| PvP duels | Equal gear/buffs, alternating sides and multiple pilots; melee, ranged, control archetypes | Matchup spread, counterplay, command/contact uptime and death/recall behavior |
| Small-group PvP | Similar budgets and multiple CH counts | Focus-fire viability, stacking/control chains, visual targeting and latency |
| Lifecycle | Store/call, relog, transfer, training, death and vitality | Persistence, no duplication, no reset-to-full exploit, no stats applied twice |

Proposed acceptance targets, **not observed results**: correct command response at least 95% in unobstructed valid cases; no unexplained idle gaps; CH within roughly 10% of a strong comparison build's PvE output when its utility is modest, or demonstrably compensating through utility/sustain. PvP needs viable matchups and pilot counterplay rather than 100% win rate. Tune numbers only after baseline measurements. Do not silently redefine S tier as faster levelling.

## Engineering handoff

First request: pinned local skills/server pet call rules, creature combat-stat setup, pet specials, healing/Embolden/Enrage, target/threat/CC handling, BE stat calculation and owned-pet progression. Ask Claude to review a small measured change set after baseline, not deploy a speculative global buff. Some command files could not be fetched during this bounded pass; no effect values invented. No new creature art required for the initial balance slice.

UM's existing research/source-inspection workflow was used; no executable tools needed for balancing arithmetic. Saved this report, local probe and feature proposal; no `/opt/swg` edits or Git commit. Next: discuss **Tames** with owner and Claude (explicit owner request), including which species can be tamed, wild-vs-BE progression, rare/endgame pets and the total pet-level budget. Taming rare models and making combat strong are related but separate decisions.
