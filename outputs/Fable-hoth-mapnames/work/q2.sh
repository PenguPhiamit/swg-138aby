C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-mapnames/work/orig
for f in src/server/zone/managers/planet/PlanetManagerImplementation.cpp src/server/zone/objects/area/ActiveArea.idl bin/scripts/managers/planet/regions.lua bin/scripts/managers/planet/hoth_regions.lua; do mkdir -p "$O/$(dirname $f)"; cp "/opt/swg/Core3-dev/MMOCoreORB/$f" "$O/$f"; done
echo "===== loadRegions: function head and row parsing"; grep -n 'void PlanetManagerImplementation::loadRegions\|void PlanetManagerImplementation::readRegionObject\|LuaObject regionObject\|getStringAt(1)\|getIntAt\|getFloatAt\|getObjectAt\|getTableSize' $C/managers/planet/PlanetManagerImplementation.cpp | head -30
echo "===== 905-1000"; sed -n '905,1000p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== ActiveArea.idl flags"; grep -n 'public static final int' $C/objects/area/ActiveArea.idl | head -24
echo "===== MapLocationEntry name"; grep -rn 'getObjectName\|getDisplayedName\|getCustomObjectName\|name' $C/managers/planet/MapLocationEntry.h | head -8; grep -rn 'getObjectName\|getDisplayedName\|getCustomObjectName\|insertAscii\|insertUnicode' $C/packets/object/GetMapLocationsResponseMessage.h $C/packets/*/GetMapLocationsResponseMessage.h 2>/dev/null | head -8
echo "===== GroundZone registerObjectWithPlanetaryMap"; sed -n '676,700p' $C/GroundZoneImplementation.cpp
