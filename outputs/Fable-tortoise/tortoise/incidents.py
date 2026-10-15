"""Offline incident layer for squad reports: bounded, evidence-linked episodes from Bot-reports/<Group>/<stamp>-<scenario>.json.

Our own work (Fable, 14 October 2026, AGPL-3.0), informed by the issue-episode rules in TortoiseBots'
tools/observability/README.md (TortoiseBots by Sagiroth, https://github.com/Sagiroth/TortoiseBots, AGPL-3.0 with
the attribution term): episodes open and close per bot/problem, a minimum age before one is shown, a post-restart
blackout, severity escalating watch -> persistent, resolved history kept, every table bounded. No TortoiseBots
code is used in this file; the rules are restated for our report shape.

What it does, in one pass over the reports of each group in time order:
- a run in state `stopped` (halt or time budget) is never evidence: it neither opens nor closes anything;
- every failed check, BLOCKED note, ERROR note and run error becomes an issue with a kind, a normalised key and
  a class: `blocked` (a prerequisite or capability the scenario said was missing: not a server defect),
  `defect-candidate` (a recorded check failed while the body was connected and the run ended: evidence for a
  server, content or scenario defect; a person decides which), `bot-down` (body not logged in, stale after a
  restart, disconnected), `harness` (a Python exception in scenario or squad code), `unclassified` (anything else);
- an episode opens the first time a key is seen for a scenario and is refreshed by every later run that shows
  it; it closes when a run of the same scenario vouches against it (the check passed; or the note/error is gone
  and the run did not end in an error); other scenarios' runs say nothing about it;
- a server restart (an epoch boundary, given with --epoch or an epochs file) closes every open episode with the
  resolution `server restart`; if the key is seen again afterwards the new episode links back (`continues`);
  bot-down issues inside the post-restart blackout are recorded as suppressed, not opened;
- only episodes seen in >= MIN_RUNS runs are surfaced (TortoiseBots gates by age; with one report per run the run
  count is the honest measure here); the rest are listed by key under `seen_once`, so nothing is silently dropped;
  severity is `watch`, then `persistent` from PERSISTENT_RUNS;
- evidence per episode is the newest EVIDENCE entries of (report file, check time, detail).

Baselines: `baseline` freezes per-(group, scenario) rates over a named window; `compare` sets a later window
against it with fixed thresholds. Pooling is explicit (window and label are in the file), never implied.

Reads reports only. Writes only under --out. Never talks to bots or the server.

    python incidents.py [--reports DIR] [--out DIR] [--epoch "YYYY-MM-DD HH:MM:SS"]... [--epochs FILE]
                        [--since "YYYY-MM-DD HH:MM"] [--min-runs 2] [--persistent-runs 3] [--blackout 300] [--evidence 5]
    python incidents.py baseline --save FILE --label TEXT [--reports DIR] [--since ...] [--until ...]
    python incidents.py compare --baseline FILE [--reports DIR] [--since ...] [--until ...] [--label TEXT]
"""
import argparse
import bisect
import hashlib
import json
import re
import statistics
import sys
from collections import deque
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REPORTS = HERE.parents[1] / 'Bot-reports'   # outputs/Bot-reports (HERE = outputs/Fable-tortoise/tortoise)
DEFAULT_OUT = HERE.parent / 'out'
GROUPS = ('Aurek', 'Besh', 'Cresh', 'Dorn', 'Esk')
MIN_RUNS, PERSISTENT_RUNS, BLACKOUT_S, EVIDENCE = 2, 3, 300, 5
SEEN_ONCE_LIMIT, RESOLVED_LIMIT = 50, 40
STAMP = '%Y-%m-%d %H:%M:%S'

BOT_DOWN = re.compile(r'not logged in|BotDown|"connected": false|\bstale\b|logged out|no such character|disconnected|'
                      r'body (?:is )?(?:down|gone|missing)', re.I)
HARNESS = re.compile(r'^(?:TypeError|KeyError|AttributeError|NameError|IndexError|ValueError|AssertionError|'
                     r'ZeroDivisionError|FileNotFoundError|JSONDecodeError|UnicodeDecodeError|RecursionError|'
                     r'ImportError|ModuleNotFoundError|SyntaxError|UnboundLocalError)\b')


# ---- reports ------------------------------------------------------------------------------------------------------

class Run:
    __slots__ = ('group', 'scenario', 'started', 'seconds', 'state', 'name', 'checks', 'notes', 'error', 'passed', 'total')

    def __init__(self, data, name):
        self.group, self.name = str(data.get('group', 'unknown')), name
        self.scenario = str(data.get('scenario', 'unknown'))
        self.started = parse_time(data.get('started')) or stamp_from_name(name)
        self.seconds = data.get('seconds')
        self.state = str(data.get('state', 'unknown'))
        checks = data.get('checks', [])
        if not isinstance(checks, list) or any(not isinstance(c, dict) or type(c.get('ok')) is not bool for c in checks):
            raise ValueError('checks must be a list of labelled boolean results')
        notes = data.get('notes', [])
        if not isinstance(notes, list) or any(not isinstance(n, str) for n in notes):
            raise ValueError('notes must be strings')
        self.checks, self.notes = checks, notes
        self.error = str(data['error']) if data.get('error') else ''
        self.passed, self.total = sum(c['ok'] for c in checks), len(checks)


def parse_time(text):
    if not text:
        return None
    for fmt in (STAMP, '%Y-%m-%d %H:%M', '%Y%m%d-%H%M%S'):
        try:
            return datetime.strptime(str(text).strip(), fmt)
        except ValueError:
            pass
    return None


def stamp_from_name(name):
    return parse_time(name[:15])


def load_runs(root, groups=GROUPS, since=None, until=None):
    """Timestamp-prefixed JSON reports per group, oldest first. Returns (runs, unreadable)."""
    root, runs, unreadable = Path(root), [], []
    for group in groups:
        for path in sorted((root / group).glob('[0-9]*-*.json')):
            try:
                run = Run(json.loads(path.read_text(encoding='utf-8')), path.name)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                unreadable.append({'report': f'{group}/{path.name}', 'error': f'{type(exc).__name__}: {exc}'[:160]})
                continue
            if run.started is None:
                unreadable.append({'report': f'{group}/{path.name}', 'error': 'no start time'})
                continue
            if (since and run.started < since) or (until and run.started > until):
                continue
            runs.append(run)
    runs.sort(key=lambda r: (r.started, r.name))
    return runs, unreadable


# ---- issues -------------------------------------------------------------------------------------------------------

def normalise(text, limit=120):
    text = re.sub(r'^\s*(BLOCKED|ERROR|FAIL)\s*:\s*', '', str(text), flags=re.I)
    text = re.sub(r'0x[0-9a-f]+|\b\d+(?:\.\d+)?\b', '#', text)
    return re.sub(r'\s+', ' ', text).strip()[:limit]


def short(text, limit=200):
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text if len(text) <= limit else text[:limit - 1] + '…'


def classify_error(text):
    if BOT_DOWN.search(text):
        return 'bot-down'
    if HARNESS.match(text) or 'Traceback' in text:
        return 'harness'
    return 'unclassified'


def issues(run):
    """[(kind, key, class, detail, t)] for one run; empty for stopped runs (a halt is not evidence)."""
    if run.state == 'stopped':
        return []
    found, seen = [], set()

    def add(kind, key, klass, detail, t):
        if (kind, key) not in seen:  # a note or label repeated inside one run counts once
            seen.add((kind, key))
            found.append((kind, key, klass, detail, t))

    for check in run.checks:
        if not check['ok']:
            detail = '' if check.get('detail') is None else check['detail']
            klass = 'bot-down' if BOT_DOWN.search(str(detail)) else 'defect-candidate'
            add('FAIL', normalise(check.get('label', 'unlabelled')), klass, short(detail), check.get('t'))
    for note in run.notes:
        upper = note.upper()
        if upper.startswith('BLOCKED'):
            add('BLOCKED', normalise(note), 'bot-down' if BOT_DOWN.search(note) else 'blocked', short(note), None)
        elif upper.startswith('ERROR'):
            add('ERROR', normalise(note), classify_error(note), short(note), None)
    if run.error:
        add('ERROR', normalise(run.error), classify_error(run.error), short(run.error), None)
    return found


# ---- episodes -----------------------------------------------------------------------------------------------------

class Episode:
    def __init__(self, ident, run, kind, key, klass, epoch, continues, evidence_limit):
        self.id, self.group, self.scenario = ident, run.group, run.scenario
        self.kind, self.key, self.klass, self.epoch, self.continues = kind, key, klass, epoch, continues
        self.first_seen = self.last_seen = run.started
        self.runs_seen, self.runs_between = 0, 0
        self.evidence = deque(maxlen=evidence_limit)
        self.resolved_at = self.resolved_by = None

    def refresh(self, run, detail, t):
        self.last_seen = run.started
        self.runs_seen += 1
        self.evidence.append({'report': f'{run.group}/{run.name}', 't': t, 'detail': detail})

    def close(self, when, by):
        self.resolved_at, self.resolved_by = when, by

    @property
    def age_s(self):
        return int((self.last_seen - self.first_seen).total_seconds())

    def severity(self, persistent_runs):
        return 'persistent' if self.runs_seen >= persistent_runs else 'watch'

    def row(self, persistent_runs):
        return {
            'id': self.id, 'group': self.group, 'scenario': self.scenario, 'kind': self.kind, 'class': self.klass,
            'key': self.key, 'state': 'resolved' if self.resolved_at else 'open',
            'severity': self.severity(persistent_runs), 'runs_seen': self.runs_seen, 'runs_between': self.runs_between,
            'first_seen': self.first_seen.strftime(STAMP), 'last_seen': self.last_seen.strftime(STAMP),
            'age_s': self.age_s, 'epoch': self.epoch, 'continues': self.continues,
            'resolved_at': self.resolved_at.strftime(STAMP) if self.resolved_at else None, 'resolved_by': self.resolved_by,
            'evidence': list(self.evidence),
        }


def episode_id(group, scenario, kind, key, n):
    digest = hashlib.sha1(f'{scenario}|{kind}|{key}'.encode('utf-8')).hexdigest()[:6]
    return f'{group[:2]}-{kind[0]}{digest}-{n}'


class Stand:
    """The (kind, key) of an episode that is not open any more, for vouches()."""
    def __init__(self, kind, key):
        self.kind, self.key = kind, key


def vouches(run, episode):
    """Does this run (same scenario) speak against the episode?"""
    if episode.kind == 'FAIL':
        return any(c['ok'] and normalise(c.get('label', 'unlabelled')) == episode.key for c in run.checks)
    if run.state == 'error':
        return False  # a run that died cannot vouch that a note or error is gone
    return all(not (kind == episode.kind and key == episode.key) for kind, key, *_ in issues(run))


def build(runs, epochs=(), min_runs=MIN_RUNS, persistent_runs=PERSISTENT_RUNS, blackout_s=BLACKOUT_S, evidence=EVIDENCE):
    epochs = sorted(epochs)
    done, open_by_group, counters, suppressed, ignored, last_restart_close = [], {}, {}, [], [], {}
    for run in runs:
        epoch = bisect.bisect_right(epochs, run.started)
        open_ = open_by_group.setdefault(run.group, {})
        for k, ep in list(open_.items()):  # a restart closes every open episode of this group
            if ep.epoch != epoch:
                ep.close(epochs[epoch - 1], f'server restart (epoch {epoch})')
                last_restart_close[(run.group,) + k] = ep.id
                done.append(ep)
                del open_[k]
        if run.state == 'stopped':
            ignored.append(f'{run.group}/{run.name}')
            continue
        in_blackout = epoch > 0 and (run.started - epochs[epoch - 1]).total_seconds() < blackout_s
        found = issues(run)
        seen = set()
        for kind, key, klass, detail, t in found:
            if in_blackout and klass == 'bot-down':
                suppressed.append({'report': f'{run.group}/{run.name}', 'kind': kind, 'key': key,
                                   'reason': f'post-restart blackout ({blackout_s} s)'})
                continue
            k = (run.scenario, kind, key)
            seen.add(k)
            ep = open_.get(k)
            if ep is None:
                n = counters[(run.group,) + k] = counters.get((run.group,) + k, 0) + 1
                ep = open_[k] = Episode(episode_id(run.group, run.scenario, kind, key, n), run, kind, key, klass,
                                        epoch, last_restart_close.pop((run.group,) + k, None), evidence)
            ep.refresh(run, detail, t)
        for k, ep in list(open_.items()):
            if k in seen or ep.scenario != run.scenario:
                continue
            if vouches(run, ep):
                ep.close(run.started, f'{run.group}/{run.name}')
                done.append(ep)
                del open_[k]
            else:
                ep.runs_between += 1
        for gk in [gk for gk in last_restart_close if gk[0] == run.group and gk[1] == run.scenario and gk[1:] not in seen]:
            if vouches(run, Stand(gk[2], gk[3])):  # seen gone after the restart: a later recurrence is a new episode
                del last_restart_close[gk]
    episodes = done + [ep for open_ in open_by_group.values() for ep in open_.values()]
    surfaced = [ep for ep in episodes if ep.runs_seen >= min_runs]
    once = [ep for ep in episodes if ep not in surfaced]
    order = lambda ep: (ep.resolved_at is not None, ep.group, ep.scenario, ep.kind, ep.key, ep.first_seen)
    rows = [ep.row(persistent_runs) for ep in sorted(surfaced, key=order)]
    return {
        'incidents': [r for r in rows if r['state'] == 'open'],
        'resolved': [r for r in rows if r['state'] == 'resolved'][-RESOLVED_LIMIT:],
        'seen_once': [{'group': ep.group, 'scenario': ep.scenario, 'kind': ep.kind, 'class': ep.klass, 'key': ep.key,
                       'seen': ep.last_seen.strftime(STAMP), 'state': 'resolved' if ep.resolved_at else 'open'}
                      for ep in sorted(once, key=order)][:SEEN_ONCE_LIMIT],
        'seen_once_total': len(once), 'suppressed': suppressed[:SEEN_ONCE_LIMIT], 'suppressed_total': len(suppressed),
        'ignored_stopped': ignored, 'epochs': [e.strftime(STAMP) for e in epochs],
        'params': {'min_runs': min_runs, 'persistent_runs': persistent_runs, 'blackout_s': blackout_s, 'evidence': evidence},
    }


def per_group(runs):
    out = {}
    for run in runs:
        row = out.setdefault(run.group, {'runs': 0, 'stopped': 0, 'scenarios': set(), 'first': None, 'last': None})
        row['runs'] += 1
        row['stopped'] += run.state == 'stopped'
        row['scenarios'].add(run.scenario)
        row['first'] = min(row['first'] or run.started, run.started)
        row['last'] = max(row['last'] or run.started, run.started)
    return {g: {'runs': r['runs'], 'stopped': r['stopped'], 'scenarios': sorted(r['scenarios']),
                'first': r['first'].strftime(STAMP), 'last': r['last'].strftime(STAMP)} for g, r in sorted(out.items())}


# ---- baselines ----------------------------------------------------------------------------------------------------

def baseline(runs, label):
    rows, considered = {}, [r for r in runs if r.state != 'stopped']
    for run in considered:
        row = rows.setdefault(f'{run.group}|{run.scenario}', {'runs': 0, 'finished': 0, 'failed': 0, 'blocked': 0,
                                                              'error': 0, 'checks': 0, 'passed': 0, 'seconds': []})
        row['runs'] += 1
        if run.state in row:
            row[run.state] += 1
        row['checks'] += run.total
        row['passed'] += run.passed
        if isinstance(run.seconds, (int, float)):
            row['seconds'].append(float(run.seconds))
    for row in rows.values():
        row['pass_rate'] = round(row['passed'] / row['checks'], 3) if row['checks'] else None
        row['median_seconds'] = round(statistics.median(row['seconds']), 1) if row['seconds'] else None
        del row['seconds']
    window = [considered[0].started.strftime(STAMP), considered[-1].started.strftime(STAMP)] if considered else None
    return {'label': label, 'window': window, 'runs': len(considered), 'rows': rows,
            'note': 'pooled per group and scenario over this window only; compare like with like (same build, '
                    'population and route conditions)'}


def compare(current, saved, pass_drop=0.2, time_up=1.5):
    out = {'label': current['label'], 'baseline_label': saved.get('label'), 'warnings': [], 'rows': []}
    if saved.get('label') != current['label']:
        out['warnings'].append('different labels: the baseline was frozen under another build or condition; '
                               'read the comparison as indicative only')
    keys = sorted(set(current['rows']) | set(saved.get('rows', {})))
    for key in keys:
        now, base = current['rows'].get(key), saved.get('rows', {}).get(key)
        flags = []
        if now is None:
            flags.append('missing now')
        elif base is None:
            flags.append('new scenario')
        else:
            if now['pass_rate'] is not None and base['pass_rate'] is not None and base['pass_rate'] - now['pass_rate'] >= pass_drop:
                flags.append(f'pass rate down {base["pass_rate"]:.2f} -> {now["pass_rate"]:.2f}')
            if now['median_seconds'] and base['median_seconds'] and now['median_seconds'] >= base['median_seconds'] * time_up:
                flags.append(f'median time up {base["median_seconds"]:.0f} s -> {now["median_seconds"]:.0f} s')
            if now['runs'] and base['runs'] and now['error'] / now['runs'] > base['error'] / base['runs']:
                flags.append('more error runs')
        out['rows'].append({'key': key, 'now': now, 'baseline': base, 'flags': flags})
    out['flagged'] = sum(1 for r in out['rows'] if r['flags'])
    return out


# ---- rendering ----------------------------------------------------------------------------------------------------

def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')


def render(result, runs, unreadable, reports_dir):
    lines = ['# Squad incidents (offline, from saved reports)', '',
             f'Source: `{reports_dir}` — {len(runs)} timestamped reports read, {len(unreadable)} unreadable, '
             f'{len(result["ignored_stopped"])} stopped runs ignored (a halt or time budget is not evidence). '
             'Saved reports only: not live bot or server state. A `blocked` incident is a missing prerequisite or '
             'capability the scenario named, not a server defect; `defect-candidate` is a failed check with the body '
             'connected, for a person to judge.', '',
             f'Gates: shown after {result["params"]["min_runs"]} runs; '
             f'persistent from {result["params"]["persistent_runs"]} runs; post-restart blackout '
             f'{result["params"]["blackout_s"]} s for bot-down issues; {result["params"]["evidence"]} newest evidence '
             f'entries each. Epochs (server restarts): ' + (', '.join(result['epochs']) or 'none given') + '.', '']
    lines += ['## Open', '']
    if result['incidents']:
        lines += ['| Id | Group | Scenario | Kind | Class | Key | Runs | First | Last | Severity | Latest evidence |',
                  '|---|---|---|---|---|---|---|---|---|---|---|']
        for r in result['incidents']:
            ev = r['evidence'][-1] if r['evidence'] else {}
            lines.append(f'| {r["id"]} | {r["group"]} | {cell(r["scenario"])} | {r["kind"]} | {r["class"]} | {cell(r["key"])} '
                         f'| {r["runs_seen"]} | {r["first_seen"][5:16]} | {r["last_seen"][5:16]} | {r["severity"]} '
                         f'| {cell(ev.get("report", ""))}: {cell(short(ev.get("detail", ""), 120))} |')
    else:
        lines.append('None.')
    lines += ['', f'## Resolved (newest {RESOLVED_LIMIT})', '']
    if result['resolved']:
        lines += ['| Id | Group | Scenario | Kind | Class | Key | Runs | First | Resolved | By |', '|---|---|---|---|---|---|---|---|---|---|']
        for r in result['resolved']:
            lines.append(f'| {r["id"]} | {r["group"]} | {cell(r["scenario"])} | {r["kind"]} | {r["class"]} | {cell(r["key"])} '
                         f'| {r["runs_seen"]} | {r["first_seen"][5:16]} | {r["resolved_at"][5:16]} | {cell(r["resolved_by"])} |')
    else:
        lines.append('None.')
    lines += ['', f'## Seen once ({result["seen_once_total"]}, not yet incidents)', '']
    for r in result['seen_once']:
        lines.append(f'- {r["group"]} · {cell(r["scenario"])} · {r["kind"]} · {r["class"]} · {cell(r["key"])} · {r["seen"][5:16]} · {r["state"]}')
    if not result['seen_once']:
        lines.append('None.')
    if result['suppressed_total']:
        lines += ['', f'## Suppressed in post-restart blackout ({result["suppressed_total"]})', '']
        lines += [f'- {cell(s["report"])} · {s["kind"]} · {cell(s["key"])}' for s in result['suppressed']]
    if unreadable:
        lines += ['', '## Unreadable reports', ''] + [f'- {cell(u["report"])}: {cell(u["error"])}' for u in unreadable]
    lines += ['', '## Runs per group', '', '| Group | Runs | Stopped | Scenarios | First | Last |', '|---|---|---|---|---|---|']
    for g, r in per_group(runs).items():
        lines.append(f'| {g} | {r["runs"]} | {r["stopped"]} | {len(r["scenarios"])} | {r["first"][5:16]} | {r["last"][5:16]} |')
    return '\n'.join(lines) + '\n'


def render_compare(result):
    lines = [f'# Baseline comparison: {result["label"]} vs {result["baseline_label"]}', '']
    lines += [f'Warning: {w}' for w in result['warnings']]
    lines += ['', f'{result["flagged"]} of {len(result["rows"])} rows flagged.', '',
              '| Group / scenario | Runs now / base | Pass rate now / base | Median s now / base | Flags |', '|---|---|---|---|---|']
    fmt = lambda row, k: ('-' if row is None or row.get(k) is None else row[k])
    for r in result['rows']:
        lines.append(f'| {cell(r["key"])} | {fmt(r["now"], "runs")} / {fmt(r["baseline"], "runs")} '
                     f'| {fmt(r["now"], "pass_rate")} / {fmt(r["baseline"], "pass_rate")} '
                     f'| {fmt(r["now"], "median_seconds")} / {fmt(r["baseline"], "median_seconds")} | {cell("; ".join(r["flags"]))} |')
    return '\n'.join(lines) + '\n'


# ---- command line -------------------------------------------------------------------------------------------------

def read_epochs(args):
    epochs = [parse_time(e) for e in (args.epoch or [])]
    if args.epochs:
        data = json.loads(Path(args.epochs).read_text(encoding='utf-8'))
        epochs += [parse_time(e) for e in (data if isinstance(data, list) else data.get('epochs', []))]
    bad = [e for e in epochs if e is None]
    if bad:
        sys.exit('epochs must be "YYYY-MM-DD HH:MM:SS"')
    return epochs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('command', nargs='?', default='incidents', choices=('incidents', 'baseline', 'compare'))
    ap.add_argument('--reports', default=str(DEFAULT_REPORTS))
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--epoch', action='append', help='server start time; repeatable')
    ap.add_argument('--epochs', help='JSON list (or {"epochs": [...]}) of server start times')
    ap.add_argument('--since'), ap.add_argument('--until')
    ap.add_argument('--min-runs', type=int, default=MIN_RUNS)
    ap.add_argument('--persistent-runs', type=int, default=PERSISTENT_RUNS)
    ap.add_argument('--blackout', type=int, default=BLACKOUT_S), ap.add_argument('--evidence', type=int, default=EVIDENCE)
    ap.add_argument('--save'), ap.add_argument('--baseline'), ap.add_argument('--label', default='unlabelled')
    args = ap.parse_args(argv)
    since, until = parse_time(args.since), parse_time(args.until)
    runs, unreadable = load_runs(args.reports, since=since, until=until)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime(STAMP)
    if args.command == 'incidents':
        result = build(runs, read_epochs(args), args.min_runs, args.persistent_runs, args.blackout, args.evidence)
        result.update(generated=generated, reports=str(args.reports), reports_read=len(runs), unreadable=unreadable,
                      per_group=per_group(runs), scope='saved reports only; not live bot or server state')
        (out / 'incidents.json').write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        (out / 'incidents.md').write_text(render(result, runs, unreadable, args.reports), encoding='utf-8')
        print(f'{len(result["incidents"])} open, {len(result["resolved"])} resolved, {result["seen_once_total"]} seen once, '
              f'{len(runs)} reports -> {out / "incidents.md"}')
    elif args.command == 'baseline':
        if not args.save:
            sys.exit('baseline needs --save FILE')
        data = baseline(runs, args.label)
        data['generated'] = generated
        Path(args.save).write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')
        print(f'baseline {args.label}: {data["runs"]} runs, {len(data["rows"])} rows -> {args.save}')
    else:
        if not args.baseline:
            sys.exit('compare needs --baseline FILE')
        saved = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
        result = compare(baseline(runs, args.label), saved)
        result['generated'] = generated
        (out / 'compare.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
        (out / 'compare.md').write_text(render_compare(result), encoding='utf-8')
        print(f'{result["flagged"]} of {len(result["rows"])} rows flagged -> {out / "compare.md"}')


if __name__ == '__main__':
    main()
