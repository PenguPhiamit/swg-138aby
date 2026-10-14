C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== StringId::setStringId"; grep -n -A14 'void StringId::setStringId(const String& fullPath)' $C/objects/scene/variables/StringId.cpp | head -18
echo "===== NAMEDREGION uses"; grep -rn 'NAMEDREGION' $C --include=*.cpp --include=*.idl --include=*.h | head -8
echo "===== region enter message"; grep -n -B3 -A10 'NAMEDREGION' $C/objects/area/ActiveAreaImplementation.cpp $C/objects/region/RegionImplementation.cpp 2>/dev/null | head -40
echo "===== rancor on hoth in dev"; grep -rln 'rancor' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/screenplays/poi/hoth* /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/mobile/spawn/hoth/ /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/mobile/hoth/ 2>/dev/null | head; grep -rn 'mynock_den\|hoth_mynock_den' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/screenplays/screenplays.lua /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/screenplays/poi/*.lua 2>/dev/null | head -4
echo "===== MapLocationEntry compare"; grep -n 'compareTo\|operator==\|operator<' $C/managers/planet/MapLocationEntry.h $C/managers/planet/MapLocationEntry.cpp | head -5
echo "===== MapLocationType enum"; grep -n 'SHUTTLEPORT\|TERMINAL\|POI\|THEMEPARK\|CAMP' $C/managers/planet/MapLocationType.h 2>/dev/null | head; find /opt/swg/Core3-dev/MMOCoreORB/src -name 'MapLocationType.h' | head -1
echo "===== hunks context: PlanetManagerImplementation includes"; grep -n '#include' $C/managers/planet/PlanetManagerImplementation.cpp | grep -i 'TemplateManager\|PlanetMapCategory\|Region' | head -5
echo "===== MapLocationEntry includes"; grep -n '#include' $C/managers/planet/MapLocationEntry.cpp | head -12
