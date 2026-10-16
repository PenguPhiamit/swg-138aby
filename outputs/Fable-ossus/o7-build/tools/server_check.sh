#!/bin/bash
# Read-only: does each client template name have a server template in Core3-dev? (object/<path>/<name>.lua, without "shared_")
#   wsl -d Debian -u swgemu -- bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o7-build/tools/server_check.sh \
#       /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o7-build/out/server-templates.list > out/server-templates.txt
# Writes nothing under /opt/swg. Also prints the dev HEAD it read, so the result can be dated.
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "# server templates checked in $S on $(date '+%d %b %Y %I:%M %p'); dev HEAD $(git -C /opt/swg/Core3-dev rev-parse --short HEAD 2>/dev/null)"
while IFS= read -r t; do
  t="${t%$'\r'}"
  case "$t" in ''|\#*) continue;; esac
  s="${t//shared_/}"; s="${s%.iff}.lua"
  if [ -f "$S/$s" ]; then echo "ok $t"; else echo "MISSING-SERVER $t"; fi
done < "$1"
