# Local SWG galaxy: project record

October 13, 2026 - America/Los_Angeles

This record covers the decisions, installation, troubleshooting, research, maintenance, community-content collection and sandbox changes carried out in this chat. It distinguishes work that was performed from ideas, unavailable content and gameplay that still needs a live test. Account passwords, database passwords and private secrets are intentionally kept in their existing private files rather than copied into this document.

## Project direction and decisions

The original request was a local Star Wars Galaxies server using pre-CU or CU rules, with no NGE game system, and room to design original content and add community work. The user wanted as much content as practical, recognized that later expansions extended beyond the pre-CU milestone, and accepted a pre-CU foundation for customization. CU was not ruled out as inherently unsuitable for custom content; the selected implementation was the public SWGEmu Core3 project.

The server and client run on this Windows PC. The supplied source was the European Complete Online Adventures Disc 1 image under C:/SWG server. The user stated that Disc 2 did not contain additional game files according to the edition documentation. The user completed the requested PC restart during WSL setup and later confirmed successful login and tutorial entry on an owner account.

The requested client layout was movable 1600 x 900 windows. The user wanted multiple clients, a mouse pointer that could leave the game window, accessible crafting resources, and graphics settings suitable for the modern PC. Later, the user clarified that a "proper sandbox" initially meant a clean developer-guided foundation before making original edits. After that baseline was documented, the user explicitly requested the optional gameplay changes, the obtainable community content, and this PDF record.

## Installation and initial configuration

Windows Subsystem for Linux 2 was installed with Debian. The installed distribution is Debian 13; SWGEmu's current manual build instructions list Debian 12. This difference was explained, and the user explicitly chose to keep the working Debian 13 installation instead of performing a separate Debian 12 migration.

Core3 was downloaded from the official project, using the unstable branch at revision 403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79. Its engine submodule is pinned at 4cbf39336e0e727dfef861fbe65bd303ce70fd37. Source, scripts, the compiled server and world saves live under /opt/swg/Core3/MMOCoreORB in Debian. Server TRE assets live under /opt/swg/tre.

The build used clang 19, CMake and Ninja, together with MariaDB, Berkeley DB 5.3, Lua 5.3, OpenSSL, Boost, Java and jemalloc dependencies. A dedicated swgemu service user owns the game files. The original runtime was a Release build; the later sandbox source changes were rebuilt in the same build directory. GDB was added during the baseline review. Installing GDB did not, by itself, turn the existing Release executable into a Debug build.

The game SQL database is named swgemu. Its account and character metadata are separate from the Berkeley DB files that hold world objects and persistent in-game state. Random database credentials and a random database secret were generated locally. The owner account is named owner and retains administrator level 15. At the latest startup verification, the SQL database still contained one account and one character, with schema version 1008.

The galaxy is named My Galaxy, with galaxy ID 2. The local configuration file is bin/conf/config-local.lua. It records the installed TRE path, database connection, account auto-registration and character-builder availability. Local CPU settings use four zone-processing threads and two navigation-mesh jobs, leaving capacity for the Windows client and desktop.

The client was assembled from the supplied disc files and the official SWGEmu launcher patch service. The required-file manifest was checked with MD5 hashes; matching disc files were reused and required replacements downloaded. Missing graphics runtime files were later supplied from the same official source. The original client/runtime copies were retained where relevant for troubleshooting.

## Operation and shutdown

The Debian service is swg-local.service. It runs the server as swgemu, from the game's bin directory. A small service wrapper keeps the server console input available and translates a normal service stop into the server's exit command, allowing the normal save/shutdown sequence. The service timeout is five minutes. A forced stop was not substituted for a normal save in the completed maintenance procedures.

Start SWG Server.cmd starts MariaDB and the galaxy, refreshes the local connection address, and keeps a WSL command alive while the game runs. The WSL address can change, so the launcher updates both the galaxy address in SQL and the client's swgemu_login.cfg. Stop SWG Server.cmd requests a graceful shutdown. Play SWG.cmd starts the pre-CU client.

WSL services alone did not reliably keep the distribution alive after the last Windows-to-WSL command exited. The launcher was therefore made persistent while the galaxy runs. Planned maintenance now creates a marker recognized by the launcher so it stays connected through a stop/backup/restart. A quiet helper was also started during maintenance to keep the current WSL session available. Stopping the galaxy remains the intended way to shut down before rebooting.

The game uses UDP ports 44453, 44462 and 44463. These were checked after startup. The server is not configured to launch automatically at Windows startup. No router forwarding or new Windows firewall exception was added in this work.

## Client troubleshooting and final preferences

The client initially closed during startup. Its recorded error was a failure to create the Sony Online Entertainment Default registry settings, with access denied. Creating a user registry key did not resolve the observed failure. The user successfully launched the client using Run as administrator; that launch method remains documented. This is an observed workaround for this installation, not a claim that every SWG installation requires elevation.

Teleport initially produced "No such command, mood, chat type: teleport" while God Mode was already active. This showed that the client rejected the text before the server handled it. An earlier proposal combined an admin-role client-flag change with an auxiliary database credential change; automatic approval review rejected that combined scope. The user then explicitly approved the narrower admin flag change and restart. That flag change alone did not fix command entry.

The documented client setting [ClientGame] 0fd345d9=true, loaded through user.cfg, resolved command entry in the user's test. The temporary admin-role flag change was subsequently restored to the exact upstream role file during the clean-baseline review. The owner account stayed at level 15. A fresh live command check after that restoration remains part of acceptance testing; server-side permission checks alone do not prove the client accepted a command.

The user also reported Enter switching between fullscreen and windowed mode. A modifier-key reset was attempted, and a Return test remained windowed. The user later confirmed that the reported problems were fixed. A latched Alt key was a possible explanation, but its cause was not proven.

The saved client preferences are movable 1600 x 900 windows, multiple instances, an unconstrained mouse cursor, a hardware cursor, disabled pointer-mode edge camera panning, full-resolution texture mip levels, and a 60 Hz fullscreen refresh preference. user.cfg is included after the other configuration files. Duplicate graphics settings in options.cfg were tidied. These preferences require reopening each client. They are configuration changes within the legacy DirectX 9 renderer, not an engine replacement or an FPS-unlock patch.

The observed hardware was an RTX 5070, a 1920 x 1080 display at 60 Hz and 12 logical CPU processors. Separate accounts are recommended for normal multiplayer testing. The later sandbox profile also permits four simultaneous characters on one account, but the same character cannot be logged in twice.

## Research, content audit and forum access

The user asked for research into missing content and the long-running project's documentation. The first research pass compared the installed source, startup logs and archive indexes. All 51 TRE archives named by the original Core3 configuration were present; 53 archives were in the original server asset folder. A file's presence in the folder did not automatically activate it, because the load list is explicit.

The initial audit identified 35 distinct missing-path/appearance references, 28 related to ships or space. It decoded 116 version-0005 archives across the server and supplied disc. It did not decode 59 version-0006 disc archives, so an asset not found in that scan was not proven absent from every file on the disc.

The ARC-170 and Jedi Starfighter tables were found in later patch archives on the user's disc, outside the configured pre-CU set. Those whole later patches were not blindly loaded. The indoor glow particle existed in a loaded archive, but the server did not instantiate its PEFT particle format. The missing tutorial snapshot was consistent with a separately scripted tutorial, which the user had already entered successfully. Other appearance, inheritance and ship-data references remained individually unresolved.

The public source contained substantial JTL systems, although the installed configuration initially left JTL disabled. Merely loading space zones did not enable every pilot and ship gameplay path. Kashyyyk and Mustafar were not enabled ground destinations. An expansion disc and a source checkout did not establish a complete playable expansion.

SWGEmu web access initially failed through the research tool. The in-app browser later loaded the forum. The user completed verification/sign-in manually, after which the development index, administration guides and scripting discussions were readable. Historical guides were checked against current source; old paths, obsolete permission examples and recompilation advice were not copied indiscriminately. One concrete scripting difference was screenplay.lua versus the current screenplays.lua content loader.

The research covered Lua screenplays, NPC/object spawning, conversations, observers, example quests, Sytner's IFF Editor and TRE tools. No extra third-party editor executable was installed. Old JTL beta downloads were not treated as verified mandatory patches. A separately advertised server's custom JTL/Kashyyyk work was not assumed to be present in the public Core3 checkout.

## Clean-baseline maintenance

The initial Mantis database connection error came from an optional bug-tracker integration, separate from the main game database and saves. No separate Mantis service was needed for this private galaxy. During later authorized baseline maintenance, its host setting was cleared to disable the unused connection. The database account password and secret were not changed by that maintenance.

GDB was installed from Debian's official package repository. The admin-role file was restored to upstream as described above. A verified galaxy snapshot was created before the maintenance settings changed. The first backup attempt exposed a MariaDB SHOW CREATE USER output-format difference; the helper restarted the galaxy safely, was corrected to accept the actual output, and then completed a verified backup.

The completed baseline check recorded initialization, expected game ports, schema 1008, retained account/character counts, owner level 15, and the disappearance of the Mantis access error. The user chose to retain Debian 13. No XP, crafting, city, travel, resource-stat or profession rules were altered during that baseline pass. The next chapter describes the later, explicitly requested sandbox profile and supersedes that historical gameplay state.

## Later sandbox implementation

After reviewing the optional changes, the user explicitly requested their implementation. A second verified snapshot was taken before any sandbox/content edits. The exact values appear in the generated settings table in the PDF and in SWG-sandbox-settings.json.

The profile changes regular positive XP to 5x, retains the ordinary 1.2 group bonus, and uses a separate 2x Jedi XP multiplier. Negative XP is not multiplied by the new regular-XP setting. New characters receive 10,000 cash and 100,000 bank credits. Skill points are set to 1,000, with recalculation updated consistently on character load, training and surrender; existing characters receive the revised budget when recalculated/relogged. Prerequisites and XP requirements still exist.

Account limits become 15 characters per galaxy and four online at once. Prototype/practice crafting waits are one second; factory timing is 25% of the original formula, with a one-second minimum. Training prices are 25% of the original amount. Structure maintenance and city maintenance each use their respective 50% settings. City rank population requirements become 1, 2, 3, 4 and 5. Player-house storage becomes 1,000 items per lot, capped at 10,000; civic and zero-lot special cases keep their separate code paths.

Resource stacks can hold 999,999 units and resource deeds supply 100,000 units. The owner command /resource perfect TYPE uses the existing manual resource-spawn system to make a new resource with all applicable attributes at 1,000. It reports the generated resource name; /resource create NAME QUANTITY then gives a stack, or a resource deed can be used. Existing resources and their spawn cycle were preserved, rather than deleting the resource database or changing every existing resource's stats.

Basic speederbike, swoop and X-34 templates use run/walk speeds of 30/10 metres per second. Shuttle/starport away times are ten seconds, landing times two seconds, and landed windows ten minutes. The Village phase duration becomes seven days. Existing already-scheduled events and persisted objects may require their next cycle, recreation or a live check before every changed template/timer is visible.

JTL and launch-from-device are enabled for sandbox testing. Standard ship/pilot functionality needs an in-game test; enabling the switch is not a declaration that every ship, component or mission works. No later ground planet was enabled solely because its terrain/assets were downloaded. No NGE combat or profession-system replacement was imported.

Twenty server source/configuration files were changed for this profile, including consistent skill-point calculations, crafting/factory timing, training price, maintenance/storage limits, resource constants and the new perfect-resource command. The server was gracefully stopped and rebuilt with six compiler jobs. The build completed successfully. The exact file list and final executable checksum are recorded in the generated manifests.

## Community content collection and installation

The research checked Sentinel's Republic, Mod the Galaxy, Sunrunner II and Empire in Flames. Public source was kept separate from the live server while it was examined. The newer Sentinel's Republic checkout references a custom-script folder that is absent from that checked tree; its public repository therefore did not supply a complete copy of its advertised content. The older website-linked repository was a historical 2020 snapshot.

The reusable local collection contains 16,912 published MTG files and a reference archive of 30,504 Sentinel's Republic Lua files. Two SR command files carrying proprietary/not-for-distribution notices were excluded from the reusable archive: autoEntertain.lua and autoGroupInvite.lua. The original research checkout was not rewritten. No private Sunrunner II scripts or permission-restricted original artwork were taken, and no complete reusable Empire in Flames package was verified. No message or permission request was sent to another team.

The MTG asset release linked by the project's DevEnv documentation was located in its public Google Drive folder. All 23 published archives downloaded, passed version-0005 TRE header checks, and received SHA-256 hashes in the local manifest. They were copied to both the server asset folder and Windows client. The original pre-CU archives retain higher search priority; MTG is a fallback for additional files. This limits unintended replacement of existing pre-CU data, although overlapping strings/assets may still need individual review.

The MTG object and NPC definitions were installed with their shared-template and conversation loaders. All 16,734 imported/generated Lua files selected for syntax validation passed Lua 5.3 parsing. An MTG Content Library menu was added to the character builder with 8,051 inventory-item and schematic entries. A catalog entry is access to a definition, not a guarantee that a complete crafting or quest-acquisition path exists for that item.

The published The Beginning example quest was installed once, using its original state/conversation framework. Han Solo and Chewbacca were moved from hard-coded interior-cell positions to outdoor Tatooine positions 3565/-4795 and 3568/-4795. Nil guards were added around their mood changes. The nearby ship/area objective remains part of the example. Its 10,000-credit completion reward and one-time quest states remain. Completion still needs a live player test.

Collected assets include definitions for later-era furniture, houses, weapons, creatures and planets. Some NPC files are placeholders; the inspected Bolotaur, for example, had no attacks or loot and was not attackable. Later ground planets, large expansion progression and private server-specific quests were not represented as completed features.

Credits, original file notices, repository revisions, hashes and the publisher's reuse statement are retained with the collection. Credit Mod the Galaxy and original contributors when adapting or publishing their work. The bundled source notices remain the source of file-specific terms; local possession of another server's launcher files would not itself supply permission to reuse its original art.

## Verification, warnings and remaining work

The rebuilt galaxy completed initialization in approximately 35 seconds. The latest check found the expected game ports, schema 1008, one account, one character and owner level 15. The startup error scan found no server error, fatal-error or Lua-error lines. That is a startup result, not end-to-end coverage of 8,051 catalog entries.

The broad import also produced 2,537 warning lines, including template-form/inheritance warnings, repeated references and unresolved assets. The missing-reference scan extracted 33 distinct paths under its stated patterns. These warnings were not suppressed and are not all proven harmless. The new content is a development library that requires item-by-item testing; the PDF includes the validation inventory and the earlier audit for context.

The remaining practical checks are login and owner commands after reopening the client; resource creation and crafting; skill training/surrender and persistence; a normal trade/group test with two clients; house/deed placement and stored items; the Han/Chewbacca quest; and standard JTL launch, movement, combat, docking and relogging. New planets and complete expansion questlines require separate dependency and progression work.

## Backups, recovery and private information

Back Up SWG Galaxy.cmd is the reusable backup shortcut. It takes a lock, saves/stops a running galaxy, exports the game SQL database, archives Berkeley DB world saves with the server source, Git history, executable and settings, preserves the existing database login/grants, copies client preferences and service metadata, verifies archive contents/checksums, copies the snapshot into outputs/Backups, and restarts a galaxy that was previously running.

The earlier baseline snapshot is baseline-before-maintenance-20261013T122253Z. The pre-sandbox/content snapshot is before-sandbox-and-content-20261013T124400Z. UTC stamps in folder names differ from Pacific display time. Each snapshot contains recovery notes and a manifest. The first snapshot predates Mantis disabling and the final admin-role restoration; the second is the clean pre-sandbox comparison point.

TRE archives and the full client are not duplicated in every galaxy backup. They remain in their installed folders and in the new content library; manifests identify their hashes. This is a galaxy recovery backup, not a full Windows/WSL disk image. A restore into a separate disposable galaxy has not yet been rehearsed.

Restore only with the server stopped. Preserve the current state first, then restore matching SQL and Berkeley DB files from the same snapshot, source/configuration/executable and compatible assets. Restore file ownership and service configuration; recreate the database login only when needed on a fresh database server. Refresh the WSL connection address with the Start launcher. Never combine SQL from one snapshot with world saves from another.

Backups contain private account hashes and database secrets. The owner password remains in SWG-login.txt. This PDF deliberately omits those values, the database password and the database secret, while recording where the private operational files live.

## Everyday sandbox use

Start the galaxy with Start SWG Server.cmd and wait for readiness. Reopen the client to load its new asset list and saved window settings. Use Play SWG.cmd again for another instance. Use Stop SWG Server.cmd to save and stop before rebooting. Use the backup shortcut before additional edits.

On the owner character, create a fresh character builder with /object characterbuilder and open MTG Content Library. For resources, obtain a Resource Deed from Deeds or create object/tangible/veteran_reward/resource.iff. The updated deed quantity is 100,000 units. /resource list tatooine lists generated resources; /resource create NAME 100000 creates an existing named resource stack. /resource perfect steel_duralloy creates a separate perfect-stat test resource; use the generated name reported by the server.

The example quest can be found near /teleport 3565 -4795 tatooine. Use ordinary test characters as well as the owner when validating normal gameplay. Administrator spawning and a clean startup do not establish normal acquisition or crafting correctness.

## Supporting material and scope of this export

The PDF appends the exact settings and installation/validation manifests, the original research reports and warning inventory, a file/change index, and the user-request history retrieved from this conversation. Historical appendices describe earlier states and are explicitly marked; the current-state chapters and final manifests take precedence.

This is a project documentation export, not a byte-for-byte dump of internal reasoning or every tool response. It records the consequential actions, decisions, fixes, failed attempts, artifacts and evidence available in the chat and workspace. The original chat remains the full interaction record. The underlying source archives, startup log, hashes, scripts and backup manifests provide the detailed operational evidence without placing private credentials in the PDF.
