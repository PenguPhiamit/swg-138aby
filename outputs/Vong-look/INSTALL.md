# Vong look test: what is staged and how to install it

Claude, 17 Oct 2026, 9:09 AM. **Staged only: nothing is installed, nothing has run on a galaxy, and it is untested in
game.**

**What it is.** The owner's pick on 17 Oct: "Mix: bone + s02 collar", no helmet. One Vong warrior stands at the Ossus
Project fields (POI 7) for the owner to look at. Patrols come after that look.

The plan and history are in `Documentation-support/vong-look-test.md`.

## Fix 1 (17 Oct, after the owner's first look): the warrior's body. `vong-look-body-fix.patch`

**What the owner saw** (run 29, client and server archive `beb06d28`): "the vong is just a fat human".

**Cause, found in the client's data files** (Claude, about 12:35 PM): the warrior's body,
`object/mobile/human_male.iff`, names the client data file
`clientdata/npc/client_shared_npc_dressed_commoner_fat_human_male_02.cdf`. From that file the client itself builds a
fat commoner:
- `MESH` hair `hum_m_hair_s18`, `jacket_s11_m`, `pants_s13_m` and `shoes_s01_m`;
- body blends including `/shared_owner/blend_fat` 204 of 255;
- skin index 41.

The server's shared template also scales that body randomly from 1 to 1.12, on top of our 1.15.

The Mos Taike guards wear a full stock armour outfit (padded) on `object/mobile/mos_taike_guard_old.iff`. That body
uses the generic `client_shared_npc_human_m.cdf`, which has only sounds and footstep effects: no clothes, no hair, no
blends. The guards' hair comes from their outfit (`hair_human_male_s23`), so the body itself is bald.

**Ruled out first:**
- the slots (`human_male` has the same `abstract/slot/descriptor/player.iff` as the guards, and our pieces use the
  stock arrangements such as `wearables/bicep_l.iff`);
- `playerRaces` (Core3 checks it only for players, in `PlayerContainerComponent`);
- the client chain: its CRC table comes from `local_planets.tre` `beb06d28` with our 8 rows, and every Vong template,
  appearance, shader and texture resolves there;
- server errors: none in `/opt/swg/testgalaxy/console.log` about vong, outfits or templates.

**The fix:** in `mobile/sandbox/ossus_vong.lua`, `templates = {"object/mobile/mos_taike_guard_old.iff"}`. That is one
line plus a comment, Lua only, and needs no client change. `git apply --check` passes on Core3-dev `4906d2eb` (read
only), and `luac5.3 -p` passes. `tools/stage_server.py` now writes the same body.

**Install (lock holder):** apply the patch on dev, commit, run `check_lua.py`, and restart the test galaxy.

**Then ask the owner openly** what they see. **Still untested:** whether our armour pieces draw. This is the most
likely cause, not a proven one. If the armour is still missing on the new body, the next check is a bot next to the
warrior, listing the objects contained in it (`AgentControl::onContainment`), to see whether the server equips the
eight pieces at all.

## Client: `tools/build_vong_client.py`

It chains on the installed archive `work/nal-hutta-life/local_planets-nalhutta-life.tre` (sha256 `b01e9f44...`, the one
named on the board's server-lock line and the same file as `SWG-client/local_planets.tre`).

- **Candidate:** `work/vong-look/local_planets-vong-look.tre`,
  **sha256 `185b3d7ff558f95a39aa47ae07ec8769aa9ae36cf6dd6d1b5120d3972ad23196`**, 332 entries.
- **The base's other 200 entries** come through byte for byte. Two runs give the same bytes. Checks:
  `Vong-look/checks-client.json`.

| Entries | What |
|---|---|
| 8 object templates `object/tangible/wearables/armor/vong/shared_armor_vong_s01_{bicep_l,bicep_r,bracer_l,bracer_r,boots,gloves,leggings}.iff`, `.../armor/vongcrab/shared_armor_vongcrab_s02_chest_plate.iff` | the stock bone s01 and marauder s02 templates with their appearance renamed |
| 16 `.sat`, 16 `.lmg`, 64 `.mgn` (both genders, LODs 0-3) | the stock meshes with only the shader names inside renamed. The geometry, skeleton weights and the human skeleton are stock |
| 10 shaders `shader/armor_vong_*` (incl. `_sm`) | the stock bone shaders with our colour texture as MAIN |
| 5 shaders: `armor_vong_leggings_waist_hcsb21`, `armor_vongcrab_chest_s02_{hcsb21,hcsb21_sm,hue_hc8,hue_hc8_sm}` | as above, plus colour 0 rebound to `palette/white.pal` index 0. It was wr_metal 0 on the waist, and wr_metal 61 (olive brown) and wr_cloth_general 120 on the chest |
| 12 textures `texture/armor_vong_*.dds`, `armor_vongcrab_chest_s02*.dds` | ours, from `convert_vonduu.py`: swatch 12 baked onto the stock UVs, DXT5, alpha 0 (the shaders' hue mask), the stock sizes and mip counts |
| `misc/object_template_crc_string_table.iff` | + 8 rows (29,367 rows) |

**What the builder checks:**
- Every swap is same-length, with its count asserted, and the differing bytes are counted: the 114 swap-only files
  differ from stock only in the renamed letters.
- Every file round-trips through the IFF parser.
- Every path the new files name resolves, in the archive, the base or the client.
- None of the new names already exists.

Kept stock and referenced by name, so not shipped: the normal maps, the lookup textures, the effects, and the marauder
chest's chainmail shader.

## Server: `vong-look.patch` (sha256 `816c4457...`, 20 files, +1,534)

Against Core3-dev `91cf87ed`. `git apply --check` passes there (run read-only as swgemu) and `luac5.3 -p` passes on all
20 Lua files. `tools/stage_server.py` regenerates it from copies of the dev files (each edit needs its anchor exactly
once).

| Change | What |
|---|---|
| `object/tangible/wearables/armor/vong/`, `.../vongcrab/` (`objects.lua`, `serverobjects.lua`, 8 server templates) | the stock bone and marauder templates renamed; stock stats; names and descriptions still the stock strings ("Bone Armor ...") |
| `object/allobjects.lua`, `object/tangible/wearables/armor/serverobjects.lua` | 2 includes each |
| `mobile/outfits/vong_fanatic_warrior_outfit.lua` (+ include) | the 8 pieces, no customization |
| `mobile/sandbox/ossus_vong.lua` (+ include in `mobile/serverobjects.lua`) | `vong_fanatic_warrior_look`: the plain `object/mobile/human_male.iff` body (as `mobile/thug/brigand.lua`), our outfit, scale 1.15, not attackable (INVULNERABLE), no faction, unarmed |
| `screenplays/sandbox/ossus_vong_look.lua` (+ include in `screenplays.lua`) | `OssusVongLookScreenPlay`: one warrior at POI 7 (1400, 4900) on Ossus, on the ground (`getWorldFloor`), heading 200 |

## Install order (for the session holding the server lock)

1. **The owner's OK** for a client archive change, as for every archive so far.
2. **If another archive was installed after `b01e9f44`,** rebuild on it first:
   `C:/Users/Pengw/miniconda3/python.exe -I outputs/Vong-look/tools/build_vong_client.py --base <that archive>`. It stops
   on its own if a name clashes. The textures must already be staged (`convert_vonduu.py`, see below).
3. **Back up the current archive** on the server and in the client (the `.bak-<sha>` convention). Then copy the
   candidate over `local_planets.tre` on both sides. The server needs it before the patch: Core3 reads each new
   wearable's client `.iff` from its own TRE list.
4. **Apply the patch:** `git -C /opt/swg/Core3-dev apply --check .../Vong-look/vong-look.patch`, then apply it, commit on
   dev and run `check_lua.py`. It is Lua only, so no C++ build is needed.
5. **Restart the test galaxy.** The standing OK covers this only with no owner client running and no squad round in
   progress.

**Rebuilding the textures:** `python_embeded\python.exe -I Vong-look/tools/convert_vonduu.py 0.7
Vong-look/tools/spec_mix.json Vong-look/bake_mix`. The bakes come from `bake_vonduu.py ... spec_mix.json`. The staged
DDS files are gitignored.

## Checks after install (untested so far)

- **Server log:** no "null outfit group vong_fanatic_warrior_outfit", no template errors for `armor/vong` or
  `armor/vongcrab`, and no `OssusVongLookScreenPlay` error.
- **Owner in the client** (Ossus, waypoint 1400, 4900, test galaxy):
  - **Ask openly:** what do you see? Don't use prefilled answers.
  - **Things to watch:** whether the armour draws, the colours (dark crab shell, no olive tint on the chest), the
    spiky collar, and seams between pieces.
  - **Also:** the head and hair from the plain human body (the warrior is bare-headed), the height, and whether any
    piece is missing or invisible.
- **If the armour shows black, missing or an error texture,** look first at texture orientation. The bake's UV
  orientation was proved against the meshes' raw UVs; DDS row 0 = top is the one remaining assumption.

## Known limits and next steps

- **Item names** are the stock "Bone Armor ..." and "Marauder ..." strings. Our own names come with the patrols.
- **Bare head:** whatever face the human body gives. A bald, pale (light grey to white) head with tattoos and blue eye
  sacs is a later head-texture job (Wookieepedia: grey most common, yellow second; Zenoc Quah light grey with black
  tattoos).
- **Unarmed:** an amphistaff look comes later.
- **No faction yet:** the `vong_fanatic` side, the patrols, levels and loot come after the owner's look.
- **The real goal (owner, 17 Oct):** our own Vong body: a TRELLIS.2 draft from a concept image, rigged to the human
  skeleton.
