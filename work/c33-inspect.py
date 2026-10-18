import sys
sys.path.insert(0, '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots')
from squad import Group, load_spec
import json
g=Group('Aurek',load_spec()['groups']['Aurek'])
print(json.dumps(g.leader.inventory(),indent=2))
