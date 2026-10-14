O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources2/work/orig
D=/opt/swg/Core3-dev
for f in MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.h MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp MMOCoreORB/src/server/zone/managers/resource/ResourceManagerImplementation.cpp MMOCoreORB/bin/scripts/managers/resource_manager.lua; do mkdir -p "$O/$(dirname $f)"; cp "$D/$f" "$O/$f"; file "$D/$f" | sed 's#.*/##'; done
cd $D && git status --porcelain -- MMOCoreORB/src/server/zone/managers/resource MMOCoreORB/bin/scripts/managers/resource_manager.lua; git rev-parse --short HEAD
echo "===== loop tail 176-200"; sed -n '176,200p' $D/MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp
echo "===== includes"; sed -n '1,40p' $D/MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp | grep -n '#include'
echo "===== ResourceTree getEntry"; grep -n 'getEntry' $D/MMOCoreORB/src/server/zone/managers/resource/resourcespawner/resourcetree/ResourceTree.h | head -3
