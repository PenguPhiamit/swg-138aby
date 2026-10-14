# Universal Modder: capability reference for Claude and the owner

Prepared 13 October 2026 by ChatGPT. Scope: **all 12 installed skills and all 10 CLI groups in version 0.2.0**, including every parser command/option in the companion [CLI reference](universal-modder-CLI-reference.md). This documents capabilities; it does not claim every workflow has been executed here.

Installed package: `C:/Users/Pengw/.codex/plugins/cache/universal-modder/universal-modder/0.2.0`. Source hashes: [source inventory](universal-modder-source-inventory.md). Public upstream: [Universal Modder](https://github.com/rehan-remade/universal-modder). Installed files take precedence over a newer upstream README.

## What provides the power

UM combines procedural skills, a Python CLI, examples and a shared knowledge base. An agent still writes game-specific code and connects external tools. Its installed `.mcp.json` declares **fal only**, not Ghidra, IDA, Frida, Cheat Engine or RenderDoc. The session-start hook adds the Bash launcher to PATH. There is no universal one-command decompiler or automatic SWG converter in the CLI.

Our parser export found **76 parser entries**, counting the root, groups and leaf commands; this is not 76 independent engines. Exporting help executes no command actions. `pyproject.toml` requires Python >=3.10, Pillow, NumPy and PyYAML. Native Python can import the CLI here, but `kb search` failed because PyYAML is absent in that interpreter. Directly searching the bundled knowledge directory found no SWG-specific field note; other Star Wars games are present. No dependency installation or remote KB synchronization was performed.

## All installed skills

| Skill | Work it guides | Deliverable / SWG use | Dependencies and limits |
|---|---|---|---|
| mod-any-game | Intake, recon, safe lab, one working slice, assets, real-game verification, packaging | A complete mod project with journal and verification; use server scripts/data first for SWG | A workflow, not an autonomous compiler for every engine |
| game-recon | Identify install, executable architecture, engine signals, loaders, saves and community route | `MODDING_PLAN.md`; useful before touching the native SWG client | Detection is heuristic; standalone installs need an explicit folder |
| game-research-websearch | Recover old forum knowledge, archive lookup, GitHub/platform research, login handoff | Source journal with dates, credibility and gaps; profession/format research | Requires search/browser/network; dead archives and login gates remain real limits |
| reverse-engineering | Static code, live behavior, graphics and binary-format analysis | Named functions/structures, a parser/writer, round-trip evidence | External RE tools required; see tool matrix below |
| fal-assets | Art, sprites, textures, material maps, 3D, rigging, audio and video | Generated files and generation manifests | Paid fal account/key, per-batch owner approval, rights review of outputs |
| asset-pipeline | Cutout, trim, fit, palettes, sheets, masks, tiling and 3D-to-sprite rendering | Engine-sized images/frames | Pillow/NumPy; Blender for rendering; still needs SWG-specific encoding |
| game-automation | Launch, capture, input, process cleanup, test scenes and in-game JSON bridges | Reproducible real-client checks | Windows tools/FFmpeg; exact window selection; owner present for our UI rules |
| showcase-video | Record game-only audio, choose moments, edit titles/music/credits | Showcase video plus EDL | FFmpeg; audio/render dependencies; not required to validate a server script |
| mashup-mods | Asset/mechanic ports, two-game passthrough, embedded simulations and reimplementations | A cross-game architecture with replay/oracle checks | Substantial custom engineering; source and asset rights checked separately |
| port-a-mod | Pin original version, adaptation matrix, extract values, port units without drift | Resumable port with parity tests | Reference release and rights; useful for old Core3 screenplay/AI APIs |
| publish-mod | Package, README, license/credits, platform instructions and release post | A distributable release | CLI provides lint, not generic platform upload; outbound publishing needs approval |
| share-field-notes | Search, document verified lessons, validate and propose KB contribution | Local field note, optional public PR | PyYAML/Git/gh/network as needed; public PR requires owner OK; private server git never pushed |

Engine playbooks include Unity, Unreal, .NET/XNA/FNA, Godot, Source, Bethesda, Minecraft, Genie/AoE2, Bannerlord, native code, retro decomp/recomp and miscellaneous engines. The installed reference directory also includes ZenGin and larger framework notes. A playbook is guidance, not a compatibility certification for a particular game version. There is no installed SWG playbook.

## All CLI groups

| Group | Commands / capabilities | Inputs → outputs | Practical limit |
|---|---|---|---|
| scan | Install discovery, engine/version/PE fingerprints, anti-cheat/loader/save hints, ranked routes | Store libraries or folder → text/JSON report | Bounded heuristic scan can misidentify launchers or miss protection elsewhere |
| fal | `image`, `sprite`, `edit`, `rmbg`, `pixelate`, `upscale`, `texture`, `pbr`, `model3d`, `rig`, `sfx`, `music`, `voice`, `video`; `run`, `search`, `schema`, `price`, `result`, `upload` | Prompts/reference files/endpoint JSON → downloaded outputs and `fal_manifest.jsonl` | Local file inputs can be uploaded; generation costs money; endpoints and prices change |
| comfy | `status`, `image`, `run` | Local server/checkpoint or API workflow JSON → files and `comfy_manifest.jsonl` | ComfyUI and models installed separately; stock image graph fits SD1.5/SDXL, other models need an API workflow |
| sprite | `info`, `cutout`, `fit`, `pixelate`, `palette`, `sheet`, `slice`, `frames`, `team-mask`, `seamless`, `tile-preview`, `preview`, `outline`, `hard-alpha`, `flip`, `rotate` | Raster art → processed rasters, masks, sprite sheets | Flood-fill cutout is not semantic segmentation; simple frames are transforms, not a learned character animator |
| render3d | GLB rendering; presets `aoe2`, `iso8`, `trueiso`, `topdown`, `side`, `turntable`; heading/animation controls | GLB + Blender → transparent sprite frames | Does not write SWG MSH/MGN/SKT/ANS; rendering a model into sprites is separate from importing it into SWG |
| video | `probe`, `contact`, `first-frame`, `beats`, `mux`, `compile` | Media/EDL/audio → measurements, contact sheets and edited video | FFmpeg and optional analysis dependencies; automatic first-frame/beat estimates need inspection |
| win | `setup`, `ps`, `kill`, `launch`, `shot`, `record`, `drive`, `reg` | Window/process/drive script → capture/input/process or registry operation | Screenshot/record by HWND supported; duplicate SWG executable input targeting is unresolved here |
| backup | `create`, `list`, `diff`, `restore` | Save/config directory → snapshots/diffs/restored files | File backup, not our transactional galaxy/database backup; restore/clean can overwrite/delete |
| publish | `check` | Mod folder, optional game folder → lint diagnostics | Heuristics detect copied files and obvious secrets/decompiler markers; no rights guarantee; no upload command |
| kb | `search`, `show`, `new`, `check`, `index`, `sync`, `pr` | Local/cached notes → search/scaffold/validation/index; optional GitHub changes | Sync uses network/cache writes; PR can branch, commit, push and post; not authorized by research alone |

The companion CLI reference contains **every currently registered option**, including timeout, endpoint overrides, seeds, node-input overrides, window selection, crop/scale, output paths, encoding and restoration options. Prefer it to copying incomplete examples from marketing summaries.

## Reverse-engineering tool matrix

| Target | UM-documented external tools | What they can establish | Fit for SWG |
|---|---|---|---|
| Managed .NET/Mono | ILSpy/ilspycmd, dnSpyEx and optional MCP bridges | C# types/methods; debugging | Not the main native SWG client route |
| Unity IL2CPP | Cpp2IL, Il2CppDumper, then Ghidra/IDA; UnityExplorer/Frida | Metadata, addresses and native methods | Not applicable to the main SWG engine |
| Java | Vineflower, CFR, Recaf; mapped source workflows | Classes and behavior | Useful for Java community tools, not the SWG client executable |
| Native C/C++ | Ghidra, IDA, Binary Ninja, radare2 plus separately configured bridges | Strings, cross-references, decompilation, function/type renaming | Candidate for understanding client follow/input or asset loading; exact binary/architecture must be pinned |
| Live native behavior | Frida, x64dbg, Cheat Engine, ReClass.NET and optional bridges | Observe calls/values, breakpoints, traces, structure layouts | Separate installation and carefully scoped experiment required; never attach during another agent's test |
| Graphics | RenderDoc and optional bridge | Draw calls, render targets, buffers, frame inspection | RenderDoc's own matrix excludes D3D9/10. Do not assume it captures a legacy SWG D3D9 renderer |
| Known asset formats | UABEA/AssetRipper, FModel/UAssetGUI, xEdit/BSArch, UndertaleModTool, genieutils, VRF/Crowbar, WitchyBND/Smithbox, GDRE Tools | Read engine-specific data with existing tools | None is a general SWG converter; use verified SWG tools/readers first |
| Unknown binary format | Compare owned samples, headers/counts/offsets, write reader then writer | Repeatable decoded structure and round-trip equality | Best fit for missing SWG asset export paths |

GhidraMCP's maintainer documents a separately installed Ghidra extension and Python MCP client: [upstream](https://github.com/LaurieWired/GhidraMCP). Frida documents interception/tracing APIs and Windows support: [official API](https://frida.re/docs/javascript-api/). RenderDoc documents its graphics API support explicitly: [upstream support matrix](https://github.com/baldurk/renderdoc#api-support). These were read; none was installed or connected in this session. Other tool names above describe the installed UM skill's options, not newly validated versions or recommendations to install them all.

## SWG applications and what still has to be built

1. **Research and source archaeology:** recover pre-CU mechanics and documented IFF layouts, with era/version checks. Already useful now.
2. **Static prop pipeline:** inspect owned MSH/SHT/APT/DDS chains; compare existing community exporters; verify a round trip; then one original cargo crate. Custom SWG writer/integration may be needed. Do not assume nobody has ever written an exporter: C1 already lists community tooling.
3. **Wearables/species:** mesh skinning, skeleton/bone mapping, attachment points, animations, species customization and clothing fit. A generated GLB or auto-rig is not a compatible SWG wearable.
4. **Planets:** dependency closure, TRE precedence/packing, CRC/datatables/STF, terrain/snapshot/travel and modern Core3 scripts. UM provides the investigation/port method; Bellum/SWG tools provide format-specific operations.
5. **Client follow investigation:** native function analysis plus observed movement traces could distinguish steering/input faults. A proper client pathfinder is a much larger feature than the current server leash workaround.
6. **Tests and demos:** exact-HWND screenshots work here; squad harness drives headless bots separately. UM is not the C7 controller and does not replace the SWG agent protocol.

## Observed local readiness

- Installed skills and parser inventory: verified by reading source and generating help.
- Windows screenshot setup: previously installed/verified; two specific game HWND captures worked. That earlier session's handles are stale.
- Multiple identical client inputs: **not verified**. WinDrive's process-name selection could hit the wrong window; no automated input until exact targeting is resolved.
- Local ComfyUI, Blender/SWG exporter and external RE tool connectivity: **not verified by this session**.
- fal: no key configured per current handoff; no paid calls made.
- KB command: missing PyYAML in the native interpreter; fallback local text search used. A Bash/uv runtime may differ and was not executed just to install dependencies.
- Publish lint: source inspected, not run on private credentials or game assets.

## Constraints and reproducibility

Project AGENTS.md governs: Claude owns `/opt/swg`, no live deploy without cross-review and owner OK, no excluded material, no public post/PR without approval, no paid batch without approval. LAN use does not resolve unclear art permissions. UM source is MIT; external tools, models and imported content have their own terms.

Store a sample manifest with input hashes/version, tool/workflow/model, parameters/seed, output hashes, license/source and the actual game check. Keep private executable/decompiled data out of public outputs. A format claim needs reader → writer → reader comparison and a real-client test; a guessed function needs a trace that supports it. Lint success is not proof of permissions or of correct gameplay.

## Research log

Queries: `universal modder rehan remade github reverse engineering`, `site:github.com/LaurieWired/GhidraMCP README`, `site:hex-rays.com IDA MCP official`, `site:renderdoc.org docs Direct3D 9 support`, `site:frida.re/docs Windows JavaScript API`. UM upstream and external maintainer documentation checked; RenderDoc website was robots-blocked, its official GitHub support matrix readable. No reliable current official IDA-MCP version result established, so no version-specific IDA install recommendation is made.

Sources inspected locally: README, CLI registration, module command definitions, `pyproject.toml`, MCP/hooks, research/recon/RE/port/mashup workflows, KB source and index. Full help regenerated by `outputs/tools/document_um_capabilities.py`. No screenshots taken for documentation research, no third-party service connected and no public contribution made.
