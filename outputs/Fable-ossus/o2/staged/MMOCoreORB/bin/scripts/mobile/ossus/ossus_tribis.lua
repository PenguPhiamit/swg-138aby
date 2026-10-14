-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_tribis = Creature:new {
	objectName = "",
	customName = "a tribis",
	socialGroup = "tribis",
	faction = "",
	mobType = MOB_HERBIVORE,
	level = 28,
	chanceHit = 0.38,
	damageMin = 255,
	damageMax = 265,
	baseXp = 2800,
	baseHAM = 8000,
	baseHAMmax = 9200,
	armor = 0,
	resists = {10,10,10,10,10,10,10,10,-1},
	meatType = "meat_herbivore",
	meatAmount = 300,
	hideType = "hide_bristley",
	hideAmount = 220,
	boneType = "bone_mammal",
	boneAmount = 140,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = PACK + HERD,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/tybis_hue.iff"},
	hues = { 16, 17, 18, 19, 20, 21, 22, 23 },
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"knockdownattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_tribis, "ossus_tribis")
