# SWG client formats, Hoth as the first Universal Modder job, and cut content to restore

13 Oct 2026, Claude, for task C1 (taken over so ChatGPT could run the bot squads). Version 1: built from the Core3 source in our dev worktree, which reads most of these formats, plus a few public tools. **Nothing was downloaded or installed for this note.** "Reader in Core3" paths are under `/opt/swg/Core3-dev/MMOCoreORB/src/` (AGPL, legitimate to read). Uncertain items are marked.

## 1. Format inventory

Almost every SWG file is an **IFF** container: big-endian `FORM` records holding typed chunks. Our engine reads them with `IffStream` (in `utils/engine3`). Assets ship inside **TRE** archives, and the client loads archives in priority order, so a new archive can override or add files.

| Format | Holds | Reader in Core3 | Public tools | What we need it for |
|---|---|---|---|---|
| `.tre` | archive of client files (index, compressed blocks) | `tre3/TreeArchive.h`, `tre3/TreeFile.h` | TRE Explorer and SIE, said to be available from Mod The Galaxy ([Reddit, 2024](https://reddit.birdcat.cafe/r/swgemu/comments/1er4xxo/weapon_mods); unverified) | packing our own `local_*.tre` for Hoth and every client change |
| `.iff` object templates (`shared_*.iff`) | client object definitions: appearance, name, slots | `templates/SharedObjectTemplate.h`, `templates/manager/TemplateManager.h` | SIE | new items and NPCs; finding cut objects |
| datatables (`datatables/*.iff`, DTII) | tables: planets, travel, skills, creation | `templates/datatables/DataTableIff.h` | SIE | Hoth registration (planet and travel tables) |
| `.stf` | string tables (names, dialogue) | `server/zone/managers/stringid/StringIdManager.h` | SIE | planet names, new text |
| `.trn` | procedural terrain: layers, boundaries, height and flora rules | `terrain/ProceduralTerrainAppearance.h` (+ `terrain/layer/…`) | not found | Hoth and other planets; the server reads it for heights |
| `.ws` | world snapshot: static buildings and props per planet | `templates/snapshot/WorldSnapshotNode.h`, `PlanetManagerImplementation.cpp` | a converter from WS to buildout tables on [Cekis's GitHub](https://github.com/Cekis) (unverified) | Hoth's Echo Base and props; mapping terminals |
| `.pob` | building interiors: cells, portals, path graph | `templates/appearance/PortalLayout.h`, `CellProperty.h`, `PathGraph.h` | not found | interiors (Echo Base, caves) and indoor paths |
| `.flr` | floor mesh for walking and collision | `templates/appearance/FloorMesh.h` | not found | indoor navigation (our bots use it through `/agentpath`) |
| `.msh` | static mesh (geometry + shader references) | `templates/appearance/MeshAppearanceTemplate.h`, `MeshData.h` | [io_scene_swg_msh](https://github.com/nostyleguy/io_scene_swg_msh) (Blender 2.9+ import and export) | first prop converter (Phase 5) |
| `.mgn` | skinned mesh for creatures and clothing | not read by the server | io_scene_swg_msh (import and export) | wearables, creatures |
| `.lod` / `.cmp` | level-of-detail and component appearances (meshes put together) | `DetailAppearanceTemplate.h`, `ComponentAppearanceTemplate.h` | not found | props with LODs; the add-on doesn't follow APT → LOD → MSH chains |
| `.apt` | appearance redirect to the real mesh | `templates/appearance/AppearanceTemplate.h`, `AppearanceRedirect.h` | io_scene_swg_msh writes a simple APT | the last step of a static prop |
| `.sht` | shader: textures and material settings | not read by the server | the Blender add-on loads images onto materials named after a shader | prop textures |
| `.dds` | textures | standard DirectDraw Surface | any DDS tool | textures |
| `.skt` / `.ans` / `.lmg` / `.sat` | skeleton, animation, LOD skinned mesh group, skeletal appearance | not read by the server | not confirmed for the Blender add-on | wearables and creatures (later) |
| `.cdf` | client data (effects and attachments; unverified) | not read by the server | not found | later |

**What the converter needs first** (as the roadmap says): static prop = `msh + sht + dds + apt`, proven by a round trip through the Blender add-on. Then wearables = `mgn + skt`. The Hoth work in section 2 needs only TRE, datatables and STF, which SIE handles. So it's a good first Universal Modder job: the formats are simple and we can test the result in the client.

**Still to do for C1** (ChatGPT or Claude):
- archive.org copies and licences for SIE, TRE Explorer and the Blender add-on;
- confirm what the add-on does with `skt`/`ans`;
- check the Cekis repositories' licences before using anything from them.

## 2. Is Hoth the right first job for Universal Modder? Yes, with one condition

**What we already have:**
- Hoth terrain and snapshot inside the MTG archives we installed: `terrain/hoth.trn`, `snapshot/hoth.ws` (`Content-catalogue/MTG-inventory-summary.json`).
- The catalogue rates this Hoth **P**: the original creator released it for server use, credit required (`SWG-content-catalogue.md`, Planets table).
- The roadmap also names Bellum Gero's current-Core3 Hoth scripts and Flurry's Echo Base. I didn't re-check their availability here, and a web search didn't find Bellum's `tre_inventory` / `dep_closure` tools, so that needs a check before step 1.

**Why it's a good first job:**
1. Most of the client work is data, not art: register the planet, travel table and strings, then pack a `local_planets.tre`. These are the simplest formats in the table (TRE, datatable, STF), and Universal Modder's reverse-engineering method can prove each by round trip.
2. The server side is ordinary Core3 work for Claude (zone, travel points, spawns), done on the test galaxy first.
3. It's testable end to end with what we built today:
   - Cresh's shuttle test already buys tickets and rides, so "ride to Hoth" is the same scenario with a new destination.
   - Esk can map Echo Base the same way it maps Mos Eisley.
   - Real-client checks go through `um win` (C2).

**The condition:** a client-side change means everyone who joins needs the new archive, including your own clients. It's still private, so nothing is published. Before any of this goes live, confirm how players will get `local_planets.tre`.

**Order after Hoth:**
- **Taanab**, also catalogue P: its terrain is a restoration of unfinished SOE terrain, so it's cut content too.
- **Kashyyyk and Mustafar:** SOE expansion assets, in MTG and on your disc.

## 3. Cut content to restore: what qualifies, and the first candidates

**Rule (Ethics check):** restore content whose assets are in your own client or in packages released for server use. Write the server logic ourselves. Leaked source and anything derived from it is out.

`Content-catalogue/Cut-content-and-backports/SOE-cut-content-selected-reference.zip` and its `backport-evidence.json` record files taken from **SWG-Source/dsrc**, which this project excludes. Don't use them. I recommend moving that folder out of `outputs/`, but that's your OK, and I haven't touched it.

**Candidates:**

| Candidate | Evidence we can use | Work |
|---|---|---|
| Taanab (unfinished SOE terrain, restored by Takhomasak) | MTG terrain + snapshot; catalogue P | a planet, same path as Hoth |
| Morag and Morag's castle (Endor) | `object/mobile/shared_morag.iff` and `appearance/morag.sat` are in **your client** (`data_other_00.tre`; recorded in `backport-evidence.json` asset coverage) | write our own NPC, conversation and small quest chain; don't use the dsrc quest data |
| Otoh Gunga (legacy underwater terrain) | catalogue D: legacy terrain, not a finished destination | research only |
| Kashyyyk / Mustafar | SOE expansion assets in MTG and on the disc | planets after Hoth |
| Dormant client objects | **done 13 Oct:** `tools/research/dormant_objects.py` → `Content-catalogue/dormant-client-objects.md`/`.json`. Of 29,342 object definitions in the client archives, 13,627 have no server template, but only **131 are SOE-client objects**; the rest are MTG package content. | see below |

**The 131 SOE-client dormant objects** (assets you own, no server template; verify each before planning, because some may be served under another path):
- **Player-city building styles:** bank, capitol, cloning facility, hospital and theater in `*_corellia/naboo/tatooine_style_01` variants (15). The server only offers the default styles. *Good first restoration:* add the templates and a style choice on the deeds.
- **Bio-engineer food additives:** duration, flavour, mental, physical and reflex components and their schematics (10 + 10).
- **JTL ship parts:** mass reduction kits and upgraded retro thrusters Mk1–5 (items + schematics), and TIE fighter / Z-95 basic reactors.
- **Resource containers by type** (38; e.g. `resource_container_energy_gas`) and **dye components** (clothing, hair).
- **Single items:** a faction-perk covert detector, a Bestine painting schematic, `test_falcon` (a test building).

**Most SOE cut content isn't a missing object at all:** Core3 has templates for almost everything. What's missing is placement and logic: NPCs nobody spawns (Morag has a template), quests, and terrain such as Taanab. So restoring cut content mostly means writing spawns, conversations and quests, which is ordinary server work for us.

**Sources** (searched 13 Oct): [nostyleguy/io_scene_swg_msh](https://github.com/nostyleguy/io_scene_swg_msh); [Cekis on GitHub](https://github.com/Cekis); [Reddit r/swgemu, weapon mods, Aug 2024](https://reddit.birdcat.cafe/r/swgemu/comments/1er4xxo/weapon_mods); [IFF background (Shikadi modding wiki)](https://moddingwiki.shikadi.net/wiki/Interchange_File_Format_(IFF)).
