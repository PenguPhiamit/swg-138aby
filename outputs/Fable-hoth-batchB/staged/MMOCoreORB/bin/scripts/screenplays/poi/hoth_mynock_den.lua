-- Mynock den: Bellum Gero's fifth Hoth cave (cave_06_flatland_s01_ice, 23 spawns) re-homed on MTG's map, where
-- that building is not in the snapshot. The cave is spawned here and its cells looked up by number, so the
-- cell-local spawn points from Bellum's generated hoth_ice_caves.lua (AGPL-3.0) apply unchanged.
-- Needs the terrain patch in outputs/Fable-hoth-batchB/staged/client/terrain/hoth.trn (flatten + mouth exclusion)
-- packed into local_planets.tre; see the README. Fable batch B, 14 Oct 2026.

HothMynockDenScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothMynockDenScreenPlay",

	caveTemplate = "object/building/general/cave_06_flatland_s01_ice.iff",
	caveX = -2000, caveZ = 44.8, caveY = -4800, caveHeading = 0,

	-- {template, respawn, cell-local x, z, y, heading, cell number (1..11 in portal-layout order)}
	mobiles = {
		{"hoth_ice_mynock", 420, 4.35, -7.68, -11.21, -103, 1},
		{"hoth_ice_mynock", 420, 5.8, -4.21, -3.27, -93, 1},
		{"hoth_ice_mynock", 420, -11.23, -30.6, -51.36, -8, 2},
		{"hoth_ice_mynock", 420, -4.19, -21.55, -31.12, -57, 2},
		{"hoth_ice_mynock", 420, -5.73, -32.3, -83.51, 1, 3},
		{"hoth_greater_ice_mynock", 420, -10.21, -32.46, -83.92, 32, 3},
		{"hoth_ice_mynock", 420, 34.42, -37.21, -95.44, -112, 4},
		{"hoth_ice_mynock", 420, 42.64, -38.2, -91.94, -54, 4},
		{"hoth_ice_mynock", 420, 50.92, -48.35, -159.39, 51, 5},
		{"hoth_greater_ice_mynock", 420, 59.26, -43.38, -139.54, 109, 5},
		{"hoth_ice_mynock", 420, 14.01, -55.17, -185.93, -160, 6},
		{"hoth_ice_mynock", 420, -15.49, -56.09, -185.35, -150, 6},
		{"hoth_ice_mynock", 420, -3.87, -56.71, -226.56, 176, 7},
		{"hoth_greater_ice_mynock", 420, -12.95, -57.77, -213.56, -121, 7},
		{"hoth_ice_mynock", 420, -69.21, -61.33, -192.88, -40, 8},
		{"hoth_ice_mynock", 420, -114.59, -62.06, -197.56, -82, 8},
		{"hoth_ice_mynock", 420, -56.92, -60.35, -107.34, -79, 9},
		{"hoth_greater_ice_mynock", 420, -60.53, -60.5, -109.43, -54, 9},
		{"hoth_ice_mynock", 420, -21.75, -67.36, -126.02, 82, 10},
		{"hoth_ice_mynock", 420, -20.18, -70.98, -139.24, 71, 10},
		{"hoth_mynock_broodmother", 1800, -82.49, -94.21, -119, -166, 11},
		{"hoth_greater_ice_mynock", 420, -98.38, -92.16, -102.78, -55, 11},
		{"hoth_greater_ice_mynock", 420, -85.46, -94.6, -116.09, -145, 11},
	}
}

registerScreenPlay("HothMynockDenScreenPlay", true)

function HothMynockDenScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnDen()
	end
end

function HothMynockDenScreenPlay:spawnDen()
	local pCave = spawnSceneObject("hoth", self.caveTemplate, self.caveX, self.caveZ, self.caveY, 0, self.caveHeading)

	if (pCave == nil or not SceneObject(pCave):isBuildingObject()) then
		print("HothMynockDenScreenPlay: could not spawn " .. self.caveTemplate)
		return
	end

	local cells = BuildingObject(pCave):getTotalCellNumber()

	if (cells < 11) then
		print("HothMynockDenScreenPlay: cave has " .. cells .. " cells, expected 11")
	end

	for i = 1, #self.mobiles do
		local m = self.mobiles[i]
		local pCell = BuildingObject(pCave):getCell(m[7])

		if (pCell ~= nil) then
			spawnMobile("hoth", m[1], m[2], m[3], m[4], m[5], m[6], SceneObject(pCell):getObjectID())
		else
			print("HothMynockDenScreenPlay: cave has no cell " .. m[7])
		end
	end
end
