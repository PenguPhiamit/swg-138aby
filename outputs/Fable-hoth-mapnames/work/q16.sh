S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
cd /opt/swg/Core3-dev && git log --oneline -12 2>/dev/null
echo "===== travel points"; grep -n -B1 -A3 'name = "Mos Eisley\|name = "Coronet\|name = "Scavenger' $S/managers/planet/planet_manager.lua | head -24
echo "===== cave bosses"; grep -n '1800\|^\s*-- cave' $S/screenplays/caves/hoth_ice_caves.lua | head -20
echo "===== boss custom names"; for f in $S/mobile/hoth/hoth_wampa_*.lua $S/mobile/hoth/hoth_mynock_broodmother*.lua; do echo "$f: $(grep -h 'customName\|objectName\|level =' $f | tr -d '\t' | tr '\n' ' ')"; done 2>/dev/null | sed 's#.*/mobile/hoth/##' | head -12
echo "===== teleport syntax"; grep -n -i 'teleport\|warp' /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/core3-command-audit.md | head -8
echo "===== botanist in dev"; grep -rn 'botanist' $S/managers/skill* $S/screenplays/*.lua $S/mobile/*.lua 2>/dev/null | head -5; grep -rln 'botanist' $S/screenplays/static_spawns $S/screenplays/trainers 2>/dev/null | head -3; grep -rn '3516' $S/screenplays --include=*.lua | head -3
echo "===== hoth quest/loot/mission files"; ls $S/screenplays/poi/ | grep hoth; ls $S/mobile/spawn/destroy_mission/ | grep hoth; grep -n 'hoth' $S/loot/loot_manager.lua 2>/dev/null | head -3; ls $S/loot/groups | grep hoth
echo "===== hoth regions in dev now"; grep -c 'NAMEDREGION' $S/managers/planet/hoth_regions.lua
