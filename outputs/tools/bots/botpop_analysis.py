"""Deeper analysis of the launch simulation (runs 2 and 3 from /opt/swg/agent/logs/botpop-launch-run*.jsonl): pacing,
hotspots, memory. Prints a compact digest for the findings write-up."""
import collections, glob, json, math, statistics, sys

CITIES = {'Mos Eisley': (3693, -4788), 'Bestine': (-1204, -3692), 'Mos Espa': (-2878, 2226), 'Mos Entha': (1344, 3149),
          'Anchorhead': (40, -5348), 'Coronet': (-178, -4504), 'Tyrena': (-5217, -2456), 'Bela Vistal': (6766, -5692),
          'Kor Vella': (-3420, 3146), 'Doaba Guerfel': (3240, 5391), 'Theed': (-5262, 4252), 'Moenia': (4786, -4729),
          'Keren': (1616, 2736), 'Kaadara': (5190, 6700), 'Dearic': (422, -3004), 'Nashal': (4348, 5245),
          'Narmle': (-5267, -2258), 'Restuss': (5318, 5680)}


def load(path):
    rows = []
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    return rows


def med(v):
    return round(statistics.median(v), 1) if v else None


def run(name, path):
    rows = load(path)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get('e')].append(r)
    t0 = min(r['t'] for r in by['spawn'])
    role = {r['bot']: r['role'] for r in by['spawn']}
    out = {'run': name, 'minutes': round((max(r['t'] for r in rows) - t0) / 60000)}

    # pacing: cumulative boxes per bot by role at 15-minute marks
    marks = list(range(15, out['minutes'] + 1, 15))
    count = collections.Counter(role.values())
    pace = {}
    for rl in count:
        series = []
        trains = sorted((t['t'] - t0) / 60000 for t in by['train'] if role.get(t['bot']) == rl)
        for m in marks:
            series.append(round(sum(1 for x in trains if x <= m) / count[rl], 2))
        pace[rl] = series
    out['pace_marks_min'] = marks
    out['boxes_per_bot_at_marks'] = pace
    # deepest boxes reached
    tiers = collections.Counter()
    for t in by['train']:
        s = t['skill']
        tiers[s[-2:] if s[-3] == '_' and s[-2:].isdigit() else ('novice' if s.endswith('novice') else 'other')] += 1
    out['boxes_by_tier'] = dict(tiers)
    out['xp_cost_median_by_tier'] = {k: med([t['xp_cost'] for t in by['train'] if t['skill'].endswith('_' + k)]) for k in ('01', '02', '03', '04')}

    # income: cash per bot over time (snapshots), credits per kill
    last = {}
    for s in by['snap']:
        last[s['bot']] = s
    cash = sum(s.get('cash', 0) + s.get('bank', 0) for s in last.values())
    out['credits_total'] = cash
    out['credits_per_kill'] = round(cash / max(len(by['kill']), 1), 2)
    out['credits_per_bot_hour'] = round(cash / len(last) / (out['minutes'] / 60), 1)
    costs = [t['cost'] for t in by['train']]
    out['training_cost_median'] = med(costs)
    out['training_cost_total'] = sum(costs)

    # danger: deaths by bot level; outliers (killer level >= bot level + 8) and where
    out['deaths_per_bot_hour'] = round(len(by['death']) / len(role) / (out['minutes'] / 60), 2)
    out['kills_per_hunter_hour'] = round(len(by['kill']) / sum(1 for r in role.values() if r in ('brawler', 'marksman', 'scout')) / (out['minutes'] / 60), 1)
    outl = collections.Counter()
    spots = collections.defaultdict(list)
    for d in by['death']:
        if d.get('klvl', 0) >= d.get('lvl', 1) + 8:
            outl[(d['killer'], d['klvl'])] += 1
            c = CITIES.get(d['city'])
            dist = int(math.hypot(d['x'] - c[0], d['y'] - c[1])) if c else None
            spots[(d['planet'], d['killer'], d['klvl'])].append((d['city'], dist, d['x'], d['y']))
    out['outlier_deaths'] = sum(outl.values())
    out['outlier_killers'] = [
        {'killer': k, 'lvl': lv, 'deaths': len(v), 'planet': p, 'near_city': collections.Counter(c for c, _, _, _ in v).most_common(1)[0][0],
         'median_dist_from_city_m': med([dd for _, dd, _, _ in v if dd is not None]),
         'example_xy': [v[0][2], v[0][3]]}
        for (p, k, lv), v in sorted(spots.items(), key=lambda kv: -len(kv[1]))[:12]]

    # spawn depletion: per city, minutes to the first widen and the first "nothing to hunt" move; kills per 15 min
    first = {}
    for w in by['widen']:
        first.setdefault(w['city'], round((w['t'] - t0) / 60000))
    moves = {}
    for tr in by['travel']:
        moves.setdefault(tr['city'], round((tr['t'] - t0) / 60000))
    kills_q = collections.defaultdict(lambda: [0] * (len(marks) + 1))
    for k in by['kill']:
        kills_q[k['city']][min(int((k['t'] - t0) / 900000), len(marks))] += 1
    out['depletion'] = {c: {'first_widen_min': first.get(c), 'first_move_min': moves.get(c), 'kills_per_15min': kills_q[c][:len(marks)]}
                        for c in CITIES if c in kills_q}

    # hotspots: 500 m squares with the most kills
    hot = collections.Counter((k['planet'], int(k['x'] // 500) * 500, int(k['y'] // 500) * 500) for k in by['kill'])
    out['kill_hotspots'] = [{'planet': p, 'x': x, 'y': y, 'kills': n} for (p, x, y), n in hot.most_common(8)]

    # combat: time to kill by weapon; aggressive creatures
    ttk = collections.defaultdict(list)
    for k in by['kill']:
        ttk[k.get('weapon', '?')].append(k['secs'])
    out['secs_to_kill_by_weapon'] = {w: [med(v), len(v)] for w, v in ttk.items()}
    out['aggressors'] = collections.Counter(a['by'] for a in by['aggro']).most_common(8)

    # support roles
    heals = [s.get('heals', 0) for s in last.values() if s['role'] == 'medic']
    out['heals_per_medic_hour'] = round(sum(heals) / max(len(heals), 1) / (out['minutes'] / 60), 1)
    out['rests'] = len(by['rested'])
    out['rests_watched'] = sum(1 for r in by['rested'] if r.get('watched'))
    return out


def host(paths):
    rows = []
    for p in paths:
        for l in open(p):
            try:
                rows.append(json.loads(l))
            except ValueError:
                pass  # a sample written while the server was restarting
    rows = [r for r in rows if (r.get('botpop') or {}).get('online') == 1500 and r.get('rss_mb')]
    segs, cur = [], []
    for r in rows:
        if cur and r['t'] - cur[-1]['t'] > 300:
            segs.append(cur)
            cur = []
        cur.append(r)
    if cur:
        segs.append(cur)
    out = []
    for s in segs:
        hours = (s[-1]['t'] - s[0]['t']) / 3600
        if hours < 0.2:
            continue
        out.append({'from': s[0]['t'], 'hours': round(hours, 2), 'rss_start': s[0]['rss_mb'], 'rss_end': s[-1]['rss_mb'],
                    'mb_per_hour': round((s[-1]['rss_mb'] - s[0]['rss_mb']) / hours), 'cores_median': med([r['cores'] for r in s if r.get('cores')]),
                    'wsl_free_min_mb': min(r['wsl_avail_mb'] for r in s), 'pass_ms_max': max((r['botpop'].get('pass_ms') or 0) for r in s)})
    return out


if __name__ == '__main__':
    result = {'runs': [run('run2', '/opt/swg/agent/logs/botpop-launch-run2.jsonl'), run('run3', '/opt/swg/agent/logs/botpop-launch-run3.jsonl')],
              'host': host(sorted(glob.glob('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Bot-reports/launch-sim/host-*.jsonl')))}
    json.dump(result, open(sys.argv[1], 'w'), indent=1)
    print(json.dumps(result)[:200])
