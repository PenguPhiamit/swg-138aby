-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kaddyr_bug = Creature:new {
	objectName = "",
	customName = "a kaddyr bug",
	socialGroup = "kaddyr",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 32,
	chanceHit = 0.4,
	damageMin = 290,
	damageMax = 300,
	baseXp = 3300,
	baseHAM = 9000,
	baseHAMmax = 10400,
	armor = 0,
	resists = {120,5,5,-1,5,-1,5,-1,-1},
	meatType = "meat_insect",
	meatAmount = 10,
	hideType = "hide_scaley",
	hideAmount = 8,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0.2,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/kliknik_hue.iff"},
	hues = { 0, 1, 2, 3, 4, 5, 6, 7 },
	controlDeviceTemplate = "object/intangible/pet/kliknik_hue.iff",
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"posturedownattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_kaddyr_bug, "ossus_kaddyr_bug")
