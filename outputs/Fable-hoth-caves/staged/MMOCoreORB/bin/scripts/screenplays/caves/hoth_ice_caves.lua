-- Hoth ice caves: wampa dens in the four ice caves of MTG's snapshot/hoth.ws.
-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/screenplays/caves/hoth_ice_caves.lua (their generated file; spawn rows are
-- {template, respawn, cell-local x, z, y, heading, cell object id}). Staged for this server 14 Oct 2026 (Fable;
-- outputs/Fable-hoth-caves/README.md). Every cell id below was checked against MTG's hoth.ws: it exists, it is a
-- cell of the named cave, and the cave sits where Bellum's comment says.
-- Changed: 23 spawns in Bellum's fifth cave (cave_06_flatland_s01_ice, building 6453174, cells
-- 6453175-6453185: the mynock den) are left out because that building is not in MTG's snapshot; the per-player
-- boss reward (WorldBossLootManager, giveHothBossRewards, HOTH_CAVE_BOSS_LOOT) and the two boss observers are
-- dropped, so the five named wampa bosses keep the corpse loot of their mobile templates; written in the style
-- of the other caves/ screenplays. Respawn times are Bellum's (420 s, bosses 1800 s).

HothIceCavesScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothIceCavesScreenPlay"
}

registerScreenPlay("HothIceCavesScreenPlay", true)

function HothIceCavesScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnMobiles()
	end
end

function HothIceCavesScreenPlay:spawnMobiles()
	-- cave_04_ice_s01 at -385.0, 2436.0 (height 58.0; building 6452962)
	--Cell[6452963]
	spawnMobile("hoth", "hoth_wampa", 420, 4.35, -15.68, -11.21, -103, 6452963)
	spawnMobile("hoth", "hoth_wampa", 420, 5.8, -12.21, -3.27, -93, 6452963)
	--Cell[6452964]
	spawnMobile("hoth", "hoth_wampa", 420, -11.23, -38.6, -51.36, -8, 6452964)
	spawnMobile("hoth", "hoth_wampa", 420, -4.19, -29.55, -31.12, -57, 6452964)
	--Cell[6452965]
	spawnMobile("hoth", "hoth_wampa", 420, -5.73, -40.3, -83.51, 1, 6452965)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -10.21, -40.46, -83.92, 32, 6452965)
	--Cell[6452966]
	spawnMobile("hoth", "hoth_wampa", 420, 34.42, -45.21, -95.44, -112, 6452966)
	spawnMobile("hoth", "hoth_wampa", 420, 42.64, -46.2, -91.94, -54, 6452966)
	--Cell[6452967]
	spawnMobile("hoth", "hoth_wampa", 420, 50.92, -56.35, -159.39, 51, 6452967)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 59.26, -51.38, -139.54, 109, 6452967)
	--Cell[6452968]
	spawnMobile("hoth", "hoth_wampa", 420, 14.01, -63.17, -185.93, -160, 6452968)
	spawnMobile("hoth", "hoth_wampa", 420, -15.49, -64.09, -185.35, -150, 6452968)
	--Cell[6452969]
	spawnMobile("hoth", "hoth_wampa", 420, -3.87, -64.71, -226.56, 176, 6452969)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -12.95, -65.77, -213.56, -121, 6452969)
	--Cell[6452970]
	spawnMobile("hoth", "hoth_wampa", 420, -69.21, -69.33, -192.88, -40, 6452970)
	spawnMobile("hoth", "hoth_wampa", 420, -114.59, -70.06, -197.56, -82, 6452970)
	--Cell[6452971]
	spawnMobile("hoth", "hoth_wampa", 420, -56.92, -68.35, -107.34, -79, 6452971)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -60.53, -68.5, -109.43, -54, 6452971)
	--Cell[6452972]
	spawnMobile("hoth", "hoth_wampa", 420, -21.75, -75.36, -126.02, 82, 6452972)
	spawnMobile("hoth", "hoth_wampa", 420, -20.18, -78.98, -139.24, 71, 6452972)
	--Cell[6452973]
	spawnMobile("hoth", "hoth_wampa_icemaw", 1800, -82.49, -102.21, -119, -166, 6452973)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -98.38, -100.16, -102.78, -55, 6452973)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -85.46, -102.6, -116.09, -145, 6452973)
	-- cave_02_ice at -543.0, 2674.0 (height 36.5; building 6452974)
	--Cell[6452975]
	spawnMobile("hoth", "hoth_wampa", 420, -13.96, -4.85, -4.85, -36, 6452975)
	spawnMobile("hoth", "hoth_wampa", 420, -10.12, -7.01, -6.54, -63, 6452975)
	--Cell[6452976]
	spawnMobile("hoth", "hoth_wampa", 420, 27.96, -36.93, -22.61, 109, 6452976)
	spawnMobile("hoth", "hoth_wampa", 420, 58.31, -51.06, -21.99, -38, 6452976)
	--Cell[6452977]
	spawnMobile("hoth", "hoth_wampa", 420, 88.85, -63.32, -23.21, -138, 6452977)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 79.59, -66.93, -33.05, 158, 6452977)
	--Cell[6452978]
	spawnMobile("hoth", "hoth_wampa", 420, 82.41, -76.3, -61.02, -136, 6452978)
	spawnMobile("hoth", "hoth_wampa", 420, 89.76, -74.69, -52.78, -84, 6452978)
	--Cell[6452979]
	spawnMobile("hoth", "hoth_wampa", 420, 92.73, -46.37, -121.19, -16, 6452979)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 68.88, -77.05, -93.98, 177, 6452979)
	--Cell[6452980]
	spawnMobile("hoth", "hoth_wampa", 420, 67.18, -67.07, -133.39, -148, 6452980)
	spawnMobile("hoth", "hoth_wampa", 420, 55, -76.35, -95.81, 127, 6452980)
	--Cell[6452981]
	spawnMobile("hoth", "hoth_wampa", 420, 85.65, -66.64, -133.79, 28, 6452981)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 89.52, -67.07, -136.22, 55, 6452981)
	--Cell[6452982]
	spawnMobile("hoth", "hoth_wampa", 420, 138.69, -66.29, -101.97, 86, 6452982)
	spawnMobile("hoth", "hoth_wampa", 420, 153.97, -66.52, -100.92, -167, 6452982)
	--Cell[6452983]
	spawnMobile("hoth", "hoth_wampa_snowblind", 1800, 159.25, -67.09, -101.44, -83, 6452983)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 188.35, -66.19, -102.5, 121, 6452983)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 191.75, -66.76, -105.62, 145, 6452983)
	--Cell[6452984]
	spawnMobile("hoth", "hoth_wampa", 420, 55.16, -48.93, -101.01, -44, 6452984)
	spawnMobile("hoth", "hoth_wampa", 420, 51.82, -49.26, -98.38, -68, 6452984)
	--Cell[6452985]
	spawnMobile("hoth", "hoth_wampa", 420, 81.55, -46.29, -139.32, -173, 6452985)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 78.66, -46.58, -142.11, 167, 6452985)
	-- cave_01_ice at -622.5, 2292.3 (height 183.3; building 6452986)
	--Cell[6452987]
	spawnMobile("hoth", "hoth_wampa", 420, 4.35, -15.68, -11.21, -103, 6452987)
	spawnMobile("hoth", "hoth_wampa", 420, 5.8, -12.21, -3.27, -93, 6452987)
	--Cell[6452988]
	spawnMobile("hoth", "hoth_wampa", 420, -11.23, -38.6, -51.36, -8, 6452988)
	spawnMobile("hoth", "hoth_wampa", 420, -4.19, -29.55, -31.12, -57, 6452988)
	--Cell[6452989]
	spawnMobile("hoth", "hoth_wampa", 420, -5.73, -40.3, -83.51, 1, 6452989)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -10.21, -40.46, -83.92, 32, 6452989)
	--Cell[6452990]
	spawnMobile("hoth", "hoth_wampa", 420, 34.42, -45.21, -95.44, -112, 6452990)
	spawnMobile("hoth", "hoth_wampa", 420, 42.64, -46.2, -91.94, -54, 6452990)
	--Cell[6452991]
	spawnMobile("hoth", "hoth_wampa", 420, 50.92, -56.35, -159.39, 51, 6452991)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 59.26, -51.38, -139.54, 109, 6452991)
	--Cell[6452992]
	spawnMobile("hoth", "hoth_wampa", 420, 14.01, -63.17, -185.93, -160, 6452992)
	spawnMobile("hoth", "hoth_wampa", 420, -15.49, -64.09, -185.35, -150, 6452992)
	--Cell[6452993]
	spawnMobile("hoth", "hoth_wampa", 420, -3.87, -64.71, -226.56, 176, 6452993)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -12.95, -65.77, -213.56, -121, 6452993)
	--Cell[6452994]
	spawnMobile("hoth", "hoth_wampa", 420, -69.21, -69.33, -192.88, -40, 6452994)
	spawnMobile("hoth", "hoth_wampa", 420, -114.59, -70.06, -197.56, -82, 6452994)
	--Cell[6452995]
	spawnMobile("hoth", "hoth_wampa", 420, -56.92, -68.35, -107.34, -79, 6452995)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -60.53, -68.5, -109.43, -54, 6452995)
	--Cell[6452996]
	spawnMobile("hoth", "hoth_wampa", 420, -21.75, -75.36, -126.02, 82, 6452996)
	spawnMobile("hoth", "hoth_wampa", 420, -20.18, -78.98, -139.24, 71, 6452996)
	--Cell[6452997]
	spawnMobile("hoth", "hoth_wampa_frostfang", 1800, -82.49, -102.21, -119, -166, 6452997)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -98.38, -100.16, -102.78, -55, 6452997)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -85.46, -102.6, -116.09, -145, 6452997)
	-- cave_03_ice at -75.0, 2969.0 (height 35.0; building 6452998)
	--Cell[6452999]
	spawnMobile("hoth", "hoth_wampa", 420, 0.5, -10.38, 2.73, -130, 6452999)
	spawnMobile("hoth", "hoth_wampa", 420, -1.19, -21.49, -16.27, -125, 6452999)
	--Cell[6453000]
	spawnMobile("hoth", "hoth_wampa", 420, -19.98, -29.91, -44.8, 53, 6453000)
	spawnMobile("hoth", "hoth_wampa", 420, -28.32, -29.35, -24.44, 112, 6453000)
	--Cell[6453001]
	spawnMobile("hoth", "hoth_wampa", 420, -45.4, -29.95, -43.8, -82, 6453001)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -35.66, -30.13, -46.15, -150, 6453001)
	--Cell[6453002]
	spawnMobile("hoth", "hoth_wampa", 420, -64.99, -45.19, -20.14, 102, 6453002)
	spawnMobile("hoth", "hoth_wampa", 420, -52.49, -38.87, -13.05, 15, 6453002)
	--Cell[6453003]
	spawnMobile("hoth", "hoth_wampa", 420, -83.8, -46.87, -52.52, -79, 6453003)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -59.91, -30.35, -45.35, 114, 6453003)
	--Cell[6453004]
	spawnMobile("hoth", "hoth_wampa", 420, -135.71, -49.65, -60.28, -29, 6453004)
	spawnMobile("hoth", "hoth_wampa", 420, -107.2, -36.8, -61.33, 132, 6453004)
	--Cell[6453005]
	spawnMobile("hoth", "hoth_wampa", 420, -71.7, -32.18, -81.55, -70, 6453005)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -74.61, -36.16, -96.34, -49, 6453005)
	--Cell[6453006]
	spawnMobile("hoth", "hoth_wampa", 420, -163.4, -49.95, -39.83, -101, 6453006)
	spawnMobile("hoth", "hoth_wampa", 420, -162.36, -49.86, -44.2, -108, 6453006)
	--Cell[6453007]
	spawnMobile("hoth", "hoth_wampa_patriarch", 1800, -95.13, -70.56, -112.36, -172, 6453007)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -75.76, -70.87, -123.72, 53, 6453007)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -77.42, -71.49, -117.95, 64, 6453007)
	--Cell[6453008]
	spawnMobile("hoth", "hoth_wampa", 420, -168.58, -49.66, -91.98, 30, 6453008)
	spawnMobile("hoth", "hoth_wampa", 420, -173.13, -49.72, -90.43, 61, 6453008)
	--Cell[6453009]
	spawnMobile("hoth", "hoth_wampa", 420, -131.88, -53.56, -92.78, -180, 6453009)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -92.89, -54.6, -85.2, -93, 6453009)
	--Cell[6453010]
	spawnMobile("hoth", "hoth_wampa", 420, -168.75, -53.22, -109.63, 125, 6453010)
	spawnMobile("hoth", "hoth_wampa", 420, -166.8, -54.19, -114.67, 111, 6453010)
	--Cell[6453011]
	spawnMobile("hoth", "hoth_wampa", 420, -128.99, -36.27, -74.17, -107, 6453011)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -126.96, -33.87, -69.56, -121, 6453011)
	--Cell[6453012]
	spawnMobile("hoth", "hoth_wampa", 420, -83.34, -57.69, -45.14, -19, 6453012)
	spawnMobile("hoth", "hoth_wampa", 420, -80.86, -58.64, -74.33, -36, 6453012)
	--Cell[6453013]
	spawnMobile("hoth", "hoth_wampa", 420, -103.65, -39.95, -43.45, 170, 6453013)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -103.61, -37.47, -49.38, 170, 6453013)
	--Cell[6453014]
	spawnMobile("hoth", "hoth_wampa", 420, -101.01, -58.33, -30.95, -161, 6453014)
	spawnMobile("hoth", "hoth_wampa", 420, -102.84, -42.1, -36.15, -149, 6453014)
	--Cell[6453015]
	spawnMobile("hoth", "hoth_wampa", 420, -108.38, -43.15, -13.88, -63, 6453015)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -103.89, -42.43, -13.13, -94, 6453015)
	--Cell[6453016]
	spawnMobile("hoth", "hoth_wampa", 420, -131.47, -57.46, -22.56, 146, 6453016)
	spawnMobile("hoth", "hoth_wampa", 420, -132.58, -53.85, -15.36, 154, 6453016)
	--Cell[6453017]
	spawnMobile("hoth", "hoth_wampa", 420, 13.26, -21.41, -21.64, 85, 6453017)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 18.92, -22.91, -24.94, 125, 6453017)
	--Cell[6453018]
	spawnMobile("hoth", "hoth_wampa", 420, 3.39, -67.44, -68.65, 63, 6453018)
	spawnMobile("hoth", "hoth_wampa", 420, 2.44, -67.12, -76.43, 57, 6453018)
	--Cell[6453019]
	spawnMobile("hoth", "hoth_wampa", 420, -21.55, -35.05, -70.04, -123, 6453019)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -31.18, -38.33, -79.49, -55, 6453019)
	--Cell[6453020]
	spawnMobile("hoth", "hoth_wampa", 420, -16.12, -44.02, -96.64, -114, 6453020)
	spawnMobile("hoth", "hoth_wampa", 420, -19.65, -40.18, -85.79, -89, 6453020)
	--Cell[6453021]
	spawnMobile("hoth", "hoth_wampa", 420, -125.87, -54.08, -115.94, -18, 6453021)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -130.23, -54.59, -117.39, 12, 6453021)
	--Cell[6453022]
	spawnMobile("hoth", "hoth_wampa", 420, -124.75, -60.22, -134.18, 21, 6453022)
	spawnMobile("hoth", "hoth_wampa", 420, -108.21, -66.65, -132.57, -95, 6453022)
	--Cell[6453023]
	spawnMobile("hoth", "hoth_wampa", 420, -64.8, -66.21, -139.44, 8, 6453023)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -49.93, -68.1, -133.42, -96, 6453023)
	--Cell[6453024]
	spawnMobile("hoth", "hoth_wampa", 420, 4.3, -67.97, -89.81, -8, 6453024)
	spawnMobile("hoth", "hoth_wampa", 420, 3.27, -70.72, -101.68, -16, 6453024)
	--Cell[6453025]
	spawnMobile("hoth", "hoth_wampa", 420, 44.65, -67.45, -69.36, -39, 6453025)
	spawnMobile("hoth", "hoth_elder_wampa", 420, 43.02, -68.75, -100.91, -50, 6453025)
	--Cell[6453026]
	spawnMobile("hoth", "hoth_wampa", 420, -58.87, -65.79, -182.06, 108, 6453026)
	spawnMobile("hoth", "hoth_wampa", 420, -57.82, -66.02, -197.35, 100, 6453026)
	--Cell[6453027]
	spawnMobile("hoth", "hoth_wampa_matriarch", 1800, -58.34, -66.58, -202.62, 151, 6453027)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -59.4, -65.68, -231.73, 158, 6453027)
	spawnMobile("hoth", "hoth_elder_wampa", 420, -62.52, -66.26, -235.12, -180, 6453027)
end
