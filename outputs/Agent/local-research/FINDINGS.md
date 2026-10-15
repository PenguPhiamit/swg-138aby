# Research findings: what to act on (Claude, 15 Oct 2026, 09:05)

Thirteen mechanics reports were written on 15 Oct by Claude Haiku agents. Opus finished them after a session restart. Each is in `<topic>/report.md` with path:line citations into Core3-dev 90044b8e. They are status **review** in `queue.json`: a report is a careful reading of the source, not a test result, so spot-check a claim before you build on it. Below is what they change for our tests and server, most useful first.

## Our bot scenarios are wrong in places (fix these first)

| Scenario | Problem (report) | Fix |
|---|---|---|
| `cresh-missions.py` | Its 600 m distance filter shuts out **every** destroy mission: the server places them 1000-2000 m away. Its terminal filter lets artisan and statue terminals through. It looks for the lair at the old waypoint, but the lair can land about 256 m away and the waypoint moves. The reward goes to the bank, not cash (missions). | Accept up to about 2300 m. General terminals only. Re-read the waypoint after "Transmission Received". Compare bank credits. Only the owner bot triggers the spawn. |
| `aurek-doctor-buffs.py` | The interior "treatment anchor" isn't needed: **any cell** of the hospital gives the 100 medical rating. It waits 5 s between buffs, but the shared cooldown is about 20 s. It reads error 2 as "lacks healEnhance", but 2 is INVALIDLOCOMOTION (doctor-enhance-wounds). | Walk into any hospital cell. Wait 20 s or for `healing_response_59`. Fix the error-code reading. |
| `dorn-social.py`, `aurek-boss-camp.py` | Dorn checks nothing about entertaining. Aurek's camp watches for 25 s, but a buff needs **60 s or more** of watching and the patron grouped with the performer (or set by /setPerformanceBuffTarget). The buff lands only when watching stops (entertainer-buffs). | Group the patron, watch for 70 s, stop watching, then look for `@healing:performance_enhance_dance_mind_d`. |
| `besh-gather.py` | **The organic survey tool has `toolType = 0`** (`survey_tool_organic.lua:46`, checked), so its list is always empty: flora needs the lumber tool. "liquid" is the chemical tool, not water. Five surveys per tool with no mind check leads to `survey_mind`, which gives `[null, 0]`. A leftover sample loop blocks surveys (survey-sample). | Drop organic or expect []. Label liquid as chemical. Check mind and stop sampling between tools. Report "no list" and "empty list" separately. |
| `class-check.py` cures | NO_EFFECT comes from silent server exits: target over 7 m, a different cell, arena. A missing pack gives a message instead (cure-poison). | ChatGPT's C33b (gather tester and ally, make inventory room) covers this. |

## New test ideas the reports make cheap

- **The Beginning (Phase 1):** Han's five options in order, walk within 40 m of the Falcon at 3863 -4856 (no waypoint), back to Han: +10,000 **cash**, state 1, then 2, then 4 (quests).
- **Crafting with fixed rolls:** the tool's forceCriticalAssembly and forceCriticalExperiment counters and `Core3.Sandbox.CraftSeconds` make results repeatable. The ceiling is weightedSum/1000, and the start value is a fixed curve (crafting, resource-quality). `/resource perfect` gives 1000 stats.
- **HAM:** the regen formula and posture factors (×1.25 kneeling, ×1.75 sitting). Wounds cap current, and armor encumbrance lowers only secondary max (ham).
- **Factions:** joining needs 200 standing. Overt takes 30 s at a recruiter and 5 min in the field. Opposite factions can attack only when both are overt, or covert with a TEF (factions).
- **Travel:** boarding inside the start delay fails with **no message**. This tree's shuttles are landed 600+2 s and away 10 s (travel-shuttles).
- **Resources:** a harvester adds floor(minutes × density × rate) per update. Stacks top out at 999,999 (resources).

## Professions (profession-gaps)

Worst gaps first: Creature Handler (17 pet-order abilities have no server reference under those names), Politician (city specialisations, every try needs a city), Image Designer (no command, and its session has a "Needs research" TODO), Smuggler slicing, Merchant perks, Bio-Engineer DNA and tissue, and Artisan customizeVehicle (a stub). The class check has real results only for marksman, medic and part of scout. Brawler, rifleman and pistol were cut off by owner halts and should be rerun, and 45 of 54 professions are untested. A bot can run entertainer, squad leader, smuggler, the sword and polearm lines, commando, bounty hunter and combat medic today.

## Server-side candidates (owner's call, not changed)

- The organic survey tool never works (toolType 0). Give it a type, or leave it out of the game.
- No Entangle Resistance (ER) attribute exists in Core3's crafting codes (resource-quality).
- `RequestCraftingSessionCommand.h` builds its error string as `@ui_craft@err_no_crafting_tool`, with an `@` where a `:` belongs (crafting).
