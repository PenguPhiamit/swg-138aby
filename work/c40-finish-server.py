from pathlib import Path
p=Path('/opt/swg/Core3-gpt/MMOCoreORB/src/client/agent/AgentControl.cpp')
s=p.read_text().replace('\t\tif (!usePath)\n\t\t\treturn moveTo','\t\t// Without a route or explicit height, NPC-height blending can select another floor.\n\t\tif (!usePath && !request.contains("z"))\n\t\t\treturn {{"ok", false}, {"error", "walking without z requires the /agentpath helper"}};\n\t\tif (cell != 0 && !request.contains("z"))\n\t\t\treturn {{"ok", false}, {"error", "cell destinations require a local z"}};\n\t\tif (!usePath)\n\t\t\treturn moveTo')
p.write_text(s)
p=Path('/opt/swg/Core3-gpt/MMOCoreORB/src/server/zone/objects/creature/commands/AgentPathCommand.h')
s=p.read_text().replace('route from our position; x/y/z are cell-local', 'route from our position; cellId 0 accepts world z; x/y/z are cell-local')
s=s.replace('Long outdoor legs get extra points every 8 m with the ground height, so the client can', "Long outdoor legs get extra points every 8 m on the floor nearest the route, so the client can")
# Indent the new conditional block without changing its logic.
a=s.index('\t\t\tManagedReference<SceneObject*> object = server->getZoneServer()->getObject(cellID);',s.index('JSONSerializationType findPath'))
b=s.index('\n\t\t\t}',a)
s=s[:a]+''.join('\t'+line+'\n' if line else '\n' for line in s[a:b].splitlines()).rstrip('\n')+s[b:]
p.write_text(s)
