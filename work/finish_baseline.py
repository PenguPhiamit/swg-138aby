from pathlib import Path
import json, os, re, subprocess, sys, time
sys.path.insert(0,'/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools')
from backup_server import backup, capture

os.umask(0o077)
binpath = Path('/opt/swg/Core3/MMOCoreORB/bin')
outputs = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')

def maintenance(snapshot):
    config = binpath/'conf/config-local.lua'
    content = config.read_text()
    if re.search(r'^Core3\.MantisHost\s*=', content, re.M):
        content = re.sub(r'^Core3\.MantisHost\s*=.*$', 'Core3.MantisHost = ""',content,flags=re.M)
    else:
        content += '\n-- Private local server: no separate Mantis bug-tracker database.\nCore3.MantisHost = ""\n'
    config.write_text(content)
    config.chmod(0o600)
    (snapshot/'maintenance-change.txt').write_text('After this snapshot: disabled optional Mantis integration with Core3.MantisHost = "". Gameplay, zones, JTL and account permissions were unchanged.\n')
    print('Disabled the unused Mantis database connection.',flush=True)

snapshot = backup('baseline-before-maintenance', maintenance)
print('Checking galaxy startup...',flush=True)
since = capture(['systemctl','show','swg-local','-p','ActiveEnterTimestamp','--value'])
deadline = time.monotonic()+180
ready = False
while time.monotonic()<deadline:
    logs = capture(['journalctl','-u','swg-local','--since',since,'--no-pager','-o','cat'])
    if '[Core] initialized' in logs:
        ready = True
        break
    if subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode:
        raise RuntimeError('The galaxy stopped during startup; inspect the service log.')
    time.sleep(2)
if not ready:
    raise RuntimeError('The galaxy did not confirm initialization within three minutes.')
ports = capture(['ss','-lunp'])
expected_ports = all(':'+str(port) in ports for port in (44453,44462,44463))
if not expected_ports:
    raise RuntimeError('The expected game ports are not all listening.')
checks = {
    'backup_linux_path':str(snapshot),
    'backup_windows_path':str(outputs/'Backups'/snapshot.name),
    'server_initialized':ready,
    'expected_game_ports_listening':expected_ports,
    'mantis_access_error_after_restart':'Access denied for user' in logs or 'MantisDatabase' in logs,
    'debugger':capture(['gdb','--version']).splitlines()[0],
    'schema':capture(['mariadb','-Nse','SELECT * FROM swgemu.db_metadata']),
    'accounts_and_characters':capture(['mariadb','-Nse','SELECT count(*) FROM swgemu.accounts; SELECT count(*) FROM swgemu.characters;']),
    'server_revision':capture(['runuser','-u','swgemu','--','git','-C','/opt/swg/Core3','rev-parse','HEAD']),
}
(outputs/'SWG-baseline-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2),flush=True)
