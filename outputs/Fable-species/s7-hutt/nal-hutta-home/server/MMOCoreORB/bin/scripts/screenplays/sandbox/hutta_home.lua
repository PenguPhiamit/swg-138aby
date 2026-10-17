-- Nal Hutta as the Hutt home (PL-04; outputs/Fable-species/s7-hutt/nal-hutta-home.md).
--
-- Spawns Bilbousa's people (positions in hutta_home_places.lua, generated from home.json): the council herald at the
-- starport end of the avenue, the Kessoth outfitter and the Vollaka broker in the bazaar, two Gamorrean guards at each
-- of the six kajidic seats, the stock smuggler trainer at the cantina door and a few idlers. It also places four general
-- mission terminals (two "Kajidic contracts" on the avenue, two "Smuggling runs" by the cantina) and one Hutt
-- businessmen camp as the east trade yard. Pre-CU has no smuggler mission type: the terminals give the general
-- destroy and deliver missions, with the lowland lairs of hutta_destroy_missions as targets.
-- The vendors sell stock items for credits through a list box (the event promoter's pattern). Hutt players pay the
-- kin price. Our own code and text. Non-persistent spawns: they are made again at every server start.

HuttaHome = ScreenPlay:new {
	planet = "hutta",

	huttSpecies = 234,          -- CreatureObject.idl HUTT = 0xEA (S7)
	kinPrice = 0.9,             -- Hutt players pay 90 percent

	terminalTemplate = "object/tangible/terminal/terminal_mission.iff",
	terminalNames = {
		kajidic_contracts = "Kajidic contracts",
		smuggling_runs = "Smuggling runs",
	},

	-- name, template, price in credits
	wares = {
		outfitter = {
			{ "Kessoth crew vest, first style", "object/tangible/wearables/vest/vest_hutt_gang_s01.iff", 2500 },
			{ "Kessoth crew vest, second style", "object/tangible/wearables/vest/vest_hutt_gang_s02.iff", 2500 },
			{ "Kessoth crew vest, third style", "object/tangible/wearables/vest/vest_hutt_gang_s03.iff", 2500 },
		},
		broker = {
			{ "Spice jar, first style", "object/tangible/container/jar/jar_spice_s01.iff", 600 },
			{ "Spice jar, second style", "object/tangible/container/jar/jar_spice_s02.iff", 600 },
			{ "Spice jar, third style", "object/tangible/container/jar/jar_spice_s03.iff", 600 },
			{ "Standing candlestick lamp", "object/tangible/furniture/all/frn_all_lamp_candlestick_free_s01_lit.iff", 900 },
			{ "Standing candlestick lamp, second style", "object/tangible/furniture/all/frn_all_lamp_candlestick_free_s02_lit.iff", 900 },
			{ "Desert hall lamp", "object/tangible/furniture/all/frn_all_lamp_tatt_s01_lit.iff", 750 },
		},
	},
}

registerScreenPlay("HuttaHome", true)

function HuttaHome:start()
	if not isZoneEnabled(self.planet) then
		return
	end

	self:spawnPeople()
	self:spawnTradeYard()
end

function HuttaHome:spawnPeople()
	for _, p in ipairs(HuttaHomePlaces.people) do
		local kind, key, x, y, heading, label = p[1], p[2], p[3], p[4], p[5], p[6]
		local z = getWorldFloor(x, y, self.planet)

		if kind == "terminal" then
			local pTerminal = spawnSceneObject(self.planet, self.terminalTemplate, x, z, y, 0, math.rad(heading))

			if pTerminal == nil then
				printLuaError("HuttaHome: could not place a terminal at " .. x .. ", " .. y)
			else
				SceneObject(pTerminal):setCustomObjectName(self.terminalNames[key])
			end
		else
			local pMobile = spawnMobile(self.planet, key, 0, x, z, y, heading, 0)

			if pMobile == nil then
				printLuaError("HuttaHome: could not spawn " .. key .. " at " .. x .. ", " .. y)
			else
				if label ~= nil and label ~= "" then
					CreatureObject(pMobile):setCustomObjectName(label)
				end

				if AiAgent(pMobile) ~= nil then
					AiAgent(pMobile):addObjectFlag(AI_STATIONARY)
				end
			end
		end
	end
end

function HuttaHome:spawnTradeYard()
	local t = HuttaHomePlaces.tradeYard
	local pYard = spawnSceneObject(self.planet, t[1], t[2], getWorldFloor(t[2], t[3], self.planet), t[3], 0, math.rad(t[4]))

	if pYard == nil then
		printLuaError("HuttaHome: could not place the trade yard " .. t[1])
	end
end

-- The vendors

function HuttaHome:price(pPlayer, base)
	if CreatureObject(pPlayer):getSpecies() == self.huttSpecies then
		return math.floor(base * self.kinPrice)
	end

	return base
end

function HuttaHome:sendSale(pNpc, pPlayer, stall)
	local wares = self.wares[stall]

	if wares == nil then
		return
	end

	writeStringData(SceneObject(pPlayer):getObjectID() .. ":hutta_home_stall", stall)

	local options = {}

	for i = 1, #wares do
		table.insert(options, { wares[i][1] .. " (" .. self:price(pPlayer, wares[i][3]) .. " credits)", 0 })
	end

	local prompt = "Choose an item and press OK to buy it with cash."

	if CreatureObject(pPlayer):getSpecies() == self.huttSpecies then
		prompt = prompt .. " One of the blood pays the kin price."
	end

	local suiManager = LuaSuiManager()
	suiManager:sendListBox(pNpc, pPlayer, "Kajidic goods", prompt, 2, "@cancel", "", "@ok", "HuttaHome", "handleSale", 32, options)
end

function HuttaHome:handleSale(pPlayer, pSui, eventIndex, arg0)
	if pPlayer == nil then
		return
	end

	local playerID = SceneObject(pPlayer):getObjectID()
	local stall = readStringData(playerID .. ":hutta_home_stall")
	deleteStringData(playerID .. ":hutta_home_stall")

	if eventIndex == 1 then
		return
	end

	local wares = self.wares[stall]
	local index = arg0 + 1

	if wares == nil or index < 1 or index > #wares then
		return
	end

	local item = wares[index]
	local cost = self:price(pPlayer, item[3])
	local pInventory = SceneObject(pPlayer):getSlottedObject("inventory")

	if pInventory == nil then
		return
	end

	if CreatureObject(pPlayer):getCashCredits() < cost then
		CreatureObject(pPlayer):sendSystemMessage("You do not have enough cash for that.")
		return
	elseif SceneObject(pInventory):isContainerFullRecursive() then
		CreatureObject(pPlayer):sendSystemMessage("Your inventory is full.")
		return
	end

	local pItem = giveItem(pInventory, item[2], -1)

	if pItem == nil then
		CreatureObject(pPlayer):sendSystemMessage("The stall has none left today.")
		printLuaError("HuttaHome: giveItem failed for " .. item[2])
		return
	end

	CreatureObject(pPlayer):subtractCashCredits(cost)
	CreatureObject(pPlayer):sendSystemMessage("You buy " .. item[1] .. " for " .. cost .. " credits.")
end

-- Conversation handlers

local function screenID(pConvScreen)
	return LuaConversationScreen(pConvScreen):getScreenID()
end

HuttaCouncilHeraldConvoHandler = conv_handler:new {}

HuttaKessothOutfitterConvoHandler = conv_handler:new {}

function HuttaKessothOutfitterConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	if screenID(pConvScreen) == "sale" then
		HuttaHome:sendSale(pNpc, pPlayer, "outfitter")
	end

	return pConvScreen
end

HuttaVollakaBrokerConvoHandler = conv_handler:new {}

function HuttaVollakaBrokerConvoHandler:runScreenHandlers(pConvTemplate, pPlayer, pNpc, selectedOption, pConvScreen)
	if screenID(pConvScreen) == "sale" then
		HuttaHome:sendSale(pNpc, pPlayer, "broker")
	end

	return pConvScreen
end
