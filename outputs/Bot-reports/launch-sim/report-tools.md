# Launch simulation report tools (C47)

From `outputs/` in WSL, as `swgemu`, run:

```sh
python3 tools/bots/botpop_analysis.py --numbers-out Bot-reports/launch-sim/numbers-run6.md
```

This reads runs 1, 2, 3, the 22:26 log (`botpop-launch.jsonl.2332.old`) and the current run 6 log, and writes `analysis.json` plus the Markdown report with all five comparisons. It sends no bot commands and writes nothing under `/opt/swg`. If the current log has been rotated/replaced, override all inputs with repeatable `--run NAME=PATH` arguments, including `--run run6=PATH`. Use a read-only copy in `/var/tmp` for an immutable observation. The early sample uses the copied run 6 rows from 23:32 through 23:48, 15 October; it is not the full overnight result.

`botpop_report.py EVENTS --out FILE --compare NAME=PATH` also works independently. Both commands accept repeatable `--host FILE`; otherwise they read the local `host-*.jsonl` files. The report filters capacity samples to the event window. Host slopes now include 1,700-bot samples and split on population changes.

Final despawn is excluded using explicit event markers if present, the server's last full-population sample before an online decline, or the last host sample before logout activity. Older logs do not log the despawn command itself. These sampled boundaries are conservative and can discard up to one sampling interval of valid play. If neither source captures the stop, the report explicitly says so: supply `--until-ms EPOCH_MILLISECONDS` with the actual command time. For the default five-run command that explicit time applies to run 6; with custom inputs it applies to all specified runs.

Income uses separate denominators: missions and junk use summed time from each bot's own spawn to the report boundary. Loot credits are a **residual estimate**, using each bot's first-to-last cash+bank snapshot change, adding back charged training, then subtracting mission payments and junk sales in that same interval. Creation money and pre-first-snapshot earnings are excluded. Unlogged flows or delayed completion rows can affect this residual; negative values remain visible rather than being called loot.

`train.spent` identifies the charged schema; older rows without it were free training and retain their nominal cost separately. Refusals count both raw `broke` rows and distinct bot/skill pairs. For masked mission payouts (C44 F6), a matched old done/gone row uses the reward only when its logged bank delta plus inferred bank-funded training exactly equals that reward. Training consumes the latest observed cash first. This is an inference from snapshots, not independent proof of payment; unknown cash or a mismatch prevents inference. New compensated done rows use logged `paid` without adding withdrawals again.

Mission tables use the bot's level at acceptance and mission level. They show successes per accepted attempt and per resolved attempt, with pending attempts separate. Finish-time statistics include successes only. Death comparisons are descriptive: purse, run length, explorer population, bot behaviour and mission selection differ, so they cannot isolate a causal gate effect. Census counts are observations of named types; without object IDs they are not unique creature counts.

Offline tests (no galaxy access):

```sh
python3 -m unittest discover -s tools/bots -p test_botpop_reports.py -v
```
