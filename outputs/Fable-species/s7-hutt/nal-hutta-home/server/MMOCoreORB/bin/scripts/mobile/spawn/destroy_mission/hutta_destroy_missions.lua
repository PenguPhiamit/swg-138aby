-- Nal Hutta destroy-mission lairs for the mission terminals in Bilbousa (PL-04). Same shape as
-- hoth_destroy_missions.lua: MissionManagerImplementation::getRandomLairSpawn reads <zone>_destroy_missions and takes a
-- lair with minDifficulty <= player level + 5 and maxDifficulty >= min(player level - 5, minLevelCeiling). Only lairs
-- with a building can be mission targets. The rows are the lowland lairs of spawn/hutta (levels 19 to 34).
hutta_destroy_missions = {
	minLevelCeiling = 30,
	lairSpawns = {
		{
			lairTemplateName = "endor_borgle_putrid_neutral_small",
			minDifficulty = 19,
			maxDifficulty = 25,
			size = 25,
		},
		{
			lairTemplateName = "endor_squill_noxious_neutral_small",
			minDifficulty = 19,
			maxDifficulty = 25,
			size = 25,
		},
		{
			lairTemplateName = "talus_famished_sludge_panther_lair_neutral_mdium",
			minDifficulty = 20,
			maxDifficulty = 26,
			size = 25,
		},
		{
			lairTemplateName = "endor_borgle_life_sapper_neutral_small",
			minDifficulty = 25,
			maxDifficulty = 30,
			size = 25,
		},
		{
			lairTemplateName = "talus_greater_sludge_panther_lair_neutral_medium",
			minDifficulty = 25,
			maxDifficulty = 30,
			size = 25,
		},
		{
			lairTemplateName = "endor_squill_festering_neural_small",
			minDifficulty = 31,
			maxDifficulty = 36,
			size = 25,
		},
		{
			lairTemplateName = "endor_borgle_fierce_neutral_small",
			minDifficulty = 32,
			maxDifficulty = 37,
			size = 25,
		},
		{
			lairTemplateName = "naboo_fambaa_lair_neutral_large",
			minDifficulty = 34,
			maxDifficulty = 39,
			size = 30,
		},
	}
}

addDestroyMissionGroup("hutta_destroy_missions", hutta_destroy_missions);
