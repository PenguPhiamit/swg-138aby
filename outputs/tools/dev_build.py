"""Build a separate Debug copy of the server (plus core3client) without touching the live galaxy.

The live checkout's build copies core3 into its own bin/ and generates code into its own
src/autogen, so a second build directory there would overwrite the live executable.
This uses a separate git worktree instead:

  /opt/swg/Core3-dev   branch `dev` (starts from `sandbox`), own engine3 copy,
                       build dir MMOCoreORB/build/dev (Debug, ENABLE_BUILD_CLIENT=ON)

Inside Debian, as root:  python3 dev_build.py [-jN]
Merge finished dev work back with: git -C /opt/swg/Core3 merge dev   (as swgemu, on sandbox)
"""
from pathlib import Path
import os, subprocess, sys

LIVE = Path('/opt/swg/Core3')
DEV = Path('/opt/swg/Core3-dev')
ENGINE = 'MMOCoreORB/utils/engine3'
BUILD = DEV/'MMOCoreORB/build/dev'
LOG = Path('/opt/swg/dev-build.log')
ENV = dict(os.environ, PATH='/usr/lib/llvm-19/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')

def swgemu(*args, **kwargs):
    return subprocess.run(['runuser','-u','swgemu','--',*args], check=True, env=ENV, **kwargs)

jobs = next((a for a in sys.argv[1:] if a.startswith('-j')), '-j8')

if not (DEV/'.git').exists():
    print('Creating the dev worktree (branch dev from sandbox)...', flush=True)
    DEV.mkdir(exist_ok=True)
    subprocess.run(['chown','swgemu:swgemu',str(DEV)], check=True)
    has_dev = subprocess.run(['runuser','-u','swgemu','--','git','-C',str(LIVE),'rev-parse','-q',
                              '--verify','refs/heads/dev'], stdout=subprocess.DEVNULL).returncode == 0
    if has_dev:
        swgemu('git','-C',str(LIVE),'worktree','add',str(DEV),'dev')
    else:
        swgemu('git','-C',str(LIVE),'worktree','add','-b','dev',str(DEV),'sandbox')
if not (DEV/ENGINE/'.git').exists():
    # A standalone local clone of engine3 at the pinned commit, so the two checkouts never
    # share submodule state and no network access is needed.
    pinned = swgemu('git','-C',str(DEV),'rev-parse',f'HEAD:{ENGINE}',capture_output=True,text=True).stdout.strip()
    swgemu('git','clone','--quiet','--no-checkout',str(LIVE/ENGINE),str(DEV/ENGINE))
    swgemu('git','-C',str(DEV/ENGINE),'checkout','--quiet',pinned)

if not (BUILD/'CMakeCache.txt').exists():
    print('Configuring the Debug build...', flush=True)
    swgemu('cmake','-S',str(DEV/'MMOCoreORB'),'-B',str(BUILD),'-G','Ninja',
           '-DCMAKE_BUILD_TYPE=Debug','-DENABLE_BUILD_CLIENT=ON','-DENABLE_ERROR_ON_WARNINGS=OFF',
           '-DCMAKE_C_COMPILER=/usr/lib/llvm-19/bin/clang','-DCMAKE_CXX_COMPILER=/usr/lib/llvm-19/bin/clang++',
           stdout=subprocess.DEVNULL)

print(f'Building Debug core3 + core3client ({jobs}). Progress: {LOG}', flush=True)
with LOG.open('w') as log:
    result = subprocess.run(['runuser','-u','swgemu','--','cmake','--build',str(BUILD),jobs],
                            stdout=log, stderr=subprocess.STDOUT, env=ENV)
if result.returncode:
    print('\n'.join(LOG.read_text(errors='replace').splitlines()[-40:]))
    raise SystemExit('Dev build FAILED (live galaxy unaffected).')
for name in ('src/core3', 'src/client/core3client'):
    path = BUILD/name
    print(f'{name}: {"built" if path.exists() else "MISSING"}')
print('Dev build finished. The live executable was not touched.')
