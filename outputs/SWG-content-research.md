# SWGEmu content and setup audit

Researched October 13, 2026. This audit read the running installation, public SWGEmu source and accessible project documentation. It made no changes to the running galaxy, client, feature switches or credentials.

For subsequent maintenance and the current setup state, see [the developer baseline review](SWG-developer-baseline.md). That maintenance created a verified galaxy snapshot, installed GDB, disabled the unused Mantis connection and restored the admin-role file to upstream. The findings below describe the earlier research state unless stated otherwise.

**The main finding**

The warnings do not establish that the base game is missing. All 51 archives named by the installed Core3 configuration exist. The server folder contains 53 archives, but presence in that folder does not automatically mean an archive is loaded: the configuration lists the archives explicitly.

The logs contain 35 distinct missing-path or missing-appearance references. Of those, 28 concern ships or space: 24 chassis tables, three ship client-data files and a Corvette interior appearance. One of the other warnings names an effect file that is present and readable; the server does not instantiate its particle format. Other references need individual review before being called harmless or broken.

**What is installed**

| Component | Verified state |
|---|---|
| Server | Public SWGEmu Core3, `unstable` branch |
| Server revision | `403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79`, October 1, 2026 |
| Engine revision | `4cbf39336e0e727dfef861fbe65bd303ce70fd37` |
| Client | Pre-CU executable and patch set, built from the supplied Complete Online Adventures assets and official launcher downloads |
| Game database | Active; schema version 1008 |
| Ground game | Login, character creation and tutorial/world entry demonstrated; broader gameplay tests remain in progress |
| JTL | Code and space zones exist, but `Core3.JTL.JTLEnabled` defaults to false and has no local enabling override |
| Kashyyyk and Mustafar | Not enabled as destinations in the installed ground-zone configuration |
| Platform | Debian 13 under WSL 2; official build instructions list Debian 12. This build compiled and starts, but that is a reproducibility difference to record |

The branch name is not a guarantee about stability. Pin the server and engine revisions before adding content so future failures can be compared against a known baseline. See the [official repository and setup instructions](https://github.com/swgemu/Core3).

**Missing-content findings and their implications**

| Finding | Evidence | Implication / next action |
|---|---|---|
| Missing ship chassis tables | `ShipChassisData::loadComponentHardpoints()` asks for a table for each chassis and returns when the file is absent | These are tolerated lookups, not startup failures. The affected ship's hardpoint data still needs testing before it is considered supported |
| ARC-170 and Jedi Starfighter player tables | Both were found in the supplied disc's `patch_15_00.tre` and `patch_17_00.tre`, outside the configured pre-CU archive set | Some content is on the disc but intentionally outside the installed load list. Review individual assets and dependencies; do not load whole later patches into the working pre-CU client |
| Missing transport/escape-pod client data | `ShipCollisionData::setClientData()` returns when the requested client-data file is absent | Startup tolerates this, but the affected ship's attachment/collision data is not thereby verified |
| `appearance/pt_light_indoor_glow.prt` | Found in the loaded `patch_07.tre`; its IFF form is `PEFT`. `TemplateManager::instantiateAppearanceTemplate()` leaves `PEFT` uninstantiated | This warning is a server particle-format limitation, not a missing download |
| `snapshot/tutorial.ws` | The snapshot loader returns if a snapshot is absent. `TutorialScreenPlay` creates a per-player tutorial and spawns its objects | Consistent with the scripted tutorial. Completing the tutorial remains a better acceptance test than eliminating this warning |
| `godclient_cylinder_30.apt` | Referenced by no-build/developer-marker object templates | Likely a developer/helper-object reference. That is an inference from its use, not proof that every affected template is irrelevant |
| `particle_test_31.prt`, waterfall appearance and vehicle base-template lookups | Absent from the decoded configured archive indexes | Still unresolved. Check the specific object, inherited template or location before adding replacements or suppressing warnings |
| Station template warning: expected `SHOT`, found `SSHP` | The loaded shared ship base is present and has form `SSHP` | A template-type/inheritance warning, not an absent archive. Review before treating the affected station templates as correct |

Source references: [ship hardpoint loading](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/ship/ShipChassisData.cpp), [ship client-data handling](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/objects/ship/ShipCollisionData.cpp), [appearance format handling](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/templates/manager/TemplateManager.cpp), [snapshot loading](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/zone/managers/planet/PlanetManagerImplementation.cpp), [tutorial script](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/bin/scripts/screenplays/tutorial/tutorial.lua).

**Jump to Lightspeed and expansions**

Pre-CU does not exclude space gameplay. The installed public source has substantial JTL systems: ship components, flight/combat, hyperspace, AI, pilot conversations and missions. However, the configuration getter defaults JTL to off, and several pilot conversations explicitly check that switch. Loading space zones is separate from enabling those gameplay paths. See the [JTL configuration getter](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/conf/ConfigManager.h) and a [pilot recruiter conversation](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/bin/scripts/screenplays/space/conversations/neutral/gilBurtinConvoHandler.lua).

Neither an expansion disc nor a recent Core3 checkout guarantees a complete expansion experience. The client assets, server logic, Lua content, enabled zones and progression need to agree. A community server's advertised features also do not prove that its full implementation is in the public Core3 checkout. For example, the [New Foundations development diary](https://www.swgnfs.com/updates) describes its own JTL and Kashyyyk work, including ongoing quests, and describes its development as closed-source. That is evidence of the team's progress, not an installable content package for this server.

An old JTL beta download appeared in search results. It was not installed or treated as a verified current requirement. A version-matched patch recommendation needs stronger evidence than an old announcement.

**Other setup findings**

- The first-start `db_metadata` error was followed by automatic schema creation/upgrades. The current schema is 1008. The code explicitly handles that initial missing table; it is not an outstanding missing-content issue. [Schema initialization](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/db/ServerDatabase.cpp).
- The revision-info file was added earlier; the initial missing-file message is historical.
- The Mantis connection error remains: the optional bug-report integration has separate credentials. The main game database connects successfully. A later maintenance change can either configure this integration correctly or disable it by leaving its host empty, which the constructor explicitly supports. No credential changes were made during this audit. [Mantis initialization](https://github.com/swgemu/Core3/blob/403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79/MMOCoreORB/src/server/db/MantisDatabase.cpp).
- Admin commands require both server permission and the client's admin-command setting. The added client setting resolved command entry in the user's test. The earlier client privilege-flag change was not sufficient by itself. [Client setup reference](https://github.com/[name removed]/mtgserver/wiki/Guide-Client-Setup).

**What matters when we add custom content**

1. Keep server code, Lua content, client patches and archive load order together as a versioned change. A `.tre` copied into a folder is not automatically active.
2. Prefer a small content addition with a clear test case. Importing a large community fork can bring different combat rules, schemas, templates and client dependencies.
3. Back up both the SQL account/character metadata and the Berkeley DB world/object data, plus configuration and custom assets. A SQL-only backup is not a complete galaxy backup.
4. Separate editable Lua quests/spawns from C++ game-system changes, which require rebuilding. Confirm a reload mechanism exists for the specific subsystem before assuming Lua edits are live.
5. Build a feature acceptance checklist: an admin can spawn something without proving its normal acquisition, crafting, mission progression or combat works for ordinary players.

**Recommended next sequence**

Finish the ground-game tests already in progress. Then capture a complete baseline backup and resolve the optional reporting configuration during planned downtime. Test JTL separately with a normal account and a compatible ship/pilot path; enable it only as a deliberate feature change. Investigate the 28 space-related references against that test scope. Bring in expansion/community content one dependency-reviewed package at a time.

**Research limits**

SWGEmu's main site and forum pages initially returned access errors through web search. Their public source was available locally from the official repository, so the conclusions above rely primarily on the installed code and actual archive indexes. Later in the session, the public forum loaded through the in-app browser, and its latest-commit listing confirmed the installed `403893d9` revision. The user then signed in manually, and the development documentation and discussion threads were readable in that session. Web-cached GitHub commit pages were older than the installed revision.

The index audit successfully decoded 116 version-0005 archives across the server set and supplied disc. An additional 59 version-0006 disc archives were not decoded. Consequently, “not found” in the companion inventory means not found in the decoded indexes; it does not prove the asset is absent from every later file on the disc. No full later patch was loaded or converted.

**Signed-in forum research: custom content and JTL**

The [Development Documentation index](https://www.swgemu.com/forums/showthread.php?t=120093) is now accessible. It collects administration, screenplay scripting, NPC/object spawning, sample quests, and client asset tools. Its index was last updated in January 2016, so use it to locate concepts and tools, then check implementation details against the installed revision.

The developer-written [Screenplay Scripting Basics 101](https://www.swgemu.com/forums/showthread.php?t=41925) explains how Lua screenplays create NPCs, objects, event callbacks and quest behavior. This is the practical starting point for our own quests and populated locations using existing game assets. The installed tutorial and space scripts still use the same basic registration and observer mechanisms. One concrete difference: the old guide adds an include to `screenplay.lua`; the current content loader is `bin/scripts/screenplays/screenplays.lua` (plural), which loads the base class separately. Its sample also varies capitalization in its screenplay name; our own script should use one exact name consistently.

Useful next references are [spawning scene objects](https://www.swgemu.com/forums/showthread.php?t=61268), [spawning and modifying mobiles](https://www.swgemu.com/forums/showthread.php?t=61337), and the [sample quest](https://www.swgemu.com/forums/showthread.php?t=61881). The index also links [Sytner's IFF Editor](https://www.swgemu.com/forums/showthread.php?t=154893) and a [TRE archive viewer](https://www.swgemu.com/forums/showthread.php?t=68180). These were identified as references; no additional tools were installed or tested.

The official [March 30, 2025 development update](https://www.swgemu.com/forums/showthread.php?t=258477) records work on droid command-chip programming, astromech certification and flight-computer deed fields. This supports treating JTL as substantial ongoing implementation rather than assuming all space warnings mean unsupported content. It does not establish complete expansion coverage for our October 2026 checkout.

In [JTL - Controls messed up?](https://www.swgemu.com/forums/showthread.php?t=257227), a developer reports successfully walking inside a Sorosuub Yacht on TC-Prime; the original reporter later says their movement issue cleared on Nova. This is a useful example test for passenger ships, not proof that our local server or every PoB ship works. The [JTL and Atmospheric flight discussion](https://www.swgemu.com/forums/showthread.php?t=258089) includes community reports of JTL testing on Nova and TC-Prime, but does not provide a verified atmospheric-flight implementation or a version-matched local patch recipe.

The [project status list](https://www.swgemu.com/forums/showthread.php?t=75) labels its feature inventory July 31, 2023, despite a later post-edit date. Its colors and completion claims should not substitute for tests of our installed revision. Its Mantis instructions concern reporting issues to the project; running a separate Mantis service is not a prerequisite for our local crafting or content work.

No server switches, account permissions or client assets were changed during this signed-in research. The next content milestone remains a complete baseline backup, followed by a small original NPC/quest using existing assets. JTL deserves a separate enable-and-test pass; no current mandatory JTL client patch was verified in the pages read here.
