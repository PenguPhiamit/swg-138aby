LOCAL STAR WARS GALAXIES DEVELOPMENT SERVER

Start SWG Server.cmd starts the Debian database and galaxy, and refreshes the
client connection address. Allow the galaxy to finish loading before playing.
Keep the server window open while playing so Windows keeps Debian running.
Play SWG.cmd opens the pre-CU client. SWG-login.txt contains your owner account.
If the game closes immediately on first launch, right-click Play SWG.cmd and
choose Run as administrator. The observed startup error was access denied while
creating Software\Sony Online Entertainment\Default registry settings.
Stop SWG Server.cmd requests a graceful shutdown. Save your work before rebooting.
Back Up SWG Galaxy.cmd makes a verified galaxy backup with the game briefly offline,
then starts it again. Snapshots are in Backups beside this document. They include
world saves, account metadata, server code and settings. Keep the installed TREs
and full client too; those assets are not duplicated in every galaxy backup.
See SWG-developer-baseline.md for the setup review and remaining gameplay tests.
The later sandbox/content profile is described in SWG-sandbox-quickstart.md.
SWG-Complete-Project-Record.pdf documents this chat's setup and change history.
Reopen the client after the content installation to load its new archive list.

The Start window now shows the live server console. Wait for "[Core] initialized"
before logging in. View Server Log.cmd opens a second live view at any time;
closing that one is harmless. Stop SWG Server.cmd shows the shutdown and says
when it is safe to reboot.
Open Server Code.cmd opens the server code in VS Code (live = branch sandbox,
dev copy = branch dev). Use the Source Control panel, or the Git Graph button at
the top of it, to see every change. Edits there are real server edits: commit
them, and check Lua before restarting.
Rehearse Restore.cmd proves the newest backup can be restored (galaxy must be
stopped; uses a temporary copy on other ports and deletes it afterwards).
Rebuild Server.cmd recompiles after C++ changes. Check SWGEmu Updates.cmd lists
new official Core3 work without changing anything.
Server Status.cmd prints a health check: service, initialization, error lines,
ports, connection address, source branch, uncommitted files and backup age.
All launcher scripts now live in the tools folder beside this document.
See SWG-roadmap.md for the development plan and SWG-gap-check-research.md
for the October 13 content research.

PRIVATE SOURCE CONTROL
All server changes are committed on a local-only Git branch named sandbox in
/opt/swg/Core3. Pushing to GitHub is disabled. The tag upstream-base marks
the unmodified SWGEmu revision. As the swgemu user inside Debian:
  git log --oneline upstream-base..sandbox    (everything we changed)
  git status                                  (work not yet committed)
Commit each finished change before the next one. config-local.lua and the
world databases are deliberately not in Git; backups cover them.
Before restarting after Lua edits, check syntax from PowerShell:
  wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/check_lua.py

The server is not configured to start automatically at Windows startup.
No router forwarding or Windows firewall exception has been added.

Server source and content:
\\wsl.localhost\Debian\opt\swg\Core3\MMOCoreORB

Custom content starting points:
  bin\scripts\screenplays  - scripted quests, events and encounters
  bin\scripts\mobile      - NPC definitions
  bin\scripts\loot        - loot definitions
  bin\scripts\object      - server object templates
  src                     - compiled game systems

Client files: SWG-client next to this document.
Server assets: /opt/swg/tre inside Debian.
Build log: /opt/swg/build.log inside Debian.

To inspect server status from PowerShell:
  wsl -d Debian -u root -- systemctl status swg-local --no-pager
To inspect recent server messages:
  wsl -d Debian -u root -- journalctl -u swg-local -n 60 --no-pager

Community additions need review for compatibility, licensing and required client
patches. Expansion files alone do not guarantee working expansion features.
