# Research topic: Inventory and container limits

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do containers limit what goes in: the inventory's item limit, nested containers, what counts toward the limit, when a transfer is refused and with which message, and whether a reward or loot overflows a full inventory? Bot tests have been blocked by a full inventory (class check, 15 Oct), so: how can a test make room or check space first?

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
- src/src/server/zone/objects/scene/components/ContainerComponent.cpp
- src/src/server/zone/objects/scene/components/ContainerComponent.h
- src/src/server/zone/objects/player/components/PlayerContainerComponent.cpp
- src/src/server/zone/objects/scene/variables/ContainerPermissions.cpp
- src/src/server/zone/objects/creature/commands/TransferItemMiscCommand.h
- src/src/server/zone/objects/creature/commands/TransferItemCommand.h
