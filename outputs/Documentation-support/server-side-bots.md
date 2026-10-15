# Server-side bots: what 1,000+ bots on the test galaxy would take

15 October 2026 · Claude · research only: no code, server or bot changed. Core3 facts are from `/opt/swg/Core3-dev` at `57a52553` (read-only grep inside WSL). Sources are listed at the end. Numbers marked *estimate* are not measured; the measured ceiling of our current design will be in `Bot-reports/fleet-scale-test.md`.

**Credit.** The comparison point is **Sagiroth's [TortoiseBots](https://github.com/Sagiroth/TortoiseBots)**, a native C++ playerbot framework for Tortoise WoW. It's the owner's main inspiration for our bots. Sagiroth has given the owner permission to be named here, and has no ties to SWG or its community. TortoiseBots facts below come from our archived copy (`work/research/Sagiroth_TortoiseBots`, tag `v2026-10-13`, `bc914eb3`, VERSION `2026-10-13-v6`). No TortoiseBots code is used in this plan; it's a design reference.

## Short answer

- Our bots are real network clients, one `core3client` process each. On this PC (Ryzen 5 5600X, 6 cores, 32 GB) that design tops out in the **low hundreds** (*estimate*), not 1,000.
- TortoiseBots reaches the thousands because each bot is a character inside the world server with **no socket and no client**. A bot costs only its objects and an AI tick on the server's own update loop. Its README puts the range at "100-200 bots" on weak hardware and "2000+" on strong hardware. TortoiseBots ships with every bot fully active; throttling idle bots is an option it offers, and the AzerothCore playerbot module turns it on by default.
- Core3 can do the same. A character with no client session is already mostly safe in Core3: packets to it are dropped, and nearly every client lookup is null-checked. What's missing is a client-less login, a server-side driver and, as a safety valve, an "active bots" budget.
- **Recommendation: a hybrid.** Keep 20–30 real-client bots as the test instrument and add server-side population bots. The first milestone (about 5 days) is 1,000 wandering bots on the test galaxy, measured.

## 1. Why WoW playerbots scale

- **No client.** Each TortoiseBots bot logs in through a standard `WorldSession` "backed by `SessionTransport::Headless`", started with `World::StartHeadlessSession` [1]. There's no process, no network traffic and no packet parsing. The world tick drives the bots (`WorldScript::OnUpdate` → `BotManager`) [1].
  - Its rule is "Core code never knows a `Player` is a bot" [2]. The core has no `IsBot()` branches; everything bot-specific lives in the module behind one host boundary (`host/`).
  - Each character can have only one headless session, but an account can have any number. A human logging in always takes the character back from its bot [1].
  - The AzerothCore playerbot module does the same with a null socket: `new WorldSession(accountId, "", 0x0, nullptr, …)` [5].
- **Strategy and trigger engine.** TortoiseBots builds on the ike3/CMaNGOS playerbot engine (its `ai/playerbot/strategy/`; lineage in `Fable-tortoise/README.md`) [6].
  - Strategies are named behaviour sets, switched separately for combat and non-combat, for example follow or tank assist [7].
  - Each strategy registers triggers (conditions) that queue actions ranked by relevance. The engine's `DoNextAction` runs once per AI tick: it checks the triggers that are due, adds each strategy's default actions, then runs the best action that is possible, falling back to alternatives when one fails [8].
  - A trigger's default check interval is 1 [9], so most conditions are re-checked on every tick. I found no public source for the exact words "very often", but the code matches the claim.
- **How it keeps the cost down.** TortoiseBots' shipped config [3] has these defaults:
  - 500 random bots;
  - `ReactDelay` 100 ms between actions, and `PassiveDelay` 10 s when inactive;
  - at most 100 AI iterations per tick;
  - `DisableActivityPriorities = 1`: "every bot's AI is always fully active". Throttling is opt-in. With it set to 0, bots near a player, in combat, in an instance or grouped stay active, and "alone" bots update at `botActiveAlone` percent. The config's advice for lag is to "reduce the number of online bots".
- The AzerothCore module ships the other way round: `BotActiveAlone = 10` and a smart scale that pauses bots when the server's update time passes 200 ms [10].
- **So** 1.5k–2.5k on a 5600X is plausible mainly because a bot is cheap in-process state with no client. Sleeping the idle bots is a second lever, worth having but not the core of it.

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
| (b) Server-side bots | First slice about 5 days; a living world 3–6 weeks; TortoiseBots-level depth (quests, dungeons, economy) months | Medium-high: runs inside the server, so a bot bug can crash the galaxy | 1,000–2,000 if idle bots are throttled; lower with all active (to measure) |
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
- **No client, or a headless session?** The simple version leaves the owner session null, which Core3 already tolerates. TortoiseBots instead gives each bot a real session object with headless transport, so core code runs unchanged and never needs to know a player is a bot [1][2]. A Core3 headless `ZoneClientSession` would cost more up front, since sessions are managed objects tied to the network layer, and every packet would still be built. In return, it could hand the bot's packets back as events, which scenarios and the class check need (section 4). Start with null and keep the bot code behind one boundary, so that a headless session can replace it later.
- **Input:** everything a client sends must happen directly.
  - Movement: client steps arrive in `DataTransform` callbacks; a bot instead sets its position and updates the zone, as an `AiAgent` does.
  - Commands: `enqueueCommand` already works server-side; `AiAgent` uses it (`AiAgentImplementation.cpp:1518`).
  - Conversations, window answers, mission lists and trades: these are packet callbacks today, so each needs a direct call.
- **The biggest CPU risk is the AI that bots wake up.** An `AiAgent` only thinks while `numberOfPlayersInRange > 0` (`AiAgentImplementation.cpp:2190-2192, 3934`), and a client-less bot still counts as a player. So 1,000 bots spread over the planets would wake most of the world's creatures and NPCs. WoW bots wake the world around them in the same way, which may be why TortoiseBots advises fewer online bots when the server lags. The fix for Core3 is an opt-in budget, as in the playerbot configs: bots don't count as observers, and only bots near a real player plus a rotating few tick at full rate.
- **Driver.** I'd choose the strategy engine (option 2):
  1. **Reuse the behaviour trees** (`ai/bt`: Selector and Sequence nodes; `Checks`, `FollowActions` and `SimpleActions` leaves). Their nodes take an `AiAgent*`, and a player isn't one. Making the bot an `AiAgent` with a ghost would touch many `isPlayerCreature()` branches (906 hits in 412 files), so it's risky.
  2. **A small strategy engine of our own,** in the playerbots style (strategies, then triggers, then ranked actions), ticked by one manager that runs a fixed budget of bots per pass. This is cheaper to bound and to test. TortoiseBots' rule fits here: the engine owns all bot state, and Core3 core code gets no bot branches.

**(c) Hybrid.** The five squads and the crew keep real clients and stay our test instrument. Server bots provide population and background load. Tests that care about what a player sees stay on real clients.

## 4. What changes for our tools

- **squad.py scenarios:** unchanged for the real-client squads. Server bots have no FIFO, no `out.log` and no client events, so scenarios can't drive them as they are. Population bots run their in-server strategy instead. `squad.py` would gain `pop spawn|despawn|status` commands, sent as a god-mode slash command through one real-client admin bot, as `/agentpath`, `/agentgear` and `/agentskill` are today. Driving a server bot from a scenario would need a later in-server command channel that speaks the same verbs (`status`, `look`, `move`, `fight`, `command`, `say`). It would also need its own events, from a headless session (section 3) or from hooks.
- **Class check:** stays on real-client bots. It classifies from the system messages and events the client receives (`{'event': 'system', …}` in `test_class_check.py`), and a server bot receives nothing. That's the right split anyway: the check verifies what a player sees.
- **Tracker (`live_map.py`):** it reads `who.json` and `squad.py`'s `/var/tmp/swg-bots/now/*.json`. Whether server bots appear in `who.json` depends on the bot login registering them like players (to check). At 1,000 markers, the map should show squads one by one and population as counts or a heat map per planet.
- **`load_fleet.py`:** keep its memory stops, and add the server's own lag from `core3.log` as a stop, the way the AzerothCore module's smart scale works.
- **Accounts:** server bots need characters but no passwords. Mark them with a flag or name prefix, so that cleanup, backups and any later public galaxy can leave them out. TortoiseBots keeps its world bots on managed pool accounts, separate from player-owned bots [11], which is a good model.

## 5. Recommendation and first milestone

Build (c), the hybrid, using (b) for the population. Don't spend more on (a) than the fleet test shows to be cheap.

**Milestone 1: 1,000 wandering bots on the test galaxy, measured (about 5 days, Core3-dev only).** The god-mode command only works on a `_test` database, as `TameAnything` does.

1. **Days 1–2:** `/botpop spawn N` and `/botpop despawn`.
   - Create bot characters server-side on bot accounts, with no per-account online limit for them.
   - Log them in through a client-less copy of `connectPlayer`, kept behind one boundary class, and log them out with `disconnect(false)`.
   - Guard `SuiPageData::sendTo`.
2. **Day 3:** a minimal strategy tick from one manager. Bots wander along the navmesh within a radius, sit, emote, and fight back when attacked (`enqueueCommand`).
3. **Day 4:** the active budget, as a setting.
   - All bots active, as TortoiseBots ships, or throttled, where only bots near a real player plus a capped rotating set tick and idle bots don't count toward `numberOfPlayersInRange`.
   - One stats line per minute goes to `core3.log` (online, active, tick ms).
4. **Day 5:** measure 100, 250, 500 and 1,000 bots at Mos Eisley and Coronet with `load_fleet.py`'s sampler, in both budget modes, then write the results next to the fleet test.

**Done when:** 1,000 server bots stay online for 30 minutes on the test galaxy with no crash, the server's RAM growth and lag are recorded for both modes, and the real-client squads still pass the class check. After that come follow and group behaviour (as the crew does now), travel, and the scenario command channel.

## Sources

1. TortoiseBots, `docs/concepts/architecture-invariants.md` (headless sessions, host boundary) and `README.md` (hardware range): <https://github.com/Sagiroth/TortoiseBots>
2. TortoiseBots, `AGENTS.md` ("Core code never knows a `Player` is a bot").
3. TortoiseBots, `ai/playerbot/aiplayerbot.conf.dist.in`: `MinRandomBots`/`MaxRandomBots`, `DisableActivityPriorities`, `ReactDelay`, `PassiveDelay`, `IterationsPerTick`.
4. Earlier studies: `Documentation-support/tortoisebots-study.md` and `tortoisebots-prior-WoW-and-SWG-brief.md`.
5. AzerothCore playerbot module, `src/Bot/PlayerbotMgr.cpp`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/PlayerbotMgr.cpp>
6. CMaNGOS playerbots, the original ike3 engine: <https://github.com/cmangos/playerbots>
7. Strategy, formation and tank-assist commands, a player's guide: <https://briankoponen.com/world-warcraft-single-player-server-bot-control>
8. `src/Bot/Engine/Engine.cpp`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/Engine/Engine.cpp>
9. `src/Bot/Engine/Trigger/Trigger.h`: <https://github.com/liyunfan1223/mod-playerbots/blob/master/src/Bot/Engine/Trigger/Trigger.h>
10. `conf/playerbots.conf.dist` and the module README: <https://github.com/liyunfan1223/mod-playerbots>
11. TortoiseBots, `docs/guides/living-world.md` (managed pool accounts).
