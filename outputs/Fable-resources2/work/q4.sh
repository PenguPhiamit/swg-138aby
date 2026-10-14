C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
E=/opt/swg/Core3-dev/MMOCoreORB/utils/engine3/MMOEngine/src/engine
echo "===== ResourceSpawner.h members"; grep -n 'activeResourceZones\|addZone\|Vector<String>\|void load\|class ResourceSpawner\|Logger\|jtlResources' $C/managers/resource/resourcespawner/ResourceSpawner.h | head -20
echo "===== config load 85-150"; sed -n '85,150p' $C/managers/resource/ResourceManagerImplementation.cpp
echo "===== Lua::getGlobalString"; grep -n -A8 'String Lua::getGlobalString' $E/lua/Lua.cpp | head -12
echo "===== ResourceSpawn.idl spawn map accessors"; grep -n 'getSpawnMapSize\|getSpawnMapZone\|createSpawnMaps\|spawnMaps\|inShift\|getZoneRestriction\|isJTL\|getType()\|getName()' $C/objects/resource/ResourceSpawn.idl | head -14
echo "===== ResourceTreeEntry pools"; grep -n 'getMinpool\|getMaxpool\|isJTL\|getZoneRestriction\|minpool\|maxpool' $C/managers/resource/resourcespawner/resourcetree/ResourceTreeEntry.h | head -12
echo "===== where createSpawnMaps is called"; grep -rn 'createSpawnMaps' $C --include=*.cpp | head
echo "===== createResourceSpawn around"; sed -n "$(grep -n 'createSpawnMaps' $C/managers/resource/resourcespawner/ResourceSpawner.cpp | tail -1 | cut -d: -f1),+3p" $C/managers/resource/resourcespawner/ResourceSpawner.cpp
echo "===== resource_manager.lua pools"; sed -n '120,200p' $S/managers/resource_manager.lua | grep -v '^\s*--' | grep -v '^\s*$'
