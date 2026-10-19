# Ossus O14: the ghostfire crystal drives the blade on any saber, plus a strobe-trail test (Claude, 18 Oct 2026)

Owner, 18 Oct ~6:10 PM: "can we make a new Crystal entry with the new shader and make all sabers compatible with the new crystal type? also the blade needs to be dimmer and the trails more prominent (and slow like LSD ...)". Later: "def make sure you understand the stacking of the tracers ... almost time dilation kinda vibes" and "a mirage effect for the blade to help hide light". On the decision card the owner picked **the strobe trail, tested first**, and asked how a real mirage could be made possible.

**Built, not installed** (the game was running): archive `work/ossus-ghostfire-crystal/local_planets-ghostfire-crystal.tre`, sha256 `a6dcb82c…`, on `c8a61080` (now its default base, `work/ossus-ghostfire-blade/`). The main session installed the earlier `feb3bf84` with its light whip as `a2610d64` (run 37, 7:41 PM). The light whip step chained on this build is `work/ossus-ghostfire-crystal/chain/local_planets-o14-lightwhip.tre`, sha256 `f8df3089…`. Its only differences from the installed `a2610d64` are the trail files and the Ghostfire Lightsaber's blade frames. Two builds give the same hash. Checks are in `checks-crystal.json`.

## The crystal drives the blade (any saber)

- The crystal only picks a palette entry, and every stock blade draws with one pixel shader, `e_h_lightsaberblade_ps20.psh`. O14 replaces that shader with `e_h_lightsaberblade_ps20.hlsl`, compiled for ps_2_0 with the Windows SDK's `fxc.exe`. It uses 36 of 64 instruction slots, on the stock registers.
- **Every crystal the server gives** (palette 0-11 and 31, brightest channel 65% or more) gets exactly the stock result: the ghostfire weight is 0.
- **The ghostfire crystal** (32, and the server's shimmer steps 33-40) has every channel at 15.7% or less. For it, the white core drops to 1.5%, and the glow becomes faint milky opal bands at 8%. The owner, 7:15 PM, on O13's 32%: "the blade is still too visible"; it read as a solid rainbow rod in game, two to three times brighter than the preview.
  - The palette's green channel carries the shimmer step, `(20, 4k, 20)` for entry 32 + k. So the bands drift along the blade as the server steps the colour every 150 ms.
- No new server crystal is needed: the existing ghostfire crystal (colour 32) is the new crystal type.
- Older graphics paths (the effect's ps_1_1 and fixed-function versions) stay stock and show the dim tint.

## Changes after the owner's look at O13 (7:15 PM, in game)

The owner said: "the trails are still too faint and the blade is still too visible." The main session's capture showed a solid pastel rainbow rod, a swing trail that shows for a frame or two, and the kirruk and the robe lit strongly red while the blade was out.
- **Blade:** the ghostfire path is now at 8% glow and 1.5% core, and the opal is milkier (0.72 ± 0.28).
- **The Ghostfire Lightsaber draws the stock blade again.** The crystal decides its look like any saber, and the ghostfire crystal gives the faint opal path. The O13 opal textures stay in the archive, unused.
- **Red light:** the ghostfire blade file has no light section; the sleek silver blade it was copied from has none. So the red didn't come from a light set in that file. In case the engine falls back to a default light in the crystal's colour, the file now has the gen5 blade's light with its colour at 0. Which crystal was in the saber, and where the red came from, are open.
- **Strobe trails:** they now last 2.0 s, at full colour alpha (was 0.5), with the stock saber trail's doubled additive effect (`e_particle_emisadd_2x`). The bars are more saturated.

## 7:50 PM: "trails are too vibrant, and there is a red saber in there somehow"

- **The red saber:** the server sets the blade colour only when a colour crystal goes in (`SaberInventoryContainerComponent.cpp`: insert sets the crystal colour, remove sets 31). A saber that never had one has no colour, so the client uses the blade shader's default, palette 0, which is red. The take 2 red light fits this too. The owner is dark side, but alignment plays no part: nothing else on the server sets a player's blade colour.
  - The Ghostfire Lightsaber now has its own copy of the stock blade (`shader/ghostfire_blade.sht` over `ghostfire_blade_a..d.sht`) whose default is 32. With no colour crystal it shows the ghostfire blade, and any colour crystal still decides as usual. Every other saber is unchanged.
- **The trails:** the strobe copies work; each swing left a fan of separate bars. They were far too loud, so they're now on the single additive effect (was doubled), at half alpha, last 1.2 s (was 2), with 6 copies per trail (was 8). Every colour is 20% toward a smoky violet. The tip ribbons are at half alpha too.

## Oil-slick trails, and an almost invisible blade (owner, 18 Oct evening)

The owner, relayed by the main session: "maybe mix some darker colors in too for a more gasoline purple fumed kinda thing, and the color is mostly for the trails, the blade should be almost nonexistent".
- **Blade:** the ghostfire path is now at 3.5% glow and 0.6% core, a near-colourless milky sheen (0.82 ± 0.18).
- **Trails:** the strobe-trail bars and the eight tip ribbons use an oil-slick or fumed-metal palette: deep violet, indigo, petrol blue, teal, one bronze glint, magenta, plum and blue-violet. Then the owner asked to "add some cyan and a brighter green": both are now full-strength bands. Each band drifts towards the next colour from hilt to tip, like a thin film. Additive light can't darken anything, so "darker" here means deep hues, with every other band at half strength.
- The ribbons' old pastel colours are kept in `checks-crystal.json`.

## Trails

- **Research.** Dubois and VanRullen 2011 (PLOS Biology) describe LSD trails as discrete still afterimages behind a moving object, like a stroboscopic multiple-exposure photograph. PsychonautWiki: at high intensity, trails are nearly solid, last seconds and cover the whole path. Bluelight reports: repeated copies of a moving hand, with colour inside the smear. The owner adds stacking (copies that build up) and "time dilation" (the swing seems to lag behind itself).
- **Base-game trails** are one continuous smear sampled 30 times a second, with a lifetime set in the trail file (weapons 0.06 s, contrails 0.25-0.5 s, missile smoke 2-4 s). So they can't stack copies by themselves.
- **The server's tip ribbons** (main session, crystal-linked) now last 1.2 s instead of 0.1 s.
- **Strobe-trail test.** A saber's trail is the surface the blade sweeps between its trail hardpoints (`tr1s` hilt, `tr1e` tip). Bright bars with gaps along the trail's time axis should leave copies of the whole blade that stack and fade over 2 s.
  - **A, the Ghostfire Lightsaber (O13):** its trail, 2 s, 8 pastel bars per trail texture.
  - **B, "Ghostfire Lightsaber (trail test B)":** the same saber on a second template. It uses the newer trail layout with 8 samples a second and one bar per texture, in case the game repeats the texture for each sample rather than once along the trail.
  - Whichever shows copies tells us how the game maps the texture; then I tune it and tie it to the crystal.
  - Previews: `preview-strobe-a.png` and `preview-strobe-b.png` next to the archive.
  - Server: `server/strobe-test-dev.patch` (Lua: template B and its loot item). It passes `git apply --check` on dev `6d544cf3`.

## Mirage

`SWGEmu.exe` has no heat-distortion pass. The heat shaders exist only in the NGE (MTG) archives, and they need an engine pass this client lacks. The client draws through DXVK 3.1.1, the `d3d9.dll` in the client folder, which runs Direct3D 9 on Vulkan.

A real mirage needs a small graphics hook between the game and DXVK. When our blade shader draws, the hook copies the screen, and a heat pass bends it behind the blade. Visual Studio 2022 is installed here. Every player would need the DLL, and the launcher could ship it. This is its own project.

## Install (main session or this one, owner off the game)

1. Archive in both places, by rename at `/opt/swg/tre`; back up `c8a61080`.
2. `git apply` `server/strobe-test-dev.patch` in dev.
3. Restart the test galaxy with run 35's settings (Lua for test saber B).

## Please look at these (your own words)

1. Any saber with the ghostfire crystal: is the blade almost nonexistent now, or still too visible?
2. A normal crystal in any saber: does it look the same as before?
3. Spawn `/server loot item ossus_ghostfire_saber 1` (A) and `/server loot item ossus_ghostfire_saber_b 1` (B). Put the ghostfire crystal in each, and swing slowly, then fast. Which one leaves copies of the blade, and how long do they stay?
5. Is the red light on the creature and your robe still there? Which crystal was in the saber when you saw it, if any?
6. After the 7:50 PM changes: are the trails now a dark petrol sheen, or too faint? Which test saber left the fan of copies, A or B?
4. With the ghostfire crystal: how do the oil-slick colours and the 1.2 s tip ribbons look next to the strobe trail? Dark enough, or too dim to see?
