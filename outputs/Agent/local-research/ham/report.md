Written by Claude Opus, 15 Oct 2026, from Core3-dev 90044b8e.

# HAM pools (pre-CU) in Core3-dev

All paths are relative to MMOCoreORB/. "COI" = src/server/zone/objects/creature/CreatureObjectImplementation.cpp, "PMI" = src/server/zone/managers/player/PlayerManagerImplementation.cpp.

## 1. Short answer

Each creature keeps four 9-slot lists: base, current, max and wounds, plus 3 encumbrance slots (COI:216-239). Primaries (health, action, mind) are the pools that take damage and regenerate. Secondaries are pinned to max minus wounds, and constitution, stamina and willpower set the regen rate of their primary (COI:3213-3218, 1399-1400, 1467-1468). Wounds lower the usable cap (max minus wounds) but not the reported max, and each wound adds 1 shock. Shock above 250 scales down tend, heal-mind and enhance power, to a floor of 25% (COI:2644-2655). A primary at 0 or below incapacitates the player for 5-60 s, and the third incapacitation inside 10 minutes kills (PMI:1156-1166, 1222-1223).

## 2. How it works

**Pools and messages.** Index order inferred from code: 0 health, 1 strength, 2 constitution, 3 action, 4 quickness, 5 stamina, 6 mind, 7 focus, 8 willpower. "i % 3 == 0" marks a primary (PMI:5088, COI:1214), and a combat wound hits pool, pool+1 and pool+2 (src/server/zone/managers/combat/CombatManager.cpp:1692-1694). The client is sent:
- base HAM in CREO1 0x02 (COI:1361-1365)
- current in CREO6 0x0D (COI:1169-1173)
- max in CREO6 0x0E (COI:1452-1456)
- wounds in CREO3 0x11 (COI:1385-1387)
- shock in CREO3 (COI:721-722)
- encumbrance in CREO4 0x02 (COI:1478-1481)
- the incapacitation timer in CREO3 (COI:706-707)

setHAM does not clamp the value (COI:1162-1174).

**Base values.** Species ranges come from client data tables `datatables/creation/attribute_limits.iff` and `racial_mods.iff` (src/server/zone/managers/player/creation/PlayerCreationManager.cpp:56-98). The numbers are not in the source tree.

**Regeneration.** PlayerObject's update calls `activateHAMRegeneration(latency)` (src/server/zone/objects/player/PlayerObjectImplementation.cpp:2407). The rules (COI:3198-3233):
- No regen while incapacitated or dead.
- NPCs do not regen in combat. Players do: the combat check applies only to non-players.
- modifier = latency/1000, times 1.25 when kneeling or 1.75 when sitting.
- Tick = ceil(max(0, secondary) x 13/2100 x modifier), with a minimum of 1 per pool.
- Constitution feeds health, stamina feeds action, willpower feeds mind.
- Healing stops at max minus wounds (COI:1277-1282).
- Worked example (inferred): constitution 1000 over 1 s gives 7 standing, 9 kneeling and 11 sitting.
- Strength, quickness and focus do nothing here. Their use is not covered by the code read.

**Damage floors.** inflictDamage does nothing if the target is incapacitated (unless feigning death), dead or invulnerable, or if damage is 0 (COI:1200). It floors at 1 when destroy is false or the target has the avoid_incapacitation skill mod (COI:1208-1212). Secondaries never go below 0, but primaries can go negative (COI:1214). At 0 or below it notifies the destruction observers (COI:1256-1257).

**Incapacitation and death.** Each incapacitation is logged, and the counter is the number of incapacitations in the last 600 s (PlayerObjectImplementation.cpp:2322-2335; src/server/zone/objects/player/PlayerObject.idl:1198-1199).
- If the counter is 3 or more, the player is killed (PMI:1222-1223).
- Otherwise: posture INCAPACITATED, combat cleared, timer set (PMI:1225-1240).
- Timer: under 5 points below zero gives 5 s; otherwise points/5, capped at 60 (PMI:1156-1166).
- The `food.incap_recovery` buff cuts the timer by its percent and is used up (PMI:1169-1182).
- On recovery, any primary below 0 is set to 1 and the player stands up (src/server/zone/objects/player/events/PlayerIncapacitationRecoverTask.h:58-75).
- Healing a primary from 0 or below while incapacitated or dead stands the player up (COI:1284-1292).

**Wounds.**
- setWounds keeps wounds between 0 and base-1, so the limit is base, not max (COI:1374-1379). It then lowers current to max minus wounds, and sets secondaries to exactly that (COI:1395-1400).
- addWounds sends the "wounded" combat-spam message and by default adds 1 shock (COI:1432-1439; src/server/zone/objects/creature/CreatureObject.idl:606).
- In combat, the weapon's wounds ratio is the % chance to wound. A hit wounds one primary and its two secondaries by 1 each (CombatManager.cpp:1688-1694), which is 3 shock in total (inferred).
- healWound lowers wounds, never below 0 (COI:1327-1345).
- Passive wound regen: each regen tick adds (int)(skill mod x 0.2) from `private_med_wound_health/action/mind`. At 100 it heals 1 wound on each of the three pools in that group (COI:3236-3272).

**Battle fatigue (shock).**
- Shock is held between 0 and 1000, with the "shock_wound" message (COI:729-739).
- `calculateBFRatio` gives 1.0 up to 250 shock, then (1250-shock)/1000, with a floor of 0.25 (COI:2644-2655). For example, 500 shock gives 0.75.
- It is used by tend (src/server/zone/objects/creature/commands/TendCommand.h:213), heal mind (HealMindCommand.h:156) and enhance buff power (HealEnhanceCommand.h:209).
- No code read applies it to max HAM or regen.

**Encumbrance (armor).** On equip, `applyEncumbrancies` clamps each armor value to 0 or more and adds it to the three encumbrance slots (PMI:2451-2458). It then damages and lowers the max of the secondaries:
- health encumbrance: strength and constitution
- action encumbrance: quickness and stamina
- mind encumbrance: focus and willpower

`removeEncumbrancies` reverses this (PMI:2460-2503). Armor examine shows `cat_armor_encumbrance.*` (src/server/zone/objects/tangible/wearables/ArmorObjectImplementation.cpp:262-264). Lower constitution, stamina or willpower means slower regen (inferred from the regen formula).

**Buffs (medical, entertainer, food).**
- Applying a buff with attribute modifiers: max += value (minimum 1). The buff stores the amount actually applied. Current is held to new max minus wounds. Then the pool is filled, or healed by the value if the value is positive (src/server/zone/objects/creature/buffs/BuffImplementation.cpp:274-317).
- Removing it: max -= value. A primary is damaged down to the new max only if current >= new max (BuffImplementation.cpp:383-397).
- `fixHAM` rebuilds max as base + buff modifiers - encumbrance (secondaries only). It lowers current if current is above that, and changes nothing if the result is 1 or less (PMI:5026, 5079-5101). It also removes Power Boost and Force Weaken (PMI:5067-5077).
- Power Boost changes max HAM on every tick (src/server/zone/objects/creature/buffs/PowerBoostBuffImplementation.cpp:89-121).

## 3. What a bot test should check

- **Regeneration.** Damage the bot's health, then read current/max on several consecutive regen ticks while standing, kneeling and sitting, out of combat and in combat. Expect: per-tick gain = ceil(con x 13/2100 x latency/1000 x posture factor), at least 1. The sitting/standing ratio should be about 1.75 (not exact, because of ceil). Expect zero gain while incapacitated, and no gain past max minus wounds. Measure the tick interval first; it is not known.
- **Wounds.** Record base, max, wounds and shock. Apply a wound, for example take hits from a weapon with a known wound ratio. Expect: max unchanged; current at most max minus wounds; the secondaries' current equal to max minus wounds; shock +1 per wounded pool. Then heal the wounds and expect the cap to come back, but no automatic refill of the primary.
- **Encumbrance.** Read the armor's `cat_armor_encumbrance` values. Equip it and expect the max of the two matching secondaries to drop by exactly that value, current to follow, and regen to slow. Unequip and expect the values restored.
- **Battle fatigue.** Set up shock at 0, 300, 500 and 1000. Tend or heal mind with the same skill and expect power scaled by 1.0, 0.95, 0.75 and 0.25.
- **Incapacitation.** Bring a primary to N <= 0. Expect: posture incapacitated, timer max(5, min(60, |N|/5)), then the pool at 1 if it was below 0 at recovery. A third incapacitation within 600 s means death.

## 4. Likely reasons for unexpected values

- **Current above max after a buff ends.**
  - Buff removal compares current against the new max, not max minus wounds. A wounded player can therefore keep current above the usable cap (BuffImplementation.cpp:391-397).
  - The damage call it uses does nothing if the target is incapacitated, dead or invulnerable (COI:1200). A buff that ends in those states leaves current above max.
  - setMaxHAM never lowers a primary's current (COI:1445-1469), and setHAM does not clamp.
- **Negative current mind (or health/action).** inflictDamage with destroy=true lets primaries go below 0 (COI:1208-1215). Regen stops while incapacitated (COI:3199), so the negative value stays until the recovery task sets it to 1 (PlayerIncapacitationRecoverTask.h:68-71). A pool at exactly 0 is left at 0 (inferred). Whether a given affliction or DoT calls the damage code with destroy=true was not read.
- **Negative secondary (inferred).** Wounds are limited by base, not max. If encumbrance or a debuff pushes max below wounds, setWounds sets the secondary to max minus wounds, which is negative (COI:1378-1400).
- **Max differs from the bot's expected value.** Power Boost ticks change it (PowerBoostBuffImplementation.cpp:89-121). fixHAM can rewrite max at load (PMI:5096-5100). Encumbrance lowers secondary max, not primary max.
- **Regen seems too fast.** The minimum is 1 per pool per tick (COI:3220-3227), and players regen in combat.
- **Shock jumps by 3** on one combat wound (CombatManager.cpp:1692-1694, inferred).

## 5. Open questions

- The interval and latency value of the PlayerObject update that drives regen were not read.
- Species base and limit numbers live in client .iff tables. Profession starting templates were not checked.
- Which DoTs and afflictions hit mind, and whether they pass destroy=true, is unknown (the DoT code was not read).
- How entertainers remove shock, and the code paths for entertainer and food HAM buffs other than `food.incap_recovery`, were not read.
- The medic and doctor wound-heal commands, and any admin command to set wounds or shock for tests, were not read.
- What strength, quickness and focus affect outside regen is unknown.
- Whether the bot's "max" is the raw max or max minus wounds depends on the bot code, which was not read here.


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** current versus max/wounds distinction, nine-pool ordering, constitution/stamina/willpower regeneration, posture factors, primary damage floor rules, base-1 wound cap and third-incap death are supported (CreatureObjectImplementation.cpp:1195-1215,1273-1292,1374-1400,3198-3274; PlayerManagerImplementation.cpp:1208-1233). Armor lowers secondaries rather than primary max.

**Corrections:**
- The claimed 5-second MINIMUM incap formula is false. Current calculateIncapacitationTimer returns 5 only for |condition|<5; otherwise integer |condition|/5, capped at 60 (PlayerManagerImplementation.cpp:1159-1189). Thus -5 gives 1 s, -10 gives 2 s, -25 gives 5 s before food. No max(5,...) is enforced. This follows executable code, not its comments.
- The constitution-1000, one-second worked example is 7 standing, 8 kneeling, 11 sitting (ceil(1000*13/2100*1.25)=8), not 9 kneeling (CreatureObjectImplementation.cpp:3205-3227).
- At private_med_wound_* skill 100 each tick adds 20 to an accumulator, healing 1 wound per pool once that accumulator reaches 100, normally every five ticks from zero (3236-3272). It does not heal every tick merely because skill=100.
- Shock addition is controlled by doShockWounds and is one per addWounds call, not per wound point. It can occur even when clamped wounds do not rise (1404-1439); agent staging can explicitly disable it. 'Each wound adds 1 shock' is too broad.
- healDamage can stand an incapacitated/dead creature up even if computed newValue was still <=0, forcing 1 (1284-1292); 'healing from <=0' is not proof of an ordinary legal revive command.
- Negative/over-cap telemetry possibilities are source edge cases, not observed gameplay defects. Downstream callers and observer rules must be checked before inferring an exploit or successful resurrection.

**Limit:** live latency, actual timers, equip/buff removal, client baselines and negative-HAM runtime were not exercised.

**Verdict:** Core HAM model supported; correct incap minimum, kneeling arithmetic, passive-wound cadence and per-call shock semantics; runtime untested.
