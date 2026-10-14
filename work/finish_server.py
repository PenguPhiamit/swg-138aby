from pathlib import Path
import subprocess, secrets, hashlib, re
root=Path('/opt/swg/Core3/MMOCoreORB')
config=(root/'bin/conf/config-local.lua').read_text()
secret=re.search(r'Core3.DBSecret = "(.*?)"',config).group(1)
password=secrets.token_urlsafe(14)
salt=secrets.token_hex(16)
digest=hashlib.sha256((secret+password+salt).encode()).hexdigest()
sql=f"INSERT INTO swgemu.accounts (username,password,station_id,admin_level,salt) VALUES ('owner','{digest}',1,15,'{salt}');"
subprocess.run(['mariadb'],input=sql,text=True,check=True)
out=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
(out/'SWG-login.txt').write_text(f'Private development server\nUsername: owner\nPassword: {password}\nAdministrator access: enabled\n')
subprocess.run(['useradd','--system','--create-home','--home-dir','/opt/swg/home','--shell','/bin/bash','swgemu'],check=True)
subprocess.run(['chown','-R','swgemu:swgemu','/opt/swg/Core3','/opt/swg/tre'],check=True)
Path('/etc/systemd/system/swg-local.service').write_text('''[Unit]
Description=Local SWGEmu development galaxy
After=mariadb.service
Requires=mariadb.service
[Service]
User=swgemu
WorkingDirectory=/opt/swg/Core3/MMOCoreORB/bin
ExecStart=/usr/bin/python3 /opt/swg/server_service.py
TimeoutStopSec=300
KillMode=mixed
[Install]
WantedBy=multi-user.target
''')
subprocess.run(['systemctl','daemon-reload'],check=True)
print('Owner account and manually started server service prepared.')
