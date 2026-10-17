-- Nal Hutta as the Hutt home (PL-04): conversations. Our own text; the handlers are in screenplays/sandbox/hutta_home.lua.
-- Era 138-139 ABY: Krayt is dead on Coruscant and his Empire is breaking up; the kajidics never stopped trading.

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

-- the council herald, at the starport end of the avenue
local herald = convo("HuttaCouncilHeraldConvoHandler")
screen(herald, "greet", "Welcome to Bilbousa, seat of the kajidic council of Nal Hutta. Kindly keep your weapons holstered. The council's peace holds inside the city, and the Gamorreans keep it.", {
	{"What is this place?", "about"},
	{"Who runs the city?", "kajidics"},
	{"Where can I find work?", "work"},
	{"Goodbye.", "bye"},
})
screen(herald, "about", "Nal Hutta is the Hutts' world, and Bilbousa is its capital. The council sits in the great palace at the south end of this avenue. Since the Sith emperor died on Coruscant, the council has had a great deal of new business. Beyond the town shelf the swamp begins. The lowlands breed borgles, squills and worse, and the deep swamp is worse still.", {
	{"Who runs the city?", "kajidics"},
	{"Where can I find work?", "work"},
	{"Goodbye.", "bye"},
})
screen(herald, "kajidics", "Six kajidics keep seats in Bilbousa. Kessoth, Vollaka, Dromuul and Narissik hold the old towers; Tashuga and Bessolo built on the new ground to the north and west. Lamps and banners mark each tower's door, and its guards stand there. The clans trade with everyone and trust no one.", {
	{"What is this place?", "about"},
	{"Where can I find work?", "work"},
	{"Goodbye.", "bye"},
})
screen(herald, "work", "Contract terminals stand on both sides of this avenue. There are more by the cantina door, for those who prefer quieter runs, and the smugglers' trainer drinks there too. In the bazaar, by the council palace, the Kessoth outfitter and the Vollaka broker keep stalls.", {
	{"What is this place?", "about"},
	{"Who runs the city?", "kajidics"},
	{"Goodbye.", "bye"},
})
screen(herald, "bye", "May your dealings profit you, and the council.", {}, true)
addConversationTemplate("hutta_council_herald_convo_template", herald)

-- the Kessoth outfitter, in the bazaar
local outfitter = convo("HuttaKessothOutfitterConvoHandler")
screen(outfitter, "greet", "A customer. Kessoth dresses its crews in its own colours, and for a fair price, so can you. No Hutt wears anything so small, of course.", {
	{"Show me what you sell.", "sale"},
	{"Goodbye.", "bye"},
})
screen(outfitter, "sale", "Take your time. Kessoth is patient with paying customers.", {}, true)
screen(outfitter, "bye", "Come back when you have credits.", {}, true)
addConversationTemplate("hutta_kessoth_outfitter_convo_template", outfitter)

-- the Vollaka broker, in the bazaar
local broker = convo("HuttaVollakaBrokerConvoHandler")
screen(broker, "greet", "Spice jars, lamps, small comforts for a Hutt's hall. Vollaka goods, honestly come by. Mostly.", {
	{"Show me your goods.", "sale"},
	{"Goodbye.", "bye"},
})
screen(broker, "sale", "Look all you like. Touching is extra.", {}, true)
screen(broker, "bye", "Vollaka remembers its customers.", {}, true)
addConversationTemplate("hutta_vollaka_broker_convo_template", broker)
