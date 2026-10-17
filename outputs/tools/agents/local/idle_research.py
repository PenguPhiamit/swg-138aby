"""Idle research for the owner's local model (Claude, 15 Oct 2026). Owner: "when ollama goes idle for more than 10 mins,
start researching game mechanics (taking over for gpt) that will help our testing".

Inside Debian as swgemu; swg-idle-research.timer runs `check` every 5 minutes:

    python3 idle_research.py check     # start the next open topic if the model has been idle 10+ minutes
    python3 idle_research.py check --now   # start it now, without the idle wait (when the owner asks; STOP still holds)
    python3 idle_research.py status    # say why it would or wouldn't start now

Idle means all of: no /api/chat or /api/generate request in Ollama's log for 10 minutes (this runner's own last topic
doesn't count, so topics follow each other while nobody else needs the model); the GPU below 30 %; none of the owner's
SWG clients running; no Agent/local-research/STOP file; and (15 Oct) at least 8 GB of Windows commit headroom, because
Ollama's prompt cache once grew by ~15 GB in 25 requests (memguard.py).

Where Ollama runs comes from ollama_url.py (OLLAMA_URL, then ollama-url.txt, then 127.0.0.1). For a server on another
PC (REMOTE-OLLAMA.md) the log, GPU and client checks are about this PC and are skipped; instead each timer run asks
the server's /api/ps which models are loaded and when they expire. A request that finishes moves a model's expires_at,
so the same list on consecutive runs means nobody used it; 10 minutes of that, written to state.json, count as idle.

Each topic in Agent/local-research/queue.json names Core3-dev sources (MMOCoreORB-relative, with an optional
:START-END line range) and project files (prefix h:). They are copied, read-only and line-numbered, into
Agent/local-research/<id>/src/, and local_agent.py (file tools inside that folder only: no shell, no network) writes
<id>/report.md. Reports are notes: Claude or ChatGPT checks them against the source before a test relies on them.
Nothing here touches the server, the bots or the board. Anyone may add an "open" topic to the queue.

A topic with "kind": "map" and "job": <name> is a chunk job instead (local_jobs.py names them: proofread, bot-gaps):
local_jobs.py prepares <id>/input.jsonl, local_map.py asks the model about one chunk at a time (yielding to the owner's
client and to low memory; a paused topic stays open and resumes), and local_jobs.py writes <id>/report.md.

Fallback (17 Oct): ollama-url.txt may list several servers (the friend's PC, then this PC); each timer run uses the
first that answers (ollama_url.pick) and hands that one address, model and context size to the job. Optional topic
fields: "model" runs the topic with that model (it waits while the server in use doesn't have it), "ctx" with that
context size, and "local_only": true keeps it on this PC (for text with real people's names). Agent/local-model.md is
the workflow.

Chaining (owner, 17 Oct): while the server in use is another PC, `check` starts the next topic as soon as one finishes,
after the same checks, instead of waiting for the next timer run. It stays inside the service's 4 hours (a chained
topic that reaches the end goes back to open) and stops after 3 failures in a row. This PC keeps one topic per run.
"""
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
import memguard
import ollama_url

H = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
BASE = H / 'outputs' / 'Agent' / 'local-research'
QUEUE, LOG, STATE, STOP = BASE / 'queue.json', BASE / 'LOG.md', BASE / 'state.json', BASE / 'STOP'
CORE3 = Path('/opt/swg/Core3-dev/MMOCoreORB')
AGENT = H / 'outputs' / 'tools' / 'agents' / 'local' / 'local_agent.py'
MAP, JOBS = AGENT.with_name('local_map.py'), AGENT.with_name('local_jobs.py')
START_HEADROOM_GB = 8.0   # don't start below this: the model and its cache need room (memguard.py)
OLLAMA_LOG = Path('/mnt/c/Users/Pengw/AppData/Local/Ollama/server.log')
NVIDIA_SMI = '/usr/lib/wsl/lib/nvidia-smi'  # WSL's GPU tools; not on a systemd service's PATH
IDLE_S, OWN_SLACK_S, GPU_BUSY = 600, 90, 30
# Server on another PC: timer jitter (AccuracySec=30s) allowed on the 10 minutes; the longest gap between two timer runs
# that still counts as watching the server continuously; how long past its expiry a loaded model counts as mid-request.
REMOTE_SLACK_S, REMOTE_GAP_S, OVERDUE_S = 30, 8 * 60, 20
EXPIRES = re.compile(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(?:\.(\d+))?(Z|[+-]\d\d:\d\d)')
SOURCE_CAP = 120_000  # characters per topic at a 64K-token window (scaled by source_cap()): the brief, files and notes share it
MAX_STEPS, RUN_LIMIT_S = 40, 3 * 3600
# Chaining topics on the friend's PC: swg-idle-research.service may run 4 h (TimeoutStartSec) less a margin; a topic is
# chained only with at least CHAIN_MIN_S of that left, and chaining stops after MAX_CHAIN_FAILS failures in a row.
SERVICE_S, CHAIN_MIN_S, MAX_CHAIN_FAILS = 4 * 3600 - 10 * 60, 30 * 60, 3
GIN = re.compile(r'\[GIN\] (\d{4}/\d\d/\d\d - \d\d:\d\d:\d\d) \|.*POST +"/api/(?:chat|generate)"')

BRIEF = """# Research topic: {title}

You are helping test a private Star Wars Galaxies emulator server (SWGEmu Core3, pre-CU rules). Bot characters run
automated test scenarios on a test galaxy. Read the files in src/ and explain the game mechanic below, so that the
scenarios check it correctly.

Question: {question}

The files in src/ are copies of the server source{scenario_note}. Every line starts with its line number in the
original file ("  919| ..."); cite those numbers.

Write report.md with these sections:
1. Short answer (3-6 sentences).
2. How it works: conditions, skill mods and numbers, timings, and the messages the player sees. Cite file:line for
   every claim.
3. What a bot test should check: observable results (system messages, states, inventory, attributes) and the setup
   it needs first.
4. Likely reasons a test sees no effect.
5. Open questions: what these files don't answer (name the missing file or function if you can).

Rules: use only what the files show. Mark anything you infer rather than read with "(inferred)". Never invent function
names, numbers or file names. Plain English; no code excerpt longer than 3 lines.
"""


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def last_request():
    """Epoch seconds of the newest finished chat/generate request in Ollama's log (local time, as WSL's clock)."""
    try:
        with OLLAMA_LOG.open('rb') as f:
            f.seek(max(0, OLLAMA_LOG.stat().st_size - 400_000))
            tail = f.read().decode('utf-8', 'replace')
    except OSError:
        return None
    stamps = GIN.findall(tail)
    return time.mktime(time.strptime(stamps[-1], '%Y/%m/%d - %H:%M:%S')) if stamps else 0.0


def gpu_busy():
    peak = 0
    for _ in range(3):
        try:
            out = subprocess.run([NVIDIA_SMI, '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                 capture_output=True, text=True, timeout=20).stdout
            peak = max([peak] + [int(x) for x in out.split() if x.isdigit()])
        except (OSError, subprocess.SubprocessError):
            return None
        time.sleep(1)
    return peak


def owner_client():
    try:
        out = subprocess.run(['/mnt/c/WINDOWS/system32/tasklist.exe', '/FO', 'CSV', '/NH'], capture_output=True,
                             text=True, errors='replace', timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(re.search(r'(?im)^"(swgclient|swgemu)', out))


def load(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def save(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp.replace(path)


def parse_expiry(text, server_now):
    """Epoch seconds of an /api/ps expires_at, or None when it is no use: missing, unreadable, or "never" (keep-alive -1
    shows year 1 or a date centuries away), where a finished request leaves no trace."""
    found = EXPIRES.fullmatch(text or '')
    if not found or int(found.group(1)) <= 1:
        return None
    year, month, day, hour, minute, second, fraction, zone = found.groups()
    offset = timedelta() if zone == 'Z' else timedelta(hours=int(zone[1:3]), minutes=int(zone[4:6])) * (
        -1 if zone[0] == '-' else 1)
    try:
        when = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second),
                        int((fraction or '0')[:6].ljust(6, '0')), timezone(offset))
        epoch = when.timestamp()
    except (ValueError, OverflowError):
        return None
    return epoch if epoch < server_now + 30 * 86400 else None


def fetch_ps(base):
    """({loaded model: expiry epoch or None}, the server's own clock) from its /api/ps. The server's Date header is
    the clock, so a skewed clock on the other PC doesn't matter. OSError or ValueError when it isn't answering."""
    with urllib.request.urlopen(ollama_url.api('/api/ps', base), timeout=10) as response:
        data = json.load(response)
        stamp = response.headers.get('Date')
    if not isinstance(data, dict):
        raise ValueError('/api/ps did not answer with an object')
    try:
        server_now = parsedate_to_datetime(stamp).timestamp()
    except (TypeError, ValueError):
        server_now = time.time()
    return {m.get('name') or m.get('model') or '?': parse_expiry(m.get('expires_at'), server_now)
            for m in data.get('models') or []}, server_now


def remote_key(base):
    return hashlib.sha1(base.encode()).hexdigest()[:10]  # state.json holds this, not the LAN address itself


def remote_step(prev, key, models, server_now, now):
    """One look at a server on another PC. prev is the record the last look stored (or None). Returns (record, why):
    the record to store (None: start over next time) and the reasons it isn't idle yet (empty: idle).
    A request that finishes moves its model's expires_at, so a model list that stays the same between looks means
    nobody used the server in between. A model that vanishes after its expiry just timed out; one that vanishes
    early was unloaded by someone. A loaded model past its expiry is mid-request."""
    blind = sorted(n for n, e in models.items() if e is None)
    if blind:
        return None, [f'remote Ollama keeps {", ".join(blind)} loaded with no usable expiry (keep-alive -1?), '
                      'so use cannot be told']
    busy = sorted(n for n, e in models.items() if e < server_now - OVERDUE_S)
    old = prev.get('models', {}) if prev and prev.get('key') == key and 0 <= now - prev.get('seen', -1e9) <= \
        REMOTE_GAP_S else None
    changed = old is not None and (any(n not in old or abs(old[n] - e) > 0.001 for n, e in models.items())
                                   or any(n not in models and e > server_now + 2 for n, e in old.items()))
    since = prev['since'] if old is not None and not changed and not busy else now
    record = {'key': key, 'models': models, 'since': since, 'seen': now}
    if busy:
        return record, [f'remote Ollama is mid-request ({", ".join(busy)} is past its expiry)']
    covered = now - since
    if covered >= IDLE_S - REMOTE_SLACK_S:
        return record, []
    return record, [('first look at remote Ollama' if old is None else
                     'remote Ollama was used since the last look' if changed else 'remote Ollama quiet')
                    + f' ({int(covered // 60)} of {IDLE_S // 60} min so far, counted on the timer runs)']


def remote_blockers(base, record=False, now=None):
    """Reasons not to start while Ollama runs on another PC; the local log, GPU and client checks don't apply to it.
    record=True (the timer's `check`) stores this look in state.json; `status` only reads."""
    now = time.time() if now is None else now
    state = load(STATE, {})
    try:
        models, server_now = fetch_ps(base)
    except (OSError, ValueError):
        new, why = None, [f'remote Ollama at {ollama_url.describe(base)} is not answering']
    else:
        new, why = remote_step(state.get('remote'), remote_key(base), models, server_now, now)
    if record:
        if new:
            state['remote'] = new
        else:
            state.pop('remote', None)
        save(STATE, state)
    return why


def choose():
    """(server, skipped, problem): the Server this run uses (the first in ollama-url.txt that answers), the host:port of
    the ones before it that didn't answer, and instead of a server, why the settings are unusable."""
    try:
        server, skipped = ollama_url.pick()
    except ollama_url.OllamaUrlError as error:
        return None, [], f'bad Ollama address ({error})'
    except ollama_url.OllamaSettingError as error:
        return None, [], f'bad Ollama setting ({error})'
    return server, skipped, None


def remote_base(server=None):
    """The other PC's address, or None when Ollama is on this PC (or the settings are unusable: blockers() says so)."""
    server = choose()[0] if server is None else server
    return None if server is None or ollama_url.is_local(server.base) else server.base


def tags_of(base):
    """The body of the server's /api/tags answer, or None when it doesn't answer."""
    try:
        return urllib.request.urlopen(ollama_url.api('/api/tags', base), timeout=5).read()
    except OSError:
        return None


def blockers(record=False, server=None):
    """Reasons not to start now on server (default: the one choose() picks); an empty list means idle."""
    why = []
    if STOP.exists():
        why.append('Agent/local-research/STOP exists')
    if server is None:
        server, _, problem = choose()
        if problem:
            return why + [problem]
    base, model = server.base, server.model
    remote = not ollama_url.is_local(base)
    if remote:
        why += remote_blockers(base, record)
    tags = None
    if not any('not answering' in reason for reason in why):   # (a remote server that is down has said so already)
        tags = tags_of(base)
        if tags is None and not remote:
            why.append('Ollama is not answering')
    absent = ollama_url.model_missing(tags, model) if tags is not None else None   # else every topic would fail
    if absent:
        why.append(absent)
    if remote:
        return why
    last = last_request()
    own = load(STATE, {}).get('last_finish', 0)
    if last is None:
        why.append("Ollama's server.log is not readable")
    elif time.time() - last < IDLE_S and last > own + OWN_SLACK_S:
        why.append(f'Ollama was used {int(time.time() - last)} s ago (needs {IDLE_S} s idle)')
    gpu = gpu_busy()
    if gpu is None or gpu >= GPU_BUSY:
        why.append(f'GPU at {gpu} %' if gpu is not None else 'nvidia-smi failed')
    client = owner_client()
    if client is None or client:
        why.append("an owner's SWG client is running" if client else 'tasklist.exe failed')
    room = memguard.commit_headroom_gb()
    if room is not None and room < START_HEADROOM_GB:
        why.append(f'Windows commit headroom {room:.1f} GB (needs {START_HEADROOM_GB:.0f} GB)')
    return why


def source_cap(ctx):
    """Characters of source per topic for a context window of ctx tokens: SOURCE_CAP at 64K, in proportion otherwise."""
    return max(10_000, SOURCE_CAP * ctx // 65536)


def copy_sources(topic, src, cap=SOURCE_CAP):
    """Line-numbered copies of the topic's files; returns (copied, skipped) descriptions."""
    copied, skipped, total = [], [], 0
    for spec in topic.get('sources', []):
        project = spec.startswith('h:')
        rel, a, b = re.fullmatch(r'(.*?)(?::(\d+)-(\d+))?', spec[2:] if project else spec).groups()
        try:
            text = ((H if project else CORE3) / rel).read_text(encoding='utf-8', errors='replace').split('\n')
        except OSError:
            skipped.append(f'{spec} (not found)')
            continue
        first, last = (int(a), min(int(b), len(text))) if a else (1, len(text))
        body = '\n'.join(f'{n:6d}| {text[n - 1]}' for n in range(first, last + 1)) + '\n'
        if total + len(body) > cap:
            skipped.append(f'{spec} (over the {cap}-character budget)')
            continue
        total += len(body)
        out = src / (rel + (f'.lines-{first}-{last}' if a else ''))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding='utf-8')
        copied.append(f'src/{out.relative_to(src).as_posix()}')
    return copied, skipped


def run_map(topic, server, limit=RUN_LIMIT_S):
    """A chunk job: local_jobs.py prepares the input, local_map.py asks the model chunk by chunk, local_jobs.py writes
    report.md. A run paused by the owner's client or low memory leaves the topic open; it resumes where it stopped."""
    ws = BASE / topic['id']
    ws.mkdir(parents=True, exist_ok=True)
    job, started, steps, code = topic.get('job', ''), time.time(), [], 1
    base = remote_base(server)
    env = dict(os.environ, OLLAMA_URL=server.base)   # the very server this run was decided on, no second pick
    try:
        prep = subprocess.run([sys.executable, str(JOBS), 'prepare', job, str(ws)], capture_output=True, text=True,
                              errors='replace', timeout=1800)
        steps.append(prep.stdout + prep.stderr)
        if prep.returncode == 0:
            mapped = subprocess.run([sys.executable, str(MAP), '--input', str(ws / 'input.jsonl'), '--instruction',
                                     str(ws / 'instruction.txt'), '--out', str(ws), '--yield-to-owner',
                                     '--model', server.model, '--ctx', str(min(server.ctx, 16384))],
                                    capture_output=True, text=True, errors='replace', timeout=limit, env=env)
            steps.append(mapped.stdout + mapped.stderr)
            code = mapped.returncode
    except subprocess.TimeoutExpired:
        code = 3
        steps.append(f'stopped after {int(limit)} s; resumes next time')
    output = '\n'.join(s.strip() for s in steps if s.strip())
    tries = topic.get('tries', 0) + 1
    # a few chunks that fail every time shouldn't hold the report back for ever
    finished = code == 0 or (code == 3 and 'failed; rerun' in output and tries >= 3)
    if finished:
        made = subprocess.run([sys.executable, str(JOBS), 'report', job, str(ws)], capture_output=True, text=True,
                              errors='replace', timeout=600)
        output += '\n' + (made.stdout + made.stderr).strip()
        finished = made.returncode == 0
        code = 0 if finished else 1
    if base:   # map-output.txt is tracked in git; the LAN address is not
        output = output.replace(base, '<ollama-url>').replace(ollama_url.describe(base).rsplit(':', 1)[0], '<ollama-host>')
    (ws / 'map-output.txt').write_text(output + '\n', encoding='utf-8')
    status = 'review' if finished else 'open' if code == 3 else 'failed'
    minutes = round((time.time() - started) / 60)
    queue = load(QUEUE, {'topics': []})   # re-read: someone may have added topics meanwhile
    for t in queue['topics']:
        if t['id'] == topic['id']:
            t.update(status=status, minutes=t.get('minutes', 0) + minutes, tries=tries,
                     **({'finished': now()} if finished else {}))
    save(QUEUE, queue)
    state = load(STATE, {})
    if base:   # as in run(): our own use doesn't count against the idle window
        try:
            models, _ = fetch_ps(base)
            state['remote'] = {'key': remote_key(base), 'models': models, 'since': time.time() - IDLE_S,
                               'seen': time.time()} if None not in models.values() else None
        except (OSError, ValueError):
            state['remote'] = None
        if state['remote'] is None:
            state.pop('remote')
    state.update(last_finish=time.time(), last_topic=topic['id'])
    save(STATE, state)
    last = output.strip().splitlines()[-1][:160] if output.strip() else 'no output'
    with LOG.open('a', encoding='utf-8', newline='') as f:
        f.write(f'- {now()} {topic["id"]} ({job}): ' + {'review': 'report written', 'open': 'paused, resumes when idle',
                                                         'failed': 'failed'}[status] + f' ({last}), {minutes} min\n')
    return status != 'failed'


def run(topic, server=None, limit=RUN_LIMIT_S):
    """Run one topic on server (default: the one choose() picks, with the topic's own model and ctx if it names them)."""
    if server is None:
        server = with_topic(choose()[0], topic)
    if topic.get('kind') == 'map':
        return run_map(topic, server, limit)
    ws = BASE / topic['id']
    src = ws / 'src'
    shutil.rmtree(src, ignore_errors=True)
    report = ws / 'report.md'
    if report.exists() and report.stat().st_size:   # a rerun keeps the last report for comparison (17 Oct: reruns
        report.replace(ws / 'report.previous.md')   # had replaced the 15 Oct reports, which survived only in git)
    for old in ('TASK.md', 'agent-log.jsonl'):
        (ws / old).unlink(missing_ok=True)
    src.mkdir(parents=True)
    model, ctx = server.model, server.ctx   # blockers() has checked them; local_agent.py gets them as flags
    copied, skipped = copy_sources(topic, src, source_cap(ctx))
    scenario = any('/scenarios/' in c for c in copied)
    (ws / 'TASK.md').write_text(BRIEF.format(
        title=topic['title'], question=topic['question'],
        scenario_note=' and, where its path says scenarios/, of the bot test scenario' if scenario else '')
        + '\nFiles:\n' + ''.join(f'- {c}\n' for c in copied), encoding='utf-8')
    started = time.time()
    base = remote_base(server)
    env = dict(os.environ, OLLAMA_URL=server.base)   # hand local_agent.py the very address this run was decided on
    try:
        out = subprocess.run([sys.executable, str(AGENT), '--workspace', str(ws), '--max-steps', str(MAX_STEPS),
                              '--model', model, '--ctx', str(ctx), '--task', 'Read TASK.md, then the files it lists, then write report.md as TASK.md asks.'],
                             capture_output=True, text=True, errors='replace', timeout=limit, env=env)
        output = out.stdout + out.stderr
    except subprocess.TimeoutExpired:   # a chained topic that ran out of the service's time is not a failure
        output = f'stopped after {int(limit)} s' + ('' if limit >= RUN_LIMIT_S else ': the end of a chained run; starts again')
    if base:   # agent-output.txt is tracked in git; the LAN address is not
        output = output.replace(base, '<ollama-url>').replace(ollama_url.describe(base).rsplit(':', 1)[0], '<ollama-host>')
    (ws / 'agent-output.txt').write_text(output, encoding='utf-8')
    report = ws / 'report.md'
    ok = report.exists() and report.stat().st_size > 300
    minutes = round((time.time() - started) / 60)
    state = load(STATE, {})
    cut = limit < RUN_LIMIT_S and output.startswith('stopped after')   # a chained run's time ran out: not a failure
    gone = False
    if base:   # our own use doesn't count against the idle window (as with the local log); a vanished server does
        try:
            models, _ = fetch_ps(base)
            if None in models.values():
                state.pop('remote', None)
            else:
                state['remote'] = {'key': remote_key(base), 'models': models, 'since': time.time() - IDLE_S,
                                   'seen': time.time()}
        except (OSError, ValueError):
            state.pop('remote', None)
            gone = not ok
    queue = load(QUEUE, {'topics': []})   # re-read: someone may have added topics meanwhile
    for t in queue['topics']:
        if t['id'] == topic['id']:
            t.update(status='review' if ok else 'open' if gone or cut else 'failed', finished=now(), minutes=minutes,
                     skipped=skipped or None)
    save(QUEUE, queue)
    state.update(last_finish=time.time(), last_topic=topic['id'])
    save(STATE, state)
    with LOG.open('a', encoding='utf-8', newline='') as f:
        f.write(f'- {now()} {topic["id"]}: ' + (f'report written ({report.stat().st_size} bytes)' if ok else
                'no report: remote Ollama stopped answering, topic left open' if gone else
                'no report: the chained run reached its time limit, topic left open' if cut else
                f'no report ({output.strip().splitlines()[-1][:120] if output.strip() else "no output"})')
                + f', {minutes} min, {len(copied)} files' + (f'; skipped {", ".join(skipped)}' if skipped else '')
                + '\n')
    return ok


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('check', 'status'):
        print(__doc__)
        return 2
    lock = (BASE / '.lock').open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print('a topic is running')
        return 0
    queue = load(QUEUE, {'topics': []})
    if sys.argv[1] == 'check':  # holding the lock, so a "running" topic is left over from a run that died
        for t in queue['topics']:
            if t.get('status') == 'running':
                t['status'] = 'open'
        save(QUEUE, queue)
    # check --now (owner's request, 17 Oct): start the next topic without waiting for the quiet minutes; STOP still holds
    now_asked = sys.argv[1] == 'check' and '--now' in sys.argv[2:]
    started, fails, code = time.time(), 0, 0
    while True:
        # Chained topics (owner, 17 Oct: "start the next topic right after one finishes, while the friend's PC is the
        # server") get only what is left of the service's time, so the service is never killed mid-topic.
        result, remote = one_round(sys.argv[1], now_asked, min(RUN_LIMIT_S, SERVICE_S - (time.time() - started)))
        if result is None:
            return code
        code = code or (0 if result else 1)
        fails = 0 if result else fails + 1
        now_asked = False
        if not remote or fails >= MAX_CHAIN_FAILS or SERVICE_S - (time.time() - started) < CHAIN_MIN_S:
            return code


def one_round(command, now_asked, limit):
    """One look at the queue and the server; starts the next topic if it may. Returns (None if nothing started, else
    whether the topic went well; whether the server is another PC)."""
    queue = load(QUEUE, {'topics': []})
    todo = [t for t in queue['topics'] if t.get('status') == 'open']
    server, skipped, problem = choose()
    held, topic = {}, None
    if server:
        tags = None
        for t in todo:
            reason = hold_reason(t, server, tags)
            if reason == 'tags?':   # fetch the model list only when a topic names a model
                tags = tags_of(server.base) or b''
                reason = hold_reason(t, server, tags)
            if reason:
                held[t['id']] = reason
            elif topic is None:
                topic = t
        if topic:
            server = with_topic(server, topic)
    why = ([] if not STOP.exists() else ['Agent/local-research/STOP exists']) + [problem] if problem else \
        (['Agent/local-research/STOP exists'] if STOP.exists() else []) if now_asked else \
        blockers(record=command == 'check', server=server)
    remote = remote_base(server) if server else None
    where = ', '.join(skipped) + ' not answering, so ' if skipped else ''
    print((f'[{where}remote Ollama {ollama_url.describe(remote)}] ' if remote else
           f'[{where}this PC] ' if skipped else '')
          + f'{len(todo)} open topic(s)' + (f', {len(held)} held ({"; ".join(f"{k}: {v}" for k, v in held.items())})'
                                            if held else '') + '; '
          + ('idle: would start ' + topic['id'] if not why and topic else
             'not starting: ' + ('; '.join(why) if why else 'queue empty' if not todo else 'every open topic is held')))
    if command == 'status' or why or not topic:
        return None, bool(remote)
    for t in queue['topics']:
        if t['id'] == topic['id']:
            t.update(status='running', started=now())
    save(QUEUE, queue)
    return run(topic, server, limit), bool(remote)


def with_topic(server, topic):
    """server with the topic's own "model" and "ctx" (context size in tokens), where it names them."""
    return server._replace(model=ollama_url.parse_model(topic['model']) if topic.get('model') else server.model,
                           ctx=ollama_url.parse_ctx(topic['ctx']) if topic.get('ctx') else server.ctx)


def hold_reason(topic, server, tags):
    """Why topic can't run on server now (None: it can). 'tags?' asks the caller for the server's model list."""
    if topic.get('local_only') and not ollama_url.is_local(server.base):
        return 'local_only, waits for this PC'
    if topic.get('ctx'):
        try:
            ollama_url.parse_ctx(topic['ctx'])
        except ollama_url.OllamaSettingError as error:
            return f'bad ctx ({error})'
    name = topic.get('model')
    if not name:
        return None
    try:
        ollama_url.parse_model(name)
    except ollama_url.OllamaSettingError as error:
        return f'bad model ({error})'
    if tags is None:
        return 'tags?'
    return f'needs {name}, not on this server' if ollama_url.model_missing(tags, name) else None


if __name__ == '__main__':
    sys.exit(main())
