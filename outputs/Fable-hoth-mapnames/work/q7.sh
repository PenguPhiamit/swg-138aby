C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== StringId ctor"; grep -n -A10 'StringId(const String& fullPath' $C/objects/scene/variables/StringId.h | head -24; grep -n -A14 'StringId::StringId(const String& fullPath' $C/objects/scene/variables/StringId.cpp | head -20
echo "===== setObjectName(String"; grep -n 'setObjectName' $C/objects/scene/SceneObject.idl | head -4
echo "===== Region.idl"; sed -n '60,80p' $C/objects/region/Region.idl
echo "===== getCityRegionAt"; grep -n 'getCityRegionAt' $C/managers/planet/PlanetManagerImplementation.cpp | head -2
echo "===== hoth sites in dev poi screenplays"; ls /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/screenplays/poi/ | grep -i hoth; grep -n 'CIRCLE\|camp\|-- ' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/screenplays/poi/hoth_camps.lua | head -30
echo "===== planet_manager hoth"; grep -n -A12 '^\s*hoth = {' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/planet_manager.lua | head -16
