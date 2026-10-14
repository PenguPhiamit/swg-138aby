-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/items/bellum/hoth/hoth_vehicle_basilisk_war_droid_deed.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_vehicle_basilisk_war_droid_deed = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "Basilisk War Droid Deed",
	directObjectTemplate = "object/tangible/deed/vehicle_deed/basilisk_war_droid.iff",
	craftingValues = {},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("hoth_vehicle_basilisk_war_droid_deed", hoth_vehicle_basilisk_war_droid_deed)
