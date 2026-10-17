-- Hoth fill: load the new files with stand-ins for the Core3 globals they use, and call each table builder, to catch
-- errors luac -p can't (an unknown global, a wrong field). Not the server: run_check.sh in INSTALL.md is the real check.
local S = arg[1]
local mt = {__index = function(t, k) return k end}
setmetatable(_G, {__index = function(_, k)
	if k:match("^[A-Z_]+$") then return 1 end   -- bitmask constants
	error("unknown global " .. k, 2)
end})
local function new(self, t) return t end
Creature = {new = new}; Lair = {new = new}; ConvoTemplate = {new = function(_, t) t.addScreen = function(self, s) table.insert(self.screens, s) end return t end}
ConvoScreen = {new = new}; ScreenPlay = {new = new}
creatures, lairs, groups, convs, sps = {}, {}, {}, {}, {}
CreatureTemplates = {addCreatureTemplate = function(_, t, n) creatures[n] = t end}
function addLairTemplate(n, t) lairs[n] = t end
function addSpawnGroup(n, t) groups[n] = t end
function addConversationTemplate(n, t) convs[n] = t end
function registerScreenPlay(n) sps[n] = true end
function merge(...) local r = {} for _, a in ipairs({...}) do for _, x in ipairs(a) do table.insert(r, x) end end return r end
brawlermaster, marksmanmaster, pistoleermaster = {{"a",""}}, {{"b",""}}, {{"c",""}}
conv_handler = {new = function(self, t) return setmetatable(t, {__index = self}) end}
for _, f in ipairs({"mobile/hoth/hoth_fill_creatures.lua", "mobile/sandbox/hoth_world.lua", "mobile/lair/creature_dynamic/hoth/hoth_fill_lairs.lua",
	"mobile/spawn/hoth/hoth_fill_areas.lua", "mobile/conversations/sandbox/hoth_world_conv.lua", "screenplays/sandbox/hoth_world.lua",
	"screenplays/poi/hoth_echo_base.lua", "screenplays/poi/hoth_glacial_rancor_den.lua"}) do
	assert(loadfile(S .. "/" .. f))()
end
local n = 0 for _ in pairs(creatures) do n = n + 1 end
print("creatures " .. n)
-- every mobile a place, the townsfolk or Echo Base names must be one of ours or a known stock/hoth template
local known = {}
for k in pairs(creatures) do known[k] = true end
for _, k in ipairs({"commoner", "commoner_old", "commoner_naboo", "nomad", "artisan", "hoth_ice_mynock", "hoth_greater_ice_mynock",
	"hoth_wampa", "hoth_elder_wampa", "hoth_probe_droid", "hoth_tauntaun_herd_neutral_none", "hoth_wampa_neutral_none", "hoth_wampa_lair_neutral_large"}) do known[k] = true end
for k in pairs(lairs) do known[k] = true end
local function want(n) assert(known[n], "unknown template " .. n) end
for _, p in ipairs(HothWorld.townsfolk) do want(p[1]) end
for _, pl in ipairs(HothWorld.places) do for _, p in ipairs(pl.people) do want(p[1]) end if pl.job then want(pl.job.template) end end
for _, s in ipairs(HothEchoBaseScreenPlay.interior) do want(s[2]) assert(s[1] >= 1 and s[1] <= 40) end
want(HothEchoBaseScreenPlay.baron[2])
for _, l in pairs(lairs) do for _, m in ipairs(l.mobiles) do want(m[1]) end end
for _, g in pairs(groups) do for _, l in ipairs(g.lairSpawns) do want(l.lairTemplateName) end end
-- every talker's conversation exists, and every screen an option links to exists
for name, c in pairs(creatures) do
	if c.conversationTemplate ~= "" then
		local conv = assert(convs[c.conversationTemplate], "no conversation " .. c.conversationTemplate)
		local ids = {} for _, s in ipairs(conv.screens) do ids[s.id] = true end
		for _, s in ipairs(conv.screens) do for _, o in ipairs(s.options) do assert(ids[o[2]], name .. ": no screen " .. o[2]) end end
		assert(_G[conv.luaClassHandler] or rawget(_G, conv.luaClassHandler), "no handler " .. conv.luaClassHandler)
	end
end
print("lairs, groups, places, Echo Base and conversations: ok")
