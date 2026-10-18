# Research topic: Jedi unlock on this galaxy: the village progression

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: The galaxy is set to VILLAGEJEDIPROGRESSION (jedi_manager.lua:14). From these files: 1) how a character becomes force sensitive ('glowing') under the village progression: which skills, badges or other counts, and when it is checked; 2) what happens next (the old man encounter, the Sith shadow, going to the village on Dathomir), with the exact messages and the states or quest flags set at each step; 3) what the holocron does here; 4) how Jedi visibility rises and falls (VisibilityManager.cpp) and when a Jedi shows on bounty terminals; 5) what a bot test can check without a real Jedi (states, flags, messages, a GM tool in village_gm_sui.lua if the files show one). Say which of these the code shows and which you infer.

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
- src/bin/scripts/managers/jedi/village_jedi_manager.lua
- src/bin/scripts/screenplays/village/village_jedi_manager_common.lua
- src/bin/scripts/screenplays/village/village_jedi_manager_holocron.lua
- src/bin/scripts/screenplays/village/intro/glowing.lua
- src/bin/scripts/screenplays/village/intro/fs_intro.lua
- src/bin/scripts/screenplays/village/intro/old_man_intro_encounter.lua
- src/bin/scripts/screenplays/village/intro/go_to_dathomir.lua
- src/src/server/zone/managers/visibility/VisibilityManager.cpp
- src/bin/scripts/managers/jedi/visibility_manager.lua
