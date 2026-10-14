# Content research gap-check (Claude, 13 October 2026)

The earlier ChatGPT research covered Mod the Galaxy, Stardust/DLSWG5, Empire in Flames, Sentinel's Republic (now excluded), Sunrunner II, Uprising, Infinity, Legend of Hondo, SWG-Forge, SWG-Source (dsrc/serverdata/mesh) and twistedatrocity's mods. This pass looked for **public sources that research missed**, with a focus on our build: Core3 pre-CU, one owner, local only.

Method: I made blobless Git clones (file lists and history only: no checkout, nothing built or run) and compared each file tree with our upstream base `403893d9`. I then subtracted what our MTG import already provides and read the READMEs and design docs. Nothing was installed. Revisions are in [gap-check-evidence.json](Content-catalogue/gap-check-evidence.json). The clones are in `work/research/gap-check` (36 MB).

## Headline findings

1. **Upstream is current.** Our pin `403893d9` is the newest `unstable` commit on GitHub (1 Oct 2026). Gerrit has 4 open changes. Two are worth watching: *"shutdown with no timer could hang the server on a lost wakeup"* (relevant to our graceful-stop launcher) and a WIP *"Revamped 14.1 Player Tutorial"*.
2. **Bellum Gero is the best new content source.** It's AGPL, actively developed (commits on 12 Oct 2026), and built on a recent Core3 (behavior-tree AI). Its **Hoth** has outposts, starports, fortified shuttleports, wampa caves, cave bosses, the Glacial Rancor world boss, Hoth missions, and Hoth resources. It also ships **~60 standard-library Python tools for adding planets**: TRE pack/merge/verify, IFF/datatable/STF/CRC editors, dependency-closure and terrain inspectors. Those tools fit our MTG Hoth terrain directly.
3. **Flurry has the largest collection of server-side scripts for MTG-era planets.** Beyond what we already have from MTG, it adds about 8,500 script files. They include screenplays for Mandalore, Taanab, Kashyyyk (Kachirho), Mustafar, Nal Hutta, Hoth Echo Base, Coruscant and Dagobah. It also has dungeons (Exar Kun, ISD, IG-88, Avatar Platform, Myyydril, Nightsister), 15 rotating world bosses, 30 Gray Jedi trials, events (Life Day, Halloween, CoA, droid racing), ~1,660 loot files, CU armor and post-14.1 weapons. The catch: it runs on the **old AI system**, so it needs porting, and some content depends on Flurry's own TRE download.
4. **There's a ready-made basis for a bot framework.**
   - Core3 already contains a C++ test client (`src/client`: login, create character, zone-in, logout). It's switched off in our build (`ENABLE_BUILD_CLIENT=OFF`).
   - The official SWGEmu **Behavior Studio** edits Core3 AI behavior trees.
   - Two new 2026 clients (Unreal and Godot) document the protocol thoroughly.

**Excluded at the owner's request (13 Oct):** BorrieBoBaka/SWG_D20_RP_TC, including its Progor-Chat bot. The research clone has been deleted. Borrie's separate decor packs already in the catalogue are unaffected.

## New sources

Overlap means files we already have from the MTG import. Many old forks also carry about 1,450 `mobile/lair` files. Those are an old upstream layout, not new content.

| Source | What's genuinely new to us | Base / activity | License | Fit and next step |
|---|---|---|---|---|
| [Miphstoe/BellumGero-Live](https://github.com/Miphstoe/BellumGero-Live) | Hoth planet (22 mobiles, missions, caves, POIs, world boss), `tools/newplanets` (60 py), `tools/worldbuilder`, Discord manager (C++), house pack-up, world reset, live resource exporter, Image Designer station, vendor search waypoints, name-change service, 45 Bellum screenplays, ~1,690 script files | Recent Core3 (behavior-tree AI, pre-SWGRealms); daily commits | AGPL-3.0 | **High.** Use for our first new planet. Hoth client art comes from their private `bg_custom1.tre` (ported from Infinity), so pair their server scripts with our MTG Hoth terrain instead, and port only assets with clear permission. |
| [Thrax989/SWGFlurry](https://github.com/Thrax989/SWGFlurry) | ~8,500 new script files: planet screenplays for MTG worlds, dungeons, world bosses, Gray Jedi, events, POI waypoint helpers, buff terminal, custom loot, CU armor / post-14.1 weapons | Old Core3 (pre-behavior-tree AI); last push Feb 2023 | AGPL-3.0 | **High value, medium effort.** Port selected screenplays (the world boss rotation and Mandalore/Taanab content first). Check each one's template/asset chain against MTG before relying on Flurry's TRE download. |
| [SWG-Awakening/Awakening-Core3](https://github.com/SWG-Awakening/Awakening-Core3) | ~107 C++ object changes, AI/spawn manager tweaks, townsperson/AI mobiles | Old AI base; Jun 2025 | AGPL-3.0 | Low–medium. Mine individual fixes; don't merge wholesale. |
| [DetoxxeGaming/SWG-OrionDawn](https://github.com/DetoxxeGaming/SWG-OrionDawn) | 737 custom loot files, web servlets, events | 2018 | AGPL-3.0 | Low. Its loot tables are an alternative to Flurry's. |
| [XanderOlson/swgemu_single_player](https://github.com/XanderOlson/swgemu_single_player) | Solo tuning made with Codex: interplanetary travel override, fewer Jedi Knight trial kills, village unlock gate, force-XP conversion, vehicle decay, faster shuttles; **Lua spec tests + CTest in GitHub Actions** | Feb 2026, recent Core3 | AGPL-3.0 | **Medium.** Its test harness (`spec/helpers_spec.lua`, doctest units) is a good model for our own checks. Several tweaks overlap our sandbox. |
| [rambodolphin13/SWGEmu-Solo](https://github.com/rambodolphin13/SWGEmu-Solo) | "Perfect startup resources" baseline commit | May 2026 | AGPL-3.0 | Low. We already have `/resource perfect`. |
| [Skyyyr/rotf-os](https://github.com/Skyyyr/rotf-os) (Return of the Force) | Extra force/saber commands (Force Lightning 3–5, Force Throw 3, saber bleeds), custom professions | 2024 | AGPL-3.0 | Low–medium. Candidates for Jedi expansion. |
| [codeberg gitfitz1/SWG-Hunted](https://codeberg.org/gitfitz1/SWG-Hunted) | MTG named-crystal pack, loot items | Feb 2025 | (Core3 AGPL) | Low. |
| [swghardcore/public](https://github.com/swghardcore/public), [SWG-Animus](https://github.com/SWG-Animus/Animus-Core3), [chadeadams/SWG-Resurrection](https://github.com/chadeadams/SWG-Resurrection), [Tarkin II (kinshi)](https://github.com/kinshi/Core3) | Little distinct content: older bases, a single-zip upload, or an empty tree | — | AGPL-3.0 / none | Skip. |

## Tools

| Tool | Use for us |
|---|---|
| [swgemu/Tools](https://github.com/swgemu/Tools): Behavior Studio, WorldSpawnerTool (Java + Python), SWGHeightDump, CRCCalculator | AI behavior trees for bots/NPCs; planning spawn regions on new planets |
| [pickart/Behavior-Studio-SWGEmu](https://github.com/pickart/Behavior-Studio-SWGEmu) | Windows 11 / PySide6 port of Behavior Studio (v0.1.5, still being validated) |
| [jdswebb/swb-region-editor](https://github.com/jdswebb/swb-region-editor) | Region editing for new planets and cities |
| [Aliman00/convocreator](https://github.com/Aliman00/convocreator), [Slothicide drag-n-drop editor](https://github.com/Slothicide/Sloth-s-Drag-N-Drop) | Faster conversation / screenplay authoring |
| [monkjames/vsCode-sft-editor](https://github.com/monkjames/vsCode-sft-editor) | Edit `.stf` string tables in VS Code |
| [pwillworth/galaxyharvester](https://github.com/pwillworth/galaxyharvester) (Python, active) | Self-hosted resource tracker; pairs with Bellum's live resource exporter for the "resource board" idea |
| [czerkacorp/citadel-2018](https://github.com/czerkacorp/citadel-2018) | Account/web portal (Rails), only if the galaxy ever goes multi-user |
| [ptklatt/Utinni](https://github.com/ptklatt/Utinni) (MIT) | Client plugin/injection framework. Reference only; injecting into the client is outside our current scope |
| [brendenbowers/SWGEmuClient](https://github.com/brendenbowers/SWGEmuClient), [jebot-git/swgxr](https://github.com/jebot-git/swgxr) | Modern protocol implementations (handshake, CRC, encryption, compression, reliability, login/zone messages) with protocol docs. Bot references; no license file, so read, don't copy |
| [0x695/swgemu-status-bot](https://github.com/0x695/swgemu-status-bot), [TylerSchum Discord village bot](https://github.com/TylerSchum/Discord-Bot-Village-SWG) | Small Discord status/village-phase bots |

## Cautions

- **AGPL:** fine for private use. Obligations start only if we distribute the server or let other people connect. Keep credits with anything ported.
- **Client art is separate from server code.** Bellum's Hoth art and Flurry's TREs come from their own client packages. Our MTG archives are the cleared base. Run `dep_closure`/`chain_check` (Bellum tools) before porting a planet or dungeon.
- **Old-AI forks** (Flurry, Awakening, OrionDawn, Resurrection) use `ai/templates` names that current Core3 replaced with behavior trees. Mobile templates need their AI fields mapped. Screenplays mostly port with small API fixes.
- None of this has been runtime-tested on our galaxy.
