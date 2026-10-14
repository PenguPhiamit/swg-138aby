from pathlib import Path
import os, subprocess

Path('/run/swg-local-maintenance').touch()
subprocess.run(['systemctl','stop','swg-local'],check=True)
if subprocess.run(['pgrep','-x','core3'],stdout=subprocess.DEVNULL).returncode==0:
    raise SystemExit('Game still running; refusing to replace its executable.')
env=dict(os.environ)
env['PATH']='/usr/lib/llvm-19/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
print('Compiling the sandbox server. Build progress is recorded in /opt/swg/sandbox-build.log.',flush=True)
with open('/opt/swg/sandbox-build.log','w') as log:
    result=subprocess.run(['runuser','-u','swgemu','--','cmake','--build','/opt/swg/Core3/MMOCoreORB/build/local','-j6'],stdout=log,stderr=subprocess.STDOUT,env=env)
if result.returncode:
    print('\n'.join(Path('/opt/swg/sandbox-build.log').read_text(errors='replace').splitlines()[-35:]),flush=True)
    raise SystemExit(result.returncode)
print('Sandbox server compiled successfully. Content installation can now finish before startup.',flush=True)
