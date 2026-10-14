-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_mynock_broodmother.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_rare (5%), hoth_vehicle_deeds (2%).

hoth_mynock_broodmother = Creature:new {
	objectName = "",
	customName = "the mynock broodmother",
	socialGroup = "mynock",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 100,
	chanceHit = 0.97,
	damageMin = 680,
	damageMax = 1040,
	baseXp = 9600,
	baseHAM = 40000,
	baseHAMmax = 45000,
	armor = 2,
	resists = {160,180,45,220,45,220,45,45,-1},
	meatType = "meat_carnivore",
	meatAmount = 150,
	hideType = "hide_leathery",
	hideAmount = 200,
	boneType = "bone_mammal",
	boneAmount = 80,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,
	templates = {"object/mobile/salt_mynock_hue.iff"},
	hues = { 16, 17, 18, 19, 20, 21, 22, 23 },
	scale = 1.8,
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
	primaryAttacks = { {"blindattack",""}, {"creatureareaknockdown",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_mynock_broodmother, "hoth_mynock_broodmother")
