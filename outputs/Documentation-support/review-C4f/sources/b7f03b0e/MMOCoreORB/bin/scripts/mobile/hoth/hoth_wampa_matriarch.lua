-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_wampa_matriarch.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_rare (5%), hoth_vehicle_deeds (2%).

hoth_wampa_matriarch = Creature:new {
	objectName = "",
	customName = "the wampa matriarch",
	socialGroup = "wampa",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 110,
	chanceHit = 1.05,
	damageMin = 740,
	damageMax = 1130,
	baseXp = 10560,
	baseHAM = 54000,
	baseHAMmax = 60000,
	armor = 2,
	resists = {160,180,45,220,45,220,45,45,-1},
	meatType = "meat_carnivore",
	meatAmount = 1200,
	hideType = "hide_wooly",
	hideAmount = 1200,
	boneType = "bone_mammal",
	boneAmount = 1000,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/wampa.iff"},
	scale = 1.45,
	lootGroups = {
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
	primaryAttacks = { {"stunattack",""}, {"creatureareaknockdown",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_wampa_matriarch, "hoth_wampa_matriarch")
