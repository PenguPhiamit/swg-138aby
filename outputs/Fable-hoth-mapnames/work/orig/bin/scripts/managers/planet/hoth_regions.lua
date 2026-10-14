require("scripts.managers.planet.regions")

-- Sandbox: Hoth regions (Phase 3). Cave positions are MTG's snapshot (the same caves Bellum Gero's Hoth uses);
-- the outpost is MTG's Scavenger Starport at 0 -2000. Names from MTG's string/en/hoth_region_names.stf.
hoth_regions = {
	-- No Build Zones
	{"northedge_hoth_nobuild", -8000, 7640, {RECTANGLE, 8000, 8000}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"westedge_hoth_nobuild", -8000, -7640, {RECTANGLE, -7640, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"southedge_hoth_nobuild", -8000, -8000, {RECTANGLE, 8000, -7640}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"eastedge_hoth_nobuild", 7640, -7640, {RECTANGLE, 7999, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},

	-- The outpost
	{"@hoth_region_names:hothstarport", 0, -2000, {CIRCLE, 200}, CITY + NOSPAWNAREA},
	{"hoth_scavenger_starport_nobuild", 0, -2000, {CIRCLE, 300}, NOBUILDZONEAREA},

	-- The ice caves (MTG snapshot: cave_01..04_ice)
	{"hoth_ice_caves_nobuild", -400, 2600, {CIRCLE, 450}, NOBUILDZONEAREA},

	-- Area spawners (batch A, Fable 14 Oct 2026): the plains, foothills and patrol zones of MTG's map, sited with
	-- outputs/Fable-hoth-batchA/tools/hoth_survey.py (flat ground, away from the outpost, the caves and the massif).
	-- Groups are in mobile/spawn/hoth/. The world spawner below stays as the fallback everywhere else.
	{"hoth_tauntaun_plains_west", -3000, -1500, {CIRCLE, 1800}, SPAWNAREA, {"hoth_tauntaun_plains"}, 64},
	{"hoth_tauntaun_plains_east", 3000, -1200, {CIRCLE, 1500}, SPAWNAREA, {"hoth_tauntaun_plains"}, 64},
	{"hoth_mynock_fields_south", -2000, -4800, {CIRCLE, 1200}, SPAWNAREA, {"hoth_mynock_fields"}, 48},
	{"hoth_wampa_flanks_west", -1800, 3200, {CIRCLE, 900}, SPAWNAREA, {"hoth_wampa_flanks"}, 32},
	{"hoth_wampa_flanks_southeast", 1200, 1500, {CIRCLE, 700}, SPAWNAREA, {"hoth_wampa_flanks"}, 32},
	{"hoth_imperial_zone_east", 2500, -3500, {CIRCLE, 1200}, SPAWNAREA, {"hoth_imperial_zone"}, 48},
	{"hoth_rebel_zone_northwest", -2500, 1000, {CIRCLE, 1200}, SPAWNAREA, {"hoth_rebel_zone"}, 48},
	{"hoth_scavenger_zone_southwest", -1500, -3200, {CIRCLE, 900}, SPAWNAREA, {"hoth_scavenger_zone"}, 48},

	-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).
	-- Outside the outpost (CITY + NOSPAWNAREA, 200 m) and the no-spawn edges.
	{"hoth_world_spawner", 0, 0, {RECTANGLE, 0, 0}, SPAWNAREA + WORLDSPAWNAREA, {"hoth_world"}, 1024},
}
