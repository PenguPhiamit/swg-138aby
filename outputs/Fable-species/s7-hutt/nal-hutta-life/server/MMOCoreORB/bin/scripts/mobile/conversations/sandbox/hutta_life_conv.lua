-- Nal Hutta life (PL-06): conversations for Bilbousa's townsfolk and the Kessoth job. Our own text; the handlers are
-- in screenplays/sandbox/hutta_life.lua. Era 138-139 ABY: Krayt is dead on Coruscant, his Empire is breaking up, and
-- the kajidics are richer than ever.

local function screen(template, id, text, options, stop)
	template:addScreen(ConvoScreen:new {
		id = id,
		customDialogText = text,
		stopConversation = stop and "true" or "false",
		options = options or {}
	})
end

local function convo(handler)
	return ConvoTemplate:new {
		initialScreen = "greet",
		templateType = "Lua",
		luaClassHandler = handler,
		screens = {}
	}
end

-- townsfolk: a greeting, one thing to ask, a goodbye
local function smallTalk(key, greet, question, answer, bye)
	local t = convo("HuttaTownsfolkConvoHandler")
	screen(t, "greet", greet, {{question, "answer"}, {"Goodbye.", "bye"}})
	screen(t, "answer", answer, {{"Goodbye.", "bye"}})
	screen(t, "bye", bye, {}, true)
	addConversationTemplate(key, t)
end

smallTalk("hutta_rodian_trader_convo_template",
	"Swamp eel leather, Ylesian glow-moss, Nar Shaddaa circuit boards. Everything here is honest, friend, except the prices.",
	"How is trade?",
	"Since the Sith emperor fell, the shipping lanes are wide open and half the Imperial customs posts stand empty. The kajidics have never been richer. Neither have I, almost.",
	"Come back with more credits.")
smallTalk("hutta_old_weequay_convo_template",
	"Mind your feet. The street is dry, but the swamp starts at the edge of the shelf and it does not give things back.",
	"What is out in the swamp?",
	"Borgles and squills close in. Further out, fambaa herds and worse. People say smugglers camp to the south-west, and there is an old wreck to the east that nobody has finished picking clean.",
	"Keep your blaster dry.")
smallTalk("hutta_twilek_attendant_convo_template",
	"I serve the house of the Hutt you see there. If you have business with them, speak softly and stand where they can see your hands.",
	"Is it a good house to serve?",
	"Better than some. The kajidics are at peace with each other this season, and peace means fewer poisoners in the kitchens.",
	"May your business profit you.")
smallTalk("hutta_swamp_beggar_convo_template",
	"A credit for an old spacer? I flew for the Kessoth once, before the spice took my hands.",
	"What happened to you?",
	"A run went wrong. The cargo vanished, the crew blamed me, and the Hutts do not forgive a lost cargo. Ask Bezzik at the Kessoth door. He is still looking for that spice, I hear.",
	"Bless you, whether you paid or not.")
smallTalk("hutta_nikto_dockhand_convo_template",
	"Ships in, ships out. The council takes its cut from every crate before it touches the ground.",
	"Where do the ships go?",
	"Tatooine and Corellia, mostly, on the scheduled shuttles. The rest fly from the private pads, and I do not see those.",
	"Out of my way, I have crates to move.")

local noble = convo("HuttaTownsfolkConvoHandler")
screen(noble, "greet", "(The Hutt regards you with half-closed eyes. The attendant translates.) My master asks whether you have come to buy, to sell, or to waste their time.", {
	{"I am only passing through.", "answer"},
	{"Goodbye.", "bye"},
})
screen(noble, "answer", "My master says that everyone on Nal Hutta is only passing through, except the Hutts. They wish you a short stay.", {{"Goodbye.", "bye"}})
screen(noble, "bye", "(The Hutt has already lost interest in you.)", {}, true)
addConversationTemplate("hutta_hutt_noble_convo_template", noble)

-- the Kessoth majordomo: the kajidic job (HuttaKessothJob in screenplays/sandbox/hutta_life.lua picks the first screen)
local job = convo("HuttaKessothMajordomoConvoHandler")
screen(job, "greet", "You stand at the door of the house of Kessoth. State your business, or move along.", {
	{"I am looking for work.", "offer"},
	{"Nothing. Goodbye.", "bye"},
})
screen(job, "offer", "Work. Very well. Three months ago a Kessoth freighter carrying spice went down in the swamp. The crew is dead, the spice is gone, and my master suspects the smugglers who camp to the south-west. Find out what they know. Persuade their chief, Vekk Tano, by whatever means you like.", {
	{"I will do it.", "accept"},
	{"Not now.", "bye"},
})
screen(job, "accept", "Good. I have marked the camp for you. Come back when Vekk Tano can no longer lie to anyone.", {}, true)
screen(job, "step1", "Vekk Tano still breathes, and my master's spice is still missing. The camp is south-west of the city.", {}, true)
screen(job, "step2", "So the smugglers did not take it. Then search the wreck itself, east of the city. A freighter does not lose its manifest.", {}, true)
screen(job, "step3", "Kreeg. A Nikto who thinks he is a baron. His den is far out in the north-west swamp. Bring my master's spice back, or at least make sure he never sells it.", {}, true)
screen(job, "report", "You are back. Well? Is it done?", {
	{"Kreeg is dead. The spice is in his den, waiting for your crews.", "reward"},
})
screen(job, "full", "You cannot even carry a reward. Come back when your hands are free.", {}, true)
screen(job, "reward", "Kreeg is dead and the spice is ours again. My master is pleased, which is rare. Take this, and wear Kessoth colours with pride.", {}, true)
screen(job, "done", "The house of Kessoth remembers its friends. For now, there is no more work.", {}, true)
screen(job, "bye", "Then do not block the door.", {}, true)
addConversationTemplate("hutta_kessoth_majordomo_convo_template", job)
