-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md). The owner (17 Oct): "lets get a session to flush
-- out hoth"; Hoth is a "mid, late and end game planet, no low levels ... a rougher planet". This adds
--   townsfolk at the Scavenger Starport and the camps (eight who talk, six who stand about);
--   six places to find: a crashed freighter with its one survivor, a crashed Imperial transport and its holdouts, the
--   Generator Field below Echo Base, the salvagers' camp at Echo Base's main door, Rimefang's hollow and the vent hollow;
--   three jobs: Hask Moor (the Echo Base command log; the baron is in screenplays/poi/hoth_echo_base.lua), Tavi Renn
--   (Rimefang) and Dellan Pryce (word of a survivor, back to Ysa Volt).
-- Server objects only: no client data, no terrain change. Sites checked with Fable-hoth-batchA/tools/hoth_survey.py
-- (flat ground; heights from getWorldFloor at spawn). Our own code and text, in the shape of
-- screenplays/sandbox/ossus_world.lua and hutta_life.lua; era 138-139 ABY.

HothWorld = ScreenPlay:new {
	planet = "hoth",

	-- template, x, y, heading, display name (nil: the template's), respawn seconds
	townsfolk = {
		-- Scavenger Starport (pad at 21, -1982; terminals at x 48, Vell at 44, -2010; the wall north of the pad is scenery)
		{ "hoth_fill_hask_moor", 25, -2015, 160 },
		{ "hoth_fill_kesh", 0, -2010, 120 },
		{ "hoth_fill_tavi_renn", 62, -2004, 270 },
		{ "hoth_fill_ysa_volt", 62, -1990, 270 },
		{ "hoth_fill_orrin_dask", 35, -2030, 0 },
		{ "commoner_old", 10, -2024, 45, "a prospector", 300 },
		{ "nomad", -8, -1996, 90, "a salvager", 300 },
		{ "commoner", 70, -2020, 300, "a cargo hauler", 300 },
		{ "artisan", 18, -2034, 10, "a parts trader", 300 },
		{ "commoner", 52, -2030, 200, "a dock hand", 300 },
		{ "commoner_naboo", -12, -2022, 60, "a stranded traveller", 300 },
		-- the Scavengers' Camp and the Rebel Forward Camp
		{ "hoth_fill_brother_tamm", -1388, -3290, 200 },
		{ "hoth_fill_jeth_ardo", -2792, 1194, 300 },
	},

	-- the places to find: centre, props (server template, dx, dy, heading in degrees), people (template, dx, dy, name,
	-- respawn; the respawn of a job target is ours, see job), and an optional job target
	places = {
		{ name = "the crashed freighter", x = -4200, y = -2600,
			props = {
				{ "object/static/structure/general/lucky_despot_debris_forward_hull.iff", 0, 14, 20 },
				{ "object/static/structure/general/lucky_despot_debris_aft_hull.iff", -18, -10, 200 },
				{ "object/static/structure/general/lucky_despot_debris_lg_engine_s01.iff", 22, -6, 75 },
				{ "object/static/structure/general/lucky_despot_debris_md_engine.iff", -30, 12, 140 },
				{ "object/static/structure/general/lucky_despot_debris_nose_cone.iff", 12, 32, 10 },
				{ "object/static/item/item_hoth_crate_01.iff", 8, 2, 30 },
				{ "object/static/item/item_hoth_crate_01.iff", 10, 4, 70 },
				{ "object/static/structure/general/campfire_burnt.iff", 5, -2, 0 },
			},
			people = {
				{ "hoth_fill_dellan_pryce", 6, 1, nil, 300 },
				{ "hoth_wreck_looter", -28, -22, nil, 600 },
				{ "hoth_wreck_looter", -34, -16, nil, 600 },
				{ "hoth_wreck_looter", -24, -30, nil, 600 },
				{ "hoth_ice_mynock", 30, 18, nil, 420 },
				{ "hoth_ice_mynock", 34, 24, nil, 420 },
			} },
		{ name = "the Imperial wreck", x = 3800, y = 1800,
			props = {
				{ "object/static/structure/general/debris_deathstar_large_tube.iff", 0, 10, 30 },
				{ "object/static/structure/general/debris_deathstar_turbolaser.iff", -16, 4, 110 },
				{ "object/static/structure/general/debris_deathstar_storage.iff", 14, -8, 250 },
				{ "object/static/structure/general/escape_pod.iff", -8, -18, 60 },
				{ "object/static/structure/military/bunker_crate_style_01.iff", 6, -2, 15 },
				{ "object/static/structure/military/bunker_crate_style_01.iff", 8, 0, 85 },
				{ "object/static/structure/general/campfire_burnt.iff", 0, -6, 0 },
			},
			people = {
				{ "hoth_holdout_captain_venn", 2, -4, nil, 1800 },
				{ "hoth_imperial_holdout", -6, -10, nil, 600 },
				{ "hoth_imperial_holdout", 9, -12, nil, 600 },
				{ "hoth_imperial_holdout", -12, 2, nil, 600 },
				{ "hoth_imperial_holdout", 14, 4, nil, 600 },
				{ "hoth_imperial_holdout", 0, 18, nil, 600 },
			} },
		{ name = "the Generator Field", x = -4400, y = 5400,
			props = {
				{ "object/building/heroic/hoth_generator_destroyed.iff", 0, 0, 0 },
				{ "object/static/structure/general/atat_debris_01.iff", -45, 30, 70 },
				{ "object/static/structure/general/atat_debris_02.iff", 40, -35, 200 },
				{ "object/static/item/item_hoth_generator_destroyed_01.iff", 30, 28, 40 },
				{ "object/static/item/item_hoth_crate_01.iff", -24, -26, 0 },
				{ "object/static/item/item_hoth_buggy.iff", -30, -30, 120 },
			},
			people = {
				{ "hoth_generator_scrapper", -22, -20, nil, 600 },
				{ "hoth_generator_scrapper", -28, -22, nil, 600 },
				{ "hoth_generator_scrapper", 26, 22, nil, 600 },
				{ "hoth_generator_scrapper", 34, 26, nil, 600 },
				{ "hoth_probe_droid", 0, 40, nil, 600 },
			} },
		{ name = "the salvagers' camp at Echo Base", x = -5040, y = 5460,
			props = {
				{ "object/static/structure/corellia/corl_tent_med.iff", -10, 8, 160 },
				{ "object/static/structure/corellia/corl_tent_med.iff", 10, 8, 200 },
				{ "object/static/structure/general/campfire_burnt.iff", 0, 0, 0 },
				{ "object/static/item/item_hoth_crate_01.iff", 6, -6, 20 },
				{ "object/static/item/item_hoth_crate_01.iff", 8, -5, 80 },
				{ "object/static/item/item_hoth_buggy.iff", -14, -10, 230 },
			},
			people = {
				{ "hoth_echo_salvager", -4, -3, nil, 600 },
				{ "hoth_echo_salvager", 5, -2, nil, 600 },
				{ "hoth_echo_cutter", 0, 5, nil, 600 },
			} },
		{ name = "Rimefang's hollow", x = -2400, y = -5200,
			props = {
				{ "object/building/heroic/frozen_tauntaun.iff", 8, 6, 40 },
			},
			people = {
				{ "hoth_wampa", -10, 6, nil, 600 },
				{ "hoth_wampa", 12, -8, nil, 600 },
			},
			job = { template = "hoth_wampa_rimefang", job = "rimefang", dx = 0, dy = 0, respawn = 1800 } },
		{ name = "the vent hollow", x = 1800, y = -700,
			props = {},
			people = {
				{ "hoth_whitefang_matriarch", 0, 0, nil, 1800 },
				{ "hoth_pantran_whitefang", -8, 5, nil, 600 },
				{ "hoth_pantran_whitefang", 7, 6, nil, 600 },
				{ "hoth_whitefang_stalker", 2, -9, nil, 600 },
			} },
	},
}

registerScreenPlay("HothWorld", true)

local SP = "HothWorld"

function HothWorld:start()
	if not isZoneEnabled(self.planet) then
		return
	end

	for _, p in ipairs(self.townsfolk) do
		self:spawnAt(p[1], p[2], p[3], p[4], p[5], p[6], true)
	end

	for i, place in ipairs(self.places) do
		self:spawnPlace(place)

		if place.job ~= nil then
			self:spawnJobTarget(nil, tostring(i))
		end
	end
end

function HothWorld:spawnAt(template, x, y, heading, name, respawn, stationary)
	local pMobile = spawnMobile(self.planet, template, respawn or 0, x, getWorldFloor(x, y, self.planet), y, heading, 0)

	if pMobile == nil then
		printLuaError("HothWorld: could not spawn " .. template .. " at " .. x .. ", " .. y)
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

function HothWorld:spawnPlace(place)
	for _, prop in ipairs(place.props) do
		local x, y = place.x + prop[2], place.y + prop[3]
		spawnSceneObject(self.planet, prop[1], x, getWorldFloor(x, y, self.planet), y, 0, math.rad(prop[4]))
	end

	for _, p in ipairs(place.people) do
		self:spawnAt(p[1], place.x + p[2], place.y + p[3], getRandomNumber(0, 359), p[4], p[5], false)
	end
end

-- A job target has no engine respawn: it comes back after its own time with the kill observer set up again.
function HothWorld:spawnJobTarget(pNil, args)
	local place = self.places[tonumber(args)]
	local j = place.job
	local pMobile = self:spawnAt(j.template, place.x + j.dx, place.y + j.dy, getRandomNumber(0, 359), nil, 0, false)

	if pMobile == nil then
		return
	end

	writeData(SceneObject(pMobile):getObjectID() .. ":hothWorldPlace", tonumber(args))
	createObserver(OBJECTDESTRUCTION, SP, "onJobTargetKilled", pMobile)
end

function HothWorld:onJobTargetKilled(pVictim, pAttacker)
	if pVictim == nil then
		return 1
	end

	local id = SceneObject(pVictim):getObjectID()
	local i = readData(id .. ":hothWorldPlace")
	deleteData(id .. ":hothWorldPlace")
	local place = self.places[i]

	if place == nil or place.job == nil then
		return 1
	end

	HothFillJobs:creditKill(pVictim, pAttacker, place.job.job)
	createEvent(place.job.respawn * 1000, SP, "spawnJobTarget", nil, tostring(i))

	return 1
end

-- The three jobs. Per player: readScreenPlayData(pPlayer, "HothFillJobs", <job>) is 0 (not taken), 1 (taken),
-- 2 (target done, report back) or 3 (rewarded; each job is done once).
HothFillJobs = {
	name = "HothFillJobs",
	jobs = {
		echo = {
			target = { -5051, 5440, "Hask Moor's job: Echo Base, the main door" },
			giver = { 25, -2015, "Hask Moor's job: back to Hask Moor" },
			message = "Among Vorn Skarrel's things you find the old base's command log, its casing frosted white. Take it to Hask Moor at the Scavenger Starport.",
			credits = 7000, loot = "hoth_decor_rare",
		},
		rimefang = {
			target = { -2400, -5200, "Tavi Renn's job: Rimefang's hollow" },
			giver = { 62, -2004, "Tavi Renn's job: back to Tavi Renn" },
			message = "Rimefang is dead. Tell Tavi Renn at the Scavenger Starport.",
			credits = 5000, loot = "hoth_decor_common",
		},
		pryce = {
			giver = { 62, -1990, "Dellan Pryce: tell Ysa Volt" },
			credits = 3500, loot = "hoth_decor_common",
		},
	},
}

function HothFillJobs:getStep(pPlayer, job)
	return tonumber(readScreenPlayData(pPlayer, self.name, job)) or 0
end

function HothFillJobs:setStep(pPlayer, job, step)
	writeScreenPlayData(pPlayer, self.name, job, tostring(step))
end

-- One job waypoint at a time, of the stock quest-task type (as hutta_life.lua): removed by its type.
function HothFillJobs:setWaypoint(pPlayer, point)
	local pGhost = CreatureObject(pPlayer):getPlayerObject()

	if pGhost == nil then
		return
	end

	PlayerObject(pGhost):removeWaypointBySpecialType(WAYPOINTQUESTTASK)

	if point ~= nil then
		PlayerObject(pGhost):addWaypoint("hoth", point[3], "", point[1], 0, point[2], WAYPOINT_YELLOW, true, true, WAYPOINTQUESTTASK)
	end
end

function HothFillJobs:accept(pPlayer, job)
	if self:getStep(pPlayer, job) ~= 0 then
		return
	end

	local j = self.jobs[job]

	if j.target ~= nil then
		self:setStep(pPlayer, job, 1)
		self:setWaypoint(pPlayer, j.target)
	else
		self:setStep(pPlayer, job, 2)   -- the word-of-mouth job: straight to reporting back
		self:setWaypoint(pPlayer, j.giver)
	end
end

-- The killer and their group members within 128 m of the body who have the job taken all get credit.
function HothFillJobs:creditKill(pVictim, pAttacker, job)
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
		if self:getStep(pPlayer, job) == 1 then
			self:setStep(pPlayer, job, 2)
			CreatureObject(pPlayer):sendSystemMessage(self.jobs[job].message)
			self:setWaypoint(pPlayer, self.jobs[job].giver)
		end
	end
end

function HothFillJobs:reward(pPlayer, job)
	if self:getStep(pPlayer, job) ~= 2 then
		return true
	end

	local pInventory = SceneObject(pPlayer):getSlottedObject("inventory")

	if pInventory == nil or SceneObject(pInventory):isContainerFullRecursive() then
		return false
	end

	local j = self.jobs[job]
	createLoot(pInventory, j.loot, 0, true)
	CreatureObject(pPlayer):addCashCredits(j.credits, true)
	self:setStep(pPlayer, job, 3)
	self:setWaypoint(pPlayer, nil)

	return true
end

-- Conversation handlers (mobile/conversations/sandbox/hoth_world_conv.lua)

HothFillConvoHandler = conv_handler:new {}

-- a giver: greet (not taken), step1 (taken), report (target done), done (rewarded)
local function giverHandler(job)
	local handler = conv_handler:new {}

	function handler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
		local screens = {[0] = "greet", [1] = "step1", [2] = "report", [3] = "done"}
		return LuaConversationTemplate(pConvTemplate):getScreen(screens[HothFillJobs:getStep(pPlayer, job)] or "greet")
	end

	function handler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
		local id = LuaConversationScreen(pConvScreen):getScreenID()

		if id == "accept" then
			HothFillJobs:accept(pPlayer, job)
		elseif id == "reward" and not HothFillJobs:reward(pPlayer, job) then
			return LuaConversationTemplate(pConvTemplate):getScreen("full")
		end

		return pConvScreen
	end

	return handler
end

HothFillHaskConvoHandler = giverHandler("echo")
HothFillTaviConvoHandler = giverHandler("rimefang")

-- Dellan Pryce starts the third job; Ysa Volt ends it.
HothFillPryceConvoHandler = conv_handler:new {}

function HothFillPryceConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local screens = {[0] = "greet", [2] = "step1", [3] = "done"}
	return LuaConversationTemplate(pConvTemplate):getScreen(screens[HothFillJobs:getStep(pPlayer, "pryce")] or "greet")
end

function HothFillPryceConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	if LuaConversationScreen(pConvScreen):getScreenID() == "accept" then
		HothFillJobs:accept(pPlayer, "pryce")
	end

	return pConvScreen
end

HothFillYsaConvoHandler = conv_handler:new {}

function HothFillYsaConvoHandler:getInitialScreen(pPlayer, pNpc, pConvTemplate)
	local screen = HothFillJobs:getStep(pPlayer, "pryce") == 2 and "report" or "greet"
	return LuaConversationTemplate(pConvTemplate):getScreen(screen)
end

function HothFillYsaConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	if LuaConversationScreen(pConvScreen):getScreenID() == "reward" and not HothFillJobs:reward(pPlayer, "pryce") then
		return LuaConversationTemplate(pConvTemplate):getScreen("full")
	end

	return pConvScreen
end
