# Fleet-scale test: how many test bots the PC carries (15 Oct, 12:52-13:17 PDT)

**Answer: 100 bots run comfortably.** At 100 bodies, all fighting near Mos Eisley, Theed and Coronet, the PC used about 2 of its 12 CPU threads and about 0.6 GB more WSL memory than with 23 bots. The server logged no lag, and its chat round trip stayed at 81 ms. **Recommended fleet: up to 100 for routine testing.** 150-200 probably fits too, but that was not measured. Projected from the measurements, CPU runs out first, at roughly 350-650 bodies; see "Projected ceiling".

Bots cost no Claude usage. Claude's cost is only the output it reads, so scripts summarise each run.

## How it was run

- 77 plain load bots in `tools/bots/load-groups.json`: 11 groups of 7, named after the Aurebesh letters after Forn (Grek to Qek), split across Tatooine, Naboo and Corellia. They are kept out of `groups.json` so that `squad.py setup/status/run` never starts them by accident.
- `tools/bots/load_fleet.py` logs them in (it creates each character the first time). Each bot fights any ordinary creature within 80 m, or walks 40-60 m legs if none is near. Every 10 s it samples core3, the bodies, WSL `MemAvailable` and Windows commit headroom. It also counts lag-like lines in `core3.log`. One bot times the server's echo of its own chat line every 15 s.
- **No galaxy restart.** The load bots need no `AgentAccounts` entry: they use no `/agentpath`, `/agentskill` or gear. So the Forn escort run (pid 765847, started 12:37) kept running throughout.
- The owner's character was offline: who.json listed only the 23 bots.
- Safety guard: the test stops and logs the load bots out if WSL MemAvailable falls under 4 GB or commit headroom under 6 GB. Neither limit came close.
- Each step: logins, then 3 min of play, then a 5-min sample. Raw data is in `Bot-reports/fleet-scale/` (local only: report JSON is git-ignored).

## Results per step

| Bodies online | core3 CPU, cores (avg / max) | core3 memory | Bodies' CPU, cores (avg / max) | Bodies' memory, RSS (PSS) | WSL MemAvailable, lowest | Commit headroom, lowest | Chat round trip (avg / max) | Lag lines in core3.log | Fights |
|---|---|---|---|---|---|---|---|---|---|
| 23 (squads only, 45 s) | 0.83 / 0.88 | 4.73 GB | 0.10 / 0.11 | 283 MB (83) | 10.66 GB | 14.99 GB | n/a | n/a | n/a |
| 24 (1 load bot, 2 min) | 0.89 / 0.98 | 4.76 GB | 0.12 / 0.15 | 295 MB (87) | 10.30 GB | 13.76 GB | 81 / 81 ms | 0 | n/a |
| **50** (5 min) | 1.22 / 1.34 | 4.83 GB | 0.27 / 0.36 | 631 MB (183) | 10.40 GB | 13.75 GB | 81 / 82 ms | 0 | 286 |
| **98** (5 min) | 1.49 / 1.63 | 4.87 GB | 0.43 / 0.62 | 1.25 GB (363) | 10.06 GB | 11.67 GB | 80 / 82 ms | 0 | 814 |
| 100 (1 min check) | 1.48 / 1.52 | 4.87 GB | 0.48 / 0.55 | 1.28 GB (371) | 10.18 GB | 11.74 GB | 90 / 114 ms | 0 | 152 |
| 23 after takedown (1 min) | 1.39 / 1.44 | 4.87 GB | 0.13 / 0.14 | 285 MB (86) | 10.51 GB | 11.58 GB | n/a | n/a | n/a |

Notes on the table:
- **98, not 100, in the 5-minute step.** The server refused two generated names (`name_declined_developer`). They were renamed, and the 1-minute check then ran with the full 100.
- **The driver** (`load_fleet.py`, one Python thread per bot) used another 0.05 cores at 50 bots and 0.12-0.18 cores at 100.
- **Logins were quick.** 27 new characters came up in 81 s, and 50 more in 82 s (groups log in side by side). There were no login failures apart from the two names.
- **Bodies' memory.** RSS counts shared libraries once per body (12.8 MB each). PSS is the fair share: about 3.7 MB per body. WSL MemAvailable fell about 0.5 GB from 23 to 100 bodies, which is roughly 6.5 MB per extra bot, server growth included.
- **Commit headroom.** It fell from about 14.2 to 11.7 GB during the 100-bot step and stayed there after the takedown. Afterwards the WSL VM (`vmmemWSL`) held 16.4 GB of commit, its whole 16 GB allowance. So the drop was most likely the VM growing to its cap: it was filling page cache with the bodies' logs, and it does not give memory back to Windows quickly. The VM is now at its cap, so more bots cannot take more Windows commit; only Windows programs can.
- **core3 CPU stayed at 1.39 cores** 1-2 minutes after the takedown, against 0.83-0.89 before. That is probably the creatures the fights woke up. Whether it settles back was not checked.
- **The chat round trip is flat at 81 ms** at every size. That looks like a fixed server timer, not load. It did not rise.
- **The server log** had no lag, slow, overload or timeout lines at any step. It had two kinds of errors:
  - About 12 `handleNetStatusRequest` errors per body per minute. These are dev-client noise and appear at every fleet size.
  - `decreaseOnlineCharCount missing account` when the load bots logged out.
- **No free walking was tested.** There was always a creature within 80 m, so the load was approach-and-fight, never a walking leg.

## Projected ceiling: CPU runs out first, at roughly 350-650 bodies

These are straight-line projections, not measurements. Each one takes the cost per load bot at that step, compared with the 23 idle squad bodies (0.93 cores, 10.66 GB available), and asks how many bodies fit before each resource runs out.

| Projected from | CPU per bot (server + body + driver) | Memory per bot (WSL) | CPU: 6 cores busy | CPU: 10 of 12 threads | WSL memory down to the 4 GB guard | Windows commit | Binds first |
|---|---|---|---|---|---|---|---|
| 50-bot step | 0.023 cores (0.014 + 0.006 + 0.002) | 8.1 MB | ~250 bodies | ~425 | ~840 | does not bind | CPU |
| 100-bot step | 0.015 cores (0.009 + 0.004 + 0.002) | 6.5 MB | ~365 bodies | ~635 | ~1,040 | does not bind | CPU |

- **CPU binds first.** The bodies and the driver run on the same 6-core / 12-thread CPU as the server, so the useful limit is the whole fleet's CPU. The server's share alone would reach 6 cores at about 610 bodies (100-bot slope). The 100-bot slope is the better guide: the cost per bot fell from 50 to 100, because the first fighting bots also woke up the creature AI.
- **WSL memory comes second.** The bodies share library pages, so the measured cost is about 6.5 MB per bot. If each body cost its full 12.8 MB RSS plus server growth (about 14.3 MB in all), memory would bind at about 490 bodies, which is still above the CPU estimate.
- **Windows commit does not bind** while WSL stays capped at 16 GB. The WSL VM already holds its whole allowance, so bots inside it cannot take more. Raising the WSL memory limit would make commit count again, one GB of commit per GB of WSL.
- **Why not thousands.** Server-side bot systems that live inside the server process reach thousands of bots on similar PCs. Each of these bots is a full separate client: its own process, network session and copy of the world, plus a driver thread. The server also has to treat each one as a remote player, with packets, position updates and object visibility.
- **Untested limits that may bind before these numbers:**
  - core3's busiest single thread (only total core3 CPU was sampled);
  - login bursts;
  - **client logs.** A fighting body writes about 2 MB a minute to `/var/tmp/swg-bots/<account>/log/core3client.log` (45 MB in 20 minutes). 100 fighting bots write about 12 GB an hour into the WSL disk. C: had 330 GB free. For long 100-bot runs, trim these logs. `load_fleet.py down` now deletes the load bots' logs; the 1.9 GB from this test is already deleted.

## Use

```
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/load_fleet.py step 27 180 300
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/load_fleet.py down
```

`step N` brings the first N load bots online (characters stay in the test galaxy until a restore), plays for WARMUP+SAMPLE seconds and prints the summary. The bots stay online for the next step until `down`.
