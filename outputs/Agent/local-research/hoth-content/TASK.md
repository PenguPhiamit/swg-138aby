# Research topic: Hoth: regions, caves, dens, camps, Echo Base, outposts

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: What does a player find on Hoth (our port; Hoth is open for the friends launch): the regions, the ice caves and creature dens and what spawns there, the camps, Echo Base, the outpost terminals, and the scavenger quartermaster task? What should a bot that visits each place check?

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
- src/bin/scripts/managers/planet/hoth_regions.lua
- src/bin/scripts/screenplays/caves/hoth_ice_caves.lua
- src/bin/scripts/screenplays/poi/hoth_camps.lua
- src/bin/scripts/screenplays/poi/hoth_echo_base.lua
- src/bin/scripts/screenplays/poi/hoth_glacial_rancor_den.lua
- src/bin/scripts/screenplays/poi/hoth_mynock_den.lua
- src/bin/scripts/screenplays/poi/hoth_outpost_terminals.lua
- src/bin/scripts/screenplays/tasks/hoth/scavenger_quartermaster.lua
