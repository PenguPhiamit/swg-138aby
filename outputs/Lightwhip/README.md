# Light whip step 1: the stiff whip (L1, Claude, 18 Oct 2026)

Owner, 18 Oct ~7:05 PM: "build step 1 of the light whip: the whip hilt template, the long thin blade with its own shaders and trail, and the server saber template with loot and schematic. Built, not installed."

The stiff whip is a straight 2.1 m strand (2.5 m until the owner's 8:26 PM answers). Later it is the fallback for anyone without the graphics hook, once the bending whip (step 3) exists. Design and later steps: [lightwhip-design.md](../Documentation-support/lightwhip-design.md).

**On the test galaxy since 18 Oct 7:42 PM (run 37); archive `b8b59aca` since 9:04 PM** (installed by the main session on the client and at `/opt/swg/tre`; backups `.bak-23368576`; board commit `65ff724`). The boss-drop and schematic-rule patch is still not applied (owner: "Later"). Owner, 7:26 PM: "Install the light whip archive (with O14) and the Lua patch on the test galaxy and restart it." The archive is on the client and at `/opt/swg/tre` (backups `.bak-c8a61080`). Dev `e6e6d3bb` has O14's test-B Lua, and `9d08e265` has the whip's. The server log shows no new warnings or errors, and the whip's schematic is in the database.

- **Run 36** (7:33 PM) had `d424d2f6`, built on the older O14 `892475a4`. **Run 37** has `a2610d64`, built on the current O14 `feb3bf84`; the main session caught the old base.
- **Owner's first look:** "whip doesnt bend". That's expected, since this is the stiff whip and bending is step 3. On the colour ("the same color as the ghostfire? not wuite what i wanted") they picked "keep as built": the crystal decides, and the ghostfire crystal gives the near-invisible ghostfire blade.

## The owner's answers (8:26 PM, via the main session) and the rebuild

- **Hilt:** "the hilt it has now for now". The leather hilt stays.
- **Length:** "a little shorter then it is now to start". Now 2.1 m, with `tr1e` at 2.025 m and `whp1` at 1.3125 m.
- **Trail:** "none without a specific crystal". The default is now no visible trail: the whip's trail file draws a transparent texture. The ghostfire crystal still brings its server-played ribbons, because `GhostfireShimmerTask` runs on any Jedi weapon and plays at the `tr1e` tip.
- **Drop:** "Krayt dragons for now, the boss". Only the rotation's two krayt bosses (Ghost-Scale the Canyon Krayt, `giant_canyon_krayt_dragon`; Old Rattlebones, `krayt_dragon_ancient`), at 10% per kill.
- **Schematic:** "Master weaponsmith +saber crafting 1 or 2 or jedi master". The skill names are found but not wired yet; see the design note.
- **Ghostfire:** "the ghostfire almost looks better in the whip". The whip keeps its own ghostfire values (O14 `feb3bf84`'s 3.5% glow, 0.6% core) rather than O14's newer take.
- **Final chain for the joint swap (owner: "Wait for both"):** `b8b59aca…` on O14 `a0cca018`, which ties the ghostfire trail to the crystal in any hilt (418 entries; two builds give the same hash). Installed at 9:04 PM.
  - O14 now overrides the shared saber trail, so the builder reads the stock `sw_light_saber_white.swh` from the client's own archives.
  - O14's override stays in the chain untouched. The whip's row still points at `sw_ghostfire_trail.swh`.
- **Trail fix, 8:45 PM.** Owner in game: "the ghostfire crystal also has no trails on the whip hilt". Rebuilt as `5a67358f…` on O14 `b60189b7` (413 entries; two builds give the same hash). Built, not installed.
  - The whip's swoosh row now points at O14's ghostfire-only trail, `appearance/sw_ghostfire_trail.swh`, with UseObjectHue 1. Its program draws the strobe bars for the ghostfire palette (32-40) and nothing for any other crystal.
  - Only the shader-model-2 path is gated. On ps_1_x or fixed-function graphics the bars would show tinted by any crystal; DXVK always takes the first path.
  - The transparent "none" trail files are left out now; `--trail none` still makes them.
- **Before that, rebuilt and installed:** `23368576…` on O14 `4c5a29d0` (412 entries). Two builds give the same hash. It replaces the main session's chain `49d6ae99`, which is the same builder with the old settings on `4c5a29d0`.
  - The main session installed it at 8:35 PM with the owner's OK ("Install now (Recommended)"), on the client and at `/opt/swg/tre`, by rename. Backups are `.bak-49d6ae99` in both places.
  - It's client data only, so run 37 kept running.
- **Schematic rule (owner's pick, 8:3x PM):** "Smith + Tech I, or LS Master", that is (`crafting_weaponsmith_master` and `force_discipline_light_saber_technique_01`) or `force_discipline_light_saber_master`.
  - It's done as a Lua menu, `LightwhipSchematicMenuComponent` in `screenplays/sandbox/lightwhip_schematic_menu.lua`. It checks the rule, teaches the schematic for 3 crafts, then uses the notes up.
  - Its `requiredSkill` is empty, because the stock menu takes one skill only.

## Scope (owner, 18 Oct about 8:20 PM, changed 8:3x PM)

- **Now:**
  - **The bend** (steps 0 and 3). It goes to the mirage session, which owns the O15 hook. Owner: "can we wait on the parry thing in favor of the bend?"
  - **Drop: the krayt bosses only, plus the schematic rule.** `server/lightwhip-boss-drop-dev.patch` (made by `server/make_boss_drop_patch.py`), built, not applied. Both go in at the next test galaxy restart, which needs the owner's OK.
    - A slain krayt boss of the world rotation (2 of the 14 in `sandbox_world_bosses.lua`, marked `lightwhip = true`) has a 10% chance to give one random player who damaged it a roll of `lightwhip_boss`: the schematic 80%, a finished whip 20%. It goes into their inventory, or the next player's if that one is full.
    - The bosses' stock templates are untouched, so ordinary creatures never drop it.
    - The patch renames the group from `lightwhip_nightsister`, and it adds the Lua menu with its include line.
    - It passes `git apply --check` on dev `9d08e265`, and `luac5.3 -p` passes on all 6 files.
    - Untested: the Lua menu replaces the stock menu without calling it, as the radiation sensor's Lua menu does on another inventory item.
- **After the 22 Oct reset:** step 2, the parry slip and weaker blocking (its options are in the design note, and no C++ is written), and step 4, an original hilt and crack sound.

## Client archive (`build_lightwhip.py`)

- **Out:** `work/lightwhip/local_planets-lightwhip.tre`, sha256 `23368576…` (full hash in the `.sha256` file). Two builds give the same hash.
  - 412 entries: 4 changed and 21 new, against the O14 base.
  - Checks are in `checks-lightwhip.json`.
- **Base:** the O14 archive `4c5a29d0`. Installing this archive installs O14 too.
- **What it adds:**

| Files | What they are |
|---|---|
| `appearance/wp_mle_lightwhip.apt`, `lod/…lightwhip.lod`, `mesh/…lightwhip_l0..2.msh` | The leather-grip one-handed hilt. The trail's tip hardpoint `tr1e` moves from 1.125 to 2.025 m, and the mid-blade `whp1` from 0.75 to 1.3125 m, so the trail covers the whole strand. |
| `appearance/wp_mle_lightwhip_blade.lsb` | That hilt with a 2.1 m blade (saber 1.2 m), 0.09 m wide (saber 0.15). Stock hum, ignite and retract values. |
| `shader/lightwhipblade.sht`, `…_a..d.sht` | The stock blade shaders on the whip's own effect. Stock textures, and the crystal still sets the colour. |
| `effect/e_h_lightwhipblade.eft`, `pixel_program/e_h_lightwhipblade_ps20.psh` | The blade program: the O14 one (ghostfire included), with the white core at 75% so a thin strand shows more of the crystal's colour. Its id is `238eb66a`, against stock `acc853c5` and O14 `0ea2a331` (`4c5a29d0`). The hook's `blade_ids.h` still lists the old O14 id `7b68e0f1`. The O15 hook can find whip blades by that id. |
| (trail) | Default: the swoosh row points at O14's `appearance/sw_ghostfire_trail.swh`, so there's a trail only with the ghostfire crystal. `--trail none`: `sw_lightwhip.swh` on a transparent texture. `--trail S`: the stock trail lasting S seconds. |
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
