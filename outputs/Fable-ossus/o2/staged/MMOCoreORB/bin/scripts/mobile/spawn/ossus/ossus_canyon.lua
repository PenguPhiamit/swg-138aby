-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_canyon = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_kaddyr_hive_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 30,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kaddyr_swarm_neutral_none",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 30,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kirruk_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 48,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 25,
			size = 25,
		},
		{
			lairTemplateName = "ossus_gokob_den_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 22,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
	}
}

addSpawnGroup("ossus_canyon", ossus_canyon);
