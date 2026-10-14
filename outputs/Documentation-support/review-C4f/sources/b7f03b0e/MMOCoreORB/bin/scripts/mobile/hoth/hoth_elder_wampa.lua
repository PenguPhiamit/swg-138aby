-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_elder_wampa.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: bg_token_group, hoth_art_rare, hoth_decor_common, hoth_ice_decor, hoth_vehicle_deeds, hoth_vehicle_schematics, jedi_robe.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_rare (5%), hoth_vehicle_deeds (2%).

hoth_elder_wampa = Creature:new {
	objectName = "",
	customName = "an elder wampa",
	socialGroup = "wampa",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 98,
	chanceHit = 0.95,
	damageMin = 640,
	damageMax = 980,
	baseXp = 9400,
	baseHAM = 22000,
	baseHAMmax = 27000,
	armor = 2,
	resists = {155,170,40,210,40,210,40,40,-1},
	meatType = "meat_carnivore",
	meatAmount = 1000,
	hideType = "hide_wooly",
	hideAmount = 1000,
	boneType = "bone_mammal",
	boneAmount = 850,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = KILLER + STALKER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/wampa.iff"},
	scale = 1.15,
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
				{group = "hoth_decor_rare", chance = 10000000}
			},
			lootChance = 500000
		},
		{
			groups = {
				{group = "hoth_vehicle_deeds", chance = 10000000}
			},
			lootChance = 200000
		}
	},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"stunattack",""}, {"creatureareaknockdown",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_elder_wampa, "hoth_elder_wampa")
