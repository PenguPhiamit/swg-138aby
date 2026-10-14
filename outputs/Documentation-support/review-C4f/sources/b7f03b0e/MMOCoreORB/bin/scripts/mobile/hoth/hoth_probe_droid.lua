-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_probe_droid.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: hoth_art_rare.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_common (3%).

hoth_probe_droid = Creature:new {
	objectName = "",
	customName = "an Imperial probe droid",
	socialGroup = "imperial",
	faction = "",
	mobType = MOB_DROID,
	level = 74,
	chanceHit = 0.72,
	damageMin = 520,
	damageMax = 720,
	baseXp = 7100,
	baseHAM = 12500,
	baseHAMmax = 15000,
	armor = 1,
	resists = {140,140,140,30,30,30,30,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = KILLER,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {"object/mobile/probot.iff"},
	lootGroups = {
		{
			groups = {
				{group = "armor_all", chance = 3000000},
				{group = "weapons_all", chance = 3500000},
				{group = "wearables_all", chance = 3500000}
			},
			lootChance = 2000000
		},
		{
			groups = {
				{group = "hoth_decor_common", chance = 10000000}
			},
			lootChance = 300000
		}
	},
	defaultAttack = "attack",
	primaryWeapon = "droid_probot_ranged",
	secondaryWeapon = "none",
	conversationTemplate = ""
}

CreatureTemplates:addCreatureTemplate(hoth_probe_droid, "hoth_probe_droid")
