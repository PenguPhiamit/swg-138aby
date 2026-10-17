# Vong look test: the first ComfyUI job

Claude (Opus 5.5), 17 Oct 2026, 8:10 AM. The owner asked: "lets que up our first custom creature, some vong patrols for
ossus, or should we do another local project to test things?" On the decision card they picked **"Vong look test"**.
That means the local model's first real job is a Vong warrior's look. One warrior stands at the Ossus Project fields for
the owner to see, and patrols come after that look.

**Status, 17 Oct about 9:30 AM: the base shape is now a mix, bone arms and legs plus the marauder s02 chest, with no
helmet.** Six DDS files are staged and checked, and a lit preview went to the owner. Next is the owner's view of it,
then step 4, the clone chain for the mix. Nothing has been built into an archive or installed in the game.

**Why the chitin version was dropped (owner, after its preview):** "that looks nothing like vong armor, no helmet".
- **The shape was the problem.** The stock chitin armour's squared plates, shoulder pads and visor helmet read as
  sci-fi plate whatever the texture.
- **Lineup** (`Vong-look/tools/lineup_vonduu.py`; `Vong-look/lineup/lineup_sheet.png`). There are 47 stock armour sets
  in the client, almost all trooper or sci-fi plate. Six were rendered in the same swatch-12 finish with no helmets, at
  the same scale: bone s01, marauder s01 (long coat), s02 (spiky collar), s03 (fanned shoulder spikes), acklay chitin
  and chitin s01. **Acklay chitin is the same mesh as chitin s01**, just a different texture.
- **Owner's pick: "Mix: bone + s02 collar".** Each armour piece is its own wearable, so a mix needs no mesh edits.
  Owner, on the way forward: the lineup now, our own Vong body (TRELLIS.2 draft, rigged to the human skeleton) later.
- **No helmet (owner):** the warrior is bare-headed. A bald human head in the palest stock skin tone comes first;
  scars, tattoos and eye sacs are a later head texture.

**The mix's shaders (read from the client).**
- **Bone** uses `h_color2_specmap_bump`. **The marauder chest** uses `h_color2_specmap_bump_aniso`, plus a cut-out
  chainmail part (`a_punchout_bump`, which keeps its stock texture).
- **Both pixel programs work like chitin's:** the colour texture's alpha is the hue mask, and the normal map's
  (`_n.dds`) alpha is the specular mask. So our textures carry alpha 0 again. The stock normal maps stay referenced:
  the bone and marauder relief lights over our colour.
- **Two parts take colour 0 from a palette other than `white.pal`:** the bone leggings' waist strip (`wr_metal.pal`)
  and the marauder chest (`wr_metal.pal` and `wr_cloth_general.pal`). They will carry that palette's default tint until
  step 4 rebinds colour 0 to `palette/white.pal` in our cloned shaders, as the ice rancor's builder did for its palette.
- **The bake:** `bake_vonduu.py`, `convert_vonduu.py` and `preview_vonduu.py` now take a spec file (`spec_mix.json`).
  Names are same-length renames for step 4: `armor_bone_*` -> `armor_vong_*` and `armor_marauder_*` ->
  `armor_vongcrab_*`.
  - Six textures: bicep, bracer and boots 256x128; gloves 128x64; leggings 256x256 (both leggings shaders); and the
    chest 256x256 (both chest shaders).
  - All pass: DXT5, the stock size, full mips (9, gloves 8), alpha 0, colour error 2.0-2.7.
  - The orientation proof was not repeated for the mix: the same importer and bake code are used.
- **GPU or CPU (owner, twice):** only the image runs use the RTX 5070, at about 4 s an image, so the spikes are short.
  The bakes, previews and the lineup run Blender on the CPU by design (10-23 s each), to leave the card free. Blender
  3.6 does list the 5070 for CUDA and OptiX, so a GPU switch is possible; whether it works on the 50-series is
  untested.

**The earlier chitin status (9:05 AM), kept for the record:** steps 1-3 were done on the chitin armour, with seven DDS
files staged and checked.

**Step 3 results (8:58 to 9:05 AM, Blender 3.6.23 on the CPU).**
- **What the armour shader does** (read from the client: `effect/h_color2_envmask_specmap.eft` and its pixel programs):
  - the colour texture's **alpha is the hue mask**: hue = lerp(colour 0 from `palette/white.pal`, colour 1 from
    `palette/wr_chitin_armor.pal`, alpha);
  - the `_spec` texture is the specular mask, and its alpha masks the environment reflection
    (`texture/env_pseudo_irid.dds`);
  - so our colour textures carry **alpha 0**: no palette tint, our colours exactly. That has to be DXT5; DXT1 would
    read as alpha 1, full tint. No palette rebinding is needed (unlike the ice rancor). The stock `_spec` and env maps
    stay referenced by name.
- **`Vong-look/tools/bake_vonduu.py`** imports each stock male `_l0` mesh with the add-on's own importer (identity
  matrix) and paints it with swatch 12 by box projection in object space (1.5 repeats a metre, blend 0.3), darkened by
  ambient occlusion (0.05 m, mapped to 0.55-1). It then bakes the colour (an EMIT bake, 64 samples, 8 px margin) into
  each piece's own UV layout at the stock size:

  | Texture | Size |
  |---|---|
  | bicep, bracer, boots, leggings | 128x256 |
  | chest plate, helmet | 256x256 |
  | gloves | 128x128 |

  Bicep and bracer bake from the left piece; left and right share one texture. The helmet's visor faces (`_has15`)
  bake into a throwaway image, so the visor keeps its stock texture. All seven take 10 s. `bake_report.json` lists the
  meshes, materials and triangle counts.
- **Orientation, proved without stock art:** the raw UV triangles read from each `.mgn` and drawn with row 0 at the
  top match the bake masks at 96-99% overlap, against 66-96% when flipped either way. (A first test that compared
  stock texture detail was inconclusive, because stock textures are painted past their islands.) The one assumption
  left is the Direct3D rule that DDS row 0 is the top of the texture; the in-game look confirms it.
- **Brightness:** the bakes average a luminance of about 30 of 255, as dark as the swatch, and the client lights the
  colour without a hue. `Vong-look/tools/convert_vonduu.py` therefore lifts the midtones (gamma 0.7, to about 57), sets
  alpha 0, and writes BC3 with full mips through texconv.
  - It checks each file: DXT5, the stock size, the stock mip count (9, gloves 8), alpha 0, and a mean colour error of
    1.8-2.9 out of 255. All seven pass.
  - Output: `Vong-look/staged/client/texture/armor_vonduu_*.dds` (gitignored; rebuilt by the script). The untouched
    bakes stay in `Vong-look/bake/`.
- **`Vong-look/tools/preview_vonduu.py`** renders the nine male pieces with the staged textures (back, back
  three-quarter, front; `Vong-look/bake/preview_sheet.png`).
  - It reads as dark grey crab-shell plating. Swatch 12's red crevices mostly wash out at this size, and the seamless
    cross-blend shows as a few mirrored V shapes on the chest.
  - It is a preview with flat studio light, no body underneath and no client lighting.

**Rounds 2 and 3** (owner: "Another round", with a screenshot of an image search for the species as the look they
want). The screenshot was used only as a description by eye. It was not fed to the model, because those pictures are
other artists' Star Wars art.
- **What I took from it:** a crustacean or insect exoskeleton rather than tiles, irregular ribbed segments with spines
  and horn-like spurs, and charcoal, slate blue-grey and olive-bronze colours with much less red.
- **Round 2 (5-8):** the colours were right, but the model drew whole shells on a grey background. Once mirrored by
  `um sprite seamless`, that background would show as stripes, so round 2 is superseded. Concept sheet 8 has the right
  armour but a reptilian head.
- **Round 3 (9-12):** the same looks, with prompts that begin "Close-up of a surface completely covered edge to edge
  by ..." and say "fill the entire frame with no background and no gaps". All four fill the frame and tile after the
  seamless pass, with faint doubled plates from the cross-blend.
- **The owner chose 12:** rough, irregular dark crab shell with bumps, spurs and a deep red tint in the crevices.
- **The RAM error and the fix.** Round 2's second image failed with a `MemoryError` while ComfyUI streamed the 8 GB
  text encoder (`hostbuf_file_reader_read failed`); about 9 GB of Windows RAM was free. A retry worked. Round 3 ran
  with `--disable-pinned-memory`: no errors, 24.5 s cold, 2.1-3.5 s an image.

## The look in game (Wookieepedia, Legends, "Biology and appearance", read 17 Oct in the browser pane)

The owner asked whether the Vong are paler white or green and a little more humanlike. The article, in our words:
- **Body:** humanoid and humanlike, but much taller and heavier than humans.
- **Head:** sloping, ridge-like foreheads; short stub noses, so the faces look skull-like; pointed ears on some.
  Little hair: black, often long, or completely bald.
- **Skin:** grey is the most common tone, and yellow the second. Pale greys fit; green is not listed.
- **Other sources (owner: "you can check other sources too").**
  - The Alien Species wiki and the Archivum mirror give the same grey-then-yellow ranking.
  - A toy review calls them pale grey (an opinion, not canon).
  - Slayers have black skin that is really bonded armour.
  - Wikipedia gives no colour.
  - Wookieepedia's character infoboxes, read through its API in the browser pane: many leave skin blank. The ones that
    give it:

    | Character | Skin |
    |---|---|
    | **Nei Rin**, the Ossus Project's Master Shaper | "White with purple tattoos" |
    | **Zenoc Quah**, the fanatic shaper who helped the One Sith sabotage the project | "Light gray with black tattoos" |
    | Khalee Lah | "Gray" |
    | the Vong spy at Coruscant's Leafy Green tapcafe | "Pale" |

  - **No source gives green;** it shows up only as a tint in some art. For our Ossus Vong, Zenoc Quah's kind (the
    `vong_fanatic` patrols) are **light grey to white with black tattoos**, and Nei Rin's Shapers are white with
    purple tattoos.
- **Other marks:** small blue sacs under the eyes that swell with mood; black blood; heavy ritual scars and tattoos.

What that means for us:
- **Height and build.** The human male body already gives the humanlike shape. The mobile template's scale (about
  1.15) gives the height.
- **The first look keeps the chitin helmet on.** No skin shows, so the armour is the whole test.
- **A bare-headed Vong is a later job.** Grey or yellow skin, eye sacs, scars and tattoos need a head texture of our own
  on a cloned human head chain. Alternatively, a stock skin palette rebound the way the ice rancor's was, which would
  give the colour but no scars. Stock human skin tones are natural colours (to be checked for a pale grey).

**Step 1 results** (8:24 to 8:26 AM; the timings and memory figures are in `local-art-models.md`). The images are in
`outputs/Vong-look/gen/`; the PNGs are gitignored, and `comfy_manifest.jsonl` holds each prompt, seed and workflow.

| # | File | What came out |
|---|---|---|
| 1 | `vonduun_1.png`, `_seamless`, `_tiled2x2` | dark oxblood and black shell plates in a diamond pattern, bone-white ridged seams with thorns. Closest to the brief, but quite regular. |
| 2 | `vonduun_2…` | maroon scales with grey coral crust and dark red cracks. Rougher, more "living coral". |
| 3 | `vonduun_3…` | glossy black tile-like plates with thin crimson seams and small barbs. Reads as beetle chitin. |
| 4 | `vonduun_4.png` | concept sheet: a grey-skinned scarred warrior in red and black segmented armour with bone shoulder spurs, staff upright, front and side. Reference only. |

None tiled straight from the model. `um sprite seamless` made all three tile (2x2 previews), and its cross-blend
leaves some doubled lines on the ridges. The server lock belongs to the main session (run 27, the pet check), so
the server side of step 5 is staged as a patch for the lock holder. This session does not touch `/opt/swg`.

## What the files say (read today from the client archives)

- **No Vong exist in the client.** There is no `object/mobile/*vong*`, no Vong body and no amphistaff. A Vong warrior is
  therefore a human NPC (the human skeleton `all_b.skt`) in stock **chitin armour**, carrying a stock staff.
- **Chitin armour** (`patch_01`; MTG adds an acklay variant) has nine pieces: two biceps, two bracers, boots, chest plate,
  gloves, helmet and leggings. Each piece has `_m` and `_f` `.sat` files, a `.lmg`, and four LOD `.mgn` files.
- **Its shaders** are eight stock `hces24` shaders, plus `armor_chitin_visor_has15`:

  | Texture | Size |
  |---|---|
  | `armor_chitin_chest_plate.dds`, `armor_chitin_helmet.dds`, `armor_chitin_visor.dds` | 256x256 DXT5, 9 mips |
  | `armor_chitin_bicep.dds`, `armor_chitin_bracer.dds`, `armor_chitin_boots.dds`, `armor_chitin_leggings.dds` | 128x256 DXT5, 9 mips |
  | `armor_chitin_gloves.dds` | 128x128 DXT5, 8 mips |

  Each colour texture has a matching `_spec` map. The helmet also has an `_env` map.
- **The textures follow the meshes' UV layout.** A generated picture cannot replace one directly. It has to be baked
  onto each mesh's own UVs (step 3).
- **Lore.** In 138 ABY, Nei Rin's Shapers are friendly to the Jedi and hidden (`Fable-factions/README.md`). Hostile
  patrols are therefore the planned `vong_fanatic` side, guarding the feral Ossus Project fields: POI 7 in
  `Fable-ossus/o6/README.md`, in the forest east at (1400, 4900). The era fit is invented and flagged as such
  (backlog CR-02). Ossus is closed for the friends launch, so all of this is test-galaxy content.

## The steps

1. **First ComfyUI run (needs the owner out of the game).**
   - Start `C:\Users\Pengw\Tools\ComfyUI_windows_portable\advanced\run_nvidia_gpu_disable_api_nodes.bat`, then run
     `um comfy status`.
   - Run the four prompts below with `um comfy run outputs/tools/comfy/flux2-klein-4b-t2i.json --set 74.text="..."
     --set 73.noise_seed:=<n> --name vonduun_<n>`. The workflow is the 4-step distilled graph, rebuilt by hand in API
     form from ComfyUI's bundled template (`image_flux2_klein_text_to_image.json` in
     `comfyui_workflow_templates_json` 0.1.110) using our fp8 file. It is untested until this run.
   - Record seconds per image, peak VRAM (`nvidia-smi`) and free RAM in `local-art-models.md`.
2. **The owner picks one swatch**, by looking at it. Then run `um sprite seamless`, scale it to 512 px and check that it
   tiles.
3. **Bake it onto the armour (Blender 3.6.23, NSG SWG Tools).**
   - Import the nine male `_l0` chitin `.mgn` files.
   - Give them our material with a box (triplanar) projection, so no stock texture pixel is used, only the meshes'
     UVs.
   - Bake the colour, with a little ambient occlusion for depth, into each piece's layout at the stock sizes above.
   - Result: eight PNGs, which texconv turns into DXT5 with full mips.
4. **Clone the client files the way the ice rancor did** (`Hoth-leftovers/build_hoth_leftovers.py`).
   - Use a same-length rename, `armor_chitin` to `armor_vonduu` (12 characters each), so every chunk keeps its size.
   - New files:
     - 9 male `.sat` and `.lmg` files and their 36 `.mgn` (only the shader names inside them change);
     - 8 `.sht` files pointing at our colour textures, with the stock `_spec` and `_env` maps kept by reference;
     - 8 `.dds` files;
     - 9 wearable templates `object/tangible/wearables/armor/vonduu/shared_armor_vonduu_s01_*.iff`, with their CRC rows
       and a name string.
   - Female files only if a female warrior is wanted later. The new files go into a test archive on top of the
     installed one. Players' own chitin armour does not change.
5. **The warrior (staged as a patch; the lock holder applies and restarts).**
   - Server templates for the nine wearables.
   - An outfit `vong_fanatic_warrior`, and a mobile `vong_fanatic_warrior` on the human male body with a stock staff.
   - For the look it is not attackable and has no faction yet.
   - One spawn at POI 7 (1400, 4900) on the test galaxy. The client archive goes on both sides.
6. **The owner looks** in the client and says what they see (an open question, not prefilled answers).
7. **Then, as a second job:** 2-3 patrols on a route through the fields, the `vong_fanatic` faction from the FW-01
   plan, levels, loot, an amphistaff look (a staff with our texture, the same method) and ritual-scar head textures.

**Fallback if the bake or the clone fails:** the `hces24` shaders take hue variables. So an NPC outfit can wear the stock
chitin in dark red with no client change at all. That look is weaker, but it needs only the server side.

## The prompts (the materials are described; no franchise, character or artist names)

| # | Seed | Prompt |
|---|---|---|
| 1 | 1 | Seamless tileable texture, flat top-down view of overlapping segmented crab-shell armour plates, dark oxblood red and charcoal black carapace with bone-white ridged edges, small thorn-like spurs along the seams, faint organic pores, slight waxy sheen, evenly lit, no shadows, no perspective, game texture |
| 2 | 2 | Seamless tileable texture, living coral grown into interlocking armour scales, deep maroon with grey coral crust and dark red veins, rough and pitted, evenly lit, flat, no perspective, game texture |
| 3 | 3 | Seamless tileable texture, glossy black beetle-like chitin plates with thin crimson seams and small barbs, layered like roof tiles, evenly lit, flat, no perspective, game texture |
| 4 | 4 | Concept art sheet, full-body front and side view of a tall alien warrior in living segmented crab-shell armour, dark red and black plates with bone-coloured spurs at the shoulders, a long staff held upright, ritual scars and tattoos on a grey face, neutral grey background, no text |

Prompt 4 is a reference for the owner and for step 7, and is not shipped. Every image kept is recorded with its model
file, seed and prompt (`comfy_manifest.jsonl`). The image files stay out of git.

## Found on the way

ComfyUI 0.41.0 also ships templates for **FLUX.3 [klein]**. That model's repo
(`black-forest-labs/flux-3-image-klein-comfy`, created 14 Oct 2026) carries the tag `license:other` and is gated, so it
is not the Apache 2.0 licence of FLUX.2 [klein] 4B. Read its terms before considering it.
