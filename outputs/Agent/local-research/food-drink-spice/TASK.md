# Research topic: Food, drink and spice buffs

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do food, drink and spice work: stomach capacity and how it empties, which buffs they give and for how long, whether buffs stack or replace, spice downers, and the messages when a player is too full or already buffed? What should a test check after eating?

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
- src/src/server/zone/objects/tangible/consumable/ConsumableImplementation.cpp
- src/src/server/zone/objects/tangible/consumable/Consumable.idl
- src/src/server/zone/objects/tangible/consumable/Food.idl
- src/src/server/zone/objects/tangible/consumable/Drink.idl
- src/src/server/zone/objects/creature/commands/EatCommand.h
- src/src/server/zone/objects/creature/buffs/SpiceBuffImplementation.cpp
- src/src/server/zone/objects/creature/buffs/SpiceBuff.idl
- src/src/server/zone/objects/creature/buffs/SpiceDownerBuff.idl
- src/src/server/zone/objects/tangible/consumable/DelayedBuffObserverImplementation.cpp
