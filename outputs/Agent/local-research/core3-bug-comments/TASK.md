# Research topic: Known Core3 bugs, from the source's own comments

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: The file core3-bug-comments-2026-10-18.tsv lists the 283 comments in our Core3 source (upstream SWGEmu as of 1 Oct 2026, 403893d9) that admit a bug or a gap: FIXME, TODO, HACK, broken, crash, exploit, workaround. Each line is 'file:line<TAB>marker<TAB>comment'. 1) Group them by game system (combat, crafting, missions, housing, chat, space, AI, loot, ...). 2) Pick the ones a player would notice on a pre-CU server: wrong results, crashes, exploits, or a feature that is missing or half done. Leave out code tidying, logging and refactor notes. 3) For each pick, give the file:line, what the comment says is wrong, and how a player would see it (inferred unless the comment says so). 4) Rank the top 20 by how much players would value a fix. Say which you infer.

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
- src/outputs/work/known-bugs/core3-bug-comments-2026-10-18.tsv
