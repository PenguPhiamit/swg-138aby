-- Ossus world (O8): conversations of four townsfolk. Our own text; no state, so one plain handler serves them all.

local function convo()
	return ConvoTemplate:new {
		initialScreen = "greet",
		templateType = "Lua",
		luaClassHandler = "OssusWorldConvoHandler",
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

-- Knossa: Sister Anwe, a pilgrim
local pilgrim = convo()
screen(pilgrim, "greet", "I came to walk the road to the academy, as my teacher did before the Sith burned it. The stones are still standing. That is something.", {
	{"Where does the road start?", "road"},
	{"Goodbye.", "bye"},
})
screen(pilgrim, "road", "Just north of the landing field. Follow the stones to the benchland. The archivist at the vault dig knows more than I do, and the garrison lets pilgrims pass if they keep their eyes down.", {}, true)
screen(pilgrim, "bye", "Walk in peace.", {}, true)
addConversationTemplate("ossus_knossa_pilgrim_convo_template", pilgrim)

-- Knossa: Rab Okkon, a settler
local settler = convo()
screen(settler, "greet", "We came out after the fighting stopped. Good soil in the fields east of town, if you can keep the tribis off the crops. Nobody else wanted the land, so now it's ours.", {
	{"Is it safe out there?", "safe"},
	{"Goodbye.", "bye"},
})
screen(settler, "safe", "Safer than it was. The beasts mostly leave you alone. It's the people you watch: scavengers picking over the old battle sites, poachers on the mesa, and something in the west foothill cave that the garrison won't talk about.", {}, true)
screen(settler, "bye", "Mind how you go.", {}, true)
addConversationTemplate("ossus_knossa_settler_convo_template", settler)

-- the hermit's hollow
local hermit = convo()
screen(hermit, "greet", "Visitors. Twice in one year. The galaxy must be getting smaller.", {
	{"Why do you live out here?", "why"},
	{"Goodbye.", "bye"},
})
screen(hermit, "why", "I kept the academy's gardens, long ago. When the ships came I ran, and I kept running until the noise stopped. Some of the others went underground. I hear them sometimes, in the quiet. Don't go looking for them. They will find you if they want to.", {}, true)
screen(hermit, "bye", "Go on, then.", {}, true)
addConversationTemplate("ossus_hollow_hermit_convo_template", hermit)

-- the deserters' camp
local deserter = convo()
screen(deserter, "greet", "Keep your voice down. If the major's patrols find this camp, we're all shot. We walked out of the garrison when word came that Krayt was dead. Nobody gives orders for a dead Emperor.", {
	{"What is in the west foothill cave?", "cave"},
	{"Goodbye.", "bye"},
})
screen(deserter, "cave", "The old interrogation post. We used to run prisoners through it. Now there are people in black robes down there, guarding things they took from the academy. Their leader calls himself the Keeper. Go armed, and go with friends.", {}, true)
screen(deserter, "bye", "You never saw us.", {}, true)
addConversationTemplate("ossus_deserter_convo_template", deserter)
