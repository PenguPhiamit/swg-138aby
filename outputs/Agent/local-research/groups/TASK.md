# Research topic: Groups: invites, XP split, loot and group missions

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: In Core3, how does a group form (invite, accept, leader, size limit), how is combat experience split between members (range, level differences, the group bonus), how does loot work in a group, and how does the group's level change the missions a member gets (MissionManagerImplementation.cpp around line 1912 uses getGroupLevel)? Answer for a test bot that drives a real client (tools/bots/, AgentControl.cpp): list, in order, every action the client must send (queue command names and arguments, radial menu ids, SUI window answers, or packet names), what the server answers at each step (windows, system message string ids, objects created, credit changes), the checks that refuse the action and their messages, and one pass line a log or a bot can confirm. Quote file:line for each claim.

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
- src/src/server/zone/managers/group/GroupManager.cpp
- src/src/server/zone/objects/group/GroupObjectImplementation.cpp
- src/src/server/zone/managers/player/PlayerManagerImplementation.cpp.lines-1941-2140
