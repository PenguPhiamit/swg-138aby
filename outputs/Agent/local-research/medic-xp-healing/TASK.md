# Research topic: How a medic earns medical experience

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: In Core3, exactly when does healing award medical experience, and how much? Cover healdamage, healwound and healstate: healing yourself or a pet gives none (HealDamageCommand.h:304 says so); what counts for healing another player (range, line of sight, the amount healed, any cap or cooldown, groups), and which XP type each awards. The multiclass bots (Brawler + Medic, Entertainer + Medic) heal themselves first: what should they do instead to earn medical XP between fights?

The files in src/ are copies of the server source. Every line starts with its line number in the
original file ("  919| ..."); cite those numbers.

Write report.md with these sections:
1. Short answer (3-6 sentences).
2. How it works: conditions, skill mods and numbers, timings, and the messages the player sees. Cite file:line for
   every claim.
3. What a bot test should check: observable results (system messages, states, inventory, attributes) and the setup
   it needs first.
4. Likely reasons a test sees no effect.
5. Open questions: what these files don't answer (name the missing file or function if you can).

Rules: use only what the files show. Mark anything you infer rather than read with "(inferred)". Never invent function
names, numbers or file names. Plain English; no code excerpt longer than 3 lines.

Files:
- src/src/server/zone/objects/creature/commands/HealDamageCommand.h
- src/src/server/zone/objects/creature/commands/HealWoundCommand.h
- src/src/server/zone/objects/creature/commands/HealStateCommand.h
