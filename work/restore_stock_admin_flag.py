from pathlib import Path
import json, subprocess, time

repo = Path('/opt/swg/Core3')
path = repo/'MMOCoreORB/bin/scripts/staff/levels/admin.lua'
original = subprocess.check_output(['runuser','-u','swgemu','--','git','-C',str(repo),'show','HEAD:MMOCoreORB/bin/scripts/staff/levels/admin.lua'])
current = path.read_bytes()
expected = original.replace(b'flag = 0,', b'flag = 2, -- Developer flag enables owner commands in the client', 1)
if current not in (original,expected):
    raise SystemExit('Unexpected admin-role changes: left the source intact.')
outputs = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
checks = json.loads((outputs/'SWG-baseline-checks.json').read_text())
snapshot = Path(checks['backup_linux_path'])
if not (snapshot/'manifest.json').exists():
    raise SystemExit('Verified pre-maintenance backup was not found.')
marker = Path('/run/swg-local-maintenance')
marker.touch()
try:
    subprocess.run(['systemctl','stop','swg-local'],check=True)
    if subprocess.run(['pgrep','-x','core3'],stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError('Game still running; left admin role intact.')
    path.write_bytes(original)
    print('Restored the upstream admin role. Owner account level remains 15.',flush=True)
finally:
    subprocess.run(['systemctl','start','swg-local'],check=True)
    marker.unlink(missing_ok=True)
since = subprocess.check_output(['systemctl','show','swg-local','-p','ActiveEnterTimestamp','--value'],text=True).strip()
deadline=time.monotonic()+180
while time.monotonic()<deadline:
    logs=subprocess.check_output(['journalctl','-u','swg-local','--since',since,'--no-pager','-o','cat'],text=True)
    if '[Core] initialized' in logs:
        break
    if subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode:
        raise RuntimeError('Galaxy stopped during startup.')
    time.sleep(2)
else:
    raise RuntimeError('No galaxy initialization confirmation within three minutes.')
checks['admin_role_matches_upstream'] = path.read_bytes()==original
checks['owner_account_admin_level'] = subprocess.check_output(['mariadb','-Nse',"SELECT admin_level FROM swgemu.accounts WHERE username='owner'"],text=True).strip()
checks['source_changes'] = subprocess.check_output(['runuser','-u','swgemu','--','git','-C',str(repo),'status','--short'],text=True).strip()
checks['expected_game_ports_listening'] = all(':'+str(port) in subprocess.check_output(['ss','-lunp'],text=True) for port in (44453,44462,44463))
checks['mantis_access_error_after_restart'] = 'Access denied for user' in logs or 'MantisDatabase' in logs
checks['admin_commands_ingame_retest_pending'] = True
(outputs/'SWG-baseline-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(snapshot/'maintenance-change.txt').write_text('After this snapshot: disabled optional Mantis integration with Core3.MantisHost = "" and restored admin.lua to the exact upstream file (client flag 0). Owner account remains level 15; client admin-command setting remains enabled. Gameplay, zones and JTL were unchanged.\n')
windows_snapshot = outputs/'Backups'/snapshot.name
(windows_snapshot/'maintenance-change.txt').write_text((snapshot/'maintenance-change.txt').read_text())
print(json.dumps(checks,indent=2),flush=True)
