-- Hoth area spawn group "hoth_mynock_fields" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_mynock_fields = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_ice_mynock_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 67,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 50,
			size = 25,
		},
		{
			lairTemplateName = "hoth_ice_mynock_lair_neutral_medium",
			spawnLimit = -1,
			minDifficulty = 67,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 40,
			size = 25,
		},
		{
			lairTemplateName = "hoth_wampa_neutral_none",
			spawnLimit = -1,
			minDifficulty = 90,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 10,
			size = 25,
		},
	}
}

addSpawnGroup("hoth_mynock_fields", hoth_mynock_fields);
