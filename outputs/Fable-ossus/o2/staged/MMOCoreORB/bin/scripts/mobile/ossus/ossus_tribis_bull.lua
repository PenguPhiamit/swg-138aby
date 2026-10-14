-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_tribis_bull = Creature:new {
	objectName = "",
	customName = "a tribis bull",
	socialGroup = "tribis",
	faction = "",
	mobType = MOB_HERBIVORE,
	level = 34,
	chanceHit = 0.42,
	damageMin = 300,
	damageMax = 320,
	baseXp = 3500,
	baseHAM = 9800,
	baseHAMmax = 11200,
	armor = 0,
	resists = {20,20,20,20,20,20,20,20,-1},
	meatType = "meat_herbivore",
	meatAmount = 360,
	hideType = "hide_bristley",
	hideAmount = 260,
	boneType = "bone_mammal",
	boneAmount = 170,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = PACK + HERD + KILLER,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/tybis_hue.iff"},
	hues = { 16, 17, 18, 19, 20, 21, 22, 23 },
	scale = 1.15,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"knockdownattack",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_tribis_bull, "ossus_tribis_bull")
