#!/bin/bash
set -e
B=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/patch
T=$(mktemp -d); cd "$T"; git init -q .; git config user.email f@x; git config user.name f
mkdir -p MMOCoreORB/bin/scripts/managers; cp /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/resource_manager.lua MMOCoreORB/bin/scripts/managers/
git add -A; git commit -q -m base
git apply "$B/core3-r3-1-hoth-pools.patch" && git commit -q -am part1
git apply --check "$B/core3-r3-2-ossus-pools.patch" && echo "part-2 pool patch: git apply --check clean (on top of part 1)"
git apply "$B/core3-r3-2-ossus-pools.patch"; luac5.3 -p MMOCoreORB/bin/scripts/managers/resource_manager.lua && echo "luac ok"
lua5.3 -e 'dofile("MMOCoreORB/bin/scripts/managers/resource_manager.lua"); local h, o = 0, 0; for _, e in ipairs(minimumpoolincludes) do if e[1]:find("_hoth") then h = h + 1 end; if e[1]:find("_ossus") then o = o + 1 end end; print("minimum-pool entries: hoth", h, "ossus", o, "total", #minimumpoolincludes)'
cd /; rm -rf "$T"
