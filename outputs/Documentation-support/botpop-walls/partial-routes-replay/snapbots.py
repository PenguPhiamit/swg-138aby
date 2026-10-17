import json, sys
rows = {}
maxt = 0
for line in open('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl'):
    if '"e":"snap"' not in line: continue
    r = json.loads(line); rows[r['bot']] = r; maxt = max(maxt, r['t'])
out = open(sys.argv[1], 'w'); n = 0
for r in rows.values():
    if r['t'] >= maxt - 65000 and r['state'] not in ('dead',):
        out.write('%s %d %d %d\n' % ('hutta' if r['planet'] == 'nal_hutta' else r['planet'], r['x'], r['y'], r['z'])); n += 1
print('bots', n, 'at', maxt)
