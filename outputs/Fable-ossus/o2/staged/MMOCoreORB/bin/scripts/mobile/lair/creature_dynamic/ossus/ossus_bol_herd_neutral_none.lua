-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_bol_herd_neutral_none = Lair:new {
	mobiles = {{"ossus_bol", 4}, {"ossus_bol_bull", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Bol Herd",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_rocks_large.iff",
	buildingType = "none"
}

addLairTemplate("ossus_bol_herd_neutral_none", ossus_bol_herd_neutral_none)
