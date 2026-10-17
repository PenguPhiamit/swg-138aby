-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md): more wildlife for a rough, mid-to-end-game Hoth
-- (owner, 17 Oct: "mid, late and end game planet, no low levels"), levels 60-100 like the ported creatures.
-- Species from Wookieepedia's Legends article on Hoth (its fauna list): the pantran whitefang (a lean ice cat, the one
-- hunter fast enough to run down a tauntaun), the Hoth hog (a small omnivore that digs near thermal vents in family
-- groups), the ice scrabbler (a rodent, the commonest animal on Hoth) and the icetromper (a large beast). Our client has
-- none of their bodies, so each wears a stock body until there is art: sand panther, zucca boar, womp rat, bolle bol.
-- Also the named beasts of the places to find and the jobs (screenplays/sandbox/hoth_world.lua). Stats follow
-- hoth_tauntaun (65) and hoth_wampa (90); text is ours.

local function beast(t)
	return Creature:new {
		objectName = "",
		customName = t.name,
		socialGroup = t.social,
		faction = "",
		mobType = t.carnivore and MOB_CARNIVORE or MOB_HERBIVORE,
		level = t.level,
		chanceHit = 0.4 + t.level * 0.004,
		damageMin = math.floor(t.level * 7.2),
		damageMax = math.floor(t.level * 9.4),
		baseXp = t.level * 97,
		baseHAM = t.level * (t.boss and 420 or 192),
		baseHAMmax = t.level * (t.boss and 470 or 223),
		armor = t.level >= 85 and 2 or 1,
		resists = t.resists or {120,120,20,150,20,150,20,20,-1},
		meatType = t.carnivore and "meat_carnivore" or "meat_herbivore",
		meatAmount = t.meat or 300,
		hideType = "hide_wooly",
		hideAmount = t.hide or 250,
		boneType = "bone_mammal",
		boneAmount = t.bone or 200,
		milk = 0,
		tamingChance = 0,
		ferocity = t.carnivore and 8 or 0,
		pvpBitmask = t.aggressive and (AGGRESSIVE + ATTACKABLE + ENEMY) or ATTACKABLE,
		creatureBitmask = t.bitmask,
		optionsBitmask = AIENABLED,
		diet = t.carnivore and CARNIVORE or HERBIVORE,
		templates = {t.body},
		scale = t.scale or 1.0,
		lootGroups = t.loot,
		primaryWeapon = "unarmed",
		secondaryWeapon = "none",
		conversationTemplate = "",
		primaryAttacks = t.attacks,
		secondaryAttacks = { }
	}
end

-- 3% a common decoration (as the ported creatures); bosses 5% a rare one and 2% a deed (as the cave bosses)
local commonLoot = { { groups = { {group = "hoth_decor_common", chance = 10000000} }, lootChance = 300000 } }
local bossLoot = {
	{ groups = { {group = "hoth_decor_rare", chance = 10000000} }, lootChance = 500000 },
	{ groups = { {group = "hoth_vehicle_deeds", chance = 10000000} }, lootChance = 200000 },
}

local creatures = {
	hoth_pantran_whitefang = beast { name = "a pantran whitefang", social = "whitefang", level = 82, carnivore = true,
		aggressive = true, bitmask = PACK + KILLER, body = "object/mobile/corellian_sand_panther.iff", scale = 1.1,
		meat = 350, hide = 400, bone = 250, loot = commonLoot,
		attacks = { {"posturedownattack",""}, {"blindattack",""} } },
	hoth_whitefang_stalker = beast { name = "a whitefang stalker", social = "whitefang", level = 90, carnivore = true,
		aggressive = true, bitmask = PACK + KILLER, body = "object/mobile/corellian_sand_panther.iff", scale = 1.25,
		meat = 400, hide = 450, bone = 300, loot = commonLoot,
		attacks = { {"posturedownattack",""}, {"blindattack",""}, {"intimidationattack",""} } },
	hoth_hog = beast { name = "a Hoth hog", social = "hoth_hog", level = 62, bitmask = HERD,
		body = "object/mobile/zucca_boar.iff", scale = 0.85, meat = 250, hide = 150, bone = 120, loot = commonLoot,
		attacks = { {"knockdownattack",""} } },
	hoth_hog_boar = beast { name = "a Hoth hog boar", social = "hoth_hog", level = 68, bitmask = HERD,
		body = "object/mobile/zucca_boar.iff", scale = 1.0, meat = 300, hide = 180, bone = 150, loot = commonLoot,
		attacks = { {"knockdownattack",""}, {"dizzyattack",""} } },
	hoth_ice_scrabbler = beast { name = "an ice scrabbler", social = "ice_scrabbler", level = 60, aggressive = true,
		bitmask = PACK, body = "object/mobile/womp_rat.iff", scale = 0.8, meat = 40, hide = 30, bone = 20,
		loot = commonLoot, attacks = { {"blindattack",""} } },
	hoth_icetromper = beast { name = "an icetromper", social = "icetromper", level = 88, bitmask = HERD,
		body = "object/mobile/bolle_bol.iff", scale = 1.3, meat = 900, hide = 800, bone = 700, loot = commonLoot,
		resists = {140,140,25,170,25,170,25,25,-1}, attacks = { {"knockdownattack",""}, {"stunattack",""} } },
	hoth_icetromper_bull = beast { name = "an icetromper bull", social = "icetromper", level = 96, aggressive = true,
		bitmask = HERD + KILLER, body = "object/mobile/bolle_bol.iff", scale = 1.5, meat = 1100, hide = 950, bone = 800,
		loot = commonLoot, resists = {150,150,30,180,30,180,30,30,-1},
		attacks = { {"knockdownattack",""}, {"stunattack",""}, {"creatureareaknockdown",""} } },
	-- the named beasts
	hoth_wampa_rimefang = beast { name = "Rimefang", social = "wampa", level = 100, carnivore = true, boss = true,
		aggressive = true, bitmask = KILLER, body = "object/mobile/wampa.iff", scale = 1.35, meat = 1300, hide = 1300,
		bone = 1100, loot = bossLoot, resists = {160,180,45,220,45,220,45,45,-1},
		attacks = { {"stunattack",""}, {"creatureareaknockdown",""}, {"intimidationattack",""} } },
	hoth_wampa_old_echo = beast { name = "Old Echo", social = "wampa", level = 108, carnivore = true, boss = true,
		aggressive = true, bitmask = KILLER, body = "object/mobile/wampa.iff", scale = 1.45, meat = 1500, hide = 1500,
		bone = 1300, loot = bossLoot, resists = {170,190,50,230,50,230,50,50,-1},
		attacks = { {"stunattack",""}, {"creatureareaknockdown",""}, {"creatureareacombo",""}, {"intimidationattack",""} } },
	hoth_whitefang_matriarch = beast { name = "the vent hollow matriarch", social = "whitefang", level = 95,
		carnivore = true, boss = true, aggressive = true, bitmask = PACK + KILLER,
		body = "object/mobile/corellian_sand_panther.iff", scale = 1.4, meat = 500, hide = 600, bone = 400, loot = bossLoot,
		attacks = { {"posturedownattack",""}, {"blindattack",""}, {"intimidationattack",""} } },
}

for name, template in pairs(creatures) do
	CreatureTemplates:addCreatureTemplate(template, name)
end
