-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_world = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_gokob_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 22,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "ossus_gokob_den_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 22,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 10,
			size = 25,
		},
		{
			lairTemplateName = "ossus_tribis_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 28,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "ossus_tribis_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 28,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 10,
			size = 25,
		},
		{
			lairTemplateName = "ossus_bol_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 30,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "ossus_bol_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 30,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 8,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kaddyr_swarm_neutral_none",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kaddyr_hive_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 32,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 8,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kirruk_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 48,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 8,
			size = 25,
		},
		{
			lairTemplateName = "ossus_kirruk_den_neutral_large",
			spawnLimit = -1,
			minDifficulty = 48,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 4,
			size = 25,
		},
	}
}

addSpawnGroup("ossus_world", ossus_world);
