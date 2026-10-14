#!/bin/sh
# Parse the staged Lua files with luac5.3. Run inside Debian:
#   sh /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/tools/luac_staged.sh
cd "$(dirname "$0")/../staged/MMOCoreORB/bin/scripts" || exit 2
status=0
for f in screenplays/screenplays.lua screenplays/poi/hoth_camps.lua screenplays/poi/hoth_mynock_den.lua; do
  if luac5.3 -p "$f"; then echo "luac ok $f"; else echo "LUAC FAILED $f"; status=1; fi
done
exit $status
