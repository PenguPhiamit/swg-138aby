# Research topic: Player cities: founding, citizens, ranks and city services

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: In Core3, how is a player city founded (the city hall deed, the mayor, how many citizens and in what time), how do players join and leave as citizens, how does a city rank up or down, what the city terminal and city taxes do, and which planets allow cities (our test galaxy forbids them on Hoth and Ossus)? Answer for a test bot that drives a real client (tools/bots/, AgentControl.cpp): list, in order, every action the client must send (queue command names and arguments, radial menu ids, SUI window answers, or packet names), what the server answers at each step (windows, system message string ids, objects created, credit changes), the checks that refuse the action and their messages, and one pass line a log or a bot can confirm. Quote file:line for each claim.

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
- src/src/server/zone/managers/city/CityManagerImplementation.cpp
