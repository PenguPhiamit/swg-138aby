# The photo studio: a test-galaxy shot set on one of SOE's test terrains — Fable, 15 Oct 2026

Staging only; nothing under `/opt/swg` written, nothing built or seen in a client. Purpose (owner, 15 Oct 15:25): a place
on the test galaxy where a species, a wearable, a prop or an NPC can be photographed the same way every time: fixed light,
no weather, no spawns, a marked pad, a backdrop, and a Universal Modder capture routine that produces the standard shot set.
**Verified** = read from the archives tonight with `tools/swgfmt`; **proposed** = design.

## 1. The four SOE test terrains (verified from `data_other_00.tre`; MTG 013 ships the same bytes)

| file | bytes | layout | size | water | layers / affectors | shader, flora, environment families |
|---|---|---|---|---|---|---|
| `terrain/character_farm.trn` | 801 | PTAT **0013** | 16,384 m | none | 1 layer: a constant height (`AHCN`) | **none at all** (empty shader, flora, radial, environment groups) |
| `terrain/simple.trn` | 2,271 | PTAT **0014** | 16,384 m | none | 5 layers: fractal height (`AHFR` + `FFRA` filter), a constant height (`ACCN`), rectangle/polygon/polyline boundaries, one exclusion (`AEXC`); 2 fractal families | **no shader families, no flora, no environment family** |
| `terrain/creature_test.trn` | 10,325 | PTAT **0013** | 4,096 m | none | 4 layers: fractal height, constant heights (`AHCN` x2), flora (`AFSC` x2, `AFDN`), polygon and circle boundaries | 1 environment family (`Family_0`, Tatooine patchy cloud tile); **no shader families** |
| `terrain/test_wearables.trn` | 146,908 | PTAT 0014 | 4,096 m | global water at **-2.5 m**, shader `water_test` | 1 layer with an environment affector (`AENV`); the bulk of the file is the 0014 water/seed maps | 1 environment family (`default`); **no shader families** |

Core3-dev `bin/conf/config.lua` lists `character_farm`, `creature_test`, `simple` and `test_wearables` among the commented-out
test zones (lines 105–125), so the server knows the names. None of the four is in the installed planet CRC table (the merged
table has `hutta`, `nalhutta`, `ossus`, `dungeon1–4`, `adventure1–2`, `tutorial`...), none has `datatables/environment/<name>.iff`,
`terrain/environment/<name>.iff` or `clientregion/<name>.iff` in any archive, and **none has a shader family**, so each would
draw its ground with no shader (expect white or black, possibly a client error). `test_wearables` was SOE's own studio (the
name says so) but is a 4 km water plane at -2.5 m: a floor exactly at sea level with test water.

## 2. Pick: the zone name `simple`, with our own terrain under it

Use **`simple`** as the zone (Core3 lists it; `0014` is the layout our Ossus builder writes and Core3 reads; 16 km leaves room
for several sets), but **ship our own `terrain/simple.trn`** in the test-session `local_planets.tre`, which shadows the stock
file the same way our Ossus and MTG files already do. Reasons: the stock test terrains have no shaders, no sky and no
regions, so every one of them needs the same four client files we would write anyway; writing the terrain too costs one
builder call (`Fable-ossus/tools/ossus_terrain.py` already emits a 0014 terrain with shader, flora, radial and environment
families from a Python description) and gives us a floor we control. `character_farm` is the alternative if a flat 16 km
plain with nothing else is wanted; it would still need the shader family added, which means writing the file, so there is
no saving.

**The studio terrain (proposed, 0014, 16,384 m, chunk 8 m, 2 tiles, no water):** one shader family only, a neutral mid-grey:
the stock `shader/tat_rock_dark_asb13`? no: choose a flat, low-contrast stock ground shader with no normal map so lighting
reads true; candidates to confirm in the archives: the Corellia road `shader/corl_road_...` or a packed-dirt shader we already
use on Ossus (`Fable-ossus/README.md` lists "packed dirt" among the nine families). No flora, no radials. Ground: one constant
height layer at **10.0 m** over the whole map (the Ossus builder's `AHCN`), plus a **pad** at (0, 0): a circle r 60 flattened
to exactly 10.0 m (it already is; the layer exists so the pad can later be raised 0.2 m with a second shader as a visible
disc), and a **compass**: four shader circles r 2 at 40 m north, east, south and west in a contrasting shader (the
Dantooine pink meadow grass from Ossus) so a photographer can stand on a marked spot. A second set 2,000 m east (2000, 0) for
vehicles and large props, same pattern with r 120. One environment family, `studio`, over everything.

**Sky and fixed light (proposed):** `terrain/environment/simple.iff` = Tatooine's `ENVM` (single sun, no night-sky flag) and
`datatables/environment/simple.iff` = one family x 5 weather rows copied from Tatooine's clearest row with the cloud shaders
blanked; **the colour ramps are the fixed-noon lever**: the environment rows name `terrain/colorramp/*` textures that map
time of day to light and fog colours (MTG's Nal Hutta ships its own `terrain/colorramp/nalhutta_test.tga`, which proves ramps
are per planet); a ramp that is the same colour across its whole width gives the same light at every hour. We write
`terrain/colorramp/studio_*.tga` with the Ossus TGA writer: ambient a neutral 0.45 grey, sun 1.0 warm white, fog colour =
sky colour, fog distance far. Until the ramp columns are confirmed (which row names which ramp; the environment table has 25
columns), the fallback is the server: Core3's planet time is galaxy time, so the first shots are simply taken at the same
server hour. Weather: the `simple` block in `planet_manager.lua` with `weatherEnabled = 0`.

**Backdrop and no-spawn region (proposed):** `managers/planet/simple_regions.lua`: one `RECTANGLE` over the whole map with
`NOSPAWNAREA + NOBUILDZONEAREA`, and `simple_studio` as a CITY circle r 200 at (0, 0) so the location line reads "Studio"
(`string/en/simple_region_names.stf`, ours). Backdrop = static objects placed with `/createSpawningElement spawn <template>`
(verified 15 Oct 15:05: it places statics and buildings; `/createCreature <object/mobile/...iff>` places NPCs). A straight
wall 20 m behind the pad (north): stock `object/static/structure/tatooine/shared_wall_pristine_tatooine_large_style_02.iff` x3
(the piece Darklight's Bilbousa uses), or the Corellian plain wall; a light-grey wall reads best against dark bodies, a dark
one (Naboo stone) against pale ones: place both sets, 60 m apart, two pads. Lamps: street lamps do not light dynamically in
this client, so "light" is the ramp above; lamps are props only.

## 3. The standard shot set

Subject on the pad centre facing **south** (toward the photographer's default spot): a player stands at (0, 0) after
`/teleport 0 0 simple`; an NPC is spawned with `/createCreature` while the spawner stands at (0, -3) facing north, which puts
the NPC at the spawner's position facing the spawner, so the spawner then steps back. Camera: the client's chase camera orbits
the player's own character with the right mouse button held and zooms with the wheel; for an NPC subject the photographer's
character is the camera rig: stand on a compass spot, face the pad, and use the camera's free look. Distances are in metres
of standing room, counted from the pad centre.

| shot | photographer at | camera | notes |
|---|---|---|---|
| front | south spot (0, -40) facing north | default pitch, zoom so the subject fills 70 % of the height | the reference frame for every species and wearable |
| three-quarter | south-east (28, -28) facing north-west | same zoom | the "box art" angle |
| side | east spot (40, 0) facing west | same zoom | tail length, silhouette |
| back | north spot (0, 40) facing south | same zoom | cloaks, backpacks |
| top | south spot, camera pitched to its maximum, zoom out two steps | the client caps the pitch short of straight down; good enough for footprint and tail | |
| close-up | south spot, zoom in until the head fills the frame | face, headdress, eyes | two more at the hands and the chest for gear |

The subject's own frame is recorded too: `/setDirection` does not exist in Core3, so the subject faces south by walking one
step south then stopping; an NPC faces its spawner. Each shot's file name: `<subject>_<shot>_<yyyymmdd-hhmm>.png`.

## 4. What Claude must do

1. **Zone:** add `simple` to `TEST_ZONES` in `tools/test_galaxy.py` (it writes `ZonesEnabled` and `backfillZones`); never the
   live `config.lua`. The `simple` block in `planet_manager.lua` (no travel point needed; staff reach it by `/teleport 0 0 simple`;
   a shuttle later if the owner wants to send a bot there); `simple_regions.lua` as above.
2. **Client, into the test-session `local_planets.tre`:** `terrain/simple.trn` (ours, section 2), `terrain/environment/simple.iff`,
   `datatables/environment/simple.iff`, `datatables/clientregion/simple.iff` + `string/en/simple_region_names.stf`, the colour
   ramps, and, if the planetary map should open there, a `misc/planet_crc_string_table.iff` row `simple` + `planet_n` "Studio" (the
   Ossus O1b writers do both). Loading screen: the generic tile.
3. **Set dressing script:** a staff macro file (`Documentation-support/studio-dressing.txt`, ours) with the
   `/createSpawningElement spawn` lines for the two walls and the four compass markers (small stock statics, e.g. the Corellian
   brazier Bilbousa uses), run once after a `--fresh` start, since the resumed copy keeps them.
4. **How to get there:** `/teleport 0 0 simple` as a staff character; the owner's test account has admin level on the test
   galaxy. Bots: `squad.py` has no studio scenario; a bot subject needs a `goto`/`teleport` wrapper (ChatGPT, if wanted).
5. **Capture routine (Universal Modder, owner at the PC, client running; `um win shot` is proven on the SWG client at
   1600x900 in about 2 s, 15 Oct 14:46):**
   - `um win shot --exe SwgClient_r.exe <out>\<subject>_front.png --scale 0.33` after each manual camera set-up; the scaled
     copy is for the chat, the full frame for the record. Six calls per subject.
   - Later, with the owner's OK for input each time (AGENTS.md: agents never drive the owner's client without it):
     `um win drive --proc SwgClient_r "focus" "key <F-key bound to a /teleport macro>" ...` to move between the compass
     spots, then a drag for the orbit (the WinDrive protocol has `click`, `key` and mouse moves; a right-button drag of a
     fixed pixel distance gives a repeatable orbit angle) and `um win shot`. One `.ps1`/`.sh` under `tools/studio/` that takes
     the subject name and writes the six files. Recording for a turntable: `um win record --exe SwgClient_r.exe --out <base>
     --seconds 20` then `um video mux` (both proven 15 Oct).
   - Screenshots go to Claude's scratchpad or `Fable-studio/shots/` (add to `.gitignore`: they can show the owner's character
     name) and the owner keeps copies.
6. **First subjects, in order:** the Hutt NPC (`/createCreature object/mobile/hutt_male.iff`) before and after the Level 1
   table (sit, dance, floater), then each Level 2 piece, then the Chiss/Nautolan/Togruta creation faces for the species
   README screenshots, then every Ossus and Hoth prop that has only been seen in the field.

## 5. Open points

- Which colour ramp columns the environment table drives: read `datatables/environment/tatooine.iff`'s 25 column names and
  one stock ramp before writing ours; if the ramp is not the light source, the fallback (same server hour) stands.
- Whether the client accepts a terrain whose only layer is a constant height with no fractal: Ossus has fractals; the stock
  `character_farm.trn` is exactly that shape and SOE shipped it, so I expect yes.
- The pitch cap of the chase camera (how "top" the top shot gets) and the exact zoom steps: the owner's first visit sets the
  numbers in section 3.
