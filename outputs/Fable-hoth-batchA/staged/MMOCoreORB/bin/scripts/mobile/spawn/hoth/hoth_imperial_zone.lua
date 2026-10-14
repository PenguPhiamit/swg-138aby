-- Hoth area spawn group "hoth_imperial_zone" (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md). Lair templates are the
-- ones ported from Bellum Gero (AGPL-3.0) into mobile/lair/*/hoth; weights and difficulties follow mobile/spawn/hoth/hoth_world.lua.

hoth_imperial_zone = {
	lairSpawns = {
		{
			lairTemplateName = "hoth_snowtrooper_patrol_imperial_none",
			spawnLimit = -1,
			minDifficulty = 76,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 45,
			size = 25,
		},
		{
			lairTemplateName = "hoth_imperial_salvage_team_imperial_none",
			spawnLimit = -1,
			minDifficulty = 72,
			maxDifficulty = 500,
			numberToSpawn = 15,
			weighting = 30,
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
	}
}

addSpawnGroup("hoth_imperial_zone", hoth_imperial_zone);
