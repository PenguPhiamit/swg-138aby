# C15: reusable art and audio shortlist

Checked 14 October 2026 by ChatGPT. Research only: no asset downloads, purchases, imports or runtime tests. The ten entries in the JSON are candidates for selection, not installed content. Sources are creator pages; package file lists/hashes and bundled licences must be captured when an owner-authorized download happens.

## First ten candidates

All ten are advertised under **CC0 1.0 Universal**. Its [legal text](https://creativecommons.org/publicdomain/zero/1.0/legalcode) permits copying, alteration and redistribution, including adapted files inside a client TRE. Attribution is not required; our project still records creators and provenance. Suggested credits below are voluntary. No payment is required for the identified free material; optional donations and paid tiers are separate.

| Priority | Creator source | Useful for | Published formats/resolution | Voluntary credit |
|---|---|---|---|---|
| 1 | [Poly Haven Snow 02](https://polyhaven.com/a/snow_02) | Hoth ground | PNG/JPG/EXR maps, 1–8K; 2 m source scale | Snow 02 — Rob Tuytel / Poly Haven, CC0 1.0 |
| 2 | [Poly Haven Snow 01](https://polyhaven.com/a/snow_01) | Alternate snow surface | PBR maps; exact chosen files to record at download | Snow 01 — Poly Haven, CC0 1.0; record named artist at selection |
| 3 | [Poly Haven Snow Field Pure Sky](https://polyhaven.com/a/snow_field_puresky) | Hoth sky and reflection source | HDR/EXR, 1–16K; tonemapped JPG available | Snow Field Pure Sky — Jarod Guest and Sergej Majboroda / Poly Haven, CC0 1.0 |
| 4 | [Poly Haven Metal Plate](https://polyhaven.com/a/metal_plate) | Outpost floors and industrial props | PNG/JPG/EXR, 1–8K; 0.5 m source scale | Metal Plate — Rob Tuytel / Poly Haven, CC0 1.0 |
| 5 | [Quaternius Ultimate Modular Sci-Fi](https://quaternius.com/packs/ultimatemodularscifi.html) | Original outpost rooms and props | 46 models, FBX/OBJ/Blend; texture dimensions unverified | Ultimate Modular Sci-Fi Pack — Quaternius, CC0 1.0 |
| 6 | [Kenney Modular Space Kit](https://kenney.nl/assets/modular-space-kit) | Modular station blockout | 40 files; animations/variants advertised; archive formats unverified | Modular Space Kit — Kenney, CC0 1.0 |
| 7 | [Quaternius Sci-Fi Essentials](https://quaternius.com/packs/scifiessentialskit.html) | Crates, screens, robot concepts | FBX/OBJ/Blend/glTF; free subset only, not every advertised model | Sci-Fi Essentials Kit — Quaternius, CC0 1.0 |
| 8 | [Kenney Sci-fi Sounds](https://kenney.nl/assets/sci-fi-sounds) | Terminals, machines and effects | 70 files; encoding/sample rates unverified | Sci-fi Sounds — Kenney, CC0 1.0 |
| 9 | [Kenney Particle Pack](https://kenney.nl/assets/particle-pack) | Snow, mist and effect texture experiments | 80 images, 512×512; archive image encoding unverified | Particle Pack — Kenney, CC0 1.0 |
| 10 | [cgbookcase Patch 06](https://www.cgbookcase.com/textures/patch-06) | Masked surface detail/decal experiments | Base colour, AO, height, mask, DX normal, roughness; exact sizes/encoding unverified | Patch 06 — Dorian Zgraggen / cgbookcase, CC0 1.0 |

Rights evidence: [Poly Haven asset licence](https://polyhaven.com/license) expressly includes original/donated art and redistribution; [cgbookcase texture catalogue](https://www.cgbookcase.com/textures) links CC0 1.0; each Kenney and Quaternius page above has its own CC0 link. Website text, logos and preview renders are not automatically covered by Poly Haven's asset grant. Do not package those previews.

## Other useful sources and licence gates

[ambientCG's creator licence](https://docs.ambientcg.com/license/) explicitly allows raw files inside games, modification and redistribution under CC0 1.0. Strong additional source for snow, sand, rocks, forest ground and industrial surfaces; individual asset IDs, formats and resolution remain to be selected. Optional credit: “Created using <asset name> from ambientCG.com, licensed under the Creative Commons CC0 1.0 Universal License.” No bulk fetch performed.

[ShareTextures terms](https://www.sharetextures.com/p/terms) advertise CC0 1.0 but separately prohibit automated scraping/downloads and unauthorized API use, and contain confusing revocation language. **Hold for manual selection/terms clarification before acquisition**; not in the first ten. No integration or download service proposed.

No CC-BY or CC-BY-SA package was selected in this bounded pass: ten suitable CC0 candidates are available. For future CC-BY entries, record the exact version, creator, title, source and licence links and indicate modifications in credits. For CC-BY-SA, preserve the selected version's attribution and ShareAlike conditions for adapted assets; do not assume either that the entire game becomes ShareAlike or that packing an adaptation in a TRE removes those duties. Mixed-contributor sites such as OpenGameArt require a per-release audit. NC, personal-use-only, no-redistribution, game rips and AI packs of unclear provenance are excluded from this shortlist.

## SWG adaptation, proposed and untested

Local evidence: [format inventory](swg-format-inventory.md) identifies `.msh` material references, client `.sht` shader templates and DDS textures. It does not prove every map is supported by every pre-CU shader. Select a known working local `.sht`/effect combination before choosing its map slots. Free GLSL/HLSL, Unity URP, Unreal and Godot shaders cannot simply be copied into SWG; Quaternius's paid source-tier hologram shaders are not needed for the free static props.

| Source data | Proposed adaptation | Acceptance check |
|---|---|---|
| Base colour | Diffuse DDS, modest 512/1024 starting sizes and mipmaps | Colour space, tiling and readability in the real client |
| Normal | Use only a normal-capable SWG shader; confirm handedness/channel encoding | Known-direction relief test; don't assume DX suffix alone proves compatibility |
| Roughness/metalness | Author legacy specular/gloss response; inverse roughness is only a starting approximation | Compare painted metal and bare metal under several lights |
| AO | Optional mild diffuse bake; avoid double-darkening | Shadows and night lighting |
| Emission | Emissive-capable template/texture where available | Day/night and bloom settings |
| HDR environment | Tonemap and convert to the sky/reflection layout SWG expects | Orientation, seams, exposure, weather/day cycle |
| Height | Bake appropriate detail; no automatic terrain geometry/displacement | Ground seams, navigation and collision unaffected |
| Particle images | SWG particle appearance/effect with correct alpha blend | Sorting, framerate and transparency |

DDS DXT1/BC1 is a candidate for opaque colour; DXT5/BC3 for smooth alpha. Preserve suitable normal-map encoding rather than blindly compressing everything as DXT1. This is a proposed conversion plan, not a renderer guarantee. Sound files likewise need a compatible SWG sound template and tested codec/channel/sample settings. Room meshes need cells, portals, collision and navigation; a CC0 model alone is not a usable dungeon.

Before import: save exact release/version, files and SHA-256 hashes, bundled licence text, every contributor and chosen credit; convert one small static prop/material first; test in the real client. No such import or test has occurred in C15.
