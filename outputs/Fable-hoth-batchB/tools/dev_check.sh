#!/bin/sh
# Read-only checks against Core3-dev for batch B. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/tools/dev_check.sh
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "== server templates for the props and the cave"
for f in object/static/structure/general/camp_tent_s01.lua object/static/structure/general/campfire_fresh.lua \
         object/static/structure/general/camp_cot_s01.lua object/static/structure/general/camp_stool_short_s01.lua \
         object/static/structure/general/camp_spit_s01.lua object/static/structure/general/palette_supply_01.lua \
         object/static/structure/general/poi_all_impl_corral_half_64x64_s01.lua object/static/structure/general/poi_all_rebl_corral_64x64_s01.lua \
         object/static/structure/general/atst_debris_01.lua object/static/structure/military/military_wall_med_imperial_16_style_01.lua \
         object/static/structure/military/military_wall_med_rebl_16_style_01.lua object/static/structure/military/bunker_crate_style_01.lua \
         object/building/general/cave_06_flatland_s01_ice.lua; do
  if [ -f "$S/$f" ]; then echo "ok  $f"; else echo "MISSING $f"; fi
done
echo "== NPC templates"
grep -rhoE 'addCreatureTemplate\([a-z0-9_]+, "(junk_dealer|imperial_recruiter|rebel_recruiter|hoth_snowtrooper|hoth_snowtrooper_sergeant|hoth_rebel_snow_soldier|hoth_rebel_snow_sergeant|hoth_scavenger|hoth_scavenger_raider|hoth_imperial_salvage_tech|hoth_ice_mynock|hoth_greater_ice_mynock|hoth_mynock_broodmother)"' "$S/mobile" | sort -u
echo "== getCell indexing"
grep -n "CellObject\* getCell\|getCell(int" /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/objects/building/BuildingObject.idl /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/objects/building/BuildingObjectImplementation.cpp 2>/dev/null | head -5
grep -n "getCell(int number)" -A 6 /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/objects/building/BuildingObjectImplementation.cpp | head -12
grep -n "getCell" -B2 -A8 "$S/screenplays/tutorial/tutorial.lua" | sed -n 1,16p
