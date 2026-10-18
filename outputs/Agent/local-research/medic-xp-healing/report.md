# Medical Experience Report — Core3 (pre-CU)

## 1. Short answer

Healing awards medical experience only when you heal **another player creature** (never yourself or pets). The XP type is always `"medical"`. HealDamage awards `(healthHealed + actionHealed) × 0.25` XP; HealWound awards `woundHealed × 2.5`; HealState awards a flat **50** XP per successful state removal. All three require the healer to be within range and have line of sight to the target, and the target must not be dead, attackable by you, or in an arena duel. HealWound additionally requires the target (and healer) to be out of combat. Multiclass bots that heal themselves first earn zero medical XP; they should instead target a willing ally player who has damage/states to heal.

## 2. How it works

### HealDamageCommand (`HealDamageCommand.h`)

- **Range**: default `5` metres (line 26). For ranged stimulants the range is `packRange + (healing_range skillMod / 100 × 14)` (lines 437–440).
- **Line of sight**: required when healing another creature (line 446); missing LOS sends `"@healing:no_line_of_sight"` (line 447).
- **Target validity**: target must have HEALTH or ACTION damage (line 120), not be dead (line 132), pass `isHealableBy` (line 159), and not be in an arena duel (line 154).
- **Stim pack selection**: searches inventory for a compatible StimPack whose `medicineUseRequired ≤ healing_ability skillMod` (lines 88–106); ranged stimulants additionally check `combat_healing_ability` (line 111) and have their own range (line 111).
- **Mind cost**: base `50`, adjusted by `calculateCostAdjustment(CreatureAttribute::FOCUS, mindCost)` (line 429).
- **XP award**: type `"medical"`, amount = `(healthHealed + actionHealed) × 0.25` (lines 245–258, called at line 304). Healing yourself or pets is explicitly skipped (`targetCreature != creature && !targetCreature->isPet`) (line 304).
- **Cooldown**: `deactivateInjuryTreatment` sets a delay of `round(20 − modSkill/5)` seconds, minimum 4, reduced by any `FOOD_HEAL_RECOVERY` buff (lines 38–51). The player sees `"healing_response:healing_response_58"` ("You are now ready to heal more damage.") when the cooldown ends.
- **System messages**: sender sees `"You heal <name> for X health and Y action damage."`; target (if a player) sees `"<name> heals you for …"` (lines 230–242).

### HealWoundCommand (`HealWoundCommand.h`)

- **Range**: fixed `6` metres (line 26).
- **Line of sight**: required when healing another creature (line 156); same error message as above.
- **Target validity**: target must have wounds in the requested attribute (lines 311–326), not be in combat (**critical** — lines 131–139 block both healer and target if either is in combat), pass `isHealableBy`, and not be in an arena duel.
- **Wound pack selection**: searches inventory for a WoundPack whose attribute matches the target's wounded pool and whose `medicineUseRequired ≤ healing_ability skillMod` (lines 202–218). If no argument is given, it auto-detects the first wounded attribute on the target (lines 289–304).
- **Mind cost**: base `50`, adjusted by FOCUS (line 306).
- **XP award**: type `"medical"`, amount = `woundHealed × 2.5` (lines 61–74, called at line 349). Again, healing yourself or pets is skipped (line 349).
- **Cooldown**: `deactivateWoundTreatment` delay = `round(modSkill × −2/25 + 20)`, minimum 3 seconds, reduced by `FOOD_HEAL_RECOVERY` buff (lines 32–45). Player sees `"healing_response:healing_response_59"`.
- **System messages**: sender sees `"You heal <name> for X <pool> wound damage."`; target (if player) sees `"<name> heals you for …"` (lines 89–101).

### HealStateCommand (`HealStateCommand.h`)

- **Range**: fixed `6` metres (line 27).
- **Line of sight**: required when healing another creature (line 263); same error message.
- **Target validity**: target must have one of the four healable states — STUNNED, DIZZY, BLINDED, INTIMIDATED (lines 28–31), pass `isHealableBy`, and not be in an arena duel. No combat restriction.
- **State pack selection**: searches inventory for a StatePack matching the target's current state (lines 150–151). If no argument is given, it iterates the four healable states and picks the first match (lines 226–241).
- **Mind cost**: base `20`, adjusted by FOCUS (line 253).
- **XP award**: type `"medical"`, fixed amount **50** per successful state removal (lines 56–69, called at line 303). Healing yourself or pets is skipped (line 303).
- **Cooldown**: same formula as HealDamage — `round(20 − modSkill/5)`, minimum 4 seconds, reduced by `FOOD_HEAL_RECOVERY` (lines 36–49). Same message key.
- **System messages**: sender sees `"You remove the <state> state from <name>."`; target (if player) sees `"<name> removes the <state> from you."` (lines 80–92).

### Skill modifiers referenced

| Modifier | Used by | Effect |
|---|---|---|
| `healing_ability` | All three | Minimum medicineUseRequired for stim/wound/state packs (HealDamageCommand.h:88, HealWoundCommand.h:202, HealStateCommand.h:136) |
| `combat_healing_ability` | HealDamage only (ranged stimulants) | Minimum medicineUseRequired for ranged stimulants (HealDamageCommand.h:89, 111) |
| `healing_range` | HealDamage only (ranged stimulants) | Extends range by `(skillMod / 100 × 14)` metres (HealDamageCommand.h:438) |
| `healing_injury_speed` | HealDamage & HealState cooldowns | Reduces cooldown delay (HealDamageCommand.h:36, HealStateCommand.h:35) |
| `healing_wound_speed` | HealWound cooldown | Reduces cooldown delay (HealWoundCommand.h:30) |
| `private_medical_rating` | HealWound only | Must be > 0 unless near a surgical droid or in a hospital/campsite (HealWoundCommand.h:115–128) |

### Timings summary

| Command | Base cooldown | Minimum | Skill that reduces it |
|---|---|---|---|
| HealDamage | `round(20 − modSkill/5)` s | 4 s | `healing_injury_speed` |
| HealWound | `round(modSkill × −2/25 + 20)` s | 3 s | `healing_wound_speed` |
| HealState | `round(20 − modSkill/5)` s | 4 s | `healing_injury_speed` |

All cooldowns are further reduced by any active `FOOD_HEAL_RECOVERY` buff (percentage from the buff's skill modifier value).

## 3. What a bot test should check

### Setup needed first
1. Bot must have the **Medic** discipline trained and the relevant skill mods (`healing_ability`, etc.) set to known values.
2. Bot must carry appropriate pharmaceutical items in inventory: StimPack(s), WoundPack(s), StatePack(s) with `medicineUseRequired ≤ healing_ability`.
3. For HealWound, bot must have `private_medical_rating > 0` **or** be near a surgical droid / inside a hospital or campsite (HealWoundCommand.h:115–128).
4. A willing target player creature must exist with the appropriate condition to heal (HEALTH/ACTION damage, wounds in a specific pool, or one of the four states).

### Observable results to verify

| Test | What to check | Expected outcome |
|---|---|---|
| HealDamage on ally | System messages on both bot and target; target's HEALTH/ACTION HAM bars increase | Bot sees `"You heal <name> for X health and Y action damage."`; target sees `"<name> heals you …"` (HealDamageCommand.h:234–238) |
| HealWound on ally | Target's wound count in the healed pool decreases by `woundHealed`; bot's MIND HAM decreases by mindCost | Bot sees `"You heal <name> for X <pool> wound damage."` (HealWoundCommand.h:93–94) |
| HealState on ally | Target's state bitmask no longer contains the healed state; target's state buff removed | Bot sees `"You remove the <state> state from <name>."` (HealStateCommand.h:84) |
| XP award | Check bot's medical skill progress after each heal | HealDamage: `(healthHealed + actionHealed) × 0.25`; HealWound: `woundHealed × 2.5`; HealState: **50** (HealDamageCommand.h:251, HealWoundCommand.h:67, HealStateCommand.h:62) |
| Cooldown behavior | Attempt to heal again immediately after a successful heal | Should fail with `"You must wait before you can do that."` until cooldown expires (HealDamageCommand.h:38–51, etc.) |
| Self-heal XP | Heal yourself and check medical XP gain | **No** medical XP awarded (HealDamageCommand.h:304, HealWoundCommand.h:349, HealStateCommand.h:303) |
| Pet-heal XP | Heal a pet and check medical XP gain | **No** medical XP awarded (same lines as above) |

### For multiclass bots (Brawler + Medic / Entertainer + Medic)

The bots currently heal themselves first (earning zero XP). To earn medical XP between fights they should:
- Target a **willing ally player creature** who has damage/states to heal.
- Ensure the target is within range and line of sight.
- For HealWound, ensure neither bot nor target is in combat (HealWoundCommand.h:131–139).

## 4. Likely reasons a test sees no effect

1. **Healing yourself or your pet** — XP is explicitly suppressed at lines 304, 349, and 303 of the respective files.
2. **Target out of range** — HealDamage uses dynamic range for ranged stimulants (line 440); HealWound and HealState use fixed 6 m (HealWoundCommand.h:26, HealStateCommand.h:27). Missing `checkDistance` returns `TOOFAR`.
3. **Missing line of sight** — All three commands check LOS for cross-player healing (HealDamageCommand.h:446, HealWoundCommand.h:156, HealStateCommand.h:263) and send `"@healing:no_line_of_sight"`.
4. **Target in combat (HealWound only)** — HealWound blocks the entire operation if either healer or target is in combat (HealWoundCommand.h:131–139). This is a common trap for bots that heal between fights while still flagged as in-combat.
5. **No valid pharmaceutical item** — `findStimPack`/`findWoundPack`/`findStatePack` return `nullptr` if no item matches the skill requirement or attribute, causing early exit with `"No valid medicine found."` (HealDamageCommand.h:145, HealWoundCommand.h:111, HealStateCommand.h:111).
6. **Target not healable** — `isHealableBy` returns false for PvP enemies or arena duel participants (checked at HealDamageCommand.h:159, HealWoundCommand.h:146, HealStateCommand.h:120).
7. **Cooldown active** — The pending task (`injuryTreatment`, `woundTreatment`, `stateTreatment`) blocks re-use until the delay expires (HealDamageCommand.h:38–51, HealWoundCommand.h:29–45, HealStateCommand.h:34–49).
8. **Insufficient mind** — HAM check fails if target mind < adjusted cost (HealDamageCommand.h:149, HealWoundCommand.h:151, HealStateCommand.h:125).

## 5. Open questions

- **Exact XP formula for HealDamage**: The code multiplies `(healthHealed + actionHealed) × 0.25` (HealDamageCommand.h:251), but it is unclear whether `healDamage()` on the target returns the actual amount healed or the stim's base power before clamping to available damage. The files do not show the `CreatureObject::healDamage()` implementation.
- **Group healing for HealState**: HealStateCommand heals a single target only; there is no area-of-effect variant shown. HealDamage has `handleArea` (line 310) but HealWound and HealState do not. Is this intentional or incomplete?
- **`checkForTef` function**: All three files call `checkForTef(creature, targetCreature)` at the end (HealDamageCommand.h:306, HealWoundCommand.h:355, HealStateCommand.h:309), but its definition is not in these headers. What does TEF stand for and what effect does it have?
- **`medicalAnywhere` function**: HealWound references `medicalAnywhere(creature)` at line 116 to bypass the hospital/droid requirement, but its implementation is not in this file. Where is it defined?
- **Battle fatigue messages**: The code calls `playerManager->sendBattleFatigueMessage()` (HealDamageCommand.h:298, HealWoundCommand.h:336, HealStateCommand.h:261), but the battle fatigue system's rules are not described in these files. Does healing reduce or increase battle fatigue?
- **Stim pack power calculation**: `stimPack->calculatePower(creature, targetCreature)` is called but its formula (which skill mods and stats it uses) is not visible here. The StimPack class definition would be needed.


## ChatGPT's review (2026-10-18 02:30)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) and available `src/` snapshots; no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** base medical award requests are round((actual health+action healed)*0.25), round(actual wounds healed*2.5) and 50 for HealState, excluding self/pet at the award sites (HealDamageCommand.h:245-257,462-497; HealWoundCommand.h:61-74,328-349; HealStateCommand.h:56-68,302-303). Current snapshots match these command sources apart from trailing blank lines. Wound healing checks BOTH healer and patient combat status (HealWoundCommand.h:131-139).

**Saluki corrections:** power*1 in HealStateCommand.h:62 does not contradict 50: its caller passes literal 50 (303). The damage formula's power is the sum of returned health/action amounts (497), not stim base potency; CreatureObjectImplementation.cpp:1273-1282 clamps the returned amount to missing usable HAM. Its combat objection is also false: both wound participants are checked.

**Draft corrections/qualifications:**
- All numeric formulas above are rounded base award requests; global XP adjustments/caps in awardExperience can alter the actual gain. Do not assert unrounded quarter XP. Mind healed is excluded even when a ranged pack heals mind (HealDamageCommand.h:476-497).
- Ranged stim cooldown uses healing_range_speed; ordinary stim uses healing_injury_speed (HealDamageCommand.h:30-38). The cooldown table omits this branch.
- HealWound needs positive non-city medical rating OR the gated medicalAnywhere test exception, not a bare 'hospital/droid or rating' alternative (HealWoundCommand.h:115-129; SandboxTestGalaxy.h:18-32,45-49).
- Auto ranged selection uses combat_healing_ability rather than requiring both medicine skills (HealDamageCommand.h:88-112). The table's 'minimum medicineUseRequired' wording reverses the inequality: the player's skill must meet/exceed the pack requirement.
- Insufficient mind is checked on the HEALER, not the target (HealDamageCommand.h:149; HealWoundCommand.h:151; HealStateCommand.h:125).
- These three headers do not establish that ALL medical XP in the game is only from another player. Their award conditions exclude self/pet but are not a general census of all medical commands. Actual multiclass bot behavior is not shown by these headers.

**Not established:** observed XP, a patient's current state and any old test's causal diagnosis. No bot was driven.

**Verdict:** Core XP formulas hold with rounding/downstream modifiers; Saluki's 50-XP and combat objections are false; fix ranged cooldown, healer-mind and environment details.
