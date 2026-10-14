# Pre-CU macro bots and bounded squad routines

14 October 2026 — ChatGPT. Research and local source inspection only; no macro executed, bot driven or server/client changed.

## Findings

Players built useful automation by combining targeting, gameplay commands, pauses and repeated macro calls. Movement was part of this: an archived official Bio-Engineer guide, edited March 2005, records selecting a nearby creature, following it, waiting, sampling DNA and looping. The author attributes the suggestion to WildWildMan and says they had not personally used it. This is historical evidence for the technique, not proof it works in our client today. [Archived guide](https://swglostera.com/jedi-archives/star-wars-galaxies-forums/pre-cu-archive/professions/bio-engineer/bio-engineer-guide-and-faq/new-forum-visitors-please-read-this-first.html).

Empire in Flames' own 2017 macro article describes separate targeting, follow, combat, loot and posture loops combined into one routine. It also warns about synchronization failures and generic corpse targeting around others. This is evidence of a pre-CU emulator practice, with server-specific behavior, rather than an authoritative specification for our Core3 build. [EiF article](https://www.empireinflames.net/?p=514).

An early player looping guide, originally posted July 2003 and edited November 2004, explains toolbar-slot recursion; later comments describe named macro recursion and stopping macros. The historical techniques depend on client toolbar state and timing. [Jehosephat's looping guide](https://swgreckoning.org/archive/data/20071216103635/guides_106.html).

Other historical examples rotate through group members to heal, alternate sampling and recovery, and sequence entertainer flourishes. The healing guide was available through search-index text; a full-page fetch failed, so exact syntax needs rechecking before use. [Group healing](https://swgreckoning.org/archive/data/20071216103635/guides_107.html), [sampling](https://swgreckoning.org/archive/data/20071216103635/guides_105.html), [entertainer guide](https://swgreckoning.org/archive/data/20070127014307/index.html).

No verified coordinate-navigation `/moveTo` command was established in this pass. Target-follow, directional movement, pet commands and waypoint creation are distinct operations. Creating a waypoint does not establish that a character will walk to it. Avoid substituting NGE or space macros for ground pre-CU behavior.

## Application to our bots

The local C4d AgentControl.cpp export forwards a command name, target and arguments to the server. It does not demonstrate a full-client macro, toolbar or UI-action interpreter. Its acknowledgement is not proof of gameplay success; this is an older review export, not a fresh current-body audit.

Our current Python squad runner already sequences requests and supports repeated rounds. Scenarios ordinarily finish, leaving characters logged in. Its time limit prevents starting another round; it does not interrupt an already-running round. The halt file is likewise checked between rounds. *(Superseded at 00:52: `run_control.py` now stops at checkpoints inside a round, and Claude confirmed a live halt at 02:14; see bot-control-update-20261014.md.)* Native client `/dump` must not be presented as cancelling this runner or an outstanding body request.

Recommended implementation is small, observable routines rather than initially reproducing the whole client macro engine:

| Routine | Historical pattern | Required checks |
|---|---|---|
| Doctor support | Rotate patients, heal, wait | Agreed group membership, actual injuries, medicine/skill, range/cell, HAM and observed healing |
| Entertainer | Performance plus flourish loop | Action reserve, audience, actual recipient effect; standing still can be expected |
| Survey/sample | Sample, recover, repeat | Tool/resource, posture, inventory delta, HAM and exact popup identity |
| Combat assist | Select, approach, attack, loot | Eligible NPC, certified gear, path arrival, survivability, corpse ownership |
| Travel/objectives | Approach target then interact | Scene/cell, distance reduction, arrival, alternate objective after bounded failure |

Use the body's path helper and measured positions for approach instead of depending on the owner's already-problematic native follow. Start with one short test per routine. Give each an overall deadline, retry cap, failure backoff and explicit terminal result. Check stopping inside long operations where supported; missing cancellation is an engineering gap. Avoid blind default-button responses and manufactured damage/XP loops.

Claude owns execution on the test galaxy. No routine proposed here has been implemented or verified in-game. Current stationary-bot diagnosis remains unverified: Codex's read-only WSL status attempt returned E_ACCESSDENIED, and Claude has been asked to inspect. *(Since 02:35: Claude found the bots idle, not stuck, and `Agent/live/status.md` gives Codex a read-only snapshot every 5 minutes.)*
