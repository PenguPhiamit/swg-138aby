-- Nal Hutta as the Hutt home (PL-04; outputs/Fable-species/s7-hutt/nal-hutta-home.md): the Bilbousa NPCs who talk.
-- Placed by screenplays/sandbox/hutta_home.lua. Stock bodies only; names and text are our own (the kajidic names are
-- the S7 README's inventions, section 5.5, not Legends clans). Guards, idlers and the trainer reuse stock templates.

local function huttaNpc(name, body, conversation)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = "",
		mobType = MOB_NPC,
		faction = "",
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
	-- the bazaar, in front of the tents
	{"hutta_kessoth_outfitter", "Dessuk Kessoth, outfitter", "object/mobile/hutt_male.iff", "hutta_kessoth_outfitter_convo_template"},
	{"hutta_vollaka_broker", "Garulla Vollaka, broker", "object/mobile/hutt_female.iff", "hutta_vollaka_broker_convo_template"},
	-- the starport end of the avenue
	{"hutta_council_herald", "a council protocol droid", "object/mobile/3po_protocol_droid_silver.iff", "hutta_council_herald_convo_template"},
}

for _, p in ipairs(people) do
	CreatureTemplates:addCreatureTemplate(huttaNpc(p[2], p[3], p[4]), p[1])
end
