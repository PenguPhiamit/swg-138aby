from pathlib import Path
p=Path('/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/botpop')
for f in p.glob('*'):
 if not f.is_file():continue
 lines=f.read_text().splitlines()
 for i,l in enumerate(lines):
  if any(x in l.lower() for x in ['despawn','simlog::instance()->write']):
   if 'despawn' in l.lower():print(f.name,i+1,'\n'.join(lines[max(0,i-2):i+5]))
