C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "===== resource_manager.lua"; cat $S/managers/resource_manager.lua | head -120
echo "===== ResourceCommand.h subcommands"; grep -n '"[a-z]*"\|args\|==' $C/objects/creature/commands/ResourceCommand.h | head -40
