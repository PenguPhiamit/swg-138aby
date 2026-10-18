# Research topic: Tells, mail, friends and ignore

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: How do tells, in-game mail, the friends list and the ignore list work: sending a tell to an offline or ignored player, sending mail (to offline players, size limits), what /findfriend does, and the messages for each? What should a two-bot test check?

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
- src/src/server/chat/ChatManagerImplementation.cpp.lines-1462-1563
- src/src/server/chat/ChatManagerImplementation.cpp.lines-1783-2052
- src/src/server/chat/PersistentMessage.idl
- src/src/server/chat/PersistentMessageImplementation.cpp
- src/src/server/zone/objects/creature/commands/AddFriendCommand.h
- src/src/server/zone/objects/creature/commands/FindFriendCommand.h
- src/src/server/zone/objects/creature/commands/RemoveFriendCommand.h
- src/src/server/zone/objects/creature/commands/AddIgnoreCommand.h
- src/src/server/zone/objects/creature/commands/RemoveIgnoreCommand.h
