-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_bol_bull = Creature:new {
	objectName = "",
	customName = "an Ossus bol bull",
	socialGroup = "bol",
	faction = "",
	mobType = MOB_HERBIVORE,
	level = 36,
	chanceHit = 0.43,
	damageMin = 310,
	damageMax = 330,
	baseXp = 3700,
	baseHAM = 10200,
	baseHAMmax = 11800,
	armor = 0,
	resists = {145,30,-1,30,30,-1,30,-1,-1},
	meatType = "meat_herbivore",
	meatAmount = 220,
	hideType = "hide_leathery",
	hideAmount = 340,
	boneType = "bone_mammal",
	boneAmount = 210,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = PACK + HERD + KILLER,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/bol_hue.iff"},
	hues = { 8, 9, 10, 11, 12, 13, 14, 15 },
	scale = 1.1,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"knockdownattack",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_bol_bull, "ossus_bol_bull")
