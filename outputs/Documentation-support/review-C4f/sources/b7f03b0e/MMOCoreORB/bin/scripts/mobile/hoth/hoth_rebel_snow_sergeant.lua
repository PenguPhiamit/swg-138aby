-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/mobile/hoth/hoth_rebel_snow_sergeant.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Changed: removed loot groups this server lacks: bg_token_group, hoth_art_rare, hoth_decor_common, hoth_rebel_snow_schematics.
-- Hoth loot slice (14 Oct 2026): drops hoth_decor_rare (5%).

hoth_rebel_snow_sergeant = Creature:new {
	objectName = "",
	customName = "a Rebel snow sergeant",
	randomNameType = NAME_GENERIC,
	randomNameTag = true,
	mobType = MOB_NPC,
	socialGroup = "rebel",
	faction = "rebel",
	level = 85,
	chanceHit = 0.84,
	damageMin = 610,
	damageMax = 870,
	baseXp = 8160,
	baseHAM = 15500,
	baseHAMmax = 18500,
	armor = 1,
	resists = {50,50,70,50,90,50,50,-1,-1},
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
	creatureBitmask = PACK + KILLER,
	optionsBitmask = AIENABLED,
	diet = HERBIVORE,
	templates = {
		"object/mobile/rebel_snow_m_01.iff",
		"object/mobile/rebel_snow_f_01.iff"
	},
	lootGroups = {
		{
			groups = {
				{group = "rebel_tier_4", chance = 10000000}
			}
		},
		{
			groups = {
				{group = "hoth_decor_rare", chance = 10000000}
			},
			lootChance = 500000
		}
	},
	primaryWeapon = "rebel_carbine",
	secondaryWeapon = "rebel_pistol",
	thrownWeapon = "thrown_weapons",
	conversationTemplate = "",
	reactionStf = "@npc_reaction/military",
	personalityStf = "@hireling/hireling_military",
	primaryAttacks = merge(carbineermaster,marksmanmaster),
	secondaryAttacks = merge(pistoleermaster,marksmanmaster)
}

CreatureTemplates:addCreatureTemplate(hoth_rebel_snow_sergeant, "hoth_rebel_snow_sergeant")
