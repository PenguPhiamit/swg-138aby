-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_imperial_salvage_tech.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: hoth_art_rare, hoth_decor_common.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_common (3%).

hoth_imperial_salvage_tech = Creature:new {
	objectName = "",
	customName = "an Imperial salvage technician",
	randomNameType = NAME_STORMTROOPER,
	randomNameTag = true,
	mobType = MOB_NPC,
	socialGroup = "imperial",
	faction = "imperial",
	level = 72,
	chanceHit = 0.66,
	damageMin = 500,
	damageMax = 690,
	baseXp = 6900,
	baseHAM = 12500,
	baseHAMmax = 15000,
	armor = 1,
	resists = {30,30,30,30,60,30,30,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = PACK,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {
		"object/mobile/dressed_imperial_atat_pilot_m.iff"
	},
	lootGroups = {
		{
			groups = {
				{group = "hoth_decor_common", chance = 10000000}
			},
			lootChance = 300000
		}
	},
	primaryWeapon = "imperial_weapons_light",
	secondaryWeapon = "unarmed",
	conversationTemplate = "",
	reactionStf = "@npc_reaction/military",
	primaryAttacks = marksmanmid,
	secondaryAttacks = brawlermid
}

CreatureTemplates:addCreatureTemplate(hoth_imperial_salvage_tech, "hoth_imperial_salvage_tech")
