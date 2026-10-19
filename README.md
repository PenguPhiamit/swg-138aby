# Star Wars Galaxies, 138 ABY

A personal, non-commercial project: a private SWGEmu (Core3) server that keeps pre-Combat-Upgrade Star Wars Galaxies
as it was and builds on it. The new content is set in the Legends era around 138–139 ABY, after Darth Krayt's fall:
new planets, playable species, creatures and story, plus a population of bots that play the game through the real
client protocol to test it.

## How it started

What began as a way to preserve the pre-CU era with bots on a private LAN has grown into a much wider project. The bots
log in through the real game protocol and play the professions, and they still test everything that goes in. From there
the world kept growing: Hoth, Ossus and new species, set around 138 ABY, along with a light whip and ghostfire crystals.
New professions might be possible one day, but for now it stays small, with a friends-only test first.

## What's here

Status words: **on the test galaxy** means installed and being played and tested; **staged** means built and checked
offline but not installed yet; **planned** means not started. Nothing is open to the public yet.

| Area | What | Status |
|---|---|---|
| Hoth | Travel from Corellia, Echo Base, the Scavenger outpost, ice caves and creature dens, Quartermaster Vell's job chain, Hoth resources and named loot | On the test galaxy |
| Ossus | The old Jedi world, with terrain built from scratch by our own tools (Knossa, the Academy benchland, Imhar Canyon), the One Sith in the caves, the spirit of Ood Bnar | On the test galaxy (still filling out) |
| Ghostfire crystal | A lightsaber colour crystal with an almost invisible blade and its own blade shader: the colour is in the trails, which shimmer through oil-slick hues in any hilt | On the test galaxy (being tuned) |
| New species | Chiss at character creation | On the test galaxy |
| More species | Nautolan (male) and Togruta (female) at character creation | Staged |
| Light whip | A one-handed lightsaber variant: a 4.5 m strand with more reach than a saber and weaker against armour, which bends like a rope with the graphics hook. Krayt dragon bosses drop it, and a Master Weaponsmith with Lightsaber Technique I or a Lightsaber Master can learn its schematic | On the test galaxy; the drop and the schematic are staged |
| The Hutt | Can be created; can't be played yet, because the pre-CU client won't drive the Hutt body as a player. Nal Hutta as its home world | Staged, in research |
| Backports | Vehicles and items from Mod the Galaxy, new creatures and enemies | On the test galaxy |
| The base game | Fixing what was left thin or broken: professions such as Image Designer and Politician, Creature Handler and Bio-Engineer pets, missions and bounties | In progress |
| Test bots | A squad of 24 bots that log in through the real game protocol, play the professions and report what works and what doesn't | On the test galaxy |
| Bot population | Up to 1,700 bots that live in the world (hunting, travelling, exploring) for load tests and launch rehearsals | On the test galaxy |
| Graphics hook | An optional client add-on in front of DXVK: the light whip's bend and a heat haze around ghostfire blades, each switched in game (Ctrl+Shift+B, Ctrl+Shift+M); without it the game looks stock | On the test galaxy; the friends' launcher installs it |
| Tools | Readers and writers for SWG's file formats (TRE, IFF, terrain), content builders with offline checks, a live map and a Discord feed | In use; the map and feed are staged |
| Next places | Kashyyyk and Mustafar; places from KOTOR rebuilt from public descriptions with SWG's own art (the Dantooine Jedi Enclave ruins first) | Planned |
| An AI player | An agent that plays a character and learns, under strict safety rules | Planned |
| Light whip, next | A hilt model (credited), a crack sound, a coil at the wielder's feet when idle, and the parry and blocking changes | Planned |

A small friends-only test comes first. The whole plan, with dates, is in
[outputs/SWG-roadmap.md](outputs/SWG-roadmap.md).

## If there's a public server

If I do open a public or whitelisted server after the friends test, it will be in early alpha for a while. If you
join, this is what to expect:

- **Expect wipes.** Characters, skills, items, credits, houses and resources can all be reset, maybe more than once,
  whenever a change needs a clean start: a rebuilt planet, a reworked profession, an economy that went wrong. I'll
  warn on the Discord before a planned wipe whenever I can, but nothing is promised to carry over.
- **Progression is sped up to make up for it.** Experience and the slowest grinds run faster than in the original
  game, so a wipe costs you days rather than months. The speed-up is there because of the wipes, and it gets looked
  at again once they stop.
- **Things will break.** Content is unfinished, planets that aren't ready stay closed, and there will be restarts,
  rollbacks and downtime while fixes go in. Bug reports are the most useful thing you can give back, and they decide
  what gets fixed first.
- **A whitelist to start.** A small group keeps the server at a size where problems can be found and fixed. It may
  open wider as it settles.
- **Then a stable live point.** When the server gets there, I'll announce it here and on the Discord. From then on
  characters are meant to last, and a wipe would be a last resort.

You'll need your own copy of the original SWG client to play; the server's patch goes on top of it. Like the rest of
the project, the server is non-commercial.

## Goals

- Keep the pre-CU game as it was, and finish what was left thin or broken.
- Add places and story that fit the setting, in our own words.
- Make testing cheap and honest: bots that play each profession and report what works and what doesn't.
- Give back. This repository is open source now, under the AGPL-3.0. Anyone may read it, learn from it and reuse it
  under that licence, as far as I can share it while respecting the developers whose work it builds on. I'm here for
  the love of the game, not for profit or clout.

## Transparency

- Most of the engineering and writing here is done by AI agents (Claude, ChatGPT/Codex and local models) working
  under my direction. I set the priorities, test in game and make the calls. Their task board, notes and reviews stay
  in this repository on purpose, so anyone can see how each piece was made and checked.
- It builds on other people's open work under their own licences: SWGEmu's Core3, Mod the Galaxy, TortoiseBots (with
  its author's permission) and Wookieepedia for lore (our text is our own). Credits are in [NOTICE.md](NOTICE.md);
  the repository is licensed under the AGPL-3.0, the same licence as Core3 ([LICENSE](LICENSE)).
- No leaked or not-for-distribution code or assets are used, and no game client files are included. I love this game;
  it holds some really precious core memories for me from when life was good still. I ain't here to hurt people.

## Finding your way around

This is a working project, not a polished release, and there's no installer for other people yet. Running it needs
your own copy of the SWG client and a Core3 build.

- [outputs/SWG-handoff.md](outputs/SWG-handoff.md): the agents' task board and log, newest first.
- [outputs/SWG-roadmap.md](outputs/SWG-roadmap.md): the plan, by phase.
- [outputs/tools/](outputs/tools/): the bots, the file-format tools and the build and check scripts.
- `outputs/Fable-*`, `outputs/Hoth-*`, `outputs/Vong-look/` and similar folders: content batches, each with its own
  README, patch and checks.
- [outputs/Bot-reports/](outputs/Bot-reports/): what the bots found, run by run.
- [outputs/Documentation-support/](outputs/Documentation-support/): designs, reviews and test plans.

## Working together

If you run or develop an SWG server and would like to work together, share ideas or use anything here, I would love
to hear from you, whether that's the teams behind Empire in Flames, Sentinels Republic or Restoration, SWGEmu
themselves or anyone else. Every one of those communities has kept this game alive, and I have nothing but respect for
them. The only line I keep is for this project's own code and assets, as above. A Discord server is coming and its link
will be posted here; until then, message me on GitHub.

Discord: *link coming*
