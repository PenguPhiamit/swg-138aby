"""O2b: the story-neutral server side of Ossus for Core3-dev: the planet entry (travel point at the Knossa pad),
ossus_regions.lua (edges, city, no-build over the ruins and caves, spawn areas, world spawner) and native fauna on
stock bodies (creature templates, lairs, spawn groups), plus new-files.txt and patches.tsv for apply.sh.
Our own code and text (Fable, 14 Oct 2026); names after the asset plan (gokob, tribis, kaddyr bug, kirruk; the mount
beast on the bol body), levels a PLACEHOLDER mid band 20-60 (owner question). No Ysanna, Imperials or Jedi.

    python -I stage_server.py       # writes ../staged/MMOCoreORB/bin/scripts/..., ../snippets/, ../new-files.txt,
                                    #   ../patches.tsv, ../out/server-report.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O2 = os.path.normpath(os.path.join(HERE, '..'))
OSSUS = os.path.normpath(os.path.join(O2, '..'))
STAGED = os.path.join(O2, 'staged', 'MMOCoreORB', 'bin', 'scripts')
SNIPPETS = os.path.join(O2, 'snippets')
OUT = os.path.join(O2, 'out')
SITES = os.path.join(OSSUS, 'out', 'ossus-sites.json')
HEADER = '-- Sandbox: Ossus (Fable batch O2, 14 Oct 2026; outputs/Fable-ossus/o2/README.md). Our own text; stock bodies and lair\n-- props referenced by name. Levels are a placeholder mid band (owner question).\n\n'

# ---------------------------------------------------------------- fauna (stock body -> our creature)
# (key, display name, stock body template, stock pet control device or '', level, mob type, diet, pvp, creature bits,
#  chanceHit, dmgMin, dmgMax, baseXp, ham, hamMax, armor, resists, meat, meatAmt, hide, hideAmt, bone, boneAmt, taming, attacks)
FAUNA = [
    ('ossus_gokob', 'a gokob', 'object/mobile/womp_rat_hue.iff', 'object/intangible/pet/womp_rat_hue.iff', 22, 'MOB_CARNIVORE', 'CARNIVORE',
     'ATTACKABLE', 'PACK + HERD', 0.34, 210, 220, 2100, 6000, 6900, 0, '{0,0,0,0,0,0,0,-1,-1}', 'meat_wild', 12, 'hide_leathery', 8, 'bone_mammal', 6, 0.25,
     '{ {"intimidationattack",""} }'),
    ('ossus_gokob_scavenger', 'a gokob scavenger', 'object/mobile/womp_rat_hue.iff', 'object/intangible/pet/womp_rat_hue.iff', 27, 'MOB_CARNIVORE', 'CARNIVORE',
     'AGGRESSIVE + ATTACKABLE + ENEMY', 'PACK + KILLER', 0.37, 250, 260, 2700, 7600, 8700, 0, '{0,0,0,0,0,0,0,-1,-1}', 'meat_wild', 14, 'hide_leathery', 10, 'bone_mammal', 7, 0.2,
     '{ {"intimidationattack",""}, {"posturedownattack",""} }'),
    ('ossus_tribis', 'a tribis', 'object/mobile/tybis_hue.iff', '', 28, 'MOB_HERBIVORE', 'HERBIVORE',
     'ATTACKABLE', 'PACK + HERD', 0.38, 255, 265, 2800, 8000, 9200, 0, '{10,10,10,10,10,10,10,10,-1}', 'meat_herbivore', 300, 'hide_bristley', 220, 'bone_mammal', 140, 0,
     '{ {"knockdownattack",""} }'),
    ('ossus_tribis_bull', 'a tribis bull', 'object/mobile/tybis_hue.iff', '', 34, 'MOB_HERBIVORE', 'HERBIVORE',
     'ATTACKABLE', 'PACK + HERD + KILLER', 0.42, 300, 320, 3500, 9800, 11200, 0, '{20,20,20,20,20,20,20,20,-1}', 'meat_herbivore', 360, 'hide_bristley', 260, 'bone_mammal', 170, 0,
     '{ {"knockdownattack",""}, {"intimidationattack",""} }'),
    ('ossus_kaddyr_bug', 'a kaddyr bug', 'object/mobile/kliknik_hue.iff', 'object/intangible/pet/kliknik_hue.iff', 32, 'MOB_CARNIVORE', 'CARNIVORE',
     'AGGRESSIVE + ATTACKABLE + ENEMY', 'PACK', 0.4, 290, 300, 3300, 9000, 10400, 0, '{120,5,5,-1,5,-1,5,-1,-1}', 'meat_insect', 10, 'hide_scaley', 8, '', 0, 0.2,
     '{ {"posturedownattack",""} }'),
    ('ossus_kaddyr_soldier', 'a kaddyr soldier', 'object/mobile/kliknik_hue.iff', 'object/intangible/pet/kliknik_hue.iff', 40, 'MOB_CARNIVORE', 'CARNIVORE',
     'AGGRESSIVE + ATTACKABLE + ENEMY', 'PACK + KILLER', 0.45, 340, 360, 4000, 10500, 12000, 1, '{130,15,15,-1,15,-1,15,-1,-1}', 'meat_insect', 14, 'hide_scaley', 10, '', 0, 0.15,
     '{ {"posturedownattack",""}, {"dizzyattack",""} }'),
    ('ossus_kirruk', 'a kirruk', 'object/mobile/gurreck_hue.iff', 'object/intangible/pet/gurreck_hue.iff', 48, 'MOB_CARNIVORE', 'CARNIVORE',
     'AGGRESSIVE + ATTACKABLE + ENEMY', 'PACK', 0.5, 390, 480, 4700, 10800, 12800, 1, '{130,130,-1,150,150,-1,150,-1,-1}', 'meat_carnivore', 80, 'hide_wooly', 50, '', 0, 0.2,
     '{ {"posturedownattack",""}, {"intimidationattack",""} }'),
    ('ossus_kirruk_alpha', 'a kirruk alpha', 'object/mobile/gurreck_hue.iff', 'object/intangible/pet/gurreck_hue.iff', 56, 'MOB_CARNIVORE', 'CARNIVORE',
     'AGGRESSIVE + ATTACKABLE + ENEMY', 'PACK + KILLER', 0.55, 450, 560, 5600, 12500, 14500, 1, '{140,140,-1,160,160,-1,160,-1,-1}', 'meat_carnivore', 95, 'hide_wooly', 60, '', 0, 0.15,
     '{ {"posturedownattack",""}, {"intimidationattack",""}, {"knockdownattack",""} }'),
    ('ossus_bol', 'an Ossus bol', 'object/mobile/bol_hue.iff', '', 30, 'MOB_HERBIVORE', 'HERBIVORE',
     'ATTACKABLE', 'PACK + HERD', 0.39, 262, 272, 2950, 8500, 10300, 0, '{135,20,-1,20,20,-1,20,-1,-1}', 'meat_herbivore', 185, 'hide_leathery', 300, 'bone_mammal', 185, 0.2,
     '{ {"knockdownattack",""}, {"intimidationattack",""} }'),
    ('ossus_bol_bull', 'an Ossus bol bull', 'object/mobile/bol_hue.iff', '', 36, 'MOB_HERBIVORE', 'HERBIVORE',
     'ATTACKABLE', 'PACK + HERD + KILLER', 0.43, 310, 330, 3700, 10200, 11800, 0, '{145,30,-1,30,30,-1,30,-1,-1}', 'meat_herbivore', 220, 'hide_leathery', 340, 'bone_mammal', 210, 0,
     '{ {"knockdownattack",""}, {"intimidationattack",""} }'),
]
HUES = {'womp_rat_hue': '{ 0, 1, 2, 3, 4, 5, 6, 7 }', 'tybis_hue': '{ 16, 17, 18, 19, 20, 21, 22, 23 }', 'kliknik_hue': '{ 0, 1, 2, 3, 4, 5, 6, 7 }',
        'gurreck_hue': '{ 24, 25, 26, 27, 28, 29, 30, 31 }', 'bol_hue': '{ 8, 9, 10, 11, 12, 13, 14, 15 }'}
SCALE = {'ossus_tribis_bull': 1.15, 'ossus_kirruk_alpha': 1.2, 'ossus_bol_bull': 1.1, 'ossus_kaddyr_soldier': 1.1, 'ossus_gokob_scavenger': 1.1}

LAIR_BASE = 'object/tangible/lair/base/'
# creature lairs (with a building) and dynamic groups (no building): name, mobiles, buildings, mission building
LAIRS = [
    ('ossus_gokob_den_neutral_medium', 'creature_lair', [('ossus_gokob', 3), ('ossus_gokob_scavenger', 1)], ['poi_all_lair_warren_large', 'poi_all_lair_mound_small'], None, 'Gokob Den'),
    ('ossus_tribis_lair_neutral_medium', 'creature_lair', [('ossus_tribis', 2), ('ossus_tribis_bull', 1)], ['poi_all_lair_mound_large', 'poi_all_lair_thicket_large'], None, 'Tribis Lair'),
    ('ossus_kaddyr_hive_neutral_medium', 'creature_lair', [('ossus_kaddyr_bug', 3), ('ossus_kaddyr_soldier', 1)], ['poi_all_lair_insecthill_large', 'poi_all_lair_insecthill_small'], None, 'Kaddyr Hive'),
    ('ossus_kirruk_den_neutral_large', 'creature_lair', [('ossus_kirruk', 2), ('ossus_kirruk_alpha', 1)], ['poi_all_lair_rock_shelter_large', 'poi_all_lair_bones_large'], None, 'Kirruk Den'),
    ('ossus_bol_lair_neutral_medium', 'creature_lair', [('ossus_bol', 2), ('ossus_bol_bull', 1)], ['poi_all_lair_rocks_large', 'poi_all_lair_rock_shelter_large'], None, 'Bol Lair'),
    ('ossus_gokob_pack_neutral_none', 'creature_dynamic', [('ossus_gokob', 4), ('ossus_gokob_scavenger', 1)], [], 'poi_all_lair_warren_large', 'Gokob Pack'),
    ('ossus_tribis_herd_neutral_none', 'creature_dynamic', [('ossus_tribis', 4), ('ossus_tribis_bull', 1)], [], 'poi_all_lair_mound_large', 'Tribis Herd'),
    ('ossus_kaddyr_swarm_neutral_none', 'creature_dynamic', [('ossus_kaddyr_bug', 4), ('ossus_kaddyr_soldier', 1)], [], 'poi_all_lair_insecthill_large', 'Kaddyr Swarm'),
    ('ossus_kirruk_pack_neutral_none', 'creature_dynamic', [('ossus_kirruk', 3), ('ossus_kirruk_alpha', 1)], [], 'poi_all_lair_rock_shelter_large', 'Kirruk Pack'),
    ('ossus_bol_herd_neutral_none', 'creature_dynamic', [('ossus_bol', 4), ('ossus_bol_bull', 1)], [], 'poi_all_lair_rocks_large', 'Bol Herd'),
]
# spawn groups: (name, [(lair, minDifficulty, maxDifficulty, numberToSpawn, weighting)])
GROUPS = {
    'ossus_plains': [('ossus_tribis_herd_neutral_none', 28, 500, 15, 40), ('ossus_tribis_lair_neutral_medium', 28, 500, 15, 20),
                     ('ossus_bol_herd_neutral_none', 30, 500, 15, 30), ('ossus_bol_lair_neutral_medium', 30, 500, 15, 15),
                     ('ossus_gokob_pack_neutral_none', 22, 500, 15, 30), ('ossus_gokob_den_neutral_medium', 22, 500, 15, 15)],
    'ossus_forest': [('ossus_kaddyr_swarm_neutral_none', 32, 500, 15, 35), ('ossus_kaddyr_hive_neutral_medium', 32, 500, 15, 20),
                     ('ossus_gokob_pack_neutral_none', 22, 500, 15, 25), ('ossus_tribis_lair_neutral_medium', 28, 500, 15, 20)],
    'ossus_highlands': [('ossus_kirruk_pack_neutral_none', 48, 500, 15, 35), ('ossus_kirruk_den_neutral_large', 48, 500, 15, 20),
                        ('ossus_kaddyr_swarm_neutral_none', 32, 500, 15, 20), ('ossus_bol_herd_neutral_none', 30, 500, 15, 25)],
    'ossus_canyon': [('ossus_kaddyr_hive_neutral_medium', 32, 500, 15, 30), ('ossus_kaddyr_swarm_neutral_none', 32, 500, 15, 30),
                     ('ossus_kirruk_pack_neutral_none', 48, 500, 15, 25), ('ossus_gokob_den_neutral_medium', 22, 500, 15, 15)],
    'ossus_world': [('ossus_gokob_pack_neutral_none', 22, 500, 15, 20), ('ossus_gokob_den_neutral_medium', 22, 500, 15, 10),
                    ('ossus_tribis_herd_neutral_none', 28, 500, 15, 20), ('ossus_tribis_lair_neutral_medium', 28, 500, 15, 10),
                    ('ossus_bol_herd_neutral_none', 30, 500, 15, 15), ('ossus_bol_lair_neutral_medium', 30, 500, 15, 8),
                    ('ossus_kaddyr_swarm_neutral_none', 32, 500, 15, 15), ('ossus_kaddyr_hive_neutral_medium', 32, 500, 15, 8),
                    ('ossus_kirruk_pack_neutral_none', 48, 500, 15, 8), ('ossus_kirruk_den_neutral_large', 48, 500, 15, 4)],
}
# spawn areas on the terrain (centre, radius, group, max), away from the pad (0,-3600), the benchland and the lake
AREAS = [
    ('ossus_plains_west', -4400, -1200, 1800, 'ossus_plains', 64),
    ('ossus_plains_north', -1500, 5200, 1700, 'ossus_plains', 64),
    ('ossus_forest_east', 1200, 5400, 1200, 'ossus_forest', 48),
    ('ossus_forest_southwest', -3200, -3400, 1000, 'ossus_forest', 48),
    ('ossus_highlands_south', 2600, -4300, 1500, 'ossus_highlands', 48),
    ('ossus_canyon_country', 5100, -100, 1600, 'ossus_canyon', 48),
]


def write(rel, text):
    path = os.path.join(STAGED, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return rel


def creature_lua(c):
    (key, name, body, pcd, level, mob, diet, pvp, bits, hit, dmin, dmax, xp, ham, hammax, armor, resists, meat, meatn, hide, hiden, bone, bonen, taming, attacks) = c
    hue = HUES[body.split('/')[-1][:-4]]
    lines = [HEADER.rstrip('\n'), '', '%s = Creature:new {' % key,
             '\tobjectName = "",', '\tcustomName = "%s",' % name, '\tsocialGroup = "%s",' % key.split('_')[1], '\tfaction = "",',
             '\tmobType = %s,' % mob, '\tlevel = %d,' % level, '\tchanceHit = %s,' % hit, '\tdamageMin = %d,' % dmin, '\tdamageMax = %d,' % dmax,
             '\tbaseXp = %d,' % xp, '\tbaseHAM = %d,' % ham, '\tbaseHAMmax = %d,' % hammax, '\tarmor = %d,' % armor, '\tresists = %s,' % resists,
             '\tmeatType = "%s",' % meat, '\tmeatAmount = %d,' % meatn, '\thideType = "%s",' % hide, '\thideAmount = %d,' % hiden,
             '\tboneType = "%s",' % bone, '\tboneAmount = %d,' % bonen, '\tmilk = 0,', '\ttamingChance = %s,' % taming, '\tferocity = 0,',
             '\tpvpBitmask = %s,' % pvp, '\tcreatureBitmask = %s,' % bits, '\toptionsBitmask = AIENABLED,', '\tdiet = %s,' % diet,
             '\ttemplates = {"%s"},' % body, '\thues = %s,' % hue]
    if pcd:
        lines.append('\tcontrolDeviceTemplate = "%s",' % pcd)
    if key in SCALE:
        lines.append('\tscale = %s,' % SCALE[key])
    lines += ['\tlootGroups = {},', '\tprimaryWeapon = "unarmed",', '\tsecondaryWeapon = "none",', '\tconversationTemplate = "",',
              '\tprimaryAttacks = %s,' % attacks, '\tsecondaryAttacks = { }', '}', '', 'CreatureTemplates:addCreatureTemplate(%s, "%s")' % (key, key), '']
    return '\n'.join(lines)


def lair_lua(l):
    name, kind, mobiles, buildings, mission, custom = l
    mobs = ', '.join('{"%s", %d}' % m for m in mobiles)
    blds = ', '.join('"%s%s.iff"' % (LAIR_BASE, b) for b in buildings)
    lines = [HEADER.rstrip('\n'), '', '%s = Lair:new {' % name, '\tmobiles = {%s},' % mobs, '\tspawnLimit = 15,']
    for tier in ('VeryEasy', 'Easy', 'Medium', 'Hard', 'VeryHard'):
        lines.append('\tbuildings%s = {%s},' % (tier, blds))
    lines.append('\tcustomName = "%s"%s' % (custom, ',' if mission else ''))
    if mission:
        lines.append('\tmissionBuilding = "%s%s.iff",' % (LAIR_BASE, mission))
        lines.append('\tbuildingType = "none"')
    lines += ['}', '', 'addLairTemplate("%s", %s)' % (name, name), '']
    return '\n'.join(lines)


def group_lua(name, entries):
    lines = [HEADER.rstrip('\n'), '', '%s = {' % name, '\tlairSpawns = {']
    for lair, mn, mx, num, weight in entries:
        lines += ['\t\t{', '\t\t\tlairTemplateName = "%s",' % lair, '\t\t\tspawnLimit = -1,', '\t\t\tminDifficulty = %d,' % mn,
                  '\t\t\tmaxDifficulty = %d,' % mx, '\t\t\tnumberToSpawn = %d,' % num, '\t\t\tweighting = %d,' % weight, '\t\t\tsize = 25,', '\t\t},']
    lines += ['\t}', '}', '', 'addSpawnGroup("%s", %s);' % (name, name), '']
    return '\n'.join(lines)


def regions_lua(sites):
    pad, ruins, caves = sites['starport_pad'], sites['academy_ruins'], sites['caves']
    lines = ['require("scripts.managers.planet.regions")', '',
             '-- Sandbox: Ossus regions (Fable batch O2, 14 Oct 2026). Sites from outputs/Fable-ossus/out/ossus-sites.json (the terrain',
             '-- survey): Knossa pad, the Academy ruins pad, three cave mouths; spawn areas on flat ground off the pad, the benchland and',
             '-- the lake. Groups are in mobile/spawn/ossus/. Region name keys are in string/en/ossus_region_names.stf (batch O1).',
             'ossus_regions = {', '\t-- No Build Zones',
             '\t{"northedge_ossus_nobuild", -8000, 7640, {RECTANGLE, 8000, 8000}, NOSPAWNAREA + NOBUILDZONEAREA},',
             '\t{"westedge_ossus_nobuild", -8000, -7640, {RECTANGLE, -7640, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},',
             '\t{"southedge_ossus_nobuild", -8000, -8000, {RECTANGLE, 8000, -7640}, NOSPAWNAREA + NOBUILDZONEAREA},',
             '\t{"eastedge_ossus_nobuild", 7640, -7640, {RECTANGLE, 7999, 7640}, NOSPAWNAREA + NOBUILDZONEAREA},', '',
             '\t-- Knossa (the starport on the flattened pad)',
             '\t{"@ossus_region_names:knossa", %d, %d, {CIRCLE, 200}, CITY + NOSPAWNAREA},' % (pad['x'], pad['y']),
             '\t{"ossus_knossa_nobuild", %d, %d, {CIRCLE, 320}, NOBUILDZONEAREA},' % (pad['x'], pad['y']), '',
             '\t-- The Academy ruins (snapshot/ossus.ws) and the cave mouths',
             '\t{"ossus_academy_ruins_nobuild", %d, %d, {CIRCLE, 260}, NOSPAWNAREA + NOBUILDZONEAREA},' % (ruins['x'], ruins['y'])]
    for c in caves:
        lines.append('\t{"ossus_%s_nobuild", %d, %d, {CIRCLE, 120}, NOBUILDZONEAREA},' % (c['name'], c['x'], c['y']))
    lines += ['', '\t-- Area spawners (placeholder level band 20-60; owner question)']
    for name, x, y, r, group, mx in AREAS:
        lines.append('\t{"%s", %d, %d, {CIRCLE, %d}, SPAWNAREA, {"%s"}, %d},' % (name, x, y, r, group, mx))
    lines += ['', '\t-- World spawner: everything else, outside the no-spawn areas',
              '\t{"ossus_world_spawner", 0, 0, {RECTANGLE, 0, 0}, SPAWNAREA + WORLDSPAWNAREA, {"ossus_world"}, 1024},', '}', '']
    return '\n'.join(lines)


def planet_block(sites):
    pad = sites['starport_pad']
    tx, ty = round(pad['x'] + 20.3, 1), round(pad['y'] + 17.8, 1)
    return '\n'.join([
        'ossus = {',
        '\t-- Sandbox: Ossus (Fable batches O1/O2, 14 Oct 2026; outputs/Fable-ossus/). Our own terrain (terrain/ossus.trn) and',
        '\t-- snapshot (snapshot/ossus.ws) in local_planets.tre; the Knossa starport sits on the flattened pad at %d %d (%.1f m).' % (pad['x'], pad['y'], pad['height']),
        '\t-- Reached from Corellia (datatables/travel/travel.iff, placeholder fare).',
        '\tweatherEnabled = 1,', '\tgcwEnabled = 1,', '',
        '\tplanetTravelPoints = {',
        '\t\t-- the outpost_starport landing pad: the same offset from the building as Hoth and Yavin IV (yaw 180)',
        '\t\t{name = "Knossa", x = %.1f, z = %.1f, y = %.1f, interplanetaryTravelAllowed = 1, incomingTravelAllowed = 1, landingRange = 3},' % (tx, pad['height'], ty),
        '\t},', '', '\tbadgeAreas = {', '\t},', '', '\tnavAreas = {', '\t\t{"ossus_knossa", %d, %d, 150},' % (pad['x'], pad['y']), '\t},', '',
        '\tplanetObjects = {', '\t}', '}', ''])


def main():
    with open(SITES, encoding='utf-8') as f:
        sites = json.load(f)
    new_files = []
    # creatures
    inc = [HEADER.rstrip('\n'), '']
    for c in FAUNA:
        new_files.append(write('mobile/ossus/%s.lua' % c[0], creature_lua(c)))
        inc.append('includeFile("ossus/%s.lua")' % c[0])
    new_files.append(write('mobile/ossus/serverobjects.lua', '\n'.join(inc) + '\n'))
    # lairs
    for l in LAIRS:
        new_files.append(write('mobile/lair/%s/ossus/%s.lua' % (l[1], l[0]), lair_lua(l)))
    # spawn groups
    for name, entries in GROUPS.items():
        new_files.append(write('mobile/spawn/ossus/%s.lua' % name, group_lua(name, entries)))
    # regions
    new_files.append(write('managers/planet/ossus_regions.lua', regions_lua(sites)))
    # planet block snippet
    os.makedirs(SNIPPETS, exist_ok=True)
    with open(os.path.join(SNIPPETS, 'planet_manager_ossus.lua'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(planet_block(sites))
    with open(os.path.join(O2, 'new-files.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# new files under MMOCoreORB/bin/scripts (copied by apply.sh; refused if a different file exists)\n' + '\n'.join(new_files) + '\n')
    patches = [
        ('mobile/serverobjects.lua', 'after', 'includeFile("hoth/serverobjects.lua") -- Sandbox: Hoth creatures (Bellum Gero, AGPL-3.0)',
         'includeFile("ossus/serverobjects.lua") -- Sandbox: Ossus fauna (Fable batch O2)'),
        ('mobile/lair/creature_lair/serverobjects.lua', 'after', 'includeFile("lair/creature_lair/hoth/hoth_wampa_lair_neutral_large.lua")',
         'includeFile("lair/creature_lair/ossus/serverobjects.lua") -- Sandbox: Ossus lairs (Fable batch O2)'),
        ('mobile/lair/creature_dynamic/serverobjects.lua', 'after', 'includeFile("lair/creature_dynamic/hoth/hoth_wampa_neutral_none.lua")',
         'includeFile("lair/creature_dynamic/ossus/serverobjects.lua") -- Sandbox: Ossus herds and packs (Fable batch O2)'),
        ('mobile/spawn/serverobjects.lua', 'after', 'includeFile("spawn/hoth/hoth_scavenger_zone.lua")',
         'includeFile("spawn/ossus/serverobjects.lua") -- Sandbox: Ossus spawn groups (Fable batch O2)'),
        ('managers/planet/planet_manager.lua', 'before-file', 'tutorial = {', 'snippets/planet_manager_ossus.lua'),
    ]
    # one include list per lair kind and for the spawn groups, so each list file takes a single patched line
    for kind in ('creature_lair', 'creature_dynamic'):
        names = [l[0] for l in LAIRS if l[1] == kind]
        new_files.append(write('mobile/lair/%s/ossus/serverobjects.lua' % kind, HEADER + '\n'.join('includeFile("lair/%s/ossus/%s.lua")' % (kind, n) for n in names) + '\n'))
    new_files.append(write('mobile/spawn/ossus/serverobjects.lua', HEADER + '\n'.join('includeFile("spawn/ossus/%s.lua")' % n for n in GROUPS) + '\n'))
    with open(os.path.join(O2, 'new-files.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# new files under MMOCoreORB/bin/scripts (copied by apply.sh; refused if a different file exists)\n' + '\n'.join(new_files) + '\n')
    with open(os.path.join(O2, 'patches.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# <file under MMOCoreORB/bin/scripts>\t<after|before|before-file|append>\t<anchor line | marker>\t<new line | snippet>; \\t = tab, \\\\ = backslash\n')
        for p in patches:
            f.write('\t'.join(p) + '\n')
    rep = {'new_files': new_files, 'patches': [dict(zip(('file', 'mode', 'anchor', 'new'), p)) for p in patches],
           'fauna': [{'key': c[0], 'name': c[1], 'body': c[2], 'level': c[4]} for c in FAUNA],
           'lairs': [{'name': l[0], 'kind': l[1], 'mobiles': l[2], 'buildings': l[3], 'mission_building': l[4]} for l in LAIRS],
           'spawn_groups': {k: [e[0] for e in v] for k, v in GROUPS.items()}, 'spawn_areas': AREAS,
           'stock_bodies': sorted(set(c[2] for c in FAUNA)), 'stock_pcds': sorted(set(c[3] for c in FAUNA if c[3])),
           'lair_props': sorted(set(LAIR_BASE + b + '.iff' for l in LAIRS for b in l[3] + ([l[4]] if l[4] else []))),
           'travel_point': planet_block(sites).split('name = "Knossa"')[1].split('}')[0]}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'server-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    print(len(new_files), 'new files,', len(patches), 'patches;', len(FAUNA), 'creatures,', len(LAIRS), 'lairs,', len(GROUPS), 'groups,', len(AREAS), 'spawn areas')
    return 0


if __name__ == '__main__':
    sys.exit(main())
