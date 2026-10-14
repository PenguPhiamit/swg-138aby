C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== clientpoi use 1240-1290"; sed -n '1240,1290p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== ClientPoiDataTable columns"; grep -n 'getValue\|String\|float\|planet\|name' $C/managers/planet/ClientPoiDataTable.h | head -24
