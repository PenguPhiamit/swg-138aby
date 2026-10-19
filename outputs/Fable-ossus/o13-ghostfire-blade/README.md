# Ossus O13: a ghostfire lightsaber with its own blade, trail and hum (Claude, 18 Oct 2026)

Owner, 18 Oct: the ghostfire saber should be "damn near invisible with an opalescent sheen", leave "LSD trails", and use a custom shader.

**Installed on the test galaxy, 18 Oct 5:55 PM (run 35), untested in game.** Owner, 5:50 PM: "Install it get the test server up and ill look at it." Ossus stays closed for the friends launch, so this goes to the test galaxy only.

- **Installed archive: `c8a61080`.** It chains the archive that was installed then, `2ee1799f` (the main session's lsd2 step: half-brightness blade, eight synced ribbons), with the O12 rain byte (`912f48fd`, made with `build_ossus_rain.py --base`), then this step (`--base` that file). Backups are `.bak-2ee1799f` on the client and at `/opt/swg/tre`. The 5dd26325 build below, made on the rain-fix archive alone, was not installed: it lacks lsd2.
- **Dev `03c180d4`** has the Lua patch. `checks-blade.json` is from the installed build.

**Crystal or hilt?** In stock SWG the crystal sets the colour: it picks one entry in the blade palette. The saber object picks the blade file, and every stock blade file uses the same shader, so the crystal looks like the only thing that matters. A palette entry can only tint that shared shader, and it can't touch the white core, so a crystal alone can't make a blade near-invisible or opal. That's why this look comes with its own saber. The ghostfire crystal in an ordinary saber keeps the dim tint. The question about a different crystal in this saber asks whether it should still look ghostfire (as built) or take that crystal's colour.

## Why the blade drew white (read from the client files)

- Every stock blade file (`appearance/*.lsb`) uses `shader/lightsaberblade.sht`. That file is a switching shader: four frames, 1/16 s each, `lightsaberblade_a..d.sht`.
- Each frame uses the stock effect `e_h_lightsaberblade.eft`. Its pixel program (the HLSL source is inside the `.psh`) works out `rgb = texture.rgb * crystal colour + texture.a`, blended additively.
- The texture's alpha is a "white-hot core" added **after** the crystal's tint. So no palette entry could make the ghostfire blade dim or opal: the core stays full white.
- The fix needs no new effect or pixel program, only textures and shader files of our own. No stock file changes, so every other saber stays as it is.

## What the archive adds (`build_ghostfire_blade.py`)

| File | What it is |
|---|---|
| `texture/ghostfire_blade_0..7.dds` | 8 frames, 256x64 uncompressed (stock uses this format in about 900 files). They keep the stock blade's shape. The white core is cut to 10% and the glow to 32%, filled with milky pastel opal bands and soft coloured sparks. The bands drift along the blade. |
| `shader/ghostfire_blade_0..7.sht` | The stock frame shader on those textures, without its palette part. The texture alone sets the look, and the crystal does not tint it. |
| `shader/ghostfire_blade.sht` | A switching shader: 8 frames at 0.1 s, so the sheen loops every 0.8 s. It runs in the client, with no server messages. |
| `sound/ghostfire_idle.snd` | The stock idle hum with its volume pair at 25%. The volume field is a guess: they are the only two 1.0 values in the file. |
| `appearance/wp_mle_sword_lightsaber_blade_ghostfire.lsb` | The sleek silver one-handed blade file (hilt, light, length) with the shader and hum above. |
| `object/.../shared_sword_lightsaber_one_handed_ghostfire.iff` | The s12 gen4 one-handed saber template with that appearance. The server reads it from the archive too. |
| `texture/sw_ghostfire.dds`, `shader/sw_ghostfire.sht`, `appearance/sw_ghostfire.swh` | The swing trail: a pastel rainbow ribbon in the stock saber trail file, with only its shader changed. |
| `datatables/weapon/swoosh.iff` | Adds a row: the ghostfire template gets `sw_ghostfire.swh` with UseObjectHue 0, so the crystal doesn't dim the trail. |
| `misc/object_template_crc_string_table.iff` | Adds the template's CRC, `b1192eb6`. |

- **Base:** `work/ossus-rain/local_planets-ossus-rain.tre`, `fbdf58e8…` (the O12 rain fix, not installed yet).
- **Out:** `work/ossus-ghostfire-blade/local_planets-ghostfire-blade.tre`, sha256 `5dd26325…` (in the `.sha256` file; two builds give the same hash). It has 373 entries: 348 stay byte for byte, the CRC table changes, and 24 are new.
- **Checks:** `checks-blade.json`.
- **Previews:** `preview-blade-dark.png` and `preview-blade-day.png` (all 8 frames, blended the way the game blends them) and `preview-trail.png`, next to the archive.
- **Settings:** `--glow`, `--core` and `--hum` (0-1) rebuild it brighter, dimmer or quieter.

## Server half (`server/ghostfire-saber-dev.patch`, Lua only, no C++ build)

Made by `server/make_ghostfire_saber_patch.py` from Core3-dev HEAD `2687887a`. It passes `git apply --check` on the dev tree, and `luac -p` passes on all 8 files.
- It adds the shared and server templates (`sword_lightsaber_one_handed_ghostfire`, a renamed s12 gen4 one-handed saber: gen4 certification and crafting ranges).
- It adds the loot item **"Ghostfire Lightsaber"**: fixed stats from the middle of the gen4 crafting ranges (150-250 damage, speed 4.3, Force cost 51), plus its group.
- The keeper now gives the crystal **and** the saber, which needs two free slots. A character who finished the quest before gets the saber on the next visit.
- It does not touch `CombatManager.cpp` or `GhostfireShimmerTask.h`, which have the trail-step work uncommitted in the dev tree.
- Like any saber, it lights only with a colour crystal in it.

**Install order (main session, server lock, owner off the game):**
1. Install the archive in both places (`SWG-client/local_planets.tre`, and `/opt/swg/tre/local_planets.tre` by rename). It includes the rain fix.
2. Apply the patch to Core3-dev.
3. Restart the test galaxy. Lua only, so no build.

**Staff shortcut for the first look:** `/server loot item ossus_ghostfire_saber 1`. Then tune the ghostfire crystal into it.

## Now versus O13

| | In effect now (installed `dc07e0b9` + dev `2687887a`) | O13 (this build) |
|---|---|---|
| Which sabers | Any saber with the ghostfire crystal | Only the Ghostfire Lightsaber. The crystal in any other saber keeps the "now" look. |
| Blade | Stock blade tinted by dim palette 32. The server steps it through 33-40. The full-strength white core still shows, so it reads as a dim white blade. | Its own texture: the core at 10%, faint opal bands and sparks drifting along it. Close to invisible in daylight, a pastel glow at night. |
| Shimmer | The server changes the colour index every 0.7 s (150 ms in the trail step being built). | 8 texture frames in the client, a 0.8 s loop, no server traffic. |
| Trail | The stock trail tinted by the dim palette (barely shows), plus server-played ribbon effects at the feet or hilt (the tip in the step being built). | Its own swing trail, a pastel rainbow ribbon that follows the blade like the stock trail. Not tinted by the crystal. |
| Hum | Stock | The stock hum at about 25% |

The two can run together. With the ghostfire crystal in the new saber, the shimmer task still runs but has no visible effect on this blade, and the server ribbons would play on top of the new trail.

## Please look at these (answer in your own words)

1. Does the saber appear in your hand with its hilt and a blade? If the client crashes or the blade is missing, say when it happened.
2. Turn it on at night and in daylight. What do you see, and do the colours move?
3. How visible is it: too faint, about right, or too strong? (I can turn the glow and core up or down.)
4. Swing it. What does the trail look like next to the ribbon effects you saw before?
5. The hum: quieter, the same, silent, or odd?
6. Should another colour crystal in this saber still look ghostfire (as now), or tint it?
7. The hilt is the sleek silver one, and the saber needs the gen4 one-handed certification. Would you like a different hilt or a lower tier?

## Unknowns until tried

- Whether the client takes our new template and blade file on the first try (the formats are copied from stock files, and every file round-trips).
- Whether the two 1.0 values in the hum file really are its volume.
- Which way the trail's rainbow bands run (across the ribbon or along it).
