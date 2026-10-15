"""Idle research for the owner's local model (Claude, 15 Oct 2026). Owner: "when ollama goes idle for more than 10 mins,
start researching game mechanics (taking over for gpt) that will help our testing".

Inside Debian as swgemu; swg-idle-research.timer runs `check` every 5 minutes:

    python3 idle_research.py check     # start the next open topic if the model has been idle 10+ minutes
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


def remote_base():
    """The other PC's address, or None when Ollama is on this PC (or the address is unusable: blockers() says so)."""
    try:
        base = ollama_url.base_url()
    except ollama_url.OllamaUrlError:
        return None
    return None if ollama_url.is_local(base) else base


def blockers(record=False):
    """Reasons not to start now; an empty list means idle."""
    why = []
    if STOP.exists():
        why.append('Agent/local-research/STOP exists')
    try:
        base = ollama_url.base_url()
    except ollama_url.OllamaUrlError as error:
        return why + [f'bad Ollama address ({error})']
    try:
        model, _ = ollama_url.model(), ollama_url.ctx()
    except ollama_url.OllamaSettingError as error:
        return why + [f'bad Ollama setting ({error})']
    remote = not ollama_url.is_local(base)
    if remote:
        why += remote_blockers(base, record)
    tags = None
    if not any('not answering' in reason for reason in why):   # (a remote server that is down has said so already)
        try:
            tags = urllib.request.urlopen(ollama_url.api('/api/tags', base), timeout=5).read()
        except OSError:
            if not remote:
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


def run_map(topic):
    """A chunk job: local_jobs.py prepares the input, local_map.py asks the model chunk by chunk, local_jobs.py writes
    report.md. A run paused by the owner's client or low memory leaves the topic open; it resumes where it stopped."""
    ws = BASE / topic['id']
    ws.mkdir(parents=True, exist_ok=True)
    job, started, steps, code = topic.get('job', ''), time.time(), [], 1
    base = remote_base()
    env = dict(os.environ, OLLAMA_URL=base) if base else None
    try:
        prep = subprocess.run([sys.executable, str(JOBS), 'prepare', job, str(ws)], capture_output=True, text=True,
                              errors='replace', timeout=1800)
        steps.append(prep.stdout + prep.stderr)
        if prep.returncode == 0:
            mapped = subprocess.run([sys.executable, str(MAP), '--input', str(ws / 'input.jsonl'), '--instruction',
                                     str(ws / 'instruction.txt'), '--out', str(ws), '--yield-to-owner'],
                                    capture_output=True, text=True, errors='replace', timeout=RUN_LIMIT_S, env=env)
            steps.append(mapped.stdout + mapped.stderr)
            code = mapped.returncode
    except subprocess.TimeoutExpired:
        code = 3
        steps.append(f'stopped after {RUN_LIMIT_S} s; resumes next time')
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


def run(topic):
    if topic.get('kind') == 'map':
        return run_map(topic)
    ws = BASE / topic['id']
    src = ws / 'src'
    shutil.rmtree(src, ignore_errors=True)
    for old in ('report.md', 'TASK.md', 'agent-log.jsonl'):
        (ws / old).unlink(missing_ok=True)
    src.mkdir(parents=True)
    model, ctx = ollama_url.model(), ollama_url.ctx()   # blockers() has checked them; local_agent.py gets them as flags
    copied, skipped = copy_sources(topic, src, source_cap(ctx))
    scenario = any('/scenarios/' in c for c in copied)
    (ws / 'TASK.md').write_text(BRIEF.format(
        title=topic['title'], question=topic['question'],
        scenario_note=' and, where its path says scenarios/, of the bot test scenario' if scenario else '')
        + '\nFiles:\n' + ''.join(f'- {c}\n' for c in copied), encoding='utf-8')
    started = time.time()
    base = remote_base()   # a server on another PC: hand local_agent.py the very address this run was decided on
    env = dict(os.environ, OLLAMA_URL=base) if base else None
    try:
        out = subprocess.run([sys.executable, str(AGENT), '--workspace', str(ws), '--max-steps', str(MAX_STEPS),
                              '--model', model, '--ctx', str(ctx), '--task', 'Read TASK.md, then the files it lists, then write report.md as TASK.md asks.'],
                             capture_output=True, text=True, errors='replace', timeout=RUN_LIMIT_S, env=env)
        output = out.stdout + out.stderr
    except subprocess.TimeoutExpired:
        output = f'stopped after {RUN_LIMIT_S} s'
    if base:   # agent-output.txt is tracked in git; the LAN address is not
        output = output.replace(base, '<ollama-url>').replace(ollama_url.describe(base).rsplit(':', 1)[0], '<ollama-host>')
    (ws / 'agent-output.txt').write_text(output, encoding='utf-8')
    report = ws / 'report.md'
    ok = report.exists() and report.stat().st_size > 300
    minutes = round((time.time() - started) / 60)
    state = load(STATE, {})
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
            t.update(status='review' if ok else 'open' if gone else 'failed', finished=now(), minutes=minutes,
                     skipped=skipped or None)
    save(QUEUE, queue)
    state.update(last_finish=time.time(), last_topic=topic['id'])
    save(STATE, state)
    with LOG.open('a', encoding='utf-8', newline='') as f:
        f.write(f'- {now()} {topic["id"]}: ' + (f'report written ({report.stat().st_size} bytes)' if ok else
                'no report: remote Ollama stopped answering, topic left open' if gone else
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
    todo = [t for t in queue['topics'] if t.get('status') == 'open']
    why = blockers(record=sys.argv[1] == 'check')
    remote = remote_base()
    print((f'[remote Ollama {ollama_url.describe(remote)}] ' if remote else '')
          + f'{len(todo)} open topic(s); ' + ('idle: would start ' + todo[0]['id'] if not why and todo else
                                              'not starting: ' + ('; '.join(why) if why else 'queue empty')))
    if sys.argv[1] == 'status' or why or not todo:
        return 0
    topic = todo[0]
    for t in queue['topics']:
        if t['id'] == topic['id']:
            t.update(status='running', started=now())
    save(QUEUE, queue)
    return 0 if run(topic) else 1


if __name__ == '__main__':
    sys.exit(main())
