# Kael's public gameplay knowledge sources

Prepared by ChatGPT, 13 October 2026. Covers professions, combat/HAM, surveying and sampling, crafting and experimentation, dungeons, and travel. No sign-in or restricted material is needed.

## How to use this list

Use our guide and observed game events first. For mechanics, use the official SWGEmu Core3 implementation at the pinned upstream base below; our private sandbox includes later local changes. A guide from another emulator can explain the player workflow, but its rewards, balance and custom features may differ. A web guide is never proof that a feature worked here.

Pre-CU means the original skill-box system and Health/Action/Mind pools. CU and NGE guides require separate checks. Archive crawl dates and forum signatures can be later than the actual post: inspect the body and original post date. Do not assume an archived page is pre-CU merely because SWGEmu hosts it.

## Primary implementation references

These are public files in the official [SWGEmu Core3 repository](https://github.com/swgemu/Core3), pinned to our upstream base `403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79`. The corresponding files were checked in the local research checkout. They are technical references, rather than beginner walkthroughs. Reliability: **high for that upstream implementation; compare local changes and test in-game before claiming current behavior**. Era: **SWGEmu pre-CU**, with selectively implemented later content where explicitly present.

1. **Professions and skill training — SkillManager**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/skill/SkillManager.cpp
   - Covers: skill acquisition/removal, skill-tree handling, experience and caps. Use alongside the relevant profession data when investigating a particular skill box.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

2. **Combat and HAM — CombatManager**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/combat/CombatManager.cpp
   - Covers: combat processing, health/action/mind damage, attack restrictions and incapacitation/death processing. Do not substitute this for a live health display: Kael's current tools do not expose HAM.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

3. **Surveying and resource sampling — ResourceManager**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/resource/ResourceManagerImplementation.cpp
   - Covers: survey results, sampling tasks and resource-management behavior. Local resource spawns and sandbox settings can differ from upstream defaults.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

4. **Survey command prerequisites**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/creature/commands/RequestSurveyCommand.h
   - Covers: command validation and dispatch to the survey workflow. Useful for diagnosing a command failure before investigating the UI.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

5. **Sample command prerequisites**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/creature/commands/RequestCoreSampleCommand.h
   - Covers: command validation and dispatch to resource sampling. Inventory, tools and survey/SUI visibility still need agent-body support before a useful crafting test.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

6. **Crafting and experimentation — CraftingManager**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/crafting/CraftingManagerImplementation.cpp
   - Covers: schematic/resource information, crafting calculations and experimentation-related behavior. Follow the relevant schematic and crafting-tool code for an individual recipe.
   - Era/reliability: pre-CU implementation; primary, high within the pinned revision.

7. **Dungeon implementation — the Warren screenplay**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/bin/scripts/screenplays/dungeon/warren/warren.lua
   - Covers: Warren setup, NPCs, progression and scripted interactions; the adjacent components and conversation handlers contain further details.
   - Era/reliability: pre-CU emulator dungeon; primary, high within the pinned revision. Not permission to attempt it with an agent that lacks indoor movement, health and SUI.

8. **Travel timing — planet manager configuration**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/bin/scripts/managers/planet/planet_manager.lua
   - Covers: global shuttle away/landing/landed timing and other planet-manager settings. Destination definitions and fares need their own checks before assuming a particular route is enabled.
   - Era/reliability: pre-CU emulator configuration; primary, high within the pinned revision.

9. **Boarding shuttles — ticket collector**
   - URL: https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/tangible/terminal/ticketcollector/TicketCollectorImplementation.cpp
   - Covers: ticket-collector radial-menu handling and boarding-command dispatch. Ticket purchase and UI support are separate parts of the workflow.
   - Era/reliability: pre-CU emulator implementation; primary, high within the pinned revision.

## Player-facing reading

10. **A Guide to Tailoring — preserved historical player guide**
    - URL: https://www.swgemu.com/archive/scrapbookv51/data/20080108200838/tailor_guide.html
    - Covers: a general crafting walkthrough, assembly/prototypes/manufacturing schematics, experimentation and resource gathering advice, as well as tailoring.
    - Era: historical skill-box-era guide, suitable as pre-CU background; the 2008 archive timestamp is not its original publication date.
    - Reliability: **medium, historical player account**, not SWGEmu developer specifications. Some claims in the guide are explicitly marked unverified. Search-index text was readable on 13 October; direct opening returned an error, so do not describe the whole page as revalidated.

11. **A New Player Guide / random tips for beginners — preserved forum thread**
    - URL: https://www.swgemu.com/archive/scrapbookv51/data/20070210174828/message.html
    - Covers: beginner travel and vehicles, waypoints and JTL starter-pilot advice in late thread replies.
    - Era: original replies shown are from October/November 2004 (pre-CU/JTL); later NGE-era signatures are mixed into the archived rendering.
    - Reliability: **medium for historical first-hand advice**. This is a late page of a discussion, not a complete manual. Search-index text was available; direct opening returned an error on this check.

12. **SWG Infinity's Warren guide — another server's own walkthrough**
    - URL: https://www.swginfinity.com/guides/the-warren
    - Covers: a readable introduction and route for the Warren dungeon on Dantooine.
    - Era: modern pre-CU emulator with server-specific changes, not an NGE walkthrough.
    - Reliability: **high for what Infinity documents about its own server; medium as orientation here**. Our dungeon scripts and observed results take priority. Public page opened successfully on 13 October 2026.

## Lore (owner, 13 Oct)

13. **Wookieepedia, Legends continuity preferred**
    - URL: https://starwars.fandom.com/wiki/ (Legends articles have a "Legends" tab or a `/Legends` page suffix).
    - Use for: **any lore question, for everything it covers** (owner, 13 Oct). That means planets (region, sector, grid square, climate, native species, history), creatures and their behaviour, species, factions and ranks, named characters, places and buildings, ships and vehicles, weapons, armour and items, organisations, events and eras, languages and naming styles. It is the lore source for all new content (Hoth, quests, NPC dialogue, item names and descriptions, loot themes) and for placing planets on our galaxy map.
    - Continuity: prefer **Legends**, the old Expanded Universe that SWG itself belongs to. Use canon only where Legends says nothing, and label it.
    - Rights: Wookieepedia text is **CC BY-SA 3.0**. Read and cite it, but write our own in-game text (descriptions, dialogue, item names); don't paste its text into the game. Images on it are mostly copyrighted stills: don't use them as assets.
    - Reliability: **high for lore, with citations on each article**; not a source for game mechanics.

## Agent-specific limits and next reading

Kael's current safe starting point is outdoor navigation, nearby-object inspection and NPC conversations. The play guide permits only weak-creature combat while HAM is unavailable. SUI, inventory/loot, crafting and indoor movement remain untested or unsupported by the current agent body. Do not mistake this for missing server gameplay.

Maintain separate notebooks for routes and quest conversations. Record object IDs, coordinates, commands, received events and uncertainty in bug reports. For a missing string-table message, first check the command context and public Core3 source; an `@file:key` label alone is not a bug.
