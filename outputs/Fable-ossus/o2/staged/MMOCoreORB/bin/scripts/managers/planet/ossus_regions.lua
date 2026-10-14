require("scripts.managers.planet.regions")

-- Sandbox: Ossus regions (Fable batch O2, 14 Oct 2026). Sites from outputs/Fable-ossus/out/ossus-sites.json (the terrain
-- survey): Knossa pad, the Academy ruins pad, three cave mouths; spawn areas on flat ground off the pad, the benchland and
-- the lake. Groups are in mobile/spawn/ossus/. Region name keys are in string/en/ossus_region_names.stf (batch O1).
ossus_regions = {
	-- No Build Zones
	{"northedge_ossus_nobuild", -8000, 7640, {RECTANGLE, 8000, 8000}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"westedge_ossus_nobuild", -8000, -7640, {RECTANGLE, -7640, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"southedge_ossus_nobuild", -8000, -8000, {RECTANGLE, 8000, -7640}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"eastedge_ossus_nobuild", 7640, -7640, {RECTANGLE, 7999, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},

	-- Knossa (the starport on the flattened pad)
	{"@ossus_region_names:knossa", 0, -3600, {CIRCLE, 200}, CITY + NOSPAWNAREA},
	{"ossus_knossa_nobuild", 0, -3600, {CIRCLE, 320}, NOBUILDZONEAREA},

	-- The Academy ruins (snapshot/ossus.ws) and the cave mouths
	{"ossus_academy_ruins_nobuild", 2016, 2848, {CIRCLE, 260}, NOSPAWNAREA + NOBUILDZONEAREA},
	{"ossus_cave_foothills_west_nobuild", -2976, -4960, {CIRCLE, 120}, NOBUILDZONEAREA},
	{"ossus_cave_foothills_east_nobuild", 4896, -4960, {CIRCLE, 120}, NOBUILDZONEAREA},
	{"ossus_cave_north_nobuild", 1376, 5920, {CIRCLE, 120}, NOBUILDZONEAREA},

	-- Area spawners (placeholder level band 20-60; owner question)
	{"ossus_plains_west", -4400, -1200, {CIRCLE, 1800}, SPAWNAREA, {"ossus_plains"}, 64},
	{"ossus_plains_north", -1500, 5200, {CIRCLE, 1700}, SPAWNAREA, {"ossus_plains"}, 64},
	{"ossus_forest_east", 1200, 5400, {CIRCLE, 1200}, SPAWNAREA, {"ossus_forest"}, 48},
	{"ossus_forest_southwest", -3200, -3400, {CIRCLE, 1000}, SPAWNAREA, {"ossus_forest"}, 48},
	{"ossus_highlands_south", 2600, -4300, {CIRCLE, 1500}, SPAWNAREA, {"ossus_highlands"}, 48},
	{"ossus_canyon_country", 5100, -100, {CIRCLE, 1600}, SPAWNAREA, {"ossus_canyon"}, 48},

	-- World spawner: everything else, outside the no-spawn areas
	{"ossus_world_spawner", 0, 0, {RECTANGLE, 0, 0}, SPAWNAREA + WORLDSPAWNAREA, {"ossus_world"}, 1024},
}
