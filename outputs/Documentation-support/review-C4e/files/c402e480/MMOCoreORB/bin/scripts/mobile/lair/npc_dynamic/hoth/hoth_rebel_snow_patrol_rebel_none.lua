-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/npc_dynamic/hoth/hoth_rebel_snow_patrol_rebel_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_rebel_snow_patrol_rebel_none = Lair:new {
	mobiles = {{"hoth_rebel_snow_soldier", 3}, {"hoth_rebel_snow_sergeant", 1}},
	spawnLimit = 9,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Rebel Snow Patrol",
	faction = "rebel",
	mobType = "npc",
	missionBuilding = "object/tangible/lair/base/objective_banner_rebel.iff",
	buildingType = "none"
}

addLairTemplate("hoth_rebel_snow_patrol_rebel_none", hoth_rebel_snow_patrol_rebel_none)
