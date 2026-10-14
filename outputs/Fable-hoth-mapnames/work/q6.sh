C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
E=/opt/swg/Core3-dev/MMOCoreORB/utils/engine3/MMOEngine/src/engine
echo "===== ContainerComponent 300-330"; sed -n '300,330p' $C/objects/scene/components/ContainerComponent.cpp
echo "===== LuaObject fields"; grep -n 'getStringField\|getIntField\|getFloatField\|getStringAt\|isValidTable' $E/lua/LuaObject.h | head -8
echo "===== StringId ctor"; grep -n -A8 'StringId(const String& fullPath)\|StringId(const String&' $E/../../../../src/templates/../../../../../src/engine/util/u3d/../../../engine/service/proto/../../../../../src/engine/util/StringId.h 2>/dev/null | head -2; find /opt/swg/Core3-dev -name 'StringId.h' | head -2
echo "===== isRegion"; grep -rn 'isRegion()' $C/objects/scene/SceneObject.idl $C/objects/region/Region.idl $C/objects/area/ActiveArea.idl | head -5
echo "===== areaName"; grep -n 'areaName\|getAreaName\|setAreaName' $C/objects/area/ActiveArea.idl | head -5
echo "===== StringIdManager 16-60"; sed -n '16,60p' /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/stringid/StringIdManager.cpp
echo "===== dev hoth_regions.lua"; cat /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/hoth_regions.lua
echo "===== regions.lua flags block"; grep -n 'NOPETAREA\|NAMEDREGION\|^CIRCLE\|^RECTANGLE\|^RING\|UNDEFINEDAREA' /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/regions.lua
echo "===== getObjectNameStringIdFile"; grep -n 'getObjectNameStringIdFile\|getObjectNameStringIdName\|getFullPath' $C/objects/scene/SceneObject.idl | head -4
