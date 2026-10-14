-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/groups/bellum/hoth/hoth_vehicle_deeds.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Cut to the 18 of 30 items whose objects our client has; equal weights.

hoth_vehicle_deeds = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "hoth_vehicle_snowspeeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_landspeeder_ab1_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_landspeeder_xp38_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_landspeeder_organa_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_sith_speeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_basilisk_war_droid_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_stap_speeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_swamp_speeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_tcg_military_transport_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_tcg_8_single_pod_airspeeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_speeder_ric_920_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_podracer_anakin_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_mechno_chair_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_hover_chair_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_a1_deluxe_floater_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_mustafar_panning_droid_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_hoverlifter_speeder_deed", weight = 555555},
		{itemTemplate = "hoth_vehicle_flare_s_swoop_deed", weight = 555565}
	}
}

addLootGroupTemplate("hoth_vehicle_deeds", hoth_vehicle_deeds)
