-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md): dynamic lairs (no building) for the new Hoth
-- creatures in mobile/hoth/hoth_fill_creatures.lua, in the shape of hoth_tauntaun_herd_neutral_none.lua.

local function herd(name, mobiles, limit)
	return Lair:new {
		mobiles = mobiles,
		spawnLimit = limit,
		buildingsVeryEasy = {},
		buildingsEasy = {},
		buildingsMedium = {},
		buildingsHard = {},
		buildingsVeryHard = {},
		customName = name,
		missionBuilding = "object/tangible/lair/base/poi_all_lair_mound_large.iff",
		buildingType = "none"
	}
end

addLairTemplate("hoth_whitefang_pack_neutral_none", herd("Whitefang Pack", {{"hoth_pantran_whitefang", 3}, {"hoth_whitefang_stalker", 1}}, 12))
addLairTemplate("hoth_hog_family_neutral_none", herd("Hoth Hog Family", {{"hoth_hog", 4}, {"hoth_hog_boar", 1}}, 15))
addLairTemplate("hoth_scrabbler_swarm_neutral_none", herd("Ice Scrabbler Swarm", {{"hoth_ice_scrabbler", 6}}, 15))
addLairTemplate("hoth_icetromper_herd_neutral_none", herd("Icetromper Herd", {{"hoth_icetromper", 3}, {"hoth_icetromper_bull", 1}}, 10))
