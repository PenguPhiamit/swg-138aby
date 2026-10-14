# Ossus O3: map art from our own terrain — Fable, 14 Oct 2026

Story-neutral client art for Ossus, rendered from our `staged/client/terrain/ossus.trn` through the Core3 height port
(no wiki or third-party image anywhere): the planetary map, a planet-select globe cloned from a stock chain, and the
loading screen pointing at our own tile. Our own DDS writer, self-tested on stock files. Nothing installed; Claude's
archive builder takes `staged/client/` (or calls `stage_map_art(stage_dir)`).

## Files (`staged/client/`)

| path | what | from |
|---|---|---|
| `texture/ui_map_ossus.dds` | 1024x1024 planetary map, A8R8G8B8, no mips (stock maps have none): hillshaded relief, water where the ground lies more than 0.75 m under the terrain's water table (38.5 m), the Knossa road | 1,048,576 heights from `trn_read`/`trn_road` (0.09 ms each) |
| `texture/ui_planet_sel_ossus.dds` | 256x256 globe texture, 9-level mip chain like stock `ui_planet_sel_*.dds`: western hemisphere = the map, eastern = the map turned 180 degrees, crossfaded at both seams, darkened towards the poles | the map |
| `appearance/ui_planet_sel_ossus.apt`, `appearance/mesh/ui_planet_sel_ossus.msh`, `shader/ui_planet_sel_ossus.sht` | stock `ui_planet_sel_tato.apt` → `ui_planet_sel_tato.msh` → `ui_planet_sel_tatt_as8.sht` (`effect\a_simple.eft`), each parsed, round-tripped byte-exact and rebuilt with its one NAME reference renamed | stock (data_other_00 / data_static_mesh_01) |
| `texture/loading/ossus/ui_load_ossus.dds` | 512x512 loading tile, A8R8G8B8 like `texture/loading/lok/ui_load_lok.dds`: the map box-filtered and vignetted | the map |
| `datatables/loading/ossus.iff` | O1c's four rows, every `Picture` now `loading/ossus/ui_load_ossus` (the strings `string/en/loading/ossus*.stf` are O1c's, unchanged) | O1c |
| `out/*.png` | previews of the two textures | |

Palette by height: shore sand at the water table, olive scrub on the plains (44–60 m), khaki foothills, red-brown mesa
(100–140 m), green benchland (140–165 m), grey rock above 180 m (the southern range). The plains' many small hollows
below the water table are real (water sits at the 6th percentile of the plains), so the map shows ponds; hollows
shallower than 0.75 m are drawn as damp ground instead.

## DDS (`tools/dds.py`)

Reader/writer for the 124-byte header plus data; `write(read(x)) == x` on four stock files (uncompressed A8R8G8B8
`ui_load_lok.dds`, MTG's 24-bit `ui_map_hoth.dds`, DXT1 `ui_planet_sel_tatt.dds` with 9 mips, DXT5 `ui_planet_sel_hoth.dds`);
`encode(rows, mips)` writes uncompressed A8R8G8B8 with the stock UI header pattern (flags 0xa1007, pixel-format 0x41,
caps 0x401008, linear size) and a box-filtered mip chain; `decode(encode(x)) == x` on a test image. Uncompressed was
chosen over DXT1 because 161 of 400 sampled stock `texture/ui_*.dds` are uncompressed 32-bit and MTG's own Hoth map is
uncompressed 24-bit, so no DXT encoder had to be proved.

## Hooks for the archive builder

- `python -I tools/map_art.py <stage_dir>` or `map_art.stage_map_art(stage_dir)`; `--check <dir>` re-reads the set
  (headers, mip sizes, IFF rebuilds, apt→msh→sht→dds chain, loading rows → tile).
- `datatables/player/waypoint_planets.iff` row `ossus` still names O1's placeholder `ui_planet_sel_dant.apt`
  (`stage_tables.PLACEHOLDERS['planet_model']`): set it to `ui_planet_sel_ossus.apt` when this is packed. The ticket
  UI's planet entry and the planetary-map page (`ui/ui_planet_map.inc`, `ui_map_ossus`) are Claude's clones, as for Hoth.
- Untested in a client: that the ticket screen draws the globe with a 32-bit texture (stock globes are DXT1/DXT5) and
  that the map page accepts a 1024 A8R8G8B8 map (MTG ships its Hoth map 24-bit uncompressed, so the client's loader
  takes uncompressed maps; its page is still on the owner's to-look list). If either stays blank, say so: a DXT1
  encoder verified against a stock decode is the next step.
