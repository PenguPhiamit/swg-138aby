from pathlib import Path
from datetime import datetime, timezone
import re, shutil, subprocess

SERVER = Path('/opt/swg/Core3')
OUTPUTS = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
PORTS = (44453, 44462, 44463)

def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ''

def git(*args):
    return run(['runuser','-u','swgemu','--','git','-C',str(SERVER),*args])

def line(label, value, ok=None):
    mark = '       ' if ok is None else ('[ OK ] ' if ok else '[WARN] ')
    print(f'{mark}{label:<22} {value}')

print('SWG local galaxy status\n')

galaxy = run(['systemctl','is-active','swg-local']) or 'inactive'
database = run(['systemctl','is-active','mariadb']) or 'inactive'
line('Galaxy service', galaxy, galaxy == 'active')
line('Database service', database, database == 'active')

since = run(['systemctl','show','swg-local','-p','ActiveEnterTimestamp','--value'])
if galaxy == 'active' and since:
    line('Running since', since)
    logs = run(['journalctl','-u','swg-local','--since',since,'--no-pager','-o','cat'])
    ready = '[Core] initialized' in logs
    line('Initialized', 'yes' if ready else 'not yet (still loading?)', ready)
    errors = [l for l in logs.splitlines() if re.search(r'\bERROR\b|FATAL|lua error|Lua error', l)]
    line('Error lines', f'{len(errors)} since start', not errors)
    for entry in errors[-5:]:
        print('         ', entry[:160])
    sockets = run(['ss','-lun'])
    listening = [p for p in PORTS if f':{p} ' in sockets + ' ']
    line('Game ports', ', '.join(map(str, listening)) or 'none', len(listening) == len(PORTS))

if database == 'active':
    address = run(['mariadb','-Nse','SELECT address FROM swgemu.galaxy WHERE galaxy_id=2'])
    config = OUTPUTS/'SWG-client/swgemu_login.cfg'
    client = ''
    if config.exists():
        found = re.search(r'loginServerAddress0=(\S+)', config.read_text())
        client = found.group(1) if found else ''
    line('Galaxy address', f'{address} (client: {client or "missing"})', bool(address) and address == client)
    line('Accounts/characters', run(['mariadb','-Nse',
         'SELECT CONCAT((SELECT count(*) FROM swgemu.accounts),"/",(SELECT count(*) FROM swgemu.characters))']))

branch = git('rev-parse','--abbrev-ref','HEAD')
head = git('log','-1','--format=%h %s')
dirty = [l for l in git('status','--short').splitlines() if l]
local = git('rev-list','--count','upstream-base..HEAD')
line('Source branch', f'{branch} @ {head}', branch == 'sandbox')
line('Local commits', f'{local or "?"} on top of upstream-base')
line('Uncommitted files', str(len(dirty)), len(dirty) <= 1)
for entry in dirty[:8]:
    print('         ', entry)
push = git('remote','get-url','--push','origin')
line('Push to GitHub', 'disabled' if 'DISABLED' in push else push, 'DISABLED' in push)

backups = sorted((OUTPUTS/'Backups').glob('*-20*Z'), key=lambda p: p.name.rsplit('-',1)[-1])
if backups:
    newest = backups[-1]
    stamp = datetime.strptime(newest.name.rsplit('-',1)[-1], '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - stamp
    days = age.total_seconds() / 86400
    line('Newest backup', f'{newest.name} ({days:.1f} days old)', days < 7)
else:
    line('Newest backup', 'none found', False)

free = shutil.disk_usage('/opt/swg').free / 2**30
line('Free disk (Debian)', f'{free:.0f} GiB', free > 20)
