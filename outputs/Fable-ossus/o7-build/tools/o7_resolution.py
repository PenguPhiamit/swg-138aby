"""The "(confirm)" items of o6 and what each resolved to against the client's object template list. Our own data (Claude,
16 Oct 2026). make_o7.py checks every path here (stock CRC table, client file and appearances, server template) and writes
../template-resolution.json. 'chosen' lists only paths that statics.json or terrain.json really use."""
from o7_pois import BE, BG, BM, CO, DA, G, IT, MIL, TA

SHADER = 'shader/%s.sht'

RESOLUTION = [
    {'o6': 'POI 1 craters: shader ACCN to a dark burnt ground (candidates shader/must_ash_* (confirm), else Dathomir black rock)',
     'poi': 1, 'status': 'resolved: other stock shaders', 'shaders': [SHADER % n for n in (
         'dirt_scorched_tornearth', 'dirt_scorched_tornearth_a1', 'dirt_scorched_tornearth_a2',
         'dirt_scorched_earth', 'dirt_scorched_earth_a1', 'dirt_scorched_earth_a2', 'rock_mtns_whitelimestone')],
     'why': 'No shader/must_ash_* exists (the Mustafar terrain uses rock_mustafar_*, MTG art, not needed). Stock Yavin 4 already '
            'ships dirt_scorched_tornearth (crater floor) and dirt_scorched_earth (scorch fans; Endor uses it too); the glass pan keeps o6\'s "limestone family '
            'already in the file" (rock_mtns_whitelimestone). ACCN is a vertex-colour affector in the stock files, not a shader, so the shader '
            'goes in as ASCN (shader family constant), the affector every stock layer uses for ground shaders.'},
    {'o6': 'POI 1 rubble apron: ACRF radial/flora off inside, rocks on', 'poi': 1, 'status': 'resolved: other affectors',
     'chosen': [], 'why': 'ACRF is a colour-ramp-by-fractal affector. The apron uses the file\'s own flora affectors: clear_flora() (the removal pattern '
                          'Dantooine\'s stock layers use) over r 130, then AFSC (rocks, family 4) outside r 60.'},
    {'o6': 'POI 1 blast debris: shared_debris_* stock piles (confirm names; Endor and Corellia have object/static/structure/general/shared_debris_*)',
     'poi': 1, 'status': 'resolved: other names',
     'chosen': [G % 'poi_all_construction_stone_pile', G % 'poi_all_construction_metal_pile', G % 'atst_debris_01', G % 'atat_debris_01', G % 'atat_debris_02',
                G % 'transport_debris_02', G % 'prp_junk_s5'],
     'why': 'The shared_debris_* names that exist are all Death Star pieces (conduit, tubes, turbolaser): wrong for a ground attack. The same folder has '
            'rubble and wreck pieces; stone and metal piles for the lips, an AT-ST and AT-AT wreck, a transport hull section and a junk heap for the Sith and Imperial ground forces.'},
    {'o6': 'POI 1 downed Imperial drop-pod or shuttle: Tatooine shared_crashed_ship_* or Dantooine crashed escape pod (confirm)', 'poi': 1,
     'status': 'resolved: other name', 'chosen': [G % 'escape_pod', G % 'escape_pod_door'],
     'why': 'No shared_crashed_ship_* exists. object/static/structure/general/shared_escape_pod.iff (3.9 x 8.5 m, 18 stock snapshot nodes) is the drop pod. '
            'The destroyed Lambda shuttle (object/static/worldbuilding/vehicles/shared_lambda_shuttle_static_destroyed.iff) is MTG-only, not mapped to a catalogue P row: not used.'},
    {'o6': 'POI 1 memorial: six standing stones (stock shared_marker_*/Dantooine standing stones (confirm))', 'poi': 1, 'status': 'resolved: other name',
     'chosen': [DA % 'dant_jedi_temple_pillar_sm'],
     'why': 'No shared_marker_* exists. poi_all_monolith_s01 is 36 m tall and gravestone_generic_style_* are 0.7 m: both wrong. The Dantooine temple\'s own '
            'short pillar (2 x 4.7 m, 24 uses here) reads as a Jedi memorial stone and is already in the ruins set.'},
    {'o6': 'POI 2 sanctuary: shared_cave_01 or a cellar .pob from the stock bunker set (confirm); holocron pedestal decor shared_holocron_* (confirm)', 'poi': 2,
     'status': 'resolved: other name; holocron decor has no static', 'chosen': [BG % 'cave_06_flatland_s01_damprock'],
     'why': 'The ruins pad is flat ground with no hillside, so the self-contained flatland variant of cave_01 is used (same 13-portal layout as cave_01_damprock, '
            'damp-rock look; 12 cells). The bunker interiors are Imperial concrete. No holocron static or pedestal exists in the stock table: the stock item '
            'object/tangible/jedi/shared_jedi_holocron_light.iff can be created by script, and the Dantooine altar static (object/static/structure/dantooine/shared_dant_jedi_temple_altar.iff) '
            'is the pedestal. Interior contents are a screenplay job (cell ids = building id + 1..11).'},
    {'o6': 'POI 3 garrison: object/building/military/shared_military_guard_tower, shared_military_outpost_* (confirm)', 'poi': 3, 'status': 'resolved: other names',
     'chosen': [BM % 'mun_all_military_tower_impl_guard_s01', BM % 'military_base_shed_imperial_style_officer_s01', BM % 'military_base_shed_imperial_barracks_s01',
                MIL % 'military_wall_strong_imperial_32_style_01', MIL % 'military_wall_strong_imperial_16_style_01', MIL % 'military_wall_strong_imperial_style_01',
                MIL % 'military_column_strong_imperial_style_01', G % 'banner_imperial_style_01'],
     'why': 'shared_military_guard_tower does not exist; shared_military_outpost_guard_tower_1 does (no portal layout, no interior) but the guard tower with a door '
            'and two cells, mun_all_military_tower_impl_guard_s01, is what the Yavin 4 snapshot places (ten of them). The sheds are the Imperial-style buildings Corellia, Rori, Lok, Naboo and Dantooine place '
            '(a node plus 6 cells each).'},
    {'o6': 'POI 4 vaults: third stock cave (cave_02 flatland variant) + Dantooine temple pillars', 'poi': 4, 'status': 'resolved',
     'chosen': [BG % 'cave_07_flatland_s02', DA % 'dant_jedi_temple_pillar_base', DA % 'dant_jedi_temple_pillar_fallen', DA % 'dant_jedi_temple_pillar_sm'],
     'why': 'cave_07_flatland_s02 is the flatland variant of the cave_02 layout (14 portals, 12 cells).'},
    {'o6': 'POI 5 Ysanna camp: stock Tusken/Dantari-style camp statics (hide tents, racks, a fire)', 'poi': 5, 'status': 'resolved',
     'chosen': [DA % n for n in ('dant_small_mudhut', 'dant_large_rock_hut', 'dant_hide_tanning_s01', 'dant_hide_tanning_s02', 'dant_rack_spears', 'dant_cooking_stone',
                                 'dant_mud_oven', 'dant_fire_pit', 'dant_skull_bol', 'dant_skull_thune', 'dant_skull_lizard', 'dant_totem_pole', 'dant_fence_8m')],
     'why': 'The Dantooine Dantari camp set, the same pieces Dantooine\'s stock snapshot places in bulk (fence_8m 151 nodes, totem poles 66, spear racks 42).'},
    {'o6': 'POI 6 stone circle: standing stones + a fire pit + bone totems', 'poi': 6, 'status': 'resolved',
     'chosen': [G % 'rock_mossy_big', G % 'rock_mossy_big_a1', G % 'tato_cave_rock_large', DA % 'dant_fire_pit', DA % 'dant_totem_pole', DA % 'dant_skull_thune'],
     'why': 'Boulders for the stones (no stock standing-stone static of a sensible size), the Dantooine fire pit and totem poles.'},
    {'o6': 'POI 8 hamlet: Dantooine farmstead set, a dock of Naboo pier pieces, nets', 'poi': 8, 'status': 'resolved: Endor pier instead of Naboo',
     'chosen': [DA % 'dant_small_mudhut', DA % 'dant_large_mudhut', DA % 'dant_fish_rack', DA % 'dant_hide_tanning_s01', DA % 'dant_fence_8m', DA % 'dant_boundary_post',
                BE % 'endor_lake_walkway_straight', BE % 'endor_lake_platform', IT % 'item_basket_closed'],
     'why': 'No Naboo pier statics exist (the seawall_* pieces are Theed harbour walls). Endor\'s wooden lake walkway and platform (60 and 41 stock snapshot nodes, '
            'one Dantooine snapshot also uses them) are the dock; dant_fish_rack are the nets and racks.'},
    {'o6': 'POI 9 adit: stock mine entrance static + ore carts + a lamp string; the cave mouth is a flatland cave', 'poi': 9, 'status': 'resolved: allum_mine_* statics; one piece dropped',
     'chosen': [BG % 'cave_08_flatland_s03', G % 'allum_mine_car_s01', G % 'allum_mine_support_s01', G % 'allum_mine_wall_lamp_s01', G % 'allum_mine_bucket_s01',
                G % 'allum_mine_pipes_s01', G % 'allum_mine_device_s01'],
     'why': 'The stock allum-mine set is exactly the ore carts, timbers, lamps, buckets, pipes and crusher; the cave mouth is cave_08_flatland_s03 (30 cells). '
            'object/building/general/shared_bunker_allum_mine.iff exists (Endor uses it) but its entrance portal lies 5 to 8 m below the building origin and needs a pit, so it is not used. '
            'allum_mine_console_s01 names appearance/bunker_mine_console_s01.apt, which is not in the client archives: dropped (the crafting station is a script object).'},
    {'o6': 'POI 7 Vong project fields: MTG/stock Kashyyyk Vong statics if the merged table has them (confirm shared_vong_* names)', 'poi': 7,
     'status': 'held by the owner (15 Oct); recorded only', 'chosen': [],
     'why': 'Not placed. For the record: the stock table and the installed merged table (29,358 names) have no shared_vong_*, yuuzhan, coral, damutek or voxyn template '
            '(the only match for "coral" is a player-style mobile, dressed_coraline_dynes), so the fields will need new art or Dathomir and Mustafar stand-ins when the voxyn content exists.'},
    {'o6': 'POI 10 crossing: Naboo or Corellian bridge pieces (confirm a static bridge exists; else platform pieces)', 'poi': 10, 'status': 'resolved: Tatooine bridge',
     'chosen': [TA % 'bridge_tatooine_small_style_03'],
     'why': 'Static bridges exist: Tatooine small_style_01/02/03 (8, 16, 32 m), Corellia imprv_bridge_sm/lg (16, 28 m), Naboo bridge_naboo_theed_style_1 (50 m). '
            'The 32.5 m Tatooine piece (Lok places ten) chains 10 times (325 m) over the 284 m rim-to-rim span, with about 20 m resting on each rim. Nothing in stock supports a span this long: the deck is unsupported.'},
    {'o6': 'POI 11 old town: Tatooine/Dantooine filler blocks, merchant tents, stock Dantooine cantina', 'poi': 11, 'status': 'resolved',
     'chosen': [BG % 'merchant_tent_all_s01', CO % 'corl_tent_large', CO % 'corl_tent_med', BM % 'military_base_shed_imperial_style_cantina_s01', TA % 'stone_hovel_tatooine_style_01',
                TA % 'shed_junkshop_watto', TA % 'wall_ruined_tatooine_large_style_01', TA % 'wall_ruined_tatooine_large_style_02', TA % 'pillar_ruined_large_style_01',
                TA % 'pillar_ruined_small_style_01', DA % 'dant_large_rock_hut_dest'],
     'why': 'There is no separate Dantooine cantina object: Dantooine\'s own snapshot uses the Imperial-style shed with the cantina name (military_base_shed_imperial_style_cantina_s01). '
            'The merchant tent has a one-room interior.'},
    {'o6': 'POI 12 road markers: small standing stones or lamp posts', 'poi': 12, 'status': 'resolved', 'chosen': [DA % 'dant_jedi_temple_pillar_sm'],
     'why': 'The same short temple pillar as the memorial.'},
    {'o6': 'POI 13 watch ruin: Dantooine temple base + one pillar, Yavin-style tower stub (confirm)', 'poi': 13, 'status': 'resolved; no tower stub',
     'chosen': [DA % 'dant_jedi_temple_pillar_base', DA % 'dant_jedi_temple_pillar', DA % 'dant_jedi_temple_pillar_med', DA % 'dant_jedi_temple_pillar_fallen',
                DA % 'dant_jedi_wall_1', DA % 'dant_jedi_wall_2', DA % 'dant_jedi_temple_pillar_sm'],
     'why': 'The Yavin 4 temples are whole buildings with interiors (object/building/yavin/temple_*), not stubs; the Dantooine pieces make the tower footing.'},
    {'o6': 'POI 14 Sith post: stock Imperial crates, a cage, a terminal', 'poi': 14, 'status': 'resolved (outside); interior by screenplay',
     'chosen': [MIL % 'bunker_crate_style_01', G % 'data_terminal_free_s2', G % 'banner_imperial_style_01', G % 'palette_supply_02', G % 'campfire_burnt'],
     'why': 'Outside dressing only. For the cells: object/static/item/shared_item_cage_bamboo.iff (1 x 0.8 m cage), shared_item_door_impl_s01.iff (Imperial door), '
            'shared_item_datapad_s1.iff exist as statics a screenplay can create inside the cave\'s cells.'},
    {'o6': 'POI 15 crashed fighter: stock crashed X-wing/A-wing static (confirm shared_crashed_*)', 'poi': 15, 'status': 'resolved: other name', 'chosen': [G % 'xwing'],
     'why': 'No shared_crashed_* statics; object/static/structure/general/shared_xwing.iff (13 x 15.6 m, 5 stock snapshot nodes) is the fighter. There is no A-wing static; the X-wing plus wreckage piles do the job.'},
    {'o6': 'POI 16 sky burial: bone totems, a wooden platform', 'poi': 16, 'status': 'resolved',
     'chosen': [DA % 'dant_totem_pole', DA % 'dant_skull_bol', G % 'skeleton_human_headandbody', BE % 'endor_lake_platform', DA % 'dant_rack_spears'],
     'why': 'Dantooine totem poles and skulls; Endor\'s wooden lake platform is the burial platform.'},
    {'o6': 'POI 18 Hutt landing field: object/building/poi/shared_tatooine_hutt_businessmen_camp_medium.iff (verified to exist in the client)', 'poi': 18,
     'status': 'not usable as a camp; composed from statics',
     'chosen': [G % 'landing_pad_transport', CO % 'corl_tent_hut_s01', IT % 'item_crate_spice'],
     'why': 'The path exists, but the client template carries only terrainModificationFileName terrain/poi_medium.lay and no appearance: it is a server theater anchor '
            '(Core3 creates the camp\'s contents), so placed in a snapshot it is an invisible flattening. The field is built from a stock landing pad, tents, pallets and crates. '
            'object/mobile/shared_hutt_male.iff (the Hutt broker\'s body) exists in the client and in dev.'},
]
