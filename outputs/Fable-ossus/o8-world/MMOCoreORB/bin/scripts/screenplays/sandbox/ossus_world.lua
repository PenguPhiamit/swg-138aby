-- Ossus world (O8; outputs/Fable-ossus/o8-world/README.md): the owner found Ossus empty (17 Oct). This adds
--   townsfolk at Knossa and the settlements, and an Imperial patrol on the memorial road below the garrison;
--   six places to find outside the settlements (camps with props from the stock art, fighters with loot, two who talk);
--   the dungeon: a One Sith cell in the west foothill cave (POI 14, snapshot node 6900002, cells 6900003-6900013),
--   with spawns in every cell and Keeper Raskal Vonn in the deepest chamber.
-- Server objects only: no client data, no terrain change. Our own code and text; era 138-139 ABY.

OssusWorld = ScreenPlay:new {
	planet = "ossus",

	-- template, x, y, heading, display name (nil: the template's), respawn seconds
	townsfolk = {
		-- Knossa (the starport footprint and the old-town statics stay clear)
		{ "ossus_knossa_pilgrim", 12, -3570, 200 },
		{ "ossus_knossa_settler", -40, -3640, 90 },
		{ "commoner", 40, -3575, 250, "a settler", 300 },
		{ "commoner_naboo", -95, -3585, 120, "a settler", 300 },
		{ "nomad", 60, -3650, 300, "a scavenger", 300 },
		{ "commoner", -110, -3630, 45, "a pilgrim", 300 },
		{ "commoner_naboo", -15, -3690, 0, "a pilgrim", 300 },
		{ "artisan", -54, -3652, 0, "a trader", 300 },
		{ "artisan", 2, -3652, 0, "a trader", 300 },
		{ "nomad", 95, -3600, 270, "a traveller", 300 },
		-- the Adega hamlet, the Ysanna camp, the Hutt field
		{ "farmer", -3040, 1090, 200, "a fisher", 300 },
		{ "commoner_old", -3055, 1110, 30, "a net mender", 300 },
		{ "nomad", -1318, -4940, 270, "an Ysanna tracker", 300 },
		{ "mercenary", 3392, -2290, 180, "a Hutt guard", 300 },
		{ "mercenary", 3410, -2290, 180, "a Hutt guard", 300 },
		{ "thief", 3415, -2310, 90, "a cargo handler", 300 },
	},

	-- the patrol walks the road between the last two memorial stones and back (stone 14 stands on the 33 degree climb)
	patrol = {
		templates = { "imperial_trooper", "imperial_trooper", "imperial_first_lieutenant" },
		points = { { 1740.2, 2304.6 }, { 1860.0, 2500.0 }, { 1983.0, 2694.1 }, { 1860.0, 2500.0 } },
		pause = 20,
	},

	-- the places to find: centre, props (server template, dx, dy, heading in degrees), people (template, dx, dy, name, respawn)
	places = {
		{ name = "the scavengers' battle site", x = 1408, y = -640,
			props = {
				{ "object/static/structure/corellia/corl_tent_med.iff", -8, 6, 160 },
				{ "object/static/structure/corellia/corl_tent_med.iff", 9, 7, 200 },
				{ "object/static/structure/general/campfire_burnt.iff", 0, 0, 0 },
				{ "object/static/structure/general/poi_all_construction_metal_pile.iff", 14, -10, 40 },
				{ "object/static/structure/general/atst_debris_01.iff", -22, -18, 110 },
				{ "object/static/structure/military/bunker_crate_style_01.iff", 4, -8, 10 },
				{ "object/static/structure/military/bunker_crate_style_01.iff", 6, -9, 80 },
			},
			people = {
				{ "ossus_scavenger_boss", 0, 4, nil, 900 },
				{ "scavenger", -6, -4, "a scavenger", 300 },
				{ "scavenger", 7, -3, "a scavenger", 300 },
				{ "scavenger", -12, 2, "a scavenger", 300 },
				{ "scavenger", 12, 12, "a scavenger", 300 },
			} },
		{ name = "the poachers' camp", x = 2944, y = -1408,
			props = {
				{ "object/static/structure/corellia/corl_tent_med.iff", -7, 8, 180 },
				{ "object/static/structure/dantooine/dant_hide_tanning_s01.iff", 8, 6, 220 },
				{ "object/static/structure/dantooine/dant_rack_spears.iff", 10, -4, 270 },
				{ "object/static/structure/dantooine/dant_fire_pit.iff", 0, 0, 0 },
				{ "object/static/structure/dantooine/dant_skull_thune.iff", -10, -6, 30 },
			},
			people = {
				{ "ossus_poacher_chief", 2, 4, nil, 900 },
				{ "poacher", -5, -3, "a poacher", 300 },
				{ "poacher", 6, -5, "a poacher", 300 },
				{ "poacher", -9, 5, "a poacher", 300 },
			} },
		{ name = "the smugglers' drop", x = 4480, y = -1152,
			props = {
				{ "object/static/structure/corellia/corl_tent_hut_s01.iff", -8, 6, 170 },
				{ "object/static/item/item_crate_spice.iff", 4, 2, 0 },
				{ "object/static/item/item_crate_spice.iff", 5, 3, 40 },
				{ "object/static/item/item_crate_spice.iff", 3, 4, 80 },
				{ "object/static/structure/general/palette_supply_02.iff", 8, -4, 90 },
				{ "object/static/structure/general/campfire_burnt.iff", -2, -2, 0 },
			},
			people = {
				{ "ossus_smuggler_captain", 0, 3, nil, 900 },
				{ "thief", -5, -4, "a smuggler", 300 },
				{ "thief", 6, -2, "a smuggler", 300 },
				{ "thief", 9, 6, "a smuggler", 300 },
			} },
		{ name = "the deserters' camp", x = -640, y = -384,
			props = {
				{ "object/static/structure/corellia/corl_tent_med.iff", 0, 8, 180 },
				{ "object/static/structure/general/campfire_burnt.iff", 0, 0, 0 },
				{ "object/static/structure/military/bunker_crate_style_01.iff", 6, 4, 30 },
				{ "object/static/structure/general/banner_imperial_style_01.iff", -8, 6, 160 },
			},
			people = {
				{ "ossus_deserter", 2, 2 },
				{ "mercenary", -4, -3, "a deserter", 300 },
				{ "mercenary", 5, -4, "a deserter", 300 },
			} },
		{ name = "the pilgrims' rest", x = 520, y = -1480,
			props = {
				{ "object/static/structure/dantooine/dant_fire_pit.iff", 0, 0, 0 },
				{ "object/static/structure/dantooine/dant_cooking_stone.iff", 3, 2, 20 },
				{ "object/static/item/item_basket_closed.iff", -3, 2, 0 },
			},
			people = {
				{ "commoner_naboo", -3, -2, "a resting pilgrim", 300 },
				{ "commoner", 3, -3, "a resting pilgrim", 300 },
				{ "commoner_old", 0, 4, "an old pilgrim", 300 },
			} },
		{ name = "the hermit's hollow", x = -1408, y = 2432,
			props = {
				{ "object/static/structure/dantooine/dant_small_mudhut.iff", 0, 9, 180 },
				{ "object/static/structure/dantooine/dant_fire_pit.iff", 0, 0, 0 },
				{ "object/static/structure/dantooine/dant_cooking_stone.iff", 3, 1, 50 },
				{ "object/static/structure/dantooine/dant_jedi_temple_pillar_sm.iff", -9, -6, 15 },
			},
			people = {
				{ "ossus_hollow_hermit", 1, 3 },
			} },
	},

	-- the dungeon: cell id, template, x, z (height), y in the cell, respawn. O11 (17 Oct): points re-read from each cell's
	-- floor mesh as tools/navmap.py reads it (the first reader skipped the vertex count and put them off the floor):
	-- centres of floor triangles with no wall edge, up to three per cell about 6 m apart
	dungeon = {
		{ 6900003, "ossus_sith_acolyte", 2.99, -10.32, -0.54, 600 },
		{ 6900003, "ossus_sith_acolyte", -2.72, -9.31, 1.23, 600 },
		{ 6900004, "ossus_sith_acolyte", -3.33, -29.09, -30.26, 600 },
		{ 6900004, "ossus_sith_acolyte", -1.56, -27.93, -24.67, 600 },
		{ 6900005, "ossus_sith_acolyte", 6.94, -40.64, -68.30, 600 },
		{ 6900005, "ossus_sith_enforcer", 1.46, -40.72, -70.78, 600 },
		{ 6900006, "ossus_sith_acolyte", 43.46, -47.93, -78.31, 600 },
		{ 6900006, "ossus_sith_enforcer", 37.75, -45.65, -76.60, 600 },
		{ 6900007, "ossus_sith_enforcer", 38.07, -54.02, -147.21, 600 },
		{ 6900007, "ossus_sith_acolyte", 40.56, -51.89, -141.74, 600 },
		{ 6900008, "ossus_sith_enforcer", -11.06, -63.98, -183.56, 600 },
		{ 6900008, "ossus_sith_acolyte", -9.47, -64.28, -177.79, 600 },
		{ 6900009, "ossus_sith_enforcer", -13.15, -65.30, -232.24, 600 },
		{ 6900009, "ossus_sith_enforcer", -9.27, -63.80, -227.59, 600 },
		{ 6900010, "ossus_sith_enforcer", -88.27, -99.75, -152.51, 600 },
		{ 6900010, "ossus_sith_acolyte", -91.32, -101.39, -147.43, 600 },
		{ 6900011, "ossus_sith_enforcer", -44.64, -69.67, -96.53, 600 },
		{ 6900011, "ossus_sith_acolyte", -39.55, -70.09, -99.80, 600 },
		{ 6900012, "ossus_sith_enforcer", -35.94, -80.60, -141.98, 600 },
		{ 6900012, "ossus_sith_enforcer", -40.78, -82.11, -138.36, 600 },
		{ 6900013, "ossus_sith_enforcer", -91.28, -101.10, -107.70, 600 },
		{ 6900013, "ossus_sith_enforcer", -86.93, -101.67, -111.70, 600 },
		{ 6900013, "ossus_sith_keeper", -92.49, -101.36, -112.98, 1800 },
	},
}

registerScreenPlay("OssusWorld", true)

local SP = "OssusWorld"

function OssusWorld:start()
	if not isZoneEnabled(self.planet) then
		return
	end

	for _, p in ipairs(self.townsfolk) do
		self:spawnAt(p[1], p[2], p[3], p[4], p[5], p[6], 0, true)
	end

	for _, place in ipairs(self.places) do
		self:spawnPlace(place)
	end

	self:spawnPatrol()

	for _, d in ipairs(self.dungeon) do
		local pMobile = spawnMobile(self.planet, d[2], d[6], d[3], d[4], d[5], getRandomNumber(0, 359), d[1])

		if pMobile == nil then
			printLuaError("OssusWorld: could not spawn " .. d[2] .. " in cell " .. d[1])
		end
	end
end

function OssusWorld:spawnAt(template, x, y, heading, name, respawn, cell, stationary)
	local pMobile = spawnMobile(self.planet, template, respawn or 0, x, getWorldFloor(x, y, self.planet), y, heading, cell or 0)

	if pMobile == nil then
		printLuaError("OssusWorld: could not spawn " .. template .. " at " .. x .. ", " .. y)
		return nil
	end

	if name ~= nil then
		CreatureObject(pMobile):setCustomObjectName(name)
	end

	if stationary then
		AiAgent(pMobile):addObjectFlag(AI_STATIONARY)
	end

	return pMobile
end

function OssusWorld:spawnPlace(place)
	for _, prop in ipairs(place.props) do
		local x, y = place.x + prop[2], place.y + prop[3]
		spawnSceneObject(self.planet, prop[1], x, getWorldFloor(x, y, self.planet), y, 0, math.rad(prop[4]))
	end

	for _, p in ipairs(place.people) do
		self:spawnAt(p[1], place.x + p[2], place.y + p[3], getRandomNumber(0, 359), p[4], p[5], 0, true)
	end
end

-- The patrol: each trooper keeps its own place in the loop

function OssusWorld:spawnPatrol()
	for i = 1, #self.patrol.templates do
		self:spawnPatroller(nil, tostring(i))
	end
end

-- No engine respawn for the patrol: a killed trooper comes back after five minutes with its patrol set up again.
function OssusWorld:spawnPatroller(pNil, args)
	local i = tonumber(args)
	local start = self.patrol.points[1]
	local pMobile = self:spawnAt(self.patrol.templates[i], start[1] + i * 2, start[2], 30, nil, 0, 0, false)

	if pMobile == nil then
		return
	end

	local id = SceneObject(pMobile):getObjectID()
	writeData(id .. ":ossusPatrolPoint", 1)
	writeData(id .. ":ossusPatrolSlot", i)
	createObserver(DESTINATIONREACHED, SP, "onPatrolReached", pMobile)
	createObserver(OBJECTDESTRUCTION, SP, "onPatrollerKilled", pMobile)
	AiAgent(pMobile):setMovementState(AI_PATROLLING)
	createEvent(getRandomNumber(10, 20) * 1000, SP, "patrolNext", pMobile, "")
end

function OssusWorld:onPatrollerKilled(pMobile, pKiller)
	if pMobile ~= nil then
		local id = SceneObject(pMobile):getObjectID()
		createEvent(5 * 60 * 1000, SP, "spawnPatroller", nil, tostring(readData(id .. ":ossusPatrolSlot")))
		deleteData(id .. ":ossusPatrolPoint")
		deleteData(id .. ":ossusPatrolSlot")
	end

	return 1
end

function OssusWorld:patrolNext(pMobile)
	if pMobile == nil or CreatureObject(pMobile):isDead() or AiAgent(pMobile):isInCombat() then
		return
	end

	local id = SceneObject(pMobile):getObjectID()
	local n = readData(id .. ":ossusPatrolPoint") % #self.patrol.points + 1
	writeData(id .. ":ossusPatrolPoint", n)
	local p = self.patrol.points[n]

	AiAgent(pMobile):stopWaiting()
	AiAgent(pMobile):setNextPosition(p[1], getWorldFloor(p[1], p[2], self.planet), p[2], 0)
	AiAgent(pMobile):executeBehavior()
end

function OssusWorld:onPatrolReached(pMobile)
	if pMobile == nil or CreatureObject(pMobile):isDead() then
		return 1
	end

	createEvent(self.patrol.pause * 1000, SP, "patrolNext", pMobile, "")
	return 0
end

OssusWorldConvoHandler = conv_handler:new {}
