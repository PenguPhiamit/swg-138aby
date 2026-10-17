import json, math, collections
log = '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl'
piece = {}
for l in open('/root/pr/arr_pieces.txt'):
    if l.startswith('PIECE'):
        _, mesh, x, y, z, s, main = l.split(); piece[(mesh.split('_')[0], int(float(x)), int(float(y)))] = (int(s), int(main))
arr = {}; out = collections.defaultdict(lambda: [0, 0, None])
for line in open(log):
    if '"e":"travel_done"' in line:
        r = json.loads(line); arr[r['bot']] = r; out.pop(r['bot'], None)
    elif '"e":"snap"' in line or '"e":"travel_try"' in line:
        r = json.loads(line); a = arr.get(r['bot'])
        if a and r['t'] > a['t']:
            o = out[r['bot']]; o[0] = max(o[0], math.hypot(r['x'] - a['x'], r['y'] - a['y'])); o[1] = (r['t'] - a['t']) / 60000
            if r['e'] == 'travel_try': o[2] = 'travelled on'
res = collections.Counter()
for b, a in arr.items():
    pl = 'hutta' if a['to_planet'] == 'nal_hutta' else a['to_planet']
    s, main = piece.get((pl, a['x'], a['y']), (None, None))
    kind = 'not in a town mesh' if s is None else 'main mesh' if main else 'cut-off piece' if s >= 0 else 'no polygon'
    o = out.get(b, [0, 0, None])
    if o[1] < 10: continue
    res[(kind, 'left (>100 m)' if o[0] > 100 else 'travelled on' if o[2] else 'still there (<100 m)')] += 1
for k, v in sorted(res.items()): print('  %-22s %-22s %4d' % (k[0], k[1], v))
print('travel_done x,y is the landing? sample:', {k: arr[next(iter(arr))][k] for k in ('x', 'y', 'z', 'to_point', 'to_city', 'city')})
miss = collections.Counter()
for b, a in arr.items():
    pl = 'hutta' if a['to_planet'] == 'nal_hutta' else a['to_planet']
    if (pl, a['x'], a['y']) not in piece: miss[(a['planet'], a['to_point'])] += 1
print('not matched:', miss.most_common(8))
