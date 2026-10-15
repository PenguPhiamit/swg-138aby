"""Fleet-scale load test for the TEST galaxy: extra plain bodies (load-groups.json) that log in, walk and fight
near their starting city, plus a sampler for the server's and the PC's memory and CPU.
Owner question, 15 Oct: how many test bots can the PC carry? Results: Bot-reports/fleet-scale-test.md.

Run inside Debian as swgemu:
  load_fleet.py step N [WARMUP_S] [SAMPLE_S]   bring the first N load bots online, let them play, sample, summarise
  load_fleet.py sample SECONDS                 sample only (starts no bots)
  load_fleet.py down                           log every load bot out
The load bots need no AgentAccounts entry (no /agentpath: they walk in straight lines), so adding them needs no
galaxy restart and leaves a running squad.py run alone. Summaries: /var/tmp/swg-bots/load/step-N-<time>.json.
Safety: the test stops and logs the load bots out if WSL MemAvailable falls under 4 GB or Windows commit headroom
under 6 GB (the PC crashed from memory pressure on 15 Oct 07:31).
"""
import json, math, os, random, re, subprocess, sys, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from squad import Bot, BotDown, Group, NOW, RUNS  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = RUNS / 'load'
LOG = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/core3.log')
POWERSHELL = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
MIN_AVAILABLE_KB, MIN_COMMIT_KB = 4 * 1024 ** 2, 6 * 1024 ** 2
CLK = os.sysconf('SC_CLK_TCK')
TRIP = threading.Event()
TRIP_WHY = []
LAG = re.compile(r'\blag|slow|overload|behind|deadlock|took \d+ ?ms|timed? ?out', re.I)
NOISE = ('could not open lua', 'handleNetStatusRequest', 'ClientInactivityMessage')


def groups():
    spec = json.loads((HERE / 'load-groups.json').read_text(encoding='utf-8'))
    return [(Group(name, g), g['city']) for name, g in spec['groups'].items()]


def first_n(n):
    """The first n load bots, in file order, with their group's city."""
    chosen = []
    for group, city in groups():
        for bot in group.bots:
            if len(chosen) < n:
                chosen.append((bot, city))
    return chosen


# ---- sampling ----

def read_proc(pid, *names):
    try:
        stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        ticks = int(stat[11]) + int(stat[12])
        kb = {}
        for name in names:
            path = 'smaps_rollup' if name == 'Pss' else 'status'
            for line in Path(f'/proc/{pid}/{path}').read_text().splitlines():
                if line.startswith(name + ':'):
                    kb[name] = int(line.split()[1])
        return ticks, kb
    except (OSError, ValueError, IndexError):
        return None


def pids(exe):
    found = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                if (entry / 'cmdline').read_bytes().split(b'\0')[0].endswith(exe):
                    found.append(int(entry.name))
            except OSError:
                pass
    return found


def mem_available_kb():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1])


class Sampler(threading.Thread):
    """Every 10 s: core3 CPU and RSS, the bodies' CPU, RSS and PSS, WSL MemAvailable, this driver's CPU.
    Windows commit headroom (FreeVirtualMemory) every 30 s from a second thread."""

    def __init__(self):
        super().__init__(daemon=True)
        self.rows, self.phase, self.commit_kb, self.done = [], 'up', None, threading.Event()
        threading.Thread(target=self._commit, daemon=True).start()

    def _commit(self):
        while not self.done.is_set():
            try:
                text = subprocess.run([POWERSHELL, '-NoProfile', '-Command',
                                       '(Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory'],
                                      capture_output=True, text=True, timeout=40).stdout
                self.commit_kb = int(text.strip().splitlines()[-1])
            except (OSError, ValueError, IndexError, subprocess.SubprocessError):
                pass
            self.done.wait(30)

    def run(self):
        server = [p for p in pids(b'core3') if 'testgalaxy' in os.readlink(f'/proc/{p}/cwd')]
        last, last_t = {}, time.time()
        while not self.done.is_set():
            now = time.time()
            ticks, row = {}, {'t': round(now), 'phase': self.phase}
            core = read_proc(server[0], 'VmRSS') if server else None
            if core:
                ticks['core3'] = core[0]
                row['core3_rss_mb'] = round(core[1].get('VmRSS', 0) / 1024)
            bodies = [(p, read_proc(p, 'VmRSS', 'Pss')) for p in pids(b'core3client')]
            bodies = [(p, r) for p, r in bodies if r]
            ticks.update({p: r[0] for p, r in bodies})
            row['bodies'] = len(bodies)
            row['bodies_rss_mb'] = round(sum(r[1].get('VmRSS', 0) for _, r in bodies) / 1024)
            row['bodies_pss_mb'] = round(sum(r[1].get('Pss', 0) for _, r in bodies) / 1024)
            me = read_proc(os.getpid())
            ticks['driver'] = me[0] if me else 0
            row['wsl_available_mb'] = round(mem_available_kb() / 1024)
            row['commit_headroom_mb'] = round(self.commit_kb / 1024) if self.commit_kb else None
            if last:
                span = (now - last_t) * CLK
                row['core3_cores'] = round((ticks.get('core3', 0) - last.get('core3', 0)) / span, 2)
                row['bodies_cores'] = round(sum(t - last[p] for p, t in ticks.items()
                                                if isinstance(p, int) and p in last) / span, 2)
                row['driver_cores'] = round((ticks['driver'] - last['driver']) / span, 2)
                self.rows.append(row)
            last, last_t = ticks, now
            if mem_available_kb() < MIN_AVAILABLE_KB:
                TRIP_WHY.append(f'WSL MemAvailable {row["wsl_available_mb"]} MB'); TRIP.set()
            if self.commit_kb and self.commit_kb < MIN_COMMIT_KB:
                TRIP_WHY.append(f'commit headroom {row["commit_headroom_mb"]} MB'); TRIP.set()
            self.done.wait(10)


def log_window(start):
    """What core3.log said after byte `start`: line counts and the lag-like messages."""
    with open(LOG, 'rb') as stream:
        stream.seek(start)
        text = stream.read().decode('utf-8', 'replace')
    lines = text.splitlines()
    lag = [l for l in lines if LAG.search(l) and not any(n in l for n in NOISE)]
    kinds = {}
    for line in lag:
        key = re.sub(r'\d+', 'N', line.split('] ', 2)[-1])[:110]
        kinds[key] = kinds.get(key, 0) + 1
    return {'lines': len(lines), 'warnings': sum('WARNING' in l for l in lines),
            'errors': sum('ERROR' in l and 'handleNetStatusRequest' not in l for l in lines),
            'netstatus_errors': sum('handleNetStatusRequest' in l for l in lines),
            'lag_lines': len(lag), 'lag_kinds': sorted(kinds.items(), key=lambda kv: -kv[1])[:6]}


def stats(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return {'min': min(values), 'avg': round(sum(values) / len(values), 2), 'max': max(values)}


# ---- bots ----

def bring_up(bot, city):
    """Log one bot in (creating its character the first time) and move it out of the tutorial room."""
    if bot.running() and not bot.stale() and bot.status().get('connected') is not False:
        return 'online'
    began = time.time()
    result = bot.start()
    if result == 'missing':
        result = bot.start(create=True, wait=150)
        if result != 'created':
            return f'create {result}'
        result = bot.start()
    if result != 'ready':
        return f'login {result}'
    status = bot.status()
    if status.get('planet') == 'tutorial':
        bot.request('command', 5, name='newbieSelectStartingLocation', args=city, target=0)
        bot.wait_for('"scene_start"', 45)
        time.sleep(3)
        status = bot.status()
    return f'ready on {status.get("planet")} in {time.time() - began:.0f} s'


def up(n, results):
    """The first n load bots online: groups in parallel, each group's members one after another."""
    by_group = {}
    for bot, city in first_n(n):
        by_group.setdefault(bot.group.name, []).append((bot, city))

    def one_group(pairs):
        for bot, city in pairs:
            if TRIP.is_set():
                results[bot.first] = 'skipped (safety stop)'
                continue
            try:
                results[bot.first] = bring_up(bot, city)
            except BotDown as exc:
                results[bot.first] = f'down: {exc}'
    threads = [threading.Thread(target=one_group, args=(pairs,)) for pairs in by_group.values()]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def wild(obj):
    return str(obj.get('name', '')).startswith('@mob/creature_names:') and obj.get('posture') == 'upright'


def play(bot, until, tally):
    """Walk in 40-60 m straight legs, wandering outward up to 600 m from the start, and fight any ordinary
    creature within 80 m. A downed bot waits for recovery (and takes the clone offer)."""
    try:
        home = bot.status()
        hx, hy = home.get('x', 0), home.get('y', 0)
        heading = random.uniform(0, 2 * math.pi)
        while time.time() < until and not TRIP.is_set():
            if bot.posture() in ('incapacitated', 'dead'):
                bot.recover(60)
                tally['recoveries'] += 1
                continue
            prey = next((o for o in bot.look(80, 'CREO', 200) if wild(o)), None)
            if prey:
                reply = bot.fight(prey['oid'], min(45, max(5, until - time.time())))
                tally['fights'] += 1
                tally['fight_ok'] += bool(reply.get('ok'))
                continue
            here = bot.status()
            x, y = here.get('x', hx), here.get('y', hy)
            if math.hypot(x - hx, y - hy) > 600:
                heading = math.atan2(hy - y, hx - x) + random.uniform(-0.8, 0.8)
            leg = random.uniform(40, 60)
            reply = bot.request('move', 60, x=x + leg * math.cos(heading), y=y + leg * math.sin(heading),
                                timeout=40, path=False)
            tally['moves'] += 1
            if not reply.get('arrived'):
                tally['moves_stuck'] += 1
                heading = random.uniform(0, 2 * math.pi)
            time.sleep(random.uniform(0.5, 2))
    except BotDown:
        tally['dropped'] += 1


def probe(bot, until, rtts):
    """Server round trip: say a line and time the server's echo (the body hears its own spatial chat)."""
    n = 0
    while time.time() < until and not TRIP.is_set():
        n += 1
        tag = f'load probe {n}'
        try:
            bot._read()
            bot.inbox = []
            began = time.time()
            bot._write({'cmd': 'say', 'text': tag})
            heard = None
            while time.time() - began < 10 and heard is None:
                bot._read()
                if any(e.get('event') == 'chat' and tag in json.dumps(e) for e in bot.inbox):
                    heard = time.time() - began
                time.sleep(0.02)
            rtts.append(round(heard * 1000) if heard is not None else None)
        except BotDown:
            rtts.append(None)
        time.sleep(15)


def down():
    for group, _ in groups():
        for bot in group.bots:
            if bot.running():
                bot.stop()
            (NOW / f'{bot.first}.json').unlink(missing_ok=True)  # off the live map
            for old in (bot.dir / 'log').rglob('core3client*.log'):  # a fighting body logs about 2 MB a minute
                old.unlink(missing_ok=True)
    print('load bots logged out:', len(pids(b'core3client')), 'bodies still running (the squads)')


def step(n, warmup, sample_s):
    OUT.mkdir(parents=True, exist_ok=True)
    sampler = Sampler()
    sampler.start()
    began = time.time()
    results = {}
    up(n, results)
    up_seconds = round(time.time() - began)
    online = [(b, c) for b, c in first_n(n) if b.running()]
    tally = {k: 0 for k in ('fights', 'fight_ok', 'moves', 'moves_stuck', 'recoveries', 'dropped')}
    rtts, log_start, threads = [], None, []
    if not TRIP.is_set() and online:
        until = time.time() + warmup + sample_s
        prober, players = online[0][0], online[1:]
        threads = [threading.Thread(target=play, args=(b, until, tally), daemon=True) for b, _ in players]
        threads.append(threading.Thread(target=probe, args=(prober, until, rtts), daemon=True))
        for thread in threads:
            thread.start()
        if not TRIP.wait(warmup):
            sampler.phase = 'sample'
            rtts.clear()
            log_start = LOG.stat().st_size
            TRIP.wait(sample_s)
        for thread in threads:
            thread.join(timeout=120)
    sampler.done.set()
    sampler.join(timeout=15)
    window = [r for r in sampler.rows if r['phase'] == 'sample']
    summary = {
        'load_bots_asked': n, 'load_bots_online': len(online), 'bodies_total': stats([r['bodies'] for r in window]),
        'up_seconds': up_seconds, 'login_failures': {k: v for k, v in results.items() if not v.startswith(('ready', 'online'))},
        'sample_seconds': sample_s if window else 0, 'samples': len(window),
        'core3_cores': stats([r.get('core3_cores') for r in window]),
        'core3_rss_mb': stats([r.get('core3_rss_mb') for r in window]),
        'bodies_cores': stats([r.get('bodies_cores') for r in window]),
        'bodies_rss_mb': stats([r.get('bodies_rss_mb') for r in window]),
        'bodies_pss_mb': stats([r.get('bodies_pss_mb') for r in window]),
        'driver_cores': stats([r.get('driver_cores') for r in window]),
        'wsl_available_mb': stats([r.get('wsl_available_mb') for r in window]),
        'commit_headroom_mb': stats([r.get('commit_headroom_mb') for r in window]),
        'lowest_during_logins': {'wsl_available_mb': min((r['wsl_available_mb'] for r in sampler.rows), default=None),
                                 'commit_headroom_mb': min((r['commit_headroom_mb'] for r in sampler.rows
                                                            if r.get('commit_headroom_mb')), default=None)},
        'chat_rtt_ms': stats(rtts), 'chat_rtt_missed': sum(r is None for r in rtts), 'chat_rtt_all': rtts,
        'activity': tally, 'server_log': log_window(log_start) if log_start is not None else None,
        'safety_stop': TRIP_WHY[:1],
    }
    (OUT / f'step-{n}-{time.strftime("%m%d-%H%M")}.json').write_text(json.dumps({'summary': summary, 'rows': sampler.rows}, indent=1))
    print(json.dumps(summary, indent=1))
    if TRIP.is_set():
        print('SAFETY STOP:', TRIP_WHY[0], '- logging the load bots out')
        down()


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == 'step':
        step(int(args[1]), int(args[2]) if len(args) > 2 else 180, int(args[3]) if len(args) > 3 else 300)
    elif args[0] == 'sample':
        s = Sampler(); s.phase = 'sample'; s.start(); time.sleep(int(args[1])); s.done.set(); s.join(15)
        start = s.rows
        print(json.dumps({k: stats([r.get(k) for r in start]) for k in
                          ('bodies', 'core3_cores', 'core3_rss_mb', 'bodies_cores', 'bodies_rss_mb', 'bodies_pss_mb',
                           'wsl_available_mb', 'commit_headroom_mb')}, indent=1))
    elif args[0] == 'down':
        down()
    else:
        raise SystemExit(__doc__)
