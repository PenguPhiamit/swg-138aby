-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_wampa.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: bg_token_group, hoth_art_rare, hoth_decor_common, hoth_ice_decor, hoth_vehicle_deeds, hoth_vehicle_schematics, jedi_robe.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_common (3%).

hoth_wampa = Creature:new {
	objectName = "",
	customName = "a wampa",
	socialGroup = "wampa",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 90,
	chanceHit = 0.86,
	damageMin = 590,
	damageMax = 880,
	baseXp = 8600,
	baseHAM = 16000,
	baseHAMmax = 20000,
	armor = 1,
	resists = {150,165,35,200,35,200,35,35,-1},
	meatType = "meat_carnivore",
	meatAmount = 900,
	hideType = "hide_wooly",
	hideAmount = 900,
	boneType = "bone_mammal",
	boneAmount = 750,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = KILLER + STALKER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/wampa.iff"},
	scale = 1.0,
	lootGroups = {
		{
			groups = {
				{group = "armor_attachments", chance = 10000000}
			},
			lootChance = 250000
		},
		{
			groups = {
				{group = "clothing_attachments", chance = 10000000}
			},
			lootChance = 250000
		},
		{
			groups = {
				{group = "color_crystals", chance = 10000000}
			},
			lootChance = 150000
		},
		{
			groups = {
				{group = "power_crystals", chance = 10000000}
			},
			lootChance = 150000
		},
		{
			groups = {
				{group = "krayt_pearls", chance = 10000000}
			},
			lootChance = 50000
		},
		{
			groups = {
				{group = "hoth_decor_common", chance = 10000000}
			},
			lootChance = 300000
		}
	},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"intimidationattack",""}, {"knockdownattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_wampa, "hoth_wampa")
