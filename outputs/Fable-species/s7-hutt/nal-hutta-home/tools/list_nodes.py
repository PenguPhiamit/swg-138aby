import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hutta_common import ws_nodes, yaw_of, size_xz
pat = sys.argv[1]
nodes, _ = ws_nodes()
for n in nodes:
    if n['depth'] == 0 and pat in n['template']:
        print(n['id'], n['template'].split('/')[-1], round(n['x'], 1), round(n['y'], 1), round(n['z'], 1), round(yaw_of(n['quat'])), [round(v, 1) for v in size_xz(n['template'])])
