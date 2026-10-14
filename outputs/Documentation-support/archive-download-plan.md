# Archive download plan

Claude, 13 October 2026, for the owner's request: *"determine which things we can download to the archives and add to the plan, and then have codex download those."* The list comes from GPT's catalogue (`Content-catalogue/active-content-catalogue.json`, 102 entries), Claude's gap check (`SWG-gap-check-research.md`), the format inventory and the open-assets note. Each item was checked against the AGENTS.md ethics rules.

**Status: owner authorized 13 October 2026; blocked by sandbox network.** A1 metadata request failed with socket access denied. Nothing downloaded; record in `../Content-catalogue/archive-downloads.json`. Authorization persists; resume only with network available, following the checks below.

## Where things go

- **Code sources** go to `work/research/<owner>_<repo>/`. Use a pinned revision and a sparse checkout of only the folders listed. These are reference copies: nothing in them is built, run or installed.
- **Asset packs and tools** go to `outputs/Content-catalogue/<pack>.zip`, as the Borrie packs already are.
- **One record per item** goes in `outputs/Content-catalogue/archive-downloads.json`: URL, revision or version, date, bytes, SHA-256, licence name, the licence or readme text, credits, and the folders taken.

## A. Clear terms: download now

| # | Item | Licence | Take | Why we want it | Size |
|---|---|---|---|---|---|
| A1 | [Miphstoe/BellumGero-Live](https://github.com/Miphstoe/BellumGero-Live) | AGPL-3.0 | `MMOCoreORB/bin/scripts` (Hoth and Bellum screenplays) and `tools/` (newplanets, worldbuilder) | Phase 3 Hoth, steps 1–3: `tre_inventory`, `dep_closure` and `chain_check` against our MTG archives, plus Hoth mobiles, caves and missions to port | measure first; the sparse checkout should be well under 500 MB |
| A2 | [Thrax989/SWGFlurry](https://github.com/Thrax989/SWGFlurry) at `947a7e66` | AGPL-3.0 | `MMOCoreORB/bin/scripts` only | Echo Base and screenplays for Mandalore, Taanab, Kashyyyk and Mustafar; dungeons; POI waypoint helpers (Phase 2–3). The world boss work already credits it | measure first |
| A3 | [nostyleguy/io_scene_swg_msh](https://github.com/nostyleguy/io_scene_swg_msh) | MIT | latest release zip | the existing SWG Blender exporter for the first prop (Phase 5). Download only; installing Blender or the add-on needs the owner's OK | a few MB |
| A4 | [swgemu/Tools](https://github.com/swgemu/Tools) | check the repo's licence file | whole repo | Behavior Studio for bot and NPC behaviour trees; WorldSpawnerTool for new planets' spawn regions | measure first |
| A5 | [XanderOlson/swgemu_single_player](https://github.com/XanderOlson/swgemu_single_player) | AGPL-3.0 | `spec/`, the test and CTest files, the README | model for our own automated Lua and C++ checks (whole-server testing) | small |
| A6 | [[name removed]/swgmtv](https://github.com/[name removed]/swgmtv) | check the licence file | whole repo | mobile template viewer: browse NPC and creature templates when building scenarios | small |
| A7 | CC0 kits: [Quaternius Ultimate Modular Sci-Fi](https://quaternius.com/packs/ultimatemodularscifi.html), [Kenney Modular Space Kit](https://kenney.nl/assets/modular-space-kit), two or three [Poly Haven](https://polyhaven.com/license) metal or panel textures (1K) | CC0, confirmed on the creator pages | the free downloads only | base material for the first prop (an original terminal or crate). CC0 needs no clearance beyond keeping source and licence (AGENTS.md) | tens of MB |

If a repo has no licence file (A4, A6), keep it as a read-only reference, "read, don't copy", and say so in its record.

## B. Rated "published for server use" but not downloaded yet

These are all [Mod the Galaxy](https://modthegalaxy.com) resources, like the Borrie packs we already have. MTG's downloads may need a forum account. **If a login wall appears, stop and list the item for the owner to fetch by hand.** Agents never create accounts or sign in.

| # | Item | Why |
|---|---|---|
| B1 | [Borrie's Dark Interiors](https://modthegalaxy.com/index.php?resources/borries-dark-interiors.100/) | completes the Borrie set |
| B2 | Original planet releases: [Hoth](https://modthegalaxy.com/index.php?threads/new-planet-hoth.756/), [Taanab](https://modthegalaxy.com/index.php?threads/new-planet-taanab-mini-expansion.686/), [Mandalore](https://modthegalaxy.com/index.php?threads/mandalore-for-swgemu-based-emulators.433/), [Dromund Kaas](https://modthegalaxy.com/index.php?threads/dromund-kaas-for-swgemu-based-emulators.349/), [Kashyyyk](https://modthegalaxy.com/index.php?resources/kashyyyk-for-precu.2/), [Mustafar](https://modthegalaxy.com/index.php?resources/mustafar-for-precu.3/) | The terrain is already in our MTG TREs. The releases add each author's readme, terms and server files, which the catalogue says to use ("use the original release") |

## C. Read the terms first; download only if the page grants reuse explicitly

These were rated "release or permission unverified":
- [Named Saber Crystals](https://modthegalaxy.com/index.php?threads/named-saber-crystals.419/);
- [Classic BARC assets](https://modthegalaxy.com/index.php?threads/classic-barc-speeder-assets-patch.238/);
- [Post-14.1 house assets](https://modthegalaxy.com/index.php?threads/post-14-1-house-assets-patch.237/);
- [Borrie's /tool and Jawa toolbox](https://modthegalaxy.com/index.php?threads/borries-tool-command-featuring-the-jawa-toolbox-object-syncing-command.1395/);
- [SWG Galaxy Map Editor](https://modthegalaxy.com/index.php?resources/swg-galaxy-map-editor.173/);
- [Sytner's IFF Editor (SIE)](https://modthegalaxy.com/index.php?resources/sie.1/).

SIE and the map editor are Windows programs: archive them only, and never run them without the owner's OK. Record each item's terms verbatim either way.

## D. Owner-approved additions

| # | Item | Licence | Take | Why we want it | Size |
|---|---|---|---|---|---|
| D1 | [Sagiroth/TortoiseBots](https://github.com/Sagiroth/TortoiseBots) at `bc914eb3` | per file: AGPL-3.0 core with an attribution term; GPL/AGPL donor lineages (its `LICENCE.md`) | whole repo, shallow clone (**downloaded 13 Oct 23:12**, 42.6 MB) | the owner's main inspiration: a mature WoW playerbot framework. Design reference for our bot module (pool bots that live in the world, observability dashboard with a live map, stuck tracking, one test per behaviour policy). Reference only: we write our own code | 43 MB |

D1: the owner asked in Claude's chat, with a screenshot of the author's permission (Discord, 13 Oct 22:53). Not forked on GitHub. Credit in `Community-content/CREDITS-and-sources.txt`.

## Not downloadable

Each of these is ruled out by AGENTS.md, the owner's exclusions or the catalogue:
- Sentinel's Republic, and BorrieBoBaka's SWG_D20_RP_TC (owner exclusions);
- the SWG-Source repositories, and the 2026 "Legends" leak;
- Sunrunner II's original quests and art (creator permission needed);
- Bellum's private `bg_custom1.tre` (Hoth art ported from Infinity; not in the repo anyway);
- Flurry's TRE pack (client art of unverified origin) and EiF's custom ship models (unverified);
- KOTOR files: that research is closed until one creator-original asset is chosen.

## Rules for the download task

- Pin every revision. Use sparse or shallow checkouts. Don't execute, build or install anything downloaded.
- Total budget **3 GB**. If an item would push past it, skip it and list it.
- Measure size before downloading (for example the GitHub API repo size, or a `HEAD` request).
- No accounts, sign-ins, captchas, purchases or messages to authors.
- If the Codex sandbox has no network, say so and stop. Claude can then fetch the same list from WSL once the owner agrees.
