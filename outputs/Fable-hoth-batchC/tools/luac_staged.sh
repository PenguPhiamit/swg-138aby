#!/bin/sh
# Parse the staged Lua files (and the append snippet) with luac5.3. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchC/tools/luac_staged.sh
cd "$(dirname "$0")/.." || exit 2
status=0
for f in staged/MMOCoreORB/bin/scripts/mobile/spawn/destroy_mission/hoth_destroy_missions.lua \
         staged/MMOCoreORB/bin/scripts/screenplays/poi/hoth_outpost_terminals.lua \
         staged/MMOCoreORB/bin/scripts/screenplays/tasks/hoth/scavenger_quartermaster.lua \
         staged/MMOCoreORB/bin/scripts/mobile/quest/hoth/scavenger_quartermaster_npcs.lua \
         snippets/mission_npc_spawn_points_hoth.lua; do
  if luac5.3 -p "$f"; then echo "luac ok $f"; else echo "LUAC FAILED $f"; status=1; fi
done
exit $status
