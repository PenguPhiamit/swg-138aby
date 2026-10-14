-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kirruk_den_neutral_large = Lair:new {
	mobiles = {{"ossus_kirruk", 2}, {"ossus_kirruk_alpha", 1}},
	spawnLimit = 15,
	buildingsVeryEasy = {"object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff", "object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsEasy = {"object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff", "object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsMedium = {"object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff", "object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsHard = {"object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff", "object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	buildingsVeryHard = {"object/tangible/lair/base/poi_all_lair_rock_shelter_large.iff", "object/tangible/lair/base/poi_all_lair_bones_large.iff"},
	customName = "Kirruk Den"
}

addLairTemplate("ossus_kirruk_den_neutral_large", ossus_kirruk_den_neutral_large)
