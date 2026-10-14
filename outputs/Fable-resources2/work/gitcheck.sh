#!/bin/bash
# git apply --check of cpp/resource-backfill.patch on a scratch repo holding the verbatim Core3-dev files.
set -e
P=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources2/cpp/resource-backfill.patch
T=$(mktemp -d)
cd "$T"
git init -q .
git config user.email fable@example.invalid
git config user.name fable
for f in MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.h \
         MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp \
         MMOCoreORB/src/server/zone/managers/resource/ResourceManagerImplementation.cpp \
         MMOCoreORB/bin/scripts/managers/resource_manager.lua; do
  mkdir -p "$(dirname "$f")"
  cp "/opt/swg/Core3-dev/$f" "$f"
done
git add -A
git commit -q -m base
git apply --check "$P" && echo "git apply --check: clean"
git apply "$P"
git diff --stat
luac5.3 -p MMOCoreORB/bin/scripts/managers/resource_manager.lua && echo "luac ok"
cd /
rm -rf "$T"
