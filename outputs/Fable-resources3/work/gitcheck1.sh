#!/bin/bash
set -e
B=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/patch
T=$(mktemp -d); cd "$T"; git init -q .; git config user.email f@x; git config user.name f
mkdir -p MMOCoreORB/bin/scripts/managers; cp /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/resource_manager.lua MMOCoreORB/bin/scripts/managers/
git add -A; git commit -q -m base
git apply --check "$B/core3-r3-1-hoth-pools.patch" && echo "core3 patch: git apply --check clean"
git apply "$B/core3-r3-1-hoth-pools.patch"; luac5.3 -p MMOCoreORB/bin/scripts/managers/resource_manager.lua && echo "luac ok resource_manager.lua"
lua5.3 -e 'dofile("MMOCoreORB/bin/scripts/managers/resource_manager.lua"); local n = 0; for _, e in ipairs(minimumpoolincludes) do if e[1]:find("_hoth") then n = n + 1 end end; print("hoth minimum-pool entries", n)'
cd /; rm -rf "$T"
T=$(mktemp -d); cd "$T"; git init -q .; git config user.email f@x; git config user.name f
mkdir -p outputs/tools/hoth; cp /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_client_build.py outputs/tools/hoth/
git add -A; git commit -q -m base
git apply --check "$B/h-r3-1-hoth_client_build.patch" && echo "h patch: git apply --check clean"
cd /; rm -rf "$T"
