-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kaddyr_swarm_neutral_none = Lair:new {
	mobiles = {{"ossus_kaddyr_bug", 4}, {"ossus_kaddyr_soldier", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {},
	buildingsEasy = {},
	buildingsMedium = {},
	buildingsHard = {},
	buildingsVeryHard = {},
	customName = "Kaddyr Swarm",
	missionBuilding = "object/tangible/lair/base/poi_all_lair_insecthill_large.iff",
	buildingType = "none"
}

addLairTemplate("ossus_kaddyr_swarm_neutral_none", ossus_kaddyr_swarm_neutral_none)
