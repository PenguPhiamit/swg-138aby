# Light whip step 1: the stiff whip (L1, Claude, 18 Oct 2026)

Owner, 18 Oct ~7:05 PM: "build step 1 of the light whip: the whip hilt template, the long thin blade with its own shaders and trail, and the server saber template with loot and schematic. Built, not installed."

The stiff whip is a straight 2.5 m strand. Later it is the fallback for anyone without the graphics hook, once the bending whip (step 3) exists. Design and later steps: [lightwhip-design.md](../Documentation-support/lightwhip-design.md).

**On the test galaxy since 18 Oct 7:42 PM (run 37).** Owner, 7:26 PM: "Install the light whip archive (with O14) and the Lua patch on the test galaxy and restart it." The archive is on the client and at `/opt/swg/tre` (backups `.bak-c8a61080`). Dev `e6e6d3bb` has O14's test-B Lua, and `9d08e265` has the whip's. The server log shows no new warnings or errors, and the whip's schematic is in the database.

- **Run 36** (7:33 PM) had `d424d2f6`, built on the older O14 `892475a4`. **Run 37** has `a2610d64`, built on the current O14 `feb3bf84`; the main session caught the old base.
- **Owner's first look:** "whip doesnt bend". That's expected, since this is the stiff whip and bending is step 3. On the colour ("the same color as the ghostfire? not wuite what i wanted") they picked "keep as built": the crystal decides, and the ghostfire crystal gives the near-invisible ghostfire blade.

## Client archive (`build_lightwhip.py`)

- **Out:** `work/lightwhip/local_planets-lightwhip.tre`, sha256 `a2610d64…` (full hash in the `.sha256` file). Two builds give the same hash.
  - 409 entries: 386 unchanged, 4 changed, 19 new.
  - Checks are in `checks-lightwhip.json`.
- **Base:** the O14 archive `feb3bf84`. Installing this archive installs O14 too.
- **What it adds:**

| Files | What they are |
|---|---|
| `appearance/wp_mle_lightwhip.apt`, `lod/…lightwhip.lod`, `mesh/…lightwhip_l0..2.msh` | The leather-grip one-handed hilt. The trail's tip hardpoint `tr1e` moves from 1.125 to 2.425 m, and the mid-blade `whp1` from 0.75 to 1.5625 m, so the trail covers the whole strand. |
| `appearance/wp_mle_lightwhip_blade.lsb` | That hilt with a 2.5 m blade (saber 1.2 m), 0.09 m wide (saber 0.15). Stock hum, ignite and retract values. |
| `shader/lightwhipblade.sht`, `…_a..d.sht` | The stock blade shaders on the whip's own effect. Stock textures, and the crystal still sets the colour. |
| `effect/e_h_lightwhipblade.eft`, `pixel_program/e_h_lightwhipblade_ps20.psh` | The blade program: the O14 one (ghostfire included), with the white core at 75% so a thin strand shows more of the crystal's colour. Its id is `238eb66a`, against stock `acc853c5` and O14 `fac25b60`. The hook's `blade_ids.h` still lists the old O14 id `7b68e0f1`. The O15 hook can find whip blades by that id. |
| `appearance/sw_lightwhip.swh` | The stock saber trail, lasting 0.25 s (saber 0.06 s), tinted by the crystal. |
| `object/…/crafted_saber/shared_sword_lightwhip.iff` | The s5 gen4 one-handed saber template with that blade, named "Lightwhip" with its own description. |
| `object/draft_schematic/…/shared_lightsaber_lightwhip.iff` | The gen4 one-handed saber schematic, making the whip. |
| `object/tangible/loot/loot_schematic/shared_lightwhip_schematic.iff` | "Lightwhip Schematic", a handheld viewscreen like the Geonosian schematics. |
| Changed: `swoosh.iff`, the CRC table, `weapon_name`, `weapon_detail`, `craft_weapon_ingredients_n` and `_d` | The trail row, the three template CRCs, and the names and descriptions in our own words. |

Every file the whip refers to was traced (44 files), and none is missing.

Settings: `--length`, `--width` and `--trail` rebuild it longer, thinner or with a longer trail.

## Server half (`server/lightwhip-dev.patch`, Lua only, no C++ build)

Made by `server/make_lightwhip_patch.py`, first on Core3-dev `6d544cf3`. For the install it was re-made on `e6e6d3bb` (O14's test-B Lua) and committed as dev `9d08e265`. `luac -p` passes on all 15 files.

- **Saber template `sword_lightwhip`:** the s5 gen4 one-handed saber.
  - More reach: ideal range 3 → 5 m, max range 5 → 7 m. The saber specials use the weapon's range.
  - Weaker against armour: armour piercing MEDIUM → LIGHT.
  - Unchanged: gen4 certification, crafting ranges and the crystal slots.
- **Draft schematic `lightsaber_lightwhip`:** the gen4 one-handed saber schematic making the whip, with the same skills, ingredients and experimentation. It is listed in `managers/crafting/schematics.lua`.
- **Loot schematic:** teaches that schematic for 3 crafts. It needs `force_discipline_light_saber_master`, the skill that grants the gen4 saber schematics.
- **Loot items:** `lightwhip` (fixed mid-range gen4 stats, like the Ghostfire Lightsaber) and `lightwhip_schematic`.
- **Loot group `lightwhip_nightsister`:** schematic 80%, finished whip 20%. No creature drops it yet; that is step 4.
- Not in this patch: weaker blocking and the parry slip. Both need C++ (step 2).

## Install (main session, server lock, owner off the game)

1. Install the archive in both places (`SWG-client/local_planets.tre`, and `/opt/swg/tre/local_planets.tre` by rename). Back up `c8a61080` first. This also brings in O14.
2. `git apply` `server/lightwhip-dev.patch` in Core3-dev. If the O14 strobe-test patch goes in first, re-run the generator so the include lines stay right.
3. Restart the test galaxy. Lua only, so no build.

**Staff shortcuts:** `/server loot item lightwhip 1` and `/server loot item lightwhip_schematic 1`. Like any saber, the whip lights only with a colour crystal in it.

## Please look at these (your own words)

1. Does the whip appear in your hand with its hilt, and does the blade come on? If anything crashes or is missing, when did it happen?
2. The strand: how long and how thin does it look, standing and in combat? Does it go through the ground on low swings?
3. The trail: what does a swing leave behind?
4. Names: what do the whip and the schematic call themselves, and what do their descriptions say? (A blank or odd name means the strings didn't load.)
5. On a Jedi with Light Saber master: can you learn the schematic, and does crafting make a whip?
6. Reach: does attacking from 6-7 m work?
7. A normal crystal, then the ghostfire crystal: what colour is the strand?

## Unknowns until tried

- What the ignite and retract values mean. If they are a speed, the longer blade takes about twice as long to unfurl.
- Whether the server accepts an empty `additionalTemplates` in a saber schematic. Other schematics use it.
- Whether 2.5 m is the right length next to the combat animations.
