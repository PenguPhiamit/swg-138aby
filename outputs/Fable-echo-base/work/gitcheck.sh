#!/bin/bash
# git apply --check of patch/echo-base-e0.patch on a scratch repo holding the verbatim Core3-dev files, then luac on every Lua file touched.
set -e
P=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-echo-base/patch/echo-base-e0.patch
S=MMOCoreORB/bin/scripts
T=$(mktemp -d)
cd "$T"
git init -q .
git config user.email fable@example.invalid
git config user.name fable
for f in $S/screenplays/screenplays.lua $S/managers/planet/hoth_regions.lua $S/object/allobjects.lua $S/object/building/serverobjects.lua; do
  mkdir -p "$(dirname "$f")"
  cp "/opt/swg/Core3-dev/$f" "$f"
done
git add -A
git commit -q -m base
git apply --check "$P" && echo "git apply --check: clean"
git apply "$P"
git diff --stat HEAD
for f in $S/screenplays/screenplays.lua $S/managers/planet/hoth_regions.lua $S/object/allobjects.lua $S/object/building/serverobjects.lua $S/object/building/heroic/objects.lua $S/object/building/heroic/echo_base.lua $S/object/building/heroic/serverobjects.lua $S/screenplays/poi/hoth_echo_base.lua; do
  luac5.3 -p "$f" && echo "luac ok $f"
done
cd /
rm -rf "$T"
