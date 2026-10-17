"""PL-05 Hoth leftovers, server half (Claude, 17 Oct 2026). Edits a scratch copy of Core3-dev's scripts.

    python -I stage_server.py <scratch root holding MMOCoreORB/bin/scripts copies of the dev files>

Each edit replaces an anchor that must occur exactly once, so a moved dev file stops the step instead of patching
the wrong place. The patch in ../hoth-leftovers.patch is `git diff` of the result. Owner's answers: SWG-handoff.md,
"Owner's answers, 15 Oct 15:30-16:10", Q4, and the 14 Oct set, question 9 (the ice-cave den, option 1).
"""
import os
import sys

ROOT = os.path.join(sys.argv[1], 'MMOCoreORB', 'bin', 'scripts')
BADGE = 141  # next free index after Ossus's 140; the client step stops if the archive already uses it


def edit(rel, pairs):
    path = os.path.join(ROOT, rel)
    text = open(path, encoding='utf-8', newline='').read()
    for old, new in pairs:
        assert text.count(old) == 1, (rel, old[:60], text.count(old))
        text = text.replace(old, new)
    open(path, 'w', encoding='utf-8', newline='').write(text)


def new(rel, text):
    path = os.path.join(ROOT, rel)
    assert not os.path.exists(path), rel
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8', newline='').write(text)


HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))

# 1. The mynock den: Fable's staged screenplay (batch B2, option 1, the stock ice cave), unchanged.
den = open(os.path.join(OUTPUTS, 'Fable-hoth-batchB', 'staged', 'MMOCoreORB', 'bin', 'scripts', 'screenplays', 'poi',
                        'hoth_mynock_den.lua'), encoding='utf-8', newline='').read()
new('screenplays/poi/hoth_mynock_den.lua', den)

# 2. The glacial rancor's den: one fixed spawn with a respawn timer at the Glacial Rancor Grounds.
new('screenplays/poi/hoth_glacial_rancor_den.lua', '''-- Hoarfang's den: the glacial rancor in one fixed place with a respawn timer (owner, 15 Oct, Hoth Q4).
-- Site: the Glacial Rancor Grounds, a flat glacial valley south of the outpost (outputs/Fable-hoth-mapnames/sites.tsv,
-- ground 11-28 m within 100 m; terrain height 26.4 m at the spawn point). The owner picks the final site; see
-- outputs/Hoth-leftovers/LEFTOVERS-INSTALL.md. Respawn 1800 s, as the Hoth cave bosses. Claude, 17 Oct 2026.

HothGlacialRancorDenScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothGlacialRancorDenScreenPlay",

	x = 600, z = 26.4, y = -4600, heading = 180,
	respawn = 1800,
}

registerScreenPlay("HothGlacialRancorDenScreenPlay", true)

function HothGlacialRancorDenScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		spawnMobile("hoth", "hoth_glacial_rancor", self.respawn, self.x, self.z, self.y, self.heading, 0)
	end
end
''')

edit('screenplays/screenplays.lua', [(
    'includeFile("poi/hoth_camps.lua") -- Sandbox: Hoth camps (Fable batch B)\n',
    'includeFile("poi/hoth_camps.lua") -- Sandbox: Hoth camps (Fable batch B)\n'
    'includeFile("poi/hoth_glacial_rancor_den.lua") -- Sandbox: Hoth glacial rancor den (PL-05)\n'
    'includeFile("poi/hoth_mynock_den.lua") -- Sandbox: Hoth mynock den, the stock ice cave (Fable batch B2, PL-05)\n')])

# 3. Pale blue rancor: our client chain rancor_ice (the stock rancor_hue meshes and texture, its shaders bound to the
#    Chiss skin palette, palette/npc_chiss_skin.pal). Hue 5 = RGB (0, 128, 182), the palette's lightest entry.
edit('mobile/hoth/hoth_glacial_rancor.lua', [
    ('-- Not wired to any spawn yet: see the README for the three options.\n',
     '-- Spawned by screenplays/poi/hoth_glacial_rancor_den.lua (PL-05). Colour (owner, 15 Oct): pale blue from the Chiss\n'
     '-- skin palette, through our rancor_ice chain in local_planets.tre (outputs/Hoth-leftovers).\n'),
    ('\ttemplates = {"object/mobile/rancor_hue.iff"},  -- the hue-capable body; plain rancor.iff ignores hues (C22-F2)\n'
     '\thues = { 15 },\n',
     '\ttemplates = {"object/mobile/rancor_ice.iff"},  -- rancor_hue\'s body, shaders on palette/npc_chiss_skin.pal (8 entries)\n'
     '\thues = { 5 },\n')])

new('object/mobile/rancor_ice.lua', '''-- The glacial rancor's body: the stock rancor_hue meshes with shaders bound to the Chiss skin palette.
-- Client chain built by outputs/Hoth-leftovers/build_hoth_leftovers.py into local_planets.tre. Claude, 17 Oct 2026.

object_mobile_rancor_ice = object_mobile_shared_rancor_ice:new {

}

ObjectTemplates:addTemplate(object_mobile_rancor_ice, "object/mobile/rancor_ice.iff")
''')

edit('object/mobile/serverobjects.lua', [(
    'includeFile("mobile/rancor_hue.lua")\n',
    'includeFile("mobile/rancor_hue.lua")\nincludeFile("mobile/rancor_ice.lua")\n')])

edit('object/mobile/objects.lua', [(
    'ObjectTemplates:addClientTemplate(object_mobile_shared_rancor_hue, "object/mobile/shared_rancor_hue.iff")\n',
    'ObjectTemplates:addClientTemplate(object_mobile_shared_rancor_hue, "object/mobile/shared_rancor_hue.iff")\n\n'
    '-- Sandbox (PL-05): the glacial rancor body, ours, in local_planets.tre (rancor_hue with the Chiss skin palette).\n'
    'object_mobile_shared_rancor_ice = SharedCreatureObjectTemplate:new {\n'
    '\tclientTemplateFileName = "object/mobile/shared_rancor_ice.iff"\n'
    '}\n\n'
    'ObjectTemplates:addClientTemplate(object_mobile_shared_rancor_ice, "object/mobile/shared_rancor_ice.iff")\n')])

# 4. The quest chain's last job also gives a badge and a rare-decor roll.
edit('screenplays/tasks/hoth/scavenger_quartermaster.lua', [(
    '\t\t\t{ rewardType = "credits", amount = 2000 }\n',
    '\t\t\t{ rewardType = "credits", amount = 2000 },\n'
    '\t\t\t{ rewardType = "loot", lootGroup = "hoth_decor_rare" },\n'
    '\t\t\t{ rewardType = "badge", badge = %d }  -- bdg_thm_park_hoth_salvage, datatables/badge/badge_map.iff (PL-05)\n' % BADGE)])

# 5. Recruiters at the starport only; artisan and entertainer terminals at the starport.
edit('screenplays/poi/hoth_camps.lua', [
    ('\tspawnMobile("hoth", "imperial_recruiter", 60, 2596, 33.5, -3896, -45, 0)\n', ''),
    ('\tspawnMobile("hoth", "rebel_recruiter", 60, -2804, 23, 1196, 45, 0)\n', '')])

edit('screenplays/poi/hoth_outpost_terminals.lua', [
    ('\tif (isZoneEnabled("hoth")) then\n\t\tself:spawnSceneObjects()\n\tend\n',
     '\tif (isZoneEnabled("hoth")) then\n\t\tself:spawnSceneObjects()\n\t\tself:spawnMobiles()\n\tend\n'),
    ('\tspawnSceneObject("hoth", "object/tangible/terminal/terminal_mission.iff", 48.0, 0.0, -2002.0, 0, math.rad(-90))\nend\n',
     '\tspawnSceneObject("hoth", "object/tangible/terminal/terminal_mission.iff", 48.0, 0.0, -2002.0, 0, math.rad(-90))\n'
     '\t-- PL-05 (owner, 15 Oct): artisan and entertainer terminals at the starport, in the same row.\n'
     '\tspawnSceneObject("hoth", "object/tangible/terminal/terminal_mission_artisan.iff", 48.0, 0.0, -1990.0, 0, math.rad(-90))\n'
     '\tspawnSceneObject("hoth", "object/tangible/terminal/terminal_mission_entertainer.iff", 48.0, 0.0, -1984.0, 0, math.rad(-90))\n'
     'end\n\n'
     '-- PL-05 (owner, 15 Oct): recruiters at the starport only (they stood at the forward camps before).\n'
     'function HothOutpostTerminalsScreenPlay:spawnMobiles()\n'
     '\tspawnMobile("hoth", "imperial_recruiter", 60, 54.0, 0.0, -2016.0, -90, 0)\n'
     '\tspawnMobile("hoth", "rebel_recruiter", 60, 54.0, 0.0, -1980.0, -90, 0)\n'
     'end\n')])

# 6. Delivery points at the camps: the three peaceable camps become mission "cities" with three neutral spawn points
#    each, so general deliver missions from the starport can end at a camp (MissionManager picks another city's
#    centre, then a point within 1500 m of it). The raiders' camp and the contested ground are fights, so not used.
edit('managers/mission/mission_cities.lua', [(
    '\t{ "hoth", "Scavenger Starport", 0, -2000, 150 },\n',
    '\t{ "hoth", "Scavenger Starport", 0, -2000, 150 },\n'
    '\t{ "hoth", "Imperial Forward Camp", 2600, -3900, 80 },\n'
    '\t{ "hoth", "Rebel Forward Camp", -2800, 1200, 80 },\n'
    '\t{ "hoth", "Scavengers\' Camp", -1400, -3300, 80 },\n')])

edit('managers/mission/mission_npc_spawn_points.lua', [(
    '\t\t{ -140.0, -1990.0, 0.3, 2 }\n\t}\n}\n\nuniverse:addPlanet(planet_hoth);',
    '\t\t{ -140.0, -1990.0, 0.3, 2 },\n'
    '\t\t{ 2630.0, -3900.0, 4.7, 2 },\n'
    '\t\t{ 2600.0, -3870.0, 3.1, 2 },\n'
    '\t\t{ 2570.0, -3900.0, 1.6, 2 },\n'
    '\t\t{ -2770.0, 1200.0, 4.7, 2 },\n'
    '\t\t{ -2800.0, 1235.0, 3.1, 2 },\n'
    '\t\t{ -2830.0, 1205.0, 1.6, 2 },\n'
    '\t\t{ -1370.0, -3300.0, 4.7, 2 },\n'
    '\t\t{ -1400.0, -3270.0, 3.1, 2 },\n'
    '\t\t{ -1425.0, -3320.0, 1.6, 2 }\n'
    '\t}\n}\n\nuniverse:addPlanet(planet_hoth);')])

# 7. Map names for the two dens (the held rows of Fable's sites.tsv) and a no-spawn circle over the mynock cave so
#    the mynock-fields lairs do not land on its mouth.
edit('managers/planet/hoth_regions.lua', [(
    '\t{"@hoth_region_names:scavenger_zone", -1500, -3200, {CIRCLE, 900}, NAMEDREGION},\n',
    '\t{"@hoth_region_names:scavenger_zone", -1500, -3200, {CIRCLE, 900}, NAMEDREGION},\n'
    '\t-- The dens (PL-05, 17 Oct 2026): the mynock ice cave and the glacial rancor\'s grounds.\n'
    '\t{"@hoth_region_names:mynock_den", -2000, -4800, {CIRCLE, 60}, NAMEDREGION},\n'
    '\t{"@hoth_region_names:rancor_grounds", 600, -4600, {CIRCLE, 200}, NAMEDREGION},\n'
    '\t{"hoth_mynock_den_nospawn", -2000, -4800, {CIRCLE, 160}, NOSPAWNAREA},\n')])

print('server edits: OK')
