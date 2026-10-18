import json
import sys
sys.path.insert(0, '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots')
from squad import Group, load_spec

g = Group('Aurek', load_spec()['groups']['Aurek'])
for b in g.bots:
    s = b.status()
    items = b.inventory().get('items', [])
    print(json.dumps(dict(bot=b.first, count=len(items), planet=s.get('planet'),
                         cell=s.get('cell'), position=[s.get(k) for k in ('x', 'y', 'z')],
                         medicine=[i for i in items if any(t in str(i.get('name'))
                           for t in ('cure', 'revive', 'enhance', 'fire_blanket', ':bank'))])), flush=True)
