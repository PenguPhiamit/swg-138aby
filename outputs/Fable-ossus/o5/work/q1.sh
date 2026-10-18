S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
cd /opt/swg/Core3-dev && git log --oneline -1
echo "===== hoth in managers (what Hoth touched)"; grep -rln 'hoth' $S/managers | head; grep -n 'hoth' $S/managers/weather_manager.lua $S/managers/resource_manager.lua 2>/dev/null | head -5
echo "===== snapshot missing behaviour"; grep -n 'snapshot/\|loadSnapshotObjects\|ws\b' $C/managers/planet/PlanetManagerImplementation.cpp | head -8; sed -n "$(grep -n 'void PlanetManagerImplementation::loadSnapshotObjects' $C/managers/planet/PlanetManagerImplementation.cpp | cut -d: -f1),+14p" $C/managers/planet/PlanetManagerImplementation.cpp
echo "===== planet_manager hoth block"; sed -n "$(grep -n '^hoth = {' $S/managers/planet/planet_manager.lua | cut -d: -f1),+22p" $S/managers/planet/planet_manager.lua
echo "===== tutorial anchor"; grep -n '^tutorial = {' $S/managers/planet/planet_manager.lua
echo "===== resource_manager activeZones line"; grep -n '^activeZones' $S/managers/resource_manager.lua
O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o5/work/orig/MMOCoreORB/bin/scripts; mkdir -p $O/managers/planet; cp $S/managers/planet/planet_manager.lua $O/managers/planet/; cp $S/managers/resource_manager.lua $O/managers/
cd /opt/swg/Core3-dev && git status --porcelain -- MMOCoreORB/bin/scripts/managers/planet/planet_manager.lua MMOCoreORB/bin/scripts/managers/resource_manager.lua; echo "copied"
