# Research topic: Droid storage compartment shows Mechanism Quality -999999 (SWGEmu GitHub issue 11)

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: SWGEmu's GitHub issue 11: crafting a Droid Storage Compartment shows 'Mechanism Quality -999999'. From these files: 1) where mechanism_quality is set and shown for a droid component (DroidComponentImplementation.cpp) and for the item storage module; 2) which experimental property or crafting value the storage module's template gives it, and why that value can be missing so a sentinel like -999999 shows; 3) the smallest fix, with file:line. Say which you infer.

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
- src/src/server/zone/objects/tangible/component/droid/DroidComponentImplementation.cpp
- src/src/server/zone/objects/tangible/components/droid/DroidItemStorageModuleDataComponent.cpp
- src/src/server/zone/objects/tangible/components/droid/DroidItemStorageModuleDataComponent.h
- src/bin/scripts/object/tangible/component/droid/item_storage_module_1.lua
