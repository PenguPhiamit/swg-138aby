from pathlib import Path
r=Path('/opt/swg/Core3-gpt/MMOCoreORB')
p=r/'bin/scripts/object/intangible/vehicle/a1_deluxe_floater_pcd.lua'
p.write_text(p.read_text().replace('\n\ttemplateType = VEHICLECONTROLDEVICE,',''))
p=r/'src/server/zone/managers/name/NameManager.cpp'
p.write_text(p.read_text().replace('\t\tdelete humanData;\n\tdelete huttData;', '\t\tdelete humanData;\n\t\tdelete huttData;'))
