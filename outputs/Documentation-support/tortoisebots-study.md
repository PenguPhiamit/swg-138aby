# TortoiseBots: what our bot module can learn from it

Claude, 13 October 2026. Source: [Sagiroth/TortoiseBots](https://github.com/Sagiroth/TortoiseBots) at `bc914eb3`, reference copy in `work/research/Sagiroth_TortoiseBots` (download record D1). Sagiroth gave permission on 13 Oct and is the owner's main inspiration for this project. Credit: `Community-content/CREDITS-and-sources.txt`.

**Rule for this study: ideas and structure, not code.** TortoiseBots is C++ for a WoW 1.12 server; nothing compiles against Core3. Its files carry their own licence lines (AGPL-3.0 core with an attribution term, plus GPL/AGPL donor files), so any file ever ported keeps its notices and the credit. So far nothing is ported.

## How the two projects differ

| | TortoiseBots | Ours |
|---|---|---|
| Where a bot runs | inside the world server, as a headless session | outside it: `core3client --agent-control`, a real client over the real protocol |
| Who drives it | a strategy engine every world tick | Python scenarios (`tools/bots/squad.py`) and, for Kael, an agent over MCP |
| Main goal | a living, populated world for one solo player | first testing the server (B7), then a living world |

Our design tests the server the way a player would: packets, zone transfers and shuttles. That is why TortoiseBots' world-life ideas fit us, but its in-server engine would have to become client-side Python or C++.

## What to take, in order of use to us

1. **A watch page for the test galaxy.** This answers the owner's earlier request to observe the test server. Their optional dashboard is the model (`docs/guides/observability-dashboard.md`):
   - a live 2D map per planet with a marker per bot;
   - a census of the states below, plus an issues list;
   - a bot profile.

   Ours would be a stdlib Python page in WSL on `localhost`. It would read what squad.py already knows (planet, x, y, HAM, posture, current scenario step) and draw it on the planetary map images in the client (`ui_map_<planet>.dds`; Hoth's comes from MTG).
2. **State and issue definitions that are tested and gated.** They count a bot as:
   - **busy:** still, but doing real work;
   - **stalled:** holding a destination but getting nowhere for 45 s;
   - **idle:** nothing happening for 45 s.

   Issues open only past a gate: stuck for 60 s while moving, dead for 2+ minutes, a combat target unreachable for 2+ minutes. Repeated actions are reported as ACTION_LOOP anomalies. We have the same failures (Esk stuck at walls, the leash second hop, Dorn's 11.7 m), but they only surface as a FAIL inside one scenario. Plan: `squad.py` writes `Bot-reports/incidents.csv` (time, bot, kind, planet, x, y, detail) with the same gates. The watch page and `timings.py` then read it.
3. **Failure backoff.** Their `ActionFailureBackoff` stops a bot retrying a failing action, using an exponential timeout. Our scenarios retry blindly: ticket purchases, boarding tries, `walk` tries. One shared helper in squad.py would do (`retry(what, fn, tries, base_s)` that logs each failure to incidents).
4. **One small, tested function per behaviour decision.** They have about 100 `tools/test_*_policy.cpp` files, each testing one decision without a server: which mob to fight, when to leave a zone, when to rest. A `verify_all.sh` runs them in about a second. Ours would be `tools/bots/policies.py` plus `unittest`:
   - which shuttle to take;
   - whether a creature fits the bot's level;
   - when to heal;
   - when a walk counts as stuck.

   GPT can write and review these without the galaxy running.
5. **A table of named places, filled by the bots** (for B6 map new areas). They ship a world table of named locations (52,766 fishing spots alone) and an importer for travel nodes. Ours is `tools/bots/places.json`, still only Mos Eisley's outdoor terminals. Plan:
   - make it one table per planet: terminals (indoors too, via `locate`), trainers, shuttles and starports, cantinas, lairs and spawn areas, and resource spots;
   - fill it with mapping scenarios and the server's `find`;
   - use it to pick targets.

   Hoth would be the first planet mapped from scratch.
6. **Travel rules.** Bots travel the way players do: on foot, by shuttle or by starship. They pick the route once, when they pick the destination. Teleporting is only a rescue when a bot is stuck. Our leash/unstick and the shuttle scenarios already follow this; write it down as a rule for ambient bots.
7. **Purposes chosen by weight, for ambient bots later.** Their pool bots choose the next journey from a weighted table (quest 60, grind 15, camp 10, explore 5), limited to the purposes possible right now and re-rolled when one becomes impossible. The SWG version: missions, hunting, harvesting and surveying, entertaining in cantinas, crafting, exploring. Each purpose is a policy function from item 4.
8. **Scheduling when there are many bots.** Bots owned by a player go first. The others queue by how overdue they are, relative to what their situation tolerates (combat 0.4 s, dead 1 s, otherwise 3 s). No world scans or pathfinding every tick. Each pass logs its own cost. This becomes relevant when squad.py runs dozens of bots, and the cost logging belongs in `timings.py`.
9. **KPIs against a saved baseline.** `pool_kpi_report.py` compares a night's run with a frozen baseline. Ours would be `timings.py summary --baseline` with pass rate per scenario, minutes per check and incidents per hour, run after every dev build to catch regressions.
10. **Their project rules, which match ours.**
    - Bot behaviour defaults to the vision; anything else sits behind an option that is off by default.
    - Orders from the player always beat automation, which matters for the C4 leash and follow.
    - The core never knows a player is a bot. Ours: bot-only helpers stay behind `AgentAccounts`, with no bot checks in core systems.
    - A "when you change X, update doc Y" table.
    - Every task ends with a report: files, tests run and not run, evidence, open issues.
11. **Economy principles, for the owner to decide later.** In TortoiseBots, bots earn their money: no money injection, no seeded auctions, and items on the auction house were really looted or crafted. For SWG, that means ambient bots that do missions, sell loot and craft would put real items into the bazaar.

## What does not transfer

Their class rotations, raid tactics, DBC data, and WoW's auction house and battlegrounds. Their architecture (in-server sessions, the ScriptMgr hooks) doesn't transfer either. Their Go dashboard daemon is a design reference only; ours would be a small Python page.

## Proposed next steps (agreed with ChatGPT's brief; the owner chooses)

ChatGPT's [`tortoisebots-prior-WoW-and-SWG-brief.md`](tortoisebots-prior-WoW-and-SWG-brief.md) reaches the same order independently. It adds two things: snapshots carrying a session epoch and sequence number, so state from an old server run never mixes in; and lessons from the owner's earlier WoW setup. Since 14 Oct, ChatGPT owns the Python bot work (AGENTS.md, "Bot work update"), so:

1. **Incidents and failure backoff** (items 2 and 3): ChatGPT, offline first. Its report triage is a start. Claude runs it on the test galaxy and reviews it.
2. **Policies with unit tests** (item 4): ChatGPT, starting with the travel and stuck decisions the Esk and Cresh runs use.
3. **Named places per planet** (item 5): with the Hoth mapping run. Claude adds any server answers the bots need, for example building cells with a floor point each.
4. **The watch page** (item 1): after 1–3, as a static local report first. A live service needs the owner's OK.
5. The rest (7–9, 11) when ambient bots start.
