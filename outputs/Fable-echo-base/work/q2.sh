O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-echo-base/work/orig/MMOCoreORB/bin/scripts
D=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
mkdir -p $O/screenplays $O/managers/planet $O/object $O/object/building
cp $D/screenplays/screenplays.lua $O/screenplays/; cp $D/managers/planet/hoth_regions.lua $O/managers/planet/; cp $D/object/allobjects.lua $O/object/; cp $D/object/building/serverobjects.lua $O/object/building/
grep -n 'building/general/serverobjects\|building/heroic\|building/military/serverobjects' $D/object/building/serverobjects.lua | head -4
grep -n 'building/general/objects.lua\|building/heroic\|building/military/objects.lua' $D/object/allobjects.lua | head -4
grep -n 'spawnSceneObject' $D/screenplays/poi/hoth_camps.lua | head -1
cd /opt/swg/Core3-dev && git status --porcelain -- MMOCoreORB/bin/scripts/screenplays/screenplays.lua MMOCoreORB/bin/scripts/managers/planet/hoth_regions.lua MMOCoreORB/bin/scripts/object/allobjects.lua MMOCoreORB/bin/scripts/object/building/serverobjects.lua; echo "clean check done"
