# SWG server operating procedures — C13

13 October 2026 · ChatGPT. Procedures inspected against the local Python tools and launchers; commands below were **not executed**. They are instructions for the lock holder, not permission for live changes. Read current AGENTS.md and SWG-handoff.md before each job.

## Authority, paths and evidence

Claude owns `/opt/swg` and the test galaxy unless the owner transfers the lock. ChatGPT owns outside tools/research and cross-review. Owner approval is required for live changes/restarts; cross-review comes before deployment. Never run Git as root, push, enable a remote push URL, paste account files or expose backup secrets.

Windows project: `C:\Users\Pengw\Documents\Codex\2026-10-13\h`; WSL project: `/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h`. In commands below **TOOLS** means that WSL path plus `/outputs/tools` (replace it literally; it is notation, not an environment variable already configured).

| Component | Actual path / behavior |
|---|---|
| Live | `/opt/swg/Core3`, branch sandbox; `MMOCoreORB/bin`; swg-local service; ports 44453/44462/44463 |
| Development | `/opt/swg/Core3-dev`, branch dev; Debug build `MMOCoreORB/build/dev`; generated code stays here |
| Test | `/opt/swg/testgalaxy`, SQL swgemu_test; 46xxx ports; disposable from backup; test login 46453 |
| Rehearsal | `/opt/swg/rehearsal`, SQL swgemu_rehearsal; 45xxx ports; disposable restore proof |
| Database | MariaDB metadata **and** Berkeley DB world files; neither alone is a complete galaxy backup |
| Bot runtime | `/var/tmp/swg-bots`; credentials in private `/opt/swg/agent/bots`; reports in outputs/Bot-reports |
| Logs | live journal swg-local; `/opt/swg/dev-build.log`; `/opt/swg/rebuild.log`; per-bot out.log and log/ directory |
| Owner launchers | outputs/*.cmd; some pause and some mutate state—read the launcher first |

[Baseline](../SWG-developer-baseline.md) is an earlier configuration snapshot; [sandbox quickstart](../SWG-sandbox-quickstart.md) describes later settings. Neither proves current config. Use server status and pinned source/config manifests; never print config-local.lua. Baseline says restore is unrehearsed, but `restore-rehearsal-20261013T161005Z.json` reports passed checks. Keep chronology rather than silently declaring every old statement current.

## 1. Build: dev → test → review → live

1. Claim the board task/lock; record dev/sandbox HEAD and engine pin with `wsl -d Debian -u swgemu -- git -C /opt/swg/Core3-dev rev-parse HEAD`. Check dirty files without dumping secrets.
2. Arrange the required pre-change backup with the owner. `Back Up SWG Galaxy.cmd` / `wsl -d Debian -u root -- python3 TOOLS/backup_server.py` stops/restarts a previously running live service. It also refuses if **any core3 process** remains; coordinate test-galaxy shutdown with Claude first. Do not surprise a player or stop another agent's galaxy.
3. Edit only the approved dev slice. After Lua changes run `wsl -d Debian -u swgemu -- python3 TOOLS/check_lua.py`. A Lua parse pass does not prove runtime bindings/registrations.
4. C++/IDL: `wsl -d Debian -u root -- python3 TOOLS/dev_build.py -j4` (conservative example; actual default 8). It runs the build as swgemu. Never configure another build directory inside live Core3. Inspect build log and actual outputs; preserve executable hash/build pin.
5. Lock holder starts disposable test: `wsl -d Debian -u root -- python3 TOOLS/test_galaxy.py start --dev-server` plus approved test-only config arguments. Use `squad.py accounts` to generate the allowlist rather than pasting private account data. Helpers require AgentGear and account gates on test only.
6. Test the smallest changed slice in game; then justified regressions. Save commands/events, assertions, build pins and passed/failed/blocked counts. Fresh ordinary characters prove natural progression; helper-trained bots prove only their test slice.
7. Other agent cross-reviews diff and ethics. Commit logical changes as swgemu with `Agent: Claude` / `Agent: ChatGPT` trailer. Owner reviews concrete evidence and explicitly approves live promotion. Continue section 2 only then.

The [official Core3 guide](https://github.com/swgemu/Core3) describes Debug builds/GDB and current Debian 12 dependencies; our working Debian 13 difference is intentional. Follow local wrappers, not a new build layout copied from upstream.

## 2. Deploy and roll back

1. Before owner approval, prepare exact reviewed commits, client/server archive manifest, old/new configuration plan, backup identity, test evidence and rollback scope. Label pending human visual checks.
2. With owner-approved outage and lock: run a verified backup; gracefully stop live (`Stop SWG Server.cmd`). Because live build/backup guards detect any core3, coordinate stopping test too when required.
3. Merge only reviewed dev commits into sandbox **as swgemu**. Never copy the dev binary into live casually or use blanket destructive resets. Lua-only changes need parse + restart; C++ changes use `wsl -d Debian -u root -- python3 TOOLS/rebuild_server.py -j4` with galaxy stopped.
4. Client/TRE/config changes require their own reviewed manifest and owner approval. Server TRE priority is first in TreFiles; client uses higher searchTree number, but only for lines inside `[SharedFile]` and below `maxSearchPriority` (14 Oct, Claude: the MTG lines sat under `[Station]`, were ignored, and Hoth crashed the client; fixed the same day with the owner's OK by a `[SharedFile]` header above them in `swgemu_live.cfg`, backup `swgemu_live.cfg.before-sharedfile-20261014`). Check the real load order with `python -I outputs/tools/hoth/client_load_order.py [--login FILE]`. Preserve old load-order files privately; verify intended winning files.
5. Start live (`Start SWG Server.cmd`); wait for `[Core] initialized`; run `Server Status.cmd`. Verify login, changed function, save/relog and actual client where relevant. A listening port is insufficient acceptance.
6. On failure: preserve logs and stop further rollout. Decide **code/config-only rollback** versus **world/SQL rollback**. The latter discards newer progress; state exact lost interval and obtain owner approval. Code-only rollback may be invalid after database/schema changes.
7. **Missing:** a reviewed one-command live restore tool. Do not improvise tar/SQL overwrite into live. Use backup recovery notes to prepare a concrete plan, validate in rehearsal first, restore SQL and Berkeley DB from the same snapshot, then approved live recovery and acceptance.

## 3. Backups and restore drills

1. Required source: tools/backup_server.py; output mirrored to outputs/Backups with manifest/checksums/recovery notes. Read selected manifest metadata, not secrets. Full client/TREs are retained separately; galaxy snapshots are not full-PC/WSL recovery images.
2. The tool stops galaxy writers before SQL/world capture. SQL uses mariadb-dump with routines/events/triggers; preserve all world files and matching server/code/config. A successful archive listing alone is not a restore test.
3. With live stopped and rehearsal ports available, lock holder runs `wsl -d Debian -u root -- python3 TOOLS/restore_rehearsal.py <backup-directory>`; `--keep` preserves diagnostic copy. It creates/removes only the marked disposable rehearsal and isolated DB.
4. Inspect `Documentation-support/restore-rehearsal-<UTC>.json` plus log: hashes, row counts, initialization/world markers, clean shutdown, unchanged live SQL/world and cleanup. Record result, duration and precise limitations. Current historical passed report: 161005Z; not proof every later snapshot restores.
5. Rerun after risky backup/restore changes. **Missing:** RPO/RTO agreement, off-machine encrypted copy and approved retention policy. Do not delete old backups to create space without the owner's decision.

MariaDB documents [logical dumps and their consistency limits](https://mariadb.com/docs/server/clients-and-utilities/backup-restore-and-import-clients/mariadb-dump); the stopped-game capture coordinates our two stores. SQL backup advice alone does not cover Berkeley DB.

## 4. Upstream updates

1. `Check SWGEmu Updates.cmd` / root `python3 TOOLS/upstream_sync.py` fetches official commits and reports changes. It **does mutate Git fetch refs**, although it does not apply them to working source; server lock still applies.
2. Review incoming dependencies and migration risks. No blanket package updates. Make fresh backup (<2h tool requirement), stop live with approval, preserve dev work, and require clean tracked files/sandbox branch.
3. Root `python3 TOOLS/upstream_sync.py apply` internally runs Git as swgemu, tags pre-sync state, rebases local commits and aborts on conflicts. If conflict handling fails, stop and preserve evidence rather than manual destructive recovery.
4. Rebuild, use disposable validation, cross-review changes and get owner approval before live restart/promotion. The convenience tool currently targets sandbox: **gap** is a dev-first upstream rehearsal workflow rather than treating direct sandbox rebase as a complete release pipeline.

## 5. Routine health checks

1. `Server Status.cmd`: service/database, current-start initialization/errors, live ports, client/DB address match, branch/dirty state/push-disabled check and disk/backup age. It checks **live**, not test. Test status: root `python3 TOOLS/test_galaxy.py status`.
2. Windows `python outputs/tools/proc_check.py` reports galaxies/bots/relay/RAM and /tmp occupancy. `Check Processes.cmd` includes `--clean`, which can terminate recognized stale helpers; read report-only first. It is not permission to kill active clients.
3. WSL root read-only checks: `df -h /opt/swg /tmp /var/tmp`; `df -i /opt/swg /tmp /var/tmp`; `free -h`; `systemctl status mariadb --no-pager`; `journalctl -u mariadb --since '-30 min' --no-pager`. Inspect filesystem capacity/inodes as well as free memory.
4. `/tmp` is a roughly 7.8 GB RAM disk in this installation; full bot logs there caused MariaDB temporary-file/login failures on 13 Oct. Squads now use disk-backed `/var/tmp/swg-bots`. Check remaining legacy Kael/daemon/temp users too; moving one harness does not prove all writers migrated.
5. Read Bot-reports/*/LOG.md or squad.py last before raw JSON. squad.py tidy rotates report/log history; runtime client logs can still grow. Verify tool's actual thresholds and active-run exclusions before cleanup.
6. Suggested local operating thresholds (proposals, not configured alarms): investigate /tmp>70%, act before 85%; disk<20GiB or rapid inode growth; sustained swap growth/long startup. Ask owner before retention/deletion/new monitoring service.

## 6. Debug a server crash

1. Preserve exact time, PID/exit, build SHA and change trigger. Read `journalctl -u swg-local --since <time> --no-pager` (live), or the test galaxy's recorded console log. Preserve first fatal error and nearby context before a restart; don't expose secrets in copied logs.
2. Distinguish crash, OOM kill, storage failure and deliberate stop: read service result plus kernel log (`journalctl -k --since <time> --no-pager`) and storage/RAM checks. Read-only `systemctl show swg-local -p Result -p ExecMainStatus -p LimitCORE` and `/proc/sys/kernel/core_pattern` identify capture setup.
3. If available: `coredumpctl list core3`, then `coredumpctl info <PID>` and a private `coredumpctl dump <PID> --output=<private-file>`. **Missing/unverified:** systemd-coredump installation, configured size/retention and actual WSL capture. Do not install/change live capture settings without owner approval.
4. Use the **exact crashing executable and matching symbols/source**, not merely today's rebuild: `gdb <matching-executable> <private-core>`, then `set pagination off`, `info threads`, `thread apply all bt full`. Collect locally and sanitize variables/credentials before sharing. Debug build helps; optimized variables may be unavailable.
5. Reproduce the smallest input on test; fix once, add a meaningful regression and follow sections 1–2. GDB attachment or running under GDB pauses/changes execution timing; lock/owner approval for live use required.

References: [GDB backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html), [Debian coredumpctl manual](https://manpages.debian.org/bookworm/systemd-coredump/coredumpctl.1.en.html). These describe tools, not proof they're configured here.

## 7. Debug a client or bot crash

1. Decide real Windows client versus core3client versus Python/MCP daemon. Record client/body build, planet/cell, command/event sequence and exception/exit code. A command timeout is not automatically a process crash.
2. For squads inspect only the failed bot's private runtime `out.log` and needed report steps/events. Check PID identity/current process before any stop. Script traceback, unsupported body command, disconnect and server failure have separate reports.
3. Verify daemon/client command compatibility and scene generation/correlation before retrying. No two agents drive one account; read AGENT-GUIDE.md before Kael connect; end play with write_notes/progress/disconnect.
4. Real client: owner logged in/at PC, then UM screenshots and controlled steps. Reproduce on known-good load order/settings; preserve crash logs/minidump if generated. Crash log (found 14 Oct, Claude): `SWG-client/SWGEmu.exe-stage.<build>-<UTC time>.txt`, with the FATAL line, terrain, player position and last templates loaded, plus a matching `.mdmp`. **Missing:** repeatable Windows dump collection/asset-bisection harness. Never type owner password or silently change client installs.
5. Restore only this scenario's fixtures with consent, preserve error report and send body/server defect to Claude. Do not solve a client crash by deleting world DB or retrying strong combat indefinitely.

## 8. Performance

1. Establish same build/config/area/population/seed and idle baseline. Record CPU/RSS/swap, navmesh job/thread limits, route timing and server initialization. Avoid running both galaxies merely for convenience under memory pressure.
2. `python outputs/tools/timings.py summary` produces Bot-reports/TIMINGS.md; squad reports auto-record duration. `timings.py add <kind> <name> <seconds> <note>` records measured build/setup/review times, not estimates.
3. Increase bots gradually on test, one driver per bot, one variable per run. Compare p50/p95 from measured batches, total throughput and errors; fast failure is not a speed improvement. Retain scene/path proof and unresolved blockage counts.
4. **Missing:** current per-subsystem Core3 profiling/export and a repeatable load ceiling benchmark. Inspect upstream profiler/debug hooks first; perf/install/new services require separate approval. GDB sampling is intrusive; no arbitrary live attach.

## 9. Incident notes

Write outputs/Agent/reports/<date>-<topic>.md with: time+timezone; environment/build/config manifest; expected/observed; minimal steps; evidence links; data/player impact; containment; proposed fix; test result; owner decisions; remaining unknowns. Keep credentials, raw cores and backup contents private. Append concise outcome/commit/untested/next to handoff, tick roadmap only for completed work, and notify other agent via inbox. Label **observed / inferred / untested / blocked** distinctly.

## Ten highest-value gaps (ranked)

1. Verified live rollback/recovery procedure and executable/world/schema compatibility checklist.
2. Core-dump capture validation and private matching binary/symbol retention.
3. /tmp/disk/inode/RAM monitoring with actionable thresholds and log-writer inventory.
4. Dev-first upstream-update rehearsal before sandbox rebase.
5. Release manifest tying commits/engine/config/TRE/client load order and acceptance evidence together.
6. End-to-end ordinary-player crafting/trade/travel/loot acceptance; C8 wrappers alone are insufficient.
7. Restore RPO/RTO, encrypted off-machine copy and owner-approved retention.
8. Bot scenario total deadlines/cleanup, safe prey/hospital fixtures and reliable quantities/effect state.
9. Windows client crash/dump and asset-dependency/visual regression procedure.
10. Repeatable test load benchmark and subsystem profiling with resource ceilings.

This SOP supplies procedures and gaps. No build, backup, restart, deployment, dump capture, package installation or in-game check was run for C13.
