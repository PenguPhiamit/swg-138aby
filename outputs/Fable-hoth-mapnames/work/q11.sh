C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== clientpoi loader"; grep -n 'clientpoi\|loadClientPoiData\|ClientPoi\|poiMap\|PoiData' $C/managers/planet/PlanetManagerImplementation.cpp $C/managers/planet/PlanetManager.idl | head -12
echo "===== 855-910"; sed -n '855,910p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== who calls loadClientPoiData / uses the result"; grep -rn 'loadClientPoiData\|getClientPoi\|clientPoiMap\|ClientPoiData' $C --include=*.cpp --include=*.idl --include=*.h | grep -v 'PlanetManagerImplementation.cpp:8[5-9][0-9]\|PlanetManagerImplementation.cpp:90' | head -10
echo "===== map_location_base.lua"; sed -n '44,48p' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/object/tangible/planet_map_location/map_location_base.lua; sed -n '44,60p' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/object/tangible/planet_map_location/objects.lua
