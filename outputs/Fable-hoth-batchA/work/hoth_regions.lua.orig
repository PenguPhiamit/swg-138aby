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

	-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).
	-- Outside the outpost (CITY + NOSPAWNAREA, 200 m) and the no-spawn edges.
	{"hoth_world_spawner", 0, 0, {RECTANGLE, 0, 0}, SPAWNAREA + WORLDSPAWNAREA, {"hoth_world"}, 1024},
}
