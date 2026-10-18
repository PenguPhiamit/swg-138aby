# Research topic: Harvesting meat, hide and bone from creatures

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How does harvesting a dead creature work: who may harvest (killer, group), range, which creatures give which resource and how much, skill effects, how often a corpse can be harvested, and what the player sees? List what a test must set up and observe. Context, 17 Oct gate: the harvest bot found no 'ordinary wild prey' for meat near Mos Eisley (BLOCKED: prey level unknown or above 5). Which creatures near a starting city can a novice harvest?

The files in src/ are copies of the server source and, where its path says scenarios/, of the bot test scenario. Every line starts with its line number in the
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
- src/src/server/zone/managers/creature/CreatureManagerImplementation.cpp.lines-900-1075
- src/outputs/tools/bots/scenarios/besh-harvest.py
