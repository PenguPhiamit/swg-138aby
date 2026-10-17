-- Hoth: Echo Base, first look (Fable E0, 14 Oct 2026; outputs/Fable-echo-base/README.md).
-- The NGE heroic building (object/building/heroic/shared_echo_base.iff, from the MTG archives) placed where MTG's
-- hoth.trn cut the terrain for it: its hangar, main-door and tower openings fit MTG's three cut-outs within 2.3 m RMS
-- at origin -5112.8, 5096.6, heading 0, height 37.6 m (the three doors agree within 2.1 m). Owner:
-- /teleport -5051 5440 hoth (main door), /teleport -5307 5750 hoth (hangar), /teleport -5036 5120 hoth (tower).
-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md; owner, 17 Oct: "Use the NGE building"): the ruin's
-- people. Abandoned since the Galactic Civil War, Echo Base is being stripped by Vorn Skarrel's salvage crews; wampas
-- have taken the lower halls, ice mynocks the hangar. Positions are floor-mesh triangle centres of the building's pob
-- (appearance/echo_base_pob.pob, 41 cells; read with Fable-echo-base/tools/fit_echo_base.py's reader), in cell-local
-- coordinates, so each spawn stands on a cell floor; cells by number through BuildingObject:getCell. The baron is
-- Hask Moor's job target (HothFillJobs, screenplays/sandbox/hoth_world.lua).
HothEchoBaseScreenPlay = ScreenPlay:new {
	numberOfActs = 1,
	screenplayName = "HothEchoBaseScreenPlay",

	-- cell number, template, x, z (height), y in the cell, respawn seconds
	interior = {
		-- the hangar (cell 11): mynocks in the roof, salvagers at the wrecks
		{ 11, "hoth_ice_mynock", -257.87, 73.32, 536.24, 420 },
		{ 11, "hoth_ice_mynock", -180.84, 73.51, 581.26, 420 },
		{ 11, "hoth_greater_ice_mynock", -206.39, 95.25, 517.99, 420 },
		{ 12, "hoth_echo_salvager", -322.24, 78.21, 498.96, 600 },
		{ 13, "hoth_echo_salvager", -295.54, 77.64, 476.93, 600 },
		{ 14, "hoth_echo_cutter", -183.79, 77.93, 506.37, 600 },
		-- the main door (cell 1) and the corridors down from it
		{ 1, "hoth_echo_salvager", 33.98, 48.32, 284.30, 600 },
		{ 1, "hoth_echo_salvager", 4.31, 58.54, 259.10, 600 },
		{ 3, "hoth_echo_cutter", 33.99, 25.29, 206.08, 600 },
		{ 4, "hoth_echo_salvager", 28.65, 22.61, 119.63, 600 },
		{ 4, "hoth_echo_cutter", 51.25, 22.57, 29.51, 600 },
		-- the upper rooms (cells 7, 16, 39)
		{ 7, "hoth_echo_cutter", -15.53, 64.31, 112.43, 600 },
		{ 7, "hoth_echo_salvager", -44.14, 64.31, 130.81, 600 },
		{ 16, "hoth_echo_salvager", -13.22, 58.14, 236.57, 600 },
		{ 39, "hoth_echo_cutter", 10.67, 64.31, 105.28, 600 },
		-- the long ramps (cells 17, 18, 20)
		{ 17, "hoth_echo_cutter", -226.02, 47.94, 302.13, 600 },
		{ 18, "hoth_echo_salvager", -90.40, -3.54, 150.77, 600 },
		{ 20, "hoth_echo_cutter", -98.75, 43.33, 358.28, 600 },
		{ 20, "hoth_echo_cutter", -86.62, 43.12, 316.51, 600 },
		-- the lower halls, the wampas' (cells 10, 21, 22)
		{ 10, "hoth_wampa", 8.44, -21.94, 136.37, 600 },
		{ 10, "hoth_wampa", 23.10, -15.84, 148.45, 600 },
		{ 10, "hoth_wampa", 4.97, -18.21, 9.37, 600 },
		{ 21, "hoth_wampa", -204.29, 20.32, 152.51, 600 },
		{ 21, "hoth_elder_wampa", -124.00, 13.50, 169.01, 600 },
		{ 22, "hoth_elder_wampa", -209.18, -23.25, 151.70, 600 },
		{ 22, "hoth_elder_wampa", -236.15, -22.86, 160.16, 600 },
		-- the deep halls under the hangar: Old Echo (cells 31-33)
		{ 31, "hoth_elder_wampa", -275.03, -22.89, 485.42, 600 },
		{ 32, "hoth_elder_wampa", -302.81, -25.84, 429.42, 600 },
		{ 33, "hoth_wampa_old_echo", -170.20, -20.61, 538.57, 1800 },
		-- the baron's hall (cells 27-29) and his cutters
		{ 27, "hoth_echo_cutter", 91.52, -13.93, 222.67, 600 },
		{ 28, "hoth_echo_cutter", 84.37, -14.66, 282.87, 600 },
		{ 29, "hoth_echo_cutter", -23.41, -18.21, 303.11, 600 },
		{ 29, "hoth_echo_cutter", 73.16, -14.61, 302.94, 600 },
	},

	-- the baron: no engine respawn, so his kill observer comes back with him
	baron = { 29, "hoth_salvage_baron_skarrel", 10.41, -17.73, 306.20, 1800 },
}

registerScreenPlay("HothEchoBaseScreenPlay", true)

function HothEchoBaseScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
	end
end

function HothEchoBaseScreenPlay:spawnSceneObjects()
	local pBuilding = spawnSceneObject("hoth", "object/building/heroic/echo_base.iff", -5112.8, 37.6, 5096.6, 0, 0)

	if pBuilding == nil then
		printLuaError("HothEchoBaseScreenPlay: could not spawn the building")
		return
	end

	writeData("hothEchoBase:building", SceneObject(pBuilding):getObjectID())

	for _, s in ipairs(self.interior) do
		self:spawnInCell(pBuilding, s)
	end

	self:spawnBaron()
end

function HothEchoBaseScreenPlay:spawnInCell(pBuilding, s)
	local pCell = BuildingObject(pBuilding):getCell(s[1])

	if pCell == nil then
		printLuaError("HothEchoBaseScreenPlay: the building has no cell " .. s[1])
		return nil
	end

	local pMobile = spawnMobile("hoth", s[2], s[6], s[3], s[4], s[5], getRandomNumber(0, 359), SceneObject(pCell):getObjectID())

	if pMobile == nil then
		printLuaError("HothEchoBaseScreenPlay: could not spawn " .. s[2] .. " in cell " .. s[1])
	end

	return pMobile
end

function HothEchoBaseScreenPlay:spawnBaron()
	local pBuilding = getSceneObject(readData("hothEchoBase:building"))

	if pBuilding == nil then
		return
	end

	local b = self.baron
	local pMobile = self:spawnInCell(pBuilding, { b[1], b[2], b[3], b[4], b[5], 0 })

	if pMobile ~= nil then
		createObserver(OBJECTDESTRUCTION, "HothEchoBaseScreenPlay", "onBaronKilled", pMobile)
	end
end

function HothEchoBaseScreenPlay:onBaronKilled(pVictim, pAttacker)
	if pVictim ~= nil and HothFillJobs ~= nil then
		HothFillJobs:creditKill(pVictim, pAttacker, "echo")
	end

	createEvent(self.baron[6] * 1000, "HothEchoBaseScreenPlay", "spawnBaron", nil, "")

	return 1
end
