# Ossus O15: a small effects layer for the client, with the mirage first (Claude, 18 Oct 2026)

Owner, 18 Oct: "a mirage effect for the blade to help hide light", then "how do we make it possible?" (the client has no heat-distortion pass), then "also this hook could be used for other effects too right?"

It is a small `d3d9.dll` of our own that sits in front of DXVK in the client folder. It watches the game's own draw calls, recognises particular draws, and adds screen passes around them. The mirage on the ghostfire blade is the first effect. The code holds that one effect today, and the layer below is how more effects fit in. It is for Miniverse only, not for friends through the launcher.

**State, 18 Oct, 8:37 PM.**
- **The mirage runs in game.** The rebuilt proxy `dc7e87c8` has been on the owner's client since 7:52 PM. Its `mirage.log` from 8:11 PM shows:
  - the ghostfire blade matched, with c3 at about 0.125, 0.031 to 0.063, 0.125;
  - the first mirage, at 1600x900, through `DrawPrimitive`;
  - every 30 s after that, about 1,790 blade draws, all ghostfire, with the same number of mirage passes and none over the cap. The blade draws twice a frame.

  Each 30-second line appeared twice because the owner's two clients write into the same log. Each line now carries its process id.
- **The first proxy never bent anything in game** (`54150519`, 7:11 to 7:47 PM). It followed the Set calls, and the game's state got past them; the harness reproduces this with a state block. The rebuild reads the bound program and c3 from the device at each draw.
- **Archives and ids.** At 8:35 PM the client got archive `23368576`, which is O14 `4c5a29d0` plus the light whip at 2.1 m. Its saber program is new (`0ea2a331`). The installed proxy finds it through `extra_ids=0ea2a331` in `SWG-client/mirage.ini`. The next build (below) has it in its table. `blade_ids.py` now reads several archives, so one build also matches the `b9fbc48a` rollback.

  | Program | Id |
  |---|---|
  | stock saber blade | `0xacc853c5` |
  | O14 saber blade in `23368576` (O14 `4c5a29d0`) | `0x0ea2a331` |
  | O14 saber blade in `b9fbc48a` and `a2610d64` | `0xfac25b60` |
  | light whip blade (its own `e_h_lightwhipblade_ps20`) | `0x238eb66a` |
- **Installed 8:41 PM: `5582152a`** (built 8:36 PM; swapped by the main session on the owner's OK, "Install now (Recommended)"). `SWG-client/d3d9.dll` is `5582152a`, with the backup `d3d9.dll.bak-dc7e87c8`. `dxvk_d3d9.dll` (`265888c3`) is unchanged. `mirage.ini` ends with `extra_ids=0ea2a331` and `log_draws=600`. It adds the blade-draw capture for the light whip's bend (see "The light whip's bend" below) and the ids above. With the capture off it draws exactly like `dc7e87c8`. `capture_read.py` reads the capture.
- **Installed 9:07 PM: `525cd302`** (built 9:03 PM): the light whip's bend (step 3, below), plus everything in `5582152a`. Swapped by the main session on the owner's OK, "Install now (Recommended)". The backups are `d3d9.dll.bak-5582152a` and `.bak-dc7e87c8`. `mirage.ini` has `log_draws=0` and no `[whip]` section, so the whip defaults apply. Not yet seen in game.

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

## The light whip's bend (the second effect)

The plan is in [lightwhip-design.md](../../Documentation-support/lightwhip-design.md), steps 0 and 3. The owner, 18 Oct, 8:3x PM: "can we wait on the parry thing in favor of the bend?"

**Step 0, the capture (build `5582152a`, installed 8:41 PM with `log_draws=600`).**
- **What it's for.** The rope needs the blade's base and tip every frame. The capture shows whether the game's blade draw gives them.
- **What it writes.** For each blade-program draw, one record in `SWG-client/mirage-draws-<pid>.log`:
  - the call and its counts;
  - stream 0 (offset, stride, the buffer's pool, usage and FVF) and the vertex layout;
  - the indices, the positions of up to 64 vertices, and the first 4 vertices in full;
  - the vertex program's id. Its bytecode is saved once as `mirage-vs-<id>.bin`, which `fxc /dumpbin` reads.
  - the vertex constants c0 to c11, and the pixel constants c3 and c7.
- **The constants.** They follow `vertex_program/include/vertex_shader_constants.inc`, which `a_nolighting.vsh`, the blade's vertex program, includes:
  - c0 to c3: object to clip;
  - c4 to c7: object to world;
  - c8: camera position;
  - c9: viewport;
  - c10: fog;
  - c11: material.

  So the blade's vertices and c4 to c7 should give its base and tip in world space.
- **How much.** `log_draws=N` logs N draws of each blade program. The saber (`0ea2a331`) and the whip (`238eb66a`) are counted separately. Ctrl+Shift+L (`draw_key`, `draw_burst`) adds 4 s of every blade draw, for when the swing comes later than the ignition. At two draws a frame, 600 draws is about 10 s and 1 to 2 MB. The log stops at 24 MB. Each client writes its own file, overwritten when that process id starts again. Reading the buffer back is read-only: the capture never changes a draw.
- **Tested in the harness.** The harness's red blade now draws from a vertex buffer with `DrawPrimitive` at a start offset, the way the game draws. Both that path and the UP path log the right vertices. With speed 0, the image is identical for `dc7e87c8`, for the new build with the capture off, and with it on. Not tested: the vertex program path, because the harness has none and the game's blade does.
- **To run it** (with the next swap, client closed):
  1. `install.ps1` copies the proxy.
  2. Add `log_draws=600` under `[mirage]` in `SWG-client/mirage.ini`.
  3. The owner lights a stock saber and swings it for a few seconds, pressing Ctrl+Shift+L while swinging. Then the same with the whip.
  4. Afterwards, set `log_draws=0` again.
- **What decides step 3.** In the log, for every frame with the blade lit:
  - the blade's vertices, put through c4 to c7, have two far ends: the base and the tip;
  - the vertex order stays the same from frame to frame;
  - the length matches the `.lsb` (2.1 m for the whip);
  - both draws of a frame agree.

  If any of these fail, step 3 waits and the plan is rethought.

- **Result, 8:50 PM: step 0 passes.** `capture_read.py` was run on both clients' logs, from 8:43 to 8:50 PM: 4,532 draws, the capture key pressed 16 times.
  - **The draws.** Per blade per frame, `DrawPrimitive` draws a triangle fan of 4 vertices, then a line list over its first 2 vertices. Both use vertex program `5e68b930`; its bytecode is in `SWG-client/mirage-vs-5e68b930.bin`. The layout is `FLOAT3 POSITION0`, `D3DCOLOR COLOR0`, `FLOAT2 TEXCOORD0`, stride 24, in a 2 MB dynamic buffer.
  - **The quad, in object space:** x = plus or minus half the width (0.15 saber, 0.09 whip), y = 0, z = 0 at the base to the current length at the tip (1.2 saber, 2.1 whip). Vertex 0 is always at the tip. Off and igniting blades draw with length 0.
  - **The matrices.** c4 to c7 are column-major (world.x = dot(p, c4), with c7 = 0 0 0 1). The object-to-world scale is 0.817, so in the world the whip is 1.72 m and the saber 0.98 m.
  - **Tracks.** By nearest base, every lit blade had its quad in every frame: 0 frames missing for the whip (142 frames); 3 missing in 502 frames for the saber.
  - **Speeds.** Up to 7 m/s at the base and 48 m/s at the whip's tip during swings.
  - **Another 3D view.** Some frames draw the same saber three more times, one of them 0.6 m from its camera. That is likely the examine or inventory 3D view. Step 3 should leave a whip drawn in such a view straight (see below).

**Step 3, the bend: built 9:03 PM as `525cd302`, installed 9:07 PM, not yet seen in game.**
- **Rule.** Only the whip program (`ids=238eb66a` under `[whip]`).
  - The fan is replaced by a strip along a rope of 20 segments.
  - The edge line that follows it becomes a line along the rope's edge.
  - Every other blade stays as the game draws it.
- **Rope: a follow-through chain in world space.**
  - It starts at the base. Each segment's direction eases towards its parent's direction of the step before, with some momentum. The first segment eases towards the straight blade.
  - Near the hilt it follows quickly (0.5 per 1/240 s); at the tip, slowly (0.1). The momentum is 0.5.
  - So the whip trails a swing, snaps round when the swing stops, and settles straight. It keeps its length and can't fold back on itself.
  - The first model, springs pulling points towards their places on the straight blade, folded the rope into a coil by the hilt in the harness, so it was replaced.
- **Draw.**
  - The base and tip come from the quad (z 0 and z length) through c4 to c7, as in step 0.
  - The strip faces the camera (c8) and goes back into object space through the inverse of c4 to c7.
  - It is drawn with `DrawPrimitiveUP` with the game's layout, vertex program, constants, pixel program, textures and depth test. Culling is off for the strip.
  - Stream 0 and the cull mode are put back afterwards.
  - Texture coordinates run as on the game's quad: u is 1 at the base and 0 at the tip, v is 0 and 1 across.
  - The mirage bends the rope, not the straight blade, because its mask replays the rope draw.
- **Several whips.** Up to 8 ropes. Each is matched by the nearest base within 1 m of a rope drawn in the last 10 frames. A new whip, a jump of more than 0.25 s, or a change in length starts the rope straight.
- **Fallbacks.** These draw the straight blade as the game does:
  - another call or shape, another layout, an unreadable buffer, or no matrix (each logged once);
  - a length of 0 (off);
  - another 3D view (examine, inventory): the rope runs only when the viewport fills the render target;
  - an exception: whips stay straight for the session.
- **Switches.** `[whip] enabled=0`, or Ctrl+Shift+B in game. The settings are `segments`, `follow_base`, `follow_tip`, `momentum` and `substeps_hz`. A `mirage.ini` without a `[whip]` section, like the one on the client now, gets the bend on with these defaults.
- **Also in this build: one mirage pass per blade.** The mirage no longer runs its screen pass a second time for the blade's edge line, which lies inside the quad's mask. That halves the mirage's cost per blade; in the 8:4x PM logs it ran twice per blade per frame.
- **Tested in the harness** (`mirage_test.exe ... whip`). A 2.1 m whip, drawn as the client draws it (fan plus edge line, from a vertex buffer, through a vs_2_0 with the client's packing), swings 1.2 rad at 15 rad/s with `fixed_dt=0.016667`.
  - Every call worked.
  - Without the whip, the frame is identical to `dc7e87c8`.
  - With `debug_view=1` (the haze area painted in), the rope keeps its length and trails as a smooth curve: `work/o15-mirage/preview-whip-rope-mask.png`.
  - Not tested: real-time steps in game, two whips at once, the examine view, MSAA.
- **In game, about 9:10 PM** (`525cd302`, the owner's words via the main session): "lightwhip looks great, just need to be a good bit longer, and more coily it looks pretty phallic right now, ... and not enough trailing on the whip". On length: "4-5? i want it to be able to coil at their feet with an idle animation (idle comes later on)".

**Step 3b, longer and coilier: built 9:18 PM as `86d08fdb`, rebuilt 9:21 PM with the 4.5 m archive's ids as `9f64739e`, not installed.** It goes in together with the chain `f2ac1b6c` (O14 `b7378ca8` plus the 4.5 m whip; the ghostfire session's commit `baa230f`).
- **Ids in `9f64739e`.** `blade_ids.py` read the installed `b8b59aca`, the chain `f2ac1b6c` and the `b9fbc48a` rollback. That gives stock `acc853c5`; saber `0ea2a331` (installed), `983bc32d` (chain) and `fac25b60` (rollback); whip `238eb66a` (installed) and `3df92ce3` (chain). The whip rule's default ids are `238eb66a,3df92ce3`.
- **Harness.** The chain's saber program gets the mirage and its whip program the rope, with the same pixel counts as the 4.5 m test. Without a whip, the frame is identical to `dc7e87c8`.
- **The whip's native ghostfire trail** (`pixel_program/ghostfire_trail_ps20.psh`, drawn between the straight `tr1s` and `tr1e` over 2.0 s) is not bent. It fans out where a straight whip would be. A later rule could find those draws by that program and bend them along the rope's recent positions. Not built.
- **Length.** The rope takes its length from the game's quad, so 4.5 m needs no code. The default is now 40 segments (up to 64), so a 4.5 m strand (3.7 m in the world) has segments of about 9 cm.
- **Coil and droop.** Each segment now aims at its parent's direction bent a little down (`droop`) and a little round (`coil`, a helical wave of `coil_turns` along the strand, travelling from the hilt at `coil_speed`). The round direction is taken from the hilt's own x axis, so the wave turns with the hand. Both grow towards the tip.
  - In the harness, a 4.5 m whip swung and then held: it trails in waves during the swing and rests in an S-curve with a curl or hook at the end, rather than a rod. See `work/o15-mirage/preview-whip-4p5m.png`: straight on top, rope below, frames 12, 24, 48, 72 and 120.
  - It takes 1 to 2 s to settle, because the tip follows slowly.
  - At `coil` above about 0.3 the strand bunches into a knot by the hilt (`preview-whip-curl.png`), so 0.18 is the default.
- **More trailing.** The follow rates are looser: 0.35 at the hilt to 0.04 at the tip, with momentum 0.6 (before: 0.5, 0.1, 0.5). "Not enough trailing" may also mean the ghostfire trail; that is the ghostfire session's.
- **Thinner, tapered.** The strip is 0.7 of the blade's width and narrows to 0.25 of that at the tip (`width`, `taper`). This takes the rod look away without changing the `.lsb`. Players without the DLL see the `.lsb` width, but only the owner has the DLL.
- **Settings**, all in `[whip]` and read at game start: `segments`, `follow_base`, `follow_tip`, `momentum`, `droop`, `coil`, `coil_turns`, `coil_speed`, `width`, `taper`. Tuning needs no rebuild.
- **The new program id.** The whip rule matches by id (`[whip] ids`, default `238eb66a`), and the mirage by its id table. When the ghostfire session's id arrives, either set `[whip] ids=<new>` and `[mirage] extra_ids=<new>` in the ini, or rebuild with `blade_ids.py` on the new archive (preferred: one build for both).
- **Future step: the coil at the feet** (owner: "coil at their feet with an idle animation (idle comes later on)"). Not built. When the wielder is idle (the hilt still for a second or more), the strand would lie on the ground: segments below the hilt's height pulled to the ground plane at the wielder's feet and laid out in a loose spiral. Open questions:
  - where the ground is (the hook sees no terrain; the lowest point of the wielder's model, or a fixed height below the hilt);
  - how to tell idle from a slow walk;
  - what the idle animation itself does with the hand.

- **To try** (game closed, the owner's OK):
  1. Copy `work/o15-mirage/d3d9.dll` over `SWG-client/d3d9.dll`, or run `install.ps1`.
  2. Set `log_draws=0` in `mirage.ini`.
  3. Swing the whip; Ctrl+Shift+B compares rope and straight.
  4. `mirage.log` counts ropes and straight whips every 30 s.

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
- **Untested in game.** The blade draws with `DrawPrimitive` from a vertex buffer (seen in game, 8:11 PM). Still unknown:
  - whether "Post Process Effects" (bloom) draws the blade into another target (the mirage then bends that target, which should be fine);
  - SWG's anti-aliasing (MSAA). There is a multisampled path, but the harness ran without MSAA.
  - whether the O13 Ghostfire Lightsaber, whose shader has no palette part, still sets a dark c3. If it doesn't, only crystal-coloured blades get the mirage.
- **DXVK chaining.** The method table is the fixed Direct3D 9 interface, so new DXVK versions keep working. But an updated DXVK `d3d9.dll` must be renamed to `dxvk_d3d9.dll` again. ReShade's d3d9 build (Client-graphics Path A) also wants to be `d3d9.dll`, and dgVoodoo (Path B) replaces DXVK. With either one in place, this proxy can't sit in front.
- **Friends' GPUs.** Cost comes only while a matching draw is on screen. A mirage adds a screen copy and two full-screen passes, about ten texture reads a pixel. That is nothing on a 5070, and well under a millisecond on most cards from the last ten years. `max_per_frame=8` caps a crowd of ghostfire wielders. With no match in view, the cost is a few comparisons per draw. Each new effect needs its own cap.
- **Only players with the DLL see it.** It changes nothing on the server. Without it, a player sees the archive's look as it is. Effects built on redirect, such as NGE heat, would show the raw heat draw to players without the DLL, so their art has to look acceptable without it, or be marker-only.
- **Launchers.** Both launchers start the same `SWG-client` folder. I haven't checked whether their file check minds an extra `dxvk_d3d9.dll` or a changed `d3d9.dll`. DXVK's `d3d9.dll` was already an addition, so probably not; watch the first launch. To ship it to friends later, the installer would carry `d3d9.dll`, `dxvk_d3d9.dll` and the ini together. Not before it has been tried here.
- **Two clients at once** (`allowMultipleInstances`). Each loads its own copy. They share `mirage.log`, and from build `5582152a` every line carries the process id. The capture writes one file per process.

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
| `src/mirage.c` | The proxy: exports, hooks, the mirage's rule and three passes, the blade-draw capture, settings and log |
| `src/mask_ps.hlsl`, `src/haze_ps.hlsl` | The two ps_2_0 programs (compiled by fxc and built into the DLL) |
| `src/blade_ids.h`, `blade_ids.py` | The blade program ids. The script reads them from the client archives and the O14 archive; later effects' ids come the same way. |
| `src/d3d9.def` | The export names |
| `src/mirage_test.c`, `src/test_vs.hlsl` | The harness used for the checks above (`whip` mode: the client's whip draws through a stand-in vertex program) |
| `capture_read.py` | Reads `mirage-draws-<pid>.log` (step 0): the blade's shape, ends, tracks and a verdict |
| `build.cmd` | Builds `work\o15-mirage\d3d9.dll` and `mirage_test.exe` (VS 2022, x86) |
| `install.ps1`, `uninstall.ps1`, `mirage.ini` | For the owner's client |
| `checks-mirage.json` | Hashes, ids and the harness numbers |
