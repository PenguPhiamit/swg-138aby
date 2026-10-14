#!/bin/sh
# Read-only checks of species S3 (Chiss Lua) against Core3-dev plus luac5.3. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s3/tools/dev_check.sh
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
S3="$(cd "$(dirname "$0")/.." && pwd)"
status=0
for f in object/creature/player/chiss_female.lua object/creature/player/chiss_male.lua; do
  luac5.3 -p "$S3/staged/MMOCoreORB/bin/scripts/$f" && echo "luac ok $f" || { echo "LUAC FAILED $f"; status=1; }
done
luac5.3 -p "$S3/snippets/objects_chiss.lua" && echo "luac ok snippets/objects_chiss.lua" || { echo "LUAC FAILED snippet"; status=1; }
echo "== names must be free in dev"
for n in object_creature_player_chiss_male object_creature_player_chiss_female object_creature_player_shared_chiss_male; do
  c=$(grep -rl "$n" "$S/object/creature/player" 2>/dev/null | wc -l); [ "$c" = "0" ] && echo "free    $n" || { echo "TAKEN   $n"; status=1; }
done
echo "== anchor occurs once"; grep -c 'includeFile("creature/player/zabrak_male.lua")' "$S/object/creature/player/serverobjects.lua"
echo "== stock race templates in dev for comparison"; ls "$S/object/creature/player" | grep -c '_male.lua\|_female.lua'
echo "== the species skill the template grants (expected absent until skills.iff carries it)"
grep -c 'species_chiss' "$S/managers/skill_manager.lua" 2>/dev/null
exit $status
