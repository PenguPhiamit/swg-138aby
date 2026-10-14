-- Hoth destroy-mission lairs for the general mission terminals at the Scavenger Starport.
-- Sandbox: Fable batch C (14 Oct 2026). Same shape as spawn/destroy_mission/dantooine_destroy_missions.lua.
-- MissionManagerImplementation::randomizeGenericDestroyMission reads the group named <zone>_destroy_missions and
-- picks a lair with minDifficulty <= player level + 5 and maxDifficulty >= min(player level - 5, minLevelCeiling);
-- a lair needs a building (buildings* or missionBuilding in its lair template) to be a mission target.
-- Ranges follow the creature levels in mobile/hoth: tauntaun 65 / bull 72, ice mynock 67 / greater 76,
-- scavenger raider 74, wampa 90 / elder 98. Nothing on Hoth is below 62, so players under about level 55 get no
-- destroy missions here (as on any high-level planet).
hoth_destroy_missions = {
	minLevelCeiling = 75,
	lairSpawns = {
		{
			lairTemplateName = "hoth_tauntaun_lair_neutral_medium",
			minDifficulty = 60,
			maxDifficulty = 72,
			size = 25,
		},
		{
			lairTemplateName = "hoth_ice_mynock_lair_neutral_medium",
			minDifficulty = 64,
			maxDifficulty = 76,
			size = 25,
		},
		{
			lairTemplateName = "hoth_scavenger_raider_camp_neutral_none",
			minDifficulty = 70,
			maxDifficulty = 80,
			size = 25,
		},
		{
			lairTemplateName = "hoth_wampa_lair_neutral_large",
			minDifficulty = 85,
			maxDifficulty = 100,
			size = 25,
		},
	}
}

addDestroyMissionGroup("hoth_destroy_missions", hoth_destroy_missions);
