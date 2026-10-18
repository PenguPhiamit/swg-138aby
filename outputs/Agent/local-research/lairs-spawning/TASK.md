# Research topic: Lairs: spawn waves, healers, destruction and repopulation

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do creature lairs behave: when they spawn creatures (on damage thresholds, waves), when healers appear, what destroys a lair, what XP and messages that gives, and when a lair or its spawns come back? What does a bot that attacks a lair see, step by step?

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
- src/src/server/zone/managers/creature/LairObserverImplementation.cpp
- src/src/server/zone/managers/creature/LairObserver.idl
- src/src/server/zone/managers/creature/LairSpawn.h
- src/src/server/zone/managers/creature/SpawnLairMobileTask.h
- src/src/server/zone/managers/creature/LairRepopulateTask.h
- src/src/server/zone/managers/creature/LairAggroTask.h
- src/src/server/zone/managers/creature/DynamicSpawnObserverImplementation.cpp
- src/src/server/zone/managers/creature/SpawnObserverImplementation.cpp
