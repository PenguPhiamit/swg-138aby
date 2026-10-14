C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== survey list packet"; grep -n 'insert' $C/packets/resource/ResourceListForSurveyMessage.h | head -10
echo "===== getFinalClass users"; grep -rn 'getFinalClass()' $C --include=*.h --include=*.cpp | grep -v 'ResourceSpawnImplementation.cpp' | head -10
echo "===== tree entry display name"; grep -rn 'finalClass\|setFinalClass\|getStringField\|getValue(' $C/managers/resource/resourcespawner/resourcetree/ResourceTreeEntry.cpp $C/managers/resource/resourcespawner/resourcetree/ResourceTreeEntry.h $C/managers/resource/resourcespawner/resourcetree/ResourceTree.cpp 2>/dev/null | head -14
echo "===== spawner uses finalClass"; grep -n 'finalClass\|setFinalClass\|getFinalClass' $C/managers/resource/resourcespawner/ResourceSpawner.cpp | head -8
