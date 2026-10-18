import sys,json
sys.path.insert(0, '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots')
from squad import Group,load_spec
g=Group('Aurek',load_spec()['groups']['Aurek']);b=g.leader
print('recover',b.recover())
print('status', {k:v for k,v in b.status().items() if k in ('planet','x','y','z','cell','me')})
for name in ('kreetle','worrt','scurrier','rill'):
 print(name,json.dumps(b.locate(name,1200)))
