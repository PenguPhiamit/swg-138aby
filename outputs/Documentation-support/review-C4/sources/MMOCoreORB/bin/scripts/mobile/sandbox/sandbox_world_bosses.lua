-- Sandbox world boss rotation (see screenplays/sandbox/sandbox_world_bosses.lua).
-- The bosses themselves reuse existing creature templates; only the hunter is new.

sandbox_big_game_hunter = Creature:new {
	objectName = "@mob/creature_names:bounty_hunter",
	mobType = MOB_NPC,
	socialGroup = "",
	faction = "",
	level = 40,
	chanceHit = 0.43,
	damageMin = 370,
	damageMax = 450,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,20,20,20,20,-1},
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

	templates = { "object/mobile/dressed_mercenary_weak_hum_m.iff" },

	lootGroups = {},

	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "sandbox_big_game_hunter_convo_template",
	primaryAttacks = brawlermaster,
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(sandbox_big_game_hunter, "sandbox_big_game_hunter")
