"""Regression gate for the TEST galaxy (Claude, 15 Oct 2026; week 1 of the route in SWG-roadmap.md).

After every test-galaxy start: is the server healthy, are all squad bots in, and does one round of the squad plan
still pass every check that passed before? Each check keeps a short history (P/F, newest last):
  REGRESSION  passed last time, fails now, and never failed in its history: the gate FAILS
  FLAKY       fails now after passing, but has failed before too: reported, does not fail the gate
  FIXED       failed last time, passes now
  NEW         no history yet (a new or renamed check)
  FAILING     failed last time and fails again (known; listed)
  MISSING     passed last time but did not run this time (the scenario stopped early or changed)
The gate also FAILS if the server isn't running and initialized, a bot can't be logged in, or a scenario crashes.
A scenario that runs no checks, or notes BLOCKED, is a WARN line: it doesn't fail the gate, but nothing it covers
was tested.
With no history yet, the history is seeded from the newest squad reports of the same scenarios.

One verdict in Bot-reports/GATE.md; details in Bot-reports/gate/<stamp>.json; histories in Bot-reports/gate/baseline.json.

Inside Debian as swgemu:
  python3 gate.py run [--round-minutes 10] [--plan FILE]   run the gate now (waits up to 30 min for a running round)
  python3 gate.py start                                    the same in the background (the 30-minute cycle uses it)
  python3 gate.py due                                      'due', 'done', 'running' or 'no server' for the running galaxy
  python3 gate.py last                                     print GATE.md
"""
import hashlib, json, os, subprocess, sys, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
REPORTS = OUTPUTS / 'Bot-reports'
GATE_DIR = REPORTS / 'gate'
GATE_MD = REPORTS / 'GATE.md'
BASELINE = GATE_DIR / 'baseline.json'
RUNNING = GATE_DIR / 'RUNNING'
SQUAD = HERE / 'squad.py'
TEST_GALAXY = HERE.parent / 'test_galaxy.py'
PLAN = OUTPUTS / 'Agent' / 'squad-plan.txt'
DEV = Path('/opt/swg/Core3-dev')
ARCHIVE = Path('/opt/swg/tre/local_planets.tre')
HISTORY = 8          # results kept per check
SEED_REPORTS = 3     # newest reports per scenario used to seed an empty history
BUSY_WAIT = 30 * 60  # how long to wait for another squad run to finish

sys.path.insert(0, str(HERE))
from squad import load_spec, newest_server_start  # noqa: E402


def sh(args, timeout=600):
    run = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return run.returncode, run.stdout + run.stderr


def server_key():
    """Identifies one server process: the WSL boot plus the core3 start time. None when no server runs."""
    start = newest_server_start()
    if start is None:
        return None
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    return f'{boot}:{start}'


def load_baseline():
    try:
        return json.loads(BASELINE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {'checks': {}, 'last_server': None}


def pid_alive(path):
    try:
        pid = int(path.read_text().split()[0])
        return Path(f'/proc/{pid}').exists() and pid != os.getpid()
    except (OSError, ValueError, IndexError):
        return False


def health():
    info = {}
    code, out = sh([sys.executable, str(TEST_GALAXY), 'status'], 120)
    try:
        info['galaxy'] = json.loads(out[out.index('{'):out.rindex('}') + 1])
    except ValueError:
        info['galaxy'] = {'running': False, 'error': out[-300:]}
    code, out = sh(['git', '-C', str(DEV), 'rev-parse', '--short=8', 'HEAD'], 60)
    info['dev'] = out.strip() if code == 0 else '?'
    try:
        info['archive'] = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()[:8]
    except OSError:
        info['archive'] = '?'
    return info


def bots_online():
    """(online, expected) as the cycle counts them: status lines without HNone/offline."""
    expected = sum(len(g['members']) for g in load_spec()['groups'].values())
    code, out = sh([sys.executable, str(SQUAD), 'status'], 240)
    lines = [l for l in out.splitlines() if l.startswith('  ') and l[2:3].isupper()]
    return sum(1 for l in lines if 'HNone' not in l and 'offline' not in l), expected


def plan_scenarios(plan_file):
    names = [l.strip() for l in plan_file.read_text(encoding='utf-8').splitlines() if l.strip().endswith('.py')]
    return [HERE / 'scenarios' / n for n in names]


def report_checks(report):
    """(group, scenario, record) for one squad report file."""
    record = json.loads(report.read_text(encoding='utf-8'))
    return record['group'], record['scenario'], record


def seed(baseline, scenarios):
    """An empty history starts from the newest squad reports of the same scenarios (oldest first)."""
    for path in scenarios:
        for folder in (p for p in REPORTS.iterdir() if p.is_dir() and p.name not in ('runs', 'gate', 'triage')):
            reports = sorted(folder.glob(f'*-{path.stem}.json'))[-SEED_REPORTS:]
            for report in reports:
                try:
                    group, scenario, record = report_checks(report)
                except (OSError, ValueError, KeyError):
                    continue
                for c in record.get('checks', []):
                    entry = baseline['checks'].setdefault(f'{group}|{scenario}|{c["label"]}', {'history': ''})
                    entry['history'] = (entry['history'] + ('P' if c['ok'] else 'F'))[-HISTORY:]
    baseline['seeded'] = datetime.now().isoformat(timespec='seconds')


def classify(history, ok):
    if not history:
        return 'NEW'
    last = history[-1]
    if ok:
        return 'FIXED' if last == 'F' else 'PASS'
    if last == 'F':
        return 'FAILING'
    return 'FLAKY' if 'F' in history else 'REGRESSION'


def run_gate(args):
    stamp = f'{datetime.now():%Y%m%d-%H%M%S}'
    GATE_DIR.mkdir(parents=True, exist_ok=True)
    RUNNING.write_text(f'{os.getpid()} {stamp}\n')
    try:
        return _run_gate(args, stamp)
    finally:
        RUNNING.unlink(missing_ok=True)


def _run_gate(args, stamp):
    round_minutes = args[args.index('--round-minutes') + 1] if '--round-minutes' in args else '10'
    plan_file = Path(args[args.index('--plan') + 1]) if '--plan' in args else PLAN
    scenarios = plan_scenarios(plan_file)
    result = {'stamp': stamp, 'started': datetime.now().isoformat(timespec='seconds'), 'plan': [p.name for p in scenarios],
              'server': server_key(), 'problems': [], 'warnings': []}
    result['health'] = h = health()
    galaxy = h['galaxy']
    if not (galaxy.get('running') and galaxy.get('initialized')):
        result['problems'].append('server not running and initialized')
        return finish(result, None)
    online, expected = bots_online()
    if online < expected:
        sh([sys.executable, str(SQUAD), 'setup'], 900)
        online, expected = bots_online()
    result['bots'] = f'{online}/{expected}'
    if online < expected:
        result['problems'].append(f'bots online {online}/{expected} after setup')
    # Wait for a running squad round (the cycle's) to end: one driver at a time.
    active = REPORTS / 'runs' / 'ACTIVE'
    waited = time.monotonic()
    while pid_alive(active) and time.monotonic() - waited < BUSY_WAIT:
        time.sleep(20)
    if pid_alive(active):
        result['problems'].append('another squad run kept the bots busy for 30 min; gate skipped')
        result['skipped'] = True
        return finish(result, None)
    began = time.time()
    code, out = sh([sys.executable, str(SQUAD), 'run', *map(str, scenarios), '--rounds', '1',
                    '--round-minutes', round_minutes, '--no-fallback', '--stamp', 'gate-' + stamp], 3600)
    (GATE_DIR / f'{stamp}.txt').write_text(out, encoding='utf-8')
    if code != 0:
        result['problems'].append(f'squad.py run exited {code}: {out.strip().splitlines()[-1][:200] if out.strip() else ""}')
    baseline = load_baseline()
    if not baseline['checks']:
        seed(baseline, scenarios)
    rows, ran = [], set()
    for folder in (p for p in REPORTS.iterdir() if p.is_dir() and p.name not in ('runs', 'gate', 'triage')):
        for report in folder.glob('*.json'):
            if report.stat().st_mtime < began:
                continue
            try:
                group, scenario, record = report_checks(report)
            except (OSError, ValueError, KeyError):
                continue
            if scenario not in result['plan']:
                continue
            ran.add((group, scenario))
            if record.get('error'):
                result['problems'].append(f'{group} {scenario}: {record["error"][:200]}')
            blocked = [n for n in record.get('notes', []) if n.startswith('BLOCKED')]
            if not record.get('checks'):
                result['warnings'].append(f'{group} {scenario}: no checks ran ({record.get("state")})'
                                          + (f': {blocked[0][:160]}' if blocked else ''))
            elif blocked:
                result['warnings'].append(f'{group} {scenario}: {blocked[0][:200]}')
            for c in record.get('checks', []):
                key = f'{group}|{scenario}|{c["label"]}'
                entry = baseline['checks'].setdefault(key, {'history': ''})
                rows.append({'key': key, 'ok': c['ok'], 'status': classify(entry['history'], c['ok']),
                             'detail': str(c.get('detail', ''))[:200]})
                entry['history'] = (entry['history'] + ('P' if c['ok'] else 'F'))[-HISTORY:]
    for path in scenarios:
        if not any(s == path.name for _, s in ran):
            result['problems'].append(f'{path.name}: no report from this round')
    seen = {r['key'] for r in rows}
    for key, entry in baseline['checks'].items():
        group, scenario, _ = key.split('|', 2)
        if (group, scenario) in ran and key not in seen and entry['history'].endswith('P'):
            rows.append({'key': key, 'ok': None, 'status': 'MISSING', 'detail': ''})
    result['checks'] = rows
    baseline['last_server'] = result['server']
    BASELINE.write_text(json.dumps(baseline, indent=1, ensure_ascii=False), encoding='utf-8')
    return finish(result, rows)


def finish(result, rows):
    rows = rows or []
    count = lambda s: [r for r in rows if r['status'] == s]
    regressions = count('REGRESSION')
    if result.get('skipped'):
        verdict = 'SKIPPED'
    else:
        verdict = 'FAIL' if result['problems'] or regressions else 'PASS'
    result['verdict'] = verdict
    result['finished'] = datetime.now().isoformat(timespec='seconds')
    (GATE_DIR / f'{result["stamp"]}.json').write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding='utf-8')
    h = result.get('health', {})
    g = h.get('galaxy', {})
    passed = len([r for r in rows if r['ok']])
    lines = [f'# Gate: {verdict}', '',
             f'{result["finished"].replace("T", " ")} · dev `{h.get("dev", "?")}` · archive `{h.get("archive", "?")}` · '
             f'bots {result.get("bots", "?")} · server errors at start: {g.get("error_lines", "?")} · '
             f'{passed}/{len([r for r in rows if r["ok"] is not None])} checks passed · details `Bot-reports/gate/{result["stamp"]}.json`', '']
    for problem in result['problems']:
        lines.append(f'- **PROBLEM** {problem}')
    for warning in result.get('warnings', []):
        lines.append(f'- WARN {warning}')
    for status, title in (('REGRESSION', 'Regressions (passed before, fail now)'), ('FLAKY', 'Flaky (failed before too)'),
                          ('MISSING', 'Missing (passed before, did not run)'), ('FIXED', 'Fixed'),
                          ('NEW', 'New checks'), ('FAILING', 'Still failing')):
        items = count(status)
        if not items:
            continue
        lines.append(f'', )
        lines.append(f'## {title}: {len(items)}')
        for r in items[:15]:
            mark = '' if r['ok'] is None else (' (pass)' if r['ok'] else ' (FAIL)')
            lines.append(f'- {r["key"].replace("|", " · ")}{mark}' + (f' — {r["detail"][:120]}' if r['detail'] and not r['ok'] else ''))
        if len(items) > 15:
            lines.append(f'- … {len(items) - 15} more in the JSON')
    GATE_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    return 0 if verdict == 'PASS' else 1


def main():
    args = sys.argv[1:]
    command = args[0] if args else ''
    if command == 'run':
        return run_gate(args[1:])
    if command == 'start':
        if pid_alive(RUNNING):
            print('a gate is already running')
            return 0
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        log = GATE_DIR / f'{datetime.now():%Y%m%d-%H%M%S}.log'
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'run', *args[1:]],
                                 stdout=open(log, 'w', encoding='utf-8'), stderr=subprocess.STDOUT,
                                 start_new_session=True, cwd=str(HERE))
        print(f'gate started in the background (pid {child.pid}); verdict in Bot-reports/GATE.md')
        return 0
    if command == 'due':
        key = server_key()
        print('no server' if key is None else 'running' if pid_alive(RUNNING)
              else 'done' if load_baseline().get('last_server') == key else 'due')
        return 0
    if command == 'last':
        print(GATE_MD.read_text(encoding='utf-8') if GATE_MD.exists() else 'No gate yet.')
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
