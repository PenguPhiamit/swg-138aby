# Ossus O14: the ghostfire crystal drives the blade on any saber, plus a strobe-trail test (Claude, 18 Oct 2026)

Owner, 18 Oct ~6:10 PM: "can we make a new Crystal entry with the new shader and make all sabers compatible with the new crystal type? also the blade needs to be dimmer and the trails more prominent (and slow like LSD ...)". Later: "def make sure you understand the stacking of the tracers ... almost time dilation kinda vibes" and "a mirage effect for the blade to help hide light". On the decision card the owner picked **the strobe trail, tested first**, and asked how a real mirage could be made possible.

**Installed 18 Oct 8:07 PM** (owner, 8:05 PM, client closed: "Install now"): `b9fbc48a…` is on the client and at `/opt/swg/tre` (renamed in), with backups `.bak-a2610d64` in both places. Client data only, so run 37 kept running with no restart. Untested in game.

The O14 archive alone is `work/ossus-ghostfire-crystal/local_planets-ghostfire-crystal.tre`, sha256 `3797288d…`, on `c8a61080` (its default base, `work/ossus-ghostfire-blade/`). The installed file is the main session's light whip step chained on it, `work/ossus-ghostfire-crystal/chain/local_planets-o14-lightwhip.tre`, sha256 `b9fbc48a…`. Its only differences from the previous `a2610d64` are the customization table and the trail files, including test saber B's diagnostic. Two builds give the same hash. Checks are in `checks-crystal.json`.

## The crystal drives the blade (any saber)

- The crystal only picks a palette entry, and every stock blade draws with one pixel shader, `e_h_lightsaberblade_ps20.psh`. O14 replaces that shader with `e_h_lightsaberblade_ps20.hlsl`, compiled for ps_2_0 with the Windows SDK's `fxc.exe`. It uses 36 of 64 instruction slots, on the stock registers.
- **Every crystal the server gives** (palette 0-11 and 31, brightest channel 65% or more) gets exactly the stock result: the ghostfire weight is 0.
- **The ghostfire crystal** (32, and the server's shimmer steps 33-40) has every channel at 15.7% or less. For it, the white core drops to a few percent, and the glow becomes faint milky opal bands (now 14% glow and 2% core; see the 8:15 PM section). The owner, 7:15 PM, on O13's 32%: "the blade is still too visible"; it read as a solid rainbow rod in game, two to three times brighter than the preview.
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

- **The red saber, found (the owner had the ghostfire crystal in):** the client applies a customization variable only to appearances its asset customization table (`customization/asset_customization_manager.iff`, `CIDX`) lists. Stock blades link through to `/private/index_color_blade` on `wp_lightsaber.pal`. Our new blade file and the light whip's were not listed, so the server's colour 32 was dropped and the default, palette 0 (red), drew. Both now have a row pointing at the sleek silver blade's key (18199), and the Ghostfire Lightsaber draws the stock blade again. The server never uses this table for the blade colour, so this is client data only. Four MTG saber blades have the same gap and ignore their crystal: mandalorian, must, gcw_1h and pvp_bf.
- *(Superseded, kept for the record)* **The red saber, first reading:** the server sets the blade colour only when a colour crystal goes in (`SaberInventoryContainerComponent.cpp`: insert sets the crystal colour, remove sets 31). A saber that never had one has no colour, so the client uses the blade shader's default, palette 0, which is red. The take 2 red light fits this too. The owner is dark side, but alignment plays no part: nothing else on the server sets a player's blade colour.
  - The Ghostfire Lightsaber now has its own copy of the stock blade (`shader/ghostfire_blade.sht` over `ghostfire_blade_a..d.sht`) whose default is 32. With no colour crystal it shows the ghostfire blade, and any colour crystal still decides as usual. Every other saber is unchanged.
- **The trails:** the strobe copies work; each swing left a fan of separate bars. They were far too loud, so they're now on the single additive effect (was doubled), at half alpha, last 1.2 s (was 2), with 6 copies per trail (was 8). Every colour is 20% toward a smoky violet. The tip ribbons are at half alpha too.

## 8:15 PM look at `b9fbc48a` (take 4): "the trails are too faint now, and the blade can come to where the trails are now", "we dont see enough of all the colors"

**Installed 18 Oct 8:29 PM** (owner, 8:25 PM: "Install now"): on the client and at `/opt/swg/tre` (by rename), backups `.bak-b9fbc48a` in both places, `extra_ids=0ea2a331` in `SWG-client/mirage.ini`, run 37 still up. Untested in game. **Since 8:35 PM the installed file is `23368576`:** this O14 (`4c5a29d0`) plus the light whip session's rebuild (2.1 m strand, no native trail; whip program `238eb66a` unchanged), backups `.bak-49d6ae99`. The whip builder's defaults are now those settings, so the chain helper (O14, then `Lightwhip/build_lightwhip.py --base` the O14 file) gives `23368576` again, checked 8:35 PM. Owner, about 8:26 PM: "the ghostfire almost looks better in the whip, but honestly it bending is the most important to me rn the ghostfire is nearly done".

O14 `work/ossus-ghostfire-crystal/local_planets-ghostfire-crystal.tre` = `4c5a29d0…`. The chain with the light whip is `work/ossus-ghostfire-crystal/chain/local_planets-o14-lightwhip.tre` = `49d6ae99fb28b00133468582f2604398ea95e99dff5c517aa92420cc400f3269`. Two builds of each give the same hash. Only the blade shader, the eight ribbon files and the strobe trail (A) differ from the installed `b9fbc48a`. The customization table and the palette are byte for byte the same. Client data only, no restart.
- **What the capture showed:** no blade glow; the trails were thin pale streaks that read green on the grass, with almost no purple. The half-strength bands and the 20% smoky-violet mix washed the violets out, and green and cyan, much brighter to the eye, won.
- **Trails:** full alpha again (was 0.5) on the single additive effect: twice what the owner saw, half the 7:50 PM strength the owner called too vibrant. The palette has no dimmed bands and no grey. It has ten hues in an oil slick's order: violet, blue, cyan, green, gold, magenta, purple, teal, rose and indigo. Purples and blues are at full strength; green, cyan, gold and teal are a little lower, so they don't drown the rest. The tip ribbons (any hilt) take the first eight, and the strobe bars (A) the first six, so each spans the whole range.
- **Blade:** glow 3.5% → 14%, core 0.6% → 2%, and the opal a little more coloured (0.75 ± 0.25). Normal crystals still get exactly the stock blade.
- **Mirage:** the blade's compiled code changed, so its id is now `0ea2a331` (was `fac25b60`; the whip's `238eb66a` is unchanged). Add `extra_ids=0ea2a331` to `SWG-client/mirage.ini` with this install, or the mirage stops; no proxy rebuild is needed. The ghostfire c3 values are unchanged, so `max_bright` stays.
- **Builder fix:** the builder read its "stock" pixel program and customization table from the live client, whose `local_planets.tre` is now ours. It now reads them from the archives under it.

## ~8:5x PM: the ghostfire trail in any hilt ("yes, it was supposed to be tied to the crystal, go in any hilt")

The owner, after "trails do not work without the hilt": the broad swing trail showed only on the Ghostfire Lightsaber, because only its own trail row had the strobe file. The server's tip ribbons are thin, play only in combat, and don't count as the trail.

**Built, not installed:** O14 `a0cca018aceaeea12a140752dbc3bed326e086957e7e368651f6726566b47522` (two builds give the same hash; it replaces `b60189b7` below and contains it). With the light whip step on it, the chain is `b8b59aca22802d0977633f7a13657590045df9e4a11a070081054cce2ee33f9d` (light whip commit 332099e). My chain helper rebuilds it byte for byte, and the whip step changes only O14's swoosh table, CRC table and two string files. This is the archive to install.
- **The shared saber trail:** `appearance/sw_light_saber_white.swh` is the trail all 169 saber rows use, with UseObjectHue 1. It now lasts 1.2 s at alpha 1, on `shader/sw_light_saber_ghostfire.sht`. That shader's effect is a copy of the stock doubled additive effect with our ps_2_0 program, `ghostfire_saber_trail_ps20.hlsl` (28 slots).
  - **Every other crystal:** the program draws the stock result (texture × crystal colour × 2), only over the newest 5% of the trail: the stock 0.06 s, with the stock fade. Those trails should look as before.
  - **Ghostfire:** the oil-slick strobe bars over the whole 1.2 s, in any hilt.
- **The texture** `texture/sw_light_saber_ghostfire.dds` keeps the stock trail texture's alpha texel for texel, with the bars in the colour channels. The stock texture is white wherever it's visible; its faint edge texels darken with the alpha, and the program follows that.
- **The Ghostfire Lightsaber** now uses the shared trail row (UseObjectHue 1) like any hilt. Its own strobe files stay in the archive, used by the whip's trail. Test saber B is unchanged.
- **Unverified assumption:** the trail fades its vertex alpha linearly from the file's alpha to 0 over its life. The texture is uniform along the trail, so the fade has to come from the vertices, and the 7:50 PM capture shows older copies dimming. If normal crystals' trails now linger 1.2 s, the assumption is wrong. The fix then is to reinstall the previous archive (client only, no restart).
- **Older graphics paths** (ps_1_x, fixed function) keep `a_modulate2x` on the new texture: there every crystal would show coloured bars for 1.2 s. DXVK always takes the ps_2_0 path.
- **The light whip builder** copies `sw_light_saber_white.swh` from its base, and asserts its stock 0.06 s life. On this O14 it must read the stock file with `o14.stock_file(STOCK_SWH)`. I asked the light whip session.

## ~8:45 PM: "the ghostfire crystal also has no trails on the whip hilt"

**Built, not installed (8:54 PM):** O14 `b60189b74ce2406caff787b6a8414d535393d0ea5dab554d1a68ab052663f34e`; two builds give the same hash. The light whip session is asked to rebuild its step on it, with the whip's trail row on the new ghostfire trail. Its chain hash goes to the main session.
- **What I checked:**
  - The whip has `tr1e` at 2.025 m in its LOD and every mesh.
  - Its colour follows the crystal, so the server treats it as a Jedi weapon and starts the shimmer task. The run 37 binary (7:32 PM) is newer than the task's sources (5:30 PM).
  - The ribbon effects are in the archive. The whip's transparent trail uses its own shader and texture, so it can't hide the ribbons.
  - **The one gate:** the task plays the tip ribbons only while the wielder is in combat. Out of combat the ghostfire whip has no trail at all, because its own trail is transparent.
  - Nothing else whip-specific could be checked without the game.
- **The fix, client only:** a trail that draws only for the ghostfire crystal (`appearance/sw_ghostfire_trail.swh`, `shader/sw_ghostfire_trail.sht`, `effect/ghostfire_trail.eft`, `pixel_program/ghostfire_trail_ps20.psh` from `ghostfire_trail_ps20.hlsl`, 21 slots).
  - A trail row with UseObjectHue 1 hands the crystal's palette colour to the trail as its vertex colour; the vertex program copies it unchanged.
  - The program draws the oil-slick strobe bars for ghostfire, (0x20, g, 0x20) with g below r, and nothing for any other crystal. That keeps the whip's rule, "the trail; none without a specific crystal".
  - It's the saber trail layout at 1.2 s and full alpha.
  - Only the shader-model-2 path is gated; older cards would draw the bars in any crystal's colour.
- **Palette:** entry 40 is now (0x20, 0x1e, 0x20) instead of grey (0x20, 0x20, 0x20). A white crystal's trail can then never pass for ghostfire, even if a trail darkens its colour as it fades. The blade program and its mirage id `0ea2a331` are unchanged, and every ghostfire channel is still 0.17 or less.
- The same trail could later serve every crafted saber, once test saber B shows how the stock trail lays out its texture (normal crystals would then need their stock look instead of nothing).

## Any hilt (owner, 18 Oct ~8:15 PM)

The owner said: "id def prefer not using singular hilts for this, being able to swap is important to player agency". The ghostfire blade already follows the crystal in any stock hilt, through the shared blade shader. The server's tip ribbons follow it too. The stacked-copies trail is still tied to the Ghostfire Lightsaber's own trail row. Next step: move it onto the shared saber trail (`sw_light_saber_white.swh`, every crafted saber), drawn only for the ghostfire crystal's colours.
- The trail's effect multiplies its texture by the vertex colour, which carries the crystal's colour (`e_particle_emisadd_2x.eft`, `a_modulate2x.psh`). So a trail shader can tell the ghostfire crystal apart, like the blade shader does.
- To keep normal crystals' trails short while the ghostfire trail lingers, the shader needs to know how the trail lays out its texture along its length, and which end is the newest. That's unknown.
- **Test saber B is now the diagnostic:** the stock saber trail file itself, with full colour and 1.2 s life, and a texture that is white for the first 8% along the trail, then red, yellow, green, cyan, blue and violet. One swing in a capture shows the layout and the direction.

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

Done: the archive at 8:07 PM (above). The test saber B Lua (`server/strobe-test-dev.patch`) is in dev as `e6e6d3bb` and loaded in run 37.
For a later rebuild:
1. Archive in both places, by rename at `/opt/swg/tre`; back up the file it replaces (now `b9fbc48a`). Chain on `b9fbc48a`'s parts: O14's `--base` is `c8a61080`, then the light whip step.
2. Client data only needs no restart; a Lua change does.

## Please look at these (your own words)

1. Any saber with the ghostfire crystal: is the blade almost nonexistent now, or still too visible?
2. A normal crystal in any saber: does it look the same as before?
3. Spawn `/server loot item ossus_ghostfire_saber 1` (A) and `/server loot item ossus_ghostfire_saber_b 1` (B). Put the ghostfire crystal in each, and swing slowly, then fast. Which one leaves copies of the blade, and how long do they stay?
5. Is the red light on the creature and your robe still there? Which crystal was in the saber when you saw it, if any?
6. After the 7:50 PM changes: are the trails now a dark petrol sheen, or too faint? Which test saber left the fan of copies, A or B?
7. Test saber B (diagnostic): swing it slowly once while a capture runs. That's all I need from it.
4. With the ghostfire crystal: how do the oil-slick colours and the 1.2 s tip ribbons look next to the strobe trail? Dark enough, or too dim to see?
