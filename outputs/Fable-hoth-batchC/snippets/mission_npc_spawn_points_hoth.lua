
-- Sandbox: Hoth (Fable batch C): mission NPC spawn points for deliver missions at the Scavenger Starport.
-- Same block shape as the generated planets above; spawn type 2 = NEUTRALSPAWN (NpcSpawnPoint.h).
planet_hoth = PlanetSpawnMap:new {
	name = "hoth",
	npcs = {
		{ 62.0, -1975.0, 3.9, 2 },
		{ 70.0, -2030.0, 2.4, 2 },
		{ 30.0, -2060.0, 0.8, 2 },
		{ -45.0, -2070.0, 5.5, 2 },
		{ -60.0, -1985.0, 1.6, 2 },
		{ -40.0, -1925.0, 4.7, 2 },
		{ 40.0, -1935.0, 3.1, 2 },
		{ -140.0, -1990.0, 0.3, 2 }
	}
}

universe:addPlanet(planet_hoth);
