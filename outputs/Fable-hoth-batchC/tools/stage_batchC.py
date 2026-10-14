"""Stage Hoth batch C: destroy-mission lairs and mission terminals for the Scavenger Starport (C1), the
Quartermaster Vell quest chain (C1), and the line patches that wire them in. Our own code and text (Fable,
14 Oct 2026); mission theme after Bellum Gero's gen_hoth_missions.py (salvage runs, raiders), text and placement ours.
Ground heights come from the Core3 height port validated on Hoth (../../Fable-planet-test/tools/trn_read.py).

    python -I stage_batchC.py

Writes: staged/MMOCoreORB/bin/scripts/... (new files only), snippets/, new-files.txt, patches.tsv, strings.tsv,
checks.json. apply.sh copies the new files and applies patches.tsv; strings.tsv is for the client string file.
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, '..')
sys.path.insert(0, os.path.join(OUT, 'Fable-planet-test', 'tools'))
import trn_read  # noqa: E402
from trn_iff import client_file  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts')
SNIPPETS = os.path.join(ROOT, 'snippets')
WORK = os.path.join(ROOT, 'work')

# ---------------------------------------------------------------- placement (all on the outpost's flattened 0 m pad)
OUTPOST = (0.0, -2000.0)                     # MTG's outpost_starport; landing pad 20.3 -1982.2 (planet_manager.lua)
TERMINALS = [(48.0, -1996.0), (48.0, -2002.0)]  # east of the starport, facing west (toward the building)
GIVER = (44.0, -2010.0, -90)                 # Quartermaster Vell, x y heading(deg), beside the terminals
DELIVER_POINTS = [                           # mission NPC spawn points for deliver missions: x, y, heading(rad), NEUTRALSPAWN
    (62.0, -1975.0, 3.9), (70.0, -2030.0, 2.4), (30.0, -2060.0, 0.8), (-45.0, -2070.0, 5.5),
    (-60.0, -1985.0, 1.6), (-40.0, -1925.0, 4.7), (40.0, -1935.0, 3.1), (-140.0, -1990.0, 0.3),
]
SNAPSHOT_NEAR_OUTPOST = {   # MTG snapshot objects within 160 m (ws_read.py list client:snapshot/hoth.ws), for the clearance check
    'outpost_starport': (0, -2000), 'outpost_cloning_facility_s03': (-8, -2025), 'pirate_warehouse': (8, -2025),
    'sandcrawler_debris_02': (0, -1950), 'sandcrawler_debris_01': (3, -1944), 'transport_debris_01': (-80, -1900),
    'transport_debris_02': (-80, -1890), 'lucky_despot_debris_aft_hull': (-125, -2050), 'lucky_despot_debris_lg_engine_s01': (-85, -2055),
    'lucky_despot_debris_nose_cone': (-93, -2045), 'campfire_fresh': (-95, -2047), 'camp_tent_s01_a': (-97, -2052), 'camp_tent_s01_b': (-84, -2041),
    'salvage_detail (batch B)': (-100, -1960),
}
CLEARANCE = {'outpost_starport': 40, 'outpost_cloning_facility_s03': 22, 'pirate_warehouse': 22}  # others 12 m

_ev = None


def ground(x, y):
    global _ev
    if _ev is None:
        _ev = trn_read.HeightEvaluator(trn_read.read_trn(client_file('terrain/hoth.trn')), trn_read.client_bitmap_loader)
    return round(_ev.height(x, y), 1)


def clearance(x, y):
    worst = None
    for name, (ox, oy) in SNAPSHOT_NEAR_OUTPOST.items():
        d = math.hypot(x - ox, y - oy)
        need = CLEARANCE.get(name, 12)
        if worst is None or d - need < worst[0]:
            worst = (d - need, name, round(d, 1), need)
    return {'nearest': worst[1], 'distance': worst[2], 'needed': worst[3], 'ok': worst[0] >= 0}


# ---------------------------------------------------------------- C1a: destroy-mission lairs
DESTROY = '''-- Hoth destroy-mission lairs for the general mission terminals at the Scavenger Starport.
-- Sandbox: Fable batch C (14 Oct 2026). Same shape as spawn/destroy_mission/dantooine_destroy_missions.lua.
-- MissionManagerImplementation::randomizeGenericDestroyMission reads the group named <zone>_destroy_missions and
-- picks a lair with minDifficulty <= player level + 5 and maxDifficulty >= min(player level - 5, minLevelCeiling);
-- a lair needs a building (buildings* or missionBuilding in its lair template) to be a mission target.
-- Ranges follow the creature levels in mobile/hoth: tauntaun 65 / bull 72, ice mynock 67 / greater 76,
-- scavenger raider 74, wampa 90 / elder 98. Nothing on Hoth is below 62, so players under about level 55 get no
-- destroy missions here (as on any high-level planet).
hoth_destroy_missions = {
	minLevelCeiling = 75,
	lairSpawns = {
		{
			lairTemplateName = "hoth_tauntaun_lair_neutral_medium",
			minDifficulty = 60,
			maxDifficulty = 72,
			size = 25,
		},
		{
			lairTemplateName = "hoth_ice_mynock_lair_neutral_medium",
			minDifficulty = 64,
			maxDifficulty = 76,
			size = 25,
		},
		{
			lairTemplateName = "hoth_scavenger_raider_camp_neutral_none",
			minDifficulty = 70,
			maxDifficulty = 80,
			size = 25,
		},
		{
			lairTemplateName = "hoth_wampa_lair_neutral_large",
			minDifficulty = 85,
			maxDifficulty = 100,
			size = 25,
		},
	}
}

addDestroyMissionGroup("hoth_destroy_missions", hoth_destroy_missions);
'''

# ---------------------------------------------------------------- C1b: terminals screenplay
TERMINALS_LUA = '''-- Mission terminals at Hoth's Scavenger Starport. Sandbox: Fable batch C (14 Oct 2026).
-- MTG's snapshot has no terminals at the outpost, so two general mission terminals stand east of the starport on
-- the flattened pad ground (0 m), facing the building. Style: screenplays/poi/dathomir_crash_site.lua; the tutorial
-- spawns its terminal with spawnSceneObject the same way. 7-argument spawnSceneObject takes the heading in radians
-- (DirectorManager::spawnSceneObject -> Quaternion::setHeadingDirection).

HothOutpostTerminalsScreenPlay = ScreenPlay:new {
	numberOfActs = 1,
	screenplayName = "HothOutpostTerminalsScreenPlay"
}

registerScreenPlay("HothOutpostTerminalsScreenPlay", true)

function HothOutpostTerminalsScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
	end
end

function HothOutpostTerminalsScreenPlay:spawnSceneObjects()
%send
'''

# ---------------------------------------------------------------- C1c: quest chain (ThemeParkLogic, like tasks/tatooine/aaph_koden.lua)
STF = '@static_npc/hoth/scavenger_quartermaster'
TASK_LUA = '''-- Quartermaster Vell's salvage chain at Hoth's Scavenger Starport: three short jobs (collect, kill, deliver).
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
		spawnData = { npcTemplate = "hoth_quartermaster_vell", x = %s, z = %s, y = %s, direction = %d, cellID = 0, position = STAND },
		npcNumber = 1,
		stfFile = "%s",
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
'''

NPCS_LUA = '''-- NPCs of Quartermaster Vell's salvage chain (screenplays/tasks/hoth/scavenger_quartermaster.lua).
-- Sandbox: Fable batch C (14 Oct 2026). Shapes follow mobile/quest/tatooine/aaph_koden.lua (giver) and
-- talia_reede.lua (talk-to targets); the raider captain is a named, tougher hoth_scavenger_raider. All appearance
-- templates are stock (object/mobile/serverobjects.lua). Four templates in one file so one include line wires them.

-- The giver: stands by the mission terminals east of the starport.
hoth_quartermaster_vell = Creature:new {
	objectName = "",
	customName = "Quartermaster Vell",
	socialGroup = "townsperson",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
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
	optionsBitmask = AIENABLED + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_merchant_trainer_02.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_giver_convotemplate",
	primaryAttacks = {},
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_quartermaster_vell, "hoth_quartermaster_vell")

-- Mission 1 target: the salvage tech who hands over the power regulator (retrieve: talk, no kill).
hoth_salvage_tech_baxx = Creature:new {
	objectName = "",
	customName = "Ria Baxx",
	socialGroup = "",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = NONE,
	optionsBitmask = INVULNERABLE + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_brigade_technician_human_female_01.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_target_convotemplate",
	primaryAttacks = brawlermid,
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_salvage_tech_baxx, "hoth_salvage_tech_baxx")

-- Mission 2 target: the raider captain (assassinate). A named hoth_scavenger_raider, a few levels up.
hoth_raider_captain_korro = Creature:new {
	objectName = "",
	customName = "Thane Korro",
	socialGroup = "thug",
	faction = "thug",
	mobType = MOB_NPC,
	level = 80,
	chanceHit = 0.75,
	damageMin = 580,
	damageMax = 790,
	baseXp = 7900,
	baseHAM = 15000,
	baseHAMmax = 18000,
	armor = 1,
	resists = {35,35,35,35,65,35,35,-1,-1},
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
	templates = {"object/mobile/dressed_mercenary_commander_zab_m.iff"},
	lootGroups = {
		{
			groups = {
				{group = "armor_all", chance = 3000000},
				{group = "weapons_all", chance = 3500000},
				{group = "wearables_all", chance = 3500000}
			},
			lootChance = 4000000
		},
		{
			groups = {
				{group = "hoth_decor_common", chance = 10000000}
			},
			lootChance = 600000
		}
	},
	primaryWeapon = "pirate_weapons_heavy",
	secondaryWeapon = "unarmed",
	conversationTemplate = "",
	reactionStf = "@npc_reaction/slang",
	primaryAttacks = marksmanmid,
	secondaryAttacks = brawlermid
}

CreatureTemplates:addCreatureTemplate(hoth_raider_captain_korro, "hoth_raider_captain_korro")

-- Mission 3 target: the broker who takes the alternator (deliver: talk).
hoth_salvage_broker_kett = Creature:new {
	objectName = "",
	customName = "Doro Kett",
	socialGroup = "",
	mobType = MOB_NPC,
	faction = "",
	level = 62,
	chanceHit = 0.6,
	damageMin = 420,
	damageMax = 580,
	baseXp = 0,
	baseHAM = 9000,
	baseHAMmax = 11000,
	armor = 0,
	resists = {20,20,20,20,50,20,20,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = ATTACKABLE,
	creatureBitmask = NONE,
	optionsBitmask = INVULNERABLE + CONVERSABLE,
	diet = HERBIVORE,
	templates = {"object/mobile/dressed_criminal_smuggler_human_male_01.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	conversationTemplate = "scavenger_quartermaster_mission_target_convotemplate",
	primaryAttacks = brawlermid,
	secondaryAttacks = { }
}

CreatureTemplates:addCreatureTemplate(hoth_salvage_broker_kett, "hoth_salvage_broker_kett")
'''

# ---------------------------------------------------------------- strings (client stf; keys as the handlers read them)
GENERIC_STRINGS = [
    ('cant_work', "You're already on a job for someone else. Finish that first, then come and see me."),
    ('notyet', "Nothing for you right now. Check back once the next salvage run is in."),
    ('next', "That's all the work I have for you. Thanks for keeping the runs moving."),
    ('npc_reset', "Fine, we start over. Come back when you're ready."),
    ('npc_backtowork', "Then get back out there."),
    ('npc_failure_n', "That didn't go the way either of us wanted. Let's try again."),
]
MISSION_STRINGS = {
    1: [
        ('npc_1', "Hey. You look like you can handle the cold. One of my salvage techs, Ria Baxx, went out to the Lucky Despot's engine spur for a power regulator and hasn't checked in. Go find her and bring that regulator back to me."),
        ('player_1', "I'll find her."),
        ('player_2', "What's out there?"),
        ('player_3', "What's the pay?"),
        ('player_4', "Where's the engine spur?"),
        ('player_5', "Not my problem."),
        ('npc_2', "Good. I'll mark the last position she reported. Watch the wreck, the mynocks like the power lines."),
        ('npc_3', "Ice mynocks, mostly. They chew on anything that still carries a charge, and that spur still does."),
        ('npc_4', "Fifteen hundred credits when I have the regulator in my hands."),
        ('npc_5', "Out past the outpost, in the drift field. I'll give you a waypoint once you take the job."),
        ('npc_6', "Then stop warming yourself at my heater."),
        ('npc_noloc', "I can't get a fix on her position right now. Come back in a moment."),
        ('npc_work', "Still waiting on that regulator."),
        ('player_reset', "I lost track of Baxx. Can you reset the job?"),
        ('player_sorry', "Sorry, I'm on it."),
        ('npc_reset', "Fine. I'll send out a fresh fix. Come back when you're ready."),
        ('npc_backtowork', "Then go."),
        ('npc_reward', "That's the one. Baxx made it back ahead of you, by the way. Here's your fifteen hundred."),
        ('waypoint_name', "Ria Baxx"),
        ('waypoint_description', "Find the salvage tech Ria Baxx and collect the power regulator."),
        ('return_waypoint_name', "Quartermaster Vell"),
        ('return_waypoint_description', "Return the power regulator to Quartermaster Vell at the Scavenger Starport."),
        ('npc_breech', "Watch out, they're coming off the wreck!"),
        ('npc_smuggle', "You're from Vell? Take it, the regulator's yours. I'm heading back as soon as my hands thaw."),
        ('dontknowyou', "I don't know you. Talk to Vell if you want work."),
    ],
    2: [
        ('npc_1', "The regulator job tells me you can walk the drifts. Here's a harder one. A raider captain called Thane Korro has hit three of my salvage runs this month. Find him and put him down."),
        ('player_1', "Consider it done."),
        ('player_2', "Who is Korro?"),
        ('player_3', "What's it pay?"),
        ('player_4', "How many are with him?"),
        ('player_5', "I don't do killings."),
        ('npc_2', "I'll give you his last position. Don't let his crew flank you on the ice."),
        ('npc_3', "Used to run with the outpost scavengers until he decided robbing them paid better. Now he takes what my people dig out."),
        ('npc_4', "Three thousand credits for Korro. His gear is yours too."),
        ('npc_5', "Two, usually. They're good shots with those heavy rifles, so don't stand in the open."),
        ('npc_6', "Then I'll find someone who does."),
        ('npc_noloc', "I don't have a fix on Korro right now. Give me a minute."),
        ('npc_work', "Korro's still breathing. Get to it."),
        ('player_reset', "I lost Korro's trail. Can you reset the job?"),
        ('player_sorry', "Sorry, still working on it."),
        ('npc_reset', "Fine. I'll get a new fix. Come back when you're ready."),
        ('npc_backtowork', "Then go find him."),
        ('npc_reward', "Korro's done? That's three runs that come home now. Here's your three thousand."),
        ('waypoint_name', "Thane Korro"),
        ('waypoint_description', "Kill the raider captain Thane Korro."),
        ('return_waypoint_name', "Quartermaster Vell"),
        ('return_waypoint_description', "Report Korro's death to Quartermaster Vell at the Scavenger Starport."),
        ('npc_breech', "Vell sent you? Then Vell gets you back in pieces!"),
        ('dontknowyou', "I don't know you. Talk to Vell if you want work."),
    ],
    3: [
        ('npc_1', "Last job, and an easy one. A broker named Doro Kett buys what we pull out of the wrecks. Take this salvaged current alternator out to his camp and hand it over."),
        ('player_1', "I'll take it."),
        ('player_2', "Who is Kett?"),
        ('player_3', "What's it pay?"),
        ('player_4', "Where's his camp?"),
        ('player_5', "Find another courier."),
        ('npc_2', "Here's the alternator. Keep it dry and don't drop it, the casing is cracked."),
        ('npc_3', "A trader who comes out from Corellia for the Despot's parts. Pays well and asks no questions, which suits us."),
        ('npc_4', "Two thousand credits once Kett confirms delivery."),
        ('npc_5', "He camps out on the drifts, never the same spot twice. I'll give you a waypoint once you take the job."),
        ('npc_6', "Then I'll find another courier."),
        ('npc_noloc', "I don't know where Kett has set up today. Come back in a moment."),
        ('npc_work', "Kett's still waiting on that alternator."),
        ('player_reset', "I can't find Kett. Can you reset the job?"),
        ('player_sorry', "Sorry, on my way."),
        ('npc_reset', "Fine. I'll find out where he is now. Come back when you're ready."),
        ('npc_backtowork', "Then get moving."),
        ('npc_reward', "Kett sent word. Here's your two thousand, and you've got a standing welcome at this outpost."),
        ('waypoint_name', "Doro Kett"),
        ('waypoint_description', "Deliver the salvaged current alternator to the broker Doro Kett."),
        ('return_waypoint_name', "Quartermaster Vell"),
        ('return_waypoint_description', "Return to Quartermaster Vell at the Scavenger Starport."),
        ('npc_smuggle', "From Vell? Let's see it. Cracked casing, but it'll do. Tell Vell the credits are on their way."),
        ('notit', "You haven't got the alternator on you. Go back to Vell."),
        ('npc_dropoff', "Pleasure doing business. Mind the drifts on the way back."),
        ('dontknowyou', "I don't know you. Talk to Vell if you want work."),
    ],
}


def write(path, text, newline='\n'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline=newline) as f:
        f.write(text)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    checks = {'placed': [], 'files': {}, 'patches': [], 'dev_originals_at_staging': {}}
    # terminals screenplay
    lines = []
    for i, (x, y) in enumerate(TERMINALS, 1):
        z = ground(x, y)
        lines.append('\tspawnSceneObject("hoth", "object/tangible/terminal/terminal_mission.iff", %s, %s, %s, 0, math.rad(-90))\n' % (x, z, y))
        checks['placed'].append(dict(what='mission terminal %d' % i, template='object/tangible/terminal/terminal_mission.iff',
                                     x=x, z=z, y=y, heading_deg=-90, clearance=clearance(x, y)))
    write(os.path.join(STAGED, 'screenplays', 'poi', 'hoth_outpost_terminals.lua'), TERMINALS_LUA % ''.join(lines))
    # destroy missions
    write(os.path.join(STAGED, 'mobile', 'spawn', 'destroy_mission', 'hoth_destroy_missions.lua'), DESTROY)
    # quest chain
    gx, gy, gh = GIVER
    gz = ground(gx, gy)
    checks['placed'].append(dict(what='Quartermaster Vell (giver)', template='hoth_quartermaster_vell', x=gx, z=gz, y=gy, heading_deg=gh, clearance=clearance(gx, gy)))
    write(os.path.join(STAGED, 'screenplays', 'tasks', 'hoth', 'scavenger_quartermaster.lua'), TASK_LUA % (gx, gz, gy, gh, STF))
    write(os.path.join(STAGED, 'mobile', 'quest', 'hoth', 'scavenger_quartermaster_npcs.lua'), NPCS_LUA)
    # deliver-mission NPC spawn points (appended to the auto-generated planet map)
    pts = []
    for x, y, h in DELIVER_POINTS:
        pts.append('\t\t{ %s, %s, %s, 2 }' % (x, y, h))
        checks['placed'].append(dict(what='deliver-mission NPC spawn point (NEUTRALSPAWN)', x=x, z=ground(x, y), y=y, heading_rad=h, clearance=clearance(x, y)))
    snippet = ('\n-- Sandbox: Hoth (Fable batch C): mission NPC spawn points for deliver missions at the Scavenger Starport.\n'
               '-- Same block shape as the generated planets above; spawn type 2 = NEUTRALSPAWN (NpcSpawnPoint.h).\n'
               'planet_hoth = PlanetSpawnMap:new {\n\tname = "hoth",\n\tnpcs = {\n' + ',\n'.join(pts) + '\n\t}\n}\n\nuniverse:addPlanet(planet_hoth);\n')
    write(os.path.join(SNIPPETS, 'mission_npc_spawn_points_hoth.lua'), snippet)
    # new-files.txt
    new_files = [
        'mobile/spawn/destroy_mission/hoth_destroy_missions.lua',
        'screenplays/poi/hoth_outpost_terminals.lua',
        'screenplays/tasks/hoth/scavenger_quartermaster.lua',
        'mobile/quest/hoth/scavenger_quartermaster_npcs.lua',
    ]
    write(os.path.join(ROOT, 'new-files.txt'), '# new files under MMOCoreORB/bin/scripts (copied by apply.sh; refused if a different file exists)\n' + '\n'.join(new_files) + '\n')
    # patches.tsv (\t in a field stands for a tab inside the line)
    patches = [
        ('mobile/spawn/serverobjects.lua', 'after', 'includeFile("spawn/destroy_mission/factional_rebel_destroy_missions.lua")',
         'includeFile("spawn/destroy_mission/hoth_destroy_missions.lua") -- Sandbox: Hoth terminal missions (Fable batch C)'),
        ('screenplays/screenplays.lua', 'after', 'includeFile("poi/hoth_camps.lua") -- Sandbox: Hoth camps (Fable batch B)',
         'includeFile("poi/hoth_outpost_terminals.lua") -- Sandbox: Hoth mission terminals (Fable batch C)'),
        ('screenplays/screenplays.lua', 'after', 'includeFile("tasks/tatooine/aaph_koden.lua")',
         'includeFile("tasks/hoth/scavenger_quartermaster.lua") -- Sandbox: Hoth quest chain (Fable batch C)'),
        ('mobile/quest/serverobjects.lua', 'after', 'includeFile("quest/tatooine/aaph_koden.lua")',
         'includeFile("quest/hoth/scavenger_quartermaster_npcs.lua") -- Sandbox: Hoth quest chain (Fable batch C)'),
        ('mobile/conversations/themepark/logic/mission_giver_conv.lua', 'after',
         'createMissionGiverConvoTemplate("yith_seenath_mission_giver_convotemplate","yith_seenath_mission_giver_conv_handler")',
         'createMissionGiverConvoTemplate("scavenger_quartermaster_mission_giver_convotemplate", "scavenger_quartermaster_mission_giver_conv_handler") -- Sandbox: Hoth (Fable batch C)'),
        ('mobile/conversations/themepark/logic/mission_target_conv.lua', 'after',
         'createMissionTargetConvoTemplate("yith_seenath_mission_target_convotemplate","yith_seenath_mission_target_conv_handler")',
         'createMissionTargetConvoTemplate("scavenger_quartermaster_mission_target_convotemplate", "scavenger_quartermaster_mission_target_conv_handler") -- Sandbox: Hoth (Fable batch C)'),
        ('managers/mission/mission_cities.lua', 'before', '\\t{ "yavin4", "Yavin IV Labor Outpost", -6925, -5707, 130 }',
         '\\t{ "hoth", "Scavenger Starport", 0, -2000, 150 },'),
        ('managers/mission/mission_npc_spawn_points.lua', 'append', 'planet_hoth', 'snippets/mission_npc_spawn_points_hoth.lua'),
    ]
    tsv = ['# <file under MMOCoreORB/bin/scripts>\t<after|before|append>\t<anchor line | marker>\t<new line | snippet file>; a literal \\t stands for a tab']
    for p in patches:
        tsv.append('\t'.join(p))
        checks['patches'].append(dict(file=p[0], mode=p[1], anchor=p[2], line=p[3]))
    write(os.path.join(ROOT, 'patches.tsv'), '\n'.join(tsv) + '\n')
    # strings.tsv
    rows = ['# string/en/static_npc/hoth/scavenger_quartermaster.stf (client string table; the server reads it too via getStringId)',
            '# key\ttext']
    for k, t in GENERIC_STRINGS:
        rows.append('%s\t%s' % (k, t))
    for n in (1, 2, 3):
        for k, t in MISSION_STRINGS[n]:
            key = k if k == 'npc_failure_n' else '%s_%d' % (k, n)
            rows.append('%s\t%s' % (key, t))
    write(os.path.join(ROOT, 'strings.tsv'), '\n'.join(rows) + '\n')
    checks['strings'] = {'stf': 'string/en/static_npc/hoth/scavenger_quartermaster.stf', 'count': len(rows) - 2}
    # hashes
    for rel in new_files:
        checks['files'][rel] = sha(os.path.join(STAGED, rel))
    checks['files']['snippets/mission_npc_spawn_points_hoth.lua'] = sha(os.path.join(SNIPPETS, 'mission_npc_spawn_points_hoth.lua'))
    for fn in sorted(os.listdir(WORK)):
        if fn.endswith('.orig'):
            checks['dev_originals_at_staging'][fn.replace('__', '/')[:-5]] = sha(os.path.join(WORK, fn))
    # client-side objects this batch relies on (and the C2 facts), looked up in the archives the test client loads
    from trn_iff import client_index
    idx = client_index()
    wanted = {
        'mission terminal': 'object/tangible/terminal/shared_terminal_mission.iff',
        'giver appearance': 'object/mobile/shared_dressed_merchant_trainer_02.iff',
        'Baxx appearance': 'object/mobile/shared_dressed_brigade_technician_human_female_01.iff',
        'Korro appearance': 'object/mobile/shared_dressed_mercenary_commander_zab_m.iff',
        'Kett appearance': 'object/mobile/shared_dressed_criminal_smuggler_human_male_01.iff',
        'quest item 1': 'object/tangible/mission/quest_item/shared_power_regulator.iff',
        'quest item 3': 'object/tangible/mission/quest_item/shared_current_alternator.iff',
        'ice mynock (secondary spawn; mobile/hoth/hoth_ice_mynock.lua uses salt_mynock_hue)': 'object/mobile/shared_salt_mynock_hue.iff',
        'snowspeeder deed (C2)': 'object/tangible/deed/vehicle_deed/shared_snowspeeder_deed.iff',
        'snowspeeder pcd (C2)': 'object/intangible/vehicle/shared_snowspeeder.iff',
        'snowspeeder vehicle (C2)': 'object/mobile/vehicle/shared_snowspeeder.iff',
        'hoth AT-ST pcd (C2)': 'object/intangible/vehicle/shared_hoth_at_st_pcd.iff',
        'hoth AT-ST vehicle (C2)': 'object/mobile/vehicle/shared_hoth_at_st.iff',
        'hoth AT-ST deed (C2, expected absent)': 'object/tangible/deed/vehicle_deed/shared_hoth_at_st_deed.iff',
        'tauntaun creature (C2)': 'object/mobile/shared_tauntaun_hue.iff',
        'tauntaun pet pcd (C2)': 'object/intangible/pet/shared_tauntaun_hue.iff',
        'tauntaun pet deed (C2)': 'object/tangible/deed/pet_deed/shared_tauntaun_deed.iff',
        'tauntaun appearance (C2)': 'appearance/tauntaun_hue.sat',
        'mount rider slot descriptor (C2)': 'abstract/slot/descriptor/mount_rider.iff',
    }
    checks['client_objects'] = {k: {'path': v, 'archive': idx.get(v.lower())} for k, v in wanted.items()}
    # the slot descriptor the client's tauntaun template names, following the template's base chain (the server reads
    # the same IFFs: TemplateManager::addTemplate reads the client IFF, then the objects.lua entry on top)
    import re

    def chain_strings(path, depth=0):
        out = []
        data = client_file(path)
        if data is None or depth > 4:
            return [(path, None, [])]
        refs = sorted(set(m.group(0).decode('latin-1') for m in re.finditer(rb'[A-Za-z0-9_/\.]+\.iff', data)))
        descriptors = [r for r in refs if r.startswith('abstract/slot/descriptor/')]
        out.append((path, idx.get(path.lower()), descriptors))
        for r in refs:
            if r.startswith('object/') and r != path:   # the base template (DERV)
                out.extend(chain_strings(r, depth + 1))
        return out

    for label, path in (('tauntaun creature (C2)', 'object/mobile/shared_tauntaun_hue.iff'), ('tauntaun pet pcd (C2)', 'object/intangible/pet/shared_tauntaun_hue.iff'),
                        ('dewback creature (stock mount, for comparison)', 'object/mobile/shared_dewback_hue.iff'),
                        ('dewback pet pcd (stock mount, for comparison)', 'object/intangible/pet/shared_dewback_hue.iff')):
        entry = checks['client_objects'].setdefault(label, {'path': path, 'archive': idx.get(path.lower())})
        entry['template_chain'] = [{'file': p, 'archive': a, 'slot_descriptors': d} for p, a, d in chain_strings(path)]
    # mount scale ranges come from a client datatable, keyed by appearance file: is the tauntaun in the one our client loads?
    for name in ('datatables/mount/valid_scale_range.iff', 'datatables/mount/saddle_capacity.iff'):
        data = client_file(name)
        checks['client_objects'][name] = {'path': name, 'archive': idx.get(name), 'mentions_tauntaun': bool(data and b'tauntaun' in data.lower()),
                                          'mentions_dewback': bool(data and b'dewback' in data.lower())}
    checks['clearance_ok'] = all(p['clearance']['ok'] for p in checks['placed'])
    checks['ground_flat'] = all(abs(p['z']) < 0.5 for p in checks['placed'])
    checks['destroy_missions'] = {'minLevelCeiling': 75, 'lairs': ['hoth_tauntaun_lair_neutral_medium 60-72', 'hoth_ice_mynock_lair_neutral_medium 64-76',
                                                                   'hoth_scavenger_raider_camp_neutral_none 70-80', 'hoth_wampa_lair_neutral_large 85-100']}
    write(os.path.join(ROOT, 'checks.json'), json.dumps(checks, indent=1) + '\n')
    for p in checks['placed']:
        print('%-50s x %7.1f  z %5.1f  y %8.1f  nearest %s at %s m (need %s) %s' % (p['what'], p['x'], p['z'], p['y'], p['clearance']['nearest'],
              p['clearance']['distance'], p['clearance']['needed'], 'ok' if p['clearance']['ok'] else 'TOO CLOSE'))
    print('clearance ok:', checks['clearance_ok'], ' ground flat:', checks['ground_flat'], ' strings:', checks['strings']['count'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
