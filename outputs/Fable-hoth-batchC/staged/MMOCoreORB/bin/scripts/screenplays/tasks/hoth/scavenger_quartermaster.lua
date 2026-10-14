-- Quartermaster Vell's salvage chain at Hoth's Scavenger Starport: three short jobs (collect, kill, deliver).
-- Sandbox: Fable batch C (14 Oct 2026). Same framework as screenplays/tasks/tatooine/aaph_koden.lua (ThemeParkLogic);
-- story and names ours, theme after Bellum Gero's gen_hoth_missions.py (salvage runs and raiders). Dialogue keys live
-- in string/en/static_npc/hoth/scavenger_quartermaster.stf (strings.tsv in the batch folder); the server reads them
-- with getStringId, so the string file must be in a tre both sides load (local_planets.tre).
-- No faction field: the chain is neutral, like the outpost.

scavenger_quartermaster_missions =
{
	{
		-- 1: collect. Salvage tech Ria Baxx went out to the Lucky Despot engine spur for a power regulator; find her,
		-- she hands it over (retrieve = talk to the target, no kill); two ice mynocks are picking at the wreck.
		missionType = "retrieve",
		primarySpawns =
		{
			{ npcTemplate = "hoth_salvage_tech_baxx", npcName = "Ria Baxx" }
		},
		secondarySpawns =
		{
			{ npcTemplate = "hoth_ice_mynock", npcName = "an ice mynock" },
			{ npcTemplate = "hoth_ice_mynock", npcName = "an ice mynock" }
		},
		itemSpawns =
		{
			{ itemTemplate = "object/tangible/mission/quest_item/power_regulator.iff", itemName = "Salvaged Power Regulator" }
		},
		rewards =
		{
			{ rewardType = "credits", amount = 1500 }
		}
	},
	{
		-- 2: kill. Raider captain Thane Korro has been hitting the outpost's salvage runs.
		missionType = "assassinate",
		primarySpawns =
		{
			{ npcTemplate = "hoth_raider_captain_korro", npcName = "Thane Korro" }
		},
		secondarySpawns =
		{
			{ npcTemplate = "hoth_scavenger_raider", npcName = "a scavenger raider" },
			{ npcTemplate = "hoth_scavenger_raider", npcName = "a scavenger raider" }
		},
		itemSpawns = {},
		rewards =
		{
			{ rewardType = "credits", amount = 3000 }
		}
	},
	{
		-- 3: deliver. Take a salvaged current alternator to Doro Kett, the broker who buys the outpost's scrap.
		missionType = "deliver",
		primarySpawns =
		{
			{ npcTemplate = "hoth_salvage_broker_kett", npcName = "Doro Kett" }
		},
		secondarySpawns = {},
		itemSpawns =
		{
			{ itemTemplate = "object/tangible/mission/quest_item/current_alternator.iff", itemName = "Salvaged Current Alternator" }
		},
		rewards =
		{
			{ rewardType = "credits", amount = 2000 }
		}
	}
}

npcMapScavengerQuartermaster =
{
	{
		spawnData = { npcTemplate = "hoth_quartermaster_vell", x = 44.0, z = 0.0, y = -2010.0, direction = -90, cellID = 0, position = STAND },
		npcNumber = 1,
		stfFile = "@static_npc/hoth/scavenger_quartermaster",
		missions = scavenger_quartermaster_missions
	},
}

ScavengerQuartermaster = ThemeParkLogic:new {
	npcMap = npcMapScavengerQuartermaster,
	className = "ScavengerQuartermaster",
	screenPlayState = "scavenger_quartermaster_quest",
	planetName = "hoth",
	distance = 600
}

registerScreenPlay("ScavengerQuartermaster", true)

scavenger_quartermaster_mission_giver_conv_handler = mission_giver_conv_handler:new {
	themePark = ScavengerQuartermaster
}
scavenger_quartermaster_mission_target_conv_handler = mission_target_conv_handler:new {
	themePark = ScavengerQuartermaster
}
