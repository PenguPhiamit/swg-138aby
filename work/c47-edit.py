from pathlib import Path
p=Path('outputs/tools/bots/botpop_analysis.py')
s=p.read_text(); s=s.replace('import collections, glob, json, math, statistics, sys','import argparse, collections, glob, json, math, statistics, sys\nfrom pathlib import Path')
pos=s.index('\ndef run(')
new='''
def gameplay_rows(rows, until_ms=None):
    """Discard final logout activity. Older logs have no explicit despawn row.

    For those logs the last full-population server sample is a conservative
    boundary when server.online first declines; up to one sample of play is lost.
    --until-ms supplies the known command time when the log ends before a decline.
    """
    rows = sorted(rows, key=lambda r: r['t'])
    cutoff, reason = until_ms, 'explicit --until-ms' if until_ms is not None else None
    online, previous = 0, None
    for r in rows:
        candidate = None
        if r.get('e') in ('despawn', 'stop', 'shutdown'):
            candidate = r['t']
        if r.get('e') == 'server':
            n = r.get('online', 0)
            if n < online and previous is not None:
                candidate = previous
            online = max(online, n)
            previous = r['t']
        if candidate is not None and (cutoff is None or candidate < cutoff):
            cutoff, reason = candidate, 'despawn marker or last full-population server sample'
    kept = [r for r in rows if cutoff is None or r['t'] < cutoff]
    return kept, {'cutoff_ms': cutoff, 'reason': reason, 'excluded_rows': len(rows)-len(kept),
                  'note': 'No despawn marker/online decline detected; use --until-ms if the final logout is not sampled.' if cutoff is None else 'Rows at/after the boundary excluded.'}


def summarize(rows, until_ms=None):
    rows, exclusion = gameplay_rows(rows, until_ms)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get('e')].append(r)
    spawn = {r['bot']: r for r in by['spawn']}
    end = max((r['t'] for r in rows), default=0)
    bot_hours = sum(max(0, end-r['t']) for r in spawn.values()) / 3600000
    first, last = {}, {}
    for r in by['snap']:
        if 'cash' in r and 'bank' in r:
            first.setdefault(r['bot'], r)
            last[r['bot']] = r
    # Track cash separately: trainers consume cash before bank. This recovers
    # old mission_gone rows whose bank delta hid the reward (review C44 F6).
    cash, bank_spent, pending = {}, collections.Counter(), {}
    outcomes, training = [], []
    for r in rows:
        b, e = r.get('bot'), r.get('e')
        if e == 'snap' and 'cash' in r:
            cash[b] = r['cash']
        elif e == 'sell' and b in cash:
            cash[b] = r.get('cash', cash[b] + r.get('credits', 0))
        elif e == 'train':
            charged = r.get('cost', 0) if 'spent' in r else 0
            withdrawal = None
            if b in cash:
                withdrawal = max(0, charged-cash[b])
                cash[b] = max(0, cash[b]-charged)
                bank_spent[b] += withdrawal
            training.append(dict(r, charged=charged, bank_withdrawal=withdrawal))
        elif e == 'mission_take':
            pending[b] = (r, bank_spent[b], len([t for t in training if t['bot'] == b and t['bank_withdrawal'] is None]))
        elif e in ('mission_done', 'mission_gone', 'mission_abort'):
            take, start_spent, unknown = pending.pop(b, ({}, bank_spent[b], 0))
            reward = r.get('reward', take.get('reward', 0))
            paid = max(0, r.get('paid', 0)) if e != 'mission_abort' else 0
            missing = sum(t['bot'] == b and t['bank_withdrawal'] is None for t in training) - unknown
            corrected = r.get('paid', 0) + bank_spent[b]-start_spent
            inferred = (e == 'mission_gone' and bool(take) and not missing
                        and reward > 0 and corrected == reward and paid < reward)
            # New mission_done rows already compensate withdrawals in the server.
            income = reward if inferred else paid
            success = e == 'mission_done' or inferred
            outcomes.append(dict(r, income=income, inferred=inferred, success=success,
                                 take_lvl=take.get('lvl', r.get('lvl')),
                                 mlvl=r.get('mlvl', take.get('mlvl')),
                                 secs=r.get('secs', (r['t']-take['t'])/1000 if take else None)))
    def rate(n, hours=bot_hours):
        return round(n/hours, 3) if hours else None
    def stats(v):
        return {'n': len(v), 'median': med(v), 'max': max(v) if v else None}
    bylevel = collections.defaultdict(list)
    for t in by['mission_take']:
        bylevel[(t.get('lvl'), t.get('mlvl'))].append(t)
    missions = []
    for (lvl, mlvl), takes in sorted(bylevel.items(), key=lambda kv: str(kv[0])):
        os = [o for o in outcomes if (o['take_lvl'], o['mlvl']) == (lvl, mlvl)]
        done = [o for o in os if o['success']]
        missions.append({'bot_level': lvl, 'mission_level': mlvl, 'taken': len(takes),
                         'success': len(done), 'resolved': len(os), 'pending': len(takes)-len(os),
                         'success_per_taken': len(done)/len(takes),
                         'success_per_resolved': len(done)/len(os) if os else None,
                         'finish_secs': stats([o['secs'] for o in done if o['secs'] is not None]),
                         'reward': stats([t['reward'] for t in takes if 'reward' in t]),
                         'offered': stats([t['offered'] for t in takes if 'offered' in t]),
                         'distance_m': stats([t['dist'] for t in takes if 'dist' in t])})
    # Snapshot reconciliation excludes creation money. Events are restricted to
    # each bot's first/last money snapshot so interval endpoints agree.
    window_hours = sum(r['t']-first[b]['t'] for b,r in last.items())/3600000
    def inside(r):
        b = r.get('bot')
        return b in first and first[b]['t'] < r['t'] <= last[b]['t']
    delta = sum(r['cash']+r['bank']-first[b]['cash']-first[b]['bank'] for b,r in last.items())
    spend = sum(t['charged'] for t in training if inside(t))
    mission_window = sum(o['income'] for o in outcomes if inside(o))
    junk_window = sum(r.get('credits', 0) for r in by['sell'] if inside(r))
    residual = delta+spend-mission_window-junk_window
    deaths = collections.Counter((r.get('lvl'),r.get('klvl')) for r in by['death'])
    refused = {(r['bot'],r.get('skill')) for r in by['broke']}
    seen = collections.Counter((r.get('planet'),r.get('kind'),r.get('name')) for r in by['seen'])
    return {'bot_hours': round(bot_hours, 4), 'exclusion': exclusion,
            'event_counts': dict(collections.Counter(r.get('e') for r in rows)),
            'income': {'missions': {'credits': sum(o['income'] for o in outcomes), 'per_bot_hour': rate(sum(o['income'] for o in outcomes))},
                       'junk': {'credits': sum(r.get('credits',0) for r in by['sell']), 'per_bot_hour': rate(sum(r.get('credits',0) for r in by['sell']))},
                       'loot_residual': {'credits': residual, 'per_bot_hour': rate(residual,window_hours), 'bot_hours': round(window_hours,4)},
                       'method': 'Missions/junk: event totals divided by summed time from each spawn to cutoff. Loot: first-to-last cash+bank snapshot change + charged training - mission income - junk within those same snapshot windows; excludes creation purse; residual may include other unlogged flows, and negative values indicate unreconciled flows.',
                       'mission_inferred_count': sum(o['inferred'] for o in outcomes),
                       'mission_inferred_credits': sum(o['income'] for o in outcomes if o['inferred']),
                       'inference': 'mission_done uses logged paid. For an old mission_gone, infer reward only when logged paid + bank-funded training since its matched mission_take equals reward exactly. Trainers use snapshot cash first, then bank; unknown cash prevents inference. Unmatched/ambiguous gone rows remain unresolved, never assumed paid.'},
            'training': {'spent': sum(t['charged'] for t in training), 'nominal_cost': sum(t.get('cost',0) for t in training),
                         'charged_boxes': sum('spent' in t for t in training), 'legacy_free_boxes': sum('spent' not in t for t in training),
                         'refusal_rows': len(by['broke']), 'refused_bot_boxes': len(refused), 'bots_refused': len({b for b,s in refused})},
            'missions_by_level': missions,
            'mission_outcomes': dict(collections.Counter('inferred_paid' if o['inferred'] else o['e'] for o in outcomes)),
            'lair_from_spot_m': stats([r['from_spot'] for r in by['lair'] if 'from_spot' in r]),
            'lair_find_secs': stats([r['secs'] for r in by['lair'] if 'secs' in r]),
            'lairs_by_name': dict(collections.Counter(r.get('lair','?') for r in by['lair'])),
            'deaths_by_levels': [{'bot_level': b, 'killer_level': k, 'deaths': n} for (b,k),n in sorted(deaths.items(),key=lambda kv:str(kv[0]))],
            'deaths': len(by['death']), 'deaths_per_bot_hour': rate(len(by['death'])),
            'killer_at_least_8_above': sum(n for (b,k),n in deaths.items() if b is not None and k is not None and k>=b+8),
            'census': [{'planet': p, 'kind': k, 'name': n, 'observations': count} for (p,k,n),count in sorted(seen.items(),key=lambda kv:str(kv[0]))],
            'explorers_requested': sum(r.get('n',0) for r in by['explore'])}

'''
s=s[:pos]+new+s[pos:];s=s.replace('def run(name, path):\n    rows = load(path)','def run(name, path, until_ms=None):\n    raw = load(path)\n    summary = summarize(raw, until_ms)\n    rows, _ = gameplay_rows(raw, until_ms)\n    if not any(r.get("e") == "spawn" for r in rows):\n        return dict(run=name, **summary)')
s=s.replace("s[-3] == '_'", "len(s) >= 3 and s[-3] == '_'")
s=s.replace("out['minutes'] / 60", "max(out['minutes'] / 60, 1e-9)")
s=s.replace("/ len(last) /", "/ max(len(last), 1) /")
s=s.replace("/ sum(1 for r in role.values() if r in ('brawler', 'marksman', 'scout')) /", "/ max(sum(1 for r in role.values() if r in ('brawler', 'marksman', 'scout')), 1) /")
s=s.replace("    return out\n\n\ndef host", "    out.update(summary)\n    return out\n\n\ndef host",1)
s=s[:s.index("if __name__ == '__main__':")]+'''def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', nargs='?', default=str(Path(__file__).resolve().parents[2]/'Bot-reports/launch-sim/analysis.json'))
    parser.add_argument('--run', action='append', metavar='NAME=PATH', help='Repeat to override the default five runs')
    parser.add_argument('--until-ms', type=int, help='Known final despawn time (applies to run6, or all explicitly supplied runs)')
    parser.add_argument('--host', action='append', help='Host sample file (repeatable)')
    parser.add_argument('--numbers-out', help='Also generate the run6 Markdown report in this one command')
    args = parser.parse_args(argv)
    default = [('run1', '/opt/swg/agent/logs/botpop-launch-run1.jsonl'),
               ('run2', '/opt/swg/agent/logs/botpop-launch-run2.jsonl'),
               ('run3', '/opt/swg/agent/logs/botpop-launch-run3.jsonl'),
               ('run2226', '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl.2332.old'),
               ('run6', '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl')]
    paths = [x.split('=',1) for x in args.run] if args.run else default
    host_paths = args.host or sorted(glob.glob(str(Path(__file__).resolve().parents[2]/'Bot-reports/launch-sim/host-*.jsonl')))
    result = {'runs': [run(n,p,args.until_ms if args.run or n=='run6' else None) for n,p in paths], 'host': host(host_paths)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1)+'\\n', encoding='utf-8')
    if args.numbers_out:
        from botpop_report import report
        current = next((p for n,p in paths if n=='run6'), paths[-1][1])
        comparisons = [(n,load(p)) for n,p in paths if p != current]
        Path(args.numbers_out).write_text(report(load(current), [r for p in host_paths for r in load(p)], args.until_ms, comparisons), encoding='utf-8')
    print(f'wrote {args.out}: {len(result["runs"])} runs')


if __name__ == '__main__':
    main()
'''
p.write_bytes(s.replace('\n','\r\n').encode())
