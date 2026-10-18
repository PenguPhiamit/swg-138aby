from pathlib import Path
import re
for p in sorted(Path('/var/tmp').glob('core3-stacks*.txt')):
 print(p.name)
 s=p.read_text(errors='replace')
 selected=[]
 for block in re.split(r'(?=^Thread [0-9]+)',s,flags=re.M):
  if any(x in block for x in ['SpawnHelperDroidTask::run', 'AiAgentImplementation::executeBehavior', 'PetControlDeviceImplementation::callObject']):
   frames=[]
   for line in block.splitlines():
    if line.startswith('#'):
     func=re.sub(r'^#([0-9]+)\s+(?:0x[0-9a-f]+ in )?',r'#\1 ',line)
     func=func.split(' (')[0]
     loc=re.search(r' at (.*):([0-9]+)$',line)
     frames.append(func + (' at '+loc.group(1).split('/MMOCoreORB/')[-1]+':'+loc.group(2) if loc else ''))
   selected.append(frames[:24])
 print(selected[-8:])
