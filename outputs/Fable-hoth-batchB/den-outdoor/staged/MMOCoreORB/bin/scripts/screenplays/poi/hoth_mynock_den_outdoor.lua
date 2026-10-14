-- Mynock den, option 2: an outdoor den in the mynock fields (hoth_mynock_fields_south), no client change.
-- The same creatures, counts and respawn times as option 1 (Bellum Gero's cave den, AGPL-3.0; outputs/Fable-hoth-batchB),
-- laid out by us on the open snow around stock ice stalagmites and columns. Heights from the Core3 height port.
-- Fable batch B (den-outdoor), 14 Oct 2026. Do not load together with poi/hoth_mynock_den.lua (option 1).

HothMynockDenOutdoorScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothMynockDenOutdoorScreenPlay"
}

registerScreenPlay("HothMynockDenOutdoorScreenPlay", true)

function HothMynockDenOutdoorScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
		self:spawnMobiles()
	end
end

function HothMynockDenOutdoorScreenPlay:spawnSceneObjects()
	-- 7-argument spawnSceneObject: heading in radians
	spawnSceneObject("hoth", "object/static/structure/general/cave_column_ice_style_01.iff", -1996.5, 43.9, -4793.9, 0, math.rad(0))
	spawnSceneObject("hoth", "object/static/structure/general/cave_column_ice_style_02.iff", -1996.5, 44.8, -4806.1, 0, math.rad(120))
	spawnSceneObject("hoth", "object/static/structure/general/cave_column_ice_style_03.iff", -2007.0, 44.6, -4800.0, 0, math.rad(240))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_01.iff", -1996.9, 42.7, -4782.3, 0, math.rad(0))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_02.iff", -1986.2, 42.7, -4788.4, 0, math.rad(40))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_03.iff", -1982.0, 43.7, -4800.0, 0, math.rad(80))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_04.iff", -1986.2, 45.0, -4811.6, 0, math.rad(120))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_05.iff", -1996.9, 43.6, -4817.7, 0, math.rad(160))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_06.iff", -2009.0, 42.8, -4815.6, 0, math.rad(200))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_07.iff", -2016.9, 43.2, -4806.2, 0, math.rad(240))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_08.iff", -2016.9, 44.6, -4793.8, 0, math.rad(280))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_09.iff", -2009.0, 43.7, -4784.4, 0, math.rad(320))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_01.iff", -1985.6, 40.8, -4769.2, 0, math.rad(0))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_03.iff", -1966.1, 42.8, -4797.0, 0, math.rad(60))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_05.iff", -1980.5, 43.9, -4827.9, 0, math.rad(120))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_07.iff", -2014.4, 40.9, -4830.8, 0, math.rad(180))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_09.iff", -2033.9, 42.4, -4803.0, 0, math.rad(240))
	spawnSceneObject("hoth", "object/static/structure/general/cave_stalagmite_ice_style_02.iff", -2019.5, 43.0, -4772.1, 0, math.rad(300))
end

function HothMynockDenOutdoorScreenPlay:spawnMobiles()
	spawnMobile("hoth", "hoth_mynock_broodmother", 1800, -2000.0, 44.6, -4798.0, 180, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -2000.0, 43.5, -4788.0, 0, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -1990.6, 43.4, -4792.5, 51, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -1988.3, 44.3, -4802.7, 102, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -1994.8, 44.5, -4810.8, 154, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -2005.2, 43.6, -4810.8, -155, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -2011.7, 44.0, -4802.7, -103, 0)
	spawnMobile("hoth", "hoth_greater_ice_mynock", 420, -2009.4, 44.7, -4792.5, -52, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1990.1, 41.7, -4776.0, 22, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1976.0, 42.5, -4790.1, 67, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1976.0, 44.3, -4809.9, 112, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1990.1, 43.6, -4824.0, 157, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2009.9, 41.9, -4824.0, -158, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2024.0, 42.3, -4809.9, -113, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2024.0, 44.6, -4790.1, -68, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2009.9, 42.9, -4776.0, -23, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2000.0, 40.2, -4756.0, 0, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1965.6, 40.6, -4772.6, 51, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1957.1, 43.6, -4809.8, 102, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -1980.9, 42.9, -4839.6, 154, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2019.1, 39.6, -4839.6, -155, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2042.9, 41.1, -4809.8, -103, 0)
	spawnMobile("hoth", "hoth_ice_mynock", 420, -2034.4, 43.8, -4772.6, -52, 0)
end
