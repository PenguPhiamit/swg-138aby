# Server-side bots: what 1,000+ bots on the test galaxy would take

15 October 2026 · Claude · research only: no code, server or bot changed. Core3 facts are from `/opt/swg/Core3-dev` at `57a52553` (read-only grep inside WSL). Sources are listed at the end. Numbers marked *estimate* are not measured; the measured ceiling of our current design will be in `Bot-reports/fleet-scale-test.md`.

## Short answer

- Our bots are real network clients, one `core3client` process each. On this PC (Ryzen 5 5600X, 6 cores, 32 GB) that design tops out in the **low hundreds** (*estimate*), not 1,000.
- WoW playerbots reach thousands for two reasons. Each bot is a character inside the world server with **no socket and no client**. And **most of them are idle at any moment**: by default only 10% of bots are active when no real player is near.
- Core3 can do both. A character with no client session is already mostly safe in Core3: packets to it are dropped, and nearly every client lookup is null-checked. What's missing is a client-less login, a server-side driver and an "active bots" budget.
- **Recommendation: a hybrid.** Keep 20–30 real-client bots as the test instrument and add server-side population bots. The first milestone (about 5 days) is 1,000 wandering bots on the test galaxy, measured.

## 1. Why WoW playerbots scale

- **No client.** A bot logs in through a `WorldSession` created with a null socket: `new WorldSession(accountId, "", 0x0, nullptr, …)` in the AzerothCore module's `PlayerbotMgr.cpp` [1]. There's no process, no network traffic and no packet parsing; the world server's own update loop ticks the bot.
- **Strategy and trigger engine.** Strategies are named behaviour sets, switched separately for combat and non-combat, for example follow or tank assist [2][3]. Each strategy registers triggers (conditions) that queue actions ranked by relevance. `Engine::DoNextAction` runs once per AI tick: it checks the triggers that are due, adds each strategy's default actions, then runs the best action that is possible, falling back to alternatives when one fails [4]. A trigger's default check interval is 1 [5], so most conditions are re-checked on every tick. I found no public source for the exact words "very often", but the code matches the claim.
- **Throttling is what makes thousands affordable.** The shipped config [6] has these defaults:
  - 500 random bots;
  - `BotActiveAlone = 10`: "how many bots are active when no real players are nearby". At 100 the config notes "Maximum server load";
  - smart scale: when the server's update time passes 200 ms, every bot that isn't forced active is paused;
  - `ReactDelay` 100 ms between actions, `PassiveDelay` 10 s when inactive, and a manager loop every 20 s.
- The README claims "excellent performance, even when running thousands of bots" [7]. That's the project describing itself, not a benchmark. So **1.5k–2.5k on a 5600X is plausible mainly because about 90% of the bots are asleep at any time**, and each one costs only its objects in server memory.

## 2. Our design and its per-bot cost

- **How a bot works now.** Each bot is a `core3client --agent-control` process that speaks the real game protocol to the server. `squad.py` drives it through a FIFO (`/var/tmp/swg-bots/<account>/in`) and reads its events from `out.log`, with a Python thread per bot.
- **Measured, 15 Oct:**
  - 23 bots used 283 MB, about 12 MB and about 1% of a core each;
  - the test galaxy server used 4.4 GB and about 0.6 core;
  - the server holds about 144,000 objects in RAM (`core3.log`, ObjectManager save at 12:51).
- **Scaled to 1,000 bodies (*estimate*):** about 12 GB of RAM and about 10 cores of client CPU alone. The PC has 6 cores and 12 threads, which also run the server, WSL and Windows. The server's per-connection work grows with every body too: a network session, a baseline for every object each client can see, and movement validation. Client CPU runs out first, somewhere in the low hundreds. The fleet test is measuring this ceiling now; its result replaces this estimate. Its safety stops (4 GB free in WSL, 6 GB Windows commit headroom) exist because the PC crashed from memory pressure at 07:31 on 15 Oct.
- **Why keep this design anyway.** A real client exercises the whole path: login, packets, commands, windows, conversations, missions and movement checks. That path is exactly what our tests check. It's the right tool for testing and the wrong tool for population.

## 3. Options for Core3

| Option | Effort | Risk | Ceiling on this PC (*estimate*) |
|---|---|---|---|
| (a) Many bots per client process, or a lighter body | 1–2 weeks of client C++ | Medium: changes our test instrument | 2–3× today; still short of 1,000 |
| (b) Server-side bots | First slice about 5 days; a living world 3–6 weeks; WoW-level depth (quests, raids, economy) months | Medium-high: runs inside the server, so a bot bug can crash the galaxy | 1,000–2,000 if only 10–20% are active at a time; far fewer if all are |
| (c) Hybrid: (b) for population, real clients for tests | (b) plus about 2 days of tooling | Lowest: the test path is unchanged | Same as (b) |

**(a) Many bots per client process, or a lighter body.** Running N sessions in one `core3client` process would load the templates, terrain and navmesh once and share one event loop. That saves memory. I haven't checked whether the client keeps per-session state in singletons, which would decide the effort. Another option is to skip parsing baselines and deltas the bots never read. But the protocol work per session stays on both sides, including the server's network sessions and baselines for every client. So (a) raises the ceiling without changing its shape.

**(b) Server-side bots.** In this tree there's no `PlayerCreature` class. A player is a `CreatureObject` with a `PlayerObject` "ghost", plus an owner `ZoneClientSession` (`getClient()`/`setClient()`, `CreatureObject.idl:1378, 2049`). Here's what Core3 assumes about that client:

- **Outbound messages are already safe.** `CreatureObjectImplementation::sendMessage` deletes the packet when there's no owner (`CreatureObjectImplementation.cpp:3329-3338`). `SceneObject::sendTo` skips baselines when `getClient() == nullptr` (`SceneObjectImplementation.cpp:365`). A client-less player is silent and cheap on the send side.
- **Client lookups:** `getClient()` appears in 46 files.
  - 24 of them are inbound packet handlers (`server/zone/packets/object`), which a server bot never goes through.
  - Most of the rest check for null first: kick and ban (`PlayerManagerImplementation.cpp:726, 4603, 4726`), `cleanupCharacters` (`:6482`), session stats and `notifyOnline`/`notifyOffline` (`PlayerObjectImplementation.cpp:1702, 1912, 1936, 1990`), link-dead logout (`:2397`), factories and hyperspace.
  - One gap found: **`SuiPageData::sendTo` dereferences `getClient()` without a check** (`SuiPageData.cpp:150`). It would crash if a script sent a bot a window that way, so it needs a one-line guard.
- **Login is tied to a client.** `SelectCharacterCallback::connectPlayer` does the work: it checks the server cap, the lock and the per-account online limit, then calls `setClient`, inserts the player into the zone, and calls `setOnline()`, `notifyOnline()` and `chatManager->addPlayer`. The client's `CmdSceneReady` then triggers `notifySceneReady()`. A bot login is a client-less copy of this path. Character creation is client-bound too (`PlayerCreationManager.cpp:341` reads the callback's client), so bots need a server-side create, or characters made once with our existing body.
- **Logout:** a link-dead player is logged out by its session (`ZoneClientSessionImplementation.cpp:208`) and by `doRecovery`. A bot without a session never goes link-dead, so it needs its own logout through `disconnect(false)`.
- **Input:** everything a client sends must happen directly.
  - Movement: client steps arrive in `DataTransform` callbacks; a bot instead sets its position and updates the zone, as an `AiAgent` does.
  - Commands: `enqueueCommand` already works server-side; `AiAgent` uses it (`AiAgentImplementation.cpp:1518`).
  - Conversations, window answers, mission lists and trades: these are packet callbacks today, so each needs a direct call.
- **The real CPU cost is the AI that bots wake up.** An `AiAgent` only thinks while `numberOfPlayersInRange > 0` (`AiAgentImplementation.cpp:2190-2192, 3934`), and a client-less bot still counts as a player. So 1,000 bots spread over the planets would wake most of the world's creatures and NPCs. The fix is the playerbots idea: bots don't count as observers, and only a budgeted active set ticks, chosen as the bots near a real player plus a rotating few.
- **Driver.** I'd choose the strategy engine (option 2):
  1. **Reuse the behaviour trees** (`ai/bt`: Selector and Sequence nodes; `Checks`, `FollowActions` and `SimpleActions` leaves). Their nodes take an `AiAgent*`, and a player isn't one. Making the bot an `AiAgent` with a ghost would touch many `isPlayerCreature()` branches (906 hits in 412 files), so it's risky.
  2. **A small strategy engine of our own,** in the playerbots style (strategies, then triggers, then ranked actions), ticked by one manager that runs a fixed budget of bots per pass. This is cheaper to bound and to test.

**(c) Hybrid.** The five squads and the crew keep real clients and stay our test instrument. Server bots provide population and background load. Tests that care about what a player sees stay on real clients.

## 4. What changes for our tools

- **squad.py scenarios:** unchanged for the real-client squads. Server bots have no FIFO, no `out.log` and no client events, so scenarios can't drive them as they are. Population bots run their in-server strategy instead. `squad.py` would gain `pop spawn|despawn|status` commands, sent as a god-mode slash command through one real-client admin bot, as `/agentpath`, `/agentgear` and `/agentskill` are today. Driving a server bot from a scenario would need a later in-server command channel that speaks the same verbs (`status`, `look`, `move`, `fight`, `command`, `say`). It would also need its own events, because `sendMessage` drops everything sent to these bots.
- **Class check:** stays on real-client bots. It classifies from the system messages and events the client receives (`{'event': 'system', …}` in `test_class_check.py`), and a server bot receives nothing. That's the right split anyway: the check verifies what a player sees.
- **Tracker (`live_map.py`):** it reads `who.json` and `squad.py`'s `/var/tmp/swg-bots/now/*.json`. Whether server bots appear in `who.json` depends on the bot login registering them like players (to check). At 1,000 markers, the map should show squads one by one and population as counts or a heat map per planet.
- **`load_fleet.py`:** keep its memory stops, and add the server's own lag from `core3.log` as a stop, the way playerbots' smart scale works.
- **Accounts:** server bots need characters but no passwords. Mark them with a flag or name prefix, so that cleanup, backups and any later public galaxy can leave them out.

## 5. Recommendation and first milestone

Build (c), the hybrid, using (b) for the population. Don't spend more on (a) than the fleet test shows to be cheap.

**Milestone 1: 1,000 wandering bots on the test galaxy, measured (about 5 days, Core3-dev only).** The god-mode command only works on a `_test` database, as `TameAnything` does.

1. **Days 1–2:** `/botpop spawn N` and `/botpop despawn`.
   - Create bot characters server-side on bot accounts, with no per-account online limit for them.
   - Log them in through a client-less copy of `connectPlayer`, and log them out with `disconnect(false)`.
   - Guard `SuiPageData::sendTo`.
2. **Day 3:** a minimal strategy tick from one manager. Bots wander along the navmesh within a radius, sit, emote, and fight back when attacked (`enqueueCommand`).
3. **Day 4:** the active budget. Bots don't count toward `numberOfPlayersInRange`. Only bots near a real player, plus a capped rotating set, tick. One stats line per minute goes to `core3.log` (online, active, tick ms).
4. **Day 5:** measure 100, 250, 500 and 1,000 bots at Mos Eisley and Coronet with `load_fleet.py`'s sampler, then write the results next to the fleet test.

**Done when:** 1,000 server bots stay online for 30 minutes on the test galaxy with no crash, the server's RAM growth and lag are recorded, and the real-client squads still pass the class check. After that come follow and group behaviour (as the crew does now), travel, and the scenario command channel.

## Sources

1. AzerothCore playerbot module, `src/Bot/PlayerbotMgr.cpp`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/PlayerbotMgr.cpp>
2. CMaNGOS playerbots (the original engine, for classic, TBC and WotLK): <https://github.com/cmangos/playerbots>
3. Strategy, formation and tank-assist commands, a player's guide: <https://briankoponen.com/world-warcraft-single-player-server-bot-control>
4. `src/Bot/Engine/Engine.cpp`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/Engine/Engine.cpp>
5. `src/Bot/Engine/Trigger/Trigger.h`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/Engine/Trigger/Trigger.h>
6. `conf/playerbots.conf.dist`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/conf/playerbots.conf.dist>
7. Module README: <https://github.com/liyunfan1223/mod-playerbots>
