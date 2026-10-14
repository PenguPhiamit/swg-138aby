#!/bin/sh
# Parse every staged Lua file with luac5.3. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/tools/luac_staged.sh
cd "$(dirname "$0")/../staged/MMOCoreORB/bin/scripts" || exit 2
status=0
for f in managers/planet/hoth_regions.lua mobile/spawn/serverobjects.lua mobile/hoth/serverobjects.lua \
         mobile/hoth/hoth_glacial_rancor.lua mobile/spawn/hoth/hoth_tauntaun_plains.lua mobile/spawn/hoth/hoth_mynock_fields.lua \
         mobile/spawn/hoth/hoth_wampa_flanks.lua mobile/spawn/hoth/hoth_imperial_zone.lua mobile/spawn/hoth/hoth_rebel_zone.lua \
         mobile/spawn/hoth/hoth_scavenger_zone.lua; do
  if luac5.3 -p "$f"; then echo "luac ok $f"; else echo "LUAC FAILED $f"; status=1; fi
done
exit $status
