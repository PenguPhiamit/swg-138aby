# Checkout churn, 16 Oct 2026

Survey by Claude, read-only, run after 00:35 on 16 Oct. Nothing below was changed, staged or committed except this file.

`git status --short -- .` in `outputs/` shows 50 tracked changes (30 deleted and 1 modified in `Bot-reports/runs/`, 19 modified elsewhere) and 155 untracked entries (234 files once folders are expanded).

| Folder or file | State | What it is | Last commit | Kind | Suggestion |
|---|---|---|---|---|---|
| Bot-reports/runs/ | 30 deleted, 1 modified, 70 untracked | squad.py round logs (`.txt`) and round summaries (`-summary.md`) | 8ac7857 (Claude) | Generated; the deletions are rotation | Ignore `runs/*.txt` and `runs/*-summary.md` (note 2). No restore needed (note 1). |
| Bot-reports/ logs and reports | 9 modified; untracked `Forn/LOG.md` and 4 `Aurek/class-check-*-console.txt` | Per-round bot logs, timings, gate output, fallback coverage | 8ac7857 (Claude); GATE.md 7674330 (Claude) | Generated | Commit one bot-report snapshot when the owner wants it; ignore the console dumps. |
| Bot-reports/launch-sim/ | 11 untracked | Launch-sim numbers and reports, plus 8 raw host logs (`host-*.jsonl`, 1.5 MB, last written 00:35 on 16 Oct) | b589da3 (Claude) for tracked reports | Mixed: reports to keep, raw logs to ignore, two C47 files (ChatGPT) | Claude commits its reports after run 7. Ignore `*.jsonl`. `report-tools.md` and `numbers-run6-early.md` wait for C47. |
| tools/bots/ | 2 modified (botpop_analysis.py +251, botpop_report.py +82); 1 untracked `test_botpop_reports.py` | Launch-sim report tools (C47) | 0844389, 9f57c11 (Claude) | Work in progress: edited 23:55 on 15 Oct, after ChatGPT claimed C47 at 23:50 | ChatGPT commits its own files after review. Nobody else. |
| SWG-handoff.md | 4 lines added | ChatGPT's C47 claim | 486be13 (ChatGPT) | Work in progress | Commit with the C47 change. |
| Agent/gpt-queue.json | modified, 725 lines | Relay task queue, rewritten by the relay (00:31 on 16 Oct) | 619f952 (Claude) | Runtime state | Leave it. Untracking it needs an owner decision. |
| Agent/local-research/queue.json, LOG.md | modified | Local-model job queue, live (00:32 on 16 Oct) | 30eb366, fc2b964 (Claude) | Runtime state | Leave until the jobs finish. |
| Agent/proc-check.md | modified | Process-check output, rewritten on each check | 8ac7857 (Claude) | Generated | Ignore. |
| Agent/local-research/bot-gap-list/, proofread-player-text/ | 4 untracked (2 `report.md`, 2 `map-output.txt`) | Local-model reports | 30eb366 (Claude), queue commit | Finished output; .gitignore says these two files are kept | Claude commits the four files. |
| Agent/relay/ | 30 untracked (12 `.md` reports, 18 `.prompt.txt` briefs) | Relay briefs and ChatGPT's returned reports, 14-15 Oct | 8ac7857 (Claude) for earlier files | `.md` files are records the board cites; `.prompt.txt` files are generated inputs | Commit the 12 `.md` files. Ignore `*.prompt.txt`. |
| Agent/notes/, tools/agents/roadmap_digest.py | 3 untracked (12:46 to 12:55 on 15 Oct) | Roadmap digest tool, its prompt and output | none | Work in progress, never committed | Its author commits the tool. The digest output can be ignored. |
| Documentation-support/review-C4f/ | C4f-review.md modified (+6, "Reviewed by ChatGPT"); `check-fixes.py` and `fixed-results.json` untracked (14 Oct) | ChatGPT's C4 follow-up review and its check script | 8ac7857 (Claude) | Work in progress | ChatGPT commits with a pathspec. |
| Documentation-support/ (other) | `class-check-results.md` untracked (15 Oct); five `C26-*-commit.txt` (79 to 423 bytes, untracked, 14 Oct) | Class-check results; commit-message drafts for C26 (C26 is already in dev, 464a767) | none | Results: work in progress. Drafts: scratch | The author commits the results. Delete the five drafts once their author confirms. |
| Fable-hoth-guide/hoth-first-session.md; Fable-ossus/o2/README.md | 2 modified (+6/-1, 1 line) | Doc edits in the Fable workstream (14 Oct) | dc0ed5d, fd16069 (Claude) | Work in progress | The Fable author commits. |
| Fable-species/s5 and s6; Fable-ossus/o5; Fable-resources3; Fable-hoth-mapnames; Fable-hoth-batchB; Local-model-ossus-fauna/work/ | 94 untracked (s5 20, s6 30, o5 10, resources3 16, hoth-mapnames 13, hoth-batchB 1, Local-model 4) | Scratch scripts (`q*.sh`, `g*.py`, `gitcheck*.sh`), copies of Core3 files under `orig/` and `new/`, Ossus terrain and snapshot copies, and the Species 6 folder in progress (README, tools, patch, provenance) | d0ecd1e (Claude) for the parent folders | Mostly scratch and duplicates. s6 is a deliverable in progress. | Add `outputs/**/work/*` with `!outputs/**/work/*.py` (note 3). The Fable author commits s6 when it is done. |
| Local-content/old-client-local_planets.tre.* | 7 untracked, about 26 MB | Seven copies of the stock client's local_planets archive, each with a different hash (14 Oct 19:07 to 15 Oct 04:35) | none | Stock game files, which AGENTS.md excludes | Do not commit. Add `outputs/Local-content/*.tre*` to .gitignore (note 3). The owner decides whether to delete them. |
| SWG-roadmap-2026-10-15.html | 1 untracked, 52 KB | Rendered roadmap, "state as of 15 October 2026" (04:55 on 15 Oct) | none | Generated view | Commit with the next roadmap update if the owner wants dated snapshots. Otherwise ignore. Author not identified. |

## Notes

1. **The 30 deleted files.** They are the `Bot-reports/runs/20261013-*` and `20261014-*` `-summary.md` files that were tracked in 8ac7857. `tools/bots/squad.py` rotates run files: it keeps 30 loose (`KEEP_RUNS = 30`, line 823) and moves older ones into `runs/archive-202610.zip`, created 08:44 on 15 Oct (lines 830 to 841), then deletes the loose copies. I checked that the zip lists all 30 names. HEAD also holds them. The zip is ignored by `*.zip` and exists only on this PC. Nothing needs restoring.
2. **Run churn.** `20261014-060323.txt` is still growing (+358 lines since 8ac7857). The 8ac7857 commit message says per-run churn stays local, yet these files were committed. Ignoring `runs/*.txt` and `runs/*-summary.md` would match that policy. Adding a rule does not untrack files that are already tracked. Untracking them (`git rm --cached`) is an owner decision, not done here.
3. **.gitignore gaps.** (a) `outputs/Local-content/*.tre*`: `*.tre` does not match names ending in `.tre.<hash>`, so a plain `git add` would take in stock client archives. (b) `outputs/Bot-reports/runs/*.txt` and `*-summary.md`. (c) `outputs/Bot-reports/launch-sim/*.jsonl`. (d) `outputs/**/work/*` with `!outputs/**/work/*.py`: the existing `work/*` rule (.gitignore line 50) is anchored to the repo root and does not reach the nested `work/` folders. Already-tracked files under `work/` (134 in outputs) stay tracked.
4. **Rights and secrets.** The Ossus terrain copies (`ossus_academy.tga` and the others, in four untracked folders) are byte-identical (md5 319ead4d) to `Fable-ossus/o4/staged/client/terrain/ossus_academy.tga`, which is tracked. They are copies of our own art. The `.tre` copies are stock files and must not be committed. A keyword search (password, api key, secret, bearer, sk-) over modified and untracked text files found no credential values. The hits were the task name "sk-fallback" and policy wording. Code files and `.json`/`.jsonl` files were skipped in that search. A 40-character hex search also found nothing.
5. **Board log.** `SWG-handoff.md` has 4 entries under `## Log`, so no entry was moved. Its uncommitted C47 claim belongs to ChatGPT (note in the table).
6. **Not covered.** Root-level changes (`work/`, `output/`, `tmp/`) sit outside `outputs/` and were not reviewed.

## C51 applied ? 16 Oct 2026, 08:48 Pacific (ChatGPT)

Owner approval: board answers of 16 Oct 05:40, morning-sheet items 1?3. Added targeted rules for suffixed Local-content TREs, raw launch JSONL, runs/*.txt and *-summary.md, bot console dumps, proc-check.md, relay prompts, nested work copies, rendered roadmap HTML and roadmap-digest.md. Top-level Python **and shell** scripts in nested work folders stay visible; copied orig/new/local_planets trees stay ignored, including Python files inside those trees. Authored reports, digest source/prompt, local-model reports and map outputs remain visible. Existing tracked work copies are unchanged.

Used `git rm --cached` on **45 paths**: 30 already-rotated summaries, 14 run text files (including one console dump), and Agent/proc-check.md. This changes the index only: all 15 existing files retained their SHA-256 hashes; the 30 missing loose summaries were not restored. Verified every summary name in archive-202610.zip and every prior version in HEAD. No history rewrite, deletion, build, server access or bot action. Both queues stay tracked. Per-group LOG.md, GATE.md, OVERNIGHT.md, fallback-coverage.md and timings.csv remain tracked pending an explicit snapshot/state policy; this task only untracks the approved rotating run directory and generated process check.

Validation: 23 positive/negative `git check-ignore --no-index` checks cover every new category plus report/script/queue exceptions. No gameplay changes; no in-game test required. The original survey above is retained as a dated baseline, not current status.

### Remaining finished authored work ? commit separately by its author

Paths below are relative to `outputs/`. These are a commit inventory, not files staged by C51. Each author should review and use explicit paths. Prior tool changes from C47 are already committed in 3639bb2; do not recommit them.

**ChatGPT:**

- `Documentation-support/review-C4f/C4f-review.md` (the six-line signed follow-up), `Documentation-support/review-C4f/check-fixes.py`, `Documentation-support/review-C4f/fixed-results.json`: completed offline follow-up review; gameplay remains open.
- `Bot-reports/launch-sim/report-tools.md`, `Bot-reports/launch-sim/numbers-run6-early.md`: C47 authored usage notes and explicitly bounded early sample; retain sample limits.
- Returned relay records listed below are completed ChatGPT turn records, even where the underlying task still has a gameplay/review gate. Preserve failures/limitations; their authored implementation reports are already committed separately.
- `Agent/relay/20261014-1001-c21-resource-census.md`
- `Agent/relay/20261014-1301-c22-hoth-review.md`
- `Agent/relay/20261015-0113-c32-agentgear-profession.md`
- `Agent/relay/20261015-0132-c30-ossus-fauna-server.md`
- `Agent/relay/20261015-0701-c34r-agentgear-kits-review.md`
- `Agent/relay/20261015-0801-c24b-r2-coverage-review.md`
- `Agent/relay/20261015-1229-c39-dev-review-1015.md`
- `Agent/relay/20261015-1241-c42-fable-return-prep.md`
- `Agent/relay/20261015-1246-c40-roof-ledge-pathing.md`
- `Agent/relay/20261015-1735-c43-bf2-battles-ai-design.md`
- `Agent/relay/20261015-2245-c44-launch-sim-review.md`
- `Agent/relay/20261015-2340-c45-mission-recipe-fix.md`
- `Agent/relay/20261016-0348-c46-discord-feed.md`
- `Agent/relay/20261016-0358-c48-morning-sheet.md`

**Claude:**

- `tools/agents/roadmap_digest.py` and `Agent/notes/roadmap-digest-prompt.md`: tool and source prompt identify Claude, 15 Oct. Review the now-retired helper-model instructions before committing; the rendered digest is ignored.
- `Agent/local-research/bot-gap-list/report.md`, `Agent/local-research/bot-gap-list/map-output.txt`, `Agent/local-research/proofread-player-text/report.md`, `Agent/local-research/proofread-player-text/map-output.txt`: finished local-model outputs from the original survey, retained for Claude's review and explicit-path commit. Machine-produced claims are not verified facts.
- `Documentation-support/class-check-results.md`: Claude-run C33 results; commit only after reconciling its pending rows with actual run evidence. A saved results document does not close the remaining class campaign.
- `Bot-reports/launch-sim/numbers.md`: old generated report snapshot, 15 Oct 17:09?17:27. Claude owns the launch report stream; decide whether this named checkpoint is useful before committing it. Do not treat it as current results.

### Pending, generated and unfinished work ? leave in place

- **ChatGPT C50, still claimed on the board:** `Documentation-support/C50-source-probe.json`; local-model review inputs/outputs under `Agent/local-research/{medic-xp-healing,scout-xp-sources,entertainer-xp-sources}/` (`TASK.md`, `agent-output.txt`, `report.md` in each). Not marked finished by C51; commit only with the completed source audit. Local-model output provenance stays explicit.
- **Runtime state, not finished authored work:** `Agent/gpt-queue.json`, `Agent/local-research/queue.json`, `Agent/local-research/LOG.md`, `Agent/relay/RUNNING`; generated `Bot-reports/{Aurek,Besh,Cresh,Dorn,Esk,Forn}/LOG.md`, `Bot-reports/GATE.md`, `Bot-reports/OVERNIGHT.md`, `Bot-reports/fallback-coverage.md`, `Bot-reports/timings.csv`. Keep queues tracked; choose one named report snapshot separately after a run rather than committing a growing file as finished work.
- **Unfinished retired Fable lane:** modified `Fable-hoth-guide/hoth-first-session.md`, `Fable-ossus/o2/README.md`; untracked `Fable-species/s6/README.md`, `build_test_archive.py`, `checks.json`, `new-files.txt`, `patch/species-s6.patch`, `provenance.json`, `tools/acst_togruta.py`, `tools/make_patch.py`, `tools/make_provenance.py`, `tools/stage_s6.py`. No completion or new ownership inferred from retirement. No Fable file edited, staged or committed.
- **Fable scratch scripts preserved and visible:** top-level `.py`/`.sh` in `Fable-hoth-batchB/den-outdoor/work/`, `Fable-hoth-mapnames/work/`, `Fable-ossus/o5/work/`, `Fable-resources3/work/`, `Fable-species/{s5,s6}/work/`. Copies underneath orig/new/new2/local_planets/stage remain on disk but ignored. Do not sweep these scripts into a commit without review.
- **Commit drafts, keep pending author confirmation:** `Documentation-support/C26-{attributes,credit,planet,resource,waypoint}-commit.txt`. No deletion authorized by C51.
- **Root scratch outside the survey:** the existing visible `work/c33*.py`, `work/c40*.py`, `work/c45*.py`, `work/c46*.py`, `work/c47*.py`, `work/c48*.py` are session helpers, not independently reviewed deliverables; no blanket add. Suffixed client archives and other ignored scratch stay local. Nothing deleted.
