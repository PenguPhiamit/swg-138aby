-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_tauntaun.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: hoth_art_rare.

hoth_tauntaun = Creature:new {
	objectName = "",
	customName = "a Hoth tauntaun",
	socialGroup = "tauntaun",
	faction = "",
	mobType = MOB_HERBIVORE,
	level = 65,
	chanceHit = 0.6,
	damageMin = 470,
	damageMax = 610,
	baseXp = 6290,
	baseHAM = 12500,
	baseHAMmax = 14500,
	armor = 1,
	resists = {120,120,20,150,20,150,20,20,-1},
	meatType = "meat_herbivore",
	meatAmount = 700,
	hideType = "hide_wooly",
	hideAmount = 600,
	boneType = "bone_mammal",
	boneAmount = 500,
	milk = 300,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = HERD,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/tauntaun_hue.iff"},
	hues = { 16, 17, 18, 19, 20, 21, 22, 23 },
	scale = 1.0,
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"knockdownattack",""}, {"dizzyattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_tauntaun, "hoth_tauntaun")
