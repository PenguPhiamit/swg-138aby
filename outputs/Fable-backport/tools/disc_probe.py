"""Probe a few disc archives: header magic/version and first entry names. Read-only."""
import os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')
with open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8') as f:
    exec(f.read().split('if __name__')[0])
DISC = '/opt/swg/disc-extracted/SWG-group/files/SWG'
for name in sys.argv[1:]:
    p = os.path.join(DISC, name)
    with open(p, 'rb') as f:
        head = f.read(36)
    magic, version, count = struct.unpack('<4s4sI', head[:12])
    print(name, magic, version, 'count', count)
    try:
        entries = read_tre(p)
        print('  read_tre entries:', len(entries))
        for e in entries[:8]:
            print('   ', e['name'])
        objs = [e['name'] for e in entries if e['name'].lower().startswith('object/')]
        print('  object/ entries:', len(objs), objs[:3])
    except Exception as exc:
        print('  read_tre failed:', exc)
