-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/npc_dynamic/hoth/hoth_scavenger_raider_camp_neutral_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_scavenger_raider_camp_neutral_none = Lair:new {
	mobiles = {{"hoth_scavenger_raider", 4}},
	spawnLimit = 9,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Scavenger Raider Camp",
	mobType = "npc",
	missionBuilding = "object/tangible/lair/base/objective_banner_generic_2.iff",
	buildingType = "none"
}

addLairTemplate("hoth_scavenger_raider_camp_neutral_none", hoth_scavenger_raider_camp_neutral_none)
