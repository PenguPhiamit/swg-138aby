C=/opt/swg/Core3-dev/MMOCoreORB/src
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== resource_names in src"; grep -rn 'resource_names\|resource/resource' $C --include=*.cpp --include=*.h --include=*.idl | grep -v autogen | head -12
echo "===== ResourceSpawn name/type fields"; grep -n 'setObjectName\|displayName\|finalClass\|getFinalClass\|setFinalClass\|getType()' $C/server/zone/objects/resource/ResourceSpawnImplementation.cpp | head -12
echo "===== ResourceTree node names"; grep -n 'displayName\|setDisplayName\|getDisplayName\|CLASS\|getStringField\|getValue' $C/server/zone/managers/resource/ResourceTree.cpp $C/server/zone/managers/resource/ResourceTreeEntry.cpp $C/server/zone/managers/resource/ResourceTreeEntry.h 2>/dev/null | head -16
echo "===== survey results naming"; grep -rn 'finalClass\|getFinalClass\|getDisplayedName\|resource_names' $C/server/zone/managers/resource/ResourceManagerImplementation.cpp $C/server/zone/managers/resource/ResourceSpawner.cpp $C/server/zone/packets/resource/SurveyMessage.h $C/server/zone/objects/tangible/tool/SurveyToolImplementation.cpp 2>/dev/null | head -14
echo "===== resource container type name"; grep -rn 'finalClass\|getFinalClass\|resource_names\|getSpawnName\|getSpawnObject()->get' $C/server/zone/packets/resource/ResourceContainerObjectMessage*.h $C/server/zone/objects/resource/ResourceContainerImplementation.cpp 2>/dev/null | head -12
echo "===== scripts resource_names"; grep -rln 'resource_names' $S | head -5
