-- Nal Hutta (PL-04): the Hutta lowlands, 1,600 to 3,200 m from Bilbousa. Levels 31 to 38: fambaa herds in the
-- open marsh, festering squills, fierce borgles and the hunters that follow them (swamp tusk cat stalkers, diseased
-- blurrgs, rogue fambaa, dreaded vir vurs).
hutta_lowlands_mid = {
	lairSpawns = {
		{
			lairTemplateName = "endor_squill_festering_neural_small",
			spawnLimit = -1,
			minDifficulty = 31,
			maxDifficulty = 36,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "endor_borgle_fierce_neutral_small",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 37,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "naboo_swamp_tusk_cat_stalker_neutral_none",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 37,
			numberToSpawn = 15,
			weighting = 15,
			size = 20,
		},
		{
			lairTemplateName = "naboo_fambaa_lair_neutral_large",
			spawnLimit = -1,
			minDifficulty = 34,
			maxDifficulty = 39,
			numberToSpawn = 15,
			weighting = 20,
			size = 30,
		},
		{
			lairTemplateName = "naboo_fambaa_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 34,
			maxDifficulty = 39,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "endor_blurrg_diseased_neutral_none",
			spawnLimit = -1,
			minDifficulty = 37,
			maxDifficulty = 42,
			numberToSpawn = 15,
			weighting = 10,
			size = 20,
		},
		{
			lairTemplateName = "naboo_rogue_fambaa_neutral_none",
			spawnLimit = -1,
			minDifficulty = 37,
			maxDifficulty = 42,
			numberToSpawn = 15,
			weighting = 10,
			size = 20,
		},
	}
}

addSpawnGroup("hutta_lowlands_mid", hutta_lowlands_mid);
