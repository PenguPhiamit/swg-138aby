-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/items/bellum/hoth/hoth_vehicle_tcg_8_single_pod_airspeeder_deed.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged.

hoth_vehicle_tcg_8_single_pod_airspeeder_deed = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "Single-Pod Airspeeder Deed",
	directObjectTemplate = "object/tangible/deed/vehicle_deed/tcg_8_air_speeder_deed.iff",
	craftingValues = {},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("hoth_vehicle_tcg_8_single_pod_airspeeder_deed", hoth_vehicle_tcg_8_single_pod_airspeeder_deed)
