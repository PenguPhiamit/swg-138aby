# Roadmap

Where this server stands and where it's going, in plain words. Last updated 19 October 2026.

## What this is

This is a personal, non-commercial Star Wars Galaxies server. It is built on SWGEmu's Core3. The game rules are those of SWG before the Combat Upgrade ("pre-CU"). The new content is set in Star Wars Legends around 138–139 ABY. At that time, Darth Krayt has just died for good, the One Sith have gone underground, the Jedi are in hiding, and the academy on Ossus is in ruins.

It isn't open to the public. A small friends-only test comes first. The [README](README.md) explains what a public server would be like if there is one later.

New work goes onto the **test galaxy** first. This is a private copy of the server that can be reset. Test bots and the owner play on it. The live server is switched off for now.

**How to read the status words**

- **Done**: tested in the game and working. Built isn't enough.
- **In testing**: on the test galaxy, being played and fixed.
- **Built, not installed**: made and checked outside the game, waiting for its turn on the test galaxy.
- **Planned**: designed or only an idea. Plans change.

## Done

**The server and its safety net**

- Core3 builds and runs. Backups work. A full restore from a backup has been tested and passed.
- The test galaxy can be started, stopped, and picked up again where it left off.

**The base game, checked by test bots on the test galaxy** (17–18 October)

Test bots log in through the real game protocol. They play like players by fighting, traveling, crafting, and taking missions. They report what works and what does not. So far, we have checked:

- character creation for every species and gender (before Nautolan and Togruta were added);
- crafting, 21 of 21 checks;
- death, cloning, and insurance, 11 of 11;
- shuttle travel, 66 of 73 trips;
- missions at 9 of 11 kinds of mission terminals, with the right pay;
- pets: storing and repairing a pet;
- a fix that keeps new characters away from much stronger creatures (such deaths fell from about one in four to one in twenty in bot runs).

The bots' full regression check last passed on 17 October.

**Other things that work**

- A mercenary broker in Mos Eisley: you can hire companions to follow you. It is not yet proven if they help in a fight.
- The test tools: a squad of test bots, a bot population of up to 1,700 for load tests, and tools to read and write SWG file formats.

## In testing

| What | Where it stands |
|---|---|
| **Hoth** | Travel from Corellia works both ways. Echo Base, the Scavenger outpost, ice caves, creature dens, a quartermaster's job chain, Hoth resources, and named loot are in. Open: walking into Echo Base, its snow-filled hangar mouth, the bare north-west plateau, and Hoth's release check. |
| **Ossus** | The old Jedi world. The terrain was built from scratch with our own tools. It includes the One Sith in the caves, the spirit of Ood Bnar, and the ghostfire quest. It is still being filled out. |
| **Nal Hutta** | One town with townsfolk, wildlife, a few encounter sites, and a short quest. This is about half of what a stock planet has. |
| **Ghostfire crystal** | A lightsaber crystal with an almost invisible blade. Its colour shows in the trails, which shimmer with oil-slick hues. It is being tuned. |
| **Light whip** | A one-handed lightsaber variant. It is a 4.5 m strand that bends like a rope with the graphics hook. It was first tried in game on 19 October and was well liked. It needs its own animations. |
| **Graphics hook** | An optional client add-on for the light whip's bend and a heat haze around ghostfire blades. Without it, the game looks stock. |
| **New species** | Chiss are at character creation. Nautolan (male) and Togruta (female) went onto the test galaxy on 19 October but have not been checked in game yet. |
| **Missions** | Bounty missions and group pay are still open from the mission checks. |

**Built, not installed:** the light whip as a drop from the krayt dragon world bosses, and its crafting schematic for master weaponsmiths with Lightsaber Technique I and for Lightsaber Masters. A playable Hutt is still being worked out.

## Now: getting ready for the friends test

The rule for this stage is to test the whole game before adding more content.

1. **Finish the base-game checks:** trainers, vehicles and mounts, doctor and entertainer buffs, gas, moisture and wind surveys, groups, mail and guilds, the bazaar, vendors and trade, and housing, harvesters, cities and factions.
2. **Fix what the tests and code reviews find.** Nothing goes live without a second review and the owner's OK.
3. **A dress rehearsal** with the live server's settings.
4. **A client patch and installer for friends**, so they get the new planets' data and the optional graphics hook.
5. **The owner's go**, then the friends test opens.

What friends get: the ten original planets, the tutorial, the Corvette dungeon, and Hoth once it passes its release check. Ossus and Nal Hutta stay closed until their content is in and tested. Each planet is judged again at launch.

## Next

Once the base game is tested, we will work in roughly this order:

- **The next new planet**, built with the kit made for Hoth and Ossus. Candidates are Kashyyyk, Mustafar, or a world from the KOTOR games. KOTOR worlds would be rebuilt from public descriptions using SWG's own art, starting with the Dantooine Jedi Enclave ruins. No files from the KOTOR games are used.
- **More species** from public species packages, including Zeltron.
- **Resources and crafting:** an in-game board showing the resources spawning now, with their stats and survey waypoints.
- **A world that feels lived-in:** NPC adventurers who travel, hunt, and spend time in cantinas.
- **Feedback from players:** a Discord feed and an in-game way to report bugs.
- **The light whip, finished:** its own moves, a coil at the wielder's feet when idle, a hilt model, a crack sound, and its parry and blocking trade-offs.

## Later ideas

These are not promised and are not in order:

- Battlefront-style battles: capture command posts and run down the other side's reinforcements on a Hoth or Ossus battlefield.
- An AI player that plays its own character, hires companions, runs dungeons, and writes test reports.
- More worlds with published scripts to build on, such as Taanab and Mandalore.
- Content that was planned for the original game but cut, rebuilt from public sources and our own client files.

## How it's built

- Most of the engineering is done by AI agents under the owner's direction. The owner sets priorities, plays the game, and makes the calls. See the [README](README.md).
- Lore comes from Wookieepedia's Legends articles, written in our own words.
- Nothing leaked or not-for-distribution is used, and no game client files are included. Credits are in [NOTICE.md](NOTICE.md).
- The agents' own working checklist, with task codes and dates, is [outputs/SWG-roadmap.md](outputs/SWG-roadmap.md). The day-to-day log is [outputs/SWG-handoff.md](outputs/SWG-handoff.md).
