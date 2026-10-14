from pathlib import Path
import secrets, subprocess
root=Path('/opt/swg/Core3/MMOCoreORB')
subprocess.run(['systemctl','start','mariadb'],check=True)
exists=subprocess.check_output(['mariadb','-Nse',"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='swgemu'"],text=True).strip()
if exists:
    raise SystemExit('Existing swgemu database detected; leaving it intact.')
with (root/'sql/swgemu.sql').open('rb') as f:
    subprocess.run(['mariadb'],stdin=f,check=True)
password=secrets.token_hex(24)
secret=secrets.token_hex(32)
sql=f"CREATE USER 'swgemu'@'127.0.0.1' IDENTIFIED BY '{password}'; GRANT ALL PRIVILEGES ON swgemu.* TO 'swgemu'@'127.0.0.1'; UPDATE swgemu.galaxy SET name='My Galaxy',address='127.0.0.1' WHERE galaxy_id=2;"
subprocess.run(['mariadb'],input=sql,text=True,check=True)
config=root/'bin/conf/config-local.lua'
config.write_text(f'''Core3.DBHost = "127.0.0.1"
Core3.DBUser = "swgemu"
Core3.DBPass = "{password}"
Core3.DBSecret = "{secret}"
Core3.TrePath = "/opt/swg/tre"
Core3.AutoReg = 1
Core3.CharacterBuilderEnabled = "true"
Core3.ZoneProcessingThreads = 4
Core3.MaxNavMeshJobs = 2
''')
config.chmod(0o600)
print('Private development galaxy database and configuration created.')
