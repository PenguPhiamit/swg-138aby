#!/bin/sh
# git apply --check + luac for the C29 pool patch in a throw-away repo (never in h/ or /opt/swg). Run: wsl -d Debian -e sh gitcheck.sh
set -e
L=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/lore
T=$(mktemp -d)
cd "$T"
git init -q .
mkdir -p MMOCoreORB/bin/scripts/managers
cp "$L/work/orig/MMOCoreORB/bin/scripts/managers/resource_manager.lua" MMOCoreORB/bin/scripts/managers/resource_manager.lua
git add -A && git -c user.name=f -c user.email=f@f commit -q -m base
git apply --check "$L/patch/core3-c29-lore-pools.patch" && echo "git apply --check: ok"
git apply "$L/patch/core3-c29-lore-pools.patch"
luac5.3 -p MMOCoreORB/bin/scripts/managers/resource_manager.lua && echo "luac5.3 -p: ok"
grep -c 'loreType' MMOCoreORB/bin/scripts/managers/resource_manager.lua
cd /
rm -rf "$T"
echo "scratch removed"
