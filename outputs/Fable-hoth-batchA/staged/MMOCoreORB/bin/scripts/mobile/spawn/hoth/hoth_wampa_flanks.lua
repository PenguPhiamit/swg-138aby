-- Hoth area spawn group "hoth_wampa_flanks" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_wampa_flanks = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_wampa_neutral_none",
			spawnLimit = -1,
			minDifficulty = 90,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 45,
			size = 25,
		},
		{
			lairTemplateName = "hoth_wampa_lair_neutral_large",
			spawnLimit = -1,
			minDifficulty = 90,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 35,
			size = 25,
		},
		{
			lairTemplateName = "hoth_tauntaun_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 65,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 20,
			size = 25,
		},
	}
}

addSpawnGroup("hoth_wampa_flanks", hoth_wampa_flanks);
