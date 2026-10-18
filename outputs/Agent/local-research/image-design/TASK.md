# Research topic: Image Designer sessions

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How does an Image Designer session work: starting it on a target, the window both sides see, what can change (appearance, holo-emotes, stat migration), costs and timers, what cancels it, and the messages? The systems baseline marks it partial: what looks unfinished in these files?

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
- src/src/server/zone/objects/player/sessions/ImageDesignSessionImplementation.cpp
- src/src/server/zone/objects/player/sessions/ImageDesignSession.idl
- src/src/server/zone/managers/skill/imagedesign/ImageDesignManager.cpp
- src/src/server/zone/objects/creature/commands/ImagedesignCommand.h
- src/src/server/zone/objects/player/sessions/ImageDesignData.h
