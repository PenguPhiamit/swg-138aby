-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair
-- props referenced by name. Levels are a placeholder mid band (owner question).

ossus_bol = Creature:new {
	objectName = "",
	customName = "an Ossus bol",
	socialGroup = "bol",
	faction = "",
	mobType = MOB_HERBIVORE,
	level = 30,
	chanceHit = 0.39,
	damageMin = 262,
	damageMax = 272,
	baseXp = 2950,
	baseHAM = 8500,
	baseHAMmax = 10300,
	armor = 0,
	resists = {135,20,-1,20,20,-1,20,-1,-1},
	meatType = "meat_herbivore",
	meatAmount = 185,
	hideType = "hide_leathery",
	hideAmount = 300,
	boneType = "bone_mammal",
	boneAmount = 185,
	milk = 0,
	tamingChance = 0.2,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = PACK + HERD,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/bol_hue.iff"},
	hues = { 8, 9, 10, 11, 12, 13, 14, 15 },
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"knockdownattack",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(ossus_bol, "ossus_bol")
