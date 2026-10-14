-- Hoth area spawn group "hoth_scavenger_zone" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_scavenger_zone = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_scavenger_raider_camp_neutral_none",
			spawnLimit = -1,
			minDifficulty = 74,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 50,
			size = 25,
		},
		{
			lairTemplateName = "hoth_tauntaun_herd_neutral_none",
			spawnLimit = -1,
			minDifficulty = 65,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 25,
			size = 25,
		},
		{
			lairTemplateName = "hoth_ice_mynock_pack_neutral_none",
			spawnLimit = -1,
			minDifficulty = 67,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 25,
			size = 25,
		},
	}
}

addSpawnGroup("hoth_scavenger_zone", hoth_scavenger_zone);
