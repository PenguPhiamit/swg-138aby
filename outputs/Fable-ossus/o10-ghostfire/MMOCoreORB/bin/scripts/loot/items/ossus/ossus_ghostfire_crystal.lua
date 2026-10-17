-- The ghostfire colour crystal (Ossus ghostfire quest, 17 Oct 2026): given once per character by T'ra Saa's keeper
-- (screenplays/sandbox/ossus_people.lua). Colour 32 is palette entry 32 of palette/wp_lightsaber.pal in our client patch;
-- LightsaberCrystalComponentImplementation lets exactly 32 through. A colour crystal only: no stats.

ossus_ghostfire_crystal = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "Ghostfire Crystal",
	directObjectTemplate = "object/tangible/component/weapon/lightsaber/lightsaber_module_force_crystal.iff",
	craftingValues = {
		{"color",32,32,0},
	},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("ossus_ghostfire_crystal", ossus_ghostfire_crystal)
