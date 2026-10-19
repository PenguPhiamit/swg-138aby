"""Stage the server half of the light whip (L1 step 1, Claude, 18 Oct 2026) as a patch for Core3-dev. Writes nothing
under /opt/swg: it copies the touched files from the dev tree's HEAD into a scratch git repo under /tmp, edits them there
(every edit asserts its anchor), and writes lightwhip-dev.patch next to this script.

    wsl -d Debian -u swgemu -- python3 make_lightwhip_patch.py      (then: git -C /opt/swg/Core3-dev apply --check <patch>)

What the patch does (Lua only, no C++ build; the client templates are in the L1 archive, which the server reads too):
  object/weapon/melee/sword/crafted_saber/sword_lightwhip.lua      new: the s5 gen4 one-handed saber renamed, with more
        reach (ideal range 3 -> 5 m, max 5 -> 7 m; the saber specials use the weapon's range) and armour piercing
        MEDIUM -> LIGHT (weaker against armour). Gen4 certification and crafting ranges stay.
  object/draft_schematic/weapon/lightsaber/lightsaber_lightwhip.lua   new: the gen4 one-handed saber schematic, making
        the whip (same skills, ingredients and experimentation), listed in managers/crafting/schematics.lua
  object/tangible/loot/loot_schematic/lightwhip_schematic.lua       new: teaches that schematic for 3 crafts to a Jedi
        with force_discipline_light_saber_master (the skill that grants the gen4 saber schematics)
  loot/items/lightwhip/lightwhip.lua, lightwhip_schematic.lua        new loot items (the whip: fixed mid-range gen4 stats)
  loot/groups/lightwhip/lightwhip_nightsister.lua                   new group: schematic 80%, finished whip 20%. Not on
        any creature yet: the Nightsister placement is step 4.
  plus the shared-template blocks in each objects.lua and the include lines.
Not in this patch: weaker blocking and the parry slip (both need C++, step 2).
"""
import os
import re
import shutil
import subprocess

DEV = '/opt/swg/Core3-dev'
S = 'MMOCoreORB/bin/scripts/'
STAGE = '/tmp/lightwhip-stage'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lightwhip-dev.patch')

SABER_DIR = S + 'object/weapon/melee/sword/crafted_saber/'
SABER_OBJECTS = SABER_DIR + 'objects.lua'
SABER_SERVEROBJECTS = SABER_DIR + 'serverobjects.lua'
S5 = SABER_DIR + 'sword_lightsaber_one_handed_s5_gen4.lua'
WHIP = SABER_DIR + 'sword_lightwhip.lua'

DS_DIR = S + 'object/draft_schematic/weapon/lightsaber/'
DS_OBJECTS = DS_DIR + 'objects.lua'
DS_SERVEROBJECTS = DS_DIR + 'serverobjects.lua'
GEN4_DS = DS_DIR + 'lightsaber_one_hand_gen4.lua'
WHIP_DS = DS_DIR + 'lightsaber_lightwhip.lua'
SCHEMATICS = S + 'managers/crafting/schematics.lua'

LS_DIR = S + 'object/tangible/loot/loot_schematic/'
LS_OBJECTS = LS_DIR + 'objects.lua'
LS_SERVEROBJECTS = LS_DIR + 'serverobjects.lua'
WHIP_LS = LS_DIR + 'lightwhip_schematic.lua'

ITEMS = S + 'loot/items.lua'
GROUPS = S + 'loot/groups.lua'
ITEM_WHIP = S + 'loot/items/lightwhip/lightwhip.lua'
ITEM_LS = S + 'loot/items/lightwhip/lightwhip_schematic.lua'
GROUP = S + 'loot/groups/lightwhip/lightwhip_nightsister.lua'

NEW = [WHIP, WHIP_DS, WHIP_LS, ITEM_WHIP, ITEM_LS, GROUP]
TOUCHED = [SABER_OBJECTS, SABER_SERVEROBJECTS, DS_OBJECTS, DS_SERVEROBJECTS, SCHEMATICS, LS_OBJECTS, LS_SERVEROBJECTS,
           ITEMS, GROUPS]


def git(*args, cwd=STAGE):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True).stdout


def head(path):
    return git('show', 'HEAD:' + path, cwd=DEV).decode('utf-8')


def put(path, text):
    full = os.path.join(STAGE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def replace_once(text, old, new):
    assert text.count(old) == 1, 'anchor not unique: %r' % old[:80]
    return text.replace(old, new)


def append(text, block):
    assert text.endswith('\n')
    return text + block


def shared_block(var, path, what):
    return ('\n-- %s (L1, 18 Oct 2026). The .iff is in the light whip archive, local_planets.tre (client and server).\n'
            '%s = %s:new {\n\tclientTemplateFileName = "%s"\n}\n\n'
            'ObjectTemplates:addClientTemplate(%s, "%s")\n' % (what[0], var, what[1], path, var, path))


ITEM_WHIP_TEXT = '''-- The light whip (L1, 18 Oct 2026): a one-handed saber with a long, thin blade and its own trail
-- (object/weapon/melee/sword/crafted_saber/sword_lightwhip.lua; client files in local_planets.tre). Like any saber it
-- lights only with a colour crystal in it. Fixed stats: the middle of the s5 gen4 one-handed crafting ranges. The name
-- comes from the client string file (weapon_name:sword_lightwhip), so a blank name in game means the strings did not load.

lightwhip = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "",
	directObjectTemplate = "object/weapon/melee/sword/crafted_saber/sword_lightwhip.iff",
	craftingValues = {
		{"mindamage",150,150,0},
		{"maxdamage",250,250,0},
		{"attackspeed",4.3,4.3,1},
		{"woundchance",37,37,0},
		{"forcecost",51,51,1},
		{"attackhealthcost",42,42,0},
		{"attackactioncost",52,52,0},
		{"attackmindcost",80,80,0},
	},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("lightwhip", lightwhip)
'''

ITEM_LS_TEXT = '''-- The lightwhip schematic (L1, 18 Oct 2026): teaches the lightwhip draft schematic for 3 crafts
-- (object/tangible/loot/loot_schematic/lightwhip_schematic.lua).

lightwhip_schematic = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "",
	directObjectTemplate = "object/tangible/loot/loot_schematic/lightwhip_schematic.iff",
	craftingValues = {
	},
	customizationStringNames = {},
	customizationValues = {}
}

addLootItemTemplate("lightwhip_schematic", lightwhip_schematic)
'''

GROUP_TEXT = '''-- Light whip loot (L1, 18 Oct 2026): mostly the schematic, sometimes a finished whip. Not on any creature yet: the
-- Nightsister placement on Dathomir is step 4 of Documentation-support/lightwhip-design.md.

lightwhip_nightsister = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "lightwhip_schematic", weight = 8000000},
		{itemTemplate = "lightwhip", weight = 2000000}
	}
}

addLootGroupTemplate("lightwhip_nightsister", lightwhip_nightsister)
'''

LS_TEXT = '''-- The lightwhip schematic (L1, 18 Oct 2026): a Jedi who can craft gen4 sabers learns to make the lightwhip, 3 crafts.

object_tangible_loot_loot_schematic_lightwhip_schematic = object_tangible_loot_loot_schematic_shared_lightwhip_schematic:new {
	templateType = LOOTSCHEMATIC,
	objectMenuComponent = "LootSchematicMenuComponent",
	attributeListComponent = "LootSchematicAttributeListComponent",
	requiredSkill = "force_discipline_light_saber_master",
	targetDraftSchematic = "object/draft_schematic/weapon/lightsaber/lightsaber_lightwhip.iff",
	targetUseCount = 3
}

ObjectTemplates:addTemplate(object_tangible_loot_loot_schematic_lightwhip_schematic, "object/tangible/loot/loot_schematic/lightwhip_schematic.iff")
'''


def main():
    taken = subprocess.run(['grep', '-rli', 'lightwhip', os.path.join(DEV, S)], capture_output=True, text=True).stdout
    assert not taken.strip(), 'lightwhip already in the scripts:\n' + taken

    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    git('init', '-q')
    git('config', 'user.name', 'stage')
    git('config', 'user.email', 'stage@localhost')
    git('config', 'core.autocrlf', 'false')
    for p in TOUCHED:
        put(p, head(p))
    git('add', '-A')
    git('commit', '-q', '-m', 'Core3-dev HEAD ' + git('rev-parse', '--short', 'HEAD', cwd=DEV).decode().strip())

    # the saber template
    put(SABER_OBJECTS, append(head(SABER_OBJECTS), shared_block(
        'object_weapon_melee_sword_crafted_saber_shared_sword_lightwhip',
        'object/weapon/melee/sword/crafted_saber/shared_sword_lightwhip.iff',
        ('The light whip: the s5 gen4 one-handed saber template with a long, thin blade and its own trail',
         'SharedWeaponObjectTemplate'))))
    tpl = head(S5).replace('sword_lightsaber_one_handed_s5_gen4', 'sword_lightwhip')
    assert tpl.count('sword_lightwhip') == 4, tpl.count('sword_lightwhip')
    tpl = replace_once(tpl, 'object_weapon_melee_sword_crafted_saber_sword_lightwhip = ',
                       '-- The light whip (L1, 18 Oct 2026): the s5 gen4 one-handed saber renamed. Its client template draws a long,\n'
                       '-- thin blade with a longer trail. More reach (the saber specials use the weapon\'s range) and weaker against\n'
                       '-- armour, per the lore. Weaker blocking and the parry slip need C++ (step 2, lightwhip-design.md).\n'
                       'object_weapon_melee_sword_crafted_saber_sword_lightwhip = ')
    tpl = replace_once(tpl, '\tarmorPiercing = MEDIUM,\n', '\tarmorPiercing = LIGHT, -- light whip: MEDIUM on the saber\n')
    tpl = replace_once(tpl, '\tidealRange = 3,\n', '\tidealRange = 5, -- light whip: 3 on the saber\n')
    tpl = replace_once(tpl, '\tmaxRange = 5,\n', '\tmaxRange = 7, -- light whip: 5 on the saber\n')
    put(WHIP, tpl)
    put(SABER_SERVEROBJECTS, replace_once(
        head(SABER_SERVEROBJECTS),
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_s5_gen4.lua")\n',
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_s5_gen4.lua")\n'
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightwhip.lua") -- light whip (L1)\n'))

    # the draft schematic
    put(DS_OBJECTS, append(head(DS_OBJECTS), shared_block(
        'object_draft_schematic_weapon_lightsaber_shared_lightsaber_lightwhip',
        'object/draft_schematic/weapon/lightsaber/shared_lightsaber_lightwhip.iff',
        ('The light whip schematic: the gen4 one-handed saber schematic, making the whip',
         'SharedDraftSchematicObjectTemplate'))))
    ds = head(GEN4_DS).replace('lightsaber_one_hand_gen4', 'lightsaber_lightwhip')
    assert ds.count('lightsaber_lightwhip') == 4, ds.count('lightsaber_lightwhip')
    ds = replace_once(ds, 'object_draft_schematic_weapon_lightsaber_lightsaber_lightwhip = ',
                      '-- The light whip schematic (L1, 18 Oct 2026): the gen4 one-handed saber schematic making the whip. It is\n'
                      '-- learnt from the lightwhip loot schematic (object/tangible/loot/loot_schematic/lightwhip_schematic.lua).\n'
                      'object_draft_schematic_weapon_lightsaber_lightsaber_lightwhip = ')
    ds = replace_once(ds, 'customObjectName = "Fourth Generation Lightsaber",', 'customObjectName = "Lightwhip",')
    ds = replace_once(ds, 'targetTemplate = "object/weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_gen4.iff",',
                      'targetTemplate = "object/weapon/melee/sword/crafted_saber/sword_lightwhip.iff",')
    blocks = re.findall(r'additionalTemplates = \{.*?\n\s*\}', ds, flags=re.S)
    assert len(blocks) == 1 and 'shared_sword_lightsaber_one_handed_s5_gen4.iff' in blocks[0], blocks
    ds = ds.replace(blocks[0], 'additionalTemplates = {}')
    put(WHIP_DS, ds)
    put(DS_SERVEROBJECTS, replace_once(
        head(DS_SERVEROBJECTS),
        'includeFile("draft_schematic/weapon/lightsaber/lightsaber_one_hand_gen4.lua")\n',
        'includeFile("draft_schematic/weapon/lightsaber/lightsaber_one_hand_gen4.lua")\n'
        'includeFile("draft_schematic/weapon/lightsaber/lightsaber_lightwhip.lua") -- light whip (L1)\n'))
    put(SCHEMATICS, replace_once(
        head(SCHEMATICS),
        '\t{path="object/draft_schematic/weapon/lightsaber/lightsaber_one_hand_gen4.iff"},\n',
        '\t{path="object/draft_schematic/weapon/lightsaber/lightsaber_one_hand_gen4.iff"},\n'
        '\t{path="object/draft_schematic/weapon/lightsaber/lightsaber_lightwhip.iff"}, -- light whip (L1)\n'))

    # the loot schematic
    put(LS_OBJECTS, append(head(LS_OBJECTS), shared_block(
        'object_tangible_loot_loot_schematic_shared_lightwhip_schematic',
        'object/tangible/loot/loot_schematic/shared_lightwhip_schematic.iff',
        ('The lightwhip schematic: a handheld viewscreen like the Geonosian schematics, with its own name',
         'SharedTangibleObjectTemplate'))))
    put(WHIP_LS, LS_TEXT)
    put(LS_SERVEROBJECTS, replace_once(
        head(LS_SERVEROBJECTS),
        'includeFile("tangible/loot/loot_schematic/geonosian_sonic_blaster_schematic.lua")\n',
        'includeFile("tangible/loot/loot_schematic/geonosian_sonic_blaster_schematic.lua")\n'
        'includeFile("tangible/loot/loot_schematic/lightwhip_schematic.lua") -- light whip (L1)\n'))

    # loot items and group
    put(ITEM_WHIP, ITEM_WHIP_TEXT)
    put(ITEM_LS, ITEM_LS_TEXT)
    put(GROUP, GROUP_TEXT)
    put(ITEMS, append(head(ITEMS), '--lightwhip sub-folder (the light whip, L1, 18 Oct 2026)\n'
                                   'includeFile("items/lightwhip/lightwhip.lua")\n'
                                   'includeFile("items/lightwhip/lightwhip_schematic.lua")\n'))
    put(GROUPS, append(head(GROUPS), '--lightwhip sub-folder (the light whip, L1, 18 Oct 2026)\n'
                                     'includeFile("groups/lightwhip/lightwhip_nightsister.lua")\n'))

    git('add', '-N', *NEW)
    patch = git('diff')
    with open(OUT, 'wb') as f:
        f.write(patch)
    git('apply', '--check', OUT, cwd=DEV)
    for p in TOUCHED + NEW:
        subprocess.run(['luac', '-p', os.path.join(STAGE, p)], check=True)
    print('wrote %s (%d bytes); git apply --check on %s: ok; luac -p on %d files: ok'
          % (OUT, len(patch), DEV, len(TOUCHED + NEW)))


if __name__ == '__main__':
    main()
