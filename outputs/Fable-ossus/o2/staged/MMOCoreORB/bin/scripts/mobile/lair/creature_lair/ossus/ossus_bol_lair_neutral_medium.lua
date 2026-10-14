-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_bol_lair_neutral_medium = Lair:new {
	mobiles = {{"ossus_bol", 2}, {"ossus_bol_bull", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_rocks_large.iff", "object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_rocks_large.iff", "object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_rocks_large.iff", "object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_rocks_large.iff", "object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_rocks_large.iff", "object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff"},
	customName = "Bol Lair"
}

addLairTemplate("ossus_bol_lair_neutral_medium", ossus_bol_lair_neutral_medium)
