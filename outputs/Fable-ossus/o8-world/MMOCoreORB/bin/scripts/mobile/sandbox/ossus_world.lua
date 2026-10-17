-- Ossus world (O8; outputs/Fable-ossus/o8-world/README.md): the named fighters of the six places to find and the
-- dungeon under the foothills, and four townsfolk who talk. Placed by screenplays/sandbox/ossus_world.lua.
-- Stock bodies and stock loot groups; names and text are our own. Era 138-139 ABY.

local function fighter(name, level, body, loot, social, weapon, attacks)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = social,
		mobType = MOB_NPC,
		faction = "",
		level = level,
		chanceHit = 0.25 + level * 0.005,
		damageMin = 10 * level,
		damageMax = 10 * level + 10,
		baseXp = 75 * level,
		baseHAM = 200 * level,
		baseHAMmax = 250 * level,
		armor = 0,
		resists = {10,10,10,10,10,10,10,-1,-1},
		meatType = "",
		meatAmount = 0,
		hideType = "",
		hideAmount = 0,
		boneType = "",
		boneAmount = 0,
		milk = 0,
		tamingChance = 0,
		ferocity = 0,
		pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
		creatureBitmask = PACK + KILLER,
		optionsBitmask = AIENABLED,
		diet = HERBIVORE,
		templates = {body},
		lootGroups = loot,
		primaryWeapon = weapon,
		secondaryWeapon = "unarmed",
		conversationTemplate = "",
		-- an 80 m leash instead of the stock 256 m (ai/ossus.lua; the owner was chased out of the One Sith cave, 17 Oct)
		customAiMap = "ossusShortLeash",
		primaryAttacks = attacks,
		secondaryAttacks = {}
	}
end

local function talker(name, body, conversation)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = "townsperson",
		mobType = MOB_NPC,
		faction = "",
		level = 10,
		chanceHit = 0.3,
		damageMin = 90,
		damageMax = 100,
		baseXp = 0,
		baseHAM = 2000,
		baseHAMmax = 2400,
		armor = 0,
		resists = {0,0,0,0,0,0,0,-1,-1},
		meatType = "",
		meatAmount = 0,
		hideType = "",
		hideAmount = 0,
		boneType = "",
		boneAmount = 0,
		milk = 0,
		tamingChance = 0,
		ferocity = 0,
		pvpBitmask = NONE,
		creatureBitmask = NONE,
		optionsBitmask = AIENABLED + INVULNERABLE + CONVERSABLE,
		diet = HERBIVORE,
		templates = {body},
		lootGroups = {},
		primaryWeapon = "unarmed",
		secondaryWeapon = "none",
		conversationTemplate = conversation,
		primaryAttacks = {},
		secondaryAttacks = {}
	}
end

local common = {
	{
		groups = {
			{group = "junk", chance = 4500000},
			{group = "loot_kit_parts", chance = 2000000},
			{group = "wearables_common", chance = 2000000},
			{group = "tailor_components", chance = 1500000},
		},
		lootChance = 8000000
	},
}

local leader = {
	{
		groups = {
			{group = "junk", chance = 3000000},
			{group = "loot_kit_parts", chance = 2500000},
			{group = "wearables_common", chance = 2000000},
			{group = "clothing_attachments", chance = 1250000},
			{group = "armor_attachments", chance = 1250000},
		},
	},
	{
		groups = {
			{group = "pistols", chance = 5000000},
			{group = "rifles", chance = 5000000},
		},
		lootChance = 3000000
	},
}

local keeper = {
	{
		groups = {
			{group = "color_crystals", chance = 4000000},
			{group = "armor_attachments", chance = 2000000},
			{group = "clothing_attachments", chance = 2000000},
			{group = "melee_weapons", chance = 2000000},
		},
	},
	{
		groups = {
			{group = "junk", chance = 5000000},
			{group = "loot_kit_parts", chance = 5000000},
		},
	},
}

local ranged = merge(brawlermaster, marksmanmaster)

local templates = {
	-- the dungeon: the One Sith cell in the foothill cave (POI 14)
	ossus_sith_acolyte = fighter("a One Sith acolyte", 18, "object/mobile/dressed_dark_jedi_human_male_01.iff", common, "sith_shadow", "pirate_weapons_heavy", ranged),
	ossus_sith_enforcer = fighter("a One Sith enforcer", 26, "object/mobile/dressed_dark_jedi_human_female_01.iff", common, "sith_shadow", "pirate_weapons_heavy", ranged),
	ossus_sith_keeper = fighter("Keeper Raskal Vonn", 38, "object/mobile/dressed_dark_jedi_human_male_01.iff", keeper, "sith_shadow", "pirate_weapons_heavy", merge(brawlermaster, marksmanmaster, pistoleermaster)),
	-- the places to find
	ossus_scavenger_boss = fighter("Mother Gessa, scavenger boss", 14, "object/mobile/dressed_criminal_slicer_human_male_01.iff", leader, "thug", "pirate_weapons_heavy", ranged),
	ossus_poacher_chief = fighter("Harl Dennick, poacher chief", 21, "object/mobile/dressed_mand_miner_hum_02.iff", leader, "poacher", "pirate_weapons_heavy", ranged),
	ossus_smuggler_captain = fighter("Captain Sava Rook, smuggler", 19, "object/mobile/dressed_criminal_slicer_human_male_01.iff", leader, "thug", "pirate_weapons_heavy", ranged),
}

for name, t in pairs(templates) do
	CreatureTemplates:addCreatureTemplate(t, name)
end

local talkers = {
	{"ossus_knossa_pilgrim", "Sister Anwe, a pilgrim", "object/mobile/dressed_tatooine_hermit.iff", "ossus_knossa_pilgrim_convo_template"},
	{"ossus_knossa_settler", "Rab Okkon, a settler", "object/mobile/dressed_quest_farmer.iff", "ossus_knossa_settler_convo_template"},
	{"ossus_hollow_hermit", "the hermit of the hollow", "object/mobile/dressed_tatooine_hermit.iff", "ossus_hollow_hermit_convo_template"},
	{"ossus_deserter", "Lieutenant Iden Sarr, a deserter", "object/mobile/dressed_imperial_major_m.iff", "ossus_deserter_convo_template"},
}

for _, t in ipairs(talkers) do
	CreatureTemplates:addCreatureTemplate(talker(t[2], t[3], t[4]), t[1])
end
