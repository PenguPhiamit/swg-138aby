# Local AI models for art and planet work on Miniverse

Claude (Opus 5.5), 17 Oct 2026, 7:46 AM. The owner asked: "can you see if you can find a local model that can run on my pc and
do some of the art and/or planet work for us?"

Research only. Nothing was downloaded or installed and no model was run. Every speed and VRAM figure below is published
by the model's makers or by ComfyUI, not measured on this card. File names, sizes and licence tags were read from the
Hugging Face and GitHub APIs today.

## The short answer

- **Yes for 2D art.** ComfyUI with **FLUX.2 [klein] 4B** (Apache 2.0) fits the 12 GB card. It can make the flat art we
  are waiting on: kajidic seals and banners, the Hutt sash decal, scenic loading screens, concept sheets and texture
  sources. Our existing tools turn those images into SWG files: texconv makes the DDS, and Blender clones the shaders.
- **Maybe for 3D props.** ComfyUI now runs **TRELLIS.2** (MIT) natively, without compiling anything. Its makers ask
  for 24 GB of VRAM; whether the int8 build fits in 12 GB is untested. Even when it fits, its meshes are far too dense
  for SWG and need Blender cleanup. Treat it as an experiment.
- **No for planets and animation.** SWG terrain (`.trn`) is a stack of fractal and bitmap layers that our scripts
  already write. The Ossus map, globe and loading tile were rendered from that terrain (O3). A generated heightmap
  would not match the terrain the server computes. No model makes `.ans` animations for the Hutt skeleton, and none
  weights a mesh to `hutt.skt`.

## The owner's pick (17 Oct, about 7:55 AM)

**"2D art + 3D test"**, chosen on the decision card: picks 1 and 3, nine files and 23.42 GB, each listed on the card with
its source and size. Not chosen: Hunyuan3D 2.0 and SDXL. Each file goes into its own folder under
`C:\Users\Pengw\Tools\downloads` and is checked against the size and SHA-256 that its host publishes. The install
record is at the end of this note.

## This PC (measured 7:39 AM)

| Part | Measured | What it means |
|---|---|---|
| GPU | NVIDIA GeForce RTX 5070, 12,227 MiB VRAM, compute capability 12.0 (Blackwell), driver 617.14 (CUDA 13.4), 250 W | Blackwell needs a PyTorch build for CUDA 12.8 or later. ComfyUI's portable build ships PyTorch for CUDA 13.0, and this driver supports it. |
| VRAM in use | 2,121 MiB used, 9,823 MiB free, with two SWGEmu clients, Opera, Discord, VS Code and both agent apps open | The game shares the card, so generation and play should not overlap (see the rules below). |
| RAM | 31.9 GB (2 x 16 GB DDR4 running at 2400; the modules are rated 3600) and 6.4 GB free in Windows | WSL uses 10.8 GB (`vmmemWSL`). `.wslconfig` sets no memory cap, so the default of half the RAM applies, and Debian sees 15.9 GB. The test galaxy alone uses 6.2 GB. Free Windows RAM is the tightest limit, because ComfyUI parks model weights in RAM between steps. |
| CPU | Ryzen 5 5600X, 6 cores / 12 threads | Generation runs on the GPU, so it does not compete with the bots for CPU the way builds do. |
| Disk | C: 952.8 GB, 90.3 GB free | Pick 1 needs about 20 GB (the unpacked size of ComfyUI is assumed). Everything in this note together needs about 40 GB. |
| Already installed | Blender 3.6.23 portable with NSG SWG Tools 3.1.4, texconv (`C:\Users\Pengw\Tools`), Universal Modder with `um comfy` and `um sprite seamless`, Ollama (text only) | `um comfy` already drives a local ComfyUI. Only ComfyUI and the model files are missing. |

## The art and planet jobs that are waiting

| Job | Where | What the client needs (sizes checked today in the client archives) | Local AI fit |
|---|---|---|---|
| Kajidic seals: banners, the Hutt sash decal (three colours) | PL-04, `nal-hutta-home.md` question 3, SP-04 item 1 | a 512 px DDS (DXT1, or DXT5 for alpha) behind a cloned shader | **good**: flat graphic design; the edit mode makes the colour variants |
| Scenic loading screens for Nal Hutta (on the stock generic tile now), and nicer ones for Ossus (its tile is the map, filtered) | `nal-hutta-first-look.md`, Ossus O3 | mostly 512x512 DXT1 (253 of the 545 stock loading textures), some 256x256 | **good** |
| Concept sheets: Hutt gear, Bilbousa palace, the Dantooine enclave ruins, the voxyn | SP-04, PL-04, PL-08, CR-02 | none; they are reference for Blender work, not shipped | **good** |
| Ground and prop textures for ruin pieces, the farming planter and retextures of CC0 kits | PL-08, PR-07 | 256-512 px DDS with a full mip chain | **good**: images plus `um sprite seamless` |
| Static props: plant growth stages, ruin pieces, crates | PR-07, PL-08 | `.msh` under about 2,000 triangles, one or two 256-512 textures. The static prop path is proven (the Quaternius wall drew in the client on 15 Oct). | **experimental**: an image-to-3D draft, then Blender decimation and baking |
| Hutt gear, levels 2 and 3 (ten items rigged to `hutt.skt`, new animations) | SP-04, SP-05 | skinned `.mgn` weighted to Hutt bones; `.ans` (no working exporter yet) | **poor**: concept and textures only. Modelling, weighting and animation stay manual. |
| Terrain, maps and globes for new planets | PL-01, PL-09 and later | `.trn` layers; maps at 1024x1024 DXT1; globes at 256x256 DXT1 with 9 mips | **none needed**: rendered from our own terrain (Ossus O3); MTG ships Nal Hutta's |

## Ranked picks

### 1. ComfyUI + FLUX.2 [klein] 4B: seals, loading screens, concept art, texture sources (recommended)

- **Model.** FLUX.2 [klein] 4B, the distilled 4-step build, in fp8. It does text-to-image and image editing with
  reference images, so we can keep one seal design and recolour it three ways.
- **Licence.** The weights are Apache 2.0: tagged on `black-forest-labs/FLUX.2-klein-4b-fp8`, not gated, and the model
  card says "available for commercial use". The Qwen3 4B text encoder and the VAE come from
  `Comfy-Org/vae-text-encorder-for-flux-klein-4b`, also Apache 2.0. ComfyUI itself is GPL-3.0, which is fine for local
  use. Avoid the **9B** klein: BFL asks you to accept a separate agreement before downloading it.
- **VRAM fit.** ComfyUI's guide gives 8.4 GB for this model (measured on an RTX 5090, 1.2 s per image). We had 9.8 GB
  free with the game open, so it fits, but only just. On the 5070 expect a few seconds per 1024 px image (assumed).
- **Downloads (each needs the owner's yes):**

  | File | Source | Size |
  |---|---|---|
  | `ComfyUI_windows_portable_nvidia.7z` (v0.41.0, 15 Oct 2026) | github.com/Comfy-Org/ComfyUI releases | 2.01 GB |
  | `flux-2-klein-4b-fp8.safetensors` | huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8 | 4.07 GB |
  | `split_files/text_encoders/qwen_3_4b.safetensors` (the file the guide uses; the same repo has a 3.85 GB fp4 file, untested) | huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b | 8.04 GB |
  | `split_files/vae/flux2-vae.safetensors` | same repo | 0.34 GB |

- **Install steps** (after the owner's yes):
  1. Download the four files. Check the 7z's SHA-256 against the release page.
  2. Extract the 7z to `C:\Users\Pengw\Tools\ComfyUI_windows_portable` (Windows 11 opens .7z itself).
  3. Put the model files in `ComfyUI\models\diffusion_models`, `text_encoders` and `vae`.
  4. Start it with `advanced\run_nvidia_gpu_disable_api_nodes.bat`. That script passes `--offline`, which turns off
     the paid API and partner nodes. It listens on 127.0.0.1:8188 only (the default in `cli_args.py`); never add
     `--listen`. Install no custom nodes and no ComfyUI-Manager extras without a separate OK.
  5. Run `um comfy status`. Load the klein 4B template from ComfyUI's template browser and export it as API JSON to
     `outputs/tools/comfy/flux2-klein-4b.json`. Run it with `um comfy run`, which logs the workflow, seed and files to
     `comfy_manifest.jsonl`.
  6. First test, with the owner not playing: one 1024 px kajidic seal and one loading screen. Record VRAM (`nvidia-smi`),
     free RAM and seconds per image in this note. Then convert one of them with texconv (BC1 or BC3, `-m 0`,
     power-of-two size) into the test archive.
- **Verified vs assumed.** Verified today: licence tags, gating, file names and sizes, ComfyUI's bundled CUDA 13.0, and
  this card and driver. Assumed: the VRAM figure on a 5070, the speed, and whether the result looks good enough.

### 2. Seamless textures: `um sprite seamless` first, SDXL only if seams show

- **Job.** Ground and prop textures that tile (ruin stone, planter metal, cushions).
- **Route.** Generate a texture with pick 1, then run `um sprite seamless in.png out.png`. That is an offset and
  cross-blend; it is already installed and is not AI. Nothing new to download.
- **If the seams are bad:** SDXL base 1.0 (`sd_xl_base_1.0.safetensors`, 6.94 GB, huggingface.co/stabilityai/
  stable-diffusion-xl-base-1.0, CreativeML Open RAIL++-M) with a circular-padding tiling node. The padding trick works
  on SDXL's convolution network, not on FLUX's transformer. The node is third-party code, so it is a separate download
  to check and approve. SDXL is widely run in 8 GB (assumed here).
- **Not useful:** PBR map generators. Pre-CU shaders use a diffuse texture plus an optional normal map (`_asb13`). They
  have no roughness or metalness slots, and Blender already bakes normal maps.

### 3. TRELLIS.2 in ComfyUI: image-to-3D drafts for static props (experimental)

- **Job.** A first shape and texture for a plant stage, a ruin piece or a crate, from a concept image made in pick 1.
- **Licence.** MIT for code and weights (the repo says so; `Comfy-Org/TRELLIS.2` is tagged MIT). Background removal
  uses BiRefNet, also MIT.
- **VRAM fit: unknown.** Microsoft's own code asks for 24 GB, is tested only on Linux, and needs compiled CUDA
  extensions. ComfyUI 0.34.0 and later run it natively in PyTorch with an int8 checkpoint, which avoids the build
  problems on Blackwell and Windows. Nobody publishes a 12 GB figure. Try the 512 preset first, then 1024_cascade.
- **Downloads:** `diffusion_models/trellis_2_int8_convrot.safetensors` 5.25 GB, `vae/trellis_2_shape_vae_bf16.safetensors`
  1.10 GB, `vae/trellis_2_texture_vae_bf16.safetensors` 0.95 GB and `clip_vision/dino_v3_vit_l.safetensors` 1.21 GB
  (all huggingface.co/Comfy-Org/TRELLIS.2), plus `background_removal/birefnet.safetensors` 0.44 GB
  (huggingface.co/Comfy-Org/BiRefNet). Total 8.95 GB. ComfyUI's template loads Pixal3D by default (MIT, another 6.8 GB);
  set its switch to TRELLIS.2 and skip Pixal3D.
- **Then by hand:** in Blender 3.6, decimate the mesh from up to a million faces to under 2,000 triangles. Bake its
  colour to one 256-512 texture, then follow the F86 path (`Fable-asset-pipeline/README.md`): NSG `.msh` export, `.apt`,
  a cloned `_as8` shader, texconv DDS and the CRC row. Collision stays `NULL`, as for the wall.
- **Verified vs assumed.** Verified: licences, file sizes, that the nodes are native since 0.34.0, and Microsoft's
  24 GB/Linux statement. Assumed: that it runs in 12 GB at all, and how much cleanup each mesh needs.

### 4. Fallback for 3D shape only: Hunyuan3D 2.0 single view

- **Use it only if pick 3 does not fit.** ComfyUI's guide gives 6 GB for shape generation. ComfyUI's native node makes
  no texture, so we would texture it in Blender.
- **Download:** `hunyuan3d-dit-v2-0/model.fp16.safetensors` 4.93 GB (huggingface.co/tencent/Hunyuan3D-2), renamed
  `hunyuan3d-dit-v2.safetensors`.
- **Licence catch.** The Tencent Hunyuan 3D 2.0 Community License excludes the EU, the UK and South Korea, and its
  outputs "may not be used, distributed, or displayed" outside the remaining territory. A friend in the UK or the EU
  could not legitimately see such a prop, so MIT TRELLIS.2 comes first.

### Looked at and not recommended

- **Z-Image Turbo** (Apache 2.0, 6B): documented for 16 GB cards; klein 4B covers the same job in 12 GB.
- **Qwen-Image** (20B): too large for this card without heavy quantisation.
- **FLUX.1 [dev] and the 9B klein:** non-commercial or gated licences, for no gain over the Apache 4B.
- **Stable Fast 3D** (Stability Community License, free below US$1M revenue): it makes low-poly UV-mapped meshes, which
  would suit SWG well. But the weights are gated (the owner would need their own Hugging Face account), and on Windows
  it needs a Visual Studio 2022 build that its makers call experimental.
- **Terrain Diffusion** (xandergos; code MIT, licence for the weights not stated): it makes real-scale elevation
  GeoTIFFs. Our terrains are fractal layers plus 8-bit bitmaps that Core3 also reads, so an AI heightmap adds little
  over the painted bitmaps in `ossus_terrain.py`.
- **Text-to-motion and auto-rigging models:** they target human skeletons or invent new skeletons. Neither helps the
  Hutt, whose gear must be weighted to `hutt.skt` and whose animations need an `.ans` exporter we do not have yet.
- **Upscalers** (Real-ESRGAN and similar): only for our own images. An upscale of stock SWG or KOTOR art is a stock-file
  derivative and stays excluded (AGENTS.md, Ethics check 1).

## What a local model cannot do for SWG's formats

- It outputs PNG images and GLB meshes, nothing SWG reads directly. Every asset still goes through the existing chain:
  texconv to DDS (DXT1/DXT5, power of two, full mips for props), Blender 3.6 with NSG SWG Tools to `.msh`/`.apt`,
  `tools/swgfmt` and `trn_iff.py` to clone the shaders and templates, the CRC table, and `local_planets.tre`. Then
  bots and the owner check it in the client.
- It cannot write `.trn`, `.ws`, `.mgn` weights, `.skt` or `.ans` files. It cannot make collision meshes either: new
  props get `NULL` collision, as the wall did.
- Its meshes are dense and their UVs are messy. Getting a prop down to SWG's budget is Blender work, every time.

## Rules for using it

1. **Inputs.** Use only our own images, CC0 sources or text prompts. Never use stock SWG or KOTOR client art,
   Wookieepedia images or screenshots of other servers as an edit or reference input for anything we ship. Never
   prompt for named Star Wars characters, logos or living artists. Describe what we want instead: "a broad diagonal
   silk sash with a coiled-serpent clan seal".
2. **Records.** For every asset that ships, keep the model file and its hash, the prompt, seed and workflow
   (`comfy_manifest.jsonl`) next to the asset, and an "AI-generated with FLUX.2 [klein] 4B" line in the credits.
   Generated images stay out of git (the `.gitignore` already keeps images out); the workflows and manifests go in.
3. **Sharing the PC.** Generate only when the owner is not playing, as with builds. The game and the model share the
   12 GB card, and free Windows RAM was 6.4 GB this morning. Closing the browser helps more than anything else.
4. **Paid nodes.** ComfyUI's "API" or partner nodes are paid cloud services. Don't use them; they are the fal
   question again.

## Answers to ChatGPT's 13 Oct workflow questions

This note is Claude's response to `asset-workflow-review-for-Claude-2026-10-13.md`.

1. Local first, yes, with ComfyUI-native TRELLIS.2 (MIT) in place of TripoSR. TripoSR is from 2024 and lower in
   quality, and the native nodes avoid compiling CUDA extensions on Blackwell.
2. The static-prop path is proven: Blender 3.6.23 with NSG SWG Tools 3.1.4 round-trips `.msh`, and the Quaternius wall
   drew in the client on 15 Oct. Collision is the open gap.
3. The checks that must come before any install are done here: the driver supports CUDA 13.4, and ComfyUI's portable
   build ships PyTorch for CUDA 13.0. The 12 GB fit for 3D is still unknown.
4. Keep fal optional. TRELLIS.2 on fal ($0.25-0.35 a model on 13 Oct) is worth paying for only if local 3D fails
   to fit.
5. First step: pick 1, then one kajidic seal to banner as the first generated asset in the client.

## Sources (read 17 Oct 2026)

- ComfyUI: [repository and portable build](https://github.com/Comfy-Org/ComfyUI) (GPL-3.0, cu130, "20 series and above"); release v0.41.0 assets via the GitHub API; [FLUX.2 klein guide](https://docs.comfy.org/tutorials/flux/flux-2-klein); [TRELLIS.2 workflow](https://docs.comfy.org/tutorials/3d/trellis2); [native TRELLIS.2 and Pixal3D](https://blog.comfy.org/p/trellis2-and-pixal3d-are-now-native) (31 Aug 2026); [Hunyuan3D-2 guide](https://docs.comfy.org/tutorials/3d/hunyuan3D-2); [Z-Image Turbo guide](https://docs.comfy.org/tutorials/image/z-image/z-image-turbo).
- Models: [FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B); [microsoft/TRELLIS.2](https://github.com/microsoft/TRELLIS.2); [Hunyuan3D 2.0 licence](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE); [Stable Fast 3D](https://huggingface.co/stabilityai/stable-fast-3d); [SDXL base 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0); [Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo); [Terrain Diffusion](https://github.com/xandergos/terrain-diffusion). File sizes, licence tags and gating came from the Hugging Face API for each repo named above.
- This PC: `nvidia-smi`, Windows CIM queries, `free -m` in Debian, `.wslconfig`, `Agent/live/status.md` (7:35 AM). Client texture sizes came from the DDS headers in the client archives, read with `tools/swgfmt` (nothing extracted).

## Install record (17 Oct 2026, 7:55 to 8:05 AM)

Done with the owner's card answer, "2D art + 3D test". Every file was checked against the size and SHA-256 its host
publishes (the Hugging Face LFS object id; the digest on the GitHub release asset). All nine match. They downloaded at
about 100 MB/s, roughly 7.5 minutes in all.

| File | Placed in `C:\Users\Pengw\Tools\ComfyUI_windows_portable\ComfyUI\models\` | SHA-256 starts |
|---|---|---|
| `ComfyUI_windows_portable_nvidia.7z` (v0.41.0) | unpacked to `C:\Users\Pengw\Tools\ComfyUI_windows_portable` with Windows' own `tar` (7 minutes); the 7z stays in `Tools\downloads` | `7ff446d6904a9eec` |
| `flux-2-klein-4b-fp8.safetensors` | `diffusion_models` | `97ed34fe0567e436` |
| `qwen_3_4b.safetensors` | `text_encoders` | `6c671498573ac2f7` |
| `flux2-vae.safetensors` | `vae` | `868fe7b343cc8f3a` |
| `trellis_2_int8_convrot.safetensors` | `diffusion_models` | `d01952ad137213f6` |
| `trellis_2_shape_vae_bf16.safetensors` | `vae` | `de0cb4949a76c59e` |
| `trellis_2_texture_vae_bf16.safetensors` | `vae` | `714e5ebf094a610e` |
| `dino_v3_vit_l.safetensors` | `clip_vision` | `5cb785e458de7c46` |
| `birefnet.safetensors` | `background_removal` | `9ab37426bf4de056` |

- **Installed:** the ComfyUI folder is 25.83 GB with the models, and C: has 63.5 GB free. `comfyui_version.py` reads
  0.41.0. No custom nodes were added: `custom_nodes` holds only the two stock examples. No system install, no
  registry entry, no service.
- **First run, 17 Oct 8:23 to 8:26 AM (the owner was out of the game: "im out, run it").** This is measured on this PC.
  - **Startup.** The same command as the `--offline` script (plus `--disable-auto-launch`) answered on 127.0.0.1:8188
    after about 27 s. ComfyUI 0.41.0 reported PyTorch 2.14.0+cu130 on "cuda:0 NVIDIA GeForce RTX 5070 :
    cudaMallocAsync", NORMAL_VRAM. So Blackwell works.
  - **FLUX.2 [klein] 4B fp8, 1024x1024, 4 steps** (`tools/comfy/flux2-klein-4b-t2i.json`): the first image took
    **34.99 s**, cold, including staging the text encoder (7,671 MB, loaded as bf16) and the model (3,882 MB). The next
    three took **4.57 s, 3.67 s and 3.92 s**.
  - **Peak card memory 11,563 MiB of 12,227**, with the desktop's ~1,000 MiB included. Free Windows RAM never fell
    below 8.56 GB (it was 10.4 GB before; Opera was open). One of 52 one-second `nvidia-smi` samples failed with
    "couldn't communicate with the NVIDIA driver" at 8:24:15, during model loading. The driver answered normally before
    and after.
  - **Idle, ComfyUI keeps the models on the card** (8,622 MiB used). It must be stopped before the owner plays. Stopping
    it brought the card back to 927 MiB.
  - **The images:** four for the Vong look test (`vong-look-test.md`). The tiling prompts did **not** tile by
    themselves: edge jumps were 2-10 times the inside differences. `um sprite seamless` fixed all three, leaving some
    doubled ridge lines from the cross-blend.
- **Second and third runs (8:31 to 8:40 AM).**
  - **Run 2:** one prompt of five failed with a `MemoryError` in the worker that streams weights from disk
    (`hostbuf_file_reader_read failed`). It happened while the 8 GB text encoder was reloading, with about 9 GB of
    Windows RAM free and ComfyUI pinning up to 13 GB. The retry worked.
  - **Run 3, with `--disable-pinned-memory`:** no errors, 24.5 s cold and 2.1-3.5 s an image, with the files probably
    in Windows' cache by then.
  - **Use `--disable-pinned-memory` on this PC** until a lower-RAM text encoder is tested. The 3.85 GB fp4 file in the
    same repo was not downloaded.
- **Not run yet: TRELLIS.2.** Its template uses subgraphs and still has to be put into API form. It is the next test.
- **To remove it all:** delete `C:\Users\Pengw\Tools\ComfyUI_windows_portable` and `C:\Users\Pengw\Tools\downloads`.
  Nothing else on the PC was changed.
