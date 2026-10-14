from pathlib import Path
import json, os, re, subprocess

ROOT=Path('/opt/swg/Core3/MMOCoreORB')
OUT=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
changes={}
def edit(rel,old,new,count=1,include=False):
    path=ROOT/rel
    text=changes.get(path,path.read_text())
    if text.count(old)!=count:
        raise RuntimeError('Unexpected source at '+rel+' ('+str(text.count(old))+' matches)')
    text=text.replace(old,new)
    if include and '#include "conf/ConfigManager.h"' not in text:
        start=text.index('#include ')
        text=text[:start]+'#include "conf/ConfigManager.h"\n'+text[start:]
    changes[path]=text

for rel,count in [('src/server/zone/managers/skill/SkillManager.cpp',2),('src/server/zone/objects/creature/CreatureObjectImplementation.cpp',1)]:
    edit(rel,'int totalSkillPointsWasted = 250;','int totalSkillPointsWasted = ConfigManager::instance()->getInt("Core3.Sandbox.SkillPoints", 250);',count,True)
edit('bin/scripts/managers/player_creation_manager.lua','skillPoints = 250','skillPoints = 1000')
edit('bin/scripts/managers/player_creation_manager.lua','startingCash = 100\n','startingCash = 10000\n')
edit('bin/scripts/managers/player_creation_manager.lua','startingBank = 1000\n','startingBank = 100000\n')
edit('bin/scripts/managers/player_manager.lua','onlineCharactersPerAccount = 2','onlineCharactersPerAccount = 4')
edit('bin/scripts/managers/player_manager.lua','globalExpMultiplier = 1.0','globalExpMultiplier = 5.0')
edit('src/server/zone/managers/player/PlayerManagerImplementation.cpp',
     'xp = playerObject->addExperience(trx, xpType, (int) (amount * speciesModifier * buffMultiplier * localMultiplier * globalExpMultiplier));',
     'const float sandboxMultiplier = amount > 0 ? (xpType == "jedi_general" ? ConfigManager::instance()->getFloat("Core3.Sandbox.JediXpMultiplier", 1.f) : globalExpMultiplier) : 1.f;\n\t\txp = playerObject->addExperience(trx, xpType, (int) (amount * speciesModifier * buffMultiplier * localMultiplier * sandboxMultiplier));',include=True)
edit('src/server/zone/objects/player/sessions/crafting/CraftingSessionImplementation.cpp',
     'void CraftingSessionImplementation::startCreationTasks(int timer, bool practice) {',
     'void CraftingSessionImplementation::startCreationTasks(int timer, bool practice) {\n\tconst int sandboxSeconds = ConfigManager::instance()->getInt("Core3.Sandbox.CraftSeconds", 0);\n\tif (sandboxSeconds > 0) timer = sandboxSeconds;',include=True)
edit('src/server/zone/objects/installation/factory/FactoryObjectImplementation.cpp',
     'timer = ((int)schematic->getComplexity()) * 8;',
     'timer = Math::max(1, (int)(((int)schematic->getComplexity()) * 8 * ConfigManager::instance()->getFloat("Core3.Sandbox.FactoryTimeMultiplier", 1.f)));',include=True)
edit('src/server/zone/objects/creature/variables/Skill.h',
     '\t\treturn moneyRequired;',
     '\t\treturn Math::max(0, (int)(moneyRequired * ConfigManager::instance()->getFloat("Core3.Sandbox.TrainingCostMultiplier", 1.f)));',include=True)
edit('src/server/zone/objects/structure/StructureObjectImplementation.cpp',
     'float rate = getBaseMaintenanceRate();',
     'float rate = getBaseMaintenanceRate() * ConfigManager::instance()->getFloat("Core3.Sandbox.StructureMaintenanceMultiplier", 1.f);',include=True)
edit('src/server/zone/objects/building/BuildingObjectImplementation.cpp',
     'auto maxItems = MAXPLAYERITEMS;\n\n\treturn Math::min(maxItems, lots * 100);',
     'auto maxItems = ConfigManager::instance()->getInt("Core3.Sandbox.HouseMaxItems", MAXPLAYERITEMS);\n\tconst int itemsPerLot = ConfigManager::instance()->getInt("Core3.Sandbox.HouseItemsPerLot", 100);\n\treturn Math::min(maxItems, lots * itemsPerLot);',include=True)
edit('src/server/zone/objects/resource/ResourceContainer.idl','public static final int MAXSIZE = 100000;','public static final int MAXSIZE = 999999;')
edit('src/server/zone/managers/resource/ResourceManager.idl','public static final int RESOURCE_DEED_QUANTITY = 30000;','public static final int RESOURCE_DEED_QUANTITY = 100000;')
edit('bin/scripts/managers/city_manager.lua','CitizensPerRank = {2, 4, 6, 8, 10}','CitizensPerRank = {1, 2, 3, 4, 5}')
edit('bin/scripts/managers/city_manager.lua','maintenanceDiscount = 1.0','maintenanceDiscount = 0.5')
for name,value in [('shuttleportAwayTime',10),('starportAwayTime',10),('shuttleportLandingTime',2),('starportLandingTime',2),('shuttleportLandedTime',600),('starportLandedTime',600)]:
    path=ROOT/'bin/scripts/managers/planet/planet_manager.lua'
    text=changes.get(path,path.read_text())
    replaced,n=re.subn(r'^'+name+r' = \d+',name+' = '+str(value),text,flags=re.M)
    if n!=1:raise RuntimeError('Unexpected travel setting '+name)
    changes[path]=replaced
edit('bin/scripts/screenplays/village/village_jedi_manager_township.lua','VILLAGE_PHASE_DURATION = 3 * 7 * 24 * 60 * 60 * 1000','VILLAGE_PHASE_DURATION = 7 * 24 * 60 * 60 * 1000')
for name in ('speederbike','speederbike_swoop','landspeeder_x34'):
    edit('bin/scripts/object/mobile/vehicle/'+name+'.lua','\ttemplateType = VEHICLE,','\ttemplateType = VEHICLE,\n\tspeed = {30.0, 10.0}, -- Sandbox: run and walk speeds in metres per second')

attributes=sorted(set(re.findall(r'"(res_[a-z_]+)"',(ROOT/'bin/scripts/managers/resource_manager_spawns.lua').read_text())))
if len(attributes)<8:raise RuntimeError('Resource attribute list was not available.')
perfect=' '.join(name+',1000' for name in attributes)
edit('src/server/zone/objects/creature/commands/ResourceCommand.h',
     '} else if(command == "create") {\n\t\t\t\tgiveResource(creature, &args);',
     '} else if(command == "perfect") {\n\t\t\t\tString type;\n\t\t\t\tif (!args.hasMoreTokens()) throw Exception();\n\t\t\t\targs.getStringToken(type);\n\t\t\t\tresMan->createResourceSpawn(creature, UnicodeString(type + " '+perfect+'"));\n\t\t\t} else if(command == "create") {\n\t\t\t\tgiveResource(creature, &args);')
edit('src/server/zone/objects/creature/commands/ResourceCommand.h',
     'creature->sendSystemMessage("\t\tcreate <name> [quantity] : Spawns resource in inventory");',
     'creature->sendSystemMessage("\t\tcreate <name> [quantity] : Spawns resource in inventory");\n\t\t\tcreature->sendSystemMessage("\t\tperfect <type> : Creates a test resource with all applicable stats at 1000");')

config=ROOT/'bin/conf/config-local.lua'
content=config.read_text()
if 'Core3.Sandbox' in content:raise RuntimeError('Sandbox settings already exist; refusing a duplicate application.')
content+='''
-- Local sandbox profile, applied October 13, 2026.
Core3.Sandbox = {
    SkillPoints = 1000,
    JediXpMultiplier = 2.0,
    CraftSeconds = 1,
    FactoryTimeMultiplier = 0.25,
    TrainingCostMultiplier = 0.25,
    StructureMaintenanceMultiplier = 0.5,
    HouseItemsPerLot = 1000,
    HouseMaxItems = 10000,
}
Core3.PlayerCreationManager = Core3.PlayerCreationManager or {}
Core3.PlayerCreationManager.MaxCharactersPerGalaxy = 15
Core3.JTL = Core3.JTL or {}
Core3.JTL.JTLEnabled = true
Core3.JTL.LaunchFromDevice = true
'''
changes[config]=content

# All replacements are checked before any server source is changed.
backup=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/sandbox-backup-path.txt').read_text().strip()
if not (Path(backup)/'manifest.json').exists():raise RuntimeError('Verified backup required.')
for path,text in changes.items():
    path.write_text(text)
config.chmod(0o600)
manifest={'backup_before_changes':backup,'profile':{'regular_xp':5,'group_bonus':1.2,'jedi_xp':2,'skill_points':1000,'characters_per_account':15,'online_characters_per_account':4,'prototype_seconds':1,'factory_time_multiplier':0.25,'training_cost_multiplier':0.25,'structure_maintenance_multiplier':0.5,'city_maintenance_multiplier':0.5,'citizens_per_rank':[1,2,3,4,5],'house_items_per_lot':1000,'house_max_items':10000,'resource_stack_limit':999999,'resource_deed_quantity':100000,'vehicle_run_speed':30,'shuttle_away_seconds':10,'shuttle_landing_seconds':2,'shuttle_landed_seconds':600,'village_phase_days':7,'starting_cash':10000,'starting_bank':100000,'jtl_enabled':True,'launch_from_device':True,'perfect_resources':'owner command /resource perfect TYPE; existing resources preserved'},'changed_files':[str(path.relative_to(ROOT)) for path in changes]}
(OUT/'SWG-sandbox-settings.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Applied sandbox profile to '+str(len(changes))+' source/configuration files.',flush=True)
