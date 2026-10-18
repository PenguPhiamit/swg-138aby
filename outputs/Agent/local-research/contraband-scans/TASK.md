# Research topic: Contraband scans by faction NPCs

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do contraband scans work: which NPCs scan whom and when, what counts as contraband, what happens to a player who carries it or has a faction the scanner hates (fines, attacks, faction loss), and the messages? What could a bot test check?

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
- src/src/server/zone/managers/gcw/sessions/ContrabandScanSessionImplementation.cpp
- src/src/server/zone/managers/gcw/sessions/ContrabandScanSession.idl
- src/src/server/zone/managers/gcw/GCWManagerImplementation.cpp.lines-3432-3438
