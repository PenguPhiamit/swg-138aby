import subprocess
import time

print('Waiting for existing squad run to finish', flush=True)
while subprocess.run(['wsl', '-d', 'Debian', '-u', 'swgemu', '--',
                      'pgrep', '-f', '[s]quad.py run'], capture_output=True).returncode == 0:
    time.sleep(15)
print('SQUAD IDLE', flush=True)
