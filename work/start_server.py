from pathlib import Path
import subprocess, socket, time
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
    s.connect(('192.0.2.1',80))
    address=s.getsockname()[0]
subprocess.run(['systemctl','start','mariadb'],check=True)
subprocess.run(['mariadb'],input=f"UPDATE swgemu.galaxy SET address='{address}' WHERE galaxy_id=2;",text=True,check=True)
client=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client/swgemu_login.cfg')
client.write_text(f'[ClientGame]\nloginServerPort0=44453\nloginServerAddress0={address}\n')
subprocess.run(['systemctl','start','swg-local'],check=True)
print('Galaxy starting at '+address+'. First startup may take several minutes.')
print('Keep this server window open while playing.', flush=True)
while subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0 or Path('/run/swg-local-maintenance').exists():
    time.sleep(10)
