-- Sandbox world boss rotation.
--
-- Keeps a few named, tougher versions of existing creatures alive on their home planets.
-- A boss that nobody kills slips away after its lifetime and a different one appears
-- elsewhere; a slain boss pays every player who damaged it and is replaced after a delay.
-- A big game hunter at the Mos Eisley starport tells players where the current bosses are.
--
-- Design inspired by SWG Flurry's WorldBossSpawner (AGPL-3.0, github.com/Thrax989/SWGFlurry);
-- spawn reference points adapted from its world_boss_spt.lua. Rewritten for current Core3.

SandboxWorldBosses = ScreenPlay:new {
	activeBosses = 3,               -- bosses alive at the same time
	firstSpawnDelay = 120,          -- seconds after server start
	lifetime = 6 * 3600,            -- seconds before an unkilled boss slips away
	combatGrace = 10 * 60,          -- re-check delay when a boss is in combat at expiry
	respawnAfterKill = 90 * 60,     -- seconds before a slain boss's slot refills
	respawnAfterEscape = 2 * 60,    -- seconds before an escaped boss's slot refills
	spawnRadius = 400,              -- metres around a reference point
	reward = 25000,                 -- bank credits per player who damaged the boss

	-- template, display name, health multiplier, home planet
	roster = {
		{ template = "giant_canyon_krayt_dragon", name = "Ghost-Scale the Canyon Krayt", ham = 1.5, planet = "tatooine" },
		{ template = "krayt_dragon_ancient", name = "Old Rattlebones, Ancient Krayt", ham = 1.25, planet = "tatooine" },
		{ template = "gorax", name = "The Gorax Patriarch", ham = 1.5, planet = "endor" },
		{ template = "blurrg_raptor", name = "Razorback the Blurrg Raptor", ham = 4, planet = "endor" },
		{ template = "graul_marauder", name = "Gnasher the Graul Marauder", ham = 3, planet = "dantooine" },
		{ template = "mammoth_thune", name = "Old Thunderhide", ham = 4, planet = "dantooine" },
		{ template = "giant_dune_kimogila", name = "The Dune Tyrant", ham = 3, planet = "lok" },
		{ template = "peko_peko_albatross", name = "Stormwing the Elder Peko-Peko", ham = 3, planet = "naboo" },
		{ template = "reptilian_life_stealer", name = "The Life Stealer", ham = 4, planet = "dathomir" },
		{ template = "giant_cavern_spider_recluse", name = "Widowmaker", ham = 4, planet = "dathomir" },
		{ template = "gronda_juggernaut", name = "Ironhide the Gronda Juggernaut", ham = 6, planet = "corellia" },
		{ template = "mad_angler", name = "The Mad Angler Queen", ham = 4, planet = "yavin4" },
		{ template = "mire_marauder", name = "Mirefang", ham = 6, planet = "talus" },
		{ template = "mutant_bark_mite_queen", name = "The Bark Mite Broodmother", ham = 8, planet = "rori" },
	},

	-- Wilderness reference points, away from cities.
	spawnPoints = {
		corellia = { {-3646, 2870}, {4630, -5740}, {1414, -316} },
		naboo = { {-1969, 5295}, {-4627, 4207}, {-5832, -94}, {2850, 1084} },
		tatooine = { {-4512, -2270}, {-3933, -4423}, {-2575, -5517}, {-4000, 6250}, {-4632, -4346} },
		lok = { {4578, -1151}, {-70, 2650} },
		dantooine = { {4195, 5208}, {-3819, -5726}, {-555, -3825} },
		dathomir = { {-4002, -58}, {-2102, 3165}, {5676, 1901} },
		endor = { {-4550, -2250}, {-1714, 9} },
		rori = { {-2073, 3339}, {772, -2109} },
		talus = { {-2595, 3724}, {4285, 1032} },
		yavin4 = { {5097, 5537}, {466, -693}, {-3150, -3050} },
	},

	hunter = { planet = "tatooine", x = 3546.0, y = -4786.0, heading = 120 },
}

registerScreenPlay("SandboxWorldBosses", true)

local PREFIX = "SandboxWorldBosses:"

local function planetLabel(planet)
	local labels = { yavin4 = "Yavin IV" }
	return labels[planet] or (planet:sub(1, 1):upper() .. planet:sub(2))
end

function SandboxWorldBosses:start()
	local h = self.hunter
	if isZoneEnabled(h.planet) then
		local pHunter = spawnMobile(h.planet, "sandbox_big_game_hunter", 0, h.x, getWorldFloor(h.x, h.y, h.planet), h.y, h.heading, 0)
		if pHunter ~= nil then
			CreatureObject(pHunter):setCustomObjectName("Rhea Tannor (a big game hunter)")
			AiAgent(pHunter):addObjectFlag(AI_STATIONARY)
		end
	end

	for slot = 1, self.activeBosses do
		writeData(PREFIX .. "slot:" .. slot, 0)
		createEvent((self.firstSpawnDelay + slot * 5) * 1000, "SandboxWorldBosses", "fillSlot", nil, tostring(slot))
	end
end

-- Roster indexes of bosses that are alive right now (no duplicates in the rotation).
function SandboxWorldBosses:activeRosterIndexes()
	local active = {}
	for slot = 1, self.activeBosses do
		local pBoss = getSceneObject(readData(PREFIX .. "slot:" .. slot))
		if pBoss ~= nil and not CreatureObject(pBoss):isDead() then
			active[readData(PREFIX .. "roster:" .. slot)] = true
		end
	end
	return active
end

function SandboxWorldBosses:fillSlot(pNil, args)
	local slot = tonumber(args)
	local active = self:activeRosterIndexes()
	local choices = {}

	for index, boss in ipairs(self.roster) do
		if not active[index] and isZoneEnabled(boss.planet) and self.spawnPoints[boss.planet] ~= nil then
			table.insert(choices, index)
		end
	end

	if #choices == 0 then
		createEvent(self.respawnAfterEscape * 1000, "SandboxWorldBosses", "fillSlot", nil, args)
		return
	end

	local index = choices[getRandomNumber(1, #choices)]
	local boss = self.roster[index]
	local points = self.spawnPoints[boss.planet]
	local point = points[getRandomNumber(1, #points)]
	local spot = getSpawnPoint(boss.planet, point[1], point[2], 0, self.spawnRadius)

	if spot == nil then
		spot = { point[1], getWorldFloor(point[1], point[2], boss.planet), point[2] }
	end

	local pBoss = spawnMobile(boss.planet, boss.template, 0, spot[1], spot[2], spot[3], getRandomNumber(0, 359), 0)

	if pBoss == nil then
		printLuaError("SandboxWorldBosses: could not spawn " .. boss.template .. " on " .. boss.planet)
		createEvent(self.respawnAfterEscape * 1000, "SandboxWorldBosses", "fillSlot", nil, args)
		return
	end

	CreatureObject(pBoss):setCustomObjectName(boss.name .. " (world boss)")

	for _, pool in ipairs({0, 3, 6}) do -- health, action, mind
		local value = math.floor(CreatureObject(pBoss):getMaxHAM(pool) * boss.ham)
		CreatureObject(pBoss):setMaxHAM(pool, value)
		CreatureObject(pBoss):setHAM(pool, value)
	end

	local bossID = SceneObject(pBoss):getObjectID()
	writeData(PREFIX .. "slot:" .. slot, bossID)
	writeData(PREFIX .. "roster:" .. slot, index)
	writeData(bossID .. ":sandboxWorldBossSlot", slot)

	createObserver(OBJECTDESTRUCTION, "SandboxWorldBosses", "onBossKilled", pBoss)
	createEvent(self.lifetime * 1000, "SandboxWorldBosses", "expire", nil, slot .. ":" .. bossID)

	broadcastToGalaxy(nil, "\\#ffcc66[World boss]\\#ffffff " .. boss.name .. " has been sighted on " .. planetLabel(boss.planet) .. ". Ask a big game hunter in Mos Eisley for its trail.")
end

function SandboxWorldBosses:onBossKilled(pBoss, pKiller)
	if pBoss == nil then
		return 1
	end

	local bossID = SceneObject(pBoss):getObjectID()
	local slot = readData(bossID .. ":sandboxWorldBossSlot")
	local boss = self.roster[readData(PREFIX .. "roster:" .. slot)]
	local name = boss ~= nil and boss.name or "A world boss"
	local planet = SceneObject(pBoss):getZoneName()

	local dealers = CreatureObject(pBoss):getDamageDealerList()
	local paid, names = 0, {}

	if dealers ~= nil then
		for _, pPlayer in pairs(dealers) do
			if pPlayer ~= nil and SceneObject(pPlayer):isPlayerCreature() then
				CreatureObject(pPlayer):addBankCredits(self.reward, true)
				CreatureObject(pPlayer):sendSystemMessage("You receive " .. self.reward .. " credits for helping bring down " .. name .. ".")
				table.insert(names, CreatureObject(pPlayer):getFirstName())
				paid = paid + 1
			end
		end
	end

	local by = paid > 0 and (" by " .. table.concat(names, ", ")) or ""
	broadcastToGalaxy(nil, "\\#ffcc66[World boss]\\#ffffff " .. name .. " has been slain on " .. planetLabel(planet) .. by .. "!")

	deleteData(bossID .. ":sandboxWorldBossSlot")
	if slot ~= nil and slot > 0 then
		writeData(PREFIX .. "slot:" .. slot, 0)
		createEvent(self.respawnAfterKill * 1000, "SandboxWorldBosses", "fillSlot", nil, tostring(slot))
	end

	return 1
end

function SandboxWorldBosses:expire(pNil, args)
	local slot, bossID = string.match(args, "(%d+):(%d+)")
	slot, bossID = tonumber(slot), tonumber(bossID)

	if readData(PREFIX .. "slot:" .. slot) ~= bossID then
		return -- already killed and replaced
	end

	local pBoss = getSceneObject(bossID)

	if pBoss == nil or CreatureObject(pBoss):isDead() then
		return
	end

	if CreatureObject(pBoss):isInCombat() then
		createEvent(self.combatGrace * 1000, "SandboxWorldBosses", "expire", nil, args)
		return
	end

	local boss = self.roster[readData(PREFIX .. "roster:" .. slot)]
	local planet = SceneObject(pBoss):getZoneName()

	dropObserver(OBJECTDESTRUCTION, "SandboxWorldBosses", "onBossKilled", pBoss)
	deleteData(bossID .. ":sandboxWorldBossSlot")
	SceneObject(pBoss):destroyObjectFromWorld()
	writeData(PREFIX .. "slot:" .. slot, 0)

	broadcastToGalaxy(nil, "\\#ffcc66[World boss]\\#ffffff " .. (boss ~= nil and boss.name or "A world boss") .. " has slipped away from " .. planetLabel(planet) .. ". Something else is stirring...")
	createEvent(self.respawnAfterEscape * 1000, "SandboxWorldBosses", "fillSlot", nil, tostring(slot))
end

-- Text for the big game hunter, and waypoints for the asking player.
function SandboxWorldBosses:describeAndMark(pPlayer)
	local lines = {}
	local pGhost = CreatureObject(pPlayer):getPlayerObject()

	for slot = 1, self.activeBosses do
		local pBoss = getSceneObject(readData(PREFIX .. "slot:" .. slot))

		if pBoss ~= nil and not CreatureObject(pBoss):isDead() then
			local boss = self.roster[readData(PREFIX .. "roster:" .. slot)]
			local planet = SceneObject(pBoss):getZoneName()
			-- Approximate the trail to the nearest 50 m: hunters, not GPS.
			local x = math.floor(SceneObject(pBoss):getWorldPositionX() / 50 + 0.5) * 50
			local y = math.floor(SceneObject(pBoss):getWorldPositionY() / 50 + 0.5) * 50
			table.insert(lines, boss.name .. " on " .. planetLabel(planet) .. ", near " .. x .. ", " .. y)

			if pGhost ~= nil then
				PlayerObject(pGhost):addWaypoint(planet, boss.name, "World boss trail", x, 0, y, WAYPOINT_ORANGE, true, false, 0, 0)
			end
		end
	end

	if #lines == 0 then
		return "Quiet out there right now. Nothing worth hunting has shown itself. Check back later."
	end

	return "Here's what's prowling: " .. table.concat(lines, "; ") .. ". I've marked the trails in your datapad. Bring friends."
end

SandboxBigGameHunterConvoHandler = conv_handler:new {}

function SandboxBigGameHunterConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	local screen = LuaConversationScreen(pConvScreen)

	if screen:getScreenID() == "report" then
		local pClone = screen:cloneScreen()
		LuaConversationScreen(pClone):setCustomDialogText(SandboxWorldBosses:describeAndMark(pPlayer))
		return pClone
	end

	return pConvScreen
end
