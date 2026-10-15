S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== heroic templates in dev"; ls $S/object/building/heroic/ 2>/dev/null | head; grep -n 'heroic' $S/object/building/serverobjects.lua $S/object/allobjects.lua | head -4
echo "===== building spawns from screenplays (examples)"; grep -rn 'spawnSceneObject(".*object/building/' $S/screenplays --include=*.lua | head -5
echo "===== a server building template example"; grep -rn 'SharedBuildingObjectTemplate:new' $S/object/building/general/objects.lua | head -2; grep -n -A3 'object_building_general_shared_bunker_rebel_01 = ' $S/object/building/general/objects.lua | head -6; grep -n -A3 '^object_building_general_bunker_rebel_01 = ' $S/object/building/general/bunker_rebel_01.lua | head -6
echo "===== hoth includes in screenplays.lua"; grep -n 'hoth' $S/screenplays/screenplays.lua
echo "===== regions file tail"; tail -5 $S/managers/planet/hoth_regions.lua
cd /opt/swg/Core3-dev && git log --oneline -1
