S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== dev echo base doors: client paths"; grep -n 'clientTemplateFileName\|addClientTemplate' $S/object/custom_content/tangible/door/objects.lua | grep -i echo | cut -c1-200 | head -6
echo "===== dev hoth mission spawn points"; grep -n -A12 'hoth = {' $S/managers/mission_npc_spawn_points.lua 2>/dev/null | head -16; grep -rn 'hoth' $S/managers/mission_npc_spawn_points.lua 2>/dev/null | head -3; grep -rln 'NEUTRALSPAWN' $S/managers/*.lua $S/screenplays/*.lua 2>/dev/null | head -3
echo "===== botanist client/skills in dev"; grep -rn 'botanist' $S/screenplays/static_spawns/*.lua $S/screenplays/cities/tatooine_mos_eisley.lua 2>/dev/null | cut -c1-200 | head -4
