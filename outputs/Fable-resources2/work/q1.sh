C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
cd /opt/swg/Core3-dev && git log --oneline -3
echo "===== ResourceSpawnImplementation: createSpawnMaps / getSpawnZones"; grep -n 'createSpawnMaps\|getSpawnZones\|isJTL\|jtl\|zoneRestriction\|spawnMaps\|minPool\|maxPool' $C/objects/resource/ResourceSpawnImplementation.cpp | head -40
echo "===== getSpawnZones body"; sed -n "$(grep -n 'ResourceSpawnImplementation::getSpawnZones' $C/objects/resource/ResourceSpawnImplementation.cpp | cut -d: -f1),+45p" $C/objects/resource/ResourceSpawnImplementation.cpp
echo "===== createSpawnMaps body"; sed -n "$(grep -n 'ResourceSpawnImplementation::createSpawnMaps' $C/objects/resource/ResourceSpawnImplementation.cpp | cut -d: -f1),+40p" $C/objects/resource/ResourceSpawnImplementation.cpp
