-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_tribis_herd_neutral_none = Lair:new {
	mobiles = {{"ossus_tribis", 4}, {"ossus_tribis_bull", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Tribis Herd",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_mound_large.iff",
	buildingType = "none"
}

addLairTemplate("ossus_tribis_herd_neutral_none", ossus_tribis_herd_neutral_none)
