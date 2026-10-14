# Setting and optional encounter policy

Owner direction,14 October 2026. This records design intent; no server/client/configuration changed.

## Setting

The owner wants Legends NJO–Legacy, explicitly after the Yuuzhan Vong War and Abeloth, with the Krayt Empire in mind. Pre-CU remains the mechanical foundation, independently of narrative era.

**Provisional era envelope: 130–138 ABY while Krayt's Empire exists; exact year not selected.** [Wookieepedia's Krayt Empire article](https://starwars.fandom.com/wiki/Darth_Krayt%27s_Galactic_Empire) dates it to 130–138 ABY. [Second Imperial Civil War](https://starwars.fandom.com/wiki/Second_Imperial_Civil_War) places its dissolution at 138 ABY. If the owner instead means after Krayt's fall, use 138 ABY onward; do not quietly choose that interpretation. NJO/Fate-era history is background for this later setting rather than one simultaneous time period.

Consequences for design, subject to individual lore checks:
- Hoth's old Echo Base can be ruins, a recovered site or a newly repurposed base. An active original-film garrison is not assumed unchanged a century later.
- New dialogue, recruitable NPCs and local faction identities should fit this later period. Historical characters require lifespan/history checks, archival presentation or an explicitly separate historical scenario.
- Krayt's Empire/One Sith, Fel loyalists and surviving Jedi/Alliance interests are candidate narrative frames, not implemented faction/reputation mappings. Current faction engine labels remain unchanged until a reviewed design/port.
- Old quests/encounters stay available as optional modules to adapt, recontextualize or present as historical scenarios; the era decision is not an instruction to delete them.

## Retain optional encounter modules

Server-added bosses, cave encounters, faction camps/turrets, hubs, rewards and similar gameplay remain candidates. In C12, defer/omit-v1 means **not in the first safe slice**, not rejection of the final feature. Choose one of these paths per encounter:

| Path | When | Record |
|---|---|---|
| Direct compatible adaptation | Code, geometry and permitted dependencies work | Pinned source, changes, tests and required credit |
| Re-engineered implementation | Old API/lifecycle or obsolete mechanics cannot be carried over safely | Original behavior specification and our own implementation/tests |
| Original replacement asset or location | Appearance/geometry unavailable or uncleared | New original/cleared art, stock stand-in or our own placement; retain intended encounter role |
| Optional historical/alternate presentation | Present-day lore conflicts with original story | Explicit scenario context, never an unnoticed continuity blend |
| Blocked pending evidence | Rights, binding or geometry not yet resolved | Exact blocker and feasible alternatives; do not call it impossible |
| Infeasible | Fundamental requirement cannot be met after bounded investigation | Concrete evidence, alternatives attempted and owner-facing explanation |

For Hoth, Rimeclaw can retain an optional boss concept using a verified stock rancor look or later original art. Additional caves can be authored/remapped. Moved outposts can be rebuilt. Vendor/reward systems can be narrowed or reimplemented. Those possibilities are retained without asserting they already work or promising identical donor balance.

Rights restrictions and the existing excluded sources still apply. Optional status neither enables content nor authorizes deployment, downloads, paid asset generation or external contact. Any implementation needs its own source/dependency checks, game tests, cross-review and owner-approved live change.
