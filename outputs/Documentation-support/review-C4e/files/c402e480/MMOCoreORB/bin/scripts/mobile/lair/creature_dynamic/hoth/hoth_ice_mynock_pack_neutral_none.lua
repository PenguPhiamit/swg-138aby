-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_dynamic/hoth/hoth_ice_mynock_pack_neutral_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_ice_mynock_pack_neutral_none = Lair:new {
	mobiles = {{"hoth_ice_mynock", 3}, {"hoth_greater_ice_mynock", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Ice Mynock Swarm",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_nest_small.iff",
	buildingType = "none"
}

addLairTemplate("hoth_ice_mynock_pack_neutral_none", hoth_ice_mynock_pack_neutral_none)
