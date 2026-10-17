-- The 104 m mesa east of Knossa: herds of tribis and gokob, a few kirruk packs.
-- Dynamic encounters keep creature base levels (O8, 17 Oct: more wildlife where the census found none).
ossus_mesa = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_tribis_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 4,
			weighting = 40,
			size = 20,
		},
		{
			lairTemplateName = "ossus_gokob_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 4,
			weighting = 35,
			size = 20,
		},
		{
			lairTemplateName = "ossus_kirruk_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 3,
			weighting = 25,
			size = 20,
		},
	}
}

addSpawnGroup("ossus_mesa", ossus_mesa);
