-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kirruk = Creature:new {
	objectName = "",
	customName = "a kirruk",
	socialGroup = "kirruk",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 48,
	chanceHit = 0.5,
	damageMin = 390,
	damageMax = 480,
	baseXp = 4700,
	baseHAM = 10800,
	baseHAMmax = 12800,
	armor = 1,
	resists = {130,130,-1,150,150,-1,150,-1,-1},
	meatType = "meat_carnivore",
	meatAmount = 80,
	hideType = "hide_wooly",
	hideAmount = 50,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0.2,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/gurreck_hue.iff"},
	hues = { 24, 25, 26, 27, 28, 29, 30, 31 },
	controlDeviceTemplate = "object/intangible/pet/gurreck_hue.iff",
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"posturedownattack",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_kirruk, "ossus_kirruk")
