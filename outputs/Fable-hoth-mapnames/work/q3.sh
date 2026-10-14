C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== readRegionObject 1000-1130"; sed -n '1000,1130p' $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== MapLocationTable transferObject"; grep -n 'transferObject\|getPlanetMapCategory\|getPlanetMapSubCategory\|isActive\|insert' $C/objects/scene/MapLocationTable*.h $C/objects/scene/*MapLocation*.cpp 2>/dev/null | head -20
echo "===== MapLocationEntry.h"; sed -n '1,80p' $C/managers/planet/MapLocationEntry.h | grep -n 'getObjectName\|getDisplayedName\|getCustomObjectName\|insert\|Unicode\|String\|class\|bool' | head -24
echo "===== map response"; grep -rn 'getDisplayedName\|getCustomObjectName\|getObjectName\|insertUnicode\|insertAscii\|insertByte\|insertInt\|insertFloat' $C/packets/player/GetMapLocationsResponseMessage.h | head -20
echo "===== Region idl/impl"; grep -n 'setObjectName\|StringId\|customName\|getDisplayedName' $C/objects/region/RegionImplementation.cpp $C/objects/region/Region.idl $C/objects/area/ActiveAreaImplementation.cpp 2>/dev/null | head -12
echo "===== SceneObject getDisplayedName"; grep -n 'getDisplayedName' $C/objects/scene/SceneObjectImplementation.cpp | head -3
