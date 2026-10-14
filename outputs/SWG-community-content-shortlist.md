# Community content shortlist

Researched October 13, 2026. Public source was downloaded into separate research folders for inspection. No downloaded scripts, plugins, launchers or binaries were executed, and no content was installed into the galaxy or client.

The strongest starting point from this first pass is **Mod the Galaxy's published content catalog**, followed by selected server changes whose individual permissions and dependencies are clear. A public Core3 fork is not necessarily a complete copy of the server's original quests, planets and artwork.

## Optional changes from the earlier discussion

These were community gameplay choices, rather than required setup fixes:

| Type | Examples |
|---|---|
| Progression | Higher XP rates, faster Jedi/Village progression |
| Crafting | Shorter crafting and factory timers, larger resource stacks/deeds, perfect test resources |
| Building and economy | Lower maintenance/training costs, more house storage, fewer residents needed for city ranks |
| Character limits | More simultaneous characters, extra skill points beyond the normal cap |
| Travel | Faster speeders and shorter shuttle waits |
| Additional features | Deliberately enabling and testing JTL, or adding planets and content packs |

We did not apply these changes. JTL is a separate feature choice, not a shortcut in the same sense as higher XP. The baseline maintenance instead addressed backups, debugging support and the unused Mantis connection.

## Sources checked

| Source | What is actually available / stated | Assessment |
|---|---|---|
| [Sentinel's Republic newer public repository](https://github.com/swgsremu/sentinelsrepublic-server) | Core3 fork with server modifications. Checked revision `5df918b48f9fe011e93738c539311778906e189f`, December 10, 2025. | Useful for inspecting selected changes; not verified as a complete original-content release. |
| [Sentinel's Republic legacy repository](https://github.com/DesporoWace/SWG-SR) | This is the repository linked by the server website's Public Repository link. Checked snapshot `75f5a9f8a808204d23d84d0a0b6ca15ecab9deb3`, March 27, 2020. | Historical reference. Its age makes wholesale replacement of our October 2026 Core3 installation a poor fit. |
| [Mod the Galaxy repository and wiki](https://github.com/ModTheGalaxy/mtgserver/wiki) | The wiki offers contributed content for other servers with creator credit. Checked repository branch `update-wip`, revision `54deb619e83c2c5e353f6a825a829d56201704f0`, October 3, 2025. | Best first catalog for small, selected additions. Check individual file notices and credits too. |
| [Sunrunner II](https://swgsunrunner2.com/about/) | Describes public server code, private original Lua scripts, and artwork for which its team requests permission and credit. | Strong design reference; its launcher assets should not be treated as a blanket reuse package. |
| [Empire in Flames](https://www.empireinflames.net/?page_id=985) | Credits document shared planets, screenplay exchanges and separately credited artwork. Its current site describes original quests and seasonal events. | Useful ideas and possible author-approved contributions. No complete reusable content package was verified in this pass. |

## Sentinel's Republic findings

The [official site](https://swgsremu.com/) advertises additional planets, species, quests, dungeons and later-era items. Those feature descriptions do not establish that all the corresponding implementation is published in its newer repository.

At the checked newer revision, `MMOCoreORB/bin/scripts/screenplays/screenplays.lua` includes `../custom_scripts/screenplays/screenplays.lua`, but Git's tracked tree contains **no entries under `MMOCoreORB/bin/scripts/custom_scripts/`**. The legacy `bin/custom_scripts` directory contains pointers and a readme referring to that location. Consequently, the public checkout alone does not supply that referenced content folder.

A concrete permission issue also appears in [autoEntertain.lua](https://github.com/swgsremu/sentinelsrepublic-server/blob/5df918b48f9fe011e93738c539311778906e189f/MMOCoreORB/bin/scripts/commands/autoEntertain.lua): its header identifies Wasted Potential Studios and says “Proprietary code and work not for distribution.” This is a separate notice alongside the repository's AGPL label. Leave that particular contribution out of an import until its permission is clarified; do not generalize the notice to every file in the fork.

The older repository has additional region definitions and some script differences, but its inventory does not establish that current advertised dungeons are available as self-contained packages. Neither SR snapshot was built or tested locally.

## Mod the Galaxy findings

The checked source contains **14,010 Lua files under `object/custom_content`** and **2,719 under `mobile/custom_content`**. These are file counts, including supporting definitions and conversations, not counts of complete playable items or quests. There are four files under `screenplays/custom_screenplays`, including two versions of the same tutorial and a blank base; that is not four finished quests.

Its configuration names a separate MTG archive set, including `mtg_planets.tre` and `mtg_patch_001` through later patches. Our client/server currently use the stock pre-CU archive set. Copying these Lua definitions alone would not supply their models, shared templates, sounds, terrain or other client data. Archive download availability and checksums were not verified here; a forum link to the archive collection returned the forum landing page through the research browser tool.

Concrete candidates inspected:

| Candidate | Files / behavior inspected | Suitability |
|---|---|---|
| Small furniture addition | [Rustic armoire schematic](https://github.com/ModTheGalaxy/mtgserver/blob/54deb619e83c2c5e353f6a825a829d56201704f0/MMOCoreORB/bin/scripts/object/custom_content/draft_schematic/furniture/furniture_armoire_rustic.lua) registers a schematic derived from a shared template. | A manageable first item investigation. Still needs the crafted item, shared data, ingredients, skill/vendor acquisition and client assets traced. Not ready to install from this one file. |
| Example quest | [The Beginning tutorial](https://github.com/ModTheGalaxy/mtgserver/blob/54deb619e83c2c5e353f6a825a829d56201704f0/MMOCoreORB/bin/scripts/screenplays/custom_screenplays/the_tutorial/the_tutorial_0001_the_beginning.lua) demonstrates Han/Chewbacca, an area trigger, conversation states and a credit reward. | Good framework to adapt using verified existing assets. References custom NPCs, later sounds and a fixed interior cell ID; those need adjustment/verification before use. |
| YT-1300 house | [House definition](https://github.com/ModTheGalaxy/mtgserver/blob/54deb619e83c2c5e353f6a825a829d56201704f0/MMOCoreORB/bin/scripts/object/custom_content/building/player/yt1300_house.lua) contains lots, maintenance, terminals, elevators and many sign options. | Attractive later project. More dependencies and persistence tests than a small decorative item. |
| Kashyyyk Bolotaur | [Mobile definition](https://github.com/ModTheGalaxy/mtgserver/blob/54deb619e83c2c5e353f6a825a829d56201704f0/MMOCoreORB/bin/scripts/mobile/custom_content/kashyyyk/bolotaur.lua) exists, but the inspected version has no combat attacks, no loot and `pvpBitmask = NONE`. | Demonstrates why an expansion NPC definition is not proof of a complete expansion encounter. |

Later-era artwork and objects can be considered individually while retaining pre-CU combat and professions. Installing an entire server fork would bring additional rules and system changes that we have not selected.

## Recommended first content pass

1. Keep the current galaxy baseline and its backup as the comparison point.
2. Select a small MTG item or an example quest, then list every required server file and client asset plus its creator/notice.
3. Adapt the package to the pinned Core3 revision in a separate development copy. Give it a clear credits entry and installation/removal notes.
4. Test normal acquisition and use, relogging and persistence, then check startup logs. For crafting, verify the whole schematic-to-item path rather than only spawning the finished item.
5. Add houses, new planets and large expansion systems after that import process works reliably.

The research copies are under `work/research/`; they are reference material, not the live server. No third-party server was contacted by message, and no permission request was sent to a content creator.
