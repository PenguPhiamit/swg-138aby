-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_gokob_pack_neutral_none = Lair:new {
	mobiles = {{"ossus_gokob", 4}, {"ossus_gokob_scavenger", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Gokob Pack",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_warren_large.iff",
	buildingType = "none"
}

addLairTemplate("ossus_gokob_pack_neutral_none", ossus_gokob_pack_neutral_none)
