-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_kaddyr_soldier = Creature:new {
	objectName = "",
	customName = "a kaddyr soldier",
	socialGroup = "kaddyr",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 40,
	chanceHit = 0.45,
	damageMin = 340,
	damageMax = 360,
	baseXp = 4000,
	baseHAM = 10500,
	baseHAMmax = 12000,
	armor = 1,
	resists = {130,15,15,-1,15,-1,15,-1,-1},
	meatType = "meat_insect",
	meatAmount = 14,
	hideType = "hide_scaley",
	hideAmount = 10,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0.15,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/kliknik_hue.iff"},
	hues = { 0, 1, 2, 3, 4, 5, 6, 7 },
	controlDeviceTemplate = "object/intangible/pet/kliknik_hue.iff",
	scale = 1.1,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"posturedownattack",""}, {"dizzyattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_kaddyr_soldier, "ossus_kaddyr_soldier")
