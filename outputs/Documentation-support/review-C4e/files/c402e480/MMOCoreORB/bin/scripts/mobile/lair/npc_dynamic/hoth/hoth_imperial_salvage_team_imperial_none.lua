-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/npc_dynamic/hoth/hoth_imperial_salvage_team_imperial_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_imperial_salvage_team_imperial_none = Lair:new {
	mobiles = {{"hoth_imperial_salvage_tech", 3}, {"hoth_snowtrooper", 1}},
	spawnLimit = 9,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Imperial Salvage Team",
	faction = "imperial",
	mobType = "npc",
	missionBuilding = "object/tangible/lair/base/objective_power_generator.iff",
	buildingType = "none"
}

addLairTemplate("hoth_imperial_salvage_team_imperial_none", hoth_imperial_salvage_team_imperial_none)
