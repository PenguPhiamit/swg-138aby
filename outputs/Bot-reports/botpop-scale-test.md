# Server-side population bots (/botpop): first measurements (15 Oct, 13:40-13:51 PDT)

**Answer so far: 250 server-side bots cost the server about 2 cores and 0.26 GB, and need no client processes.** That is milestone 1 of `Documentation-support/server-side-bots.md`, measured in the throttled mode only. In the fleet test (`fleet-scale-test.md`), 100 client bots cost about 2 CPU threads and 0.5 GB in all. Here 250 server-side bots cost about 2 cores and 0.26 GB, and needed no processes, no network sessions and no driver threads. **Not measured yet:** 500 and 1,000 bots, the "all" mode, the 30-minute hold at 1,000 and the class check alongside. The series was stopped at 13:51 so the owner's full-fleet run could have the test galaxy. Everything below is from the two steps that finished.

## What was built (Core3-dev, test galaxy only)

- **Code.** Dev `e6749a9e` (SuiPageData null guard) and `7f58804d` (`/botpop`). All the bot code is in `src/server/zone/managers/botpop/` and is header-only, so it can move into a TortoiseBots fork later. Core3 has three narrow hooks:
  - the command's registration;
  - an observer flag asked by `AiAgent::notifyInsert`/`notifyDissapear` and `SpawnArea::notifyPositionUpdate`;
  - the normal login and logout calls, wrapped in one boundary class (`ClientlessLogin.h`). A headless `ZoneClientSession` could replace it later.
- **Design reference.** Sagiroth's TortoiseBots. No TortoiseBots code is copied.
- **Commands.**
  - `/botpop spawn N [here|mos_eisley|coronet|split] [radius]`, `/botpop despawn [N|all]`, `/botpop status`, `/botpop mode [all|throttled]`.
  - Gated like `TameAnything`: a database ending in `_test` and `Core3.BotPop = true`, then god mode or an account in `Core3.AgentAccounts`.
- **What a bot is.**
  - A transient player character: a CreatureObject with a PlayerObject ghost, no client, no database rows and no account. It is named `Popbot<n>` and gets a random species and plain clothes.
  - It logs in through a client-less copy of `SelectCharacterCallback::connectPlayer`, without the server cap or the per-account online limit.
  - It logs out through the safe-logout steps. `disconnect(false)` on an online character only marks it link-dead for 3 minutes, so that alone wasn't enough.
- **Behaviour.**
  - Every second, the acting bots walk navmesh paths within 200 m of home, sit, emote, or fight back when attacked (`enqueueCommand attack`).
  - Their steps run on the server's worker threads, 64 bots per task.
  - A bot dead for 30 s is replaced.
- **Two modes.**
  - *all*: every bot acts and counts as a player everywhere, as TortoiseBots does by default.
  - *throttled*: bots don't wake AI or trigger creature spawns. Only bots within 128 m of a real player (up to 150), a rotating 50 and any bot that is fighting act.
- **Stats.** Once a minute `core3.log` gets a `[BotPop]` line: mode, online, active, pass time, step time per second and slowest chunk.

## How it was run

- **Galaxy.** The test galaxy on the dev build with `--config 'BotPop=true'`. The 23 squad bots were logged in and idle at Mos Eisley; the Forn crew was waiting for the owner in the escort run. They are the "real players" the throttle looks for, so many Mos Eisley bots counted as near.
- **Driver.** `tools/bots/botpop_scale.py step N split 60 240 throttled`. Half the bots go to Mos Eisley and half to Coronet, then 1 minute of warmup and a 4-minute sample.
- **Sampling.** The driver reuses `load_fleet.py`'s sampler and memory stops: it logs every bot out if WSL MemAvailable falls under 4 GB or commit headroom under 6 GB. Neither came near.
- **Commands and lag.** `/botpop` goes through one squad bot (Tovan, `esk3`), which also times the server's echo of its own chat line.
- **Raw data.** In `Bot-reports/botpop-scale/`. It is local only, because report JSON is git-ignored.

## Results

| Bots online | Took to log in | core3 CPU, cores (avg / max) | core3 memory (avg) | WSL MemAvailable (avg) | Acting bots per pass (avg) | Bot steps, ms per second | Slowest 64-bot chunk | Chat round trip (avg / max) | Errors, warnings |
|---|---|---|---|---|---|---|---|---|---|
| 0 (before the series, after a restart) | n/a | n/a | 4.52 GB | n/a | n/a | n/a | n/a | n/a | n/a |
| **100** (throttled) | 6 s | 1.26 / 1.50 | 4.57 GB | 10.82 GB | 82-87 | 97-112 | 134-206 ms | 80 / 82 ms | 0, 0 |
| **250** (throttled) | 12 s | 2.03 / 2.10 | 4.78 GB | 10.60 GB | 113-125 | 213-261 | 224-330 ms | 80 / 102 ms | 0, 0 |

- **Per bot, from 100 to 250.** About 0.005 cores and 1.4 MB of server memory per extra bot. For comparison, a client bot cost 0.015 cores and 6.5 MB at 100.
- **Logins are fast.** 25 bots a second (the batch size), with no failures.
- **The throttle held.** With 250 online, about 120 acted each pass: about 70 near the squads plus the rotating 50.
- **The rest of the server cost is per player, not per acting bot.**
  - The steps themselves cost 0.1 cores at 100 and 0.25 at 250. core3 rose 0.77 cores between the two, so most of it is not the steps.
  - Likely causes, none of them profiled yet:
    - Core3's own per-player recovery tick, which runs for every online player;
    - in-range updates when bots move past other bots;
    - movement packets that are built for every nearby player and then thrown away for the bots (`sendMessage` drops them, but the copy is made first).
- **Step cost per acting bot grows with crowding:** about 1.2 ms at 100 and about 2 ms at 250. More bots in range means more work per move.
- **No lag seen.** The chat round trip stayed at about 80 ms, the same as in the fleet test, and there were no errors or warnings.
  - The sampler's "lag lines" counted 4 per step, but they are false positives: its pattern matches "slowest" in the `[BotPop]` line itself.
- **The manager's own tick costs under 1 ms a pass** once the bots are spawned. Spawn passes take up to 0.7 s, for 25 logins each.
- **Walking fails often.** About half of the walk attempts found no path (`no path` 70-150 a minute). Those bots wait 5-10 s and try again. Not investigated: the Coronet centre (-130, -4650) may sit off the navmesh, or the outdoor path may be cut where it enters a building.

## Projection (not measured)

- **Throttled, straight line from 250 at 0.005 cores per bot:** core3 would reach about 6 cores at about 1,000 bots.
- **But the cost per bot rose with crowding**, so 1,000 bots in two cities is likely to cost more than the straight line. Spreading them over more cities or planets would help.
- **Memory is not the limit:** 1,000 bots would add about 1.4 GB.
- **The all mode will cost more**, because every bot acts and wakes the creature AI around it. The 1,000-bot hold is what decides this.

## Not done (to finish milestone 1)

1. Throttled 500 and 1,000, and the all mode at 100, 250, 500 and 1,000: `botpop_scale.py step N split 60 240 MODE` for each size, smallest first (switching mode logs every bot out first).
2. The 30-minute hold at 1,000:
   ```bash
   botpop_scale.py step 1000 split 30 1800 throttled
   ```
   Run it with the class check alongside, for example `CLASS_CHECK_PROFESSIONS=combat_marksman squad.py run scenarios/class-check.py --group Aurek --rounds 1 --round-minutes 30 --no-fallback`. The last baseline was 23 WORKS, 1 BLOCKED, 1 RAN.
3. The class check was not run with server bots online. The offline `test_class_check.py` was not re-run either; this work didn't touch it.
4. Follow-ups:
   - the `no path` rate;
   - skip copying movement packets for client-less receivers;
   - a CMake option that builds Core3 without the module. Not added: a global define would rebuild the whole tree.

## Use

```bash
python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/botpop_scale.py status
```

```bash
python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/botpop_scale.py step 100 split 60 240 throttled
```

```bash
python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/botpop_scale.py down
```

Run them inside Debian as swgemu on a test galaxy started with `--dev-server --config 'BotPop=true'`. The squad bot that sends the commands is `BOTPOP_VIA=esk3` by default and must be in `AgentAccounts`.
