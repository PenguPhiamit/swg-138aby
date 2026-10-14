-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/lair/creature_dynamic/hoth/hoth_tauntaun_herd_neutral_none.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_tauntaun_herd_neutral_none = Lair:new {
	mobiles = {{"hoth_tauntaun", 4}, {"hoth_tauntaun_bull", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Tauntaun Herd",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_mound_large.iff",
	buildingType = "none"
}

addLairTemplate("hoth_tauntaun_herd_neutral_none", hoth_tauntaun_herd_neutral_none)
