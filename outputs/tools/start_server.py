from pathlib import Path
from datetime import datetime, timezone
import subprocess, socket, time

OUTPUTS = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
MAINTENANCE = Path('/run/swg-local-maintenance')

def active():
    return subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0

with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
    s.connect(('192.0.2.1',80))
    address=s.getsockname()[0]
subprocess.run(['systemctl','start','mariadb'],check=True)
subprocess.run(['mariadb'],input=f"UPDATE swgemu.galaxy SET address='{address}' WHERE galaxy_id=2;",text=True,check=True)
client=OUTPUTS/'SWG-client/swgemu_login.cfg'
client.write_text(f'[ClientGame]\nloginServerPort0=44453\nloginServerAddress0={address}\n')

already_running = active()
# Stream the server console into this window. Start following before the service
# starts so no startup lines are missed; show recent history if it is already up.
console = subprocess.Popen(['journalctl','-u','swg-local','-f','-o','cat',
                            '-n','40' if already_running else '0'])
if already_running:
    print('The galaxy was already running; showing its live console.', flush=True)
else:
    subprocess.run(['systemctl','start','swg-local'],check=True)
    print('Galaxy starting at '+address+'. Loading takes about a minute; wait for "[Core] initialized".', flush=True)
print('KEEP THIS WINDOW OPEN while playing. Use Stop SWG Server.cmd to shut down.', flush=True)
stamps = [p.name.rsplit('-',1)[-1] for p in (OUTPUTS/'Backups').glob('*-20*Z')]
if stamps:
    newest = datetime.strptime(max(stamps), '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - newest).days
    if days >= 7:
        print(f'REMINDER: the newest backup is {days} days old. Run Back Up SWG Galaxy.cmd soon.', flush=True)

# A live Windows-to-WSL command keeps the distro running while the galaxy is up.
try:
    while active() or MAINTENANCE.exists():
        time.sleep(5)
finally:
    console.terminate()
print('The galaxy has stopped.', flush=True)
