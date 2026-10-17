-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md): the people of the Hoth fill. Talkers at the
-- Scavenger Starport and the camps (their text is in mobile/conversations/sandbox/hoth_world_conv.lua, drafted by the
-- local role-play model from our briefs and edited by Claude), and the named fighters of the places to find and the
-- Echo Base ruin, placed by screenplays/sandbox/hoth_world.lua and screenplays/poi/hoth_echo_base.lua. Stock bodies
-- and stock loot groups plus the Hoth decor groups; names and text are ours. Era 138-139 ABY; levels 74-98, as Hoth is a
-- mid-to-end-game planet.

local function fighter(name, level, bodies, loot, social, attacks)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = social,
		mobType = MOB_NPC,
		faction = "",
		level = level,
		chanceHit = 0.3 + level * 0.005,
		damageMin = 7 * level,
		damageMax = 10 * level,
		baseXp = 96 * level,
		baseHAM = 190 * level,
		baseHAMmax = 225 * level,
		armor = level >= 90 and 2 or 1,
		resists = {35,35,35,35,65,35,35,-1,-1},
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
		templates = bodies,
		lootGroups = loot,
		primaryWeapon = "pirate_weapons_heavy",
		secondaryWeapon = "unarmed",
		conversationTemplate = "",
		reactionStf = "@npc_reaction/slang",
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

local crew = {
	{
		groups = {
			{group = "armor_all", chance = 3000000},
			{group = "weapons_all", chance = 3500000},
			{group = "wearables_all", chance = 3500000}
		},
		lootChance = 2500000
	},
	{ groups = { {group = "hoth_decor_common", chance = 10000000} }, lootChance = 300000 },
}

local leader = {
	{
		groups = {
			{group = "armor_attachments", chance = 2500000},
			{group = "clothing_attachments", chance = 2500000},
			{group = "weapons_all", chance = 2500000},
			{group = "armor_all", chance = 2500000}
		},
	},
	{ groups = { {group = "hoth_decor_rare", chance = 10000000} }, lootChance = 500000 },
	{ groups = { {group = "hoth_vehicle_deeds", chance = 10000000} }, lootChance = 200000 },
}

local scavengers = {
	"object/mobile/dressed_tatooine_scavenger.iff",
	"object/mobile/dressed_mercenary_commander_zab_m.iff",
	"object/mobile/dressed_goon_twk_male_01.iff",
	"object/mobile/dressed_robber_human_female_01.iff"
}

local ranged = merge(brawlermaster, marksmanmaster)

local templates = {
	-- Echo Base: the salvage crews who strip the ruin, and their baron (Hask Moor's job)
	hoth_echo_salvager = fighter("an Echo Base salvager", 78, scavengers, crew, "thug", ranged),
	hoth_echo_cutter = fighter("an Echo Base cutter", 84, scavengers, crew, "thug", ranged),
	hoth_salvage_baron_skarrel = fighter("Vorn Skarrel, the salvage baron", 98,
		{"object/mobile/dressed_mercenary_commander_zab_m.iff"}, leader, "thug", merge(brawlermaster, marksmanmaster, pistoleermaster)),
	-- the crashed freighter: looters picking it over
	hoth_wreck_looter = fighter("a wreck looter", 76, scavengers, crew, "thug", ranged),
	-- the Imperial wreck: a crashed transport of Krayt's Empire and the holdouts who never left it
	hoth_imperial_holdout = fighter("an Imperial holdout", 82, {"object/mobile/snowtrooper_s01.iff"}, crew, "imperial", ranged),
	hoth_holdout_captain_venn = fighter("Captain Tarsk Venn", 94, {"object/mobile/dressed_imperial_officer_m.iff"}, leader, "imperial",
		merge(brawlermaster, marksmanmaster, pistoleermaster)),
	-- the Generator Field: scavengers cutting up the old shield generator
	hoth_generator_scrapper = fighter("a generator scrapper", 80, scavengers, crew, "thug", ranged),
}

for name, t in pairs(templates) do
	CreatureTemplates:addCreatureTemplate(t, name)
end

local talkers = {
	{"hoth_fill_hask_moor", "Hask Moor, an old prospector", "object/mobile/dressed_commoner_old_human_male_02.iff", "hoth_fill_hask_moor_convo_template"},
	{"hoth_fill_tavi_renn", "Tavi Renn, a hunting guide", "object/mobile/dressed_rebel_specforce_pathfinder_twk_female_01.iff", "hoth_fill_tavi_renn_convo_template"},
	{"hoth_fill_orrin_dask", "Medic Orrin Dask", "object/mobile/dressed_tatooine_rodian_clan_medic.iff", "hoth_fill_orrin_dask_convo_template"},
	{"hoth_fill_kesh", "Kesh, a freighter pilot", "object/mobile/dressed_mercenary_messanger_sullustan_m.iff", "hoth_fill_kesh_convo_template"},
	{"hoth_fill_ysa_volt", "Ysa Volt, the tally clerk", "object/mobile/dressed_brigade_technician_human_female_01.iff", "hoth_fill_ysa_volt_convo_template"},
	{"hoth_fill_brother_tamm", "Brother Tamm", "object/mobile/dressed_tatooine_hermit.iff", "hoth_fill_brother_tamm_convo_template"},
	{"hoth_fill_dellan_pryce", "Dellan Pryce, a crash survivor", "object/mobile/dressed_commoner_naboo_human_male_04.iff", "hoth_fill_dellan_pryce_convo_template"},
	{"hoth_fill_jeth_ardo", "Corporal Jeth Ardo", "object/mobile/dressed_rebel_trooper_bith_m_01.iff", "hoth_fill_jeth_ardo_convo_template"},
}

for _, t in ipairs(talkers) do
	CreatureTemplates:addCreatureTemplate(talker(t[2], t[3], t[4]), t[1])
end
