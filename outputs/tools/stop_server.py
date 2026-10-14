import subprocess

def active():
    return subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0

if not active():
    print('The galaxy is already stopped.')
    raise SystemExit(0)

print('Saving the world and shutting down. This can take a minute or two...', flush=True)
console = subprocess.Popen(['journalctl','-u','swg-local','-f','-o','cat','-n','0'])
try:
    result = subprocess.run(['systemctl','stop','swg-local'])
finally:
    console.terminate()
outcome = subprocess.run(['systemctl','show','swg-local','-p','Result','--value'],
                         capture_output=True, text=True).stdout.strip()
if result.returncode == 0 and not active() and outcome == 'success':
    print('\nGalaxy stopped cleanly. It is now safe to reboot.')
else:
    print(f'\nThe stop did not finish cleanly (result: {outcome or "unknown"}). '
          'Run Server Status.cmd and check the log before rebooting.')
    raise SystemExit(1)
