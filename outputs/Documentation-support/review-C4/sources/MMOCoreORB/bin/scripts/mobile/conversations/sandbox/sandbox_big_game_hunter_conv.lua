sandbox_big_game_hunter_convo_template = ConvoTemplate:new {
	initialScreen = "greet",
	templateType = "Lua",
	luaClassHandler = "SandboxBigGameHunterConvoHandler",
	screens = {}
}

hunter_greet = ConvoScreen:new {
	id = "greet",
	customDialogText = "Rhea Tannor, tracker. The big ones come and go across the systems. Kill one and every blaster that drew blood gets paid.",
	stopConversation = "false",
	options = {
		{"What's out there right now?", "report"},
		{"How does the bounty work?", "rules"},
		{"Maybe later.", "bye"},
	}
}
sandbox_big_game_hunter_convo_template:addScreen(hunter_greet)

hunter_report = ConvoScreen:new {
	id = "report",
	customDialogText = "(filled in by the screenplay)",
	stopConversation = "true",
	options = {}
}
sandbox_big_game_hunter_convo_template:addScreen(hunter_report)

hunter_rules = ConvoScreen:new {
	id = "rules",
	customDialogText = "Three beasts roam at a time. If nobody brings one down within a few hours, it moves on and another shows up somewhere else. Everyone who wounds a beast before it falls is paid 25,000 credits into their bank account.",
	stopConversation = "false",
	options = {
		{"What's out there right now?", "report"},
		{"Thanks.", "bye"},
	}
}
sandbox_big_game_hunter_convo_template:addScreen(hunter_rules)

hunter_bye = ConvoScreen:new {
	id = "bye",
	customDialogText = "Good hunting.",
	stopConversation = "true",
	options = {}
}
sandbox_big_game_hunter_convo_template:addScreen(hunter_bye)

addConversationTemplate("sandbox_big_game_hunter_convo_template", sandbox_big_game_hunter_convo_template)
