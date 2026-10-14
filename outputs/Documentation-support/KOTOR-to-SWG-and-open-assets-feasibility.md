# KOTOR I/II, mods and open assets → SWG

Research for the owner and Claude, 13 October 2026. Owner owns both KOTOR games. Scope: technical feasibility, rights evidence, original inspiration and open asset alternatives. **No game extraction, package download, tool installation or SWG import was performed.** No conversion or in-game appearance is verified yet.

## Conclusion

**UM can help substantially.** Existing KOTOR readers and Blender importers plus an existing SWG exporter provide a credible conversion path. UM supplies research, batch scripting, asset preparation and verification workflows; it does not itself implement an Odyssey-to-SWG converter.

The most practical first result is **one original or CC0 static prop** with a KOTOR-inspired function/style, adapted to SWG's look. Direct stock-asset reuse remains rights-unresolved; individual mod contributions need their own terms. Owning the games is relevant to legitimate local access but does not establish blanket cross-game reuse permission.

## Four routes

| Route | What we would do | Feasibility / rights status | Main difficulty |
|---|---|---|---|
| Stock KOTOR assets | Inspect owned installation, convert a selected mesh/material | Technically credible, cross-game permission not established | SWG export/material/collision setup; rigging for characters |
| KOTOR mod assets | Identify genuinely new author-created contribution and request/verify reuse terms | Depends on each asset and upstream sources; “modder resource” is not automatically unrestricted | Permission chain plus conversion |
| Original KOTOR-inspired work | Study broad visual/function references; create our own geometry, textures, writing and encounters | Recommended creation route; no claim that a close remake loses underlying franchise rights | Original design and SWG integration |
| Open-licensed assets | Adapt CC0/other suitably licensed source art, keep provenance | Clearest asset-level reuse path where the specific pack has clear terms | Art-direction consistency, optimization and integration |

Private LAN, a local converter and ownership checks do not automatically resolve license conditions. A bring-your-own-files installer reduces redistribution of source assets but is **not** a universal permission substitute. This research has not verified the owner's edition-specific EULAs: the two Steam EULA URLs tested were inaccessible. Before a stock-asset conversion/import, read the installed license and resolve the cross-game scope under our project's rights rule. Research and original design can proceed independently.

## Existing tools: we do not need to begin by reversing everything

| Tool / primary source | Verified advertised role | License / compatibility caveat |
|---|---|---|
| [KotorBlender, seedhartha](https://github.com/seedhartha/kotorblender) | MDL models/animations/walkmeshes, LYT layouts, PTH paths, lightmap baking and minimaps | GPL-3.0-or-later; maintainer states Blender 3.6/4.2 compatibility and 4.4 testing. Not a guarantee of every newer Blender |
| [PyKotor, OpenKotOR](https://github.com/OpenKotOR/PyKotor) | Read/modify KOTOR I/II formats; Holocron Toolset and Python scripting | LGPL-3.0-or-later; old OldRepublicDevs URL redirects here. Check chosen release/subproject licenses before bundling |
| [PyKotor format documentation](https://github.com/OpenKotOR/PyKotor/wiki/Resource-Formats-and-Resolution) | Archive/resource resolution and format reference | Use for the source-side parser; game data retains separate terms |
| [xoreos-tools](https://github.com/xoreos/xoreos-tools) | Aurora-family resource utilities, including archive/texture workflows | External alternative, not installed or benchmarked here; inspect selected tool/license/release before use |
| [NoStyleGuy SWG Blender add-on](https://github.com/nostyleguy/io_scene_swg_msh) | Import/export MSH, MGN, LOD, POB and SKT; appearance-chain helpers | MIT. README targets Blender 2.9+/3+ and documents skeletal limitations; latest Blender compatibility not established |

**Important correction to the older converter plan:** a SWG exporter already exists. Investigate it before writing a new one. Its documentation supports static-mesh/material/UV/hardpoint work and room-based interiors. It warns that SKT rotation recreation is inaccurate and animations are not supported in that workflow. Existing tools make props more plausible; they do not make KOTOR skeletons/animations automatically compatible with SWG.

A sensible compatibility experiment uses a separate Blender 3.6 environment because the documented version ranges overlap there. That is an inference for a test, not a tested combination or installation authorization. Another option is separate importer/exporter environments with an intermediate mesh format, validating what survives that transfer.

## Format and integration map

| KOTOR concept/data | SWG destination or replacement | Work needed |
|---|---|---|
| KEY/BIF, RIM/ERF/MOD archives | Local staging; ultimately our own client asset package | Resolve exact source and overrides, index dependencies, retain hashes |
| Static MDL/MDX geometry | MSH + APT, optionally LOD | Units/axes/pivot, triangulation/normals/UVs, bounds, material paths |
| TPC/TGA textures and TXI material instructions | DDS textures and compatible SHT/material setup | Alpha/mipmaps, normal/specular/environment behavior, baked vs runtime lighting |
| LYT room arrangement + area walkmesh/path data | POB cells/portals/floors and SWG navigation setup | Rebuild room links, visibility, collision and traversal; path files are not interchangeable |
| Skinned models/animations | MGN on compatible SWG SKT/animation system | Rebind weights/bones, poses/attachments/occlusion and body shapes; often reuse an existing SWG rig |
| DLG/GFF/2DA, scripts, quests | Original Core3 templates/screenplays/conversations | Reimplement objectives/state/rewards; KOTOR scripts do not execute in Core3 |
| Music/voice/lip animation | Newly created/licensed audio and SWG event setup | Separate rights, encoding and playback integration; not a first prototype |

This map is an engineering inference from the documented formats/tool capabilities. No file renaming alone makes an asset work. In particular, KOTOR baked lighting can look wrong under SWG lighting, and a visible room is not necessarily walkable, navigable or correctly portalized.

## What ownership and mod permission do—and do not—tell us

[Deadly Stream's published porting announcement](https://deadlystream.com/topic/6362-a-new-chapter-for-the-kotor-community/) allows specified within-series ports for hosting and retains author-permission requirements. It does **not establish permission to port those assets into SWG**, and a hosting site's policy is not a grant of the game's underlying rights.

Its [modder-resource catalogue](https://deadlystream.com/files/category/18-modders-resources/) contains both new work and modified stock assets. For example, the fat-commoner resource explicitly modifies game body models: its author credit/reuse statement does not turn the underlying game mesh into original open art. Upscaling stock textures similarly does not remove their provenance.

[Sithspecter's High Quality Blasters resource listing](https://deadlystream.com/files/category/18-modders-resources/page/2/?sortby=file_submitted&sortdirection=desc) describes credit, notification and restrictions on rehosting unmodified sources. This is a **candidate for a specific author inquiry**, not a finding that SWG reuse is already authorized. No message was sent; no permission is inferred from silence.

For each proposed mod asset, record: release/version and author; whether new or derived stock content; all contributing authors; source files and license/readme; explicit cross-game/redistribution scope; modification conditions; credits; response if permission is requested. A payment arrangement is possible only if the relevant rights holder actually offers one; paying a mod author does not authorize rights they do not own.

The [U.S. Copyright Office's derivative-work explanation](https://www.copyright.gov/eco/help-limitation.html) distinguishes new contributions from pre-existing material and identifies adaptation as an owner's exclusive right, subject to applicable exceptions. This research has not determined that a particular private conversion qualifies for an exception. Under the project's AGENTS.md, unclear source rights are resolved before importing.

## Inspiration: useful without copying a package

We can work from broad design briefs such as “ancient archaeological ruin,” “frontier cantina,” “industrial mining station,” “weathered droid workshop,” or “branching companion conversation.” Create new room layouts, meshes, textures, inscriptions, dialogue, names and quest logic. Do not treat an exact traced model, copied scene, reproduced dialogue or AI transformation of a stock texture as automatically independent work.

Useful SWG-sized projects:

- **Original archive terminal:** a new model and local HoloNet/Writer-style content; directly supports F74.
- **Ancient expedition camp:** original ruins, artifact props and a short dynamic quest; supports F40/F77.
- **Modular mining room:** open geometry plus original materials/interactions; useful for exploring the Miner idea F67 without building a whole profession.
- **Droid maintenance station:** static station first; later repair/crafting interactions using native SWG systems.
- **Companion story:** original dialogue and quests around our mercenary framework, retaining pre-CU gameplay rather than importing KOTOR combat rules.

These are ideas, not claims about cancelled official content. They also avoid forcing Old Republic characters/events into SWG's timeline unchanged.

## Open asset shortlist, verified at creator sources

| Source | Useful material | Terms verified | SWG suitability |
|---|---|---|---|
| [Quaternius Ultimate Modular Sci-Fi Pack](https://quaternius.com/packs/ultimatemodularscifi.html) | 46 modular interior/prop models, FBX/OBJ/Blend | Creator page says CC0, personal/commercial use | Good room/prop blockout; materials/detail need SWG art pass |
| [Quaternius Sci-Fi Essentials](https://quaternius.com/packs/scifiessentialskit.html) | Robot/weapon/screen/crate family | CC0; free and paid tiers differ in included files | Use specific free files first, animated models need separate SWG rig work |
| [Kenney Modular Space Kit](https://kenney.nl/assets/modular-space-kit) | 40 modular objects, variants/animations | CC0 on creator page | Strong prototype geometry; stylized appearance may need reworking |
| [Kenney Space Kit](https://kenney.nl/assets/space-kit) | Space-themed 3D kit | CC0 on creator page | Props/blockout; not a finished SWG-compatible ship/space system |
| [Poly Haven](https://polyhaven.com/license) | Original PBR textures, models and HDRIs | Assets CC0; website/service terms separate | Excellent material reference/source; reduce texture sizes and bake to legacy SWG shaders |
| [OpenGameArt](https://opengameart.org/content/sci-fi-essentials-kit) | Creator-hosted copies and broader library | This Quaternius pack is CC0; site is NOT uniformly CC0 | Verify each package and contributor list; avoid confusing 2D tiles with usable 3D meshes |

“Open assets” is a better term than “open-source assets”: CC0/CC-BY/CC-BY-SA govern art while MIT/GPL/LGPL govern tools/code. Tool licenses do not relicense imported game art. CC0 does not grant unrelated Star Wars trademark/character rights; a purported CC0 game rip is not made trustworthy by a label.

Keep each downloaded pack's actual license and source/hash when implementation begins. A purchased source/engine tier is not required merely because free assets can be used commercially. No packs purchased or downloaded here.

## UM's concrete role

1. Archive-aware research and prior-art search. Bundled KB search found no KOTOR/Odyssey note by text search this pass; native `um kb` still has the previously recorded missing-PyYAML dependency.
2. Inventory source formats/dependencies and create a reproducible batch script around the existing import/export tools.
3. Prepare original/licensed textures, resize/preview/inspect alpha, adapt source materials and optimize meshes in Blender. UM `render3d` is optional previews/sprites, not the SWG 3D exporter.
4. Build a narrow original prop; validate export with round-trip checks, inspect in the real SWG client and record issues.
5. For larger imports, track room/cell/portal and rig mappings; use source/readers before native executable debugging. Ghidra/Frida are not required just to try the existing asset tools.

No need to run both games together or build a renderer bridge for this asset-only approach. A two-game passthrough is much more complex and does not provide ordinary persistent SWG content to other LAN clients.

## Difficulty and recommended first slice

| Slice | Preliminary difficulty | What proves completion |
|---|---|---|
| Original/CC0 crate or terminal | Medium | Export, valid material/appearance, sensible scale/bounds, client visibility and persistence |
| Permission-cleared static KOTOR/mod prop | Medium–High plus rights gate | Source audit plus same checks; no unsupported renderer feature |
| Wearable or handheld weapon | High | SWG attachment/rig, several body shapes, correct combat/visual behavior |
| Droid/creature/NPC | High–Very high | Animation/rig/state integration, collision and normal movement/combat |
| Single walkable room | High | Portals/floor/collision/LOS/AI paths, enter/exit and relog |
| Whole area/dungeon | Very high | All room/door/lighting/object dependencies plus original Core3 gameplay |

**Recommended:** a small original terminal using a CC0 mesh/material base, with an independently designed KOTOR-inspired aesthetic. Prove the existing SWG exporter on that first. This gives us a reusable pipeline and supports an actual proposed sandbox feature without waiting on stock-art terms. Direct KOTOR conversion remains an optional second investigation after a selected source's rights are resolved.

## Research audit

Sources: maintained importer/readers, SWG exporter README/license, Deadly Stream administrator/author terms, creator asset pages and Copyright Office explanation. Queries included KotorBlender/PyKotor formats/licenses, KOTOR porting rules/modder resources, SWG mesh exporter, CC0 sci-fi kits and game-specific EULA pages. Old importer ndixUR is documented as incompatible with modern Blender; prefer investigating seedhartha's maintained fork. Exact tool releases will be pinned if installed.

Access gaps: Steam EULA pages unavailable; no installed licenses read, no KOTOR installation scanned. Those gaps do not block original/open-asset planning, but prevent claiming stock-art reuse is cleared. This document is feasibility research, **not a validated converter or legal clearance**.

Author-level follow-up: [KOTOR mod reuse audit](KOTOR-mod-reuse-audit.md), 13 October 2026. This supersedes any preliminary uncertainty about Silveredge9's own grant: his direct 2016 statement is verified; other contributors remain separate.
