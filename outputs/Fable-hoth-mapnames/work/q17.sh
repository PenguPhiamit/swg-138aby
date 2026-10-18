S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/objects/creature/commands
echo "===== teleport syntax"; grep -n 'Syntax\|syntax\|args.getStringToken\|getFloatToken\|getIntToken\|planet' $C/TeleportCommand.h | head -12
echo "===== elder wampa / wampa levels"; grep -h 'level =' $S/mobile/hoth/hoth_wampa.lua $S/mobile/hoth/hoth_elder_wampa.lua $S/mobile/hoth/hoth_tauntaun.lua $S/mobile/hoth/hoth_ice_mynock.lua 2>/dev/null | tr -d '\t'
echo "===== quest step 1"; grep -n 'Ria Baxx\|ria_baxx\|x = \|npcTemplate\|missionType\|missionTarget\|spawnData' $S/screenplays/tasks/hoth/scavenger_quartermaster.lua | head -24
echo "===== salvage detail + scavenger camp NPCs"; sed -n '94,112p' $S/screenplays/poi/hoth_camps.lua
echo "===== policy date"; grep -n -i 'century\|date\|ABY\|era' /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/setting-and-encounter-policy.md | head -8
