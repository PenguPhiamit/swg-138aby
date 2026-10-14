-- Hoth area spawn group "hoth_tauntaun_plains" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_tauntaun_plains = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_tauntaun_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 65,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 60,
			size = 25,
		},
		{
			lairTemplateName = "hoth_tauntaun_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 65,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 40,
			size = 25,
		},
		{
			lairTemplateName = "hoth_probe_droid_neutral_none",
			spawnLimit = -1,
			minDifficulty = 74,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 10,
			size = 25,
		},
	}
}

addSpawnGroup("hoth_tauntaun_plains", hoth_tauntaun_plains);
