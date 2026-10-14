C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== isInRangeWithPoi callers"; grep -rn 'isInRangeWithPoi' /opt/swg/Core3-dev/MMOCoreORB/src --include=*.cpp --include=*.h | grep -v 'PlanetManagerImplementation.cpp:1248' | head -6
echo "===== named region / area name consumers"; grep -rn 'isNamedRegion()\|getAreaName()' $C --include=*.cpp --include=*.h | grep -v 'ActiveAreaImplementation.cpp\|ActiveArea.idl' | head -10
echo "===== clientregion in src"; grep -rln 'clientregion' /opt/swg/Core3-dev/MMOCoreORB/src | head -3
echo "===== glacial rancor placement"; grep -rn 'glacial_rancor\|rancor_grounds' $S/mobile/spawn/hoth $S/screenplays/poi/hoth* $S/mobile/spawn/lair/hoth* $S/managers/planet/hoth_regions.lua 2>/dev/null | head -8; ls $S/mobile/spawn/lair/ 2>/dev/null | grep -i hoth | head
echo "===== screenplays.lua hoth includes"; grep -n 'hoth' $S/screenplays/screenplays.lua | head -12
echo "===== mynock den in dev?"; ls $S/screenplays/poi/ | grep -i 'mynock'; grep -rn 'mynock_den' $S/screenplays/screenplays.lua | head -2
