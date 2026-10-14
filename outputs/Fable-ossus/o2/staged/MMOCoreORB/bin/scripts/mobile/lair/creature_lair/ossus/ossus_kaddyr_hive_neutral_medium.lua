-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kaddyr_hive_neutral_medium = Lair:new {
	mobiles = {{"ossus_kaddyr_bug", 3}, {"ossus_kaddyr_soldier", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_insecthill_large.iff", "object/tangible/lair/base/poi_all_lair_insecthill_small.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_insecthill_large.iff", "object/tangible/lair/base/poi_all_lair_insecthill_small.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_insecthill_large.iff", "object/tangible/lair/base/poi_all_lair_insecthill_small.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_insecthill_large.iff", "object/tangible/lair/base/poi_all_lair_insecthill_small.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_insecthill_large.iff", "object/tangible/lair/base/poi_all_lair_insecthill_small.iff"},
	customName = "Kaddyr Hive"
}

addLairTemplate("ossus_kaddyr_hive_neutral_medium", ossus_kaddyr_hive_neutral_medium)
