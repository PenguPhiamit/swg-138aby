# Ossus O7: Fable's o6 made buildable — Claude, 16 Oct 2026

Fable's first Ossus pass (`../o6/README.md`: craters and scorch on the academy ruins, settlement fields, 18 points of interest) as build-ready
data, with the owner's answers of 15 Oct 23:15 applied. Stock art only, by template path: every one of the 89 templates is in the stock client's
object template table (none MTG-only). Nothing under `/opt/swg` was written, Fable's staged files are untouched (the terrain was built in a temp
folder, the real rebuild is step 1 below), nothing was run in a client or on a galaxy. Our own code and data; the stock names are references only.

| File | What |
|---|---|
| `statics.json` | **295 objects** for 16 places (object path, x, z, y, yaw, point of interest, role) with their snapshot ids, node floats and, for the 12 buildings, portal layout, cell count and CRC. |
| `terrain.json` | the layers (14, ready for `ossus_terrain.py` through `tools/o7_terrain.py`), the two new shader families, and the design numbers behind them. |
| `poi-placements.json` | per place: centre, ground z, census samples, creatures and lair props near it, distance from Knossa, steep/water/no-build flags, notes; plus **spawn anchors** (`npc_points`: x, y, z, heading, role, stock mobile names that exist in dev). |
| `template-resolution.json` | every "(confirm)" of o6 against the client's template list (section 1), each chosen path checked against the stock table, the client files and Core3-dev. |
| `checks.json` | everything below that is a number, from `tools/run_all.py`. |
| `tools/` | `o7_terrain.py` (design, build, survey), `o7_pois.py` (the layouts, one function per place), `o7_resolution.py` (the "(confirm)" table), `make_o7.py` (placements and checks), `append_snapshot.py`, `run_all.py`, `server_check.sh` (read-only, WSL), `render_tables.py` (fills this README's tables), `o7_common.py`. |
| `out/` | `server-templates.list/.txt` (the Core3-dev lookup), `snapshot-usage.json` (how stock snapshots use each template), `checks-statics.json`. |

## The owner's answers, as applied

| Answer (15 Oct 23:15) | In this batch |
|---|---|
| Craters 2-4 m deep as designed | Five craters, 3.5 / 2.5 / 2.0 / 2.0 / 2.0 m. o6's own list ended 1.5 and 1.0 m, outside the owner's range, so craters 4 and 5 are 2.0 m (`terrain.json` keeps `o6_depth_m`). Lips peak at 0.37-0.41 m, under o6's 0.6 m. |
| Only Westmarch and Knossa Fields | Two flatten layers. North Reach, Rim Mesa and Lakeshore are listed under `design.held`, not staged. |
| Garrison on the benchland rim over the ruins, guarding the dig | POI 3 moved from east of Knossa to the flat ground nearest the crest north-east of the ruins, with the dig between its gate and the hall. |
| Hold POI 7 (Vong fields) | Not placed. POI 17 (terrain only) is not held and is in `terrain.json`. |
| Creature levels unchanged | No mobile, lair or spawn file is touched or proposed. |
| Stock art first, MTG only where the catalogue rates it usable | No MTG art at all. One MTG-only candidate was left out (the destroyed Lambda shuttle: stock `escape_pod` does the job); the Mustafar ash shaders o6 named do not exist. |

## 1. Template paths: every "(confirm)" resolved

The table of names is `misc/object_template_crc_string_table.iff`: the winning copy in `patch_14_00.tre` (15,792 names) and the installed
`local_planets.tre` (29,358, stock plus 13,566 MTG and Hoth names), read with `outputs/tools/swgfmt` in memory (nothing extracted). A path counts as
resolved when it is in the stock table, its client template and every appearance it names are in the archives, and Core3-dev has its server
template (`object/<path>/<name>.lua`, checked read-only inside WSL as swgemu, dev HEAD 8b48a044: 89 of 89 present, and the Hutt body). `dir/shared_{a, b}.iff` below means `dir/shared_a.iff` and `dir/shared_b.iff`.

<!-- RESOLUTION -->
- **POI 1 craters: shader ACCN to a dark burnt ground (candidates shader/must_ash_* (confirm), else Dathomir black rock)**
  - Status: resolved: other stock shaders.
  - Chosen: `shader/dirt_scorched_tornearth.sht`, `shader/dirt_scorched_tornearth_a1.sht`, `shader/dirt_scorched_tornearth_a2.sht`, `shader/dirt_scorched_earth.sht`, `shader/dirt_scorched_earth_a1.sht`, `shader/dirt_scorched_earth_a2.sht`, `shader/rock_mtns_whitelimestone.sht`
  - Why: No shader/must_ash_* exists (the Mustafar terrain uses rock_mustafar_*, MTG art, not needed). Stock Yavin 4 already ships dirt_scorched_tornearth (crater floor) and dirt_scorched_earth (scorch fans; Endor uses it too); the glass pan keeps o6's "limestone family already in the file" (rock_mtns_whitelimestone). ACCN is a vertex-colour affector in the stock files, not a shader, so the shader goes in as ASCN (shader family constant), the affector every stock layer uses for ground shaders.
- **POI 1 rubble apron: ACRF radial/flora off inside, rocks on**
  - Status: resolved: other affectors.
  - Chosen: (no template; terrain affectors)
  - Why: ACRF is a colour-ramp-by-fractal affector. The apron uses the file's own flora affectors: clear_flora() (the removal pattern Dantooine's stock layers use) over r 130, then AFSC (rocks, family 4) outside r 60.
- **POI 1 blast debris: shared_debris_* stock piles (confirm names; Endor and Corellia have object/static/structure/general/shared_debris_*)**
  - Status: resolved: other names.
  - Chosen: `object/static/structure/general/shared_{poi_all_construction_stone_pile, poi_all_construction_metal_pile, atst_debris_01, atat_debris_01, atat_debris_02, transport_debris_02, prp_junk_s5}.iff`
  - Why: The shared_debris_* names that exist are all Death Star pieces (conduit, tubes, turbolaser): wrong for a ground attack. The same folder has rubble and wreck pieces; stone and metal piles for the lips, an AT-ST and AT-AT wreck, a transport hull section and a junk heap for the Sith and Imperial ground forces.
- **POI 1 downed Imperial drop-pod or shuttle: Tatooine shared_crashed_ship_* or Dantooine crashed escape pod (confirm)**
  - Status: resolved: other name.
  - Chosen: `object/static/structure/general/shared_{escape_pod, escape_pod_door}.iff`
  - Why: No shared_crashed_ship_* exists. object/static/structure/general/shared_escape_pod.iff (3.9 x 8.5 m, 18 stock snapshot nodes) is the drop pod. The destroyed Lambda shuttle (object/static/worldbuilding/vehicles/shared_lambda_shuttle_static_destroyed.iff) is MTG-only, not mapped to a catalogue P row: not used.
- **POI 1 memorial: six standing stones (stock shared_marker_*/Dantooine standing stones (confirm))**
  - Status: resolved: other name.
  - Chosen: `object/static/structure/dantooine/shared_dant_jedi_temple_pillar_sm.iff`
  - Why: No shared_marker_* exists. poi_all_monolith_s01 is 36 m tall and gravestone_generic_style_* are 0.7 m: both wrong. The Dantooine temple's own short pillar (2 x 4.7 m, 24 uses here) reads as a Jedi memorial stone and is already in the ruins set.
- **POI 2 sanctuary: shared_cave_01 or a cellar .pob from the stock bunker set (confirm); holocron pedestal decor shared_holocron_* (confirm)**
  - Status: resolved: other name; holocron decor has no static.
  - Chosen: `object/building/general/shared_cave_06_flatland_s01_damprock.iff`
  - Why: The ruins pad is flat ground with no hillside, so the self-contained flatland variant of cave_01 is used (same 13-portal layout as cave_01_damprock, damp-rock look; 12 cells). The bunker interiors are Imperial concrete. No holocron static or pedestal exists in the stock table: the stock item object/tangible/jedi/shared_jedi_holocron_light.iff can be created by script, and the Dantooine altar static (object/static/structure/dantooine/shared_dant_jedi_temple_altar.iff) is the pedestal. Interior contents are a screenplay job (cell ids = building id + 1..11).
- **POI 3 garrison: object/building/military/shared_military_guard_tower, shared_military_outpost_* (confirm)**
  - Status: resolved: other names.
  - Chosen: `object/building/military/shared_{mun_all_military_tower_impl_guard_s01, military_base_shed_imperial_style_officer_s01, military_base_shed_imperial_barracks_s01}.iff`; `object/static/structure/military/shared_{military_wall_strong_imperial_32_style_01, military_wall_strong_imperial_16_style_01, military_wall_strong_imperial_style_01, military_column_strong_imperial_style_01}.iff`; `object/static/structure/general/shared_banner_imperial_style_01.iff`
  - Why: shared_military_guard_tower does not exist; shared_military_outpost_guard_tower_1 does (no portal layout, no interior) but the guard tower with a door and two cells, mun_all_military_tower_impl_guard_s01, is what the Yavin 4 snapshot places (ten of them). The sheds are the Imperial-style buildings Corellia, Rori, Lok, Naboo and Dantooine place (a node plus 6 cells each).
- **POI 4 vaults: third stock cave (cave_02 flatland variant) + Dantooine temple pillars**
  - Status: resolved.
  - Chosen: `object/building/general/shared_cave_07_flatland_s02.iff`; `object/static/structure/dantooine/shared_{dant_jedi_temple_pillar_base, dant_jedi_temple_pillar_fallen, dant_jedi_temple_pillar_sm}.iff`
  - Why: cave_07_flatland_s02 is the flatland variant of the cave_02 layout (14 portals, 12 cells).
- **POI 5 Ysanna camp: stock Tusken/Dantari-style camp statics (hide tents, racks, a fire)**
  - Status: resolved.
  - Chosen: `object/static/structure/dantooine/shared_{dant_small_mudhut, dant_large_rock_hut, dant_hide_tanning_s01, dant_hide_tanning_s02, dant_rack_spears, dant_cooking_stone, dant_mud_oven, dant_fire_pit, dant_skull_bol, dant_skull_thune, dant_skull_lizard, dant_totem_pole, dant_fence_8m}.iff`
  - Why: The Dantooine Dantari camp set, the same pieces Dantooine's stock snapshot places in bulk (fence_8m 151 nodes, totem poles 66, spear racks 42).
- **POI 6 stone circle: standing stones + a fire pit + bone totems**
  - Status: resolved.
  - Chosen: `object/static/structure/general/shared_{rock_mossy_big, rock_mossy_big_a1, tato_cave_rock_large}.iff`; `object/static/structure/dantooine/shared_{dant_fire_pit, dant_totem_pole, dant_skull_thune}.iff`
  - Why: Boulders for the stones (no stock standing-stone static of a sensible size), the Dantooine fire pit and totem poles.
- **POI 8 hamlet: Dantooine farmstead set, a dock of Naboo pier pieces, nets**
  - Status: resolved: Endor pier instead of Naboo.
  - Chosen: `object/static/structure/dantooine/shared_{dant_small_mudhut, dant_large_mudhut, dant_fish_rack, dant_hide_tanning_s01, dant_fence_8m, dant_boundary_post}.iff`; `object/building/endor/shared_{endor_lake_walkway_straight, endor_lake_platform}.iff`; `object/static/item/shared_item_basket_closed.iff`
  - Why: No Naboo pier statics exist (the seawall_* pieces are Theed harbour walls). Endor's wooden lake walkway and platform (60 and 41 stock snapshot nodes, one Dantooine snapshot also uses them) are the dock; dant_fish_rack are the nets and racks.
- **POI 9 adit: stock mine entrance static + ore carts + a lamp string; the cave mouth is a flatland cave**
  - Status: resolved: allum_mine_* statics; one piece dropped.
  - Chosen: `object/building/general/shared_cave_08_flatland_s03.iff`; `object/static/structure/general/shared_{allum_mine_car_s01, allum_mine_support_s01, allum_mine_wall_lamp_s01, allum_mine_bucket_s01, allum_mine_pipes_s01, allum_mine_device_s01}.iff`
  - Why: The stock allum-mine set is exactly the ore carts, timbers, lamps, buckets, pipes and crusher; the cave mouth is cave_08_flatland_s03 (30 cells). object/building/general/shared_bunker_allum_mine.iff exists (Endor uses it) but its entrance portal lies 5 to 8 m below the building origin and needs a pit, so it is not used. allum_mine_console_s01 names appearance/bunker_mine_console_s01.apt, which is not in the client archives: dropped (the crafting station is a script object).
- **POI 7 Vong project fields: MTG/stock Kashyyyk Vong statics if the merged table has them (confirm shared_vong_* names)**
  - Status: held by the owner (15 Oct); recorded only.
  - Chosen: (no template; terrain affectors)
  - Why: Not placed. For the record: the stock table and the installed merged table (29,358 names) have no shared_vong_*, yuuzhan, coral, damutek or voxyn template (the only match for "coral" is a player-style mobile, dressed_coraline_dynes), so the fields will need new art or Dathomir and Mustafar stand-ins when the voxyn content exists.
- **POI 10 crossing: Naboo or Corellian bridge pieces (confirm a static bridge exists; else platform pieces)**
  - Status: resolved: Tatooine bridge.
  - Chosen: `object/static/structure/tatooine/shared_bridge_tatooine_small_style_03.iff`
  - Why: Static bridges exist: Tatooine small_style_01/02/03 (8, 16, 32 m), Corellia imprv_bridge_sm/lg (16, 28 m), Naboo bridge_naboo_theed_style_1 (50 m). The 32.5 m Tatooine piece (Lok places ten) chains 10 times (325 m) over the 284 m rim-to-rim span, with about 20 m resting on each rim. Nothing in stock supports a span this long: the deck is unsupported.
- **POI 11 old town: Tatooine/Dantooine filler blocks, merchant tents, stock Dantooine cantina**
  - Status: resolved.
  - Chosen: `object/building/general/shared_merchant_tent_all_s01.iff`; `object/static/structure/corellia/shared_{corl_tent_large, corl_tent_med}.iff`; `object/building/military/shared_military_base_shed_imperial_style_cantina_s01.iff`; `object/static/structure/tatooine/shared_{stone_hovel_tatooine_style_01, shed_junkshop_watto, wall_ruined_tatooine_large_style_01, wall_ruined_tatooine_large_style_02, pillar_ruined_large_style_01, pillar_ruined_small_style_01}.iff`; `object/static/structure/dantooine/shared_dant_large_rock_hut_dest.iff`
  - Why: There is no separate Dantooine cantina object: Dantooine's own snapshot uses the Imperial-style shed with the cantina name (military_base_shed_imperial_style_cantina_s01). The merchant tent has a one-room interior.
- **POI 12 road markers: small standing stones or lamp posts**
  - Status: resolved.
  - Chosen: `object/static/structure/dantooine/shared_dant_jedi_temple_pillar_sm.iff`
  - Why: The same short temple pillar as the memorial.
- **POI 13 watch ruin: Dantooine temple base + one pillar, Yavin-style tower stub (confirm)**
  - Status: resolved; no tower stub.
  - Chosen: `object/static/structure/dantooine/shared_{dant_jedi_temple_pillar_base, dant_jedi_temple_pillar, dant_jedi_temple_pillar_med, dant_jedi_temple_pillar_fallen, dant_jedi_wall_1, dant_jedi_wall_2, dant_jedi_temple_pillar_sm}.iff`
  - Why: The Yavin 4 temples are whole buildings with interiors (object/building/yavin/temple_*), not stubs; the Dantooine pieces make the tower footing.
- **POI 14 Sith post: stock Imperial crates, a cage, a terminal**
  - Status: resolved (outside); interior by screenplay.
  - Chosen: `object/static/structure/military/shared_bunker_crate_style_01.iff`; `object/static/structure/general/shared_{data_terminal_free_s2, banner_imperial_style_01, palette_supply_02, campfire_burnt}.iff`
  - Why: Outside dressing only. For the cells: object/static/item/shared_item_cage_bamboo.iff (1 x 0.8 m cage), shared_item_door_impl_s01.iff (Imperial door), shared_item_datapad_s1.iff exist as statics a screenplay can create inside the cave's cells.
- **POI 15 crashed fighter: stock crashed X-wing/A-wing static (confirm shared_crashed_*)**
  - Status: resolved: other name.
  - Chosen: `object/static/structure/general/shared_xwing.iff`
  - Why: No shared_crashed_* statics; object/static/structure/general/shared_xwing.iff (13 x 15.6 m, 5 stock snapshot nodes) is the fighter. There is no A-wing static; the X-wing plus wreckage piles do the job.
- **POI 16 sky burial: bone totems, a wooden platform**
  - Status: resolved.
  - Chosen: `object/static/structure/dantooine/shared_{dant_totem_pole, dant_skull_bol, dant_rack_spears}.iff`; `object/static/structure/general/shared_skeleton_human_headandbody.iff`; `object/building/endor/shared_endor_lake_platform.iff`
  - Why: Dantooine totem poles and skulls; Endor's wooden lake platform is the burial platform.
- **POI 18 Hutt landing field: object/building/poi/shared_tatooine_hutt_businessmen_camp_medium.iff (verified to exist in the client)**
  - Status: not usable as a camp; composed from statics.
  - Chosen: `object/static/structure/general/shared_landing_pad_transport.iff`; `object/static/structure/corellia/shared_corl_tent_hut_s01.iff`; `object/static/item/shared_item_crate_spice.iff`
  - Why: The path exists, but the client template carries only terrainModificationFileName terrain/poi_medium.lay and no appearance: it is a server theater anchor (Core3 creates the camp's contents), so placed in a snapshot it is an invisible flattening. The field is built from a stock landing pad, tents, pallets and crates. object/mobile/shared_hutt_male.iff (the Hutt broker's body) exists in the client and in dev.
<!-- /RESOLUTION -->

## 2. Terrain (`terrain.json`)

`ossus_terrain.py` builds the whole planet in one function, so `tools/o7_terrain.py` wraps two of its names (`layer()` to remember the node of the
`academy ruins pad (flattened)` layer, `form()` to splice our layers into the layer list right after it) and adds two shader families to its
`SHADERS` table. The first two build passes (the survey that picks the ruins, camps, caves and the road heights) run without the layers, as before;
only the final pass has them. Layer order matters and is the one o6 asked for: after the ruins pad (so the craters cut the pad's neighbourhood) and before the road.

| Layer (all under the ruins pad) | Parameters |
|---|---|
| **Crater 1-5** (one group each, four children: bowl, lip raise, lip trim, burn) | centre / radius / depth: 1 (1870, 2930) 22 m 3.5; 2 (2140, 2790) 18 m 2.5; 3 (2010, 3010) 14 m 2.0; 4 (1930, 2700) 12 m 2.0; 5 (2210, 2920) 9 m 2.0. `BCIR` bowl feather 0.9 with `AHCN` op 1 (add) -depth; lip raise `BCIR` r+6 (feather 0.6) +lip m, trim `BCIR` r+1 (0.9) -lip m, lip = 1.0 / 0.8 / 0.6 / 0.6 / 0.5; burn `BCIR` r+10 with the new `crater` shader family and removal of all flora. |
| **Scorch fans** 1-4 | `BPOL` triangle from each large crater toward the south-west (heading 225), 60 / 55 / 45 / 40 m beyond the rim, base 0.9 r wide, feather 10 m, new `scorch` shader family, flora removed. |
| **Glass pan** | `BCIR` (2016, 2848) r 60 (feather 0.25): the existing limestone family `summit`, flora removed. The pad stays flat (no height affector). |
| **Rubble apron** | `BCIR` r 130 (feather 0.35): flora removed; child layer with the r 60 circle inverted: rocks added (family `rocks`). |
| **Field Westmarch** | `BCIR` (-5344, 96) r 400, feather 0.3: `AHCN` op 0 to 46.0 m, plains grass shader, flora removed. Flat to r 280, ramp 120 m. |
| **Field Knossa Fields** | `BCIR` (1500, -3300) r 450, feather 0.3: flat 50.0 m, same surface. Flat to r 315, ramp 135 m. |
| **Glass plain (POI 17)** | `BPOL` rectangle (-300..300, -5650..-5350), feather 25 m: limestone, flora removed. |

New shader families (stock shaders, all in the client): `crater` = `dirt_scorched_tornearth` (+ `_a1`, `_a2`), `scorch` = `dirt_scorched_earth` (+ `_a1`, `_a2`).

How o6's text was translated (so nobody looks for what is not there):
- `ACCN` (colour constant), `ACRF` (colour ramp by fractal), `FSHD` and `ARCN` are not the tools for "shader" and "flora off". The stock files set ground
  shaders with `ASCN` and clear flora with the `AFSC/AFSN/AFDN/AFDF` removal pattern that `ossus_terrain.clear_flora()` already uses (Dantooine's own removal layers
  use the same flags); that is what the layers use. `FSHD` (a shader filter) has no implementation in Core3 and the pad is meadow anyway, so it is left out.
- A plain `+0.4 m` disc for the lip vanishes under the bowl (the `BCIR` falloff is steep), so the lip is a raise-and-trim pair tuned for a ring that peaks near 0.4 m just outside the rim.
- A `BPOL` feather is a distance in metres (stock Tatooine uses up to 700), not a fraction like `BCIR`'s: o6's "feather 0.8" for the fans became 10 m.
- "Feather 0.5 over the outer 100 m" for the fields is ambiguous; 0.3 gives a flat core of 280 / 315 m (the city-eligible area) and a ramp no steeper than the natural ground.
- "Meadow shader" for the fields is the file's plains grass (`grass`); the pink `bench` meadow stays on the benchland.

Measured on the built file (Core3 port, `checks.json` -> `terrain` and `terrain_survey`):
- Build `PASS`: byte round trip identical, 50 top-level layers (36 + 14), Core3-order re-read with only the 3 expected `FBIT` notes, 0 parent/child pairs unseen in stock, 39 shader children / 37 flora / 16 radial / 3 bitmaps all resolve in the client.
- The same tool without the layers reproduces the staged `ossus.trn` (27,322 bytes) and all three TGAs byte for byte, and with the layers the TGAs stay identical, so the wrapper changes nothing else. The sites it surveys (pad, ruins, caves, road) keep their positions and heights; two probe numbers move: Westmarch's camp probe is now flat (0.0 m, was 3.1) and the ruins probe's steepest 10 m step is 2.38 m, not 0.18, because crater 2's rim enters its 120 m disc (the pad's own spread stays 1.04 m).
- Craters: centre drops 3.5 / 2.5 / 2.0 / 2.0 / 2.0 m; lip peaks 0.41 / 0.40 / 0.37 / 0.40 / 0.38 m; steepest 1 m step 21.8 / 20.4 / 21.6 / 24.6 / 30.3 degrees (the smallest, crater 5, is the steep one); the layers change the height no farther than 26 / 22 / 18 / 16 / 13 m from each centre.
- Fields: spread over r 60 is 0.00 m (flat core exactly 46.0 and 50.0); steepest 20 m step 11.1 degrees (the natural ground there: 11.7) and 12.4 (natural 14.0); 1.2 % and 0.25 % of each disc lies under the 38.5 m water, all of it in the outer ramp where natural hollows are not fully filled; clear of every no-build circle by 5,063 m (Westmarch; the nearest is the west cave's) and 760 m (Knossa Fields; the nearest is Knossa's r 320 circle).
- Whole planet, 96 m grid, 29,241 samples: 122 changed, all inside the o7 discs, 0 outside, worst change outside 0.0000 m. The 87 nodes already in the snapshot stand on unchanged ground (max shift 0.00 m).
- Not a plain: POI 17's ground has 105 m of relief and 41 degree slopes (the Eocho band). The layer paints and clears it; it does not flatten it. A flat 600 x 300 m alternative exists at x 1850-2450, y -4800 to -4500 (12.6 m of relief).

## 3. Placements

Heights are the server's: the Core3 port of the built terrain. It agrees with the explorers' own ground samples (4,182 creature and static sightings, all with a z) to
a median of 0.26 m and 0.62 m at the 95th percentile once the census's whole-metre truncation is allowed for (`checks.json` -> `census_vs_terrain_model`; the few outliers are
explorer droid rows, the maximum is 12 m). The census file holds only these sightings, not the 27,834 raw ground samples. Creatures are the census's creature sightings (levels from the census); lair props are its `unknown_object` statics (the lair
and den props), minus the ruins' own statics. The census recorded no creature (explorer droids aside) east of x = 2,341 although the explorers walked the east half, so the empty columns for
POIs 9, 10, 16 and 18 mean "nobody recorded any"; whether the east is empty or just not recorded is not established here. "In no-build" is by design for the places inside the ruins, Knossa and cave circles.

<!-- POI_TABLE -->
| # | Place | Centre x / y | Ground z | Nearest census ground sample | Creatures within 300 m (census) | Lair props within 300 m | From Knossa | Flags |
|---|---|---|---|---|---|---|---|---|
| 1 | Academy ruins: craters, drop pod, memorial ring | 2,016 / 2,848 | 170.4 | 20 m: z 170 (terrain there 170.4) | none (nearest ossus_gokob L10, 1,542 m) | none | 6,756 m | in no-build: Academy ruins |
| 2 | The hidden sanctuary | 2,057 / 2,735 | 170.9 | 67 m: z 170 (terrain there 170.4) | none (nearest ossus_gokob L10, 1,661 m) | none | 6,661 m | in no-build: Academy ruins |
| 3 | Krayt's garrison (benchland rim) and its dig | 2,160 / 3,046 | 171.2 | 92 m: z 155 (terrain there 155.9) | none (nearest ossus_gokob L10, 1,395 m) | none | 6,988 m | in no-build: Academy ruins |
| 4 | Great Library vaults and dig camp | 2,300 / 1,960 | 43.3 | 128 m: z 48 (terrain there 48.3) | none (nearest ossus_gokob L10, 2,472 m) | none | 6,017 m | rough: 7 m of relief over r 45 m |
| 5 | Ysanna hunting camp | -1,325 / -4,950 | 64.6 | 80 m: z 60 (terrain there 60.8) | none (nearest ossus_gokob L10, 1,550 m) | none | 1,892 m | none |
| 6 | Ysanna stone circle | -980 / -5,610 | 230.0 | 215 m: z 276 (terrain there 276.4) | none (nearest ossus_gokob L10, 2,250 m) | none | 2,236 m | none |
| 8 | Adega Lake fishing hamlet | -3,050 / 1,100 | 43.4 | 94 m: z 39 (terrain there 39.2) | ossus_mud_yak L19 x3 (240 m) | 4 (nearest 210 m) | 5,603 m | none |
| 9 | Kathracite adit | 4,600 / -321 | 44.7 | 167 m: z 60 (terrain there 59.3) | none (nearest ossus_tribis L10, 5,474 m) | none | 5,649 m | **steep** 32 deg over r 45 m (spread 14 m) |
| 10 | Imhar Canyon crossing | 4,470 / -530 | 44.7 | 153 m: z 44 (terrain there 44.7) | none (nearest ossus_tribis L10, 5,594 m) | none | 5,423 m | none |
| 11 | Knossa old town | 0 / -3,600 | 50.3 | 0 m: z 50 (terrain there 50.3) | none (nearest ossus_kaddyr_bug L10, 2,303 m) | none | 0 m | in no-build: Knossa (city r 200 inside) |
| 12 | The Jedi memorial road | 892 / -31 | 46.8 | 160 m: z 45 (terrain there 45.7) | none (nearest ossus_mud_yak L19, 3,656 m) | none | 3,679 m | in no-build: Academy ruins |
| 13 | Eocho watch ruin | 290 / -6,400 | 337.5 | 50 m: z 324 (terrain there 323.6) | none (nearest ossus_gokob L10, 3,719 m) | none | 2,815 m | **steep** 26 deg over r 22 m (spread 7 m) |
| 14 | Sith interrogation post | -2,976 / -4,954 | 51.9 | 24 m: z 56 (terrain there 52.1) | none (nearest ossus_kaddyr_bug L10, 773 m) | none | 3,270 m | in no-build: west foothill cave |
| 15 | Crashed Alliance fighter | -1,500 / 5,200 | 61.8 | 39 m: z 60 (terrain there 60.6) | ossus_kirruk L19 x2 (127 m) | 3 (nearest 124 m) | 8,927 m | none |
| 16 | Ysanna sky-burial cliff | 5,233 / 786 | 105.2 | 170 m: z 103 (terrain there 103.0) | none (nearest ossus_kaddyr_bug L10, 4,949 m) | none | 6,828 m | none |
| 17 | Supernova glass plain (terrain only) | 0 / -5,500 | 201.8 | 185 m: z 171 (terrain there 172.2) | none (nearest ossus_gokob L10, 2,957 m) | none | 1,900 m | **steep** 38 deg over r 45 m (spread 25 m) |
| 18 | The Hutt landing field | 3,400 / -2,300 | 106.2 | 44 m: z 105 (terrain there 105.6) | none (nearest ossus_gokob L10, 5,824 m) | none | 3,640 m | none |
<!-- /POI_TABLE -->

Notes on each place (what moved and why):

<!-- POI_NOTES -->
- **1 Academy ruins: craters, drop pod, memorial ring** (20 objects). Craters 4 and 5 are 2.0 m deep, not o6's 1.5 and 1.0 m (the owner said 2-4 m). o6 put the drop pod at (2160, 2700), 92 m from the nearest crater, so it stands on the south lip of crater 2 instead. The two fallen temple pillars o6 mentions are already in the snapshot (nothing new).
- **2 The hidden sanctuary** (6 objects). Moved 120 m from o6's (2,016, 2,848). A flatland cave on the benchland south-south-east of the hall, its mouth facing the hall, in the rubble apron; chosen as the nearest mouth distance (120-230 m from the pad centre) where the footprint clears every ruin static, crater and the memorial ring. The interior (cells 1-11 = building id + k) is a screenplay job.
- **3 Krayt's garrison (benchland rim) and its dig** (49 objects). Moved 6,535 m from o6's (600, -3,300). The owner's answer of 15 Oct: the garrison sits on the benchland rim over the ruins, guarding the dig, not by Knossa; o6's (600, -3300) site is dropped. Flat ground (2 m of relief over r 40) nearest the crest north-east of the ruins (the ground drops 8 m within 70 m of it); the compound's front faces the ruins and the dig sits between the gate and the hall.
- **4 Great Library vaults and dig camp** (20 objects). Moved 60 m from o6's (2,300, 1,900). o6's (2300, 1900) is 43 m plain, not a summit; the cave stands on the flattest ground 25 m north of it. There is no hill behind it (flatland cave).
- **5 Ysanna hunting camp** (29 objects). Moved 280 m from o6's (-1,200, -5,200). o6's (-1200, -5200) is a 37 degree slope with 36 m of relief in the Eocho band (116 m, not the 180 m o6 assumed). The camp stands on the nearest ground that is flat (1.5 m over r 25), north-north-west at the foot of the mountains. There is no flat ground at 100-200 m within 450 m.
- **6 Ysanna stone circle** (18 objects). Moved 81 m from o6's (-900, -5,600). Moved to the flattest ground within 90 m of o6's point; still a mountain shoulder (ground 4-5 m of relief over the ring).
- **8 Adega Lake fishing hamlet** (24 objects). Moved 250 m from o6's (-2,900, 1,300). o6's (-2900, 1300) is 52 m up a 9 degree hillside; the hamlet stands 250 m south-west at the lake edge, 5 m above the water, with a short pier (three walkways and a platform) whose deck is set 1 m over the 38.5 m water, the one place objects stand on or over water.
- **9 Kathracite adit** (17 objects). Moved 102 m from o6's (4,500, -300). o6's (4500, -300) is on the canyon wall (spread 40 m). The cave stands on the floor against the wall, 100 m away, mouth facing the canyon centre line; the back of the mound is buried in the wall.
- **10 Imhar Canyon crossing** (10 objects). Moved 240 m from o6's (4,300, -700). Measured across the canyon every 40 m along its path, the narrowest places are 284-292 m between the 100 m contours (the painted floor half width swings 0.65 to 1.35 of 90 m, the walls are 100 m); several such places exist, so the span is put at one 240 m up the canyon from o6's vertex (4300, -700) and runs north-west to south-east (142 m of walk each side of the centre line).
- **11 Knossa old town** (25 objects). Inside Knossa's city circle (r 200) and no-build circle (r 320). The starport footprint (48 x 30 m) and the shuttle pad stay clear.
- **12 The Jedi memorial road** (16 objects). A line of 16 pillars 8-12 m off the road, one at the end of each 480 m piece; the centre shown is the middle marker.
- **13 Eocho watch ruin** (12 objects). The summit shoulder at o6's point is the best within 60 m (steep; each static takes its own ground height).
- **14 Sith interrogation post** (10 objects). Moved 6 m from o6's (-2,976, -4,960). Outside dressing only. The cave node (6900002) and its 10 cell nodes already exist; the cells are dressed by screenplay.
- **15 Crashed Alliance fighter** (10 objects). At o6's point (flat plain, 62 m).
- **16 Ysanna sky-burial cliff** (11 objects). Moved 260 m from o6's (5,000, 900). o6's (5000, 900) is flat mesa top 280 m from the nearest canyon rim. The platform stands 16 m back from that rim point.
- **17 Supernova glass plain (terrain only)** (0 objects). Terrain only (terrain.json layer 'o7 supernova glass plain'). The ground there is a 105 m, 41 degree mountain slope: the layer paints and clears it, it does not make a plain. The flat alternative (spread 12.6 m) is the foothills at x 1850-2450, y -4800 to -4500.
- **18 The Hutt landing field** (18 objects). o6's camp building (object/building/poi/shared_tatooine_hutt_businessmen_camp_medium) is a server theater anchor with no art, so the field is built from statics: a landing pad, tents, pallets, crates.
<!-- /POI_NOTES -->

What each place holds (object counts by role; the garrison is a 48 x 40 m walled compound facing the ruins with a dig 36-62 m in front of its gate):

<!-- POI_CONTENTS -->
- **1 Academy ruins: craters, drop pod, memorial ring** (20): crater debris x12, downed drop pod (crater 2 south lip), pod hatch, memorial pillar x6
- **2 The hidden sanctuary** (6): hidden sanctuary (cave, 12 cells), rubble at the mouth x2, fallen pillar at the mouth x2, half-buried pillar base
- **3 Krayt's garrison (benchland rim) and its dig** (49): perimeter wall x8, wall column x6, banner at the gate x2, guard tower x2, commander's quarters, barracks 1, barracks 2, supplies x4, crates x6, drums x2, lamp post x3, brazier fire, dig tent x3, spoil cart x2, spoil bucket x2, dig fire, cot x2, dug-up pillar, dug-up pillar base
- **4 Great Library vaults and dig camp** (20): Great Library vault (cave, 12 cells), half-buried pillar base x3, fallen pillar x2, pillar stub at the door, scholars tent x2, store tent, camp fire, cot x2, crates x2, supplies x2, lamp post, bucket, recovered pillar
- **5 Ysanna hunting camp** (29): camp fire pit, hide tent (hut) x3, shaman's stone hut, hide rack x3, spear rack x3, cooking stone x2, mud oven, bone trophy x4, boundary totem x4, camp fence x7
- **6 Ysanna stone circle** (18): standing stone x7, ritual fire pit, bone totem x3, bone offering x3, outlying stone x4
- **8 Adega Lake fishing hamlet** (24): hamlet fire pit, fisher house x3, fish and net rack x4, net-drying rack, cooking stone, bait basket x3, garden fence x5, shore post x2, pier walkway x3, pier platform
- **9 Kathracite adit** (17): kathracite adit (cave, 30 cells), ore cart x3, timber prop x4, lamp x2, bucket x2, pipes, crusher, supplies, crate, drum
- **10 Imhar Canyon crossing** (10): bridge span x10
- **11 Knossa old town** (25): market tent (with interior) x3, market tent x4, market goods x5, stock pallets x2, street lamp x2, cantina, hovel x2, ruined wall x2, ruined pillar x2, junk dealer shed, collapsed hut
- **12 The Jedi memorial road** (16): road marker x16
- **13 Eocho watch ruin** (12): watch tower base x2, standing pillar, standing pillar (broken), fallen pillar x2, wall stub x3, low pillar, boulder x2
- **14 Sith interrogation post** (10): banner at the mouth x2, crates x3, drums x2, supply pallet, field terminal (outside), cold campfire
- **15 Crashed Alliance fighter** (10): crashed Alliance fighter, wreckage x5, survivor's tent, camp fire, cot, salvaged crate
- **16 Ysanna sky-burial cliff** (11): wooden burial platform, bone totem x4, bone offering x3, laid-out bones, spear rack x2
- **18 The Hutt landing field** (18): landing pad, broker tent x4, cargo pallets x4, spice crates x4, landing light x2, camp fire, fuel drum x2
<!-- /POI_CONTENTS -->

## 4. Statics and the snapshot (`statics.json`)

- 295 objects, ids 6900087-6900461 (o2's snapshot uses 6900000-6900086). A building takes its own id and one id per interior cell 1..cells-1 (cell k is `building id + k`); 12 buildings add 80 cell nodes, so the snapshot grows from 87 to 462 nodes (45,291 bytes).
- Yaw is a compass heading (0: the object's +z faces north), the convention of o2's `stage_snapshot.py`. z is the ground height at the object's origin, as o2 placed the ruins; objects whose origin is mid-height (the escape pod, rocks, bases) are therefore half-buried by design. The three flatland caves are lowered so their entrance floor meets the ground (origin = ground at the mouth - 3.85 m, from portal 0's lowest vertex), the rule o2 calibrated for the hillside caves.
- Nodes carry the float stock snapshots use for the same template (the most common value in the stock and MTG snapshots, else 200) and, for buildings, 512 and the portal layout's CRC chunk.
- Interiors (cave cells, sheds, towers, tents) are not dressed here. Cell ids for the screenplay: sanctuary 6900107-6900118, vault 6900193-6900204, adit 6900295-6900324 (cave node, then cells 1..n-1), the garrison's tower/sheds 6900140-6900164, the market tents 6900351-6900356, the cantina 6900370-6900376. The west foothill cave (POI 14) is o2's node 6900002 with cells 6900003-6900013.
- `tools/append_snapshot.py` reads o2's `ossus.ws`, drops any node already in the o7 id range, appends the statics (adding `object/cell/shared_cell.iff` and any new template to the template list) and re-checks the result: byte round trip identical, ids unique and unused by every snapshot the client loads (29 scanned), every template in the client archives and in the merged CRC table.

## 5. Checked, and not checked

Checked (all in `checks.json`, regenerate with `tools/run_all.py`, about four minutes; only the server-template lookup is a separate WSL step, `tools/server_check.sh`; after any change to `o7_pois.py` run `run_all.py`, then `render_tables.py`):
- templates: stock table, client files, appearances, Core3-dev server templates (above); one piece dropped (`allum_mine_console_s01`: its appearance is not in the client);
- no overlaps among the 295 objects or with the 31 ruin statics and the starport footprint (separating-axis test on each template's footprint box; for the flatland caves the open apron in front of the mouth is left free);
- no object stands on ground at or under the 38.5 m water except the pier pieces (deck height 39.5 m); none inside a crater's burn zone except POI 1's own;
- buildings against the ground: the sanctuary and vault fit (ground 3.5-6.8 m above their origin, inside the mesh range); the adit's mound is buried in the canyon wall at the back by design;
- building nodes against stock: the guard towers, officer's shed, barracks, cantina shed, merchant tent and `cave_08_flatland_s03` (MTG Moraband's node) carry exactly the portal-layout CRC and cell-node count the existing snapshots give the same template (`checks.json` -> `building_node_vs_stock`); `cave_06_flatland_s01_damprock` and `cave_07_flatland_s02` have no node anywhere to compare;
- the snapshot append (above); the terrain build and survey (section 2).

Not checked, because it needs the client or the galaxy: what the craters, scorch, glass and fields look like; whether the new shaders blend; the three flatland caves (no stock snapshot places one; MTG's Moraband places a `cave_08_flatland_s03`), including whether their mouths meet the ground and whether the 12 to 30 cells load; the pier's deck against the water and the bridge (an unsupported 325 m deck, 105.5 m, resting on the mesa at both ends); every `z` of a mid-origin static; that the garrison buildings' doors face the courtyard (taken from the pob portal 0 positions); spawn behaviour of the anchors. All of it is "untested" until the owner's client visit.

## 6. Steps for Claude (in order)

Nothing here needs the server lock until step 5. Run from `outputs`, Windows Python `C:/Users/Pengw/miniconda3/python.exe -I`.

1. **Terrain.** `Fable-ossus/o7-build/tools/o7_terrain.py build --stage` (about 100 s; add `--out DIR` instead of `--stage` for a throwaway build). It rewrites `Fable-ossus/staged/client/terrain/ossus.trn` (42,834 bytes, the TGAs come out byte-identical) and `Fable-ossus/out/ossus-report.json`, `ossus-sites.json`, `ossus-height.png`. Expect `VERDICT: PASS`. Without `--stage` it builds into a temp folder instead.
2. **Snapshot.** `Fable-ossus/o7-build/tools/append_snapshot.py --stage`: rewrites `Fable-ossus/o2/staged/client/snapshot/ossus.ws` (87 -> 462 nodes). Rerunnable. Do not run o2's `stage_snapshot.py` afterwards (it writes the 87-node file again); if you must, run this again.
3. **Region labels** (o6 section 2, client side): add `westmarch` / "Westmarch" at (-5344, 96) r 400 and `knossa_fields` / "Knossa Fields" at (1500, -3300) r 450 to `REGIONS` in `Fable-ossus/tools/stage_env.py`, rerun it with `python -I Fable-ossus/tools/stage_env.py` (it writes `datatables/clientregion/ossus.iff` and `string/en/ossus_region_names.stf`, plus the unchanged environment and loading files). Server regions: nothing to add to `ossus_regions.lua`. The sanctuary and 45 of the garrison's 49 objects lie inside the ruins' r 260 no-spawn circle (the other four are 5 to 6 m outside it; widen the circle to 270 if lairs show up at the walls), and the fields stay ordinary spawnable ground as o6 asked.
4. **Archive.** `Fable-ossus/o5/build_test_archive.py` (Hoth + Ossus; it takes `terrain/ossus.trn` from `staged/client` and `snapshot/ossus.ws` from `o2/staged/client`), install it where o5 says, restart the test galaxy under the standing OK (no owner client running, no squad round).
5. **Spawns and screenplays** from `poi-placements.json` -> `npc_points`: garrison (commander, gate and tower sentries, courtyard troopers, a rim patrol, the dig overseer and workers), the sanctuary lookout and the hidden Jedi (inside cells 1-11 of node 6900107), Ysanna at POIs 5 and 6 (ritual dancers at night), fishers, the adit foreman and miners, the canyon ambush, Knossa's recruiter, artisans, junk dealer and cantina patrons, the Alliance pilot, the Hutt broker and buyers, the Sith post's guard. Each row names stock mobile templates that exist in dev as suggestions (`mobile_candidates`); there is no `sith_*` template, so Krayt's troopers are `dark_trooper` / `stormtrooper_*` / `imperial_inquisitor` until the owner wants better. Creature levels are untouched.
6. **In-game check** (`/teleport x y ossus`): the five craters (1870 2930, 2140 2790, 2010 3010, 1930 2700, 2210 2920), the memorial ring (1960 2780), the sanctuary mouth (2057 2735), the garrison gate (2148 3030) and the dig (2131 3006), Westmarch (-5344 96) and Knossa Fields (1500 -3300) for a 300 m walk, the vault (2300 1925), the Ysanna camp and circle, the hamlet and pier, the adit (4590 -310), the bridge (4470 -530), the old town (0 -3660), the first and last road markers, the watch ruin, the west cave apron, the crashed fighter (-1500 5200), the burial platform, the Hutt field (3400 -2300). Report: floating or buried pieces (especially the three flatland caves and the pier), craters too steep to walk, white or purple ground, a bridge that floats.

## 7. Open

- Owner: crater 4 and 5 raised to 2.0 m (o6 had 1.5 and 1.0); the pod on crater 2's lip instead of at (2160, 2700); field feather 0.3 instead of "0.5 over 100 m"; POI 17 on a steep slope (keep, or move to the flat foothill window); the moves of POIs 5, 6, 8, 9, 10 and 16 (notes above).
- Fable's later pass: the interiors of POIs 2, 4, 9 and 14 (cells, props, the vault door), the story text and datapads, the Hutt broker's conversation, the held POI 7.
- If the first client look shows the flatland caves floating or sunk, only the three `z` values of the caves in `statics.json` and `CAVE_FLOOR` in `tools/o7_pois.py` change.
