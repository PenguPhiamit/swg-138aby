-- Nal Hutta (PL-04): the deep swamp, 3,200 to 5,200 m from Bilbousa. Levels 37 to 56: the lowland hunters thin out
-- and mire marauders (56) hunt in packs. No lair building here yet, so no destroy missions this far out.
hutta_deep_swamp = {
	lairSpawns = {
		{
			lairTemplateName = "naboo_rogue_fambaa_neutral_none",
			spawnLimit = -1,
			minDifficulty = 37,
			maxDifficulty = 42,
			numberToSpawn = 15,
			weighting = 20,
			size = 20,
		},
		{
			lairTemplateName = "rori_dreaded_vir_vur_neutral_none",
			spawnLimit = -1,
			minDifficulty = 38,
			maxDifficulty = 43,
			numberToSpawn = 15,
			weighting = 20,
			size = 20,
		},
		{
			lairTemplateName = "endor_blurrg_diseased_neutral_none",
			spawnLimit = -1,
			minDifficulty = 37,
			maxDifficulty = 42,
			numberToSpawn = 15,
			weighting = 15,
			size = 20,
		},
		{
			lairTemplateName = "talus_mire_marauder_neutral_none",
			spawnLimit = -1,
			minDifficulty = 55,
			maxDifficulty = 60,
			numberToSpawn = 15,
			weighting = 25,
			size = 25,
		},
	}
}

addSpawnGroup("hutta_deep_swamp", hutta_deep_swamp);
