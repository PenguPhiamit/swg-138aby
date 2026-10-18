from pathlib import Path
import collections,json,shutil
root=Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log')
for name,src in [('run6',root/'botpop-launch.jsonl'),('run2226',root/'botpop-launch.jsonl.2332.old')]+[(f'run{i}',Path(f'/opt/swg/agent/logs/botpop-launch-run{i}.jsonl')) for i in (1,2,3)]:
    dst=Path('/var/tmp/c47-'+name+'.jsonl'); shutil.copyfile(src,dst)
    counts=collections.Counter(); samples={}
    for line in dst.open():
        try:r=json.loads(line)
        except ValueError:continue
        counts[r.get('e')]+=1; samples[r.get('e')]=r
    print(name,dict(counts))
    if name=='run6':
        for k,v in samples.items():print(k,json.dumps(v))
for p in Path('/opt/swg/Core3-dev').rglob('BotPopLaunchBrain.h'):
    lines=p.read_text().splitlines()
    for i,l in enumerate(lines):
        if any('"'+k in l or '\\"'+k in l for k in ['mission_done','mission_gone','despawn','train','broke','loot','lair']):
            print(str(p),i+1,'\n'.join(lines[max(0,i-4):i+9]))
