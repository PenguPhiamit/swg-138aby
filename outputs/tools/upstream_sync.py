"""Check for, and optionally apply, new official SWGEmu Core3 work.

Inside Debian, as root:
  python3 upstream_sync.py           # fetch and list new upstream commits (changes nothing)
  python3 upstream_sync.py apply     # replay our sandbox commits on top of new upstream

apply needs: galaxy stopped, no uncommitted files, a backup from the last 2 hours.
It tags the old state as pre-sync-<date> first and aborts cleanly on conflicts.
Afterwards run rebuild_server.py, then start the galaxy and test.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, sys, urllib.request

SERVER = Path('/opt/swg/Core3')
BACKUPS = Path('/opt/swg/backups')
WATCH = ('shutdown', 'hang', 'save', 'crash', 'tutorial')

def git(*args, check=True):
    result = subprocess.run(['runuser','-u','swgemu','--','git','-C',str(SERVER),*args],
                            capture_output=True, text=True)
    if check and result.returncode:
        raise SystemExit(result.stderr.strip() or f'git {" ".join(args)} failed')
    return result

def gerrit_open():
    try:
        with urllib.request.urlopen('https://review.swgemu.com/changes/?q=status:open+project:Core3&n=50',
                                    timeout=20) as response:
            return json.loads(response.read().decode()[4:])
    except (OSError, ValueError):
        return None

print('Fetching official Core3 (unstable)...', flush=True)
git('fetch', '--quiet', 'origin')
new = git('log', '--format=%h %ad %s', '--date=short', 'upstream-base..origin/unstable').stdout.strip()
ours = git('rev-list', '--count', 'origin/unstable..sandbox').stdout.strip()
print(f'Local sandbox commits: {ours}')
print(f'New upstream commits since our base: {len(new.splitlines()) if new else 0}')
if new:
    print(new)
changes = gerrit_open()
if changes is not None:
    flagged = [c for c in changes if any(w in c['subject'].lower() for w in WATCH)]
    print(f'\nOpen Gerrit changes: {len(changes)}; worth watching:')
    for change in flagged:
        print(f"  {change['updated'][:10]}  {change['subject']}")

if sys.argv[1:2] != ['apply']:
    if new:
        print('\nTo adopt them: back up, stop the galaxy, then run: upstream_sync.py apply')
    raise SystemExit(0)

if not new:
    raise SystemExit('Nothing to apply.')
if subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0:
    raise SystemExit('Stop the galaxy first.')
if git('status', '--porcelain', '--untracked-files=no').stdout.strip():
    raise SystemExit('Commit or stash uncommitted changes first.')
if git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip() != 'sandbox':
    raise SystemExit('Switch to the sandbox branch first.')
newest = max((p for p in BACKUPS.iterdir() if (p/'manifest.json').exists()),
             key=lambda p: p.name.rsplit('-', 1)[-1])
age = datetime.now(timezone.utc) - datetime.strptime(newest.name.rsplit('-', 1)[-1],
                                                     '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
if age.total_seconds() > 7200:
    raise SystemExit('Make a fresh backup first (Back Up SWG Galaxy.cmd).')

stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')
git('tag', f'pre-sync-{stamp}', 'sandbox')
result = git('rebase', '--onto', 'origin/unstable', 'upstream-base', 'sandbox', check=False)
if result.returncode:
    git('rebase', '--abort', check=False)
    print(result.stdout[-2000:], result.stderr[-2000:])
    raise SystemExit(f'Conflicts: rebase aborted, nothing changed (old state tagged pre-sync-{stamp}).')
git('submodule', 'update', '--init', '--recursive')
git('tag', '-f', 'upstream-base', 'origin/unstable')
print(f'Sandbox now sits on the new upstream. Old state: tag pre-sync-{stamp}.')
print('Next: rebuild_server.py, start the galaxy, run Server Status.cmd and test in-game.')
