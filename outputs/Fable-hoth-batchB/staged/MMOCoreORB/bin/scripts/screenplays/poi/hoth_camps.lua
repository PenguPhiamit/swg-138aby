-- Hoth camps and patrol posts (Fable batch B, 14 Oct 2026; outputs/Fable-hoth-batchB/README.md).
-- Layout idea from Bellum Gero's Hoth static spawns (github.com/Miphstoe/BellumGero-Live, AGPL-3.0: NPC rings
-- at each outpost, two trooper/rebel lines, a raider camp), re-sited into our batch A zones on MTG's map with
-- stock camp props. Heights are the terrain heights at each point (Core3 height port, validated on Hoth).

HothCampsScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothCampsScreenPlay"
}

registerScreenPlay("HothCampsScreenPlay", true)

function HothCampsScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
		self:spawnMobiles()
	end
end

function HothCampsScreenPlay:spawnSceneObjects()
	-- imperial_forward_camp at 2600, -3900 (hoth_imperial_zone_east)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_imperial_16_style_01.iff", 2586, 33.5, -3882, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_imperial_16_style_01.iff", 2614, 33.2, -3882, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_imperial_16_style_01.iff", 2586, 34.4, -3918, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_imperial_16_style_01.iff", 2614, 33.6, -3918, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", 2592, 33.6, -3894, 0, 180)
	spawnSceneObject("hoth", "object/static/structure/military/bunker_crate_style_01.iff", 2607, 33.3, -3893, 0, 30)
	spawnSceneObject("hoth", "object/static/structure/general/campfire_fresh.iff", 2600, 33.5, -3898, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/palette_supply_01.iff", 2610, 33.4, -3904, 0, 0)
	-- rebel_forward_camp at -2800, 1200 (hoth_rebel_zone_northwest)
	spawnSceneObject("hoth", "object/static/structure/general/poi_all_rebl_corral_64x64_s01.iff", -2800, 23.3, 1200, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_rebl_16_style_01.iff", -2814, 22.1, 1182, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/military_wall_med_rebl_16_style_01.iff", -2786, 21.6, 1182, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", -2792, 22.7, 1194, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", -2809, 23.1, 1195, 0, 20)
	spawnSceneObject("hoth", "object/static/structure/general/campfire_fresh.iff", -2800, 23.1, 1198, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_cot_s01.iff", -2794, 23.6, 1204, 0, 90)
	-- scavenger_camp at -1400, -3300 (hoth_scavenger_zone_southwest)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", -1407, 10, -3295, 0, 150)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", -1393, 10, -3294, 0, 210)
	spawnSceneObject("hoth", "object/static/structure/general/campfire_fresh.iff", -1400, 10, -3300, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_spit_s01.iff", -1400, 10, -3297, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_cot_s01.iff", -1406, 10, -3303, 0, 60)
	spawnSceneObject("hoth", "object/static/structure/general/camp_stool_short_s01.iff", -1398, 10, -3302, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/camp_stool_short_s01.iff", -1402, 10, -3302, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/palette_supply_01.iff", -1391, 10, -3305, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/general/atst_debris_01.iff", -1382, 10, -3286, 0, 40)
	-- raider_camp at -1200, -3600 (hoth_scavenger_zone_southwest)
	spawnSceneObject("hoth", "object/static/structure/general/camp_tent_s01.iff", -1200, 12.8, -3593, 0, 180)
	spawnSceneObject("hoth", "object/static/structure/general/campfire_fresh.iff", -1200, 12.5, -3600, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/bunker_crate_style_01.iff", -1194, 12.5, -3597, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/bunker_crate_style_01.iff", -1206, 12.7, -3597, 0, 0)
	-- contested_ground at 2400, 200 (between the zones)
	spawnSceneObject("hoth", "object/static/structure/general/atst_debris_01.iff", 2400, 23.5, 200, 0, 75)
	spawnSceneObject("hoth", "object/static/structure/military/bunker_crate_style_01.iff", 2396, 23.5, 214, 0, 0)
	spawnSceneObject("hoth", "object/static/structure/military/bunker_crate_style_01.iff", 2404, 23.7, 186, 0, 0)
	-- salvage_detail at -100, -1960 (outpost (MTG debris field, flattened ground))
end

function HothCampsScreenPlay:spawnMobiles()
	-- imperial_forward_camp
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2612, 33.3, -3900, -90, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2588, 33.7, -3900, 90, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2600, 33.4, -3887, 180, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2600, 33.8, -3913, 0, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2609, 33.3, -3891, -135, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2591, 33.9, -3909, 45, 0)
	spawnMobile("hoth", "hoth_snowtrooper_sergeant", 300, 2603, 33.5, -3903, 135, 0)
	spawnMobile("hoth", "imperial_recruiter", 60, 2596, 33.5, -3896, -45, 0)
	-- rebel_forward_camp
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2788, 23.2, 1200, -90, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2812, 23.6, 1200, 90, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2800, 24.5, 1213, 180, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2800, 22.2, 1187, 0, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2791, 24, 1209, -135, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, -2809, 22.7, 1191, 45, 0)
	spawnMobile("hoth", "hoth_rebel_snow_sergeant", 300, -2797, 23.5, 1203, -135, 0)
	spawnMobile("hoth", "rebel_recruiter", 60, -2804, 23, 1196, 45, 0)
	-- scavenger_camp
	spawnMobile("hoth", "hoth_scavenger", 300, -1395, 10, -3299, 15, 0)
	spawnMobile("hoth", "hoth_scavenger", 300, -1397, 10, -3305, 87, 0)
	spawnMobile("hoth", "hoth_scavenger", 300, -1404, 10, -3306, 159, 0)
	spawnMobile("hoth", "hoth_scavenger", 300, -1406, 10, -3298, -129, 0)
	spawnMobile("hoth", "hoth_scavenger", 300, -1401, 10, -3294, -57, 0)
	spawnMobile("hoth", "junk_dealer", 60, -1396, 10, -3296, -120, 0)
	-- raider_camp
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1200, 12.9, -3590, 0, 0)
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1191.3, 12.6, -3595, 60, 0)
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1191.3, 12.2, -3605, 120, 0)
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1200, 12.3, -3610, 180, 0)
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1208.7, 12.5, -3605, -120, 0)
	spawnMobile("hoth", "hoth_scavenger_raider", 300, -1208.7, 12.8, -3595, -60, 0)
	-- contested_ground
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2394, 23.6, 214, 180, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2397, 23.4, 214, 180, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2403, 23.3, 214, 180, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, 2406, 23.2, 214, 180, 0)
	spawnMobile("hoth", "hoth_snowtrooper_sergeant", 300, 2400, 23.3, 218, 180, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, 2394, 24.1, 186, 0, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, 2397, 24, 186, 0, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, 2403, 23.7, 186, 0, 0)
	spawnMobile("hoth", "hoth_rebel_snow_soldier", 300, 2406, 23.6, 186, 0, 0)
	spawnMobile("hoth", "hoth_rebel_snow_sergeant", 300, 2400, 23.9, 182, 0, 0)
	-- salvage_detail
	spawnMobile("hoth", "hoth_imperial_salvage_tech", 300, -95, 0, -1956, 60, 0)
	spawnMobile("hoth", "hoth_imperial_salvage_tech", 300, -102, 0, -1953, 180, 0)
	spawnMobile("hoth", "hoth_imperial_salvage_tech", 300, -106, 0, -1958, -60, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, -90, 0, -1966, 0, 0)
	spawnMobile("hoth", "hoth_snowtrooper", 300, -110, 0, -1966, 0, 0)
end
