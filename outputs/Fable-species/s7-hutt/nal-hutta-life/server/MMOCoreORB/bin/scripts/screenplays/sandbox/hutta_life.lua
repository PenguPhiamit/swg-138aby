-- Nal Hutta life (PL-06; outputs/Fable-species/s7-hutt/nal-hutta-life.md). The owner, 17 Oct after run 25: "nal hutta
-- works, better than expected. but also feels empty". This adds, on top of PL-04's people (hutta_home.lua):
--  * townsfolk: commoners and NPCs walking five street routes and standing about (the stock CityScreenPlay patrol and
--    stationary code, as in Mos Espa), a kajidic watch on three of the routes, five townsfolk who talk, two Hutt nobles
--    with their retinues, and dancers and drinkers in the cantina;
--  * five places out in the swamp: a smugglers' camp, a burned freighter, a spice den, old ruins and a rival kajidic's
--    camp, each with stock POI art and hostile NPCs;
--  * the Kessoth job, a four-step quest from the majordomo at the Kessoth door: the smugglers' camp (kill their chief),
--    the wreck (find the manifest), the spice den (kill the spice baron), back to the majordomo for the reward.
-- Positions are generated (hutta_life_places.lua). Stock templates and art; names and text are our own. Non-persistent
-- spawns, made again at every server start.

HuttaLifeScreenPlay = CityScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HuttaLifeScreenPlay",

	planet = "hutta",

	patrolNpcs = {"commoner_tatooine_patrol", "commoner_old_patrol", "commoner_fat_patrol", "commoner_technician_patrol", "explorer_patrol", "gambler_patrol"},
	patrolPoints = HuttaLifePlaces.patrolPoints,
	patrolMobiles = HuttaLifePlaces.patrolMobiles,

	stationaryCommoners = {"commoner_tatooine", "commoner_old", "commoner_fat", "commoner_technician", "patron_nikto", "twilek_slave"},
	stationaryNpcs = {"businessman", "criminal", "gambler", "info_broker", "mercenary", "pilot", "scavenger", "bounty_hunter", "noble", "smuggler_cargo_handler"},
	stationaryMobiles = HuttaLifePlaces.stationaryMobiles,

	-- the cantina (Darklight's snapshot node 390000018, a stock cantina_tatooine): cell 3 is the main hall, the same
	-- cell and positions as the Mos Eisley cantina's (screenplays/cities/tatooine_mos_eisley.lua)
	cantinaId = 390000018,
	cantinaCell = 3,
	cantinaMobiles = {
		-- template, x, z, y, heading, mood
		{"hutta_cantina_dancer", 9.4, 0, 3.9, 310, "themepark_oola"},
		{"hutta_cantina_dancer", 7.2, 0, 2.6, 130, "themepark_oola"},
		{"patron_nikto", 8.8, -0.9, -6, 208, "entertained"},
		{"commoner_tatooine", 6.8, -0.9, -6.5, 230, "entertained"},
		{"patron_nikto", 14.2, -0.9, -4.8, 67, "npc_sitting_chair"},
		{"commoner_old", 16.5, -0.9, -4.8, 320, "npc_sitting_chair"},
		{"commoner_fat", 2.11, -0.894992, 5.4, 180, "npc_standing_drinking"},
		{"twilek_slave", 4.11, -0.894992, 5.4, 158, "npc_standing_drinking"},
		{"commoner_tatooine", 1.99, -0.894992, -8.44, 325, "conversation"},
		{"patron_nikto", 1.19, -0.894992, -7.63, 152, "conversation"},
	},

	-- the swamp: template, respawn (s), point index in the site's dry points (1 = centre), heading, custom name
	siteMobiles = {
		swamp_rat_camp = {
			{"smuggler", 300, 3, 0, "a camp smuggler"}, {"smuggler", 300, 5, 90, "a camp smuggler"},
			{"smuggler", 300, 7, 180, "a camp smuggler"}, {"weequay_captain", 300, 9, 270, "a camp enforcer"},
			{"smuggler_guard", 300, 11, 45, ""}, {"smuggler_guard", 300, 13, 225, ""},
		},
		freighter_wreck = {
			{"spice_collective_sentry", 300, 4, 0, "a wreck looter"}, {"spice_collective_sentry", 300, 8, 120, "a wreck looter"},
			{"spice_collective_foreman", 300, 12, 240, "the looters' boss"},
		},
		spice_den = {
			{"aakuan_spice_guard", 300, 3, 0, "a spice den guard"}, {"aakuan_spice_guard", 300, 6, 180, "a spice den guard"},
			{"spice_collective_heavy_guard", 300, 8, 90, "a spice den bruiser"}, {"spice_collective_heavy_guard", 300, 10, 270, "a spice den bruiser"},
			{"spice_collective_heavy_guard", 300, 12, 45, "a spice den bruiser"}, {"spice_fiend", 300, 13, 200, "a spice addict"},
			{"spice_fiend", 300, 14, 20, "a spice addict"},
		},
		old_ruins = {
			{"hutt_expeditonary_force_member", 300, 3, 0, "a kajidic digger"}, {"hutt_expeditonary_force_member", 300, 6, 120, "a kajidic digger"},
			{"hutt_expeditonary_force_member", 300, 9, 240, "a kajidic digger"}, {"hutt_expeditonary_force_leader", 300, 1, 180, "the dig master"},
		},
		hit_squad_camp = {
			{"igbi_hutt_operative", 300, 3, 0, "a Bessolo enforcer"}, {"igbi_hutt_operative", 300, 5, 90, "a Bessolo enforcer"},
			{"nurla_hutt_gangster", 300, 8, 180, "a Bessolo gunman"}, {"nurla_hutt_gangster", 300, 11, 270, "a Bessolo gunman"},
			{"weequay_captain", 300, 1, 0, "a Bessolo hit squad leader"},
		},
	},
	-- props that are not a POI building: template, point index, heading
	siteProps = {
		freighter_wreck = {
			{"object/tangible/destructible/wreckage/wreck_starship_small_01.iff", 1, 35},
			{"object/static/space/debris/cargo_destroyed_small_a.iff", 6, 110},
		},
	},
	-- the job's named foes: key = {site, template, point, heading, respawn seconds, quest step they end}
	named = {
		camp_boss = {"swamp_rat_camp", "hutta_camp_boss", 1, 180, 600, 1},
		spice_baron = {"spice_den", "hutta_spice_baron", 1, 90, 900, 3},
	},
}

registerScreenPlay("HuttaLifeScreenPlay", true)

function HuttaLifeScreenPlay:start()
	if not isZoneEnabled(self.planet) then
		return
	end

	self:spawnPatrolMobiles()
	self:spawnStationaryMobiles()
	self:spawnTalkers()
	self:spawnRetinues()
	self:spawnCantina()
	self:spawnQuestGiver()
	self:spawnSites()
end

function HuttaLifeScreenPlay:talker(template, x, y, heading, mood)
	local pMobile = spawnMobile(self.planet, template, 0, x, getWorldFloor(x, y, self.planet), y, heading, 0)

	if pMobile == nil then
		printLuaError("HuttaLifeScreenPlay: could not spawn " .. template .. " at " .. x .. ", " .. y)
		return nil
	end

	if mood ~= nil and mood ~= "" then
		self:setMoodString(pMobile, mood)
	end

	if AiAgent(pMobile) ~= nil then
		AiAgent(pMobile):addObjectFlag(AI_STATIONARY)
	end

	return pMobile
end

function HuttaLifeScreenPlay:spawnTalkers()
	for _, t in ipairs(HuttaLifePlaces.talkers) do
		self:talker(t[1], t[2], t[3], t[4], t[5])
	end
end

-- a Hutt noble facing south, two Gamorrean guards behind their shoulders, a Twi'lek attendant in front
function HuttaLifeScreenPlay:spawnRetinues()
	for _, r in ipairs(HuttaLifePlaces.retinues) do
		local x, y, h = r[2], r[3], r[4]
		self:talker(r[1], x, y, h, "calm")

		local pGuard = self:talker("gamorrean_guard", x - 3, y + 1.5, h, "")
		if pGuard ~= nil then CreatureObject(pGuard):setCustomObjectName("a retinue guard") end
		pGuard = self:talker("gamorrean_guard", x + 3, y + 1.5, h, "")
		if pGuard ~= nil then CreatureObject(pGuard):setCustomObjectName("a retinue guard") end

		local pAttendant = self:talker("twilek_slave", x + 1.5, y - 2.5, h + 180, "conversation")
		if pAttendant ~= nil then CreatureObject(pAttendant):setCustomObjectName("a Hutt's attendant") end
	end
end

function HuttaLifeScreenPlay:spawnCantina()
	local pCantina = getSceneObject(self.cantinaId)

	if pCantina == nil or not SceneObject(pCantina):isBuildingObject() then
		printLuaError("HuttaLifeScreenPlay: the Bilbousa cantina " .. self.cantinaId .. " is not loaded")
		return
	end

	local pCell = BuildingObject(pCantina):getCell(self.cantinaCell)

	if pCell == nil then
		printLuaError("HuttaLifeScreenPlay: the cantina has no cell " .. self.cantinaCell)
		return
	end

	local cellID = SceneObject(pCell):getObjectID()

	for _, m in ipairs(self.cantinaMobiles) do
		local pMobile = spawnMobile(self.planet, m[1], 300, m[2], m[3], m[4], m[5], cellID)

		if pMobile ~= nil then
			self:setMoodString(pMobile, m[6])
			CreatureObject(pMobile):setPvpStatusBitmask(0)
		end
	end
end

function HuttaLifeScreenPlay:spawnQuestGiver()
	local g = HuttaLifePlaces.questGiver
	self:talker(g[1], g[2], g[3], g[4], "calm")
end

-- The swamp sites

function HuttaLifeScreenPlay:sitePoint(key, index)
	local s = HuttaLifePlaces.sites[key]
	local p = s.points[index] or s.points[1]

	return s.x + p[1], p[3], s.y + p[2]
end

function HuttaLifeScreenPlay:spawnSites()
	for key, s in pairs(HuttaLifePlaces.sites) do
		if s.building ~= "" then
			if spawnSceneObject(self.planet, s.building, s.x, s.z, s.y, 0, 0) == nil then
				printLuaError("HuttaLifeScreenPlay: could not place " .. s.building)
			end
		end

		for _, p in ipairs(self.siteProps[key] or {}) do
			local x, z, y = self:sitePoint(key, p[2])

			if spawnSceneObject(self.planet, p[1], x, z, y, 0, math.rad(p[3])) == nil then
				printLuaError("HuttaLifeScreenPlay: could not place " .. p[1])
			end
		end

		for _, m in ipairs(self.siteMobiles[key] or {}) do
			local x, z, y = self:sitePoint(key, m[3])
			local pMobile = spawnMobile(self.planet, m[1], m[2], x, z, y, m[4], 0)

			if pMobile == nil then
				printLuaError("HuttaLifeScreenPlay: could not spawn " .. m[1] .. " at " .. key)
			elseif m[5] ~= "" then
				CreatureObject(pMobile):setCustomObjectName(m[5])
			end
		end
	end

	for key, _ in pairs(self.named) do
		self:spawnNamed(key)
	end

	-- the wreck step: entering the wreck finds the manifest
	local wx, wz, wy = self:sitePoint("freighter_wreck", 1)
	local pArea = spawnActiveArea(self.planet, "object/active_area.iff", wx, wz, wy, 25, 0)

	if pArea ~= nil then
		createObserver(ENTEREDAREA, "HuttaLifeScreenPlay", "notifyEnteredWreck", pArea)
	end
end

-- Named foes respawn through this screenplay (not the spawner) so the kill observer comes back with them.
function HuttaLifeScreenPlay:spawnNamed(key)
	local n = self.named[key]

	if n == nil then
		return
	end

	local x, z, y = self:sitePoint(n[1], n[3])
	local pMobile = spawnMobile(self.planet, n[2], 0, x, z, y, n[4], 0)

	if pMobile == nil then
		printLuaError("HuttaLifeScreenPlay: could not spawn the named " .. n[2])
		return
	end

	writeStringData(SceneObject(pMobile):getObjectID() .. ":hutta_life_named", key)
	createObserver(OBJECTDESTRUCTION, "HuttaLifeScreenPlay", "notifyNamedKilled", pMobile)
end

function HuttaLifeScreenPlay:respawnNamed(pNil, key)
	self:spawnNamed(key)
end

function HuttaLifeScreenPlay:notifyNamedKilled(pVictim, pAttacker)
	if pVictim == nil then
		return 1
	end

	local oid = SceneObject(pVictim):getObjectID()
	local key = readStringData(oid .. ":hutta_life_named")
	deleteStringData(oid .. ":hutta_life_named")

	local n = self.named[key]

	if n == nil then
		return 1
	end

	HuttaKessothJob:creditKill(pVictim, pAttacker, n[6])
	createEvent(n[5] * 1000, "HuttaLifeScreenPlay", "respawnNamed", nil, key)

	return 1
end

function HuttaLifeScreenPlay:notifyEnteredWreck(pArea, pCreature)
	if pCreature == nil or not SceneObject(pCreature):isPlayerCreature() then
		return 0
	end

	HuttaKessothJob:advance(pCreature, 2)

	return 0
end

-- The Kessoth job: step 0 none, 1 the smugglers' camp, 2 the wreck, 3 the spice den, 4 back to the majordomo, 5 done.

HuttaKessothJob = {
	name = "HuttaKessothJob",
	rewardCredits = 6000,
	rewardItem = "object/tangible/wearables/vest/vest_hutt_gang_s01.iff",
	-- step -> site whose centre the waypoint marks, and the waypoint's name
	waypoints = {
		{"swamp_rat_camp", "Kessoth job: the smugglers' camp"},
		{"freighter_wreck", "Kessoth job: the burned freighter"},
		{"spice_den", "Kessoth job: Kreeg's spice den"},
	},
	messages = {
		[2] = "Vekk Tano is dead. Among his papers: the smugglers never had the Kessoth spice. Search the wreck itself.",
		[3] = "Under the burned crates you find the freighter's manifest. The spice was offloaded before the crash, to a Nikto called Kreeg, in the north-west swamp.",
		[4] = "Kreeg is dead, and the Kessoth spice is stacked in his den. Return to Bezzik at the Kessoth door in Bilbousa.",
	},
}

function HuttaKessothJob:getStep(pPlayer)
	return tonumber(readScreenPlayData(pPlayer, self.name, "step")) or 0
end

function HuttaKessothJob:setStep(pPlayer, step)
	writeScreenPlayData(pPlayer, self.name, "step", tostring(step))
end

-- One job waypoint at a time, of the stock quest-task type (as screenplays/quest_tasks/go_to_theater.lua does):
-- addWaypoint returns no id, so the old one is removed by its type.
function HuttaKessothJob:setWaypoint(pPlayer, step)
	local pGhost = CreatureObject(pPlayer):getPlayerObject()

	if pGhost == nil then
		return
	end

	PlayerObject(pGhost):removeWaypointBySpecialType(WAYPOINTQUESTTASK)

	if step >= 1 and step <= 3 then
		local s = HuttaLifePlaces.sites[self.waypoints[step][1]]
		PlayerObject(pGhost):addWaypoint("hutta", self.waypoints[step][2], "", s.x, s.z, s.y, WAYPOINT_YELLOW, true, true, WAYPOINTQUESTTASK)
	elseif step == 4 then
		local g = HuttaLifePlaces.questGiver
		PlayerObject(pGhost):addWaypoint("hutta", "Kessoth job: Bezzik in Bilbousa", "", g[2], 80, g[3], WAYPOINT_YELLOW, true, true, WAYPOINTQUESTTASK)
	end
end

-- Move a player from step (from) to the next one, with its message and waypoint.
function HuttaKessothJob:advance(pPlayer, from)
	if self:getStep(pPlayer) ~= from then
		return
	end

	self:setStep(pPlayer, from + 1)
	CreatureObject(pPlayer):sendSystemMessage(self.messages[from + 1])
	self:setWaypoint(pPlayer, from + 1)
end

-- The killer and their group members within 128 m of the body who are on that step all get credit.
function HuttaKessothJob:creditKill(pVictim, pAttacker, step)
	if pAttacker == nil or not SceneObject(pAttacker):isPlayerCreature() then
		return
	end

	local players = {pAttacker}

	if CreatureObject(pAttacker):isGrouped() then
		players = {}

		for i = 0, CreatureObject(pAttacker):getGroupSize() - 1 do
			local pMember = CreatureObject(pAttacker):getGroupMember(i)

			if pMember ~= nil and SceneObject(pMember):isPlayerCreature() and SceneObject(pMember):isInRangeWithObject(pVictim, 128) then
				table.insert(players, pMember)
			end
		end
	end

	for _, pPlayer in ipairs(players) do
		self:advance(pPlayer, step)
	end
end

function HuttaKessothJob:accept(pPlayer)
	if self:getStep(pPlayer) == 0 then
		self:setStep(pPlayer, 1)
		self:setWaypoint(pPlayer, 1)
	end
end

function HuttaKessothJob:reward(pPlayer)
	if self:getStep(pPlayer) ~= 4 then
		return
	end

	local pInventory = SceneObject(pPlayer):getSlottedObject("inventory")

	if pInventory == nil or SceneObject(pInventory):isContainerFullRecursive() then
		CreatureObject(pPlayer):sendSystemMessage("Your inventory is full. Make room, then speak to Bezzik again.")
		return false
	end

	giveItem(pInventory, self.rewardItem, -1)
	CreatureObject(pPlayer):addCashCredits(self.rewardCredits, true)
	self:setStep(pPlayer, 5)
	self:setWaypoint(pPlayer, 5)

	return true
end

-- Conversation handlers

HuttaTownsfolkConvoHandler = conv_handler:new {}

HuttaKessothMajordomoConvoHandler = conv_handler:new {}

function HuttaKessothMajordomoConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local convoTemplate = LuaConversationTemplate(pConvTemplate)
	local step = HuttaKessothJob:getStep(pPlayer)
	local screens = {[1] = "step1", [2] = "step2", [3] = "step3", [4] = "report", [5] = "done"}

	return convoTemplate:getScreen(screens[step] or "greet")
end

function HuttaKessothMajordomoConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local id = LuaConversationScreen(pConvScreen):getScreenID()

	if id == "accept" then
		HuttaKessothJob:accept(pPlayer)
	elseif id == "reward" then
		if HuttaKessothJob:reward(pPlayer) == false then
			return LuaConversationTemplate(pConvTemplate):getScreen("full")
		end
	end

	return pConvScreen
end
