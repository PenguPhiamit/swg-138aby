-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_dynamic/hoth/hoth_probe_droid_neutral_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_probe_droid_neutral_none = Lair:new {
	mobiles = {{"hoth_probe_droid", 1}},
	spawnLimit = 6,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Imperial Probe Droid",
	missionBuilding = "object/tangible/lair/base/objective_power_node.iff",
	buildingType = "none"
}

addLairTemplate("hoth_probe_droid_neutral_none", hoth_probe_droid_neutral_none)
