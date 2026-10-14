-- Glacial rancor: the apex predator of our Hoth. Clean-room template (Fable, 14 Oct 2026; outputs/Fable-hoth-batchA/README.md).
-- The concept (a glacial rancor world boss on Hoth) comes from Bellum Gero's Hoth (github.com/Miphstoe/BellumGero-Live,
-- AGPL-3.0); nothing else does: their body (object/mobile/exotic_rancor.iff) is in no archive our client loads, so this
-- uses the stock rancor body with palette colour 15 of palette/creature_rancor.pal (RGB (244, 220, 139), the palest entry),
-- and its stats are scaled from Core3's own top bosses (krayt_dragon_ancient, level 336; giant_canyon_krayt_dragon,
-- level 300; ancient_bull_rancor, level 98) to level 400, Bellum's own value for this boss (not an owner decision yet; see README). Name and text are ours.
-- Not wired to any spawn yet: see the README for the three options.

hoth_glacial_rancor = Creature:new {
	objectName = "",
	customName = "Hoarfang, the Glacial Rancor",
	socialGroup = "rancor",
	faction = "",
	mobType = MOB_CARNIVORE,
	level = 400,
	chanceHit = 0.95,
	damageMin = 2700,
	damageMax = 5000,
	baseXp = 28549,
	baseHAM = 490000,
	baseHAMmax = 600000,
	armor = 3,
	resists = {195,195,195,150,200,195,195,195,-1},
	meatType = "meat_carnivore",
	meatAmount = 2000,
	hideType = "hide_leathery",
	hideAmount = 2000,
	boneType = "bone_mammal",
	boneAmount = 1900,
	milk = 0,
	tamingChance = 0,
	ferocity = 25,
	pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = CARNIVORE,

	templates = {"object/mobile/rancor.iff"},
	hues = { 15 },
	scale = 1.35,
	lootGroups = {
		{
			groups = {
				{group = "hoth_decor_rare", chance = 10000000}
			},
			lootChance = 10000000
		},
		{
			groups = {
				{group = "hoth_vehicle_deeds", chance = 10000000}
			},
			lootChance = 5000000
		}
	},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "",
	primaryAttacks = { {"creatureareableeding",""}, {"creatureareacombo",""}, {"creatureareaknockdown",""}, {"intimidationattack",""} },
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_glacial_rancor, "hoth_glacial_rancor")
