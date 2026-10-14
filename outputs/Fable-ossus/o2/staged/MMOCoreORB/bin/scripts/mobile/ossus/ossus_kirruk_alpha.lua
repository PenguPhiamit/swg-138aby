-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kirruk_alpha = Creature:new {
	objectName = "",
	customName = "a kirruk alpha",
	socialGroup = "kirruk",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 56,
	chanceHit = 0.55,
	damageMin = 450,
	damageMax = 560,
	baseXp = 5600,
	baseHAM = 12500,
	baseHAMmax = 14500,
	armor = 1,
	resists = {140,140,-1,160,160,-1,160,-1,-1},
	meatType = "meat_carnivore",
	meatAmount = 95,
	hideType = "hide_wooly",
	hideAmount = 60,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0.15,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/gurreck_hue.iff"},
	hues = { 24, 25, 26, 27, 28, 29, 30, 31 },
	controlDeviceTemplate = "object/intangible/pet/gurreck_hue.iff",
	scale = 1.2,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"posturedownattack",""}, {"intimidationattack",""}, {"knockdownattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_kirruk_alpha, "ossus_kirruk_alpha")
