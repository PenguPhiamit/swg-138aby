from pathlib import Path
r=Path('/opt/swg/Core3-gpt/MMOCoreORB')
for gender in ('male','female'):
 p=r/f'bin/scripts/object/creature/player/hutt_{gender}.lua'
 s=p.read_text().replace('\tbaseHAM =', '\tspecies = 0xEA, -- CreatureObject::HUTT; MTG shared templates report Wookiee (4).\n\tbaseHAM =')
 p.write_text(s)
p=r/'src/server/zone/objects/creature/commands/SitServerCommand.h'
s=p.read_text().replace('You settle where you are.");\n\t\t\t\treturn SUCCESS;', 'You settle where you are.");\n\t\t\t\treturn setPlayerPosture(creature);')
p.write_text(s)
p=r/'src/server/zone/objects/creature/commands/MountCommand.h'
p.write_text(p.read_text().replace('A Hutt cannot ride this. Sell it, or give it to someone with legs.', 'That saddle was never built for a Hutt. A Hutt travels by repulsor platform.'))
p=r/'src/server/zone/objects/intangible/VehicleControlDeviceImplementation.cpp'
s=p.read_text()
mark='''	if (controlledObject == nullptr || controlledObject->getLocalZone() != nullptr) {
		return;
	}
'''
assert mark in s
s=s.replace(mark,mark+'''
	// C54: refuse before scheduling a call or spawning a vehicle the Hutt cannot ride.
	if (player->getSpecies() == CreatureObject::HUTT
			&& controlledObject->getObjectTemplate()->getFullTemplateString() != "object/mobile/vehicle/a1_deluxe_floater.iff") {
		player->sendSystemMessage("A Hutt cannot ride this. Sell it, or give it to someone with legs.");
		return;
	}
''',1)
p.write_text(s)
