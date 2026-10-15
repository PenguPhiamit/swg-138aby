# Client graphics: ReShade, and DLSS 5 through the Feeder (owner's own PC)

14 Oct 2026, Claude. For the owner's client in `SWG-client/` (`SWGEmu.exe`, SOE SwgClient_r 0.0.119.798, **32-bit,
Direct3D 9**, GPU RTX 5070). Client-side only: nothing here touches the server, the game archives or the bots, and none
of these files are ours to redistribute. The owner downloads and installs everything; agents do not. Both launchers
(live and test) use this folder, so the overlay applies to both.

Sources: SWG Restoration's ReShade page (https://swgr.org/wiki/reshade/), the DLSS5-Feeder README
(https://github.com/jlrouzies-fr/DLSS5-Feeder, MIT for its own code), Igor'sLAB's DLSS 5 guide. The neural DLL
(`nvngx_dlssnr.dll`, a modified NVIDIA build from the RenoDX Discord) is the owner's own download and choice.

## Before you start

- None of the files below exist in `SWG-client/` today (checked 14 Oct), so nothing gets overwritten. **Undo = delete
  what you added:** `D3D9.dll`, `dgVoodoo.conf`, `dgVoodooCpl.exe`, `dxgi.dll`, `ReShade.ini`, `ReShade.log`,
  `dlss5-feed.addon32`, `dlss5-feed.log`, the `reshade-shaders\` and `host64\` folders.
- In SWG's options turn **anti-aliasing (MSAA) off**, and play **windowed or borderless** (the DLSS panel needs it).

## Path A: ReShade only (the look, no AI)

1. ReShade **with full add-on support** from https://reshade.me (the default build blocks depth in online games).
2. Installer: pick `SWGEmu.exe`, API **DirectX 9**, tick all effect packages; add-on **REST** if offered.
3. In the overlay: Edit global preprocessor definitions, `RESHADE_DEPTH_INPUT_IS_REVERSED = 0` (32-bit client).
   Add-ons tab: "copy depth buffer before clear operations". Keep a 3D item on your toolbar (SWG's UI breaks depth).
4. In game: Options, Graphics, **Post Process Effects = True**.
5. Presets are `.ini` files in `SWG-client/`; the Restoration guide suggests starting with "lightroom".

## Path B: DLSS 5 through the Feeder (beta for 32-bit games)

SWG has no DLSS of its own, so the Feeder makes the DLSS calls itself from ReShade's depth and estimated motion.
On a 32-bit game the AI runs in a 64-bit helper process (`host64\`). Expect beta behaviour: some smearing in motion,
UI processed with the scene. Do Path B instead of Path A (it replaces the DirectX 9 ReShade with the D3D11 one).

1. **dgVoodoo2** (http://dege.freeweb.hu/dgVoodoo2/): copy `MS\x86\D3D9.dll`, `dgVoodoo.conf`, `dgVoodooCpl.exe` next to
   `SWGEmu.exe`. In `dgVoodoo.conf` (or dgVoodooCpl): `[General] OutputAPI = d3d11_fl11_0`; `[DirectX]
   DisableAndPassThru = false`, `VRAM = 1GB`, `VideoCard = internal3D`, `dgVoodooWatermark = true` (launch once, see the
   watermark, then set it back to false).
2. **ReShade 6.8+ with add-on support**: pick `SWGEmu.exe`, API **Direct3D 10/11/12** (it installs as `dxgi.dll`, never
   `d3d9.dll`, which is dgVoodoo's), tick "Enable loading of add-ons".
3. **The Feeder, 32-bit side** (next to `SWGEmu.exe`): `dlss5-feed.addon32`; `reshade-shaders\Shaders\DLSS5_Feed.fx`.
4. **Motion vectors, LumeniteFX**: its `Shaders\` (the `lumenite_*.fx` files and `include\`) into
   `reshade-shaders\Shaders\`, `Textures\lumenite_bluenoise256.png` into `reshade-shaders\Textures\`. In the overlay,
   `DLSS5_Feed.fx` preprocessor: `DLSS5_MV_PROVIDER = 3`, then reload.
5. **The 64-bit side**, folder `host64\` next to `SWGEmu.exe`: `dlss5-feed-host64.exe`, a **64-bit** ReShade `dxgi.dll`,
   one neural consumer (the Feeder recommends Deep Fried Chicken 1.4.8+: `deep-fried-chicken.addon64`,
   `deep-fried-chicken-nvngx.dll`, `deep-fried-chicken.cfg`), plus `nvngx_dlssnr.dll` (your download) and
   `nvngx_dlss.dll`. No `dlss5-feed.addon64` in `host64\`.
6. **Check before launching**: with the game closed, run `host64\dlss5-feed-host64.exe --test`; it must say
   `300/300 evaluates succeeded`.
7. **Technique order** in the overlay (top first), and the Generic Depth add-on set to the scene depth:
   `SpeciesColorLock_Save`, `LUMENITE: Kernel 2.0`, `DLSS 5 Feed`, `SpeciesColorLock_Apply`, then any other effects.
   Copy `SpeciesColorLock.fx` from this folder into `reshade-shaders\Shaders\`.
8. **Neural settings**: open them with "Show the DLSS 5 panel in-game" on the DLSS 5 Feed page. Start with Chicken's
   shipped cfg (on, one pass, extras off). Guides suggest NR intensity 20-35 %, Local Structure 10-25 %, **Local Tone
   low**, **Color Influence low**.

## The species colour fix

DLSS 5 can pull skin toward human tones. Two steps, in this order:
1. Lower **Local Tone** (and Color Influence where the consumer has it). That removes most of the drift.
2. `SpeciesColorLock.fx` (ours): keeps DLSS's brightness and detail, puts the game's own hue and saturation back.
   *Colour lock strength* 0.85 to start; *Only strongly coloured areas* on (grey areas keep DLSS's lighting); *Match the
   Feeder's one-frame delay* on while the Feeder's `async_home = 1` (its default). *Show the lock mask* shows what it
   protects. It fixes colour only: if faces change shape, lower NR intensity and Local Structure.

Test scene: a Chiss (blue) next to a human under the same light, close to the camera, still and then walking.

## If something goes wrong

- No dgVoodoo watermark: `DisableAndPassThru` is still true. "Ran out of video memory": raise `VRAM`.
- ReShade does nothing and there's no `dlss5-feed.log`: 32/64-bit mix-up (the 32-bit `dxgi.dll` goes next to
  `SWGEmu.exe`, the 64-bit one in `host64\`).
- "unknown technique" for DLSS5_Feed: the shader is missing, or ReShade was installed as DirectX 9.
- Sharp but smeary in motion: no motion vectors (`MV probe ... 0% non-zero` in `dlss5-feed.log`).
- "The host64\ folder is from a different release": take both halves of the Feeder from the same release.
