# L1 live client for Hoth and T2 refs() scanner — Fable, 14 Oct 2026 (STOPPED mid-way by the owner's change of plan)

**STATUS:** L1 steps (2) and (3) are done and checked; (1), (4), (5) are notes below, not written up; T2 is complete and
proven but dropped for now (not applied). Pick up from here: the README needs the (1) write-up, the (4) checklist and
the (5) server list; `checks.json` was not written.

## What is in the folder

| path | what | state |
|---|---|---|
| `l1/live_client_check.py` | read-only checker: `python -I live_client_check.py <client folder> [--login FILE] [--archives DIR] [--json]`; cfg chain read with `client_load_order.load_order` (CLIENT patched to the folder), archives with `swgfmt.fmt_tools.read_tre`, Bellum-style `cfg_priorities` view where it disagrees, duplicates, ignored lines, the four MTG archives Hoth needs, a WINS / LOSES / NOT LOADED verdict per entry of local_planets.tre | done |
| `l1/stage_live_cfg.py`, `l1/staged/`, `l1/patch/` | the live variant: `SWG-client/local_planets.cfg` (new, `[SharedFile] searchTree_00_49=local_planets.tre`, CRLF), `swgemu.cfg` + `.include "local_planets.cfg"` after the live include, and an optional one-line guard in `Play SWG Test Galaxy.cmd` (`if not exist local_planets.cfg if exist local_planets.tre ...`) so the test launcher stops adding the same line when the live file exists | done |
| `l1/checker-results.json` | the client today: 74 archives loaded, ours nowhere, 0 of 20 win; the staged cfgs (archives from the real folder): 75 loaded, ours at 49, all 20 win, no duplicates, no ignored lines, MTG archives loaded; staged + the test launcher's line: still all 20 win, `local_planets.tre` listed twice at 49 (harmless to the verdict; the guard removes it) | done |
| `t2/staged/tools/swgfmt/asset_refs.py`, `t2/staged/tools/hoth/hoth_closure.py`, `t2/patch/*.patch`, `t2/proof.json` | our own 45-line reference scanner (absolute asset paths, appearance children, terrain shader families and bare appearance names) and `hoth_closure.py` on it with no `exec` left; `git apply --check` clean on the h layout; the closure re-run writes a TSV byte-identical to `Documentation-support/hoth/hoth-closure.tsv` (487 files: 444 stock, 41 MTG, 2 missing) | done, dropped |

## Notes for (1), (4), (5), gathered but not written up

- (1) `swgemu.cfg` includes, in order, `swgemu_login.cfg` (`[ClientGame]`: login address and port; on a test session the
  launcher rewrites it and adds `[SharedFile] searchTree_00_49=local_planets.tre`, backing the live copy up as
  `swgemu_login.live.cfg`), `swgemu_live.cfg` (`[SharedFile] maxSearchPriority=50`, the stock archives at 49..24, four
  other sections, then a second `[SharedFile]` block with the 23 MTG archives at 23..2 since 14 Oct), `swgemu_preload.cfg`,
  `options.cfg`, `user.cfg` (no searchTree lines). `Play SWG.cmd` only restores the live login file and starts the exe.
  Priority order, not include order, decides: the login file's block at 49 wins although it is included first.
- (4) Server side read so far: the ticket list comes from the server as planet-name strings
  (`PlanetTravelPointListResponse` `insertAscii(planet)`), and a zone change sends the client
  `"terrain/" + zone + ".trn"` (`packets/zone/CmdStartScene.h:28`); a client without the MTG archives cannot open that
  file (the owner's 14 Oct crash, `FATAL ... terrain/hoth.trn`), and a character left on Hoth would hit it at every
  login until the files are installed (guess: strongly expected). Without local_planets.tre only: no Hoth button on the
  galaxy map and no `@planet_n:hoth` name; whether the dropdown still offers the raw name is untested.
- (5) Live needs, from `tools/test_galaxy.py`: `table.insert(Core3.TreFiles, 1, "local_planets.tre")` (first = wins),
  `hoth` in `Core3.ZonesEnabled`, the dev scripts (planet entry, regions, screenplays, mobiles), `/opt/swg/tre/local_planets.tre`
  (already there), `backfillZones = "hoth"` in `resource_manager.lua` for the first start only, then `""`; the 23 MTG
  archives are already in live's TreFiles (port log 13 Oct 23:02).
