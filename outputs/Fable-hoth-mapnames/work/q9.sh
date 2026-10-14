C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== TemplateManager include in PlanetManagerImplementation"; grep -n 'TemplateManager.h\|PlanetMapCategory' $C/managers/planet/PlanetManagerImplementation.cpp | head -5
echo "===== MapLocationType 1-80"; sed -n '14,80p' $C/managers/planet/MapLocationType.h | grep -n 'static const int' | head -70
echo "===== region line numbers for hunks"; grep -n 'region->initializePosition(x, 0, y);\|zone->transferObject(region, -1, true);\|// Region is a City, add to cityRegionMap list\|cityRegionMap.put\|zone->registerObjectWithPlanetaryMap(region);\|int type = regionObject.getIntAt(5);' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== 1130-1165"; sed -n '1130,1165p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== MapLocationEntry 25-54"; sed -n '25,54p' $C/managers/planet/MapLocationEntry.cpp
echo "===== getPlanetMapCategoryByName signature"; grep -n 'getPlanetMapCategoryByName' /opt/swg/Core3-dev/MMOCoreORB/src/templates/manager/TemplateManager.h
echo "===== luac"; which luac5.3 luac 2>/dev/null
