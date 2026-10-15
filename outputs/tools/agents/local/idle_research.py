"""Idle research for the owner's local model (Claude, 15 Oct 2026). Owner: "when ollama goes idle for more than 10 mins,
start researching game mechanics (taking over for gpt) that will help our testing".

Inside Debian as swgemu; swg-idle-research.timer runs `check` every 5 minutes:

    python3 idle_research.py check     # start the next open topic if the model has been idle 10+ minutes
    python3 idle_research.py status    # say why it would or wouldn't start now

Idle means all of: no /api/chat or /api/generate request in Ollama's log for 10 minutes (this runner's own last topic
doesn't count, so topics follow each other while nobody else needs the model); the GPU below 30 %; none of the owner's
SWG clients running; no Agent/local-research/STOP file.

Each topic in Agent/local-research/queue.json names Core3-dev sources (MMOCoreORB-relative, with an optional
:START-END line range) and project files (prefix h:). They are copied, read-only and line-numbered, into
Agent/local-research/<id>/src/, and local_agent.py (file tools inside that folder only: no shell, no network) writes
<id>/report.md. Reports are notes: Claude or ChatGPT checks them against the source before a test relies on them.
Nothing here touches the server, the bots or the board. Anyone may add an "open" topic to the queue.
"""
import fcntl
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

H = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
BASE = H / 'outputs' / 'Agent' / 'local-research'
QUEUE, LOG, STATE, STOP = BASE / 'queue.json', BASE / 'LOG.md', BASE / 'state.json', BASE / 'STOP'
CORE3 = Path('/opt/swg/Core3-dev/MMOCoreORB')
AGENT = H / 'outputs' / 'tools' / 'agents' / 'local' / 'local_agent.py'
OLLAMA_LOG = Path('/mnt/c/Users/Pengw/AppData/Local/Ollama/server.log')
OLLAMA = 'http://127.0.0.1:11434/api/tags'
NVIDIA_SMI = '/usr/lib/wsl/lib/nvidia-smi'  # WSL's GPU tools; not on a systemd service's PATH
IDLE_S, OWN_SLACK_S, GPU_BUSY = 600, 90, 30
SOURCE_CAP = 120_000  # characters per topic: the brief, the files and the agent's notes share a 64K-token window
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


def blockers():
    """Reasons not to start now; an empty list means idle."""
    why = []
    if STOP.exists():
        why.append('Agent/local-research/STOP exists')
    try:
        urllib.request.urlopen(OLLAMA, timeout=5).read()
    except OSError:
        why.append('Ollama is not answering')
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
    return why


def copy_sources(topic, src):
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
        if total + len(body) > SOURCE_CAP:
            skipped.append(f'{spec} (over the {SOURCE_CAP}-character budget)')
            continue
        total += len(body)
        out = src / (rel + (f'.lines-{first}-{last}' if a else ''))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding='utf-8')
        copied.append(f'src/{out.relative_to(src).as_posix()}')
    return copied, skipped


def run(topic):
    ws = BASE / topic['id']
    src = ws / 'src'
    shutil.rmtree(src, ignore_errors=True)
    for old in ('report.md', 'TASK.md', 'agent-log.jsonl'):
        (ws / old).unlink(missing_ok=True)
    src.mkdir(parents=True)
    copied, skipped = copy_sources(topic, src)
    scenario = any('/scenarios/' in c for c in copied)
    (ws / 'TASK.md').write_text(BRIEF.format(
        title=topic['title'], question=topic['question'],
        scenario_note=' and, where its path says scenarios/, of the bot test scenario' if scenario else '')
        + '\nFiles:\n' + ''.join(f'- {c}\n' for c in copied), encoding='utf-8')
    started = time.time()
    try:
        out = subprocess.run([sys.executable, str(AGENT), '--workspace', str(ws), '--max-steps', str(MAX_STEPS),
                              '--task', 'Read TASK.md, then the files it lists, then write report.md as TASK.md asks.'],
                             capture_output=True, text=True, errors='replace', timeout=RUN_LIMIT_S)
        output = out.stdout + out.stderr
    except subprocess.TimeoutExpired:
        output = f'stopped after {RUN_LIMIT_S} s'
    (ws / 'agent-output.txt').write_text(output, encoding='utf-8')
    report = ws / 'report.md'
    ok = report.exists() and report.stat().st_size > 300
    minutes = round((time.time() - started) / 60)
    queue = load(QUEUE, {'topics': []})   # re-read: someone may have added topics meanwhile
    for t in queue['topics']:
        if t['id'] == topic['id']:
            t.update(status='review' if ok else 'failed', finished=now(), minutes=minutes,
                     skipped=skipped or None)
    save(QUEUE, queue)
    save(STATE, {'last_finish': time.time(), 'last_topic': topic['id']})
    with LOG.open('a', encoding='utf-8', newline='') as f:
        f.write(f'- {now()} {topic["id"]}: ' + (f'report written ({report.stat().st_size} bytes)' if ok else
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
    why = blockers()
    print(f'{len(todo)} open topic(s); ' + ('idle: would start ' + todo[0]['id'] if not why and todo else
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
