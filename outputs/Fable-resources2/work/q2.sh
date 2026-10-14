C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== loadResourceSpawns"; sed -n "$(grep -n 'void ResourceSpawner::loadResourceSpawns' $C/managers/resource/resourcespawner/ResourceSpawner.cpp | cut -d: -f1),+75p" $C/managers/resource/resourcespawner/ResourceSpawner.cpp
echo "===== config reading (activeZones etc.)"; grep -n 'activeZones\|getGlobalString\|getGlobalInt\|minimumpool\|randompool\|fixedpool\|nativepool\|manualpool\|includes\|excludes\|jtl\|JTL' $C/managers/resource/ResourceManagerImplementation.cpp $C/managers/resource/resourcespawner/ResourceSpawner.cpp | head -40
