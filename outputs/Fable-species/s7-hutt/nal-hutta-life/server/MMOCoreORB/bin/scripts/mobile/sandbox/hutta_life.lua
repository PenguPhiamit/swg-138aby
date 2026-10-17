-- Nal Hutta life (PL-06; outputs/Fable-species/s7-hutt/nal-hutta-life.md): the new Bilbousa townsfolk who talk, the
-- city watch who walk the streets, the Kessoth majordomo who gives the kajidic job, and the job's two named foes.
-- Placed by screenplays/sandbox/hutta_life.lua. Stock bodies, stock loot groups; names and text are our own.

local function townsfolk(name, body, conversation, level)
	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = "",
		mobType = MOB_NPC,
		faction = "",
		level = level or 20,
		chanceHit = 0.33,
		damageMin = 180,
		damageMax = 190,
		baseXp = 0,
		baseHAM = 5000,
		baseHAMmax = 6100,
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
		optionsBitmask = conversation ~= "" and (AIENABLED + INVULNERABLE + CONVERSABLE) or (AIENABLED + INVULNERABLE),
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
	-- key, name, body, conversation
	{"hutta_rodian_trader", "Teeso, a Rodian trader", "object/mobile/dressed_commoner_tatooine_rodian_male_01.iff", "hutta_rodian_trader_convo_template"},
	{"hutta_old_weequay", "an old Weequay", "object/mobile/dressed_tatooine_weequay_thug.iff", "hutta_old_weequay_convo_template"},
	{"hutta_twilek_attendant", "Lyssa, a Twi'lek attendant", "object/mobile/dressed_commoner_naboo_twilek_female_01.iff", "hutta_twilek_attendant_convo_template"},
	{"hutta_swamp_beggar", "a swamp beggar", "object/mobile/dressed_commoner_old_twilek_male_01.iff", "hutta_swamp_beggar_convo_template"},
	{"hutta_nikto_dockhand", "a Nikto dockhand", "object/mobile/dressed_patron_nikto_01.iff", "hutta_nikto_dockhand_convo_template"},
	{"hutta_hutt_noble_kessoth", "Orruba Kessoth", "object/mobile/hutt_female.iff", "hutta_hutt_noble_convo_template"},
	{"hutta_hutt_noble_dromuul", "Gorga Dromuul", "object/mobile/hutt_male.iff", "hutta_hutt_noble_convo_template"},
	{"hutta_kessoth_majordomo", "Bezzik, Kessoth majordomo", "object/mobile/dressed_commoner_fat_twilek_male_01.iff", "hutta_kessoth_majordomo_convo_template"},
	-- the cantina's dancers (Oola's dance, in the main hall)
	{"hutta_cantina_dancer", "a cantina dancer", "object/mobile/dressed_dancer_trainer_twk_female_01.iff", ""},
	-- the city watch: walks the streets (a patrol), never fights
	{"hutta_weequay_watch", "a kajidic watchman", "object/mobile/dressed_tatooine_weequay_thug.iff", ""},
}

for _, p in ipairs(people) do
	CreatureTemplates:addCreatureTemplate(townsfolk(p[2], p[3], p[4]), p[1])
end

local function foe(name, body, level, ham, xp, loot)
	local groups = {}

	for _, g in ipairs(loot) do
		table.insert(groups, { groups = { {group = g, chance = 10000000} } })
	end

	return Creature:new {
		objectName = "",
		customName = name,
		socialGroup = "thug",
		mobType = MOB_NPC,
		faction = "thug",
		level = level,
		chanceHit = 0.4,
		damageMin = 300,
		damageMax = 310 + level,
		baseXp = xp,
		baseHAM = ham,
		baseHAMmax = math.floor(ham * 1.2),
		armor = 0,
		resists = {30,30,10,10,10,-1,-1,-1,-1},
		meatType = "",
		meatAmount = 0,
		hideType = "",
		hideAmount = 0,
		boneType = "",
		boneAmount = 0,
		milk = 0,
		tamingChance = 0,
		ferocity = 0,
		pvpBitmask = AGGRESSIVE + ATTACKABLE + ENEMY,
		creatureBitmask = PACK + KILLER,
		optionsBitmask = AIENABLED,
		diet = HERBIVORE,
		templates = {body},
		lootGroups = groups,
		primaryWeapon = "rebel_weapons_heavy",
		secondaryWeapon = "unarmed",
		conversationTemplate = "",
		reactionStf = "@npc_reaction/military",
		primaryAttacks = merge(brawlermaster,marksmanmaster),
		secondaryAttacks = { }
	}
end

-- the kajidic job (screenplays/sandbox/hutta_life.lua): step 1 at the smugglers' camp, step 3 at the spice den
CreatureTemplates:addCreatureTemplate(foe("Vekk Tano, smuggler chief", "object/mobile/dressed_binayre_scalawag_twk_male_01.iff",
	24, 9500, 2600, {"thug_tier_1", "weequay_tier_1"}), "hutta_camp_boss")
CreatureTemplates:addCreatureTemplate(foe("Kreeg, the Nikto spice baron", "object/mobile/dressed_blood_razor_pirate_captain_nikto_m.iff",
	36, 22000, 5200, {"thug_tier_1", "weequay_tier_1", "aakuans_tier_1"}), "hutta_spice_baron")
