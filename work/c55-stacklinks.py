from pathlib import Path
import re
for p in sorted(Path('/var/tmp').glob('core3-stacks*.txt')):
 print(p.name)
 for block in re.split(r'(?=^Thread [0-9]+)',p.read_text(errors='replace'),flags=re.M):
  if 'SpawnHelperDroidTask::run' not in block:
   continue
  print('thread', re.search(r'^Thread (\d+)', block).group(1))
  for line in block.splitlines():
   if 'Locker::Locker' in line or 'SpawnHelperDroidTask::run' in line:
    print(line)
