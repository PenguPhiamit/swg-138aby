-- Ossus people (PL-02; outputs/Fable-ossus/o7-build/people/README.md).
--
-- Spawns the people of the O7 places (positions from poi-placements.json -> npc_points), runs three starter
-- missions and the rare hidden Jedi in the sanctuary:
--   the highland hunt   Elder Iravi (Ysanna camp) -> three kirruk by the stone circle -> back: 1,500 credits
--   the pilot's part    Lieutenant Moll (crashed fighter) -> foreman Teel (kathracite adit) -> back: 1,000 credits
--   the memorial road   first stone above Knossa -> middle stone -> memorial ring: badge 140; Archivist Oduro: 500 credits
--   the ghostfire       Archivist Oduro's lead -> three Jedi sites on Ossus + badge 140 + one stock Jedi temple badge ->
--                       T'ra Saa's keeper in the sanctuary: one question -> the ghostfire colour crystal, once per character
-- Progress is per player in screenplay data ("OssusPeople"), so it survives logouts and restarts. Our own code and text.

OssusPeople = ScreenPlay:new {
	planet = "ossus",

	badge = 140,               -- datatables/badge/badge_map.iff row added by the PL-02 client step
	huntReward = 1500,
	partReward = 1000,
	roadReward = 500,
	huntTargets = 3,
	huntTemplate = "ossus_kirruk",
	huntSpot = { x = -980, y = -5555 },   -- the shoulder just north of the stone circle (POI 6)
	huntSpread = 25,
	huntCleanup = 30 * 60,                -- seconds before an unfought hunt target is removed

	-- the hidden Jedi: present for jediStay seconds, then away for jediAwayMin..jediAwayMax
	jedi = { template = "ossus_hidden_jedi", x = -107.26, z = -83.19, y = -92.10, heading = 0, cell = 6900118 },
	jediFirst = { 10 * 60, 60 * 60 },
	jediStay = 60 * 60,
	jediAwayMin = 2 * 3600,
	jediAwayMax = 4 * 3600,

	-- template, x, y, heading, display name (nil: the template's), respawn seconds, step forward (m)
	people = {
		-- POI 3 Krayt's garrison and its dig (the towers' sentries stand 5 m in front of each tower door)
		{ "ossus_garrison_commander", 2171.2, 3041.0, 36 },
		{ "stormtrooper_rifleman", 2151.1, 3025.3, 216, nil, 300 },
		{ "stormtrooper_rifleman", 2137.4, 3035.3, 216, nil, 300 },
		{ "stormtrooper_rifleman", 2170.2, 3010.7, 216, nil, 300, 5 },
		{ "stormtrooper_rifleman", 2123.3, 3044.9, 216, nil, 300, 5 },
		{ "stormtrooper_squad_leader", 2144.7, 3025.0, 306, nil, 300 },
		{ "stormtrooper", 2160.1, 3049.6, 36, nil, 300 },
		{ "imperial_sergeant", 2160.5, 3038.2, 216, nil, 300 },
		{ "imperial_sergeant", 2130.6, 3005.6, 36, "a dig overseer", 300 },
		{ "commoner_technician", 2137.5, 2998.1, 216, "a dig worker", 300 },
		{ "commoner_technician", 2120.7, 3009.0, 306, "a dig worker", 300 },
		-- POI 4 the Great Library vault dig
		{ "ossus_vault_archivist", 2302.0, 1987.0, 180 },
		-- POI 5 the Ysanna hunting camp, POI 6 the stone circle
		{ "ossus_ysanna_shaman", -1326.0, -4932.0, 180 },
		{ "hermit", -1321.0, -4953.0, 0, "an Ysanna hunter", 300 },
		{ "hermit", -1330.0, -4944.0, 90, "an Ysanna hunter", 300 },
		{ "commoner_old", -976.0, -5610.0, 0, "an Ysanna singer", 300 },
		{ "commoner_old", -984.0, -5610.0, 180, "an Ysanna singer", 300 },
		-- POI 8 the Adega Lake hamlet
		{ "ossus_hamlet_fisher", -3047.0, 1104.0, 280 },
		{ "farmer", -3060.0, 1094.0, 100, "a fisher", 300 },
		-- POI 9 the kathracite adit
		{ "ossus_adit_foreman", 4590.0, -310.0, 138 },
		{ "miner", 4596.0, -304.0, 228, "a kathracite miner", 300 },
		-- POI 10 the canyon floor under the bridge
		{ "brigand", 4462.0, -536.0, 0, "a canyon raider", 600 },
		{ "brigand", 4476.0, -524.0, 120, "a canyon raider", 600 },
		{ "brigand", 4470.0, -540.0, 240, "a canyon raider", 600 },
		-- POI 11 Knossa old town (the recruiter stays by the shuttle pad)
		{ "imperial_recruiter", 22.0, -3618.0, 180 },
		{ "junk_dealer", 80.0, -3640.0, 90 },
		{ "artisan", -20.0, -3656.0, 0, nil, 300 },
		{ "commoner", -70.0, -3610.0, 90, nil, 300 },
		{ "commoner", -68.0, -3604.0, 200, nil, 300 },
		-- POI 14 the Sith interrogation post (cave apron)
		{ "imperial_sergeant", -2976.0, -4946.0, 0, "a post guard", 300 },
		-- POI 15 the crashed fighter
		{ "ossus_alliance_pilot", -1476.0, 5194.0, 270 },
		-- POI 18 the Hutt landing field
		{ "ossus_hutt_broker", 3400.0, -2260.0, 180 },
		{ "smuggler", 3388.0, -2267.0, 0, "a kathracite buyer", 300 },
	},

	-- the memorial road: step, x, y, radius, what the player reads
	road = {
		{ 1, 116.4, -3012.4, 15, "You stand at the first memorial stone above Knossa. The road climbs north toward the academy." },
		{ 2, 892.3, -31.2, 15, "The middle stone. Its face is worn smooth where pilgrims have touched it." },
		{ 3, 1960.0, 2780.0, 20, "You reach the memorial ring beside the craters, at the end of the pilgrims' road." },
	},

	-- the ghostfire quest (owner 17 Oct; outputs/Fable-ossus/o10-ghostfire/README.md). The sites count only after the lead.
	ghostfire = {
		sites = {
			{ key = "gfVault", x = 2300.0, y = 1925.0, radius = 20, text = "The mouth of the Great Library vault. Something old is still breathing in the stone." },
			{ key = "gfWatch", x = 290.0, y = -6400.0, radius = 25, text = "The Eocho watch ruin. From here the masters could see the whole valley." },
			{ key = "gfCircle", x = -980.0, y = -5610.0, radius = 25, text = "The Ysanna stone circle. The stones hum faintly when the wind drops." },
		},
		badge = 140,                -- the memorial road (PL-02)
		templeBadges = { 12, 23, 30 },  -- stock exploration_jedi: Ben Kenobi's old home, Exar Kun's temple, Dantooine's Jedi temple
		retry = 60 * 60,            -- seconds before a player who answered wrongly may answer again
		lootGroup = "ossus_ghostfire_crystal",
	},

	waypoints = {
		hunt = { -980, -5555, "Kirruk by the stone circle" },
		adit = { 4590, -310, "Kathracite adit (Teel)" },
		pilot = { -1476, 5194, "Lieutenant Moll's fighter" },
		roadStart = { 116, -3012, "Memorial road: first stone" },
		roadMiddle = { 892, -31, "Memorial road: middle stone" },
		roadRing = { 1960, 2780, "Memorial road: the ring" },
		gfVault = { 2300, 1925, "Old Jedi site: the vault mouth" },
		gfWatch = { 290, -6400, "Old Jedi site: the Eocho watch ruin" },
		gfCircle = { -980, -5610, "Old Jedi site: the Ysanna stone circle" },
	},
}

registerScreenPlay("OssusPeople", true)

local SP = "OssusPeople"

local function getState(pPlayer, key)
	return readScreenPlayData(pPlayer, SP, key)
end

local function setState(pPlayer, key, value)
	writeScreenPlayData(pPlayer, SP, key, value)
end

local function getNumber(pPlayer, key)
	return tonumber(getState(pPlayer, key)) or 0
end

function OssusPeople:start()
	if not isZoneEnabled(self.planet) then
		return
	end

	self:spawnPeople()
	self:spawnRoad()
	self:spawnGhostfireSites()

	local first = getRandomNumber(self.jediFirst[1], self.jediFirst[2])
	createEvent(first * 1000, SP, "jediAppear", nil, "")
end

function OssusPeople:spawnPeople()
	for _, p in ipairs(self.people) do
		local x, y = p[2], p[3]

		if p[7] ~= nil then
			local h = math.rad(p[4])
			x, y = x + math.sin(h) * p[7], y + math.cos(h) * p[7]
		end

		local pMobile = spawnMobile(self.planet, p[1], p[6] or 0, x, getWorldFloor(x, y, self.planet), y, p[4], 0)

		if pMobile == nil then
			printLuaError("OssusPeople: could not spawn " .. p[1] .. " at " .. x .. ", " .. y)
		else
			if p[5] ~= nil then
				CreatureObject(pMobile):setCustomObjectName(p[5])
			end
			AiAgent(pMobile):addObjectFlag(AI_STATIONARY)
		end
	end
end

-- Waypoints

function OssusPeople:addWaypoint(pPlayer, key)
	local pGhost = CreatureObject(pPlayer):getPlayerObject()
	local w = self.waypoints[key]

	if pGhost ~= nil and w ~= nil then
		PlayerObject(pGhost):addWaypoint(self.planet, w[3], "", w[1], 0, w[2], WAYPOINT_BLUE, true, true, 0, 0)
	end
end

-- The highland hunt

function OssusPeople:startHunt(pPlayer)
	setState(pPlayer, "hunt", "active")
	setState(pPlayer, "huntKills", 0)
	self:spawnHuntTargets(pPlayer)
	self:addWaypoint(pPlayer, "hunt")
end

function OssusPeople:liveHuntTargets(pPlayer)
	local playerID = SceneObject(pPlayer):getObjectID()
	local live = 0

	for i = 1, self.huntTargets do
		local pTarget = getSceneObject(readData(playerID .. ":ossusHunt:target" .. i))

		if pTarget ~= nil and not CreatureObject(pTarget):isDead() and readData(SceneObject(pTarget):getObjectID() .. ":ossusHuntOwner") == playerID then
			live = live + 1
		end
	end

	return live
end

-- Spawns as many targets as the player still needs, minus those already alive.
function OssusPeople:spawnHuntTargets(pPlayer)
	local playerID = SceneObject(pPlayer):getObjectID()
	local needed = self.huntTargets - getNumber(pPlayer, "huntKills") - self:liveHuntTargets(pPlayer)
	local slot = 1

	while needed > 0 and slot <= self.huntTargets do
		local pOld = getSceneObject(readData(playerID .. ":ossusHunt:target" .. slot))

		if pOld == nil or CreatureObject(pOld):isDead() or readData(SceneObject(pOld):getObjectID() .. ":ossusHuntOwner") ~= playerID then
			local x = self.huntSpot.x + getRandomNumber(-self.huntSpread, self.huntSpread)
			local y = self.huntSpot.y + getRandomNumber(-self.huntSpread, self.huntSpread)
			local pTarget = spawnMobile(self.planet, self.huntTemplate, 0, x, getWorldFloor(x, y, self.planet), y, getRandomNumber(0, 359), 0)

			if pTarget ~= nil then
				local targetID = SceneObject(pTarget):getObjectID()
				writeData(playerID .. ":ossusHunt:target" .. slot, targetID)
				writeData(targetID .. ":ossusHuntOwner", playerID)
				createObserver(OBJECTDESTRUCTION, SP, "onHuntTargetKilled", pTarget)
				createEvent(self.huntCleanup * 1000, SP, "huntCleanup", nil, tostring(targetID))
				needed = needed - 1
			end
		end

		slot = slot + 1
	end
end

function OssusPeople:onHuntTargetKilled(pTarget, pKiller)
	if pTarget == nil then
		return 1
	end

	local targetID = SceneObject(pTarget):getObjectID()
	local ownerID = readData(targetID .. ":ossusHuntOwner")
	deleteData(targetID .. ":ossusHuntOwner")
	local pOwner = getSceneObject(ownerID)

	if pOwner == nil or not SceneObject(pOwner):isPlayerCreature() or getState(pOwner, "hunt") ~= "active" then
		return 1
	end

	local kills = getNumber(pOwner, "huntKills") + 1
	setState(pOwner, "huntKills", kills)

	if kills >= self.huntTargets then
		setState(pOwner, "hunt", "killed")
		CreatureObject(pOwner):sendSystemMessage("The kirruk by the stone circle are dead. Return to Elder Iravi at the Ysanna camp.")
	else
		CreatureObject(pOwner):sendSystemMessage("Kirruk killed: " .. kills .. " of " .. self.huntTargets .. ".")
	end

	return 1
end

function OssusPeople:huntCleanup(pNil, args)
	local targetID = tonumber(args)
	local pTarget = getSceneObject(targetID)

	if pTarget == nil or CreatureObject(pTarget):isDead() or readData(targetID .. ":ossusHuntOwner") == 0 then
		return
	end

	if CreatureObject(pTarget):isInCombat() then
		createEvent(5 * 60 * 1000, SP, "huntCleanup", nil, args)
		return
	end

	dropObserver(OBJECTDESTRUCTION, SP, "onHuntTargetKilled", pTarget)
	deleteData(targetID .. ":ossusHuntOwner")
	SceneObject(pTarget):destroyObjectFromWorld()
end

-- The memorial road

function OssusPeople:spawnRoad()
	for _, r in ipairs(self.road) do
		local pArea = spawnActiveArea(self.planet, "object/active_area.iff", r[2], getWorldFloor(r[2], r[3], self.planet), r[3], r[4], 0)

		if pArea == nil then
			printLuaError("OssusPeople: could not create the memorial road area " .. r[1])
		else
			writeData(SceneObject(pArea):getObjectID() .. ":ossusRoadStep", r[1])
			createObserver(ENTEREDAREA, SP, "onRoadArea", pArea)
		end
	end
end

function OssusPeople:onRoadArea(pArea, pPlayer)
	if pArea == nil then
		return 1
	end

	if pPlayer == nil or not SceneObject(pPlayer):isPlayerCreature() then
		return 0
	end

	local step = readData(SceneObject(pArea):getObjectID() .. ":ossusRoadStep")
	local done = getNumber(pPlayer, "roadStep")

	if step ~= done + 1 then
		return 0
	end

	setState(pPlayer, "roadStep", step)
	CreatureObject(pPlayer):sendSystemMessage(self.road[step][5])

	if step == #self.road then
		local pGhost = CreatureObject(pPlayer):getPlayerObject()

		if pGhost ~= nil and not PlayerObject(pGhost):hasBadge(self.badge) then
			PlayerObject(pGhost):awardBadge(self.badge)
		end
	end

	return 0
end

-- The ghostfire quest

function OssusPeople:spawnGhostfireSites()
	for i, site in ipairs(self.ghostfire.sites) do
		local pArea = spawnActiveArea(self.planet, "object/active_area.iff", site.x, getWorldFloor(site.x, site.y, self.planet), site.y, site.radius, 0)

		if pArea == nil then
			printLuaError("OssusPeople: could not create the ghostfire site " .. site.key)
		else
			writeData(SceneObject(pArea):getObjectID() .. ":ossusGhostfireSite", i)
			createObserver(ENTEREDAREA, SP, "onGhostfireSite", pArea)
		end
	end
end

function OssusPeople:onGhostfireSite(pArea, pPlayer)
	if pArea == nil then
		return 1
	end

	if pPlayer == nil or not SceneObject(pPlayer):isPlayerCreature() or getState(pPlayer, "ghostfire") ~= "lead" then
		return 0
	end

	local site = self.ghostfire.sites[readData(SceneObject(pArea):getObjectID() .. ":ossusGhostfireSite")]

	if site ~= nil and getState(pPlayer, site.key) ~= "1" then
		setState(pPlayer, site.key, "1")
		CreatureObject(pPlayer):sendSystemMessage(site.text)
		CreatureObject(pPlayer):sendSystemMessage("Old Jedi sites walked: " .. self:ghostfireSitesDone(pPlayer) .. " of " .. #self.ghostfire.sites .. ".")
	end

	return 0
end

function OssusPeople:ghostfireSitesDone(pPlayer)
	local n = 0

	for _, site in ipairs(self.ghostfire.sites) do
		if getState(pPlayer, site.key) == "1" then
			n = n + 1
		end
	end

	return n
end

-- What the player still lacks, as the keeper says it; nil when ready.
function OssusPeople:ghostfireMissing(pPlayer)
	local g = self.ghostfire
	local pGhost = CreatureObject(pPlayer):getPlayerObject()

	if pGhost == nil then
		return "..."
	end

	if getState(pPlayer, "ghostfire") ~= "lead" then
		return "You do not know yet what you are looking for. The archivist at the vault dig remembers more than she says. Ask her about the Jedi light."
	end

	local missing = {}

	for _, site in ipairs(g.sites) do
		if getState(pPlayer, site.key) ~= "1" then
			table.insert(missing, (self.waypoints[site.key][3]:gsub("^Old Jedi site: ", "")))
		end
	end

	if not PlayerObject(pGhost):hasBadge(g.badge) then
		table.insert(missing, "the memorial road, walked from the first stone to the ring")
	end

	local temple = false

	for _, b in ipairs(g.templeBadges) do
		if PlayerObject(pGhost):hasBadge(b) then
			temple = true
		end
	end

	if not temple then
		table.insert(missing, "one of the old temples beyond Ossus: Dantooine's ruined temple, Exar Kun's temple on Yavin 4, or the old hermit's home on Tatooine")
	end

	if #missing == 0 then
		return nil
	end

	return "Not yet. The old paths are still quiet around you. You have not yet walked: " .. table.concat(missing, "; ") .. "."
end

function OssusPeople:giveGhostfire(pPlayer)
	local pInventory = CreatureObject(pPlayer):getSlottedObject("inventory")

	if pInventory == nil or SceneObject(pInventory):isContainerFullRecursive() then
		return false
	end

	createLoot(pInventory, self.ghostfire.lootGroup, 1, true)
	setState(pPlayer, "ghostfire", "done")
	CreatureObject(pPlayer):sendSystemMessage("You receive the ghostfire crystal.")
	return true
end

-- The rare hidden Jedi in the sanctuary

function OssusPeople:jediAppear(pNil, args)
	local j = self.jedi
	local pJedi = spawnMobile(self.planet, j.template, 0, j.x, j.z, j.y, j.heading, j.cell)

	if pJedi == nil then
		-- the cell exists only with the O7 snapshot (local_planets.tre); try again after the usual absence
		printLuaError("OssusPeople: could not place the hidden Jedi in cell " .. j.cell)
		createEvent(getRandomNumber(self.jediAwayMin, self.jediAwayMax) * 1000, SP, "jediAppear", nil, "")
		return
	end

	AiAgent(pJedi):addObjectFlag(AI_STATIONARY)
	writeData("OssusPeople:jedi", SceneObject(pJedi):getObjectID())
	createEvent(self.jediStay * 1000, SP, "jediLeave", nil, "")
end

function OssusPeople:jediLeave(pNil, args)
	local pJedi = getSceneObject(readData("OssusPeople:jedi"))

	if pJedi ~= nil then
		SceneObject(pJedi):destroyObjectFromWorld()
	end

	writeData("OssusPeople:jedi", 0)
	createEvent(getRandomNumber(self.jediAwayMin, self.jediAwayMax) * 1000, SP, "jediAppear", nil, "")
end

-- Conversations

local function screenOf(pConvTemplate, id)
	return LuaConversationTemplate(pConvTemplate):getScreen(id)
end

local function screenID(pConvScreen)
	return LuaConversationScreen(pConvScreen):getScreenID()
end

OssusYsannaShamanConvoHandler = conv_handler:new {}

function OssusYsannaShamanConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local hunt = getState(pPlayer, "hunt")

	if hunt == "active" then
		return screenOf(pConvTemplate, "hunt_active")
	elseif hunt == "killed" then
		return screenOf(pConvTemplate, "hunt_reward")
	elseif hunt == "done" then
		return screenOf(pConvTemplate, "greet_done")
	end

	return screenOf(pConvTemplate, "greet")
end

function OssusYsannaShamanConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local id = screenID(pConvScreen)

	if id == "hunt_accept" and getState(pPlayer, "hunt") == "" then
		OssusPeople:startHunt(pPlayer)
	elseif id == "hunt_retrack" and getState(pPlayer, "hunt") == "active" then
		OssusPeople:spawnHuntTargets(pPlayer)
		OssusPeople:addWaypoint(pPlayer, "hunt")
	elseif id == "hunt_reward" and getState(pPlayer, "hunt") == "killed" then
		setState(pPlayer, "hunt", "done")
		CreatureObject(pPlayer):addBankCredits(OssusPeople.huntReward, true)
	end

	return pConvScreen
end

OssusAlliancePilotConvoHandler = conv_handler:new {}

function OssusAlliancePilotConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local part = getState(pPlayer, "part")

	if part == "asked" then
		return screenOf(pConvTemplate, "part_waiting")
	elseif part == "carrying" then
		return screenOf(pConvTemplate, "part_reward")
	elseif part == "done" then
		return screenOf(pConvTemplate, "greet_done")
	end

	return screenOf(pConvTemplate, "greet")
end

function OssusAlliancePilotConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local id = screenID(pConvScreen)

	if id == "part_accept" and getState(pPlayer, "part") == "" then
		setState(pPlayer, "part", "asked")
		OssusPeople:addWaypoint(pPlayer, "adit")
	elseif id == "part_reward" and getState(pPlayer, "part") == "carrying" then
		setState(pPlayer, "part", "done")
		CreatureObject(pPlayer):addBankCredits(OssusPeople.partReward, true)
	end

	return pConvScreen
end

OssusAditForemanConvoHandler = conv_handler:new {}

function OssusAditForemanConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local part = getState(pPlayer, "part")

	if part == "asked" then
		return screenOf(pConvTemplate, "part_ask")
	elseif part == "carrying" then
		return screenOf(pConvTemplate, "part_carrying")
	end

	return screenOf(pConvTemplate, "greet")
end

function OssusAditForemanConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	if screenID(pConvScreen) == "part_given" and getState(pPlayer, "part") == "asked" then
		setState(pPlayer, "part", "carrying")
		OssusPeople:addWaypoint(pPlayer, "pilot")
		CreatureObject(pPlayer):sendSystemMessage("You take the power coupling for Lieutenant Moll.")
	end

	return pConvScreen
end

OssusVaultArchivistConvoHandler = conv_handler:new {}

function OssusVaultArchivistConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	if getState(pPlayer, "roadPaid") == "1" then
		return screenOf(pConvTemplate, "greet_done")
	elseif getNumber(pPlayer, "roadStep") >= #OssusPeople.road then
		return screenOf(pConvTemplate, "road_reward")
	end

	return screenOf(pConvTemplate, "greet")
end

function OssusVaultArchivistConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local id = screenID(pConvScreen)

	if id == "road_accept" then
		OssusPeople:addWaypoint(pPlayer, "roadStart")
		OssusPeople:addWaypoint(pPlayer, "roadMiddle")
		OssusPeople:addWaypoint(pPlayer, "roadRing")
	elseif id == "ghostfire_lead" and getState(pPlayer, "ghostfire") == "" then
		setState(pPlayer, "ghostfire", "lead")
		OssusPeople:addWaypoint(pPlayer, "gfVault")
		OssusPeople:addWaypoint(pPlayer, "gfWatch")
		OssusPeople:addWaypoint(pPlayer, "gfCircle")
	elseif id == "road_reward" and getState(pPlayer, "roadPaid") ~= "1" and getNumber(pPlayer, "roadStep") >= #OssusPeople.road then
		setState(pPlayer, "roadPaid", "1")
		CreatureObject(pPlayer):addBankCredits(OssusPeople.roadReward, true)
	end

	return pConvScreen
end

OssusHiddenJediConvoHandler = conv_handler:new {}

function OssusHiddenJediConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	if CreatureObject(pPlayer):isImperial() then
		return screenOf(pConvTemplate, "refuse")
	end

	local state = getState(pPlayer, "ghostfire")

	if state == "done" then
		return screenOf(pConvTemplate, "after")
	elseif state == "" then
		return screenOf(pConvTemplate, "greet")
	elseif OssusPeople:ghostfireMissing(pPlayer) ~= nil then
		return screenOf(pConvTemplate, "not_ready")
	elseif (tonumber(getState(pPlayer, "gfRetry")) or 0) > os.time() then
		return screenOf(pConvTemplate, "not_again_yet")
	end

	return screenOf(pConvTemplate, "ready")
end

function OssusHiddenJediConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local id = screenID(pConvScreen)

	if id == "promise" and getState(pPlayer, "metJedi") ~= "1" then
		-- owner, 16 Oct: talk only; the meeting is remembered
		setState(pPlayer, "metJedi", "1")
	elseif id == "not_ready" then
		local pClone = LuaConversationScreen(pConvScreen):cloneScreen()
		LuaConversationScreen(pClone):setCustomDialogText(OssusPeople:ghostfireMissing(pPlayer) or "...")
		return pClone
	elseif id == "pass" and getState(pPlayer, "ghostfire") == "lead" and OssusPeople:ghostfireMissing(pPlayer) == nil then
		if not OssusPeople:giveGhostfire(pPlayer) then
			return screenOf(pConvTemplate, "pass_full")
		end
	elseif id == "fail_force" or id == "fail_greed" then
		setState(pPlayer, "gfRetry", os.time() + OssusPeople.ghostfire.retry)
	end

	return pConvScreen
end

OssusGarrisonCommanderConvoHandler = conv_handler:new {}

function OssusGarrisonCommanderConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	if CreatureObject(pPlayer):isRebel() then
		return screenOf(pConvTemplate, "refuse")
	end

	return screenOf(pConvTemplate, "greet")
end

OssusHuttBrokerConvoHandler = conv_handler:new {}
OssusHamletFisherConvoHandler = conv_handler:new {}
