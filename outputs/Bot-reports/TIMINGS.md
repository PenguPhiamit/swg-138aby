# How long things take

From `timings.csv` (83 entries, newest 2026-10-13 22:22). Regenerate with `python tools/timings.py summary`.

| Kind | What | Runs | Typical (median) | Fastest | Slowest | Last | Last result |
|---|---|---|---|---|---|---|---|
| build | dev client+server (incremental) | 2 | 14 s | 14 s | 15 s | 2026-10-13 22:22 |  |
| galaxy-start | test galaxy restart + 18-bot setup | 1 | 4.8 min | 4.8 min | 4.8 min | 2026-10-13 22:22 |  |
| scenario | aurek-boss-camp.py:Aurek | 6 | 4.8 min | 2.5 min | 10.3 min | 2026-10-13 19:08 | 5/7 |
| scenario | aurek-doctor-buffs.py:Aurek | 2 | 14 s | 13 s | 15 s | 2026-10-13 20:13 | 3/4 |
| scenario | aurek-hunt.py:Aurek | 7 | 110 s | 4 s | 3.1 min | 2026-10-13 17:51 | 2/4 |
| scenario | besh-gather.py:Besh | 9 | 66 s | 66 s | 2.7 min | 2026-10-13 19:50 | 9/9 |
| scenario | besh-harvest.py:Besh | 2 | 2.9 min | 2.5 min | 3.3 min | 2026-10-13 20:16 | 3/6 |
| scenario | besh-survey.py:Besh | 4 | 94 s | 28 s | 2.2 min | 2026-10-13 17:11 | 8/9 |
| scenario | cresh-missions.py:Cresh | 1 | 8.2 min | 8.2 min | 8.2 min | 2026-10-13 22:01 | 4/6 |
| scenario | cresh-travel.py:Cresh | 16 | 2.8 min | 0 s | 5.0 min | 2026-10-13 20:16 | 10/11 |
| scenario | dorn-social.py:Dorn | 17 | 48 s | 8 s | 70 s | 2026-10-13 22:19 | 9/10 |
| scenario | esk-map-terminals.py:Esk | 2 | 14.9 min | 8.7 min | 21.2 min | 2026-10-13 18:26 | 1/2 |
| scenario | esk-routes.py:Esk | 14 | 3.8 min | 0 s | 4.8 min | 2026-10-13 21:57 | 5/5 |

Time spent waiting on builds, galaxy starts, bot setup and other waits: **5.2 min** over 3 entries.
