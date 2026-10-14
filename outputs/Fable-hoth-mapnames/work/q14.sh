S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== ice caves screenplay: caves and bosses"; grep -n 'cave_0\|spawnMobile\|-- \|caveName\|boss\|matriarch\|frostfang\|icemaw\|snowblind' $S/screenplays/caves/hoth_ice_caves.lua | head -40
echo "===== glacial rancor anywhere"; grep -rn 'glacial_rancor' $S --include=*.lua | grep -v 'mobile/hoth/' | head -5
echo "===== batch A spawn groups"; ls $S/mobile/spawn/hoth/; grep -n 'template\|lairTemplate' $S/mobile/spawn/hoth/hoth_imperial_zone.lua $S/mobile/spawn/hoth/hoth_scavenger_zone.lua $S/mobile/spawn/hoth/hoth_rebel_zone.lua 2>/dev/null | head -16
echo "===== camps screenplay NPCs"; grep -n 'spawnMobile' $S/screenplays/poi/hoth_camps.lua | sed 's/.*spawnMobile("hoth", "\([^"]*\)".*/\1/' | sort | uniq -c | head -20
