-- NPCs of Quartermaster Vell's salvage chain (screenplays/tasks/hoth/scavenger_quartermaster.lua).
-- Sandbox: Fable batch C (14 Oct 2026). Shapes follow mobile/quest/tatooine/aaph_koden.lua (giver) and
-- talia_reede.lua (talk-to targets); the raider captain is a named, tougher hoth_scavenger_raider. All appearance
-- templates are stock (object/mobile/serverobjects.lua). Four templates in one file so one include line wires them.

-- The giver: stands by the mission terminals east of the starport.
hoth_quartermaster_vell = Creature:new {
	objectName = "",
	customName = "Quartermaster Vell",
	socialGroup = "townsperson",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
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
	optionsBitmask = AIENABLED + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_merchant_trainer_02.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_giver_convotemplate",
	primaryAttacks = {},
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_quartermaster_vell, "hoth_quartermaster_vell")

-- Mission 1 target: the salvage tech who hands over the power regulator (retrieve: talk, no kill).
hoth_salvage_tech_baxx = Creature:new {
	objectName = "",
	customName = "Ria Baxx",
	socialGroup = "",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = NONE,
	optionsBitmask = INVULNERABLE + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_brigade_technician_human_female_01.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_target_convotemplate",
	primaryAttacks = brawlermid,
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_salvage_tech_baxx, "hoth_salvage_tech_baxx")

-- Mission 2 target: the raider captain (assassinate). A named hoth_scavenger_raider, a few levels up.
hoth_raider_captain_korro = Creature:new {
	objectName = "",
	customName = "Thane Korro",
	socialGroup = "thug",
	faction = "thug",
	mobType = MOB_NPC,
	level = 80,
	chanceHit = 0.75,
	damageMin = 580,
	damageMax = 790,
	baseXp = 7900,
	baseHAM = 15000,
	baseHAMmax = 18000,
	armor = 1,
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
	templates = {"object/mobile/dressed_mercenary_commander_zab_m.iff"},
	lootGroups = {
		{
			groups = {
				{group = "armor_all", chance = 3000000},
				{group = "weapons_all", chance = 3500000},
				{group = "wearables_all", chance = 3500000}
			},
			lootChance = 4000000
		},
		{
			groups = {
				{group = "hoth_decor_common", chance = 10000000}
			},
			lootChance = 600000
		}
	},
	primaryWeapon = "pirate_weapons_heavy",
	secondaryWeapon = "unarmed",
	conversationTemplate = "",
	reactionStf = "@npc_reaction/slang",
	primaryAttacks = marksmanmid,
	secondaryAttacks = brawlermid
}

CreatureTemplates:addCreatureTemplate(hoth_raider_captain_korro, "hoth_raider_captain_korro")

-- Mission 3 target: the broker who takes the alternator (deliver: talk).
hoth_salvage_broker_kett = Creature:new {
	objectName = "",
	customName = "Doro Kett",
	socialGroup = "",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = NONE,
	optionsBitmask = INVULNERABLE + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_criminal_smuggler_human_male_01.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_target_convotemplate",
	primaryAttacks = brawlermid,
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_salvage_broker_kett, "hoth_salvage_broker_kett")
