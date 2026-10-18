# Research topic: How a character unlocks Jedi

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: Which Jedi progression is configured (hologrind, the village, or custom), how a character unlocks Jedi under it, how Jedi visibility works, and what the player sees? What could a test check without a real Jedi?

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
- src/bin/scripts/managers/jedi/jedi_manager.lua
- src/bin/scripts/managers/jedi/hologrind_jedi_manager.lua
- src/bin/scripts/managers/jedi/custom_jedi_manager.lua
- src/bin/scripts/managers/jedi/visibility_manager.lua
- src/src/server/zone/managers/jedi/JediManager.cpp
- src/src/server/zone/managers/jedi/JediManager.h
