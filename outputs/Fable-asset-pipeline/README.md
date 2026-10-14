# Fable asset pipeline: one CC0 static prop into the SWG client (F86 prep)

14 Oct 2026, Fable. A read-only study of the Blender add-on `work/research/nostyleguy_io_scene_swg_msh` (io_scene_swg 3.1.4, MIT; README and source read as text, nothing installed or run) plus the stock files the result must match (dumped with our IFF tool from the owner's client). **This is a plan for a validation task: no step below has been executed, and the add-on's exporter has not been proven on this client.** Example prop: one wall segment from Quaternius' Ultimate Modular Ruins Pack (CC0 on the pack page; see `Fable-planet-test/ossus-assets/`). Names used below: object `fable_ruin_01`, shader `fable_ruin_stone_as8`, texture `fable_ruin_stone`.

## 1. What the client needs, and how the files reference each other

```
object/static/structure/general/shared_fable_ruin_01.iff      STAT template; its XXXX "appearanceFilename" names
  -> appearance/fable_ruin_01.apt                                FORM APT > 0000 > NAME "appearance/lod/fable_ruin_01.lod"
     -> appearance/lod/fable_ruin_01.lod   (optional LOD chain)   DTLA > 0007: APPR extents, INFO distance bands, DATA CHLD "mesh/fable_ruin_01_l0.msh" ... l3
        -> appearance/mesh/fable_ruin_01_l0.msh                  MESH > 0005: APPR/0003 (EXBX box + sphere, NULL collision, HPTS, FLOR), SPS: one entry per material,
                                                                   each NAME "shader/fable_ruin_stone_as8.sht" + INFO + vertex/index buffers
           -> shader/fable_ruin_stone_as8.sht                     SSHT > 0000: MATS, TXMS > TXM > 0001 (DATA tag 'MAIN', NAME "texture/fable_ruin_stone.dds"), TCSS,
                                                                   NAME "effect/a_simple.eft"  (the opaque single-texture effect; 2,952 stock shaders end in _as8)
              -> texture/fable_ruin_stone.dds                     DXT1 with a full mip chain (stock 256x256 textures carry 9 mips); DXT5 only for alpha
misc/object_template_crc_string_table.iff                        add the template path with its SOE CRC; the client names every object the server sends by this table
```
Without the LOD route the `.apt` names `appearance/mesh/fable_ruin_01.msh` directly (the add-on's "Create a SWG .apt for this .msh" writes exactly that: `mesh/<object name>.msh`). Stock example of the whole chain: `appearance/decd_blba_tree.apt` -> `lod/decd_blba_tree.lod` -> four `mesh/decd_blba_tree_l*.msh` -> three `.sht` -> `.dds`.

Server side (Core3-dev, `bin/scripts/object/static/structure/general/`): `objects.lua` gets `object_static_structure_general_shared_fable_ruin_01 = SharedStaticObjectTemplate:new { clientTemplateFileName = "object/static/structure/general/shared_fable_ruin_01.iff" }` + `addClientTemplate(...)`; a new `fable_ruin_01.lua` with `object_static_structure_general_fable_ruin_01 = object_static_structure_general_shared_fable_ruin_01:new {}` + `ObjectTemplates:addTemplate(..., "object/static/structure/general/fable_ruin_01.iff")`, included from `general/objects.lua`. Core3 reads the real values (appearance, collision flags, game object type) from the client `.iff` itself (`SharedObjectTemplate::parseVariableData`), so the `.iff` must sit in an archive in the server's `TreFiles` as well as in the client. Placement: a screenplay `spawnSceneObject("hoth", "object/static/structure/general/fable_ruin_01.iff", x, z, y, 0, qw, qx, qy, qz)` on the test galaxy, or a snapshot entry later.

## 2. The steps

1. **Source.** Download the pack (owner's OK), record zip hash, licence text and credit line, pick one piece (wall segment, under 2,000 triangles) with its atlas PNG. Note: Quaternius' pack page links CC0, its site licence page now shows QAL v1.0 (no attribution, finished games allowed, no repackaging); record both.
2. **Blender.** Use **3.6 LTS**. The README says "2.9+ and 3+" and `bl_info` requires 2.81.6; the exporter calls `mesh.calc_normals_split()` and the MGN path uses Face Maps, both removed in Blender 4.0/4.1, so 4.x is expected to fail. Install the add-on from the local checkout (`io_scene_swg-3.1.4.zip`, Edit > Preferences > Add-ons > Install). The preference "SWG Client Extract Dir" (a folder holding `appearance/`, `shader/`, `texture/` from a client extract) is only needed for "Find and load materials"; export works without it.
3. **Mesh prep.** Import the FBX/OBJ; apply scale and rotation (Blender units are metres; the add-on converts axes with `support.convert_vector3`; a negative scale makes it flip normals); triangulation is automatic (`bmesh.ops.triangulate`); split normals are exported as given. One Blender material per SWG shader, **named exactly like the shader file without directory or extension** (`fable_ruin_stone_as8` -> the exporter writes `shader/fable_ruin_stone_as8.sht` into each SPS). On that material add custom properties `UVSets` = 1 and `DOT3` = 0 (no normal map with `a_simple`); no `Color0`/`Color1`. Name the object `fable_ruin_01` (single mesh) or `fable_ruin_01_l0`..`_l3` inside a collection named `fable_ruin_01` (LOD route). No hardpoints are needed (they would be Arrows empties parented to the mesh).
4. **Export.** Select the mesh, File > Export > SWG Static Mesh (.msh), option "flip UV vertical" left on (SWG's DDS V axis is flipped). The exporter writes `<object name>.msh` into the chosen folder and ignores the typed file name; it computes box and sphere extents itself and writes `NULL` collision for a new mesh (it only preserves `CollisionExtents` it imported). Then SWG menu > "Create a SWG .apt for this .msh" -> `fable_ruin_01.apt` naming `mesh/fable_ruin_01.msh`. LOD route: File > Export > SWG LOD (.lod) on the collection with `export_children` on; it writes `mesh/<name>_l<N>.msh` for every child, the `.lod` with INFO distance bands, and the `.apt` automatically.
5. **Shader.** Clone the stock `shader/eqp_camping_ground_fresh_as8.sht` (SSHT/0000, one `MAIN` texture, `effect/a_simple.eft`) with `Fable-planet-test/tools/trn_iff.py` (parse, replace the `NAME` chunk text with `texture/fable_ruin_stone.dds`, build: sizes recompute) and save it as `shader/fable_ruin_stone_as8.sht`. For leaves or cut-outs clone an `_aa7` shader (`effect/a_alpha.eft`) and use DXT5. A normal map needs an `_asb13` clone (`a_simple_bump`, second TXM tag `NRML`) and `DOT3` = 1.
6. **Texture.** Atlas PNG -> square power of two, 256 or 512 px (stock props are 256) -> DDS DXT1 (BC1) with the full mip chain; DXT5 (BC3) only with alpha. Options: **(a)** NVIDIA Texture Tools Exporter with the add-on's preset `swg_dds_nvidia_tex_tools_preset.dpf` (`--format bc3 --quality normal --mips --mip-filter box`; use bc1 for opaque); free but needs an NVIDIA account. **(b)** Microsoft `texconv` (MIT, no account): `texconv -f BC1_UNORM -m 0 -y fable_ruin_stone.png`. **(c)** our own writer: an uncompressed 32-bit DDS with box-filtered mips is 60 lines of Python, but every stock texture checked is DXT1/DXT5, so uncompressed is untested in this client; a small DXT1 encoder (per-4x4 two-colour fit) is about 100 lines and would be tested the same way. Pillow reads DDS but does not write it.
7. **Object template.** Clone `object/static/structure/general/shared_campfire_fresh.iff` (STAT: DERV base, `0000`/PCNT, SHOT/0007 with 27 XXXX properties, each `name\0` + type bytes + value) and change `appearanceFilename` to `appearance/fable_ruin_01.apt`, `clientDataFile` to empty (no `.cdf` effect), keep the collision values (material 1, action 1, block 255; `gameObjectType` 5, `snapToTerrain` 1) and the campfire's string references for the first test (its own `objectName` is empty and its description points at `@string_table:pristine wall`); our own `.stf` entry comes later. Write it with the IFF tool so chunk sizes stay right.
8. **CRC table.** Add the template path through `tools/hoth/hoth_client_build.py`'s `object_crc_table()` path (Bellum's `cstb_tool.add` = `soe_crc(name.lower())`, the same hash Core3 uses for template names; the function already merges stock + MTG and reports clashes).
9. **Pack and stage.** All new files (`.apt`, `.lod`, `.msh`, `.sht`, `.dds`, `shared_*.iff`, the merged CRC table) into `local_planets.tre` (same packer and priority 49 as Hoth); test sessions only. Server: the Lua templates above, `local_planets.tre` first in the test galaxy's `TreFiles`, a one-line screenplay to spawn it next to the Hoth starport.

## 3. Verifying each step offline, before the owner opens the client

| Step | Check | Tool |
|---|---|---|
| 4 (.msh/.apt/.lod) | structure pairs (parent form > child) are a subset of a stock counterpart's (`decd_blba_tree_l0.msh`, `.apt`, `.lod`), SPS shader names are exactly our files, triangle indices within the vertex count, extents enclose the vertices | `trn_iff.py dump`, a structure-pair check like `trn_write.py`'s step 3 |
| 5 (.sht) | parses as SSHT/0000; the only `NAME` texture path exists in staging; effect file exists in stock (`effect/a_simple.eft`) | `trn_iff.py`, client index |
| 6 (.dds) | magic `DDS `, fourCC `DXT1`/`DXT5`, power-of-two sides, mip count = log2(side)+1 | 20-line header check (as in `ossus-assets` research) |
| 7 (.iff) | byte round trip; every XXXX name present in the campfire original in the same order; `appearanceFilename` resolves | `trn_iff.py roundtrip`, closure check |
| 8 (CRC) | table round trip reproduces the stock bytes; no clash; our entry present | `hoth_client_build.py` (existing checks) |
| reference closure | every path named by iff -> apt -> lod -> msh -> sht -> dds exists in stock or in `local_planets.tre` staging (the Hoth crash was a missing file) | `hoth_closure.py` pattern on the new tree |
| server | `luac5.3 -p` on the Lua; test galaxy boots without "template not found"; a bot `look`s at the spawned object by name and walks into it (collision) | Claude, bots |
| client | ticket to Hoth, look at the prop: draws, textured, lit, no "invalid object"; then LOD switching at distance | `um win` with the owner at the PC |

## 4. What can go wrong

- **Blender version:** 4.x removes `calc_normals_split` and Face Maps; stay on 3.6. The exporter exports every selected mesh object and ignores the file name you type.
- **Collision:** a new mesh gets `NULL` collision; the add-on cannot author `CMSH`/`EXBX` collision (it only preserves imported binary). Players may walk through the prop; stock props carry collision meshes. First test accepts this; a later fix is to copy the collision form from a stock prop of similar shape, or extend the add-on.
- **LODs:** INFO distance bands must be sane (stock: 0-100, 100-200, 200-400, 400-1000 m); a single-mesh `.apt` is the safe first step.
- **Shaders:** the suffix (`_as8`, `_aa7`, `_asb13`) is only a naming habit; what matters is the effect file and the TXM tags. A wrong tag or a missing texture is a client FATAL, as with `hoth.trn`. Alpha in a DXT1 texture is dropped; alpha needs `a_alpha` + DXT5.
- **UVs and scale:** flipped V if the export option is off; metres and Y-up/Z-up handled by the add-on, but check the box extents in the dump against the intended size.
- **Textures:** non-power-of-two or missing mips can fail silently or crash; keep 256-512 px.
- **CRC table:** an object the client cannot name shows as unknown or is dropped; `default_patch.tre` and `local_planets.tre` share priority 49, so the merged table must be in ours and contain everything stock's does (the Hoth build already handles this).
- **Server:** Core3 parses the client `.iff` from its own TRE list; a Lua template with a path that has no `.iff` in `TreFiles` fails at boot. Template names must match the path (`object_static_structure_general_...`).
- **Rights:** the pack's licence text is recorded with hash and credit at download; nothing from the client is copied into the pack.

## 5. What the owner must approve

1. Blender 3.6 LTS install (free, GPL), if not already present.
2. Installing the add-on into Blender from the local checkout (`io_scene_swg-3.1.4.zip`, MIT).
3. Downloading the CC0 pack (Quaternius Ultimate Modular Ruins; zip saved outside the client, hashed and recorded with its licence text).
4. A DDS tool: Microsoft `texconv` download (MIT, no account), or the NVIDIA Texture Tools Exporter (needs an NVIDIA account), or accepting our own DXT1/uncompressed writer as the first attempt.
5. Optional: a client extract to disk for the add-on's "Find and load materials" (stock files written to a local folder, never redistributed).
6. Adding the staged files to `local_planets.tre` for a test session, and a test-galaxy run by Claude.
7. The `um win` real-client look with the owner at the PC.
8. Optional, not required: Sytner's IFF Editor (forum account) for a second opinion on the files.
