#!/usr/bin/env python3
"""A read-only snapshot of the test server and the bots, for ChatGPT (Codex can't run WSL commands).

Run inside Debian as root:   python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/live_status.py
Writes outputs/Agent/live/status.md (and status.json), replacing the previous copy. Nothing else is changed:
  - processes and memory: proc_check_wsl.py without --clean (it only reads /proc);
  - bots: one `status` line per bot through squad.py, as swgemu, but ONLY when no squad run is active, so it never
    sends a command to a bot another run is driving (one driver at a time); during a run, the run's activity
    records instead;
  - the test galaxy's console: the last lines, with anything that looks like a secret dropped.
Scheduled every 5 minutes by the WSL timer swg-live-status.timer (owner's OK, 14 Oct 2026). To stop it:
    systemctl disable --now swg-live-status.timer      (as root in Debian)
"""
import json, re, subprocess, sys, time
from datetime import datetime
from pathlib import Path

OUTPUTS = Path(__file__).resolve().parents[1]
LIVE = OUTPUTS / 'Agent' / 'live'
TOOLS = OUTPUTS / 'tools'
CONSOLE = Path('/opt/swg/testgalaxy/console.log')
ACTIVE = OUTPUTS / 'Bot-reports' / 'runs' / 'ACTIVE'
SECRET = re.compile(r'pass(word)?|secret|token|hash|salt|key=|credential', re.I)


def run(args, timeout=60, user=None):
    if user:
        args = ['runuser', '-u', user, '--'] + args
    try:
        done = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return (done.stdout or '') + (done.stderr or '')
    except (OSError, subprocess.TimeoutExpired) as error:
        return f'(failed: {error})'


def squad_run_active():
    try:
        pid = int(ACTIVE.read_text().split()[0])
        return Path(f'/proc/{pid}').exists()
    except (OSError, ValueError, IndexError):
        return False


def console_tail(lines=40):
    if not CONSOLE.exists():
        return ['(the test galaxy is not running)']
    text = CONSOLE.read_bytes()[-20000:].decode(errors='replace').replace('\0', '')
    return [l for l in text.splitlines() if l.strip() and not SECRET.search(l)][-lines:]


def main():
    started = time.time()
    procs = run([sys.executable, str(TOOLS / 'proc_check_wsl.py')])
    try:
        procs_json = json.loads(procs)
    except ValueError:
        procs_json = {'raw': procs[-2000:]}
    busy = squad_run_active()
    squad = ['python3', str(TOOLS / 'bots' / 'squad.py')]
    bots = run(squad + ['activity'], user='swgemu') if busy else run(squad + ['status'], timeout=120, user='swgemu')
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tail = console_tail()
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / 'status.json').write_text(json.dumps({'written': stamp, 'squad_run_active': busy, 'processes': procs_json,
                                                  'bots': bots, 'console_tail': tail}, indent=1) + '\n', encoding='utf-8')
    md = [f'# Live status, {stamp}', '',
          f'Written by `tools/live_status.py` in {time.time() - started:.0f} s. Read-only snapshot; it can be minutes old.', '',
          '## Bots', '', ('A squad run is active, so these are its activity records (no bot was queried):' if busy
                          else 'No squad run active; one status line per bot:'), '', '```', bots.strip(), '```', '',
          '## Processes and memory', '', '```', json.dumps(procs_json, indent=1)[:4000], '```', '',
          '## Test galaxy console (last lines)', '', '```', *tail, '```', '']
    (LIVE / 'status.md').write_text('\n'.join(md), encoding='utf-8')
    print(f'wrote {LIVE / "status.md"}')


if __name__ == '__main__':
    main()
