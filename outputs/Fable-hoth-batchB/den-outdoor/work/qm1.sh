S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== planetary map code"; grep -rn 'registerObjectWithPlanetaryMap\|unregisterObjectWithPlanetaryMap\|GetMapLocationsResponse\|planet_map_cat\|getPlanetMapCategory\|mapLocations\|PlanetMapCategory' $C --include=*.cpp --include=*.h --include=*.idl | grep -v 'Stub\|Adapter\|Helper' | sed 's#/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/##' | cut -c1-150 | head -24
echo "===== regions.lua flags"; grep -n '= 0x\|= [0-9]' $S/managers/planet/regions.lua | head -20
echo "===== region loading flags handled"; grep -n 'CITY\|NOBUILD\|SPAWNAREA\|WORLDSPAWN\|NOSPAWN\|MAPPOI\|regionFlags\|tier' $C/managers/planet/PlanetManagerImplementation.cpp | head -20
echo "===== planetMapCategory values in scripts"; grep -rhoE 'planetMapCategory = "[a-z_]+"' $S/object | sort | uniq -c | sort -rn | head -30
echo "===== planetMapSubCategory values"; grep -rhoE 'planetMapSubCategory = "[a-z_]+"' $S/object | sort | uniq -c | sort -rn | head -20
echo "===== which static templates carry a map category (sample)"; grep -rlE 'planetMapCategory = "(poi|cave|camp|city|hunting|adventure|lair|shuttleport|trainer)"' $S/object/static $S/object/tangible 2>/dev/null | head -12
