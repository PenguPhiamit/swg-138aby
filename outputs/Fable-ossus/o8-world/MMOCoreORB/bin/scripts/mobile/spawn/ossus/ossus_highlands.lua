-- The Eocho foothills and the benchland rim: kirruk packs and gokob herds.
-- Dynamic encounters keep creature base levels (O8, 17 Oct: more wildlife where the census found none).
ossus_highlands = {
	lairSpawns = {
		{
			lairTemplateName = "ossus_kirruk_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 3,
			weighting = 50,
			size = 20,
		},
		{
			lairTemplateName = "ossus_gokob_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 2,
			maxDifficulty = 2,
			numberToSpawn = 4,
			weighting = 50,
			size = 20,
		},
	}
}

addSpawnGroup("ossus_highlands", ossus_highlands);
