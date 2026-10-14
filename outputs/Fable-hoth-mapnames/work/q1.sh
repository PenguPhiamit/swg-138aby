C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== every registerObjectWithPlanetaryMap / setPlanetMapCategory site"; grep -rn 'registerObjectWithPlanetaryMap\|setPlanetMapCategory\|getPlanetMapCategoryByName' $C --include=*.cpp --include=*.h --include=*.idl | grep -v 'Stub\|Adapter\|Helper' | sed 's#/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/##' | cut -c1-140
echo "===== Lua bindings mentioning planet map"; grep -rn -i 'planetmap\|planetarymap' $C/objects/scene/LuaSceneObject.cpp $C/managers/director/DirectorManager.cpp $C/objects/creature/LuaCreatureObject.cpp 2>/dev/null | head
echo "===== PlanetManagerImplementation 1095-1160 (CITY region registration)"; sed -n '1095,1160p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== Zone registerObjectWithPlanetaryMap"; grep -n -A25 'void ZoneImplementation::registerObjectWithPlanetaryMap' $C/ZoneImplementation.cpp | head -40
echo "===== MapLocationTable.cpp"; grep -v '^\s*$' $C/managers/planet/MapLocationTable.cpp | head -80
echo "===== GetMapLocationsResponseMessage name field"; grep -rn 'getObjectName\|getDisplayedName\|getCustomObjectName\|insertAscii\|insertUnicode\|getStringId\|getFullName' $C/packets/scene/GetMapLocationsResponseMessage.h 2>/dev/null | head -8; find $C/packets -name 'GetMapLocations*' | head
