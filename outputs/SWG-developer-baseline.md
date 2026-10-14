# SWGEmu setup baseline

This is the foundation check before adding original or community content. It follows the current Core3 build instructions and checks historical forum guidance against the installed source. Optional community gameplay modifications are excluded.

## Setup decisions

| Item | Baseline |
|---|---|
| Platform | Keep the working Debian 13 / WSL 2 installation, as requested. The current manual guide lists Debian 12; this remains a documented difference. |
| Server source | Official Core3 `unstable`, pinned at `403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79`. |
| Engine source | Pinned at `4cbf39336e0e727dfef861fbe65bd303ce70fd37`. |
| Runtime build | Existing Release build with clang 19, Lua 5.3 and Berkeley DB 5.3. Runtime code was not rebuilt or replaced during this maintenance. |
| Debugging | GDB installed from Debian's official package repository, as listed in Core3's build dependencies. A future source-debugging session may need a Debug build; installing GDB alone does not add debug symbols to the existing executable. |
| Configuration | Installation-specific values stay in `config-local.lua`; upstream gameplay defaults remain the reference. Existing local CPU limits are four processing threads and two navigation-mesh jobs. |
| Standard zones | All twelve upstream ground-zone entries are enabled, including tutorial. All 51 configured server archives are present. |
| JTL / later expansions | JTL retains the upstream disabled default. Kashyyyk and Mustafar are not enabled. Enabling a feature is a later testable change, not a prerequisite for this baseline. |
| Owner tools | Existing owner level 15, character builder and documented client admin-command setting retained. The earlier troubleshooting edit to the admin-role flag was restored to upstream's value of 0; the entire role file now matches upstream. Retest command entry after logging back in. |
| Resources | Normal resource generation retained. No perfect-resource changes, database deletion or resource-cycle reset. |
| Gameplay | No changes to XP, skill-point limits, crafting timers, costs, housing limits or profession rules. |
| Mantis | Optional connection disabled with `Core3.MantisHost = ""`, because this installation has no Mantis service. Game database credentials are unchanged. |
| Client | Previously requested 1600×900 movable windows, multiple instances and free pointer settings retained. The user still needs to confirm their behavior after reopening the client. |

The generated resource-spawn script is the remaining difference reported by Git; it is maintained by the running resource manager. There are no custom quests or content packages installed by this maintenance.

## Backup and operation

**Back Up SWG Galaxy.cmd** saves and stops the galaxy, exports SQL account/character metadata, archives Berkeley DB world saves together with the server source, Git history, executable and settings, and starts the galaxy again. It also preserves database login/grants, service configuration and client preferences. A lock prevents overlapping backup runs. The Start launcher now recognizes planned maintenance and keeps its WSL connection open through it.

Verified snapshots are copied into **outputs/Backups**. Each contains a manifest, checksums and recovery notes. Backups contain private account hashes and database configuration; retain them privately.

The TRE archives and full client remain in their installed folders rather than being duplicated in each galaxy snapshot. The manifest records the server TRE hashes. This is a galaxy recovery backup, not a complete PC or Debian-image backup. Archive contents and checksums are verified; a restore into a separate disposable galaxy has not been rehearsed.

Use **Start SWG Server.cmd** to start the database and galaxy and refresh the connection address. Use **Stop SWG Server.cmd** for a graceful save and shutdown. Closing the server window or rebooting is not the intended shutdown procedure.

## Validation and remaining tests

The completed maintenance checks are recorded in **SWG-baseline-checks.json**: initialization, service ports, database schema and retained account/character counts. The earlier content audit still applies: unresolved asset warnings are recorded individually in **SWG-content-warning-inventory.md**; maintenance does not establish that every ship or effect works.

Before adding content, finish these ordinary in-game acceptance tests:

1. Log in, use the owner teleport and character-builder commands, then log out and return to the same character.
2. Complete the tutorial, travel between normal planets, fight and loot a creature, and clone after a death on a normal test character.
3. Survey/sample resources, craft an item, experiment where applicable, and confirm the item remains after relogging.
4. Open two clients, confirm the requested window/pointer behavior, and use separate accounts for a normal trade/group test.

These are user gameplay checks, not claims of automated coverage.

## References

- [Current official Core3 build instructions](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/README.md)
- [Official WSL setup entry point](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/wsl2/README.md)
- [Developer administration guide: client settings and both database stores](https://www.swgemu.com/forums/showthread.php?t=20) — historical; obsolete account-creation and permissions examples were not applied.
- [Server administration guide: zones and backups](https://www.swgemu.com/forums/showthread.php?t=36573) — historical community guide linked by the documentation index; old VM paths and recompilation advice were not copied literally.
- [Mantis initialization: empty host disables integration](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/db/MantisDatabase.cpp)
