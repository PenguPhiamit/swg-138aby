C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
E=/opt/swg/Core3-dev/MMOCoreORB/utils/engine3/MMOEngine/src
echo "===== ResourceSpawner.h 48-110"; sed -n '48,110p' $C/managers/resource/resourcespawner/ResourceSpawner.h
echo "===== ResourceSpawner.cpp 88-110 (addZone etc.)"; sed -n '88,110p' $C/managers/resource/resourcespawner/ResourceSpawner.cpp
echo "===== init order"; grep -n 'loadConfigData\|loadResourceSpawns\|loadDefaultConfig\|resourceSpawner->start\|void ResourceManagerImplementation::initialize' $C/managers/resource/ResourceManagerImplementation.cpp | head
echo "===== String hashCode"; grep -n 'hashCode' $E/system/lang/String.h | head -3
echo "===== ResourceSpawnImplementation 185-215"; sed -n '185,215p' $C/objects/resource/ResourceSpawnImplementation.cpp
echo "===== isJTL in tree entry / set"; grep -rn 'setJTL\|isJTL\|jtl' $C/managers/resource/resourcespawner/resourcetree/ResourceTree.cpp $C/managers/resource/resourcespawner/resourcetree/ResourceTreeEntry.h | head -8
echo "===== createResourceSpawn 500-545"; sed -n '500,545p' $C/managers/resource/resourcespawner/ResourceSpawner.cpp
