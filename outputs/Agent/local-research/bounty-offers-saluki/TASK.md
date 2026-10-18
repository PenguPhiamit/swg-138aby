# Research topic: The same bounty question, answered by Saluki (model comparison)

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: Missions test (functional-test-plan.md section 11), 17 Oct run 3: the bot Brask, given the Novice Bounty Hunter box, stood within 6 m of a bounty terminal on Tatooine and listed missions 30 times, and no bounty mission was offered (the bot's helper is bounty() in missions.py). Another hunter, Ressa, already holds one far bounty. From the code: 1) every check between a mission-list request at a bounty terminal and a bounty mission appearing in the list (skills, skill mods, faction, level, planet, the potential player-bounty targets, how many of the bag's slots get a bounty, any limit of one bounty per hunter), with file:line and the exact message if one is sent; 2) what an NPC bounty target needs to exist (templates, planet, distance) and what makes randomizeGenericBountyMission leave a slot empty; 3) the most likely reason a novice hunter gets an empty list, and what the bot must do or have to get one offer. Say which of these the code shows and which you infer.

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
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-150-235
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-619-645
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-762-786
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-1078-1275
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-1992-2007
- src/src/server/zone/managers/mission/MissionManagerImplementation.cpp.lines-2107-2200
- src/outputs/tools/bots/missions.py.lines-960-1060
