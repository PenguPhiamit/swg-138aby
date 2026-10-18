# How an Entertainer Earns Experience in Core3

## 1. Short Answer

Entertainers earn experience through audience interaction, flourishes, and healing effects. Dancing bots maximize XP by having large audiences (≥5), high flourish rates (≥8), and performing in groups. They cannot earn XP for the *Entertainer Healing* tree or *Music* tree boxes, as these require healing battle fatigue or mind wounds of the audience, which dancing bots do not inflict. Experience is calculated using skill mods like `healing_dance_ability` (line 69) and `healing_music_ability` (line 67), with duration adjustments (line 76).

## 2. How It Works

- **Audience Size**: Larger groups (≥5) increase XP (line 28). System messages confirm performance state (line 29).
- **Flourishes**: Each flourish (1–8) triggers XP gains via `doFlourish()` (line 54). Skill mods like `healing_dance_ability` (line 69) scale XP.
- **Healing Effects**: Music entertainers reduce audience battle fatigue via `healing_music_ability` (line 67). Dancing bots do not heal (inferred).
- **Timing**: Flourish cooldowns are `5s - (skillMod/30)` (line 76). Players see messages like `@performance:flourish_not_valid` (line 38) for invalid actions.

## 3. Bot Test Checklist

- **Setup**: Ensure the bot is in a group with ≥5 audience members (line 28). Set high flourish rate (≥8) and active entertaining session (line 26).
- **Check**: Monitor system messages (line 29), XP gains in inventory, and skill mod values (line 67/69). Verify `doFlourish()` triggers (line 54).

## 4. Likely Reasons for No Effect

- Insufficient audience size (line 28) or invalid flourish index (line 37).
- Missing `healing_dance_ability`/`healing_music_ability` skill mods (line 67/69).
- Bot not in an active entertaining session (line 26).

## 5. Open Questions

- What calculates exact XP values for dancing/music? (Missing file: `ExperienceCalculation.cpp`)
- How does healing battle fatigue/mind wounds work for music entertainers? (Missing function: `calculateHealingEffects()`)
