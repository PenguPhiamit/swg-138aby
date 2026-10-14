set -u
B=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-mapnames
echo "== --check against Core3-dev"; bash $B/apply.sh --check | tail -4; echo "exit ${PIPESTATUS[0]}"
T=$(mktemp -d); mkdir -p $T/MMOCoreORB/bin/scripts/managers/planet
cp /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/hoth_regions.lua /opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/regions.lua $T/MMOCoreORB/bin/scripts/managers/planet/
echo "== apply on a scratch copy"; CORE3_DEV=$T bash $B/apply.sh | tail -5; echo "exit ${PIPESTATUS[0]}"
echo "== load the table with lua5.3 from the bin dir"; cd $T/MMOCoreORB/bin && lua5.3 -e '
package.path = "./?.lua;" .. package.path
dofile("scripts/managers/planet/hoth_regions.lua")
local n, named, byname = 0, 0, {}
for i, r in ipairs(hoth_regions) do n = n + 1; if r[5] & NAMEDREGION ~= 0 then named = named + 1 end; byname[r[1]] = (byname[r[1]] or 0) + 1 end
local dup = {}; for k, v in pairs(byname) do if v > 1 then dup[#dup+1] = k end end
print("rows", n, "named", named, "duplicate names", #dup, table.concat(dup, ","))
for i, r in ipairs(hoth_regions) do if r[1] == "@hoth_region_names:ice_caves" then print("ice_caves flags", r[5], "expected", NAMEDREGION + NOBUILDZONEAREA) end end
' 2>&1; rm -rf $T
