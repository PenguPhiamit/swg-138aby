-- Hoth fill (Claude, 17 Oct 2026; outputs/Hoth-fill/INSTALL.md): conversations of the Hoth townsfolk and the three
-- jobs. First drafts by the local role-play model (WaifuGemma4, Agent/local-research/npc-dialogue-hoth/report.md) from
-- our briefs; reviewed and edited by Claude. Handlers are in screenplays/sandbox/hoth_world.lua.

local function convo(handler)
	return ConvoTemplate:new {
		initialScreen = "greet",
		templateType = "Lua",
		luaClassHandler = handler,
		screens = {}
	}
end

local function screen(template, id, text, options, stop)
	template:addScreen(ConvoScreen:new {
		id = id,
		customDialogText = text,
		stopConversation = stop and "true" or "false",
		options = options or {}
	})
end

-- Scavenger Starport: Medic Orrin Dask
local medic = convo("HothFillConvoHandler")
screen(medic, "greet", "Sit down and hold still. Let me see where it hurts. Frostbite, wampa claws or a raider's blaster? On Hoth it's always one of the three.", {
	{"How is the infirmary holding up?", "work"},
	{"Goodbye.", "bye"},
})
screen(medic, "work", "Badly. It's less an infirmary than a repair shop for broken people, and the bacta runs out faster than the freighters bring it. If you go north past the caves, take a medpack for every friend you bring.", {}, true)
screen(medic, "bye", "Rest when you can. I'll be here if the pain comes back.", {}, true)
addConversationTemplate("hoth_fill_orrin_dask_convo_template", medic)

-- Scavenger Starport: Kesh, a Sullustan freighter pilot (the pointer to the crashed freighter)
local pilot = convo("HothFillConvoHandler")
screen(pilot, "greet", "Watch your step on the ice, friend. I'm sitting out a storm before I fly scrap back to Corellia. Between the fuel and these landing fees I barely keep my engines warm.", {
	{"Any news from the routes?", "news"},
	{"Goodbye.", "bye"},
})
screen(pilot, "news", "A fuel freighter went down on the western glacier in the last storm. The tally clerk wrote it off. I'd swear I heard a beacon out there on the way in, but nobody pays me to go looking.", {}, true)
screen(pilot, "bye", "I'm going to try for a nap before the weather breaks. Safe travels.", {}, true)
addConversationTemplate("hoth_fill_kesh_convo_template", pilot)

-- Scavenger Starport: Brother Tamm, at the Scavengers' Camp
local tamm = convo("HothFillConvoHandler")
screen(tamm, "greet", "Peace to you. Please, tread softly near the stones.", {
	{"What are the stones for?", "stones"},
	{"Goodbye.", "bye"},
})
screen(tamm, "stones", "Each one is for someone the ice has taken: salvagers, hunters, people who walked out into a storm and never came back. The camp is loud, but I keep this little corner quiet for them.", {}, true)
screen(tamm, "bye", "May warmth find you, wherever you wander.", {}, true)
addConversationTemplate("hoth_fill_brother_tamm_convo_template", tamm)

-- Rebel Forward Camp: Corporal Jeth Ardo
local ardo = convo("HothFillConvoHandler")
screen(ardo, "greet", "State your business. We don't get many visitors out here in the snow.", {
	{"Who are you watching for?", "watch"},
	{"Goodbye.", "bye"},
})
screen(ardo, "watch", "Imperial patrols, from what's left of Krayt's Empire. We've watched these wastes for a long time, and nobody has sent us orders since word came that Krayt was dead. We stay because somebody has to.", {}, true)
screen(ardo, "bye", "Watch your step. The ice is thinner than it looks.", {}, true)
addConversationTemplate("hoth_fill_jeth_ardo_convo_template", ardo)

-- Job 1: Hask Moor and the Echo Base command log
local hask = convo("HothFillHaskConvoHandler")
screen(hask, "greet", "Keep your distance, newcomer. Forty winters I've seen on this ice. You want something, or are you just blocking the wind?", {
	{"What is out there worth seeing?", "base"},
	{"Goodbye.", "bye"},
})
screen(hask, "base", "The old Rebel base in the northern massif. Echo Base, they called it, back in the Civil War, more than a century gone. A scavenger baron named Vorn Skarrel has dug his crews in there, stripping it to the walls. He's got the base's command log, and that log belongs to history, not to some junk dealer's shelf.", {
	{"I'll get the log back.", "accept"},
	{"Not my problem.", "bye"},
})
screen(hask, "accept", "Ha. Go on, then. The main door is on the east face of the massif, nine kilometres north-west of here. Skarrel keeps to the deep halls. Bring me the log and I'll make it worth your while.", {}, true)
screen(hask, "step1", "Skarrel still has the log, and you're still standing here. The east face of the massif. Go.", {}, true)
screen(hask, "report", "Is that it? The command log, after all this time. Look at that. Here, you've earned this, and something I pulled out of the ice years ago.", {
	{"Thank you.", "reward"},
})
screen(hask, "reward", "Now go get warm before the frost settles in your bones.", {}, true)
screen(hask, "full", "Your pack's stuffed full. Make some room, then come back.", {}, true)
screen(hask, "done", "Still alive? Good. I read that log every night. Most of it's supply counts, but some of it isn't.", {}, true)
screen(hask, "bye", "Go on, then, before the frost settles in your bones.", {}, true)
addConversationTemplate("hoth_fill_hask_moor_convo_template", hask)

-- Job 2: Tavi Renn and Rimefang
local tavi = convo("HothFillTaviConvoHandler")
screen(tavi, "greet", "You look like you can handle a blaster, or at least walk straight in a blizzard. I guide hunters through these wastes.", {
	{"Any work for a hunter?", "job"},
	{"Goodbye.", "bye"},
})
screen(tavi, "job", "A rogue wampa the hunters call Rimefang has been taking my clients' tauntauns at the south-western edge of the mynock fields. Bigger than the cave wampas and smarter. I want him dealt with.", {
	{"I'll hunt him.", "accept"},
	{"Maybe later.", "bye"},
})
screen(tavi, "accept", "Good. He dens in a hollow at the south-western edge of the mynock fields. Bring friends. I don't hunt for lost causes.", {}, true)
screen(tavi, "step1", "Rimefang is still out there. The hollow at the south-western edge of the mynock fields.", {}, true)
screen(tavi, "report", "Rimefang's dead? Then my clients can ride again. Here's your fee, and something from the stores.", {
	{"Thanks.", "reward"},
})
screen(tavi, "reward", "If you ever want steady work as a guide, you know where I stand.", {}, true)
screen(tavi, "full", "You've no room to carry anything. Clear your pack, then talk to me.", {}, true)
screen(tavi, "done", "The herds are quieter since Rimefang. Thanks to you.", {}, true)
screen(tavi, "bye", "Don't get lost out there.", {}, true)
addConversationTemplate("hoth_fill_tavi_renn_convo_template", tavi)

-- Job 3: Dellan Pryce at the crashed freighter, and Ysa Volt at the starport
local pryce = convo("HothFillPryceConvoHandler")
screen(pryce, "greet", "Please... is someone there? Keep your voice down. The mynocks hear everything.", {
	{"Are you hurt?", "story"},
	{"Goodbye.", "bye"},
})
screen(pryce, "story", "I'm the only one left from the freighter. The rest were lost when we hit the ice. The wreck keeps the wind off me, and the looters haven't found my corner yet. Please, tell the starport I'm still breathing.", {
	{"I'll tell them.", "accept"},
	{"I can't help you.", "bye"},
})
screen(pryce, "accept", "Thank you. The tally clerk at the starport, Ysa Volt, she keeps the list of who's lost. Tell her Dellan Pryce isn't on it yet.", {}, true)
screen(pryce, "step1", "Please hurry. Tell Ysa Volt at the starport.", {}, true)
screen(pryce, "done", "They're sending a crawler for me. I owe you my life.", {}, true)
screen(pryce, "bye", "Please, hurry... before the light fades.", {}, true)
addConversationTemplate("hoth_fill_dellan_pryce_convo_template", pryce)

local ysa = convo("HothFillYsaConvoHandler")
screen(ysa, "greet", "State your business, or stand there quietly. I keep the tally board: every ship that leaves the pad, every crate that comes back, everyone who doesn't.", {
	{"What is the board for?", "board"},
	{"Goodbye.", "bye"},
})
screen(ysa, "board", "If it isn't on my board, as far as this starport is concerned, it never happened. And I've seen enough hauls to know exactly who lies about their cargo weight.", {}, true)
screen(ysa, "report", "You've seen the freighter on the western glacier?", {
	{"Dellan Pryce is alive in the wreck.", "reward"},
})
screen(ysa, "reward", "Alive? Then he comes off the lost column. I'll send a crawler before the next storm. The salvage office pays for word like that. Here.", {}, true)
screen(ysa, "full", "The office pays in credits and scrap, and your pack can't take the scrap. Make room and come back.", {}, true)
screen(ysa, "bye", "Don't stand in the way of the next arrival.", {}, true)
addConversationTemplate("hoth_fill_ysa_volt_convo_template", ysa)
