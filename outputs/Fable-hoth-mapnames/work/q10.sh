S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
C=/opt/swg/Core3-dev/MMOCoreORB/src
echo "===== planet_map_location in dev scripts"; grep -rn 'planet_map_location\|map_location_base' $S --include=*.lua | head -8
echo "===== planet_map_location in src"; grep -rn 'planet_map_location\|map_location_base\|clientpoi' $C --include=*.cpp --include=*.h --include=*.idl | head -8
echo "===== PlanetMapCategory.h"; sed -n '1,80p' $C/templates/manager/PlanetMapCategory.h | grep -n 'class\|get\|bool\|int \|String ' | head -20
echo "===== loadPlanetMapCategories"; grep -n -A25 'void TemplateManager::loadPlanetMapCategories' $C/templates/manager/TemplateManager.cpp | head -40
