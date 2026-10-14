-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_lair/hoth/hoth_wampa_lair_neutral_large.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_wampa_lair_neutral_large = Lair:new {
	mobiles = {{"hoth_wampa", 2}, {"hoth_elder_wampa", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	customName = "Wampa Den"
}

addLairTemplate("hoth_wampa_lair_neutral_large", hoth_wampa_lair_neutral_large)
