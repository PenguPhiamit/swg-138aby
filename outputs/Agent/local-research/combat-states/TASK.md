# Research topic: Combat states and posture: dizzy, knockdown, stun, blind, intimidate, snare, root

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do combat states and posture changes work: what chance an attack has to apply dizzy, knockdown, stun, blind, intimidate, snare or root, which defenses and skill mods resist each, how long each lasts, what posture change delays apply, and which system messages and flytexts the attacker and the target see? What can a bot test observe to confirm a state landed and wore off?

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
- src/src/server/zone/managers/combat/CombatManager.cpp.lines-1702-1755
- src/src/server/zone/managers/combat/CombatManager.cpp.lines-2975-3191
- src/src/server/zone/objects/creature/CreatureObjectImplementation.cpp.lines-931-1146
- src/src/server/zone/objects/creature/CreatureObjectImplementation.cpp.lines-1781-1797
- src/src/server/zone/objects/creature/CreatureObjectImplementation.cpp.lines-2721-2950
- src/src/server/zone/objects/creature/commands/KnockdownAttackCommand.h
- src/src/server/zone/objects/creature/commands/DizzyAttackCommand.h
- src/src/server/zone/objects/creature/commands/StunAttackCommand.h
- src/src/server/zone/objects/creature/commands/Intimidate1Command.h
- src/src/server/zone/objects/creature/commands/KneelCommand.h
- src/src/server/zone/objects/creature/commands/ProneCommand.h
- src/src/server/zone/objects/creature/commands/StandCommand.h
