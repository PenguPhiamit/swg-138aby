# Ossus O15: a real mirage for the ghostfire blade (Claude, 18 Oct 2026)

Owner, 18 Oct: "a mirage effect for the blade to help hide light", then "how do we make it possible?" (the client has no heat-distortion pass).

**Built and tested outside the game on this PC, not installed.** It is a small `d3d9.dll` of our own that sits in front of DXVK in the client folder. When a ghostfire blade draws, the scene behind it bends like heat haze, with a slight opal colour split. Then the blade draws on top as usual. Everything else in the game passes through unchanged. It is for Miniverse only until it has been tried in game.

Preview, from left to right: mirage off; on; on 8 frames later; on with the O14 blade; the debug view. It is in `work/o15-mirage/preview-mirage.png`. The numbers are in `checks-mirage.json`.

## Why this route

| | Our proxy `d3d9.dll` (chosen) | ReShade add-on |
|---|---|---|
| Sees the blade? | Yes. It sees the game's own Direct3D 9 calls: the blade pixel program and the crystal colour. | Not with DXVK. ReShade's d3d9 build wants to be `d3d9.dll` itself and loads Windows' d3d9, not DXVK. Its Vulkan mode only sees DXVK's translated shaders, without the blade program or the crystal colour. |
| Download | None (about 150 KB, built here with VS 2022) | ReShade with full add-on support (needs your OK), plus our add-on |
| Friends later | One more DLL and an ini in the client folder | ReShade's installer on every PC |

## How it works

1. **The hook.** The client's graphics plugin (`gl07_r.dll`) imports only `Direct3DCreate9` from `d3d9.dll`. Our DLL takes that name, loads DXVK from `dxvk_d3d9.dll` beside it, and patches 9 slots of the device's method table: Reset, Present, the four draw calls, and pixel-program create/set/constants.
2. **Finding the ghostfire blade.** A draw counts when both of these hold:
   - the bound pixel program is a lightsaber blade program. They are recognised by an id (FNV-1a over the bytecode without its comment block): the stock one, `0xacc853c5`, in effect now on the installed `c8a61080`, and the O14 one, `0x7b68e0f1`, built but not installed;
   - the crystal colour in register c3 has every channel at 0.17 or less. That is the O14 shader's own rule: palette 32-40 is ghostfire, and every stock crystal is 0.65 or brighter.
   So it works with today's archive and with O14, and normal crystals never trigger it.
3. **Three passes before that blade draw.** ps_2_0 has no screen position, so the screen position comes from rasterising:
   1. **Mask.** The same draw is replayed into a screen-sized mask target, with the game's vertices, viewport and depth test. Our pixel program turns the blade's glow and core into a mask value and multiplies it by the game's fade. Because the depth test is the game's, a blade behind a wall makes no haze.
   2. **Copy.** The scene drawn so far is copied with StretchRect.
   3. **Bend.** One screen quad whose texture coordinates are screen positions. It widens and softens the mask, and bends the copy by two scrolling noise layers (one rising like heat). It splits red and blue a little for an opal fringe. Pixels outside the mask are discarded, and only colour is written: alpha may carry the game's bloom.
4. **Back to the game.** A state block puts every state back, and the blade draws on top as usual. Only what was drawn before the blade bends. The UI, name tags and later particles do not.

## Tested (outside the game, 18 Oct)

`mirage_test.exe` draws the way the client does on this PC (RTX 5070, DXVK 3.1.1). It uses the real stock and O14 blade programs and a Reset at frame 20. Every Direct3D call succeeded in every run.

| Check | Result |
|---|---|
| Ghostfire half, mirage on vs off | about 7,000 pixels changed, by up to 142 of 255 |
| Red-crystal blade half, on vs off | 0 pixels changed |
| Bend set to 0, vs off, whole frame | 0 pixels changed: the game's state comes back exactly, and the blade draws as before |
| Frame 40 vs 48, mirage on | the haze moves (about 12,000 pixels) |
| Reset (window or resolution change) | succeeds: our targets are released first and made again |
| install.ps1 twice, then uninstall.ps1, on a scratch copy of the client's DXVK DLL | renames DXVK and back, places and removes the proxy |

**Without DXVK (Windows' own Direct3D 9) the haze draws nothing.** Every call succeeds, but the screen quad leaves no pixel, even in the debug view with nothing discarded. I could not trace it without Microsoft's debug runtime. So when `dxvk_d3d9.dll` is missing, the proxy passes everything through and logs that; `allow_native=1` would try anyway. The client ships with DXVK, so this only matters if someone removes it.

## Risks

- **Crashes.** A failing step is logged once and the game's own draw still happens. An exception in our code switches the mirage off for the session. A crash inside DXVK or the driver can't be caught, so the first in-game run is the real test.
- **Untested in game.** Several things are still unknown:
  - which draw call the client uses for blades;
  - whether "Post Process Effects" (bloom) draws the blade into another target (the mirage then bends that target, which should be fine);
  - SWG's anti-aliasing (MSAA). There is a multisampled path, but the harness ran without MSAA.
  - whether the O13 Ghostfire Lightsaber, whose shader has no palette part, still sets a dark c3. If it doesn't, only crystal-coloured blades get the mirage.
- **DXVK chaining.** The method table is the fixed Direct3D 9 interface, so new DXVK versions keep working. But an updated DXVK `d3d9.dll` must be renamed to `dxvk_d3d9.dll` again. ReShade's d3d9 build (Client-graphics Path A) also wants to be `d3d9.dll`, and dgVoodoo (Path B) replaces DXVK. With either one in place, this proxy can't sit in front.
- **Friends' GPUs.** Cost comes only while a ghostfire blade is on screen. Each one adds a screen copy and two full-screen passes, about ten texture reads a pixel. That is nothing on a 5070, and well under a millisecond on most cards from the last ten years. `max_per_frame=8` caps a crowd of ghostfire wielders. With no ghostfire blade in view, the cost is a few comparisons per draw.
- **Only players with the DLL see it.** It changes nothing on the server. Without it, a player sees the O14 blade as it is.
- **Launchers.** Both launchers start the same `SWG-client` folder. I haven't checked whether their file check minds an extra `dxvk_d3d9.dll` or a changed `d3d9.dll`. DXVK's `d3d9.dll` was already an addition, so probably not; watch the first launch. To ship it to friends later, the installer would carry `d3d9.dll`, `dxvk_d3d9.dll` and `mirage.ini` together. Not before it has been tried here.
- **Two clients at once** (`allowMultipleInstances`). Each loads its own copy. They share `mirage.log`, and each block starts with the process id.

## Switching it off

1. **In game:** Ctrl+Shift+M switches the mirage off and on at once (only while the game window is in front).
2. **Next start:** `enabled=0` in `SWG-client/mirage.ini`. The proxy then only passes DXVK through.
3. **Remove it:** `uninstall.ps1` with the game closed. By hand: delete `d3d9.dll`, then rename `dxvk_d3d9.dll` back to `d3d9.dll`.

## To try it (owner, game closed)

1. Run `powershell -ExecutionPolicy Bypass -File outputs\Fable-ossus\o15-mirage\install.ps1`. It refuses while an SWGEmu process runs. It renames DXVK, copies the proxy from `work\o15-mirage\d3d9.dll`, and adds `mirage.ini`.
2. Start the game as usual. Put the ghostfire crystal in a saber and light it, at night and in daylight, in front of something with edges (a building or rocks).
3. Answer in your own words:
   - What do you see around the blade, and does it hide the light enough?
   - Is the haze too strong, too weak, too fine or too coarse?
   - Does Ctrl+Shift+M switch it?
   - Does anything else on screen look different, or does the game stutter?
4. `SWG-client/mirage.log` shows whether the blade program was found, the first mirage, and 30-second counts. Tuning goes in `mirage.ini`: `strength`, `spread`, `speed`, `noise_tiles` and `chroma`, read at game start. `debug_view=1` paints the haze area red.

## Files

| File | What it is |
|---|---|
| `src/mirage.c` | The proxy: exports, hooks, the three passes, settings and log |
| `src/mask_ps.hlsl`, `src/haze_ps.hlsl` | The two ps_2_0 programs (compiled by fxc and built into the DLL) |
| `src/blade_ids.h`, `blade_ids.py` | The blade program ids. The script reads them from the client archives and the O14 archive. |
| `src/d3d9.def` | The export names |
| `src/mirage_test.c` | The harness used for the checks above |
| `build.cmd` | Builds `work\o15-mirage\d3d9.dll` and `mirage_test.exe` (VS 2022, x86) |
| `install.ps1`, `uninstall.ps1`, `mirage.ini` | For the owner's client |
| `checks-mirage.json` | Hashes, ids and the harness numbers |
