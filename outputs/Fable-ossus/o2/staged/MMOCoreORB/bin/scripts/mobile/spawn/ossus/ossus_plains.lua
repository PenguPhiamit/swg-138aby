-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_plains = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_tribis_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 28,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 40,
			size = 25,
		},
		{
			lairTemplateName = "ossus_tribis_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 28,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
		{
			lairTemplateName = "ossus_bol_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 30,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 30,
			size = 25,
		},
		{
			lairTemplateName = "ossus_bol_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 30,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
		{
			lairTemplateName = "ossus_gokob_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 22,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 30,
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

addSpawnGroup("ossus_plains", ossus_plains);
