-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/npc_dynamic/hoth/hoth_snowtrooper_patrol_imperial_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_snowtrooper_patrol_imperial_none = Lair:new {
	mobiles = {{"hoth_snowtrooper", 3}, {"hoth_snowtrooper_sergeant", 1}},
	spawnLimit = 9,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Snowtrooper Patrol",
	faction = "imperial",
	mobType = "npc",
	missionBuilding = "object/tangible/lair/base/objective_banner_imperial.iff",
	buildingType = "none"
}

addLairTemplate("hoth_snowtrooper_patrol_imperial_none", hoth_snowtrooper_patrol_imperial_none)
