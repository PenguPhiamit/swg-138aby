from pathlib import Path
import hashlib,json,re,subprocess,time

BASE=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
OUT=BASE/'outputs'
def capture(args):return subprocess.check_output(args,text=True).strip()
subprocess.run(['systemctl','start','swg-local'],check=True)
Path('/run/swg-local-maintenance').unlink(missing_ok=True)
since=capture(['systemctl','show','swg-local','-p','ActiveEnterTimestamp','--value'])
deadline=time.monotonic()+240
while time.monotonic()<deadline:
    logs=capture(['journalctl','-u','swg-local','--since',since,'--no-pager','-o','cat'])
    if '[Core] initialized' in logs:break
    if subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode:
        (BASE/'work/sandbox-startup.log').write_text(logs)
        print('\n'.join(logs.splitlines()[-45:]),flush=True)
        raise RuntimeError('Galaxy stopped during startup.')
    time.sleep(2)
else:raise RuntimeError('Galaxy did not confirm startup within four minutes.')
time.sleep(4)
logs=capture(['journalctl','-u','swg-local','--since',since,'--no-pager','-o','cat'])
(BASE/'work/sandbox-startup.log').write_text(logs)
errors=[line for line in logs.splitlines() if re.search(r'\bERROR\b|\bFATAL\b|Lua.*error|attempt to|stack traceback|Segmentation',line,re.I)]
warnings=sorted(set(re.findall(r'WARNING - ([^\s]+) not found\.',logs)))
ports=capture(['ss','-lunp'])
record={'server_initialized':True,'expected_game_ports_listening':all(':'+str(p) in ports for p in (44453,44462,44463)),
        'schema':capture(['mariadb','-Nse','SELECT * FROM swgemu.db_metadata']),
        'account_and_character_counts':capture(['mariadb','-Nse','SELECT count(*) FROM swgemu.accounts; SELECT count(*) FROM swgemu.characters;']),
        'owner_admin_level':capture(['mariadb','-Nse',"SELECT admin_level FROM swgemu.accounts WHERE username='owner'"]),
        'error_lines':errors,'missing_asset_warning_paths':warnings,
        'compiled_executable_sha256':hashlib.file_digest(open('/opt/swg/Core3/MMOCoreORB/bin/core3','rb'),'sha256').hexdigest(),
        'gameplay_tests':'Login, command entry, resource generation, crafting, house placement, quest completion and ship flight require in-game verification.',
        'startup_since':since}
(OUT/'SWG-sandbox-validation.json').write_text(json.dumps(record,indent=2)+'\n')
install=json.loads((OUT/'SWG-community-install.json').read_text())
install['runtime_test_pending']=False
install['server_initialized']=True
install['startup_error_line_count']=len(errors)
(OUT/'SWG-community-install.json').write_text(json.dumps(install,indent=2)+'\n')
print(json.dumps({**record,'error_lines':errors[:30],'missing_asset_warning_paths':warnings[:20]},indent=2),flush=True)
