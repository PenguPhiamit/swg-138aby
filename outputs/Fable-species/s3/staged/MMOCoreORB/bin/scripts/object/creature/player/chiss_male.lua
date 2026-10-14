-- Chiss male player race template. Sandbox: Fable species S3 (14 Oct 2026; outputs/Fable-species/README.md).
-- Shape: Core3-dev's object/creature/player/zabrak_male.lua. The shared client template (object/creature/player/
-- shared_chiss_male.iff) is the Halyn/Phoenix species package's, carried by MTG patch 023 and declared in objects.lua.
-- Attribute mods: the package's racial_mods row for chiss (all 100, human-like); the same row goes into the client's
-- datatables/creation/racial_mods.iff. Harmless until the client lists Chiss (ui_avatardata.inc) and Races.h names it.

object_creature_player_chiss_male = object_creature_player_shared_chiss_male:new {
	baseHAM = { 100, 100, 100, 100, 100, 100, 100, 100, 100 },
	gameObjectType = 1033,
	groundZoneComponent = "PlayerZoneComponent",
	spaceZoneComponent = "PlayerSpaceZoneComponent",
	objectMenuComponent = "PlayerObjectMenuComponent",
	containerComponent = "PlayerContainerComponent",
	pvpStatusBitmask = PLAYER,
	templateType = PLAYERCREATURE,
	childObjects = {
		{templateFile = "object/player/player.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4},
		{templateFile = "object/tangible/inventory/character_inventory.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4},
		{templateFile = "object/tangible/datapad/character_datapad.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4},
		{templateFile = "object/tangible/mission_bag/mission_bag.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4},
		{templateFile = "object/weapon/melee/unarmed/unarmed_default_player.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4},
		{templateFile = "object/tangible/bank/character_bank.iff", x = 0, z = 0, y = 0, ox = 0, oy = 0, oz = 0, ow = 0, cellid = -1, containmentType = 4}
	},
	defaultLanguage = 1,
	startingItems = { },
	startingSkills = { "species_chiss", "social_language_basic_comprehend", "social_language_basic_speak" }
}

ObjectTemplates:addTemplate(object_creature_player_chiss_male, "object/creature/player/chiss_male.iff")
