-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md): spawn groups for the three new Hoth wildlife areas
-- in managers/planet/hoth_regions.lua. Same fields as mobile/spawn/hoth/hoth_wampa_flanks.lua; difficulties are the
-- creatures' levels, so nothing below 60 spawns (owner, 17 Oct: Hoth is a mid-to-end-game planet).

local function lair(name, minDifficulty, weighting)
	return { lairTemplateName = name, spawnLimit = -1, minDifficulty = minDifficulty, maxDifficulty = 500,
		numberToSpawn = 15, weighting = weighting, size = 25 }
end

-- the vent fields east of the outpost: warm ground, so hogs and scrabblers, and the cats that hunt them
hoth_vent_fields = {
	lairSpawns = {
		lair("hoth_hog_family_neutral_none", 62, 40),
		lair("hoth_scrabbler_swarm_neutral_none", 60, 35),
		lair("hoth_whitefang_pack_neutral_none", 82, 25),
	}
}
addSpawnGroup("hoth_vent_fields", hoth_vent_fields)

-- the western glacier: icetrompers, tauntauns and the whitefangs that follow the herds
hoth_glacier_west = {
	lairSpawns = {
		lair("hoth_icetromper_herd_neutral_none", 88, 35),
		lair("hoth_tauntaun_herd_neutral_none", 65, 30),
		lair("hoth_whitefang_pack_neutral_none", 82, 25),
		lair("hoth_scrabbler_swarm_neutral_none", 60, 10),
	}
}
addSpawnGroup("hoth_glacier_west", hoth_glacier_west)

-- the northern reaches on the way to Echo Base: the hardest open ground outside the caves
hoth_northern_reaches = {
	lairSpawns = {
		lair("hoth_wampa_neutral_none", 90, 35),
		lair("hoth_whitefang_pack_neutral_none", 82, 30),
		lair("hoth_icetromper_herd_neutral_none", 88, 25),
		lair("hoth_wampa_lair_neutral_large", 90, 10),
	}
}
addSpawnGroup("hoth_northern_reaches", hoth_northern_reaches)
