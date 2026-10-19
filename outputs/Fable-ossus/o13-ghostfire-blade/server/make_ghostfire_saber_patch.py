"""Stage the server half of the ghostfire saber (Ossus O13, Claude, 18 Oct 2026) as a patch for Core3-dev. Writes nothing
under /opt/swg: it copies the touched files from the dev tree's HEAD into a scratch git repo under /tmp, edits them there
(every edit asserts its anchor), and writes ghostfire-saber-dev.patch next to this script.

    wsl -d Debian -- python3 make_ghostfire_saber_patch.py      (then: git -C /opt/swg/Core3-dev apply --check <patch>)

What the patch does:
  object/weapon/melee/sword/crafted_saber/objects.lua          + the shared template (its .iff is in local_planets.tre)
  object/weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire.lua   new: the s12 gen4 one-handed server
                                                                 template, renamed (gen4 certification and crafting ranges)
  object/weapon/melee/sword/crafted_saber/serverobjects.lua    + its includeFile
  loot/items/ossus/ossus_ghostfire_saber.lua, loot/groups/ossus/ossus_ghostfire_saber.lua   new, with include lines
  screenplays/sandbox/ossus_people.lua                          the keeper gives the saber with the crystal (two free
                                                                 slots); anyone who finished before gets it on the next visit
"""
import os
import shutil
import subprocess

DEV = '/opt/swg/Core3-dev'
S = 'MMOCoreORB/bin/scripts/'
SABER_DIR = S + 'object/weapon/melee/sword/crafted_saber/'
STAGE = '/tmp/ghostfire-saber-stage'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ghostfire-saber-dev.patch')

OBJECTS = SABER_DIR + 'objects.lua'
SERVEROBJECTS = SABER_DIR + 'serverobjects.lua'
S12 = SABER_DIR + 'sword_lightsaber_one_handed_s12_gen4.lua'
NEW_TEMPLATE = SABER_DIR + 'sword_lightsaber_one_handed_ghostfire.lua'
ITEMS = S + 'loot/items.lua'
GROUPS = S + 'loot/groups.lua'
CRYSTAL_GROUP = S + 'loot/groups/ossus/ossus_ghostfire_crystal.lua'
NEW_ITEM = S + 'loot/items/ossus/ossus_ghostfire_saber.lua'
NEW_GROUP = S + 'loot/groups/ossus/ossus_ghostfire_saber.lua'
PEOPLE = S + 'screenplays/sandbox/ossus_people.lua'


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


SHARED_BLOCK = '''
-- The Ossus ghostfire lightsaber (O13, 18 Oct 2026): the s12 gen4 one-handed template with the ghostfire blade, trail and hum
-- (appearance/wp_mle_sword_lightsaber_blade_ghostfire.lsb). The .iff is in our archive, local_planets.tre (client and server).
object_weapon_melee_sword_crafted_saber_shared_sword_lightsaber_one_handed_ghostfire = SharedWeaponObjectTemplate:new {
	clientTemplateFileName = "object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire.iff"
}

ObjectTemplates:addClientTemplate(object_weapon_melee_sword_crafted_saber_shared_sword_lightsaber_one_handed_ghostfire, "object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire.iff")
'''

ITEM = '''-- The ghostfire lightsaber (Ossus O13, 18 Oct 2026): given with the ghostfire crystal by the spirit of Ood Bnar
-- (screenplays/sandbox/ossus_people.lua). Its blade, swing trail and quiet hum are in our client archive (local_planets.tre);
-- like any saber it lights only with a colour crystal in it. Fixed stats: the middle of the s12 gen4 one-handed crafting ranges.

ossus_ghostfire_saber = {
	minimumLevel = 0,
	maximumLevel = -1,
	customObjectName = "Ghostfire Lightsaber",
	directObjectTemplate = "object/weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire.iff",
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

addLootItemTemplate("ossus_ghostfire_saber", ossus_ghostfire_saber)
'''

GIVE_OLD = '''	createLoot(pInventory, self.ghostfire.lootGroup, 1, true)
	setState(pPlayer, "ghostfire", "done")
	CreatureObject(pPlayer):sendSystemMessage("You receive the ghostfire crystal.")
	return true
end
'''

GIVE_NEW = '''	-- O13: the crystal and the saber made to carry it, so two free slots
	if SceneObject(pInventory):getContainerVolumeLimit() - SceneObject(pInventory):getCountableObjectsRecursive() < 2 then
		return false
	end

	createLoot(pInventory, self.ghostfire.lootGroup, 1, true)
	createLoot(pInventory, self.ghostfire.saberLootGroup, 1, true)
	setState(pPlayer, "ghostfire", "done")
	setState(pPlayer, "gfSaber", "1")
	CreatureObject(pPlayer):sendSystemMessage("You receive the ghostfire crystal, and a lightsaber made to carry it.")
	return true
end

-- O13: a player who finished the quest before the saber existed gets it on the next visit to the keeper.
function OssusPeople:giveGhostfireSaber(pPlayer)
	local pInventory = CreatureObject(pPlayer):getSlottedObject("inventory")

	if pInventory == nil or SceneObject(pInventory):isContainerFullRecursive() then
		CreatureObject(pPlayer):sendSystemMessage("The spirit has something more for you. Make room in your inventory and come back.")
		return
	end

	createLoot(pInventory, self.ghostfire.saberLootGroup, 1, true)
	setState(pPlayer, "gfSaber", "1")
	CreatureObject(pPlayer):sendSystemMessage("You receive a lightsaber made to carry the ghostfire.")
end
'''


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    git('init', '-q')
    git('config', 'user.name', 'stage')
    git('config', 'user.email', 'stage@localhost')
    git('config', 'core.autocrlf', 'false')
    for p in (OBJECTS, SERVEROBJECTS, ITEMS, GROUPS, PEOPLE):
        put(p, head(p))
    git('add', '-A')
    git('commit', '-q', '-m', 'Core3-dev HEAD ' + git('rev-parse', '--short', 'HEAD', cwd=DEV).decode().strip())

    objects = head(OBJECTS)
    assert objects.endswith('\n') and 'one_handed_ghostfire' not in objects
    put(OBJECTS, objects + SHARED_BLOCK)

    s12 = head(S12)
    tpl = s12.replace('sword_lightsaber_one_handed_s12_gen4', 'sword_lightsaber_one_handed_ghostfire')
    # the definition line (template and its shared parent) and the addTemplate line (variable and path)
    assert tpl.count('sword_lightsaber_one_handed_ghostfire') == 4, tpl.count('sword_lightsaber_one_handed_ghostfire')
    tpl = replace_once(tpl, 'object_weapon_melee_sword_crafted_saber_sword_lightsaber_one_handed_ghostfire = ',
                       '-- The Ossus ghostfire lightsaber (O13, 18 Oct 2026): the s12 gen4 one-handed saber renamed; its client\n'
                       '-- template draws the ghostfire blade. Given by the ghostfire quest (loot/items/ossus/ossus_ghostfire_saber.lua).\n'
                       'object_weapon_melee_sword_crafted_saber_sword_lightsaber_one_handed_ghostfire = ')
    put(NEW_TEMPLATE, tpl)

    put(SERVEROBJECTS, replace_once(
        head(SERVEROBJECTS),
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_s12_gen4_ranged.lua")\n',
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_s12_gen4_ranged.lua")\n'
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire.lua") -- Ossus O13\n'))

    put(NEW_ITEM, ITEM)
    group = head(CRYSTAL_GROUP)
    group = replace_once(group, 'hands over exactly the ghostfire crystal (Ossus ghostfire quest, 17 Oct 2026)',
                         'hands over exactly the ghostfire lightsaber (Ossus ghostfire quest, O13, 18 Oct 2026)')
    group = group.replace('ossus_ghostfire_crystal', 'ossus_ghostfire_saber')
    assert group.count('ossus_ghostfire_saber') == 4, group
    put(NEW_GROUP, group)
    put(ITEMS, replace_once(head(ITEMS), 'includeFile("items/ossus/ossus_ghostfire_crystal.lua")\n',
                            'includeFile("items/ossus/ossus_ghostfire_crystal.lua")\n'
                            'includeFile("items/ossus/ossus_ghostfire_saber.lua")\n'))
    put(GROUPS, replace_once(head(GROUPS), 'includeFile("groups/ossus/ossus_ghostfire_crystal.lua")\n',
                             'includeFile("groups/ossus/ossus_ghostfire_crystal.lua")\n'
                             'includeFile("groups/ossus/ossus_ghostfire_saber.lua")\n'))

    people = head(PEOPLE)
    people = replace_once(people, '\t\tlootGroup = "ossus_ghostfire_crystal",\n',
                          '\t\tlootGroup = "ossus_ghostfire_crystal",\n'
                          '\t\tsaberLootGroup = "ossus_ghostfire_saber",  -- O13: the ghostfire lightsaber, given with the crystal\n')
    people = replace_once(people, GIVE_OLD, GIVE_NEW)
    people = replace_once(people, '\telseif id == "fail_force" or id == "fail_greed" then\n',
                          '\telseif id == "after" and getState(pPlayer, "gfSaber") ~= "1" then\n'
                          '\t\tOssusPeople:giveGhostfireSaber(pPlayer)\n'
                          '\telseif id == "fail_force" or id == "fail_greed" then\n')
    put(PEOPLE, people)

    git('add', '-N', NEW_TEMPLATE, NEW_ITEM, NEW_GROUP)
    patch = git('diff')
    with open(OUT, 'wb') as f:
        f.write(patch)
    git('apply', '--check', OUT, cwd=DEV)
    for p in (OBJECTS, NEW_TEMPLATE, SERVEROBJECTS, NEW_ITEM, NEW_GROUP, ITEMS, GROUPS, PEOPLE):
        subprocess.run(['luac', '-p', os.path.join(STAGE, p)], check=True)
    print('wrote %s (%d bytes); git apply --check on %s: ok; luac -p on 8 files: ok' % (OUT, len(patch), DEV))


if __name__ == '__main__':
    main()
