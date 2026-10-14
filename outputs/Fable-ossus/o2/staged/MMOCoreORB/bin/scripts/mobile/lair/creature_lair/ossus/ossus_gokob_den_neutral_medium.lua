-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_gokob_den_neutral_medium = Lair:new {
	mobiles = {{"ossus_gokob", 3}, {"ossus_gokob_scavenger", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_warren_large.iff", "object/tangible/lair/base/poi_all_lair_mound_small.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_warren_large.iff", "object/tangible/lair/base/poi_all_lair_mound_small.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_warren_large.iff", "object/tangible/lair/base/poi_all_lair_mound_small.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_warren_large.iff", "object/tangible/lair/base/poi_all_lair_mound_small.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_warren_large.iff", "object/tangible/lair/base/poi_all_lair_mound_small.iff"},
	customName = "Gokob Den"
}

addLairTemplate("ossus_gokob_den_neutral_medium", ossus_gokob_den_neutral_medium)
