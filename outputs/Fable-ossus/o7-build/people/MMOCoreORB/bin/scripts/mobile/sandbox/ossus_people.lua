-- Ossus people (PL-02; outputs/Fable-ossus/o7-build/people/README.md): the NPCs who talk. Placed by
-- screenplays/sandbox/ossus_people.lua at the O7 places. Stock bodies only; names and text are our own.
-- Era 138-139 ABY: the academy fell in 130, Krayt died in 138, his garrison still holds the benchland.
-- The ambient guards, workers and townsfolk reuse stock templates and are not defined here.

local function ossusNpc(name, body, conversation, faction)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = "",
		mobType = MOB_NPC,
		faction = faction or "",
		level = 30,
		chanceHit = 0.39,
		damageMin = 290,
		damageMax = 300,
		baseXp = 0,
		baseHAM = 8400,
		baseHAMmax = 10200,
		armor = 0,
		resists = {0,0,0,0,0,0,0,-1,-1},
		meatType = "",
		meatAmount = 0,
		hideType = "",
		hideAmount = 0,
		boneType = "",
		boneAmount = 0,
		milk = 0,
		tamingChance = 0,
		ferocity = 0,
		pvpBitmask = NONE,
		creatureBitmask = NONE,
		optionsBitmask = AIENABLED + INVULNERABLE + CONVERSABLE,
		diet = HERBIVORE,
		templates = {body},
		lootGroups = {},
		primaryWeapon = "unarmed",
		secondaryWeapon = "none",
		conversationTemplate = conversation,
		primaryAttacks = {},
		secondaryAttacks = {}
	}
end

local people = {
	-- POI 5, the Ysanna hunting camp: the highland hunt
	{"ossus_ysanna_shaman", "Elder Iravi (Ysanna)", "object/mobile/dressed_tatooine_hermit.iff", "ossus_ysanna_shaman_convo_template"},
	-- POI 15, the crashed fighter: the part errand
	{"ossus_alliance_pilot", "Lieutenant Dera Moll", "object/mobile/dressed_rebel_pilot_human_female_01.iff", "ossus_alliance_pilot_convo_template"},
	-- POI 9, the kathracite adit: the other end of the errand
	{"ossus_adit_foreman", "Brannock Teel, adit foreman", "object/mobile/dressed_mand_miner_hum_01.iff", "ossus_adit_foreman_convo_template"},
	-- POI 4, the Great Library vault dig: the memorial road
	{"ossus_vault_archivist", "Archivist Senn Oduro", "object/mobile/dressed_brigade_technician_human_female_01.iff", "ossus_vault_archivist_convo_template"},
	-- POI 2, inside the sanctuary (rare: present about one hour in three to five)
	{"ossus_hidden_jedi", "a robed stranger", "object/mobile/dressed_jedi_trainer_old_human_male_01.iff", "ossus_hidden_jedi_convo_template"},
	-- POI 18, the Hutt landing field
	{"ossus_hutt_broker", "Ondrubba the Hutt", "object/mobile/hutt_male.iff", "ossus_hutt_broker_convo_template"},
	-- POI 3, the garrison over the ruins (Krayt's Empire, GCW faction imperial)
	{"ossus_garrison_commander", "Major Kesh Vantor", "object/mobile/dressed_imperial_major_m.iff", "ossus_garrison_commander_convo_template", "imperial"},
	-- POI 8, the Adega Lake hamlet
	{"ossus_hamlet_fisher", "Old Pell", "object/mobile/dressed_quest_farmer.iff", "ossus_hamlet_fisher_convo_template"},
}

for _, p in ipairs(people) do
	CreatureTemplates:addCreatureTemplate(ossusNpc(p[2], p[3], p[4], p[5]), p[1])
end
