# travel_done rows -> arrivals file for the replay; and how far each arrived bot got from its landing point since
import json, math, collections, sys
log = '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl'
arr = {}; last = {}; maxt = 0
for line in open(log):
    if '"e":"travel_done"' in line:
        r = json.loads(line); arr[r['bot']] = r
    elif '"e":"snap"' in line:
        r = json.loads(line); maxt = max(maxt, r['t'])
        if r['bot'] in arr and r['t'] > arr[r['bot']]['t']:
            a = arr[r['bot']]
            d = math.hypot(r['x'] - a['x'], r['y'] - a['y'])
            p = last.setdefault(r['bot'], [0, 0, None])
            p[0] = max(p[0], d); p[1] = (r['t'] - a['t']) / 60000; p[2] = r
print('arrivals', len(arr), 'keys', sorted(next(iter(arr.values())).keys()))
with open(sys.argv[1], 'w') as f:
    for r in arr.values():
        f.write('%s %d %d %d\n' % ('hutta' if r['to_planet'] == 'nal_hutta' else r['to_planet'], r['x'], r['y'], r.get('z', 0)))
far = collections.Counter()
for b, (d, mins, r) in last.items():
    if mins < 10: continue
    far['<10 m' if d < 10 else '<50 m' if d < 50 else '<200 m' if d < 200 else '200 m+'] += 1
print('arrived 10+ min ago, furthest from the landing point since:', dict(far))
byc = collections.Counter((r['planet'], r.get('city'), r['x'] // 20 * 20, r['y'] // 20 * 20) for r in arr.values())
for k, v in byc.most_common(12): print('  ', v, k)
