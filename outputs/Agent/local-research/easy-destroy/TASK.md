# Research topic: How a group gets an easy, near destroy mission (for the group-pay check)

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: Missions test, group pay: a group needs a destroy mission of difficulty 10 or less within about 2 km of the terminal, and on 17 Oct none of 6 offers at a Tatooine general terminal qualified (the bots are level 1-25 with master combat boxes given by the test kit). From the code: 1) how a destroy mission's difficulty and lair are chosen (player level, group size and level, skill mods, planet spawn lists), with file:line; 2) how its distance from the terminal is chosen; 3) what a group can do to be offered an easy, near lair (a different terminal, fewer or lower-level members, a different city or planet). Say which of these the code shows and which you infer.

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
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-835-1002
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-1850-1991
- src/src/server/zone/managers/mission/DestroyMissionLairObserverImplementation.cpp
