"""Findings list for a big BotPop run: PASS / FAIL / WATCH lines with the numbers behind each.

Reads the server's event log (botpop-launch.jsonl, or a finished run's .jsonl.<HHMM>.old) and, when given, the test
galaxy's core3.log, and writes Bot-reports/launch-sim/findings-<name>.md plus findings-<name>.json (the numbers, so the
next run can compare). Read-only on the server; stdlib only. Automates the checks in Bot-reports/FINDINGS-2026-10-16.md.

    python3 botpop_findings.py RUN.jsonl --name run13 [--core3-log core3.log] [--previous findings-run12.json] [--out-dir DIR]

Without --previous it compares with the newest findings-*.json in the output folder from an earlier run, if any.
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from botpop_analysis import gameplay_rows, summarize, GAP_BUCKETS

OUTPUTS = os.path.dirname(os.path.dirname(HERE))
SIM = os.path.join(OUTPUTS, 'Bot-reports', 'launch-sim')
NONCOMBAT = {'medic', 'entertainer', 'explorer', 'artisan', 'crafter', 'musician', 'dancer'}
MIN_TAKEN = 20           # fewer missions than this for a role: WATCH, not a verdict
COMBAT_SUCCESS_MIN = .10  # a combat role under this mission success rate is a FAIL
STATS_RE = re.compile(r'failed \d+, no path (\d+)(?:, routes (\d+) \((\d+) deferred(?:, (\d+) none)?\))?'
                      r'(?:, legs stopped: no start (\d+), no end (\d+), no path (\d+), partial (\d+), unloaded mesh (\d+), snapped (\d+))?')
LEG_KEYS = ('no start', 'no end', 'no path', 'partial', 'unloaded mesh')  # "snapped" is a repaired end, not a failed leg
STEPS_RE = re.compile(r'steps ([\d.]+) ms per second')
MSEC_RE = re.compile(r'\[(\d{12,}) msec\]')


def load(path):
    rows = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def pct(part, whole):
    return f'{100 * part / whole:.0f}%' if whole else '-'


def med(v):
    return round(statistics.median(v), 1) if v else None


def clock(ms):
    """12-hour local time, '4:02 PM'."""
    return time.strftime('%I:%M %p', time.localtime(ms / 1000)).lstrip('0') if ms else '?'


def n(v):
    return f'{v:,}' if isinstance(v, int) else str(v)


# ---- the numbers -------------------------------------------------------------------------------------------------

def lair_checks(rows):
    """Group lair_check rows into attempts (one bot at one mission's lair) and summarise by ranged and melee."""
    attempt_of, attempts = {}, collections.defaultdict(list)
    for r in rows:
        b = r.get('bot')
        if r.get('e') == 'mission_take':
            attempt_of[b] = (b, r['t'])
        elif r.get('e') == 'lair_check':
            attempts[attempt_of.get(b, (b, r.get('lair')))].append(r)
    out = {}
    for kind in ('ranged', 'melee'):
        groups = [g for g in attempts.values() if any(x.get('ranged') for x in g) == (kind == 'ranged')]
        checks = [x for g in groups for x in g]
        judged = [g for g in groups if len(g) >= 2]
        flat = [g for g in judged if max(x.get('damage', 0) for x in g) <= g[0].get('damage', 0)]
        out[kind] = {'attempts': len(groups), 'checks': len(checks),
                     'los_false': sum(x.get('los') is False for x in checks),
                     'attackable_false': sum(x.get('attackable') is False for x in checks),
                     'out_of_range': sum(x.get('dist', 0) > x.get('max_range', 0) > 0 for x in checks),
                     'judged_attempts': len(judged), 'damage_never_rose': len(flat),
                     'dist_median': med([x['dist'] for x in checks if 'dist' in x]),
                     'weapons': dict(collections.Counter(x.get('weapon', '?') for x in checks).most_common(5)),
                     'postures': dict(collections.Counter(str(x.get('posture')) for x in checks).most_common(4))}
    return out


def core3_numbers(path, start_ms, end_ms):
    """ERROR lines and BotPop stats lines in core3.log between the run's first and last rows."""
    before, during, stats = set(), collections.Counter(), collections.Counter()
    stats_lines = with_legs = with_routes = 0
    steps = []
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = MSEC_RE.search(line)
            if not m:
                continue
            t = int(m.group(1))
            if t > end_ms:
                continue
            if 'ERROR' in line:
                sig = signature(line)
                if t < start_ms:
                    before.add(sig)
                else:
                    during[sig] += 1
            if t >= start_ms and '[BotPop]' in line:
                s = STATS_RE.search(line)
                if s:
                    stats_lines += 1
                    g = [int(x) if x is not None else None for x in s.groups()]
                    stats['no path (route lookup)'] += g[0]
                    stats['routes'] += g[1] or 0
                    stats['deferred'] += g[2] or 0
                    stats['none'] += g[3] or 0
                    if g[1] is not None:
                        with_routes += 1
                    st = STEPS_RE.search(line)
                    if st:
                        steps.append(float(st.group(1)))
                    if g[4] is not None:
                        with_legs += 1
                        for k, v in zip(LEG_KEYS + ('snapped',), g[4:]):
                            stats[k] += v
    new = {s: c for s, c in during.items() if s not in before}
    return {'error_lines': sum(during.values()), 'signatures': len(during), 'new_signatures': len(new),
            'new_lines': sum(new.values()), 'top_new': sorted(new.items(), key=lambda kv: -kv[1])[:8],
            'top': during.most_common(5), 'stats_lines': stats_lines, 'stats_lines_with_legs': with_legs, 'stats_lines_with_routes': with_routes,
            'steps_ms_per_s_median': med(steps), 'steps_ms_per_s_max': max(steps) if steps else None, 'stats': dict(stats)}


def signature(line):
    """An ERROR line without its timestamp, thread, addresses and numbers, so repeats group together."""
    text = line.split(' - ', 1)[1] if ' - ' in line else line
    text = re.sub(r'\d+\.\d+\.\d+\.\d+(:\d+)?', '<ip>', text)
    text = re.sub(r'0x[0-9a-fA-F]+', '<hex>', text)
    text = re.sub(r'\d+', '#', text)
    return text.strip()[:160]


def metrics(raw, core3_log=None):
    rows, exclusion = gameplay_rows(raw)
    s = summarize(raw)
    by = collections.defaultdict(list)
    for r in rows:
        by[r.get('e')].append(r)
    start = min((r['t'] for r in by['spawn']), default=rows[0]['t'] if rows else 0)
    end = max((r['t'] for r in rows), default=0)
    role_of = {}
    for r in rows:
        if r.get('bot') is not None and r.get('role'):
            role_of.setdefault(r['bot'], r['role'])

    roles = {}
    for r in s['missions_by_role']:
        roles[r['role'] or '?'] = {'taken': r['taken'], 'success': r['success'], 'resolved': r['resolved'], 'aborted': r['aborted']}
    for a in by['mission_abort']:
        role = roles.setdefault(role_of.get(a.get('bot'), '?'), {'taken': 0, 'success': 0, 'resolved': 0, 'aborted': 0})
        role['aborted_lair_seen'] = role.get('aborted_lair_seen', 0) + bool(a.get('lair_seen'))

    last_snap = {}
    for r in by['snap']:
        last_snap[r['bot']] = r
    server = by['server']
    peak = max((r.get('online', 0) for r in server), default=0)
    full = [r for r in server if r.get('online', 0) == peak]
    steady = full[1:] or full

    tr = s['training']
    return {
        'start_ms': start, 'end_ms': end, 'minutes': round((end - start) / 60000, 1), 'bots': len({r['bot'] for r in by['spawn']}),
        'role_counts': dict(collections.Counter(role_of.get(r['bot']) for r in by['spawn'])),
        'exclusion': {'cutoff_ms': exclusion['cutoff_ms'], 'reason': exclusion['reason'], 'excluded_rows': exclusion['excluded_rows']},
        'missions_by_role': roles,
        'lair_check': lair_checks(rows),
        'deaths': {'total': s['deaths'], 'known': s['death_gap']['known'], 'median_gap': s['death_gap']['median'],
                   'by_gap': s['deaths_by_gap_bucket'], 'killer_8_above': s['killer_at_least_8_above'],
                   'leaks': s['gate_leaks'][:8], 'bot_hours': s['bot_hours'], 'per_bot_hour': s['deaths_per_bot_hour']},
        'travel': {'attempted': len(by['travel']), 'done': sum(r.get('travels', 0) for r in last_snap.values()),
                   'server_counter': max((r.get('travels', 0) for r in server), default=0),
                   'flows': collections.Counter(f"{r.get('planet')}>{r.get('to_planet')}" for r in by['travel']).most_common(6)},
        'training': {'bots': len(role_of), 'bots_refused': tr['bots_refused'], 'pairs': tr['refused_bot_boxes'], 'rows': tr['refusal_rows'],
                     'shortfall_median': tr['refusal_shortfall']['median'], 'skills': list(tr['refused_skills'].items())[:5],
                     'by_role': {k: v['refused_bots'] for k, v in s['income']['by_role'].items()},
                     'role_bots': {k: v['bots'] for k, v in s['income']['by_role'].items()}},
        'fallback_fields': {k: sum(r.get(k, 0) for r in server) for k in sorted({k for r in server for k in r if 'fallback' in k or k.startswith('leg_')})},
        'ticks': {'rows': len(server), 'peak_online': peak, 'full_rows': len(full),
                  'tick_avg_median': med([r.get('tick_ms_avg', 0) for r in steady]),
                  'tick_max': max((r.get('tick_ms_max', 0) for r in steady), default=None),
                  'skipped': sum(r.get('skipped', 0) for r in steady),
                  'ramp_tick_avg_max': max((r.get('tick_ms_avg', 0) for r in server), default=None),
                  'rss_mb': [steady[0].get('rss_mb'), steady[-1].get('rss_mb')] if steady else None},
        'core3': core3_numbers(core3_log, start, end) if core3_log else None,
    }


# ---- the verdicts ------------------------------------------------------------------------------------------------

def was(prev, *keys, fmt=str):
    """' (run12: X)' for the same number in the previous run, or ''."""
    if not prev:
        return ''
    v = prev['m']
    for k in keys:
        if not isinstance(v, dict) or k not in v:
            return ''
        v = v[k]
    return f" ({prev['name']}: {fmt(v)})"


def findings(m, prev=None):
    """[(section, status, text)] in report order."""
    out = []
    add = lambda sec, st, text: out.append((sec, st, text))

    # Missions by role
    sec = 'Missions by role'
    for role, r in sorted(m['missions_by_role'].items(), key=lambda kv: -kv[1]['taken']):
        if not r['taken']:
            continue
        rate = r['success'] / r['taken']
        prev_rate = was(prev, 'missions_by_role', role, fmt=lambda v: pct(v['success'], v['taken']))
        lair = f"; {n(r.get('aborted_lair_seen', 0))} aborted after finding the lair" if r.get('aborted_lair_seen') else ''
        text = f"{role}: {n(r['success'])} of {n(r['taken'])} missions succeeded ({pct(r['success'], r['taken'])}){lair}{prev_rate}."
        if r['taken'] < MIN_TAKEN:
            add(sec, 'WATCH', text + f' Too few missions to judge (under {MIN_TAKEN}).')
        elif role in NONCOMBAT:
            add(sec, 'WATCH', text + ' Not a combat role.')
        else:
            add(sec, 'FAIL' if rate < COMBAT_SUCCESS_MIN else 'PASS', text + ('' if rate >= COMBAT_SUCCESS_MIN else f' Under {COMBAT_SUCCESS_MIN:.0%}.'))
    if not any(r['taken'] for r in m['missions_by_role'].values()):
        add(sec, 'WATCH', 'No missions taken.')

    # Lair checks
    sec = 'Mission lairs (lair_check rows)'
    lc = m['lair_check']
    if not lc['ranged']['checks'] and not lc['melee']['checks']:
        add(sec, 'WATCH', 'No lair_check rows: this run predates dev 665bea04, or no bot fought a mission lair.')
    for kind in ('ranged', 'melee'):
        x = lc[kind]
        if not x['checks']:
            continue
        flat = x['damage_never_rose']
        text = (f"{kind}: {n(x['attempts'])} lair attempts, {n(x['checks'])} checks; line of sight false {pct(x['los_false'], x['checks'])}, "
                f"not attackable {pct(x['attackable_false'], x['checks'])}, beyond weapon range {pct(x['out_of_range'], x['checks'])}; "
                f"damage never rose in {n(flat)} of {n(x['judged_attempts'])} attempts with two or more checks ({pct(flat, x['judged_attempts'])}); "
                f"median distance {x['dist_median']} m; weapons {', '.join(f'{k} {v}' for k, v in x['weapons'].items())}"
                f"{was(prev, 'lair_check', kind, fmt=lambda v: pct(v['damage_never_rose'], v['judged_attempts']) + ' never rose')}.")
        status = 'PASS'
        if x['judged_attempts'] and flat / x['judged_attempts'] > .5:
            status = 'FAIL'
            causes = [c for c, k in (('line of sight', 'los_false'), ('attackable', 'attackable_false'), ('range', 'out_of_range'))
                      if x[k] / x['checks'] > .5]
            text += (' Most failing check: ' + ', '.join(causes) + '.') if causes else ' Every check passes, so shots fire and do no damage.'
        elif not x['judged_attempts']:
            status = 'WATCH'
        add(sec, status, text)

    # Deaths
    sec = 'Deaths by level gap'
    d = m['deaths']
    if d['total']:
        bands = ', '.join(f"{label} {pct(d['by_gap'].get(label, 0), d['known'])}" for label, lo, hi in GAP_BUCKETS)
        add(sec, 'PASS' if d['median_gap'] is None or d['median_gap'] <= 5 else 'WATCH',
            f"{n(d['total'])} deaths ({d['per_bot_hour']} per bot-hour{was(prev, 'deaths', 'per_bot_hour')}), killer level known for {n(d['known'])}; "
            f"median gap (killer minus bot) {d['median_gap']}{was(prev, 'deaths', 'median_gap')}. Share by gap: {bands}.")
        share = d['killer_8_above'] / d['known'] if d['known'] else 0
        leaks = '; '.join(f"{g['killer']} (level {g['killer_level']}, {g['planet']}) {g['deaths']}" for g in d['leaks'][:5])
        add(sec, 'PASS' if not d['killer_8_above'] else ('FAIL' if share >= .05 else 'WATCH'),
            f"Killers 8 or more levels above the bot: {n(d['killer_8_above'])} deaths ({100 * share:.1f}% of known)"
            f"{was(prev, 'deaths', 'killer_8_above')}" + (f". Worst: {leaks}." if leaks else '.')
            + (' The spawn level gate should stop these.' if share >= .05 else ''))
    else:
        add(sec, 'WATCH', 'No deaths logged.')

    # Travel
    sec = 'Travel'
    t = m['travel']
    flows = ', '.join(f'{k} {v}' for k, v in t['flows'])
    if not t['attempted'] and not t['done']:
        add(sec, 'WATCH', 'No travel attempted. BotPop travel also teleports (switchZone), so shuttles and tickets stay untested either way.')
    else:
        ok = t['done'] >= .9 * t['attempted']
        add(sec, 'PASS' if ok else 'FAIL', f"{n(t['attempted'])} trips attempted, {n(t['done'])} done (bots' own counters; server counter {n(t['server_counter'])})"
            f"{was(prev, 'travel', 'done')}. Routes: {flows or 'none'}. Teleport only: shuttles and tickets untested.")

    # Training
    sec = 'Training'
    tr = m['training']
    share = tr['bots_refused'] / tr['bots'] if tr['bots'] else 0
    worst = sorted(((r, tr['by_role'][r] / tr['role_bots'][r]) for r in tr['by_role'] if tr['role_bots'].get(r)), key=lambda kv: -kv[1])[:3]
    add(sec, 'PASS' if not tr['bots_refused'] else ('WATCH' if share < .5 else 'FAIL'),
        f"{n(tr['bots_refused'])} of {n(tr['bots'])} bots ({pct(tr['bots_refused'], tr['bots'])}) were refused a box for credits at least once"
        f"{was(prev, 'training', 'bots_refused')}; {n(tr['pairs'])} distinct bot/box pairs; median shortfall {tr['shortfall_median']} credits. "
        f"Most refused: {', '.join(f'{k} {v}' for k, v in tr['skills']) or 'none'}. "
        f"Worst roles: {', '.join(f'{r} {v:.0%}' for r, v in worst) or 'none'}.")

    # Route fallbacks
    sec = 'Routes'
    c3 = m['core3']
    if m['fallback_fields']:
        total = sum(m['fallback_fields'].values())
        add(sec, 'PASS' if not total else 'WATCH', 'Server rows: ' + ', '.join(f'{k} {n(v)}' for k, v in m['fallback_fields'].items()) + '.')
    if c3 and c3['stats_lines']:
        st = c3['stats']
        base = (f"{n(c3['stats_lines'])} BotPop stats lines: {n(st.get('no path (route lookup)', 0))} path lookups failed"
                + (f", {n(st.get('routes', 0))} routes planned, {n(st.get('none', 0))} with no route{was(prev, 'core3', 'stats', 'routes')}"
                   if c3['stats_lines_with_routes'] else ' (this build logs no route counts)'))
        if c3['stats_lines_with_legs']:
            legs = sum(st.get(k, 0) for k in LEG_KEYS)
            add(sec, 'PASS' if not legs else ('FAIL' if st.get('routes') and legs / st['routes'] > .05 else 'WATCH'),
                base + f"; legs stopped instead of a straight-line fallback {n(legs)} ({pct(legs, st.get('routes', 0))} of routes: "
                + ', '.join(f'{k} {n(st.get(k, 0))}' for k in LEG_KEYS) + f"; ends snapped {n(st.get('snapped', 0))}).")
        else:
            add(sec, 'WATCH', base + '. No fallback counters in the stats line (they come with the no-fallback patch), so fallbacks are not counted.')
    elif not m['fallback_fields']:
        add(sec, 'WATCH', ('No BotPop stats lines in core3.log during the run' if c3 else 'core3.log not read (pass --core3-log)')
            + ' and no fallback fields in the server rows.')

    # core3.log errors
    sec = 'Server errors (core3.log)'
    if c3 is None:
        add(sec, 'WATCH', 'core3.log not read (pass --core3-log).')
    else:
        top = '; '.join(f'{c}x {sig[:110]}' for sig, c in c3['top_new'][:4])
        add(sec, 'PASS' if not c3['new_signatures'] else 'WATCH',
            f"{n(c3['error_lines'])} ERROR lines during the run, {c3['signatures']} kinds; {c3['new_signatures']} kinds not seen before the run "
            f"started ({n(c3['new_lines'])} lines){was(prev, 'core3', 'new_signatures')}" + (f". New: {top}." if top else '.'))

    # Ticks
    sec = 'Server ticks'
    k = m['ticks']
    if k['rows']:
        worst, skipped = k['tick_max'] or 0, k['skipped']
        status = 'PASS' if worst <= 250 and not skipped else ('WATCH' if worst <= 1000 and skipped <= 10 else 'FAIL')
        add(sec, status, f"{k['full_rows']} server rows at the full {n(k['peak_online'])} bots: tick median {k['tick_avg_median']} ms"
            f"{was(prev, 'ticks', 'tick_avg_median')}, worst {worst} ms{was(prev, 'ticks', 'tick_max')}, passes skipped {skipped}"
            f"{was(prev, 'ticks', 'skipped')}; RSS {k['rss_mb'][0]} to {k['rss_mb'][1]} MB. Ramp-up tick average peaked at {k['ramp_tick_avg_max']} ms. "
            + (f"Bot steps {c3['steps_ms_per_s_median']} ms of CPU per second (median; worst {c3['steps_ms_per_s_max']}){was(prev, 'core3', 'steps_ms_per_s_median')}. " if c3 and c3.get('steps_ms_per_s_median') else '') +
            "PASS: worst tick 250 ms or less and nothing skipped; FAIL: over 1 s or more than 10 skipped.")
    else:
        add(sec, 'WATCH', 'No server rows.')
    return out


def render(name, m, found, prev=None, source=''):
    counts = collections.Counter(st for _, st, _ in found)
    md = [f'# Findings: {name}\n',
          f"{time.strftime('%d %b', time.localtime(m['start_ms'] / 1000))}, {clock(m['start_ms'])} to {clock(m['end_ms'])} "
          f"({m['minutes']:.0f} min), {n(m['bots'])} bots: " + ', '.join(f'{k} {v}' for k, v in sorted(m['role_counts'].items(), key=lambda kv: -kv[1])) + '.',
          f"Source: `{source}`. Written by `tools/bots/botpop_findings.py`; the numbers are in the .json beside this file.",
          f"Compared with: {prev['name'] if prev else 'nothing (no earlier findings file)'}.",
          f"Final logout left out: {clock(m['exclusion']['cutoff_ms']) if m['exclusion']['cutoff_ms'] else 'no boundary found'}"
          f" ({m['exclusion']['excluded_rows']} rows).\n",
          f"**{counts['FAIL']} FAIL, {counts['WATCH']} WATCH, {counts['PASS']} PASS.**\n"]
    for st in ('FAIL', 'WATCH', 'PASS'):
        lines = [(sec, text) for sec, s, text in found if s == st]
        if lines:
            md.append(f'## {st}\n')
            md += [f'- **{sec}.** {text}' for sec, text in lines]
            md.append('')
    md.append('PASS means the number is inside the line drawn here, not that the feature was tested in game. '
              'Thresholds: combat role mission success under 10% FAIL; lair damage never rising in over half the attempts FAIL; '
              'killers 8+ levels above in 5% of deaths FAIL; travel done under 90% of attempted FAIL; '
              'half the bots refused training FAIL; legs stopped on over 5% of routes FAIL.')
    return '\n'.join(md) + '\n'


def previous_file(out_dir, name, start_ms):
    best = None
    for p in glob.glob(os.path.join(out_dir, 'findings-*.json')):
        try:
            with open(p, encoding='utf-8') as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if d.get('name') != name and d['m'].get('start_ms', 0) < start_ms and (best is None or d['m']['start_ms'] > best['m']['start_ms']):
            best = d
    return best


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('events')
    ap.add_argument('--name', required=True, help='run label, e.g. run13')
    ap.add_argument('--core3-log', help='the test galaxy core3.log covering the run')
    ap.add_argument('--previous', help='findings-<run>.json of the run to compare with')
    ap.add_argument('--out-dir', default=SIM)
    a = ap.parse_args(argv)
    raw = load(a.events)
    if not raw:
        sys.exit(f'no rows in {a.events}')
    m = metrics(raw, a.core3_log)
    if a.previous:
        with open(a.previous, encoding='utf-8') as f:
            prev = json.load(f)
    else:
        prev = previous_file(a.out_dir, a.name, m['start_ms'])
    found = findings(m, prev)
    os.makedirs(a.out_dir, exist_ok=True)
    base = os.path.join(a.out_dir, f'findings-{a.name}')
    with open(base + '.md', 'w', encoding='utf-8', newline='\n') as f:
        f.write(render(a.name, m, found, prev, os.path.basename(a.events)))
    with open(base + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'name': a.name, 'm': m, 'findings': found}, f, indent=1, default=str)
    c = collections.Counter(st for _, st, _ in found)
    print(f"{base}.md: {c['FAIL']} FAIL, {c['WATCH']} WATCH, {c['PASS']} PASS")


if __name__ == '__main__':
    main()
