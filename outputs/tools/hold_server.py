from pathlib import Path
import subprocess, time

# A live Windows-to-WSL command keeps the distro available during maintenance.
while Path('/run/swg-local-maintenance').exists() or subprocess.run(
    ['systemctl','is-active','--quiet','swg-local']
).returncode == 0:
    time.sleep(5)
