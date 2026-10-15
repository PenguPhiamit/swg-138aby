# Fable-tortoise: TortoiseBots-informed bot policy slice

14 October 2026, Fable. Staged only: nothing applied, nothing run against bots or the server. Everything here is
offline Python under `outputs/Fable-tortoise/`; `tools/bots/` (ChatGPT's slice) is untouched.

Credit: **TortoiseBots by Sagiroth** (https://github.com/Sagiroth/TortoiseBots), GNU AGPL-3.0 with the TortoiseBots
attribution term. Used under the owner's full-use authorisation from the author (relayed 14 Oct). The archive at
`h/work/research/Sagiroth_TortoiseBots/` was read as text and copied from; nothing in it was run or changed.

## 1. What is ported, what is ours, what is flagged

| File here | Origin | Licence / notice | Notes |
|---|---|---|---|
| `tortoise/failure_backoff.py` | **Ported** from `ai/playerbot/strategy/ActionFailureBackoff.h` (classes `ActionFailureBackoff`, `TransitionTracker`; "issue #84") | AGPL-3.0 + attribution term, kept in the module header with the source link. The original file has no per-file notice; the repository `LICENCE.md` governs it. | **Lineage flag:** the original header says its semantics were "ported from the Shyalya runtime reference", i.e. the donor `Shyalya/tortoise-wow` (AGPL-3.0 per `docs/LICENSE_AUDIT.md`; not named in `docs/PROVENANCE.md` for this file). Same licence family as ours, so it is portable; the header says so instead of hiding it. `decide()`, `Retry`, `Impossible` are our additions. |
| `tortoise/test_failure_backoff.py` cases 1-15 | **Ported** from `tools/test_engine_failure_backoff.cpp` | as above (no per-file notice in the original) | Cases 16-20 are ours (decide, Retry with an injected clock, deadline, scene change). |
| `tortoise/incidents.py`, `tortoise/test_incidents.py`, `run_checks.py` | **Ours** | AGPL-3.0 | Informed by the issue-episode rules in `tools/observability/README.md` (minimum age, post-restart blackout, watch -> persistent, resolved history kept, bounded tables). The rules are restated for our report shape; no TortoiseBots code is in these files. |

Not ported, and why: `runtime/ObservabilityEmitter.cpp` and the Go daemon (a WoW core emitter and a web service;
we have no service and the owner has not approved one), `runtime/PlayerLagWindow.h` (derives player wait from
world-tick lengths that Core3 does not report to us; our `steps[].t` round trips are the nearer measure),
`tools/pool_kpi_report.py` (reads WoW logs and a character DB; its idea, a frozen baseline with a label and a
window, is reimplemented in `incidents.py baseline/compare`), `runtime/BotTurnScheduler.h` (not needed while squads
run bounded scenarios), and everything under `ai/playerbot/strategy/{generic,<class>}/` and the Engine, which
`docs/PROVENANCE.md` lists as copied or forward-ported from the donors `Shyalya/tortoise-wow` (AGPL-3.0),
`cmangos/playerbots` (no root licence found; "unresolved") and `mod-playerbots` (GPL-2.0(-or-later)). Those keep
their own licences and the audit (`docs/LICENSE_AUDIT.md`, status Open) is not ours to settle; they are also WoW
engine code with no place in a Python squad harness.

## 2. The six features, mapped onto our framework

| Feature (GPT's brief) | TortoiseBots source | Where it lands for us | State |
|---|---|---|---|
| Epoch + sequence roster snapshots; expire old state instead of mixing server generations | `ObservabilityEmitter.cpp`, observability README ("session epoch = server process start") | `squad.py` already has the per-bot form: `Bot.stale()` compares the body's process start with `newest_server_start()` (the 14 Oct 05:32 lesson). `incidents.py` takes server starts as **epochs**: a restart closes every open episode and a recurrence links back (`continues`). Proposal for ChatGPT's slice: write `server_start` into each report (one field next to `started`) and `epoch`/`seq` into `Agent/live/status.json`, so readers can drop records from another generation without hand-typed `--epoch` times. | design + epoch support staged |
| Bounded action failure backoff with TTL and success reset | `ActionFailureBackoff.h`, `test_engine_failure_backoff.cpp` | `failure_backoff.py`: keyed per (action, source, target, destination, result); base, 2x, 4x, 8x, 16x capped at max; TTL prune; stalest-first eviction; success clears both result variants; scene change clears all (`TransitionTracker` -> `Retry.observe`). `Retry.run(action, source, attempt, ...)` replaces blind `tries` loops; clock and sleep are injected, so scenario dry runs never wait. Hook points: `Bot.walk()` (`tries=3`), ticket purchase and boarding retries, `wait_for` polls. | ported + tested (62 checks) |
| Idle vs working vs stalled vs stuck, not ping | observability README macro states (`busy`/`stalled`/`idle` 45 s, `STUCK` 60 s), `PlayerLagWindow.h` | Next slice, `tortoise/states.py`: a pure classifier over `Bot.status()` polls (position delta, posture, HAM changes, combat states, whether a walk is in progress) with the same gates, unit-tested on recorded `steps`. Combat, healing and dancing in place count as busy, never stuck. `PlayerLagWindow` does not transfer (see above). | design only |
| Budgeted turn scheduler | `BotTurnScheduler.h`, strategy-engine docs | Not needed now: squads run bounded scenarios with `group.parallel`, one body per account. Revisit when ambient bots exist. | deferred |
| Frozen KPI baselines | `pool_kpi_report.py --baseline/--save-baseline` | `incidents.py baseline --save FILE --label TEXT` freezes per (group, scenario): runs, state counts, pooled check pass rate, median seconds, with the window in the file. `compare --baseline FILE` flags pass rate down >= 0.20, median time up >= 1.5x, more error runs, new or missing scenarios; a different label is a warning on every comparison. Stopped runs are excluded. | staged + tested |
| Bounded, evidence-linked incidents; BLOCKED is not a server defect | observability README issue episodes | `incidents.py`: one pass over `Bot-reports/<Group>/<stamp>-<scenario>.json` in time order; each failed check, BLOCKED note, ERROR note and run error is an issue with a **class**: `blocked` (prerequisite or capability named by the scenario), `defect-candidate` (failed check with the body connected), `bot-down` (not logged in, stale, disconnected), `harness` (Python exception), `unclassified`. Episodes open on first sight, refresh per run, close when a run of the same scenario vouches (check passed; note or error gone and the run did not die). Shown after 2 runs, `persistent` from 3; one-offs are listed under `seen_once`; bot-down issues within 300 s after an epoch are suppressed; evidence is the newest 5 (report, check time, detail). `stopped` runs are never evidence. Output: `out/incidents.json` + `out/incidents.md`. | staged + tested (43 checks) |

Existing tools stay as they are: `tools/squad_health_report.py` answers "what did the latest run per group say";
`incidents.py` answers "what keeps happening across runs"; `fallback.py` keeps its own two-round rule.

## 3. Files

- `tortoise/failure_backoff.py`, `tortoise/test_failure_backoff.py` (ported, see above)
- `tortoise/incidents.py`, `tortoise/test_incidents.py` (ours; tests build synthetic reports in a temporary folder)
- `run_checks.py` -> `checks.json`; `out/` holds the run on the real saved reports (`incidents.md/json`,
  `baseline-sample.json`, `compare.md/json`); regenerate any time, Bot-reports is only read

## 4. How to run (offline, from anywhere)

    python -I -B outputs/Fable-tortoise/tortoise/test_failure_backoff.py
    python -I -B outputs/Fable-tortoise/tortoise/test_incidents.py
    python -I -B outputs/Fable-tortoise/tortoise/incidents.py --epoch "2026-10-14 05:32:00" --epoch "..."   # server starts from the board log
    python -I -B outputs/Fable-tortoise/tortoise/incidents.py baseline --save outputs/Fable-tortoise/out/baseline-<label>.json --label "<archive sha, build>" --since "2026-10-14 19:00"
    python -I -B outputs/Fable-tortoise/tortoise/incidents.py compare --baseline <that file> --label "<same label>" --since "<later window>"
    python -I -B outputs/Fable-tortoise/run_checks.py

`squad.py tidy` zips reports older than the newest 20 per group, so a long window should be run before tidying
or pointed at an unzipped copy.

## 5. What the saved reports say (14 Oct 10:11-18:10, no epochs given)

149 reports read, 0 unreadable, 6 stopped runs ignored. 9 open incidents: 5 `blocked` (Aurek doctor-buffs: no
interior treatment anchor, 11 runs; Cresh missions: no same-planet destroy mission with a known waypoint, 11 runs;
Besh fallback-crafting: crafting body API unavailable, 5 runs; Dorn and Esk reach probes: no bazaar / bank terminal
in the local sample; Esk Hoth gameplay: cannot reach the mission terminal) and 4 `defect-candidate` (Besh harvest:
meat/hide/bone "ordinary wild prey found" failing since 14:19 after passing earlier, 3-4 runs; Dorn social: "leash
brings Nima to Dorn after he stops", 11 runs, 12 m off). 8 resolved (Besh prey-level block twice, the earlier
harvest failures at 14:03, the reach-probe blocks that rotated away). 30 one-offs listed. Class split confirms the
brief's point: most of what the squads report is missing prerequisites, not server defects; the two defect
candidates are the ones worth a look on the galaxy.

With the one restart inside the window from `Bot-reports/OVERNIGHT.md` (the entry under 13:27) as `--epoch`
(`out/with-epochs/`): 7 open episodes close at the restart; 4 come back afterwards and link to their predecessor
(`continues`: Aurek treatment anchor, Besh crafting API, Cresh destroy missions, Dorn leash), while the Besh
harvest failures do not link, because the 14:03 run saw them pass after the restart and the 14:19 failures are a
new episode. That is the distinction the epoch rule is for: what survived a restart versus what started after it.

The sample baseline (`out/baseline-sample.json`, 143 non-stopped runs, 24 group/scenario rows) is labelled as a
mixed-build sample on purpose; a real baseline should be frozen from a window on one archive and build.

## 6. Checks

`checks.json` (8/8): the two test modules (62 + 43 checks), the run on the real reports, the baseline round trip
(a window compared with itself flags 0 of 24 rows), and the archive untouched (no files of ours, no `.pyc` under it).

## 7. Open points for Claude and the owner

1. Where should `Retry` go first: `Bot.walk()` in `squad.py` (ChatGPT's slice; I would hand over the call shape) or
   the scenarios' own ticket and boarding loops?
2. Epochs by hand or from the reports: the one-field change to `squad.py` (`server_start`) makes the generations
   automatic. Until then the restart times come from the board log.
3. `states.py` (idle/busy/stalled/stuck classifier) is the next smallest slice; the watch page stays after it and
   needs the owner's OK for anything that is a service.

Rules kept: writes only in this folder; archive read as text, nothing run from it; no bot, server or galaxy
commands; no downloads; no secrets read or printed; AGPL notices and the attribution term kept; credit
"TortoiseBots by Sagiroth" in every ported file and here.
