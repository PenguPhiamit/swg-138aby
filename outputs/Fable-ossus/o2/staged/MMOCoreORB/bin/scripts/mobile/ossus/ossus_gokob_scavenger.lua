-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_gokob_scavenger = Creature:new {
	objectName = "",
	customName = "a gokob scavenger",
	socialGroup = "gokob",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 27,
	chanceHit = 0.37,
	damageMin = 250,
	damageMax = 260,
	baseXp = 2700,
	baseHAM = 7600,
	baseHAMmax = 8700,
	armor = 0,
	resists = {0,0,0,0,0,0,0,-1,-1},
	meatType = "meat_wild",
	meatAmount = 14,
	hideType = "hide_leathery",
	hideAmount = 10,
	boneType = "bone_mammal",
	boneAmount = 7,
	milk = 0,
	tamingChance = 0.2,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/womp_rat_hue.iff"},
	hues = { 0, 1, 2, 3, 4, 5, 6, 7 },
	controlDeviceTemplate = "object/intangible/pet/womp_rat_hue.iff",
	scale = 1.1,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"intimidationattack",""}, {"posturedownattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_gokob_scavenger, "ossus_gokob_scavenger")
