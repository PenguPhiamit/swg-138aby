"""Stage the light whip's bosses-only drop (L1, Claude, 18 Oct 2026) as a patch for Core3-dev. Writes nothing under
/opt/swg: it copies the touched files from the dev tree's HEAD into a scratch git repo under /tmp, edits them there
(every edit asserts its anchor), and writes lightwhip-boss-drop-dev.patch next to this script. Not applied.

    wsl -d Debian -u swgemu -- python3 make_boss_drop_patch.py      (then: git -C /opt/swg/Core3-dev apply --check <patch>)

Owner, 18 Oct ~8:20 PM (via the main session's card): "Bosses only", over Dathomir Nightsisters and over not yet.

What the patch does (Lua only):
  screenplays/sandbox/sandbox_world_bosses.lua    a slain krayt boss of the rotation (Ghost-Scale the Canyon Krayt and
        Old Rattlebones, marked lightwhip = true; owner, 8:26 PM: "Krayt dragons for now, the boss") gives, with
        lightwhipChance (10%) per kill, one roll of the light whip group to one random player who damaged it, straight
        into their inventory (the next one if it is full), with a message. The roster's templates stay stock, so an
        ordinary krayt or gorax never drops it.
  loot/groups/lightwhip/lightwhip_nightsister.lua -> lightwhip_boss.lua (and its include line): the owner chose bosses
        over Nightsisters, so the group's name and comment say so. Still schematic 80%, finished whip 20%.
"""
import os
import shutil
import subprocess

DEV = '/opt/swg/Core3-dev'
S = 'MMOCoreORB/bin/scripts/'
STAGE = '/tmp/lightwhip-boss-stage'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lightwhip-boss-drop-dev.patch')

BOSSES = S + 'screenplays/sandbox/sandbox_world_bosses.lua'
GROUPS = S + 'loot/groups.lua'
OLD_GROUP = S + 'loot/groups/lightwhip/lightwhip_nightsister.lua'
NEW_GROUP = S + 'loot/groups/lightwhip/lightwhip_boss.lua'
SCREENPLAYS = S + 'screenplays/screenplays.lua'
MENU = S + 'screenplays/sandbox/lightwhip_schematic_menu.lua'
LOOT_SCHEMATIC = S + 'object/tangible/loot/loot_schematic/lightwhip_schematic.lua'

# Owner, 18 Oct ~8:35 PM (via the main session): "Smith + Tech I, or LS Master". The stock loot-schematic menu checks one
# requiredSkill (LootSchematicMenuComponent.cpp), so the lightwhip schematic gets this Lua menu instead. Lua has no use
# count binding, so the item is destroyed once learnt (stock loot schematics are single use too).
MENU_TEXT = '''-- The lightwhip schematic's menu (L1, 18 Oct 2026). Owner: "Smith + Tech I, or LS Master", that is
-- (Master Weaponsmith and Lightsaber Technique I) or Lightsaber Master. It stands in for the stock
-- LootSchematicMenuComponent, which checks one skill only. Teaches the lightwhip schematic for 3 crafts, then the notes are used up.

LightwhipSchematicMenuComponent = {
	schematic = "object/draft_schematic/weapon/lightsaber/lightsaber_lightwhip.iff",
	uses = 3,
	lootType = 1, -- SchematicList::LOOT
}

function LightwhipSchematicMenuComponent:canLearn(pPlayer)
	local player = CreatureObject(pPlayer)

	return (player:hasSkill("crafting_weaponsmith_master") and player:hasSkill("force_discipline_light_saber_technique_01"))
		or player:hasSkill("force_discipline_light_saber_master")
end

function LightwhipSchematicMenuComponent:fillObjectMenuResponse(pSceneObject, pMenuResponse, pPlayer)
	if (pPlayer == nil or pMenuResponse == nil) then
		return
	end

	if (self:canLearn(pPlayer)) then
		LuaObjectMenuResponse(pMenuResponse):addRadialMenuItem(50, 3, "@loot_schematic:use_schematic") -- Learn Schematic
	end
end

function LightwhipSchematicMenuComponent:handleObjectMenuSelect(pObject, pPlayer, selectedID)
	if (pPlayer == nil or pObject == nil or selectedID ~= 50) then
		return 0
	end

	if (not SceneObject(pObject):isASubChildOf(pPlayer)) then
		CreatureObject(pPlayer):sendSystemMessage("@loot_schematic:must_be_holding") -- You must be holding that in order to use it.
		return 0
	end

	if (not self:canLearn(pPlayer)) then
		CreatureObject(pPlayer):sendSystemMessage("To follow these notes you need Master Weaponsmith and Lightsaber Technique I, or Lightsaber Master.")
		return 0
	end

	local pGhost = CreatureObject(pPlayer):getPlayerObject()

	if (pGhost == nil) then
		return 0
	end

	if (PlayerObject(pGhost):addRewardedSchematic(self.schematic, self.lootType, self.uses, true)) then
		CreatureObject(pPlayer):sendSystemMessage("@loot_schematic:schematic_learned") -- You acquire a new crafting schematic!
		SceneObject(pObject):destroyObjectFromWorld()
		SceneObject(pObject):destroyObjectFromDatabase()
	end

	return 0
end
'''


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


GROUP_TEXT = '''-- Light whip loot (L1, 18 Oct 2026): mostly the schematic, sometimes a finished whip. Owner, 18 Oct: bosses only.
-- Rolled for one damage dealer of a slain rotation boss (screenplays/sandbox/sandbox_world_bosses.lua, lightwhipChance).

lightwhip_boss = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "lightwhip_schematic", weight = 8000000},
		{itemTemplate = "lightwhip", weight = 2000000}
	}
}

addLootGroupTemplate("lightwhip_boss", lightwhip_boss)
'''

DROP = '''
	-- Light whip (L1, owner 18 Oct: "Krayt dragons for now, the boss"): sometimes one damage dealer of a krayt boss gets a
	-- roll of the whip group.
	if paid > 0 and boss ~= nil and boss.lightwhip and getRandomNumber(1, 100) <= self.lightwhipChance then
		self:giveLightwhip(dealers, name)
	end
'''

GIVE = '''
-- One random player who damaged the boss gets the light whip group's roll (schematic or finished whip) in their inventory;
-- if that inventory is full, the next player in the list does.
function SandboxWorldBosses:giveLightwhip(dealers, name)
	local players = {}

	for _, pPlayer in pairs(dealers) do
		if pPlayer ~= nil and SceneObject(pPlayer):isPlayerCreature() then
			table.insert(players, pPlayer)
		end
	end

	if #players == 0 then
		return
	end

	local first = getRandomNumber(1, #players)

	for i = 0, #players - 1 do
		local pPlayer = players[(first + i - 1) % #players + 1]
		local pInventory = CreatureObject(pPlayer):getSlottedObject("inventory")

		if pInventory ~= nil and not SceneObject(pInventory):isContainerFullRecursive() then
			createLoot(pInventory, self.lightwhipLootGroup, 0, true)
			CreatureObject(pPlayer):sendSystemMessage("Among " .. name .. "'s remains you find something left by an earlier victim: a lightwhip, or the notes to build one.")
			return
		end
	end
end
'''


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    git('init', '-q')
    git('config', 'user.name', 'stage')
    git('config', 'user.email', 'stage@localhost')
    git('config', 'core.autocrlf', 'false')
    for p in (BOSSES, GROUPS, OLD_GROUP, SCREENPLAYS, LOOT_SCHEMATIC):
        put(p, head(p))
    git('add', '-A')
    git('commit', '-q', '-m', 'Core3-dev HEAD ' + git('rev-parse', '--short', 'HEAD', cwd=DEV).decode().strip())

    text = head(BOSSES)
    text = replace_once(text, '\treward = 25000,                 -- bank credits per player who damaged the boss\n',
                        '\treward = 25000,                 -- bank credits per player who damaged the boss\n'
                        '\tlightwhipChance = 10,           -- percent per kill of a roster boss marked lightwhip (the krayts; L1)\n'
                        '\tlightwhipLootGroup = "lightwhip_boss",\n')
    for krayt in ('{ template = "giant_canyon_krayt_dragon", name = "Ghost-Scale the Canyon Krayt", ham = 1.5, planet = "tatooine"',
                  '{ template = "krayt_dragon_ancient", name = "Old Rattlebones, Ancient Krayt", ham = 1.25, planet = "tatooine"'):
        text = replace_once(text, krayt + ' },', krayt + ', lightwhip = true },')
    text = replace_once(text, '\tbroadcastToGalaxy(nil, "\\\\#ffcc66[World boss]\\\\#ffffff " .. name .. " has been slain on " .. planetLabel(planet) .. by .. "!")\n',
                        '\tbroadcastToGalaxy(nil, "\\\\#ffcc66[World boss]\\\\#ffffff " .. name .. " has been slain on " .. planetLabel(planet) .. by .. "!")\n'
                        + DROP)
    text = replace_once(text, '\treturn 1\nend\n\nfunction SandboxWorldBosses:expire(',
                        '\treturn 1\nend\n' + GIVE + '\nfunction SandboxWorldBosses:expire(')
    put(BOSSES, text)

    os.remove(os.path.join(STAGE, OLD_GROUP))
    put(NEW_GROUP, GROUP_TEXT)
    put(GROUPS, replace_once(head(GROUPS), 'includeFile("groups/lightwhip/lightwhip_nightsister.lua")\n',
                             'includeFile("groups/lightwhip/lightwhip_boss.lua")\n'))

    # the schematic rule: our Lua menu on the loot schematic, its file included with the other sandbox screenplays
    put(MENU, MENU_TEXT)
    put(SCREENPLAYS, replace_once(head(SCREENPLAYS), 'includeFile("sandbox/sandbox_world_bosses.lua")\n',
                                  'includeFile("sandbox/sandbox_world_bosses.lua")\n'
                                  'includeFile("sandbox/lightwhip_schematic_menu.lua") -- light whip (L1)\n'))
    ls = head(LOOT_SCHEMATIC)
    ls = replace_once(ls, '-- The lightwhip schematic (L1, 18 Oct 2026): a Jedi who can craft gen4 sabers learns to make the lightwhip, 3 crafts.\n',
                      '-- The lightwhip schematic (L1, 18 Oct 2026): teaches the lightwhip, 3 crafts. Owner, 18 Oct: "Smith + Tech I, or LS Master",\n'
                      '-- checked by LightwhipSchematicMenuComponent (screenplays/sandbox/lightwhip_schematic_menu.lua), which also does the\n'
                      '-- learning; requiredSkill stays empty because the stock menu and attribute list take one skill only.\n')
    ls = replace_once(ls, '\tobjectMenuComponent = "LootSchematicMenuComponent",\n', '\tobjectMenuComponent = "LightwhipSchematicMenuComponent",\n')
    ls = replace_once(ls, '\trequiredSkill = "force_discipline_light_saber_master",\n', '\trequiredSkill = "",\n')
    put(LOOT_SCHEMATIC, ls)

    git('add', '-N', NEW_GROUP, MENU)
    patch = git('diff')
    with open(OUT, 'wb') as f:
        f.write(patch)
    git('apply', '--check', OUT, cwd=DEV)
    checked = (BOSSES, GROUPS, NEW_GROUP, SCREENPLAYS, MENU, LOOT_SCHEMATIC)
    for p in checked:
        subprocess.run(['luac5.3', '-p', os.path.join(STAGE, p)], check=True)
    print('wrote %s (%d bytes); git apply --check on %s: ok; luac5.3 -p on %d files: ok' % (OUT, len(patch), DEV, len(checked)))


if __name__ == '__main__':
    main()
