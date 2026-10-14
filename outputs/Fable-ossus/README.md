# Ossus batch O1: terrain, registration tables, environment

Staged by Fable, 14 Oct 2026, from the plan in `Fable-planet-test/README.md` section 5. Everything here is our own
code, data and text; stock client art is referenced by name only (the same basis as Hoth), nothing was copied out of
the owner's archives, and no Bellum or MTG material is used. Story-neutral: geography and names only (Knossa, the
Academy benchland, Imhar Canyon, the Eocho Mountains, Adega Lake are Legends place names, no story point implied).

Contents: `staged/client/` (15 files, below), `tools/` (our writers and checkers), `out/` (reports, sites, preview),
`checks.json` (hashes + every report), `placeholders.json` (owner decisions), `work/build-log.txt`.

| Staged file | What | Built by |
|---|---|---|
| `terrain/ossus.trn` (27 KB), `terrain/ossus_academy.tga`, `terrain/ossus_canyon.tga`, `terrain/ossus_mesa.tga` | the planet and its three painted bitmaps | `tools/ossus_terrain.py build` |
| `misc/planet_crc_string_table.iff`, `datatables/travel/travel.iff`, `string/en/planet_n.stf`, `datatables/player/waypoint_planets.iff` | the four registration tables, stock copies + Ossus | `tools/stage_tables.py` |
| `terrain/environment/ossus.iff`, `datatables/environment/ossus.iff`, `datatables/clientregion/ossus.iff`, `datatables/loading/ossus.iff`, `string/en/ossus_region_names.stf`, `string/en/loading/ossus.stf`, `string/en/loading/ossus_n.stf` | sky (two suns), environment rows, named regions, loading screens and their strings | `tools/stage_env.py` |

Packing into `local_planets.tre` (Claude's step, as for Hoth) replaces the four stock tables; the Hoth versions of the
same four tables are not in `Documentation-support/hoth/client-base/` (those are the stock copies), so the build
that packs both planets must re-apply the Hoth rows on top of these or re-run `stage_tables.py` on the Hoth versions
(it takes any base: set `BASE`). Owner questions are at the end.

## O1a: `terrain/ossus.trn`

16,384 m, chunk 8 m, 2 tiles (stock planet size). Nine shader families (33 stock shaders: dark-green and yellow
Dantooine grass, fallen-leaf forest floor, mossy dirt, brown-grey cliff rock, white limestone, Dathomir canyon floor and
wall, Endor riverbed, packed dirt, pink Dantooine grass for the benchland meadow), seven flora families (37 stock
appearances: blba/oak/holly/birch plains trees, maple/birch/ginkgo/dogwood forest trees, three mountain pines, rocks,
two undergrowth sets, lillypads), six radial families (16 stock radial shaders), six environment families, five
fractals, three bitmaps. Global water `wter_dant_lake` at 38.5 m (the 6th percentile of the plains: hollows and the
basin become lakes, 5.4 % of the map).

Layers, in order: rolling hills (fractal, 0-90 m) + fine relief (6 m); forest patches (fractal filter 0.56-1); the Eocho
Mountains along the south edge (ridged fractal +320 m, feathered band); highland band 140-230 m (dry grass, pines,
tufts); summits above 230 m (limestone, no flora); **the Academy benchland** (painted bitmap over a 3400 x 2400 m
frame, ground replaced to 166.1 m = natural ground 56.1 + 110, feathered 450 m rim, meadow shader, flowers, rocks);
**canyon country** (painted mesa raised to 100 m along the canyon's line) and **Imhar Canyon** cut into it (painted
channel, floor 44.5 m = water + 6, walls ~100 m wide: the probe east of path point 3 reads 44.7 flat, then 45.2, 48.4,
57.0, 69.2, 82.6, 94.3, 101.7, 104 m every 20 m); a lake basin (-3600, 1200, r 600, sunk 10 m under the water);
lake bed and shore (riverbed shader, lillypads); mossy valleys; cliff slopes over 24 degrees (rock, no flora; client
only, see below); the Knossa landing pad (r 160, flattened to 50.3 m, inner 88 m exactly flat) and its clearing
(r 300, packed dirt, no flora, "knossa" environment); the Academy ruins pad (r 130, flattened to 170.4 m); **the road**
Knossa -> ruins (12 m wide, 7 control points, 16 pieces); its verge (polyline, no flora); **three cave mouths** (an
apron r 30 levelled to the mouth height, rock shader, and a 9 m `AEXC` hole, the size the stock Tatooine and Hoth
caves use).

Why the road is 16 pieces: Core3's `AffectorRoad::process` returns without touching the height when the point is
more than 500 m from the road's *start* point (`OUT_OF_RANGE`), so one long road would be flat on the client and
natural on the server beyond 500 m. Each piece is at most 480 m, a 2-point road with one HDTA segment sampled
every 40 m from the surveyed ground and smoothed; the server then applies all of it. Road surface vs the ground it
was sampled from: max 0.95 m, mean 0.21 m, so client and server agree along it within a metre.

Bitmaps: 8-bit greyscale TGA, file row 0 = south, column 0 = west, which is how Core3's `TargaBitmap` + `FilterBitmap`
sample it and how the TGA default origin (bottom-left) reads; values capped at 254 because a 255 pixel is exactly the
filter's upper bound and passes only by float rounding (Core3 clamps 1.0f to 0.99999 in float; a double port would
reject it, the first version of this batch had that bug). Each painted shape ends inside its frame (edge value 0).
Benchland and mesa at 256 px (13 m and 24 m per pixel), the canyon channel at 512 px (12 m).

### Verified offline (`out/ossus-report.json`, 30 s)

| Check | Result |
|---|---|
| Byte round trip (parse -> build) | identical, 27,322 B |
| Re-read in Core3's chunk order | version 0014, 36 top layers, 44 layers in all; 0 unexpected notes (the 3 expected: `FBIT` written stock-length, 24 B, Core3 reads 20) |
| Every parent/child form pair also in stock tutorial/simple/tatooine/dantooine or MTG hoth | 0 unseen |
| Every shader (33 + water), flora appearance (37), radial shader (16) resolves in the client archives; bitmaps are ours | none missing |
| Height survey, Core3 port + roads, 32 m grid, 262,144 samples | 23.9-374.2 m, mean 84.5 m, 5.4 % under water |
| Knossa pad | spread 0.00 m over r 80; steepest 10 m step walking north out of the pad 2.24 m |
| Academy ruins pad | 170.4 m, spread 1.04 m over r 120 (steepest 10 m step 0.18 m) |
| Camps (r 60): west plains (-5344, 96) 46 m, north hills (-3744, 5792) 49 m, canyon rim mesa (3232, -2656) 104 m, south foothills (-6496, -4320) 58 m | spreads 3.1 / 2.9 / 1.3 / 4.0 m, steepest 10 m steps about 1 m |
| Caves: west foothills (-2976, -4960) 51.9 m, east foothills (4896, -4960) 58.5 m, north (1376, 5920) 45.7 m, mouths facing north (0 deg) | hillside before the apron: 4-7 m rise over r 25 at under 3 m per 10 m; apron spread 1.1-1.7 m |
| Road | 16 pieces, max 0.95 m off the sampled ground |
| TGA writer -> reader | identical arrays; Core3's loader accepts all three |

`out/ossus-sites.json` carries every coordinate above (x east, y north, heights from the server-side port) for the
snapshot and regions steps; `out/ossus-height.png` is the 512 px preview (north up, white high, mid-grey water,
crosses at the pad, ruins, camps and caves).

Known limits: Core3 ignores slope, direction and shader filters for height (not a problem here: no height affector
sits under one), applies `FBIT` only with the feather in the Core3 way (ours use feather 0), and never evaluates flora
or radials, so tree and grass density is unverified until the real client. The stock big planets ship 2048 x 2048 water
and seed maps in the `0001` maps form; ours are empty as the tutorial ships (inferred acceptable, as in the prototype).
The prototype's Core3 port was validated against the live Hoth server (`Fable-planet-test/README.md` section 4); the
road port and the float32 bitmap fix are checked against Core3's source only.

## O1b: registration tables, our own writers

`tools/swg_tables.py` reads and writes CSTB (planet CRC table), DTII (datatables) and STF (string files). Exact round
trips on the stock copies in `client-base/`: `planet_crc_string_table.iff`, `travel.iff`, `waypoint_planets.iff`,
`planet_n.stf`, and, as harder tests, `object_template_crc_string_table.iff` (1.1 MB), `skills.iff`, `skl_n.stf`,
`resource_tree.iff`, plus the eight Dantooine/Tatooine tables and string files O1c copies from, all byte-identical.
The planet CRC is the SOE table CRC (MSB-first CRC-32, poly 0x04C11DB7, init and final xor 0xFFFFFFFF), matching all
25 stock entries; Ossus is `f270b502`, inserted in ascending CRC order (the client binary-searches). Every staged
table also re-reads through Claude's independent `swg_client_data.py` reader (`out/tables-report.json`).

| Table | Change |
|---|---|
| `misc/planet_crc_string_table.iff` | 25 -> 26 entries, `ossus` |
| `datatables/travel/travel.iff` | column `ossus` and row `ossus`; Corellia -> Ossus **3000** and Ossus -> Corellia **1750** (placeholders, the Yavin IV/Hoth pattern), Ossus -> Ossus 100, every other fare 0 (no route) |
| `string/en/planet_n.stf` | `ossus` = "Ossus" (id 33) |
| `datatables/player/waypoint_planets.iff` | `ossus` -> `ui_planet_sel_dant.apt` (placeholder: the stock Dantooine globe referenced in place until `ui_planet_sel_ossus.apt` exists) |

Not in this batch (as in the brief): the ticket UI (`ui_ticketpurchase.inc`) and planetary map UI, which is where the
galaxy-map spot lives. `placeholders.json` records the spot as an owner decision; Hoth's provisional (425, 225) and the
rejected affine fit are in `Documentation-support/hoth/galaxy-map-calibration.md`.

## O1c: environment, loading, client regions

- `terrain/environment/ossus.iff`: Dantooine's sky file (`FORM ENVM`: night sky flag, Tatooine's star map that Dantooine
  already uses, sun, moon, second moon, two star-destroyer silhouettes) with Tatooine's `SSUN` chunk inserted after
  `SUN ` for the second sun. Checked: both stock files round-trip; the SSUN bytes are Tatooine's, the rest Dantooine's.
- `datatables/environment/ossus.iff`: 25 columns, 30 rows = our six families x 5 weather rows, copied from Dantooine
  (`ossus_plains` <- main_base, `ossus_forest` <- second_stepes, `ossus_mountains` <- stepes, `ossus_benchland` <-
  jedi_temple, `ossus_canyon` <- dantari1, `ossus_knossa` <- outpost). Family names match the `EFAM` names in the
  terrain; every file a row names (sky gradient, cloud shaders, colour ramps, environment maps, ambient sounds, music)
  exists in the client archives.
- `datatables/clientregion/ossus.iff` + `string/en/ossus_region_names.stf`: Knossa (r 300), the Academy Benchland
  (r 1300), Imhar Canyon (r 1400), the Eocho Mountains (r 3200), Adega Lake (r 700), Ossus (r 9000).
- `datatables/loading/ossus.iff` + `string/en/loading/ossus.stf`, `ossus_n.stf`: four loading screens with our own
  text, pictures = the stock generic tile (`texture/loading/generic/generic_swg.dds`, referenced in place) until Ossus
  art exists.

## What only the real client can show

Whether the terrain loads without the "not a valid terrain file" crash and how it looks: shader blending, forest and
grass density (the family `density` values and layer feathers are stock-shaped guesses), the painted benchland and
canyon in the client's own bitmap sampling, the road surface and its shader feathering, the cave holes, water
rendering with empty water/seed maps, the two-sun sky, the loading screens, the planetary map, the ticket list
(needs the UI step) and the travel fare. Server side: zone registration, travel point at the pad (0, 0, -3600, the pad
is at 50.3 m), regions (Claude).

## Owner questions

1. Fares: keep Corellia -> Ossus 3000 / back 1750 (the Yavin IV and Hoth pattern) or another price?
2. Galaxy-map spot: where should Ossus sit on the ticket map (lore: Adega system, Outer Rim, near Yavin at R-6 vs P-6)?
3. The placeholder globe (`ui_planet_sel_dant.apt`) and generic loading tiles: fine until the map-art step?
4. Region names (Knossa, Academy Benchland, Imhar Canyon, Eocho Mountains, Adega Lake): keep, or different names so
   the story point stays open?
5. The benchland rise (110 m, ruins pad at 170 m) and canyon depth (mesa 100 m, floor 44.5 m): right scale, or gentler?
6. First real-client look at `ossus.trn`: who runs it, and may Claude put it in a test-session `local_planets.tre`?

Lesson carried over from batch C: `apply.sh`'s "before" patch lost a tab-leading anchor through `read` with
`IFS=$'\t'` (leading tabs are stripped as whitespace), so it reported success without writing; this batch has no dev
patches, and the next apply script will test every patch mode on a scratch copy first.
