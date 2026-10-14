C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== MapLocationEntry.cpp 55-160"; sed -n '55,160p' $C/managers/planet/MapLocationEntry.cpp
echo "===== MapLocationTable.cpp 14-45"; sed -n '14,45p' $C/managers/planet/MapLocationTable.cpp
echo "===== ContainerComponent 330-346"; sed -n '330,346p' $C/objects/scene/components/ContainerComponent.cpp
echo "===== getDisplayedName"; grep -n -A12 'String SceneObjectImplementation::getDisplayedName' $C/objects/scene/SceneObjectImplementation.cpp | head -16
echo "===== LuaObject fields"; grep -n 'getStringField\|getIntField\|getFloatField' /opt/swg/Core3-dev/MMOEngine/src/engine/lua/LuaObject.h 2>/dev/null | head -5; find /opt/swg/Core3-dev -name LuaObject.h | head -2
echo "===== StringIdManager source"; grep -n 'stf\|TreFiles\|DataArchiveStore\|getTreeDirectory\|populate' /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/stringid/StringIdManager.cpp | head -12
echo "===== region flags users of 0x020000+"; grep -rn '0x020000\|0x040000\|0x080000' $C --include=*.idl --include=*.h | head -5
echo "===== git state"; cd /opt/swg/Core3-dev && git log -1 --format='%h %ci' 2>/dev/null; git status --porcelain -- MMOCoreORB/src/server/zone/managers/planet/PlanetManagerImplementation.cpp MMOCoreORB/src/server/zone/managers/planet/MapLocationEntry.cpp MMOCoreORB/src/server/zone/objects/area/ActiveArea.idl MMOCoreORB/bin/scripts/managers/planet/regions.lua 2>/dev/null
