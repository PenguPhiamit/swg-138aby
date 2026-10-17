-- Imhar Canyon: kaddyr bug swarms and tree frogs on the floor and the rims.
-- Dynamic encounters keep creature base levels (O8, 17 Oct: more wildlife where the census found none).
ossus_canyon = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_kaddyr_bug_swarm_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 5,
			weighting = 55,
			size = 20,
		},
		{
			lairTemplateName = "ossus_tree_frog_solitary_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 1,
			weighting = 45,
			size = 20,
		},
	}
}

addSpawnGroup("ossus_canyon", ossus_canyon);
