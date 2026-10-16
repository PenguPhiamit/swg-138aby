"""Launch simulation analysis: pacing, income, training, missions, level gates, census and memory.

From outputs/ (WSL, as swgemu):    python3 tools/bots/botpop_analysis.py
It finds the logs itself (runs 1-3 in /opt/swg/agent/logs, the rotated botpop-launch.jsonl.*.old files and the current
log), writes Bot-reports/launch-sim/analysis.json and numbers-<newest run>.md, and compares every run with the newest.
--list shows what it found; --run NAME=PATH (repeatable) overrides the inputs; --until-ms gives the despawn time when
the log does not show it. Read-only on the server; about 30 seconds.

Run names (RUN_STARTS) come from each log's first row: run1-3 in the agent folder, run4b 22:11, run5 22:26 (110,000 purse),
run6 23:32, run7 23:53 (100 cash / 1,000 bank, training x0.25, spawn level gate, missions near level). The server renames
a finished log to botpop-launch.jsonl.<HHMM>.old when the next run starts, so a file's suffix is one run behind.

The final despawn is dropped from every table (gameplay_rows): the earliest of --until-ms, a despawn row, the last server
row before online falls 5%, the last host sample before logouts, or a final burst of 5+ mission_gone rows in one second
with no bot row after it. Loot income is a residual (snapshot change + training - missions - junk), not a logged flow.
Tests: python3 -m unittest discover -s tools/bots -p test_botpop_reports.py
"""
import argparse, collections, glob, json, math, os, statistics, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIM = HERE.parents[1] / 'Bot-reports' / 'launch-sim'
LOG_DIR = '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log'
AGENT_LOGS = '/opt/swg/agent/logs'
# The owner's run numbers, by the first row's time (epoch seconds, matched within 5 minutes). The server renames a
# finished log to botpop-launch.jsonl.<HHMM>.old when the next run starts, so that suffix is one run behind.
RUN_STARTS = {'run1': 1792109351, 'run2': 1792110823, 'run3': 1792121224, 'run4': 1792127069, 'run4b': 1792127472,
              'run5': 1792128364, 'run6': 1792132336, 'run7': 1792133596}
BURST_PER_SECOND = 5  # mission_gone rows in one second that mark the final despawn
GAP_BUCKETS = [('<= 0', None, 0), ('1-2', 1, 2), ('3-4', 3, 4), ('5-7', 5, 7), ('8-11', 8, 11), ('12+', 12, None)]

CITIES = {'Mos Eisley': (3693, -4788), 'Bestine': (-1204, -3692), 'Mos Espa': (-2878, 2226), 'Mos Entha': (1344, 3149),
          'Anchorhead': (40, -5348), 'Coronet': (-178, -4504), 'Tyrena': (-5217, -2456), 'Bela Vistal': (6766, -5692),
          'Kor Vella': (-3420, 3146), 'Doaba Guerfel': (3240, 5391), 'Theed': (-5262, 4252), 'Moenia': (4786, -4729),
          'Keren': (1616, 2736), 'Kaadara': (5190, 6700), 'Dearic': (422, -3004), 'Nashal': (4348, 5245),
          'Narmle': (-5267, -2258), 'Restuss': (5318, 5680)}


def load(path):
    rows = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def med(v):
    return round(statistics.median(v), 1) if v else None


def quantile(v, q):
    v = sorted(v)
    return round(v[min(len(v)-1, int(q*len(v)))], 1) if v else None


def stats(v):
    return {'n': len(v), 'median': med(v), 'p90': quantile(v, .9), 'max': round(max(v), 1) if v else None}


def ksort(key):
    """Sort key for level keys that may be None or tuples (None last)."""
    return tuple((x is None, x if x is not None else 0) for x in (key if isinstance(key, tuple) else (key,)))


def declined(peak, n):
    """True when the online count fell by 5% of its peak (at least one bot): a despawn, not a bot or two logging out."""
    return peak > 0 and peak-n >= max(1, .05*peak)


def host_cutoff(rows, samples):
    """Conservative last host sample before logout, limited to this event file."""
    if not rows:
        return None
    start, end = min(r['t'] for r in rows), max(r['t'] for r in rows)
    previous, peak, base_out = None, 0, None
    for r in sorted(samples, key=lambda r:r['t']):
        t = r['t'] * 1000
        if not start <= t <= end + 60000:
            continue
        pop = r.get('botpop') or {}
        n = pop.get('online')
        if n is None:
            continue
        big = max(1, .05*peak)
        out = pop.get('logged_out_total', 0)
        base_out = out if base_out is None else base_out
        if previous is not None and (pop.get('leaving',0) >= big or pop.get('queued_logout',0) >= big
                                     or out-base_out >= big or declined(peak, n)):
            return previous
        peak, previous = max(peak,n), t
    return None


def despawn_burst(rows):
    """Time (ms) of the first row of a final despawn burst, else None. Rows must be sorted by time.

    Logging the bots out empties every datapad at once: each bot with a mission writes mission_gone in the same second
    or two, and no bot row follows. It takes BURST_PER_SECOND rows in one second and no bot activity after the burst's
    own second, so a few ordinary mission_gone rows in a live run never match.
    """
    gone = [r['t'] for r in rows if r.get('e') == 'mission_gone']
    if not gone:
        return None
    i = len(gone)-1
    while i > 0 and gone[i]-gone[i-1] <= 2000:
        i -= 1
    burst = gone[i:]
    if max(collections.Counter(t//1000 for t in burst).values()) < BURST_PER_SECOND:
        return None
    last_bot_row = max((r['t'] for r in rows if 'bot' in r), default=0)
    return burst[0] if last_bot_row-burst[-1] <= 5000 else None


def gameplay_rows(rows, until_ms=None):
    """Discard final logout activity.

    Boundary = the earliest of: --until-ms, a despawn/stop row, the last server row before online falls by 5%, a final
    burst of mission_gone rows (despawn_burst), or the last host sample before logouts (host_cutoff, applied by the
    callers). Older logs have no explicit despawn row; the server-row boundary can lose up to one sample of play.
    """
    rows = sorted(rows, key=lambda r: r['t'])
    cutoff, reason = until_ms, 'explicit cutoff or last host sample before logout' if until_ms is not None else None
    online, previous = 0, None
    for r in rows:
        candidate = None
        if r.get('e') in ('despawn', 'stop', 'shutdown'):
            candidate = r['t']
        if r.get('e') == 'server':
            n = r.get('online', 0)
            if previous is not None and declined(online, n):
                candidate = previous
            online = max(online, n)
            previous = r['t']
        if candidate is not None and (cutoff is None or candidate < cutoff):
            cutoff, reason = candidate, 'despawn marker or last full-population server sample'
    burst = despawn_burst(rows)
    if burst is not None and (cutoff is None or burst < cutoff):
        cutoff, reason = burst, 'final burst of mission_gone rows (despawn)'
    kept = [r for r in rows if cutoff is None or r['t'] < cutoff]
    dropped = rows[len(kept):]
    return kept, {'cutoff_ms': cutoff, 'reason': reason, 'excluded_rows': len(dropped),
                  'excluded_mission_gone': sum(r.get('e') == 'mission_gone' for r in dropped),
                  'note': 'No despawn marker, mission_gone burst or event/host logout boundary detected; use --until-ms if the final logout is not sampled.' if cutoff is None else 'Rows at/after the boundary excluded.'}


def summarize(rows, until_ms=None):
    rows, exclusion = gameplay_rows(rows, until_ms)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get('e')].append(r)
    spawn = {r['bot']: r for r in by['spawn']}
    role_of = {}
    for r in rows:
        if r.get('bot') is not None and r.get('role'):
            role_of.setdefault(r['bot'], r['role'])
    start = min((r['t'] for r in spawn.values()), default=0)
    end = max((r['t'] for r in rows), default=0)
    hours_of = {b: max(0, end-r['t'])/3600000 for b, r in spawn.items()}
    bot_hours = sum(hours_of.values())
    first, last = {}, {}
    for r in by['snap']:
        if 'cash' in r and 'bank' in r:
            first.setdefault(r['bot'], r)
            last[r['bot']] = r
    # Track cash separately: trainers consume cash before bank. This recovers
    # old mission_gone rows whose bank delta hid the reward (review C44 F6).
    cash, bank_spent, pending = {}, collections.Counter(), {}
    unknown_training = collections.Counter()
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
            if withdrawal is None:
                unknown_training[b] += 1
            training.append(dict(r, charged=charged, bank_withdrawal=withdrawal))
        elif e == 'mission_take':
            pending[b] = (r, bank_spent[b], unknown_training[b])
        elif e in ('mission_done', 'mission_gone', 'mission_abort'):
            take, start_spent, unknown = pending.pop(b, ({}, bank_spent[b], 0))
            reward = r.get('reward', take.get('reward', 0))
            paid = max(0, r.get('paid', 0)) if e != 'mission_abort' else 0
            missing = unknown_training[b] - unknown
            corrected = r.get('paid', 0) + bank_spent[b]-start_spent
            inferred = (e in ('mission_done', 'mission_gone') and bool(take) and not missing
                        and reward > 0 and corrected == reward and paid < reward)
            # From run 7 the server adds the bank-funded training back into mission_done.paid.
            income = reward if inferred else paid
            success = e == 'mission_done' or inferred
            outcomes.append(dict(r, income=income, inferred=inferred, success=success, matched=bool(take),
                                 role=role_of.get(b), take_lvl=take.get('lvl', r.get('lvl')),
                                 mlvl=r.get('mlvl', take.get('mlvl')),
                                 secs=r.get('secs', (r['t']-take['t'])/1000 if take else None)))
    def rate(n, hours=bot_hours):
        return round(n/hours, 3) if hours else None

    # Missions: one row per group of accepted missions and the outcomes matched to them.
    takes = by['mission_take']
    matched = [o for o in outcomes if o['matched']]
    def mission_row(ts, os):
        success = [o for o in os if o['success']]
        minutes = [o['secs']/60 for o in success if o['secs'] is not None]
        return {'taken': len(ts), 'done': sum(o['e'] == 'mission_done' for o in os), 'success': len(success),
                'gone': sum(o['e'] == 'mission_gone' and not o['inferred'] for o in os),
                'aborted': sum(o['e'] == 'mission_abort' for o in os), 'resolved': len(os),
                'pending': max(0, len(ts)-len(os)),
                'success_per_taken': len(success)/len(ts) if ts else None,
                'success_per_resolved': len(success)/len(os) if os else None,
                'finish_secs': stats([o['secs'] for o in success if o['secs'] is not None]),
                'finish_minutes': stats(minutes),
                'reward': stats([t['reward'] for t in ts if 'reward' in t]),
                'offered': stats([t['offered'] for t in ts if 'offered' in t]),
                'distance_m': stats([t['dist'] for t in ts if 'dist' in t])}
    def mission_table(take_key, out_key):
        groups = {}
        for t in takes:
            groups.setdefault(take_key(t), ([], []))[0].append(t)
        for o in matched:
            if out_key(o) in groups:
                groups[out_key(o)][1].append(o)
        return [(k, mission_row(ts, os)) for k, (ts, os) in sorted(groups.items(), key=lambda kv: ksort(kv[0]))]
    def gap(lvl, mlvl):
        return mlvl-lvl if lvl is not None and mlvl is not None else None
    cells = [dict(row, bot_level=k[0], mission_level=k[1]) for k, row in
             mission_table(lambda t: (t.get('lvl'), t.get('mlvl')), lambda o: (o['take_lvl'], o['mlvl']))]
    by_bot_level = [dict(row, bot_level=k) for k, row in mission_table(lambda t: t.get('lvl'), lambda o: o['take_lvl'])]
    by_mission_level = [dict(row, mission_level=k) for k, row in mission_table(lambda t: t.get('mlvl'), lambda o: o['mlvl'])]
    by_gap = [dict(row, level_gap=k) for k, row in mission_table(lambda t: gap(t.get('lvl'), t.get('mlvl')),
                                                                 lambda o: gap(o['take_lvl'], o['mlvl']))]
    by_mission_role = [dict(row, role=k) for k, row in mission_table(lambda t: role_of.get(t.get('bot')), lambda o: o['role'])]

    # Snapshot reconciliation excludes creation money. Events are restricted to
    # each bot's first/last money snapshot so interval endpoints agree.
    window = {b: (r['t']-first[b]['t'])/3600000 for b, r in last.items()}
    window_hours = sum(window.values())
    def inside(r):
        b = r.get('bot')
        return b in first and first[b]['t'] < r['t'] <= last[b]['t']
    # loot residual = snapshot change + charged training - mission income - junk, per bot in its own window
    resid = {b: r['cash']+r['bank']-first[b]['cash']-first[b]['bank'] for b, r in last.items()}
    for t in training:
        if inside(t):
            resid[t['bot']] += t['charged']
    for o in outcomes:
        if inside(o):
            resid[o['bot']] -= o['income']
    for s in by['sell']:
        if inside(s):
            resid[s['bot']] -= s.get('credits', 0)
    residual = sum(resid.values())
    income_total = lambda key, rs: sum(r.get(key, 0) for r in rs)

    deaths = by['death']
    known = [d for d in deaths if d.get('klvl') and d.get('lvl') is not None]
    gaps = collections.Counter(d['klvl']-d['lvl'] for d in known)
    gap_buckets = {label: sum(n for g, n in gaps.items() if (lo is None or g >= lo) and (hi is None or g <= hi))
                   for label, lo, hi in GAP_BUCKETS}
    level_pairs = collections.Counter((r.get('lvl'), r.get('klvl')) for r in deaths)
    leaks = collections.Counter((d.get('killer') or '?', d['klvl'], d.get('planet')) for d in known if d['klvl']-d['lvl'] >= 8)
    refused = {(r['bot'], r.get('skill')) for r in by['broke']}
    refused_bots = collections.defaultdict(set)
    for b, skill in refused:
        refused_bots[skill].add(b)
    seen = collections.Counter((r.get('planet'), r.get('kind'), r.get('name')) for r in by['seen'])

    by_role = {}
    for role in sorted({role_of[b] for b in spawn if role_of.get(b)}):
        bots = {b for b in spawn if role_of.get(b) == role}
        hours, win = sum(hours_of[b] for b in bots), sum(window.get(b, 0) for b in bots)
        mission = sum(o['income'] for o in outcomes if o['bot'] in bots)
        junk = sum(r.get('credits', 0) for r in by['sell'] if r['bot'] in bots)
        loot = sum(resid.get(b, 0) for b in bots)
        trained = [t for t in training if t['bot'] in bots]
        broke = {p for p in refused if p[0] in bots}
        by_role[role] = {'bots': len(bots), 'bot_hours': round(hours, 4),
                         'missions': {'credits': mission, 'per_bot_hour': rate(mission, hours)},
                         'junk': {'credits': junk, 'per_bot_hour': rate(junk, hours)},
                         'loot_residual': {'credits': loot, 'per_bot_hour': rate(loot, win), 'bot_hours': round(win, 4)},
                         'income_per_bot_hour': round(sum(x for x in (rate(mission, hours), rate(junk, hours), rate(loot, win)) if x), 3),
                         'training_spent': sum(t['charged'] for t in trained), 'training_per_bot_hour': rate(sum(t['charged'] for t in trained), hours),
                         'boxes': len(trained), 'refused_bot_boxes': len(broke), 'refused_bots': len({b for b, s in broke}),
                         'kills': sum(r['bot'] in bots for r in by['kill']), 'deaths': sum(r['bot'] in bots for r in deaths),
                         'incaps': sum(r['bot'] in bots for r in by['incap']),
                         'missions_taken': sum(r['bot'] in bots for r in takes)}
    shortfall = [r['cost']-r['credits'] for r in by['broke'] if 'cost' in r and 'credits' in r]
    return {'bot_hours': round(bot_hours, 4), 'exclusion': exclusion, 'start_ms': start, 'end_ms': end,
            'minutes': round((end-start)/60000, 1) if start else 0, 'bots': len(spawn),
            'role_counts': dict(collections.Counter(role_of.get(b) for b in spawn)),
            'purse_median': med([r['cash']+r['bank'] for r in first.values()]),
            'event_counts': dict(collections.Counter(r.get('e') for r in rows)),
            'income': {'missions': {'credits': sum(o['income'] for o in outcomes), 'per_bot_hour': rate(sum(o['income'] for o in outcomes))},
                       'junk': {'credits': income_total('credits', by['sell']), 'per_bot_hour': rate(income_total('credits', by['sell']))},
                       'loot_residual': {'credits': residual, 'per_bot_hour': rate(residual, window_hours), 'bot_hours': round(window_hours, 4)},
                       'by_role': by_role,
                       'method': 'Missions/junk: event totals divided by summed time from each spawn to cutoff. Loot: first-to-last cash+bank snapshot change + charged training - mission income - junk within those same snapshot windows; excludes creation purse; residual may include other unlogged flows, and negative values indicate unreconciled flows.',
                       'mission_inferred_count': sum(o['inferred'] for o in outcomes),
                       'mission_inferred_credits': sum(o['income'] for o in outcomes if o['inferred']),
                       'inference': 'mission_done uses logged paid (from run 7 it already adds back training paid from the bank). For an older done/gone row with a masked delta, infer reward only when logged paid + bank-funded training since its matched mission_take equals reward exactly. Trainers use snapshot cash first, then bank; unknown cash prevents inference. Unmatched/ambiguous gone rows remain unresolved, never assumed paid.'},
            'training': {'spent': sum(t['charged'] for t in training), 'nominal_cost': sum(t.get('cost', 0) for t in training),
                         'spent_per_bot_hour': rate(sum(t['charged'] for t in training)),
                         'spent_running_total': sum({t['bot']: t['spent'] for t in training if 'spent' in t}.values()),
                         'charged_boxes': sum('spent' in t for t in training), 'legacy_free_boxes': sum('spent' not in t for t in training),
                         'cost_median': med([t['cost'] for t in training if 'cost' in t]),
                         'credits_before_median': med([t['credits'] for t in training if 'credits' in t]),
                         'refused_skills': {k: len(v) for k, v in sorted(refused_bots.items(), key=lambda kv: (-len(kv[1]), str(kv[0])))},
                         'refusal_shortfall': stats(shortfall),
                         'refusal_rows': len(by['broke']), 'refused_bot_boxes': len(refused), 'bots_refused': len({b for b, s in refused})},
            'missions_total': mission_row(takes, matched),
            'missions_by_level': cells, 'missions_by_bot_level': by_bot_level, 'missions_by_mission_level': by_mission_level,
            'missions_by_level_gap': by_gap, 'missions_by_role': by_mission_role,
            'mission_outcomes': dict(collections.Counter('inferred_paid' if o['inferred'] else o['e'] for o in outcomes)),
            'mission_outcomes_unmatched': len(outcomes)-len(matched),
            'lair_from_spot_m': stats([r['from_spot'] for r in by['lair'] if 'from_spot' in r]),
            'lair_find_secs': stats([r['secs'] for r in by['lair'] if 'secs' in r]),
            'lairs_by_name': dict(collections.Counter(r.get('lair', '?') for r in by['lair'])),
            'deaths_by_levels': [{'bot_level': b, 'killer_level': k, 'deaths': n} for (b, k), n in sorted(level_pairs.items(), key=lambda kv: ksort(kv[0]))],
            'deaths_by_gap': {str(g): n for g, n in sorted(gaps.items())}, 'deaths_by_gap_bucket': gap_buckets,
            'death_gap': {'known': len(known), 'unknown_killer': len(deaths)-len(known),
                          'median': med([d['klvl']-d['lvl'] for d in known]),
                          'mean': round(sum(g*n for g, n in gaps.items())/len(known), 2) if known else None},
            'gate_leaks': [{'killer': k, 'killer_level': lv, 'planet': p, 'deaths': n} for (k, lv, p), n in leaks.most_common(10)],
            'deaths': len(deaths), 'deaths_per_bot_hour': rate(len(deaths)),
            'killer_at_least_8_above': sum(n for g, n in gaps.items() if g >= 8),
            'kills': len(by['kill']), 'incaps': len(by['incap']),
            'census': [{'planet': p, 'kind': k, 'name': n, 'observations': count} for (p, k, n), count in sorted(seen.items(), key=lambda kv: str(kv[0]))],
            'terminals': [{'city': r.get('city'), 'found': r.get('found')} for r in by['terminal']],
            'mission_none_offered': stats([r['offered'] for r in by['mission_none'] if 'offered' in r]),
            'explorers_requested': sum(r.get('n', 0) for r in by['explore'])}


def run(name, path, until_ms=None, host_samples=()):
    raw = load(path)
    host_end = host_cutoff(raw, host_samples)
    until_ms = min(x for x in (until_ms,host_end) if x is not None) if until_ms is not None or host_end is not None else None
    summary = summarize(raw, until_ms)
    rows, _ = gameplay_rows(raw, until_ms)
    if not any(r.get("e") == "spawn" for r in rows):
        return dict(run=name, path=str(path), **summary)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get('e')].append(r)
    t0 = min(r['t'] for r in by['spawn'])
    role = {r['bot']: r['role'] for r in by['spawn']}
    out = {'run': name, 'path': str(path), 'minutes': round((max(r['t'] for r in rows) - t0) / 60000)}

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
        tiers[s[-2:] if len(s) >= 3 and s[-3] == '_' and s[-2:].isdigit() else ('novice' if s.endswith('novice') else 'other')] += 1
    out['boxes_by_tier'] = dict(tiers)
    out['xp_cost_median_by_tier'] = {k: med([t['xp_cost'] for t in by['train'] if t['skill'].endswith('_' + k)]) for k in ('01', '02', '03', '04')}

    # income: cash per bot over time (snapshots), credits per kill
    last = {}
    for s in by['snap']:
        last[s['bot']] = s
    cash = sum(s.get('cash', 0) + s.get('bank', 0) for s in last.values())
    out['credits_total'] = cash
    out['credits_per_kill'] = round(cash / max(len(by['kill']), 1), 2)
    out['held_credits_per_bot_hour_not_income'] = round(cash / max(len(last), 1) / (max(out['minutes'] / 60, 1e-9)), 1)
    costs = [t['cost'] for t in by['train']]
    out['training_cost_median'] = med(costs)
    out['training_nominal_cost_total'] = sum(costs)

    # danger: deaths by bot level; outliers (killer level >= bot level + 8) and where
    out['deaths_per_bot_hour'] = round(len(by['death']) / len(role) / (max(out['minutes'] / 60, 1e-9)), 2)
    out['kills_per_hunter_hour'] = round(len(by['kill']) / max(sum(1 for r in role.values() if r in ('brawler', 'marksman', 'scout')), 1) / (max(out['minutes'] / 60, 1e-9)), 1)
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
    out['heals_per_medic_hour'] = round(sum(heals) / max(len(heals), 1) / (max(out['minutes'] / 60, 1e-9)), 1)
    out['rests'] = len(by['rested'])
    out['rests_watched'] = sum(1 for r in by['rested'] if r.get('watched'))
    out.update(summary)
    return out


def host(paths):
    rows = sorted((r for p in paths for r in load(p)
                   if ((r.get('botpop') or {}).get('online') or 0) > 0 and r.get('rss_mb')), key=lambda r:r['t'])
    segs, cur = [], []
    for r in rows:
        if cur and (r['t'] - cur[-1]['t'] > 300 or r['botpop']['online'] != cur[-1]['botpop']['online']):
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
        out.append({'online': s[0]['botpop']['online'], 'from': s[0]['t'], 'hours': round(hours, 2), 'rss_start': s[0]['rss_mb'], 'rss_end': s[-1]['rss_mb'],
                    'mb_per_hour': round((s[-1]['rss_mb'] - s[0]['rss_mb']) / hours), 'cores_median': med([r['cores'] for r in s if r.get('cores')]),
                    'wsl_free_min_mb': min(r['wsl_avail_mb'] for r in s), 'pass_ms_max': max((r['botpop'].get('pass_ms') or 0) for r in s)})
    return out


def peek(path):
    """(first row time, last row time) in ms of an event log without reading all of it; None if unreadable."""
    try:
        with open(path, 'rb') as f:
            first = json.loads(f.readline())['t']
            f.seek(0, 2)
            f.seek(max(0, f.tell()-65536))
            tail = f.read().splitlines()
    except (OSError, ValueError, KeyError):
        return None
    for line in reversed(tail):
        try:
            return first, json.loads(line)['t']
        except (ValueError, KeyError):
            continue
    return None


def run_name(start_ms):
    for name, t in RUN_STARTS.items():
        if abs(start_ms/1000 - t) <= 300:
            return name
    return time.strftime('r%d-%H%M', time.localtime(start_ms/1000))


def discover_runs(log_dir=LOG_DIR, agent_dir=AGENT_LOGS, min_minutes=5):
    """[(name, path, start_ms, minutes, why_skipped)] oldest first. Runs 1-3 come from agent_dir; a rotated copy of the
    same start is skipped, as are logs with no spawn time or under min_minutes (a crashed or aborted start)."""
    paths = (sorted(glob.glob(os.path.join(agent_dir, 'botpop-launch-run*.jsonl')))
             + sorted(glob.glob(os.path.join(log_dir, 'botpop-launch.jsonl.*.old')))
             + [os.path.join(log_dir, 'botpop-launch.jsonl')])
    found, starts = [], []
    for p in paths:
        if not os.path.exists(p):
            continue
        span = peek(p)
        if span is None:
            found.append((None, p, 0, 0, 'empty or unreadable'))
            continue
        minutes = round((span[1]-span[0])/60000, 1)
        why = None
        if any(abs(span[0]-s) <= 300000 for s in starts):
            why = 'same run as an earlier file'
        elif minutes < min_minutes:
            why = f'under {min_minutes:g} minutes'
        else:
            starts.append(span[0])
        found.append((run_name(span[0]), p, span[0], minutes, why))
    return sorted(found, key=lambda f: f[2])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('out', nargs='?', default=str(SIM/'analysis.json'), help='analysis.json path')
    parser.add_argument('--run', action='append', metavar='NAME=PATH', help='Repeat to replace the logs found automatically')
    parser.add_argument('--current', help='Run the Markdown report is about (default: the newest)')
    parser.add_argument('--until-ms', type=int, help='Known final despawn time of the current run, epoch milliseconds')
    parser.add_argument('--host', action='append', help='Host sample file (repeatable; default Bot-reports/launch-sim/host-*.jsonl)')
    parser.add_argument('--numbers-out', help='Markdown report path (default Bot-reports/launch-sim/numbers-<current>.md)')
    parser.add_argument('--no-numbers', action='store_true', help='Write analysis.json only')
    parser.add_argument('--list', action='store_true', help='List the logs found and their run names, then stop')
    parser.add_argument('--log-dir', default=LOG_DIR)
    parser.add_argument('--agent-dir', default=AGENT_LOGS)
    parser.add_argument('--min-minutes', type=float, default=5, help='Skip automatically found logs shorter than this')
    args = parser.parse_args(argv)
    if args.run:
        found = [(n, p, 0, 0, None) for n, p in (x.split('=', 1) for x in args.run)]
    else:
        found = discover_runs(args.log_dir, args.agent_dir, args.min_minutes)
    if args.list:
        for name, path, start, minutes, why in found:
            when = time.strftime('%d %b %H:%M', time.localtime(start/1000)) if start else '-'
            print(f"{name or '-':8} {when:13} {minutes:7} min  {path}" + (f"  (skipped: {why})" if why else ''))
        return
    paths = [(n, p) for n, p, s, m, why in found if why is None]
    if not paths:
        sys.exit('no event logs found; give --run NAME=PATH')
    current = args.current or paths[-1][0]
    if current not in [n for n, p in paths]:
        sys.exit(f'--current {current}: not one of {", ".join(n for n, p in paths)}')
    host_paths = args.host or sorted(glob.glob(str(SIM/'host-*.jsonl')))
    host_samples = [r for p in host_paths for r in load(p)]
    result = {'runs': [run(n, p, args.until_ms if n == current else None, host_samples) for n, p in paths], 'host': host(host_paths)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1)+'\n', encoding='utf-8')
    print(f'wrote {args.out}: {len(result["runs"])} runs ({", ".join(n for n, p in paths)})')
    if not args.no_numbers:
        if str(HERE) not in sys.path:
            sys.path.insert(0, str(HERE))
        from botpop_report import report
        target = args.numbers_out or str(SIM/f'numbers-{current}.md')
        comparisons = [(r['run'], r) for r in result['runs'] if r['run'] != current]
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'w', encoding='utf-8', newline='\n') as f:
            f.write(report(load(dict(paths)[current]), host_samples, args.until_ms, comparisons, name=current))
        print(f'wrote {target}')


if __name__ == '__main__':
    main()
