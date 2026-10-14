"""Recompile the live galaxy after C++/IDL changes (the galaxy must be stopped).

Inside Debian, as root:  python3 rebuild_server.py [-jN]
Lua-only changes need no rebuild; check them with check_lua.py and restart.
"""
from pathlib import Path
import hashlib, os, subprocess, sys

CORE = Path('/opt/swg/Core3/MMOCoreORB')
LOG = Path('/opt/swg/rebuild.log')
TOOLS = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

if subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0 or \
        subprocess.run(['pgrep','-x','core3'], stdout=subprocess.DEVNULL).returncode == 0:
    raise SystemExit('Stop the galaxy first (Stop SWG Server.cmd); the build replaces its executable.')

jobs = next((a for a in sys.argv[1:] if a.startswith('-j')), '-j6')
if subprocess.run(['python3', str(TOOLS/'check_lua.py'), '--since', 'upstream-base']).returncode:
    raise SystemExit('Fix the Lua syntax errors above before rebuilding.')

before = digest(CORE/'bin/core3')
env = dict(os.environ, PATH='/usr/lib/llvm-19/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
print(f'Compiling the live server ({jobs}). Progress: {LOG}', flush=True)
with LOG.open('w') as log:
    result = subprocess.run(['runuser','-u','swgemu','--','cmake','--build',str(CORE/'build/local'),jobs],
                            stdout=log, stderr=subprocess.STDOUT, env=env)
if result.returncode:
    print('\n'.join(LOG.read_text(errors='replace').splitlines()[-35:]))
    raise SystemExit('Build FAILED; the previous executable is still in place.')
after = digest(CORE/'bin/core3')
print(f'Build succeeded. Executable {"updated" if after != before else "unchanged (nothing to rebuild)"}.')
print(f'core3 sha256: {after}')
print('Start the galaxy with Start SWG Server.cmd and check Server Status.cmd.')
