-- Hoth area spawn group "hoth_rebel_zone" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_rebel_zone = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_rebel_snow_patrol_rebel_none",
			spawnLimit = -1,
			minDifficulty = 76,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 60,
			size = 25,
		},
		{
			lairTemplateName = "hoth_probe_droid_neutral_none",
			spawnLimit = -1,
			minDifficulty = 74,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 25,
			size = 25,
		},
		{
			lairTemplateName = "hoth_tauntaun_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 65,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 15,
			size = 25,
		},
	}
}

addSpawnGroup("hoth_rebel_zone", hoth_rebel_zone);
