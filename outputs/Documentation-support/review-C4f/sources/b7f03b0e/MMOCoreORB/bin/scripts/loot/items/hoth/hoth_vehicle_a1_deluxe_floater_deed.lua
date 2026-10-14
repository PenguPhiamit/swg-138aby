-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/items/bellum/hoth/hoth_vehicle_a1_deluxe_floater_deed.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_vehicle_a1_deluxe_floater_deed = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "A-1 Deluxe Floater Deed",
	directObjectTemplate = "object/tangible/deed/vehicle_deed/a1_deluxe_floater_deed.iff",
	craftingValues = {},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("hoth_vehicle_a1_deluxe_floater_deed", hoth_vehicle_a1_deluxe_floater_deed)
