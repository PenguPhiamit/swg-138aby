from pathlib import Path
import json,collections
p=Path('/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/botpop')
for f in p.glob('*.h'):
 lines=f.read_text().splitlines()
 for i,l in enumerate(lines):
  if any(x in l for x in ['launchRow("despawn','"despawn"','"stop"','bankSpentBefore','bankBefore =','bankSpent +=','launchRow("mission_none']): print(f.name,i+1,'\n'.join(lines[max(0,i-3):i+5]))
for n in ['run2226','run1','run3']:
 rows=[]
 for l in Path('/var/tmp/c47-'+n+'.jsonl').open():
  try:rows.append(json.loads(l))
  except ValueError:pass
 print(n,'first',rows[:2],'last',rows[-2:])
 for e in ['launch','train','mission_done','mission_gone','mission_abort','sell']:
  rs=[r for r in rows if r['e']==e];print(e,len(rs),rs[:1])
