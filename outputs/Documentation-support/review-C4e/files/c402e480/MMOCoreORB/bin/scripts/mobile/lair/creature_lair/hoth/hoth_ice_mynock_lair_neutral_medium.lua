-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_lair/hoth/hoth_ice_mynock_lair_neutral_medium.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_ice_mynock_lair_neutral_medium = Lair:new {
	mobiles = {{"hoth_ice_mynock", 2}, {"hoth_greater_ice_mynock", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_mound_large.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_mound_large.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_mound_large.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_mound_large.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_mound_large.iff"},
	customName = "Ice Mynock Roost"
}

addLairTemplate("hoth_ice_mynock_lair_neutral_medium", hoth_ice_mynock_lair_neutral_medium)
