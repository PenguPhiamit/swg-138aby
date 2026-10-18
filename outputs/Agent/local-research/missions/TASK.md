# Research topic: Mission terminals and mission completion

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How are missions generated and completed: which terminal gives which mission types, how difficulty, distance and reward are chosen, how many missions a player may hold, and what completes or fails each type (destroy, deliver, survey, entertainer, crafting)? Compare with cresh-missions.py and list the checks a mission test should make.

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
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp
- src/outputs/tools/bots/scenarios/cresh-missions.py
