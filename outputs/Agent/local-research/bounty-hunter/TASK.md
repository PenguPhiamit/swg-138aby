# Research topic: Bounty hunting: missions, probe droids, tracking, visibility

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How does bounty hunting work: taking a bounty mission, finding the target with a probe or seeker droid, how player and Jedi visibility grows and decays, what happens when the target is killed, and the messages? The systems baseline marks it partial: what looks unfinished?

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
- src/src/server/zone/objects/mission/BountyMissionObjectiveImplementation.cpp
- src/src/server/zone/objects/mission/BountyMissionObjective.idl
- src/src/server/zone/managers/visibility/VisibilityManager.cpp
- src/src/server/zone/managers/visibility/VisibilityManager.h
- src/src/server/zone/objects/mission/bountyhunter/events/FindTargetTask.h
- src/src/server/zone/objects/mission/bountyhunter/BountyHunterDroid.cpp
- src/src/server/zone/objects/mission/bountyhunter/events/CallArakydTask.h
- src/src/server/zone/objects/mission/bountyhunter/events/BountyHunterTargetTask.h
