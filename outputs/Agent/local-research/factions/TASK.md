# Research topic: Factions and the GCW: joining, standing, status, TEF, attackability

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How does a player join and serve a faction (Imperial or Rebel): what the recruiter conversation offers and requires, how covert, overt and on-leave status are set and how long a change takes, what each status allows and risks, how faction points are earned and lost and what caps them, how rank promotion works and what it costs, and the messages the player sees at each step? What should a faction bot test check, and what setup does it need first?

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
- src/bin/scripts/screenplays/gcw/recruiters/recruiterConvoHandler.lua
- src/bin/scripts/screenplays/gcw/recruiters/recruiterScreenplay.lua
- src/src/server/zone/objects/tangible/TangibleObjectImplementation.cpp.lines-176-311
- src/src/server/zone/objects/player/PlayerObjectImplementation.cpp.lines-2155-2322
- src/src/server/zone/objects/creature/CreatureObjectImplementation.cpp.lines-2072-2086
- src/src/server/zone/objects/creature/CreatureObjectImplementation.cpp.lines-4182-4249
