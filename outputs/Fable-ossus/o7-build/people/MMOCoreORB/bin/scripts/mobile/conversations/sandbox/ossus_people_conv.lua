-- Ossus people (PL-02): conversations. Our own text; the handlers are in screenplays/sandbox/ossus_people.lua,
-- which also picks each NPC's first screen from the player's progress.

local function screen(template, id, text, options, stop)
	template:addScreen(ConvoScreen:new {
		id = id,
		customDialogText = text,
		stopConversation = stop and "true" or "false",
		options = options or {}
	})
end

local function convo(name, handler)
	return ConvoTemplate:new {
		initialScreen = "greet",
		templateType = "Lua",
		luaClassHandler = handler,
		screens = {}
	}
end

-- POI 5: Elder Iravi, the highland hunt
local shaman = convo("ossus_ysanna_shaman_convo_template", "OssusYsannaShamanConvoHandler")
screen(shaman, "greet", "You walked up from Knossa? Few offworlders do. My people have lived in these hills since before the Jedi came to Ossus, and we were still here when they were driven out of it.", {
	{"What do you hunt up here?", "hunt_offer"},
	{"Goodbye.", "bye"},
})
screen(shaman, "hunt_offer", "Kirruk. A pack has climbed onto the shoulder below the old stone circle, where they have no business being. They foul the ground we keep for the dead. Three of them. Will you thin them for us?", {
	{"I'll hunt them.", "hunt_accept"},
	{"Not today.", "bye"},
})
screen(shaman, "hunt_accept", "Then go up the path to the stones. I have marked the place in your datapad. Come back when the three are dead.", {}, true)
screen(shaman, "hunt_active", "The kirruk are still up by the stones. Three of them, on the shoulder below the circle.", {
	{"I lost their trail.", "hunt_retrack"},
	{"I'm on it.", "bye"},
})
screen(shaman, "hunt_retrack", "Look again. I have marked where they were last seen.", {}, true)
screen(shaman, "hunt_reward", "The stones are quiet again. Take this, and take our thanks. The Ysanna remember who helps them.", {}, true)
screen(shaman, "greet_done", "The circle is clean, thanks to you. Walk carefully in the hills, offworlder.", {}, true)
screen(shaman, "bye", "Go well.", {}, true)
addConversationTemplate("ossus_ysanna_shaman_convo_template", shaman)

-- POI 15: Lieutenant Dera Moll, the part errand
local pilot = convo("ossus_alliance_pilot_convo_template", "OssusAlliancePilotConvoHandler")
screen(pilot, "greet", "Easy. I'm not armed, and nobody's hunting me any more, I hope. Galactic Alliance, or what's left of it. I put this fighter down in the long grass when the war was still on. Now I just need to get it off the ground.", {
	{"What do you need?", "part_offer"},
	{"Who are you?", "who"},
	{"Goodbye.", "bye"},
})
screen(pilot, "who", "Dera Moll. I flew patrols out of a hidden base until Krayt's people found it. Word is he's dead now, and his garrison over the academy ruins doesn't know what to do with itself. Me neither.", {
	{"What do you need?", "part_offer"},
	{"Goodbye.", "bye"},
})
screen(pilot, "part_offer", "A power coupling. Mine cracked on landing. The foreman at the kathracite adit in Imhar Canyon, Teel, runs heavy haulers, and he'll have a spare that fits. I can't leave the fighter. Will you fetch it?", {
	{"I'll get it.", "part_accept"},
	{"Not now.", "bye"},
})
screen(pilot, "part_accept", "Thanks. The adit is east, in the canyon. I've marked it for you. Tell Teel it's for Moll.", {}, true)
screen(pilot, "part_waiting", "Teel's at the kathracite adit, in Imhar Canyon. Tell him it's for Moll.", {}, true)
screen(pilot, "part_reward", "That's the one. A day's work and she'll fly. Here, it isn't much, but it's honest pay.", {}, true)
screen(pilot, "greet_done", "Nearly ready to fly. When I go, I'll put in a word for you, wherever the Alliance has its people these days.", {}, true)
screen(pilot, "bye", "Mind the kirruk out here.", {}, true)
addConversationTemplate("ossus_alliance_pilot_convo_template", pilot)

-- POI 9: Brannock Teel, the adit foreman
local foreman = convo("ossus_adit_foreman_convo_template", "OssusAditForemanConvoHandler")
screen(foreman, "greet", "This is a working mine, friend. The kathracite goes to the Hutt's field on the mesa, and the Hutt pays when it arrives. Mind the carts.", {
	{"Just looking.", "bye"},
})
screen(foreman, "part_ask", "Moll sent you? That pilot's been out in the grass for years. A power coupling... yes, I've got one off a dead hauler. Take it. Tell her she owes me a drink.", {
	{"Thanks.", "part_given"},
})
screen(foreman, "part_given", "Go on, before I think better of it.", {}, true)
screen(foreman, "part_carrying", "Get that coupling to the lieutenant. She's by the wreck in the north grassland.", {}, true)
screen(foreman, "bye", "Mind the carts.", {}, true)
addConversationTemplate("ossus_adit_foreman_convo_template", foreman)

-- POI 4: Archivist Senn Oduro, the memorial road
local archivist = convo("ossus_vault_archivist_convo_template", "OssusVaultArchivistConvoHandler")
screen(archivist, "greet", "Mind the trench. We are opening what the Great Library left below ground. Most of it burned long ago, but stone keeps better than flimsiplast.", {
	{"Tell me about the road.", "road"},
	{"Goodbye.", "bye"},
})
screen(archivist, "road", "Pilgrims raised stones along the road from Knossa to the academy, one for every group of students who died there in the year 130. Walk it from the first stone above Knossa, past the middle stone, to the ring by the craters, and you will have seen what the ruins mean.", {
	{"I'll walk it.", "road_accept"},
	{"Maybe later.", "bye"},
})
screen(archivist, "road_accept", "I have marked the first stone, the middle stone and the ring. Walk them in that order. Then come back and tell me what you saw.", {}, true)
screen(archivist, "road_reward", "So you walked it all. Good. The road is how we remember them. Take this for your trouble, and keep the walk to yourself near the garrison.", {}, true)
screen(archivist, "greet_done", "Thank you again for walking the road. Few do.", {}, true)
screen(archivist, "bye", "Mind the trench on your way out.", {}, true)
addConversationTemplate("ossus_vault_archivist_convo_template", archivist)

-- POI 2: the robed stranger (a hidden Jedi; owner 15 Oct: rare, met in the sanctuary)
local jedi = convo("ossus_hidden_jedi_convo_template", "OssusHiddenJediConvoHandler")
screen(jedi, "greet", "You found this place. Few do, and fewer by accident. Sit, if you like. Speak softly. The garrison is close.", {
	{"Who are you?", "who"},
	{"I won't tell anyone you're here.", "promise"},
	{"I'll go.", "bye"},
})
screen(jedi, "who", "Someone who studied here once, when the academy stood. When the Sith came, some of us went into the ground and stayed there. Krayt is dead, they say. I will believe the war is over when the troopers above us go home.", {
	{"I won't tell anyone you're here.", "promise"},
	{"I'll go.", "bye"},
})
screen(jedi, "promise", "Then you have done more for us than you know. Go carefully. And if you hear the Ysanna sing at night, listen. They remember more than the archives do.", {}, true)
screen(jedi, "refuse", "The stranger keeps their head bowed and says nothing.", {}, true)
screen(jedi, "bye", "May the Force be with you.", {}, true)
addConversationTemplate("ossus_hidden_jedi_convo_template", jedi)

-- POI 18: Ondrubba the Hutt
local hutt = convo("ossus_hutt_broker_convo_template", "OssusHuttBrokerConvoHandler")
screen(hutt, "greet", "(in Huttese, through a protocol unit) The honourable Ondrubba welcomes you to his field. Everything on Ossus is for sale. Everything that leaves Ossus pays his fee.", {
	{"What do you buy?", "buy"},
	{"Goodbye.", "bye"},
})
screen(hutt, "buy", "(through the protocol unit) Kathracite from the canyon, and whatever the garrison digs up and does not want the Empire to see. Ondrubba asks no questions, and his prices show it.", {}, true)
screen(hutt, "bye", "(through the protocol unit) Ondrubba is gracious. Go.", {}, true)
addConversationTemplate("ossus_hutt_broker_convo_template", hutt)

-- POI 3: Major Kesh Vantor, the garrison
local major = convo("ossus_garrison_commander_convo_template", "OssusGarrisonCommanderConvoHandler")
screen(major, "greet", "State your business. This dig is under Imperial authority, and civilians keep to the road.", {
	{"What are you guarding?", "dig"},
	{"Goodbye.", "bye"},
})
screen(major, "dig", "Whatever the Jedi buried. My orders came from the Emperor himself, and they have not changed since his death. Until they do, we dig, and we hold this rim.", {}, true)
screen(major, "refuse", "I know what you are. Leave the benchland while you still can.", {}, true)
screen(major, "bye", "Keep to the road.", {}, true)
addConversationTemplate("ossus_garrison_commander_convo_template", major)

-- POI 8: Old Pell, the hamlet
local fisher = convo("ossus_hamlet_fisher_convo_template", "OssusHamletFisherConvoHandler")
screen(fisher, "greet", "Mind the nets. My family has fished Adega Lake through three governments and two wars. The fish never noticed any of them.", {
	{"What's in the lake?", "lake"},
	{"Goodbye.", "bye"},
})
screen(fisher, "lake", "Good eating, if you know where to cast. The mud yaks come down to drink at dusk. Leave them be and they'll leave you be.", {}, true)
screen(fisher, "bye", "Fair winds.", {}, true)
addConversationTemplate("ossus_hamlet_fisher_convo_template", fisher)
