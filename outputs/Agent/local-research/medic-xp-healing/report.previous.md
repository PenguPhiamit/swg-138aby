# Research topic: How a medic earns medical experience

## Short answer
In Core3, healing another player awards medical experience (XP) via `HealDamageCommand` (line 304), but self-healing or healing pets gives none. XP type depends on the command used, with caps and cooldowns unspecified. Bots should heal allies first to earn XP between fights.

## How it works
- **Conditions**: Line of sight and range are required (no explicit cap or cooldown in files). Healing another player grants XP, while self-healing/pets do not (HealDamageCommand.h:304).
- **Skill mods**: XP type varies by command (e.g., `healwound` vs. `healdamage`), but files lack details on modifiers.
- **Messages**: Players see "Healed" or "Wound healed" but no XP feedback (inferred from lack of logs).

## Bot test checks
- Ensure healer has line of sight and is within range of the target.
- Verify target has damageable wounds (no explicit inventory check in files).
- Confirm XP is awarded via logs or attribute changes (no system message confirmed).

## Likely reasons for no effect
- Out-of-range or no line of sight.
- Target has no damageable wounds (no explicit check in files).
- Missing skill mods or cooldowns (unspecified in source).

## Open questions
- Missing file: `HealWoundCommand.h` (no details on XP type or caps).
- How do cooldowns or skill mods affect XP awards? (unanswered in provided files).
