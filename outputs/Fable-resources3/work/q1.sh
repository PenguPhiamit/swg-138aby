D=/opt/swg/Core3-dev; C=$D/MMOCoreORB/src/server/zone/managers/resource
cd $D && git log --oneline -3
O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/orig; mkdir -p $O/MMOCoreORB/bin/scripts/managers $O/tools/hoth
cp $D/MMOCoreORB/bin/scripts/managers/resource_manager.lua $O/MMOCoreORB/bin/scripts/managers/
cp /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_client_build.py $O/tools/hoth/
git status --porcelain -- MMOCoreORB/bin/scripts/managers/resource_manager.lua
echo "===== zone restriction derivation"; grep -n -B3 -A12 'zoneRestriction\|ZoneRestriction' $C/resourcespawner/resourcetree/ResourceTree.cpp | head -60
echo "===== NativePool spawn naming"; grep -n 'createResourceSpawn\|_\" +\|zone' $C/resourcespawner/resourcepool/NativePool.cpp | head -12
echo "===== poolScaleZones in lua/cpp (Claude's new scaling)"; grep -rn 'poolScaleZones' $D/MMOCoreORB/bin/scripts/managers/resource_manager.lua $C | head -6
echo "===== resource_manager pool lines"; grep -n 'hothType\|nativepoolincludes\|minimumpoolincludes = \|randompoolincludes = \|fixedpoolincludes' $D/MMOCoreORB/bin/scripts/managers/resource_manager.lua | cut -c1-160
