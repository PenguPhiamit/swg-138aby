# Combat States and Posture Report

## 1. Short Answer

Combat states are applied through a roll-based system where the attacker's accuracy chance (from the command's StateEffect) is reduced by the target's defense skill mods (divided by 1.5) and player level, then compared against a random 0-99 roll; success requires the roll to be less than or equal to the result. States like dizzy, stun, blind, intimidate, snare, and root are applied as StateBuffs with specific durations and skill modifiers that affect combat stats. Knockdown and posture changes additionally trigger cooldown delays for posture recovery and can be countered by the combat_equilibrium skill. Each state has distinct system messages, flytexts, and visual effects that both attacker and target see on success or failure.

## 2. How It Works

### Conditions and Skill Mods

The command's StateEffect defines the base chance via `getStateChance()` (CombatManager.cpp:3014). For state-only attacks, the attacker's accuracy skill mod is added to this chance (lines 3015-3017). The target's defense is calculated by summing skill mods from `getDefenderStateDefenseModifiers()`, dividing the total by 1.5, and adding player level for players (lines 3046-3062). A random roll 0-99 must be less than or equal to `(accuracyMod - targetDefense)` for success (lines 3069-3082).

Jedi get a second defense check using `getDefenderJediStateDefenseModifiers()` if the first check passes (lines 3092-3108).

Each state applies specific skill modifiers when the buff is created:
- **Stunned**: -50 to private_melee_defense and private_ranged_defense, plus a PrivateSkillMultiplierBuff setting private_damage_divisor_stun to 20 (lines 2822-2831).
- **Blinded**: -60 to private_attack_accuracy and private_dodge_attack (lines 2851-2852).
- **Intimidated**: -20 to private_melee_defense and private_ranged_defense, plus a PrivateSkillMultiplierBuff setting private_damage_divisor_intimidate to 50 (lines 2877-2886).
- **Dizzy**, **Snared**, and **Rooted**: No skill modifiers are shown in these files.

### Timings

The duration is set by `effect.getStateLength()` for the state effect (line 3115) and passed to StateBuff constructors. Posture change delays are set via `setPostureChangeDelay()` (line 2946). Stand/Kneel/Prone commands have cooldowns of 100ms, 800ms, and 1200ms respectively (StandCommand.h:10, KneelCommand.h:12, ProneCommand.h:12).

### Messages the Player Sees

**On success (target):**
- Flytexts: "go_dizzy", "go_stunned", "go_blind", "go_intimidated", "go_snare", "go_rooted" (lines 2731, 2820, 2848, 2874, 2898, 2911).
- System messages: "@cbt_spam:go_dizzy_single" for dizzy/stun/blind (lines 1013, 1003, 1008); combat spam sent via `sendStateCombatSpam`.
- Visual effects: clienteffect files like "combat_special_defender_stun.cef" (line 1002).

**On success (attacker):**
- For NEXTATTACKDELAY states: "delay_applied_other" with target name and duration (lines 3113-3116).

**On failure (attacker):**
- "@cbt_spam:knockdown_fail" for knockdown, "@cbt_spam:posture_change_fail" for posture changes, "@combat_effects:combat_delay_resist" for delay states (lines 3136, 3141, 3152).
- Flytexts: "intimidated_miss" or "warcry_miss" (lines 3150, 3155).

**On state wear-off (target):**
- Flytexts: "no_dizzy", "no_stunned", "no_blind", "no_intimidated", "no_snare", "no_rooted" (lines 2732, 2821, 2849, 2875, 2899, 2912).
- System messages: "@cbt_spam:no_dizzy_single", "@cbt_spam:no_stunned_single", "@cbt_spam:no_blind_single" (lines 1101, 1093, 1097).

### Posture Recovery

For knockdown and posture changes, combat_equilibrium skill mod is checked; if half of it (capped at 100) exceeds a random roll and target isn't dead or intimidated, posture resets to upright (lines 3163-3172).

## 3. What a Bot Test Should Check

### Setup
- Ensure attacker has appropriate accuracy skills for state-only attacks.
- Target should have varying levels of defense skill mods to test resistance thresholds.
- For knockdown/posture tests, verify target is in an upright posture before the attack.

### Observable Results
- **States**: Check target's state bitmask using `hasState()` or `hasBuff()` for CreatureState::DIZZY, STUNNED, BLINDED, INTIMIDATED, IMMOBILIZED, FROZEN.
- **Posture**: Monitor via `getPosture()` for CreaturePosture::KNOCKEDDOWN or other posture values.
- **Messages**: Verify system messages and flytexts appear on both attacker and target at the correct times.
- **Cooldowns**: Check cooldown timers for posture recovery after knockdown/posture states.
- **Duration**: Confirm states wear off after the expected duration by checking state bitmask over time.

## 4. Likely Reasons a Test Sees No Effect

- Target's defense skill mods plus player level exceed the accuracyMod, causing the roll to fail (line 3082).
- Target has immunity via `hasEffectImmunity()` (line 3024) or an exclusion timer cooldown not yet expired (lines 3036-3039).
- For knockdown/posture states, combat_equilibrium skill mod counters the effect (lines 3163-3172).
- State is already active; buffs renew rather than reapply (e.g., line 2724 for dizzy).
- Target is a Jedi with strong jedi-specific defense modifiers that pass the second check (lines 3092-3108).

## 5. Open Questions

- The exact `getStateChance()` values for each state effect are not in these files; they're likely defined in command data files or scripts.
- The specific defense skill mod names for each state (from `getDefenderStateDefenseModifiers()`) are not listed here.
- How knockdown duration is determined and what posture it sets (CreaturePosture::KNOCKEDDOWN is referenced in StandCommand.h:25 but not its duration).
- The exact mechanics of `queueDizzyFallEvent()` that causes dizzied characters to fall when attempting posture changes.
- Whether snare/root have movement speed modifiers not shown in these files.

## ChatGPT's review (2026-10-18 22:30)

Checked disputed Saluki leads, supplied numbered snapshots and current Core3-dev (9d08e265); current CombatManager lines have shifted by six. Paths below are MMOCoreORB-relative, with unique basenames where unambiguous. Source review only; no gameplay check.

**Holds:** immunity/exclusion gates, defense /1.5, state-only accuracy, the listed buff modifiers and success/fade effects are present. The three posture commands do define MINDELTA 100/800/1200; Saluki's single-citation objection does not invalidate those definitions.

**Corrections:**
- The defense level contribution is calculated player level **minus five**, and accuracy includes stateAccuracyBonus (CombatManager.cpp:2991-3022,3062-3088). The code calls System::random(100), truncates accuracy minus defense to int, and fails on roll > calc; do not describe an assured 0-99 range. Jedi reuse that same roll for each separate Jedi modifier, rather than drawing a second roll (3098-3112).
- effect.getStateLength() at 3121 populates the delay message; actual application calls applyEffect with state strength + bonus (3129). That citation does not establish every buff's duration. Trace the individual command effect before setting test deadlines.
- Equilibrium's actual mod is combat_equillibrium; it is capped at 100 **before** halving (3168-3177), so the stated half-mod capped at 100 formula is wrong.
- Stun/blind target message keys are go_stunned_single/go_blind_single, not go_dizzy_single for all three (CreatureObjectImplementation.cpp:1001-1014). Test only messages that the relevant branch sends; both parties do not receive every flytext/message.

Verdict: Useful state overview after correcting level/bonus arithmetic, equilibrium, duration provenance and message expectations; gameplay untested.
