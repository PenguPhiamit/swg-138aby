"""Syntax-check server Lua before a restart.

Default: files that are modified or untracked in /opt/swg/Core3 (work in progress).
--since REF: every Lua file changed since REF, e.g. --since upstream-base.
--all: every Lua file under MMOCoreORB/bin/scripts.

Run inside Debian:  python3 .../outputs/tools/check_lua.py [--since REF | --all]
"""
from pathlib import Path
import subprocess, sys

SERVER = Path('/opt/swg/Core3')
SCRIPTS = 'MMOCoreORB/bin/scripts'

def git(*args):
    return subprocess.run(['runuser','-u','swgemu','--','git','-C',str(SERVER),*args],
                          capture_output=True, text=True, check=True).stdout

def luac(paths):
    return subprocess.run(['luac5.3','-p','--',*paths], capture_output=True, text=True)

args = sys.argv[1:]
if args[:1] == ['--all']:
    files = [str(p.relative_to(SERVER)) for p in (SERVER/SCRIPTS).rglob('*.lua')]
elif args[:1] == ['--since'] and len(args) == 2:
    files = git('diff','--name-only','--diff-filter=d',args[1],'--').splitlines()
    files += git('ls-files','--others','--exclude-standard').splitlines()
else:
    files = git('diff','--name-only','--diff-filter=d','HEAD','--').splitlines()
    files += git('ls-files','--others','--exclude-standard').splitlines()

files = sorted({f for f in files if f.endswith('.lua') and (SERVER/f).is_file()})
if not files:
    print('No Lua files to check.')
    raise SystemExit(0)

failures = []
for start in range(0, len(files), 400):
    batch = [str(SERVER/f) for f in files[start:start+400]]
    if luac(batch).returncode != 0:
        # luac stops at the first error; recheck one by one to report them all.
        for path in batch:
            result = luac([path])
            if result.returncode != 0:
                failures.append(result.stderr.strip())

print(f'Checked {len(files)} Lua file(s): {len(failures)} with syntax errors.')
for failure in failures:
    print('  ' + failure)
raise SystemExit(1 if failures else 0)
