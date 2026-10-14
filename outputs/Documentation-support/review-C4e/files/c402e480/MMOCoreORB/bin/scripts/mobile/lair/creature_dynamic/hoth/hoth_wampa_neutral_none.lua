-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_dynamic/hoth/hoth_wampa_neutral_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_wampa_neutral_none = Lair:new {
	mobiles = {{"hoth_wampa", 1}},
	spawnLimit = 6,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Wampa",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_bones_large.iff",
	buildingType = "none"
}

addLairTemplate("hoth_wampa_neutral_none", hoth_wampa_neutral_none)
