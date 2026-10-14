-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/object/tangible/deed/vehicle_deed/vehicle_deed_organa_speeder.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Unchanged; placed under custom_content like the other later-era vehicle deeds.

object_tangible_deed_vehicle_deed_vehicle_deed_organa_speeder = object_tangible_deed_vehicle_deed_shared_vehicle_deed_organa_speeder:new {

	templateType = VEHICLEDEED,

	controlDeviceObjectTemplate = "object/intangible/vehicle/landspeeder_organa_pcd.iff",
	generatedObjectTemplate = "object/mobile/vehicle/landspeeder_organa.iff",

	numberExperimentalProperties = {1, 1, 1},
	experimentalProperties = {"XX", "XX", "SR"},
	experimentalWeights = {1, 1, 1},
	experimentalGroupTitles = {"null", "null", "exp_durability"},
	experimentalSubGroupTitles = {"null", "null", "hit_points"},
	experimentalMin = {0, 0, 1500},
	experimentalMax = {0, 0, 3000},
	experimentalPrecision = {0, 0, 0},
	experimentalCombineType = {0, 0, 1},
}

ObjectTemplates:addTemplate(object_tangible_deed_vehicle_deed_vehicle_deed_organa_speeder, "object/tangible/deed/vehicle_deed/vehicle_deed_organa_speeder.iff")
