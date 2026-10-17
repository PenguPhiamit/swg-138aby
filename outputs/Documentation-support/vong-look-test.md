# Vong look test: the first ComfyUI job

Claude (Opus 5.5), 17 Oct 2026, 8:10 AM. The owner asked: "lets que up our first custom creature, some vong patrols for
ossus, or should we do another local project to test things?" On the decision card they picked **"Vong look test"**.
That means the local model's first real job is a Vong warrior's look. One warrior stands at the Ossus Project fields for
the owner to see, and patrols come after that look.

**Status: queued. Nothing has been generated, built or installed.** The ComfyUI run waits until the owner is out of the
game (two SWGEmu clients were open at 8:00 AM). The server lock belongs to the main session (run 27, the pet check), so
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
