#!/bin/bash
set -e
P=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o5/patch/ossus-first-look.patch
S=MMOCoreORB/bin/scripts
T=$(mktemp -d)
cd "$T"
git init -q .
git config user.email fable@example.invalid
git config user.name fable
for f in $S/managers/planet/planet_manager.lua $S/managers/resource_manager.lua $S/managers/planet/regions.lua; do
  mkdir -p "$(dirname "$f")"
  cp "/opt/swg/Core3-dev/$f" "$f"
done
git add -A
git commit -q -m base
git apply --check "$P" && echo "git apply --check: clean"
git apply "$P"
git diff --stat HEAD
for f in $S/managers/planet/planet_manager.lua $S/managers/resource_manager.lua $S/managers/planet/ossus_regions.lua; do
  luac5.3 -p "$f" && echo "luac ok $f"
done
cd $S && lua5.3 -e 'package.path = "./?.lua;" .. package.path; dofile("managers/planet/ossus_regions.lua"); print("ossus_regions rows", #ossus_regions)' 2>&1 | tail -1
cd /
rm -rf "$T"
grep -n 'TEST_ZONES' /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/test_galaxy.py | head -3
