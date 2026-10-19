# Ossus O15: a small effects layer for the client, with the mirage first (Claude, 18 Oct 2026)

Owner, 18 Oct: "a mirage effect for the blade to help hide light", then "how do we make it possible?" (the client has no heat-distortion pass), then "also this hook could be used for other effects too right?"

It is a small `d3d9.dll` of our own that sits in front of DXVK in the client folder. It watches the game's own draw calls, recognises particular draws, and adds screen passes around them. The mirage on the ghostfire blade is the first effect. The code holds that one effect today, and the layer below is how more effects fit in. It is for Miniverse only, not for friends through the launcher.

**State, 18 Oct, 7:55 PM.**
- **The first proxy never bent anything in game.** It is `54150519` (built 6:53 PM) and has been on the owner's client since about 7:11 PM. Its `mirage.log` from the 7:11 and 7:35 PM sessions shows the blade programs loading, but not a single ghostfire draw or mirage pass. It followed the game's SetPixelShader and constant calls. The harness reproduces the miss when a blade's program and colour come from a recorded state block.
- **The rebuilt proxy reads the bound program and c3 from the device at each draw**, so it doesn't matter how the game sets them. Its log also lists the first blade draws with their c3, and every 30 seconds counts how often a blade program was bound and drawn. That way the next session shows directly whether it matches.
- **Archives.** The owner's OK covers the setup installed at 7:41 PM: archive `a2610d64`, which is O14 `feb3bf84` (the near-invisible ghostfire blade with oil-slick trails) plus the light whip. The ids come from `blade_ids.py`:

  | Program | Id |
  |---|---|
  | stock saber blade | `0xacc853c5` |
  | O14 saber blade | `0xfac25b60` |
  | light whip blade (its own `e_h_lightwhipblade_ps20`) | `0x238eb66a` |

  Both of ours use the same dark-crystal rule as before.
- **Preview.** It is `work/o15-mirage/preview-mirage-a2610d64.png`. From left to right: saber off; saber on; saber on 8 frames later; whip off; whip on. Off shows almost nothing, because the blade is only a faint sheen now. On, a ripple traces the blade. The numbers are in `checks-mirage.json`.

## The layer

Every effect is made of the same three parts.

1. **Draw rules (per-draw hooks).** A rule recognises a draw and says what to do with it.
   - **Recognise by:**
     - the pixel program's id: FNV-1a over its bytecode without the comment block, the same for every player with the same archives;
     - a test on the shader constants, such as the crystal colour in c3 or the fade in c7;
     - later, the vertex program's id or the bound texture.
   - **Actions:**
     - **mask:** replay the draw into a named screen mask, then let the game's draw happen as usual (the mirage does this);
     - **redirect:** draw it only into a mask, not into the scene (for the NGE heat programs below, whose draws are not meant to be seen);
     - **swap:** draw with our own pixel program instead (possible, but the archive stays the normal route for looks everyone should see);
     - **mark:** a draw whose only job is to carry settings in its constants, such as a per-planet colour grade.
   - **Marker programs.** For new effects we ship a tiny pixel program of our own in the archive, and art that should drive an effect uses it. The layer knows its id, so recognition is exact and never guesses at stock shaders.
2. **Screen passes, at a point in the frame.**
   - **Before the matching draw.** Only what is already drawn is affected. The mirage runs here: the blade then draws on top, and the UI is untouched.
   - **After the world, before the UI.** For grading or haze over everything 3D. This needs the point where the UI starts, which is still to be found. The UI likely starts at the first pre-transformed 2D draw after the scene.
   - **Before Present.** Everything, the UI included.
   - **Kinds of pass:**
     - a distortion through a mask (mirage, heat);
     - a colour pass (grading);
     - later others.
3. **Switches.**
   - one master `enabled` for the whole layer (pass-through when 0);
   - per effect, its own `enabled`, toggle key and settings in its own ini section;
   - the uninstall script.

   Today the file is `mirage.ini`, with one `[mirage]` section that does both jobs. With a second effect it becomes `effects.ini`, with a `[layer]` section plus one section per effect.

**What the code has now.**
- A draw rule needs only Reset, Present, pixel program create and the four draw calls. At each draw it reads the bound program and constants from the device; following the Set calls missed the blade in game. New rules add no hooks. SetPixelShader, BeginStateBlock and CreateStateBlock are hooked as well, but only for the log.
- The mirage's rule and pass are written out in `run()`. The next step is a rule table read from the ini.
- "After the world, before the UI" needs a detector for the UI's first draw.
- Depth (below) needs hooks on CreateDevice, Reset, and the depth surface get and set calls.

## Candidates

| Effect | Draw rule | Screen pass | Depth texture? | Notes |
|---|---|---|---|---|
| **Mirage on the ghostfire blade** (built) | blade program id plus c3 at 0.17 or less: mask | distortion with an opal colour split, before the blade draw | No | See "The mirage" below. |
| **NGE heat shaders** (in `mtg_patch_018.tre`) | the ids of `3d_heat_render.psh` and `3d_lava_heat_render.psh`: redirect into a heat mask | `2d_heat_composite.psh` itself (ps_2_0; there is also a ps_1_4 copy), with a copy of the scene at s0 and the heat mask at s1 | No | Details below the table. |
| **Heat haze over lava, engine exhausts** | lava: the lava surface or a heat sheet above it with `3d_lava_heat_effect`. Exhausts: a particle with a marker program or `3d_heat_effect`. Either one is masked or redirected. | distortion, before the next non-heat draw or after the world | No (optional, to fade with distance) | It is the same route as NGE heat once that works. |
| **Stealth or cloak shimmer** | the stealthed character's draws: mask, or redirect for a fully see-through, Predator-like body | distortion | No | Recognising the draws is the hard part. Stock stealth fades the character through c7 on ordinary programs, and a rule on c7 would also catch every other fading object. A server-side marker (switching the stealthed body to a marker program) would be exact. |
| **Force-power shockwaves** | an expanding ring particle with a marker program: mask, where the mask's two spare channels carry the push direction, like NGE's heat mask | distortion that pushes outward | No (optional, so the foreground isn't bent) | It needs the ring particle in our archive and the server playing it on the power. |
| **Per-planet colour grading** | a mark draw per planet: a marker program on an invisible object or the sky, whose constants carry the grade. Recognising each planet's sky textures is the fallback. | colour pass (lift, gamma and gain, or a small 3D lookup table), after the world and before the UI | No (yes for grading by distance, like fog) | It needs the UI-start detector. |

**NGE heat shaders in detail.**
- **The files.** `mtg_patch_018.tre` has the whole set:
  - pixel programs `3d_heat_render`, `3d_lava_heat_render`, `2d_heat_composite` and `2d_heat_composite_1_4`;
  - vertex programs `vertex_heat_render` and `vertex_lava_heat_render`;
  - effects `3d_heat_effect` and `3d_lava_heat_effect`;
  - shaders `3d_heat_render`, `3d_lava_heat_render` and `2d_heat_composite`.
- **The heat render.** It writes the heat mask: red is intensity, green and blue are offsets from a 3D noise texture, and alpha is 0.
- **The composite.** It bends the scene by (green and blue minus 0.5) × intensity × 1% of the screen, so at most about half a percent. It keeps the old pixel where the bent lookup would land outside the heat area.
- **In the layer.** NGE's engine drew heat objects into their own target; this client would draw them straight into the scene. The layer redirects them into its mask and runs the composite at the end, so any object we give `3d_heat_effect` becomes a heat source. That makes it the general heat route, which the mirage could use too.
- **Unknowns.**
  - whether this client loads those NGE effect and shader files;
  - where their 3D noise texture lives;
  - the time value in `userConstants[0]` (c8), which NGE's engine set (the layer can set it if the client doesn't).

**Depth.**
- **Not needed for draw-rule effects.** They replay with the game's own depth buffer bound, so walls in front already hide the effect.
- **Needed for anything that reads depth as a texture.** Examples: haze that fades with distance, soft edges against the ground, not bending what stands in front, distance fog in a grade.
- **How to get it.** At device creation and Reset, the layer swaps the game's depth buffer for an INTZ depth texture and returns that to the game, the way ReShade does on Direct3D 9. DXVK lists INTZ among the depth formats it supports; I have not tried it here.
- **Limits.** An INTZ texture can't be multisampled, so depth effects would need SWG's anti-aliasing off (Client-graphics already asks that for ReShade). It is one more hooked path that touches every frame, so it should be an option only the effects that need depth turn on.

## Why a proxy rather than ReShade

| | Our proxy `d3d9.dll` (chosen) | ReShade add-on |
|---|---|---|
| Sees the game's draws? | Yes. It sees the game's own Direct3D 9 calls: pixel programs and constants. | Not with DXVK. ReShade's d3d9 build wants to be `d3d9.dll` itself and loads Windows' d3d9, not DXVK. Its Vulkan mode only sees DXVK's translated shaders, without the program ids or constants. |
| Download | None (about 150 KB, built here with VS 2022) | ReShade with full add-on support (needs your OK), plus our add-on |
| Friends later | One more DLL and an ini in the client folder | ReShade's installer on every PC |

## The mirage (the first effect)

1. **The hook.** The client's graphics plugin (`gl07_r.dll`) imports only `Direct3DCreate9` from `d3d9.dll`. Our DLL takes that name, loads DXVK from `dxvk_d3d9.dll` beside it, and patches the device methods above.
2. **The rule.** A draw counts when both of these hold:
   - the pixel program bound at that draw (read from the device) is a blade program: the stock one, the O14 saber's or the light whip's, all listed above;
   - the crystal colour in c3 has every channel at 0.17 or less. That is the O14 shader's own rule: palette 32-40 is ghostfire, and every stock crystal is 0.65 or brighter.

   Normal crystals never trigger it.
3. **Three passes before that blade draw.** ps_2_0 has no screen position, so the screen position comes from rasterising:
   1. **Mask.** The same draw is replayed into a screen-sized mask target, with the game's vertices, viewport and depth test. Our pixel program turns the blade's glow and core into a mask value and multiplies it by the game's fade.
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
| The ghostfire blade's program and c3 set through a recorded state block (rerun at 7:50 PM, hidden window) | the first proxy: 0 pixels changed, as in game. The rebuilt one: about 7,000-7,900 changed for the stock, O14 saber and whip programs, the red blade 0, bend 0 identical to off |
| install.ps1 twice, then uninstall.ps1, on a scratch copy of the client's DXVK DLL | renames DXVK and back, places and removes the proxy |

**Without DXVK (Windows' own Direct3D 9) the haze draws nothing.** Every call succeeds, but the screen quad leaves no pixel, even in the debug view with nothing discarded. I could not trace it without Microsoft's debug runtime. So when `dxvk_d3d9.dll` is missing, the proxy passes everything through and logs that; `allow_native=1` would try anyway. The client ships with DXVK, so this only matters if someone removes it. It holds for every effect in the layer.

## Risks

- **Crashes.** A failing step is logged once and the game's own draw still happens. An exception in our code switches the layer off for the session. A crash inside DXVK or the driver can't be caught, so the first in-game run is the real test.
- **Untested in game.** Several things are still unknown:
  - which draw call the client uses for blades;
  - whether "Post Process Effects" (bloom) draws the blade into another target (the mirage then bends that target, which should be fine);
  - SWG's anti-aliasing (MSAA). There is a multisampled path, but the harness ran without MSAA.
  - whether the O13 Ghostfire Lightsaber, whose shader has no palette part, still sets a dark c3. If it doesn't, only crystal-coloured blades get the mirage.
- **DXVK chaining.** The method table is the fixed Direct3D 9 interface, so new DXVK versions keep working. But an updated DXVK `d3d9.dll` must be renamed to `dxvk_d3d9.dll` again. ReShade's d3d9 build (Client-graphics Path A) also wants to be `d3d9.dll`, and dgVoodoo (Path B) replaces DXVK. With either one in place, this proxy can't sit in front.
- **Friends' GPUs.** Cost comes only while a matching draw is on screen. A mirage adds a screen copy and two full-screen passes, about ten texture reads a pixel. That is nothing on a 5070, and well under a millisecond on most cards from the last ten years. `max_per_frame=8` caps a crowd of ghostfire wielders. With no match in view, the cost is a few comparisons per draw. Each new effect needs its own cap.
- **Only players with the DLL see it.** It changes nothing on the server. Without it, a player sees the archive's look as it is. Effects built on redirect, such as NGE heat, would show the raw heat draw to players without the DLL, so their art has to look acceptable without it, or be marker-only.
- **Launchers.** Both launchers start the same `SWG-client` folder. I haven't checked whether their file check minds an extra `dxvk_d3d9.dll` or a changed `d3d9.dll`. DXVK's `d3d9.dll` was already an addition, so probably not; watch the first launch. To ship it to friends later, the installer would carry `d3d9.dll`, `dxvk_d3d9.dll` and the ini together. Not before it has been tried here.
- **Two clients at once** (`allowMultipleInstances`). Each loads its own copy. They share `mirage.log`, and each block starts with the process id.

## Switching it off

1. **In game:** Ctrl+Shift+M switches the mirage off and on at once (only while the game window is in front). Each later effect gets its own key.
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
| `src/mirage.c` | The proxy: exports, hooks, the mirage's rule and three passes, settings and log |
| `src/mask_ps.hlsl`, `src/haze_ps.hlsl` | The two ps_2_0 programs (compiled by fxc and built into the DLL) |
| `src/blade_ids.h`, `blade_ids.py` | The blade program ids. The script reads them from the client archives and the O14 archive; later effects' ids come the same way. |
| `src/d3d9.def` | The export names |
| `src/mirage_test.c` | The harness used for the checks above |
| `build.cmd` | Builds `work\o15-mirage\d3d9.dll` and `mirage_test.exe` (VS 2022, x86) |
| `install.ps1`, `uninstall.ps1`, `mirage.ini` | For the owner's client |
| `checks-mirage.json` | Hashes, ids and the harness numbers |
