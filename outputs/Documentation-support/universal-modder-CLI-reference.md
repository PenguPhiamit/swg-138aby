# Universal Modder 0.2.0: complete CLI command and option reference

Generated from the installed argparse definitions. No command actions executed.

This is the installed version, not a promise about future releases.

## um

```text
usage: um [-h]
          {scan,fal,comfy,sprite,render3d,video,win,backup,publish,kb} ...

positional arguments:
  {scan,fal,comfy,sprite,render3d,video,win,backup,publish,kb}
    scan                find installed games; fingerprint engine, anti-cheat,
                        loaders, saves, routes
    fal                 generate assets with fal (sprites, textures, 3D, rigs,
                        audio, video)
    comfy               generate images locally with ComfyUI (no API key)
    sprite              cut out, fit, pixelate, recolor and pack 2D sprites
    render3d            render a GLB into sprite frames from a game's camera
                        (Blender)
    video               compile styled showcase videos, contact sheets, trim,
                        mux
    win                 Windows/WSL: screenshots, recording with game-only
                        audio, input, processes
    backup              snapshot / diff / restore save folders before you
                        touch them
    publish             lint a mod folder before sharing (game files,
                        decompiled code, secrets)
    kb                  knowledge base of how games were modded: search,
                        write, check, PR

options:
  -h, --help            show this help message and exit
```

## um scan

```text
usage: um scan [-h] [--list] [--json] [game]

positional arguments:
  game        name (fuzzy) or install folder

options:
  -h, --help  show this help message and exit
  --list      list installed games (Steam, Epic, Xbox)
  --json
```

## um fal

```text
usage: um fal [-h] <recipe> ...

Game assets from fal (https://fal.ai): plain REST, no SDK needed. Needs FAL_KEY (env or a .env file).

    um fal sprite "a rusty scrap drone enemy, side view facing left, 16-bit pixel art" --out assets/gen --name drone
    um fal image "key art: ..." --aspect 16:9
    um fal edit "same drone, rotors blurred, second animation frame" --ref assets/gen/drone.png
    um fal rmbg in.png                       # background removal (BiRefNet v2)
    um fal pixelate in.png --colors 24       # image -> clean pixel art (grid-snapped, palette-limited)
    um fal texture "mossy cobblestone"       # seamless tiling texture
    um fal pbr "rusted sheet metal"          # basecolor/normal/roughness/metalness/height maps
    um fal model3d concept.png               # image -> textured GLB (Trellis 2; --engine hunyuan|tripo|meshy)
    um fal rig character.glb --animate       # auto-rig a humanoid (Meshy) -> rigged GLB/FBX + animations
    um fal sfx "laser rifle shot, sci-fi, punchy" --seconds 1.5
    um fal music "tense boss battle, chiptune, 140 bpm" --seconds 60
    um fal voice "You dare challenge the Mothership?" --voice-id Adam
    um fal video still.png "camera orbits the boss as it powers up"
    um fal run <endpoint> key=value key:=json image_url=@local.png   # anything else
    um fal search "image to 3d" | um fal schema fal-ai/trellis-2 | um fal price fal-ai/trellis-2

Every call appends a line to <out>/fal_manifest.jsonl (endpoint, inputs, request id, seed, files) so an
asset can be traced and regenerated. Local files passed as inputs are uploaded to fal storage first.
Model ids move fast: `um fal search` / the fal MCP's search_models find the current best.

positional arguments:
  <recipe>
    image     text -> image (Nano Banana 2)
    sprite    text -> sprite on a transparent background (GPT Image 2)
    edit      edit / make variants of reference images (consistent sets,
              animation frames)
    rmbg      remove the background (BiRefNet v2)
    pixelate  image -> grid-snapped pixel art (fal image2pixel)
    upscale   upscale an image (SeedVR2)
    texture   seamless tiling texture (Z-Image Turbo tiling)
    pbr       PBR material maps (PATINA)
    model3d   image -> textured 3D model (GLB)
    rig       auto-rig a humanoid model (Meshy), optionally with animations
    sfx       sound effect (ElevenLabs SFX v2)
    music     music track (ElevenLabs Music)
    voice     voice line / narration (ElevenLabs v3)
    video     image -> video clip (Seedance 2.5): trailers, cutscenes
    run       any endpoint: key=value / key:=json / key=@file
    search    search the fal catalog
    schema    input/output fields of an endpoint
    price     pricing of an endpoint
    result    fetch (and download) a finished request
    upload    upload a local file, print its URL

options:
  -h, --help  show this help message and exit
```

## um fal image

```text
usage: um fal image [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                    [--aspect ASPECT] [--res {0.5K,1K,2K,4K}] [--n N]
                    [--seed SEED]
                    prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --aspect ASPECT       e.g. 1:1, 16:9, 3:4, 21:9
  --res {0.5K,1K,2K,4K}
  --n N
  --seed SEED
```

## um fal sprite

```text
usage: um fal sprite [-h] [--out OUT] [--name NAME] [--model MODEL]
                     [--set K=V] [--quality {low,medium,high}] [--size SIZE]
                     [--n N]
                     prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --quality {low,medium,high}
  --size SIZE           square_hd, portrait_4_3, landscape_4_3, ...
  --n N
```

## um fal edit

```text
usage: um fal edit [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                   --ref REF [--aspect ASPECT] [--res {0.5K,1K,2K,4K}] [--n N]
                   [--seed SEED]
                   prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --ref REF             reference image (path or URL), repeatable
  --aspect ASPECT
  --res {0.5K,1K,2K,4K}
  --n N
  --seed SEED
```

## um fal rmbg

```text
usage: um fal rmbg [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                   image

positional arguments:
  image

options:
  -h, --help     show this help message and exit
  --out OUT      output folder (default assets/gen)
  --name NAME    output file stem
  --model MODEL  override the endpoint
  --set K=V      extra model input (repeatable; K:=json for numbers)
```

## um fal pixelate

```text
usage: um fal pixelate [-h] [--out OUT] [--name NAME] [--model MODEL]
                       [--set K=V] [--colors COLORS] [--scale SCALE]
                       image

positional arguments:
  image

options:
  -h, --help       show this help message and exit
  --out OUT        output folder (default assets/gen)
  --name NAME      output file stem
  --model MODEL    override the endpoint
  --set K=V        extra model input (repeatable; K:=json for numbers)
  --colors COLORS
  --scale SCALE    force the pixel scale
```

## um fal upscale

```text
usage: um fal upscale [-h] [--out OUT] [--name NAME] [--model MODEL]
                      [--set K=V] [--factor FACTOR]
                      image

positional arguments:
  image

options:
  -h, --help       show this help message and exit
  --out OUT        output folder (default assets/gen)
  --name NAME      output file stem
  --model MODEL    override the endpoint
  --set K=V        extra model input (repeatable; K:=json for numbers)
  --factor FACTOR
```

## um fal texture

```text
usage: um fal texture [-h] [--out OUT] [--name NAME] [--model MODEL]
                      [--set K=V] [--size SIZE]
                      [--tiling {both,horizontal,vertical}]
                      prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --size SIZE
  --tiling {both,horizontal,vertical}
```

## um fal pbr

```text
usage: um fal pbr [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                  [--maps MAPS] [--size SIZE]
                  prompt

positional arguments:
  prompt

options:
  -h, --help     show this help message and exit
  --out OUT      output folder (default assets/gen)
  --name NAME    output file stem
  --model MODEL  override the endpoint
  --set K=V      extra model input (repeatable; K:=json for numbers)
  --maps MAPS
  --size SIZE
```

## um fal model3d

```text
usage: um fal model3d [-h] [--out OUT] [--name NAME] [--model MODEL]
                      [--set K=V] [--engine {trellis2,hunyuan,tripo,meshy}]
                      [--texture {1024,2048,4096}] [--faces FACES]
                      image

positional arguments:
  image

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --engine {trellis2,hunyuan,tripo,meshy}
  --texture {1024,2048,4096}
  --faces FACES         target face count (game-ready: 5k-50k)
```

## um fal rig

```text
usage: um fal rig [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                  [--animate] [--height HEIGHT]
                  model_file

positional arguments:
  model_file

options:
  -h, --help       show this help message and exit
  --out OUT        output folder (default assets/gen)
  --name NAME      output file stem
  --model MODEL    override the endpoint
  --set K=V        extra model input (repeatable; K:=json for numbers)
  --animate
  --height HEIGHT  character height in meters
```

## um fal sfx

```text
usage: um fal sfx [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                  [--seconds SECONDS] [--loop]
                  prompt

positional arguments:
  prompt

options:
  -h, --help         show this help message and exit
  --out OUT          output folder (default assets/gen)
  --name NAME        output file stem
  --model MODEL      override the endpoint
  --set K=V          extra model input (repeatable; K:=json for numbers)
  --seconds SECONDS
  --loop
```

## um fal music

```text
usage: um fal music [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                    [--seconds SECONDS] [--vocals]
                    prompt

positional arguments:
  prompt

options:
  -h, --help         show this help message and exit
  --out OUT          output folder (default assets/gen)
  --name NAME        output file stem
  --model MODEL      override the endpoint
  --set K=V          extra model input (repeatable; K:=json for numbers)
  --seconds SECONDS
  --vocals
```

## um fal voice

```text
usage: um fal voice [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                    [--voice-id VOICE_ID] [--stability STABILITY]
                    text

positional arguments:
  text

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --voice-id VOICE_ID
  --stability STABILITY
```

## um fal video

```text
usage: um fal video [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                    [--seconds SECONDS] [--res {480p,720p,1080p}] [--audio]
                    image prompt

positional arguments:
  image
  prompt

options:
  -h, --help            show this help message and exit
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --model MODEL         override the endpoint
  --set K=V             extra model input (repeatable; K:=json for numbers)
  --seconds SECONDS
  --res {480p,720p,1080p}
  --audio
```

## um fal run

```text
usage: um fal run [-h] [--out OUT] [--name NAME] [--model MODEL] [--set K=V]
                  endpoint [params ...]

positional arguments:
  endpoint
  params

options:
  -h, --help     show this help message and exit
  --out OUT      output folder (default assets/gen)
  --name NAME    output file stem
  --model MODEL  override the endpoint
  --set K=V      extra model input (repeatable; K:=json for numbers)
```

## um fal search

```text
usage: um fal search [-h] [--category CATEGORY] [--limit LIMIT] query

positional arguments:
  query

options:
  -h, --help           show this help message and exit
  --category CATEGORY  text-to-image, image-to-3d, text-to-audio, ...
  --limit LIMIT
```

## um fal schema

```text
usage: um fal schema [-h] endpoint

positional arguments:
  endpoint

options:
  -h, --help  show this help message and exit
```

## um fal price

```text
usage: um fal price [-h] endpoint

positional arguments:
  endpoint

options:
  -h, --help  show this help message and exit
```

## um fal result

```text
usage: um fal result [-h] [--out OUT] [--name NAME] [--model MODEL]
                     [--set K=V]
                     endpoint request_id

positional arguments:
  endpoint
  request_id

options:
  -h, --help     show this help message and exit
  --out OUT      output folder (default assets/gen)
  --name NAME    output file stem
  --model MODEL  override the endpoint
  --set K=V      extra model input (repeatable; K:=json for numbers)
```

## um fal upload

```text
usage: um fal upload [-h] file

positional arguments:
  file

options:
  -h, --help  show this help message and exit
```

## um comfy

```text
usage: um comfy [-h] <cmd> ...

Images from a local ComfyUI server: no API key, runs on your own GPU (https://www.comfy.org).

    um comfy status                                   # is ComfyUI up? which checkpoints can it load?
    um comfy image "a rusty scrap drone enemy, side view, 16-bit pixel art" --name drone
    um comfy image "a red health potion" --sprite     # plain background, then cut out locally (um sprite cutout)
    um comfy image "mossy dungeon wall" --checkpoint sd_xl_base_1.0.safetensors --size 1024x1024 --steps 30
    um comfy run my_workflow.json --set 6.text="a blue mana potion" --set 3.seed:=42 --name potion

Start ComfyUI first. It listens on http://127.0.0.1:8188; use --url or COMFYUI_URL for another address.
`image` runs ComfyUI's default text-to-image graph (checkpoint, two prompts, KSampler, VAE decode), which
fits SD 1.5 and SDXL checkpoints. Without --checkpoint it takes the first one the server lists. For anything
else (Flux, img2img, ControlNet, LoRAs), build the graph in ComfyUI, save it with Export (API) and run it
with `um comfy run`. --set NODE.INPUT=value changes a node input first: NODE is the node id or its title,
and := takes JSON (numbers, true/false). Files land in --out (default assets/gen), and each call appends a
line to <out>/comfy_manifest.jsonl (workflow, seed, files) so an image can be traced and made again.

positional arguments:
  <cmd>
    status    is ComfyUI running, and which checkpoints can it load
    image     text -> image with ComfyUI's default graph (SD 1.5 / SDXL
              checkpoints)
    run       run a workflow saved with Export (API), with --set overrides

options:
  -h, --help  show this help message and exit
```

## um comfy status

```text
usage: um comfy status [-h] [--url URL] [--json]

options:
  -h, --help  show this help message and exit
  --url URL   ComfyUI address (default: $COMFYUI_URL or http://127.0.0.1:8188)
  --json
```

## um comfy image

```text
usage: um comfy image [-h] [--url URL] [--out OUT] [--name NAME]
                      [--timeout TIMEOUT] [--checkpoint CHECKPOINT]
                      [--negative NEGATIVE] [--size SIZE] [--steps STEPS]
                      [--cfg CFG] [--seed SEED] [--sampler SAMPLER]
                      [--scheduler SCHEDULER] [--n N] [--sprite]
                      prompt

positional arguments:
  prompt

options:
  -h, --help            show this help message and exit
  --url URL             ComfyUI address (default: $COMFYUI_URL or
                        http://127.0.0.1:8188)
  --out OUT             output folder (default assets/gen)
  --name NAME           output file stem
  --timeout TIMEOUT     seconds to wait for the result
  --checkpoint CHECKPOINT
                        checkpoint file name (default: the first one the
                        server lists)
  --negative NEGATIVE
  --size SIZE           WxH (default 1024x1024 for SDXL-looking checkpoint
                        names, else 512x512)
  --steps STEPS
  --cfg CFG
  --seed SEED           default: random (written to the manifest)
  --sampler SAMPLER
  --scheduler SCHEDULER
  --n N                 images per run (batch size)
  --sprite              a single sprite on a plain background, then cut out
                        locally
```

## um comfy run

```text
usage: um comfy run [-h] [--url URL] [--out OUT] [--name NAME]
                    [--timeout TIMEOUT] [--set NODE.INPUT=V]
                    workflow

positional arguments:
  workflow

options:
  -h, --help          show this help message and exit
  --url URL           ComfyUI address (default: $COMFYUI_URL or
                      http://127.0.0.1:8188)
  --out OUT           output folder (default assets/gen)
  --name NAME         output file stem
  --timeout TIMEOUT   seconds to wait for the result
  --set NODE.INPUT=V  change a node input (repeatable; := for JSON)
```

## um sprite

```text
usage: um sprite [-h] <cmd> ...

2D sprite tools: turn generated art into the exact frames a game expects.

    um sprite info in.png                               # size, mode, alpha coverage, bbox, colours
    um sprite cutout in.png out.png                     # flat background -> transparent (flood fill from the border)
    um sprite fit in.png out.png --size 64x26           # trim + nearest-neighbour fit into a frame (pixel art)
    um sprite fit in.png out.png --size 38x34 --anchor bottom --smooth
    um sprite pixelate in.png out.png --size 32x32 --colors 16 --outline
    um sprite palette in.png out.png --from ref.png     # snap colours to a game's palette
    um sprite sheet out.png f1.png f2.png ... --cols 4  # pack frames (grid); --vertical for a Terraria-style strip
    um sprite slice sheet.png outdir --frame 32x32      # split a sheet into frames
    um sprite frames in.png outdir --n 3 --kind bob     # quick idle animation from one frame (bob/squash/wobble/flash)
    um sprite team-mask in.png out.png --hue blue       # saturated accent -> player-colour mask (+ desaturated sprite)
    um sprite seamless in.png out.png                   # make a texture tile (offset + cross-blend)
    um sprite tile-preview in.png out.png               # 3x3 tiling preview to check seams
    um sprite preview in.png out.png --scale 4          # checkerboard + scale, for looking at it

Rules of thumb (learned the hard way): generate on a flat background or with real transparency, cut
out with a border flood fill (keeps interior whites like eyes), trim, then scale ONCE with nearest
neighbour to the engine's frame size. Keep facing directions consistent with the engine's convention
(e.g. Terraria items point right, NPC sprites face left). Frame layout comes from the engine's draw code.

positional arguments:
  <cmd>
    info          size, alpha coverage, bbox, colour count
    cutout        flat background -> transparent (border flood fill)
    fit           trim + scale into a WxH frame (nearest neighbour)
    pixelate      downscale to true pixel art with a limited palette
    palette       snap colours to a reference sprite's palette
    sheet         pack frames into a sheet
    slice         split a sheet into frames
    frames        make a small idle animation from one frame
    team-mask     player-colour mask from a saturated accent colour
    seamless      make a texture tile
    tile-preview  NxN tiled preview
    preview       checkerboard + nearest scale-up for viewing
    outline       1px outline
    hard-alpha    binary alpha
    flip          mirror horizontally (or --vertical)
    rotate        rotate by degrees (counter-clockwise), nearest

options:
  -h, --help      show this help message and exit
```

## um sprite info

```text
usage: um sprite info [-h] inputs [inputs ...]

positional arguments:
  inputs

options:
  -h, --help  show this help message and exit
```

## um sprite cutout

```text
usage: um sprite cutout [-h] [--tol TOL] [--bg BG] [--grey GREY]
                        [--spread SPREAD] [--holes] [--keep-top KEEP_TOP]
                        input output

positional arguments:
  input
  output

options:
  -h, --help           show this help message and exit
  --tol TOL            colour distance to the background (0-255 per channel)
  --bg BG              background colour hex (default: corners)
  --grey GREY          also clear light greys (soft shadows) with min channel
                       >= this
  --spread SPREAD
  --holes              also clear enclosed background-coloured areas
  --keep-top KEEP_TOP  keep this fraction from the top (drop a floor shadow)
```

## um sprite fit

```text
usage: um sprite fit [-h] --size SIZE [--anchor {center,bottom,top}]
                     [--smooth] [--no-upscale] [--hard-alpha]
                     input output

positional arguments:
  input
  output

options:
  -h, --help            show this help message and exit
  --size SIZE
  --anchor {center,bottom,top}
  --smooth              Lanczos instead of nearest (painted/HD art)
  --no-upscale
  --hard-alpha
```

## um sprite pixelate

```text
usage: um sprite pixelate [-h] --size SIZE [--colors COLORS] [--outline]
                          [--outline-color OUTLINE_COLOR]
                          input output

positional arguments:
  input
  output

options:
  -h, --help            show this help message and exit
  --size SIZE
  --colors COLORS       0 = keep all colours
  --outline
  --outline-color OUTLINE_COLOR
```

## um sprite palette

```text
usage: um sprite palette [-h] --from FROM [--max-colors MAX_COLORS]
                         input output

positional arguments:
  input
  output

options:
  -h, --help            show this help message and exit
  --from FROM
  --max-colors MAX_COLORS
```

## um sprite sheet

```text
usage: um sprite sheet [-h] [--cols COLS] [--pad PAD] [--vertical]
                       output frames [frames ...]

positional arguments:
  output
  frames

options:
  -h, --help   show this help message and exit
  --cols COLS
  --pad PAD
  --vertical   one column (Terraria NPC/projectile strips)
```

## um sprite slice

```text
usage: um sprite slice [-h] --frame FRAME [--pad PAD] input outdir

positional arguments:
  input
  outdir

options:
  -h, --help     show this help message and exit
  --frame FRAME  WxH
  --pad PAD
```

## um sprite frames

```text
usage: um sprite frames [-h] [--n N] [--kind {bob,squash,wobble,flash}]
                        input outdir

positional arguments:
  input
  outdir

options:
  -h, --help            show this help message and exit
  --n N
  --kind {bob,squash,wobble,flash}
```

## um sprite team-mask

```text
usage: um sprite team-mask [-h] [--hue {blue,red,green,magenta}] input output

positional arguments:
  input
  output

options:
  -h, --help            show this help message and exit
  --hue {blue,red,green,magenta}
```

## um sprite seamless

```text
usage: um sprite seamless [-h] [--blend BLEND] input output

positional arguments:
  input
  output

options:
  -h, --help     show this help message and exit
  --blend BLEND
```

## um sprite tile-preview

```text
usage: um sprite tile-preview [-h] [--n N] input output

positional arguments:
  input
  output

options:
  -h, --help  show this help message and exit
  --n N
```

## um sprite preview

```text
usage: um sprite preview [-h] [--scale SCALE] input output

positional arguments:
  input
  output

options:
  -h, --help     show this help message and exit
  --scale SCALE
```

## um sprite outline

```text
usage: um sprite outline [-h] [--color COLOR] input output

positional arguments:
  input
  output

options:
  -h, --help     show this help message and exit
  --color COLOR
```

## um sprite hard-alpha

```text
usage: um sprite hard-alpha [-h] [--thresh THRESH] input output

positional arguments:
  input
  output

options:
  -h, --help       show this help message and exit
  --thresh THRESH
```

## um sprite flip

```text
usage: um sprite flip [-h] [--vertical] input output

positional arguments:
  input
  output

options:
  -h, --help  show this help message and exit
  --vertical
```

## um sprite rotate

```text
usage: um sprite rotate [-h] input output degrees

positional arguments:
  input
  output
  degrees

options:
  -h, --help  show this help message and exit
```

## um render3d

```text
usage: um render3d [-h] [--preset {aoe2,iso8,trueiso,topdown,side,turntable}]
                   [--canvas CANVAS] [--length LENGTH]
                   [--measure {length,height}] [--forward-yaw FORWARD_YAW]
                   [--anims ANIMS] [--shadows] [--samples SAMPLES]
                   [--engine {cycles,eevee}] [--elevation ELEVATION]
                   [--headings HEADINGS] [--sun SUN] [--ambient AMBIENT]
                   [--ground-y GROUND_Y]
                   glb out

Render a 3D model (GLB) into sprite frames from a game's camera, with Blender.

    um render3d model.glb out/ --preset aoe2 --length 80 --anims idle:10:bob,walk:12:bob,attack:16:lunge,death:20:die --shadows
    um render3d model.glb out/ --preset side --canvas 128 --length 110            # platformer: facing right + left
    um render3d model.glb out/ --preset iso8 --canvas 256x256 --length 150 --engine eevee

This is how the AoE2 San Franciscans units were made: fal concept art -> `um fal model3d` (image-to-3D)
-> these renders -> the engine's sprite format. Rendering from 3D keeps every facing and frame consistent,
which per-frame image generation can't. Presets (camera elevation, headings, direction order):
  aoe2      ortho 30 deg, 16 headings clockwise from east (AoE2 DE / Genie unit order)
  iso8      ortho 30 deg (2:1 diamond tiles), 8 headings clockwise from east
  trueiso   ortho 35.264 deg, 8 headings
  topdown   ortho 90 deg, 8 headings (twin-stick / top-down shooters)
  side      ortho 0 deg, 2 headings: facing right, facing left (platformers, Terraria-style)
  turntable persp 20 deg, 24 headings (icons, previews, promo spins)
Needs Blender on PATH (or BLENDER=/path/to/blender). Frames: <out>/<anim>_<heading>_<frame>.png (+ _s shadow pass).
Pack them with `um sprite sheet`, or with an engine-specific writer (examples/aoe2-de-civ/sld.py).

positional arguments:
  glb
  out

options:
  -h, --help            show this help message and exit
  --preset {aoe2,iso8,trueiso,topdown,side,turntable}
  --canvas CANVAS       frame size px: N or WxH
  --length LENGTH       model's longest horizontal side (or height with
                        --measure height) in px
  --measure {length,height}
  --forward-yaw FORWARD_YAW
                        degrees to turn the model so its front faces +X (east)
  --anims ANIMS         name:frames:motion,... motions:
                        bob,walk,lunge,die,wreck,spin,still
  --shadows             also render a shadow-only pass (_s.png)
  --samples SAMPLES
  --engine {cycles,eevee}
  --elevation ELEVATION
                        override camera elevation (deg)
  --headings HEADINGS   override number of facings
  --sun SUN
  --ambient AMBIENT
  --ground-y GROUND_Y   px from the top where the ground point lands (default:
                        canvas centre)
```

## um video

```text
usage: um video [-h] <cmd> ...

Showcase videos: pick moments, cut, title, transition, score, export. ffmpeg + Pillow only.

    um video probe clip.mp4                              # duration, size, fps, audio
    um video contact clip.mp4 sheet.png --every 2        # timestamped grid of frames: look, then choose in/out points
    um video first-frame take.mkv                        # first real gameplay frame (skips dark/flat loading screens)
    um video beats music.mp3                             # tempo + first beat, to cut on the beat
    um video mux take.mkv take.mkv.audio.raw take.mkv.json out.mp4   # recorder output -> mp4 (see `um win record`)
    um video compile edl.json out.mp4 [--preview]        # the edit, described as JSON (below)

EDL (edit decision list) - every key but "segments" is optional:
  {"size": [1920, 1080], "fps": 30, "bpm": 128,
   "theme": {"accent": "#B6FF3B", "text": "#FFFFFF", "chip": "#0A0D12E0"},   # + "title_font"/"body_font"/"mono_font": .ttf paths
   "transition": {"type": "fade", "duration": 0.3},        # any ffmpeg xfade type, or "cut"
   "clip_volume": 0.6, "music": {"path": "track.mp3", "volume": 0.8, "start": 0, "fade_in": 0.2},
   "watermark": {"path": "logo.png", "height": 54, "corner": "br", "opacity": 0.9},
   "counter": false, "fade_out": 0.8, "beat_lock": true, "normalize_audio": true,
   "sfx": [{"path": "whoosh.mp3", "at": 12.5, "volume": 0.8}],
   "segments": [
     {"card": {"title": "Every game is moddable now.", "sub": "", "bg": "#05070A", "logo": "logo.png"}, "dur": 2.2},
     {"clip": "a.mp4", "in": 12.0, "dur": 4.0, "title": "Minecraft inside Elden Ring", "credit": "@TobynJacobs",
      "fill": "blur", "volume": 0.6, "speed": 1.0, "zoom": 1.0, "crop": [0, 0, 1920, 1080], "transition": {"type": "pixelize"}},
     {"clip": "b.mp4", "in": 0, "beats": 8, "hook": "Point Claude at any game."}]}
  "dur" is seconds, or give "beats" with a top-level "bpm" (+ "beat_lock" so cuts land on the grid despite transitions).
  "fill": blur | crop | pad for clips that aren't 16:9. "watermark": false on a segment hides the logo there.
  Titles are one line, bottom-left, sliding in after the transition; "credit" sits on the same line.
  Space Grotesk has Latin glyphs only: for Cyrillic, Greek or CJK titles set the theme's *_font to a font that has them.

Style that works on X: open on the strongest moment (<= 2-3 s before real gameplay), one-line titles,
3-5 s per clip, credit every creator whose footage you use, end on the name/URL, fade out.

positional arguments:
  <cmd>
    probe        duration / size / fps / audio
    contact      timestamped frame grid for choosing moments
    first-frame  seconds until the first gameplay frame
    beats        tempo and first beat of a music file
    mux          recorder .mkv + .audio.raw + .json -> mp4
    compile      render an EDL json into a finished video

options:
  -h, --help     show this help message and exit
```

## um video probe

```text
usage: um video probe [-h] input

positional arguments:
  input

options:
  -h, --help  show this help message and exit
```

## um video contact

```text
usage: um video contact [-h] [--every EVERY] [--cols COLS] [--width WIDTH]
                        [--start START] [--end END]
                        input output

positional arguments:
  input
  output

options:
  -h, --help     show this help message and exit
  --every EVERY
  --cols COLS
  --width WIDTH
  --start START
  --end END
```

## um video first-frame

```text
usage: um video first-frame [-h] input

positional arguments:
  input

options:
  -h, --help  show this help message and exit
```

## um video beats

```text
usage: um video beats [-h] input

positional arguments:
  input

options:
  -h, --help  show this help message and exit
```

## um video mux

```text
usage: um video mux [-h] [--offset OFFSET] video audio meta output

positional arguments:
  video
  audio
  meta
  output

options:
  -h, --help       show this help message and exit
  --offset OFFSET  audio offset override (s)
```

## um video compile

```text
usage: um video compile [-h] [--preview] [--keep] edl output

positional arguments:
  edl
  output

options:
  -h, --help  show this help message and exit
  --preview   half resolution, fast encode
  --keep      keep the work folder
```

## um win

```text
usage: um win [-h] <cmd> ...

Windows games from an agent (native Windows, or WSL where most coding agents live).

    um win setup                                  # copy the PowerShell tools + fetch an ffmpeg with gfxcapture (SHA-256 checked)
    um win ps [name]                              # processes with windows: pid, name, title
    um win kill <pid>                             # by exact PID only (never by pattern)
    um win launch --steam 105600 [-- args]        # or: um win launch "C:\Games\Foo\foo.exe" -- -windowed
    um win shot --exe AoE2DE_s.exe out.png [--scale 0.33]    # one frame of the game window (GPU-safe capture)
    um win drive --proc AoE2DE_s "focus" "click 640 360" "key 0x1B"   # input (WinDrive protocol, see um/ps1)
    um win record --exe Game.exe --out C:\caps\take1 --seconds 30  # video (gfxcapture) + game-only audio
    um video mux C:\caps\take1.mkv C:\caps\take1.audio.raw C:\caps\take1.json out.mp4
    um win reg get "HKCU\Software\Foo" [value] | um win reg set KEY VALUE DATA [--type REG_DWORD]

Why these tools: games render with the GPU, so GDI screen grabs are black - Windows.Graphics.Capture
(ffmpeg's gfxcapture) gets the real frames of one window even when covered. Many games talk to WASAPI
directly, so the only clean way to get just the game's sound is a process-loopback capture. Input goes
through SendInput only while the game is the foreground window, so nothing leaks into other apps.
Lessons: never block the game's main thread when stopping a recording; write .mkv (survives a kill);
NVENC H.264 tops out at 4096 px wide (ultrawide: crop or use HEVC); a crashed game's crash reporter
(BugSplat etc.) can make Steam refuse to relaunch - list and kill it by PID.

positional arguments:
  <cmd>
    setup     install the PowerShell tools and a gfxcapture-capable ffmpeg
    ps        processes that have a window
    kill      kill by exact PID
    launch    start a game (exe path or --steam APPID)
    shot      screenshot of a game window
    record    record a game window + its audio
    drive     send WinDrive commands to a game window
    reg       read / set registry values (set backs the key up first)

options:
  -h, --help  show this help message and exit
```

## um win setup

```text
usage: um win setup [-h] [--force]

options:
  -h, --help  show this help message and exit
  --force     re-download ffmpeg
```

## um win ps

```text
usage: um win ps [-h] [name]

positional arguments:
  name

options:
  -h, --help  show this help message and exit
```

## um win kill

```text
usage: um win kill [-h] pid

positional arguments:
  pid

options:
  -h, --help  show this help message and exit
```

## um win launch

```text
usage: um win launch [-h] [--steam] target [args ...]

positional arguments:
  target
  args

options:
  -h, --help  show this help message and exit
  --steam
```

## um win shot

```text
usage: um win shot [-h] [--scale SCALE] [--exe EXE] [--hwnd HWND]
                   [--title TITLE]
                   output

positional arguments:
  output

options:
  -h, --help     show this help message and exit
  --scale SCALE  also write a scaled copy (e.g. 0.33) that is cheap to look at
  --exe EXE      window's executable name, e.g. AoE2DE_s.exe (regex)
  --hwnd HWND
  --title TITLE  window title regex
```

## um win record

```text
usage: um win record [-h] --out OUT [--seconds SECONDS] [--fps FPS]
                     [--no-audio] [--crop CROP] [--pid PID] [--exe EXE]
                     [--hwnd HWND] [--title TITLE]

options:
  -h, --help         show this help message and exit
  --out OUT          base path (Windows or WSL path); writes
                     .mkv/.audio.raw/.json
  --seconds SECONDS
  --fps FPS
  --no-audio
  --crop CROP        left:top:right:bottom px to cut (e.g. ultrawide -> centre
                     16:9)
  --pid PID          process to capture audio from, when --exe is ambiguous
                     (e.g. two java.exe)
  --exe EXE          window's executable name, e.g. AoE2DE_s.exe (regex)
  --hwnd HWND
  --title TITLE      window title regex
```

## um win drive

```text
usage: um win drive [-h] --proc PROC [--no-retry] commands [commands ...]

positional arguments:
  commands

options:
  -h, --help   show this help message and exit
  --proc PROC  process name without .exe
  --no-retry
```

## um win reg

```text
usage: um win reg [-h] [--type TYPE] {get,set} key [value] [data]

positional arguments:
  {get,set}
  key
  value
  data

options:
  -h, --help   show this help message and exit
  --type TYPE
```

## um backup

```text
usage: um backup [-h] <cmd> ...

Snapshot folders before touching them (saves, profiles, config, the game's data folder).

    um backup create "C:\Users\me\Documents\My Games\Terraria" --name terraria-saves
    um backup list [name]
    um backup diff terraria-saves "C:\Users\me\Documents\My Games\Terraria"     # what changed since the last snapshot
    um backup restore terraria-saves [--to DIR] [--snapshot FILE] [--yes]

Snapshots are zip files + a manifest (size + sha1 per file) in ~/.universal-modder/backups/<name>/.
Snapshots created in the same second get numbered suffixes so earlier backups are never overwritten.
restore first snapshots the current state (so a restore can itself be undone), then puts every file
back and removes files that weren't in the snapshot only with --clean.
Habit that saved the Terraria showcase: keep a pristine copy of any world/scenario a scripted take
destroys, and restore it before each take.

positional arguments:
  <cmd>
    create    snapshot a folder
    list      list snapshots
    diff      what changed since the latest snapshot
    restore   restore the latest (or --snapshot) snapshot

options:
  -h, --help  show this help message and exit
```

## um backup create

```text
usage: um backup create [-h] [--name NAME] [--note NOTE] src

positional arguments:
  src

options:
  -h, --help   show this help message and exit
  --name NAME
  --note NOTE
```

## um backup list

```text
usage: um backup list [-h] [name]

positional arguments:
  name

options:
  -h, --help  show this help message and exit
```

## um backup diff

```text
usage: um backup diff [-h] [--snapshot SNAPSHOT] name [target]

positional arguments:
  name
  target

options:
  -h, --help           show this help message and exit
  --snapshot SNAPSHOT
```

## um backup restore

```text
usage: um backup restore [-h] [--to TO] [--snapshot SNAPSHOT] [--clean]
                         [--yes]
                         name

positional arguments:
  name

options:
  -h, --help           show this help message and exit
  --to TO
  --snapshot SNAPSHOT
  --clean              also delete files created after the snapshot
  --yes
```

## um publish

```text
usage: um publish [-h] <cmd> ...

Check a mod folder before you share it: no game files, no decompiled code, no secrets, credits present.

    um publish check ./MyMod --game "C:\Program Files (x86)\Steam\steamapps\common\Terraria"

FAIL  files byte-identical to files in the game install (redistributing game files), leaked API keys
      (FAL_KEY, Anthropic, GitHub, AWS...), .env files
WARN  decompiler fingerprints in source (FUN_xxxx / DAT_xxxx / sub_XXXX, "// Decompiled with", ILSpy/dnSpy
      headers) - reimplement or reference instead of shipping decompiled code; big engine archives
      (.pak/.bsa/.ba2/.vpk/.rpf/.utoc...) that may carry original assets; absolute user paths; no README /
      credits; fal-generated assets listed in fal_manifest.jsonl without an attribution line
Modelled on IW4L's publish-check. It is a lint, not legal advice: when in doubt ship a patch/converter that
runs on the user's own install ("bring your own game files") instead of the files themselves.

positional arguments:
  <cmd>
    check     check a mod folder

options:
  -h, --help  show this help message and exit
```

## um publish check

```text
usage: um publish check [-h] [--game GAME] mod

positional arguments:
  mod

options:
  -h, --help   show this help message and exit
  --game GAME  game install folder, to catch copied game files
```

## um kb

```text
usage: um kb [-h] <cmd> ...

The knowledge base: field notes on how games were actually modded, written by agents for agents.

    um kb search "unreal pak mod"               # prior art before you start (local repo, or synced from GitHub)
    um kb search terraria --route loader-api    # filter by game / engine / route
    um kb show games/terraria/fal-arsenal.md
    um kb new --game "Hades II" --title "A new boon god" --from-scan "hades"   # scaffold a note, pre-filled
    um kb check knowledge/games/hades-ii/new-boon-god.md                       # validate before a PR
    um kb index                                  # regenerate knowledge/INDEX.md + index.json
    um kb sync                                   # refresh the cached copy from GitHub
    um kb pr knowledge/games/hades-ii/new-boon-god.md --yes                     # branch, commit, push to your fork, open a PR

Every note is Markdown with YAML front matter (knowledge/TEMPLATE.md). `check` enforces the schema, the
required sections, no secrets, no pasted decompiled code, no huge files. Contributions go through pull
requests: that's how one agent's hard-won gotchas reach the next one. Ask your human before `um kb pr --yes`.

positional arguments:
  <cmd>
    search    find prior notes (local clone, else the GitHub copy)
    show      print a note
    new       scaffold a note from the template
    check     validate notes (all, or the given paths)
    index     regenerate knowledge/INDEX.md and index.json
    sync      refresh the cached GitHub copy
    pr        open a pull request with a note (dry run unless --yes)

options:
  -h, --help  show this help message and exit
```

## um kb search

```text
usage: um kb search [-h] [--game GAME] [--engine ENGINE]
                    [--route {data,asset-only,loader-api,managed-patch,native-hook,reimplementation,decomp-recomp,passthrough,emulator,other}]
                    [--limit LIMIT] [--json] [--remote] [--root ROOT]
                    [terms ...]

positional arguments:
  terms

options:
  -h, --help            show this help message and exit
  --game GAME
  --engine ENGINE
  --route {data,asset-only,loader-api,managed-patch,native-hook,reimplementation,decomp-recomp,passthrough,emulator,other}
  --limit LIMIT
  --json
  --remote              search the synced GitHub copy even inside a clone
  --root ROOT
```

## um kb show

```text
usage: um kb show [-h] [--remote] [--root ROOT] note

positional arguments:
  note

options:
  -h, --help   show this help message and exit
  --remote
  --root ROOT
```

## um kb new

```text
usage: um kb new [-h] --title TITLE [--game GAME] [--kind {game,technique}]
                 [--from-scan FROM_SCAN] [--engine ENGINE]
                 [--route {data,asset-only,loader-api,managed-patch,native-hook,reimplementation,decomp-recomp,passthrough,emulator,other}]
                 [--agent AGENT] [--out OUT] [--root ROOT]

options:
  -h, --help            show this help message and exit
  --title TITLE
  --game GAME
  --kind {game,technique}
  --from-scan FROM_SCAN
                        pre-fill engine / anti-cheat / loaders from `um scan
                        <game>`
  --engine ENGINE
  --route {data,asset-only,loader-api,managed-patch,native-hook,reimplementation,decomp-recomp,passthrough,emulator,other}
  --agent AGENT         e.g. "Codex (gpt-6)"; default $UM_AGENT
  --out OUT
  --root ROOT
```

## um kb check

```text
usage: um kb check [-h] [--index] [--root ROOT] [paths ...]

positional arguments:
  paths

options:
  -h, --help   show this help message and exit
  --index      also fail if INDEX.md is stale
  --root ROOT
```

## um kb index

```text
usage: um kb index [-h] [--root ROOT]

options:
  -h, --help   show this help message and exit
  --root ROOT
```

## um kb sync

```text
usage: um kb sync [-h]

options:
  -h, --help  show this help message and exit
```

## um kb pr

```text
usage: um kb pr [-h] [--yes] note

positional arguments:
  note

options:
  -h, --help  show this help message and exit
  --yes       really branch, push and open the PR
```
