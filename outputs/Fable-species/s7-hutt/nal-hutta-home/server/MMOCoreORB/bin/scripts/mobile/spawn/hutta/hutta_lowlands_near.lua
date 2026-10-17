-- Nal Hutta (PL-04): the swamp ring round Bilbousa, 650 to 1,600 m from the town centre (hutta_regions.lua).
-- Stock creatures of rot and fouled water, levels 19 to 25: players come here after the starter worlds. The five with a
-- lair building are also the planet's destroy-mission targets (spawn/destroy_mission/hutta_destroy_missions.lua).
-- Difficulty bands follow the creature levels, as the stock tables do; creatures keep their template levels.
hutta_lowlands_near = {
	lairSpawns = {
		{
			lairTemplateName = "endor_borgle_putrid_neutral_small",
			spawnLimit = -1,
			minDifficulty = 19,
			maxDifficulty = 25,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "endor_squill_noxious_neutral_small",
			spawnLimit = -1,
			minDifficulty = 19,
			maxDifficulty = 25,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "talus_famished_sludge_panther_lair_neutral_mdium",
			spawnLimit = -1,
			minDifficulty = 20,
			maxDifficulty = 26,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "talus_greater_sludge_panther_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 25,
			maxDifficulty = 30,
			numberToSpawn = 15,
			weighting = 15,
			size = 20,
		},
		{
			lairTemplateName = "endor_borgle_life_sapper_neutral_small",
			spawnLimit = -1,
			minDifficulty = 25,
			maxDifficulty = 30,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "talus_greater_sludge_panther_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 25,
			maxDifficulty = 30,
			numberToSpawn = 15,
			weighting = 10,
			size = 25,
		},
	}
}

addSpawnGroup("hutta_lowlands_near", hutta_lowlands_near);
