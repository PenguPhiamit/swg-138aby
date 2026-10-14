cd "$(dirname "$0")/.." || exit 2
luac5.3 -p staged/MMOCoreORB/bin/scripts/screenplays/poi/hoth_mynock_den_outdoor.lua && echo "luac ok hoth_mynock_den_outdoor.lua"
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
for n in 01 02 03 04 05 06 07 08 09; do [ -f $S/object/static/structure/general/cave_stalagmite_ice_style_$n.lua ] || echo "MISSING stalagmite $n"; done
for n in 01 02 03; do [ -f $S/object/static/structure/general/cave_column_ice_style_$n.lua ] || echo "MISSING column $n"; done
for c in hoth_ice_mynock hoth_greater_ice_mynock hoth_mynock_broodmother; do grep -q "addCreatureTemplate($c," $S/mobile/hoth/$c.lua && echo "ok creature $c" || echo "MISSING creature $c"; done
[ -f $S/screenplays/poi/hoth_mynock_den.lua ] && echo "NOTE option 1 (poi/hoth_mynock_den.lua) is in dev" || echo "option 1 not in dev (as expected, held)"
