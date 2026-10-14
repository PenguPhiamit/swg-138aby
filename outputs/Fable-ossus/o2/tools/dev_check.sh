#!/bin/sh
# Read-only checks of batch O2 against Core3-dev, plus luac5.3 on every staged Lua file. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o2/tools/dev_check.sh
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
O2="$(cd "$(dirname "$0")/.." && pwd)"
status=0
echo "== luac on the staged Lua and the planet block snippet"
for f in $(cd "$O2/staged/MMOCoreORB/bin/scripts" && find . -name '*.lua' | sed 's#^\./##' | sort) ; do
  if luac5.3 -p "$O2/staged/MMOCoreORB/bin/scripts/$f"; then echo "luac ok $f"; else echo "LUAC FAILED $f"; status=1; fi
done
luac5.3 -p "$O2/snippets/planet_manager_ossus.lua" && echo "luac ok snippets/planet_manager_ossus.lua" || { echo "LUAC FAILED snippet"; status=1; }
echo "== server templates the snapshot needs (work/dev-templates.txt)"
while read -r t; do
  case "$t" in \#*|"") continue ;; esac
  if [ -f "$S/$t" ]; then echo "ok      $t"; else echo "MISSING $t"; status=1; fi
done < "$O2/work/dev-templates.txt"
echo "== stock bodies, pet control devices and lair props the fauna use"
for t in object/mobile/womp_rat_hue.lua object/mobile/tybis_hue.lua object/mobile/kliknik_hue.lua object/mobile/gurreck_hue.lua object/mobile/bol_hue.lua \
         object/intangible/pet/womp_rat_hue.lua object/intangible/pet/kliknik_hue.lua object/intangible/pet/gurreck_hue.lua \
         object/tangible/lair/base/poi_all_lair_warren_large.lua object/tangible/lair/base/poi_all_lair_mound_small.lua object/tangible/lair/base/poi_all_lair_mound_large.lua \
         object/tangible/lair/base/poi_all_lair_thicket_large.lua object/tangible/lair/base/poi_all_lair_insecthill_large.lua object/tangible/lair/base/poi_all_lair_insecthill_small.lua \
         object/tangible/lair/base/poi_all_lair_rock_shelter_large.lua object/tangible/lair/base/poi_all_lair_bones_large.lua object/tangible/lair/base/poi_all_lair_rocks_large.lua; do
  if [ -f "$S/$t" ]; then echo "ok      $t"; else echo "MISSING $t"; status=1; fi
done
echo "== names that must not already exist in dev (creature templates, lairs, spawn groups, regions file, planet block)"
for n in ossus_gokob ossus_tribis ossus_kaddyr_bug ossus_kirruk ossus_bol; do
  c=$(grep -rl "addCreatureTemplate($n," "$S/mobile" 2>/dev/null | wc -l); [ "$c" = "0" ] && echo "free    $n" || { echo "TAKEN   $n"; status=1; }
done
[ -f "$S/managers/planet/ossus_regions.lua" ] && { echo "EXISTS  managers/planet/ossus_regions.lua"; } || echo "free    managers/planet/ossus_regions.lua"
grep -q '^ossus = {' "$S/managers/planet/planet_manager.lua" && echo "EXISTS  ossus block in planet_manager.lua" || echo "free    ossus block in planet_manager.lua"
echo "== patch anchors occur exactly once"
grep -c 'includeFile("hoth/serverobjects.lua") -- Sandbox: Hoth creatures (Bellum Gero, AGPL-3.0)' "$S/mobile/serverobjects.lua"
grep -c 'includeFile("lair/creature_lair/hoth/hoth_wampa_lair_neutral_large.lua")' "$S/mobile/lair/creature_lair/serverobjects.lua"
grep -c 'includeFile("lair/creature_dynamic/hoth/hoth_wampa_neutral_none.lua")' "$S/mobile/lair/creature_dynamic/serverobjects.lua"
grep -c 'includeFile("spawn/hoth/hoth_scavenger_zone.lua")' "$S/mobile/spawn/serverobjects.lua"
grep -c '^tutorial = {' "$S/managers/planet/planet_manager.lua"
exit $status
