S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== dev: echo/heroic/hoth generator templates"; grep -rln 'echo_base\|hoth_generator\|hoth_ion\|hoth_rebel_transport' $S/object 2>/dev/null | head -8
echo "===== dev botanist skills"; grep -rn 'outdoors_botanist' $S --include=*.lua | grep -v 'trainerData' | cut -c1-200 | head -10; grep -n 'botanist' $S/screenplays/trainers/trainerData.lua | head -4
echo "===== camps file 54-60"; sed -n '54,60p' $S/screenplays/poi/hoth_camps.lua
echo "===== quest step 1 npc positions"; grep -n 'x = \|cellID\|zone' $S/screenplays/tasks/hoth/scavenger_quartermaster.lua | head -12
echo "===== bellum heroic"; ls /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/research/Miphstoe_BellumGero-Live/MMOCoreORB/bin/scripts/object/building/heroic/ 2>/dev/null; grep -rn 'heroic' /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/research/Miphstoe_BellumGero-Live/MMOCoreORB/bin/scripts/object/building/serverobjects.lua | head -5
