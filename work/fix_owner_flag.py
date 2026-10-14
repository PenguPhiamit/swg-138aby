from pathlib import Path
import shutil, datetime
root=Path('/opt/swg/Core3/MMOCoreORB')
backup=Path('/opt/swg/config-backups')/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True)
staff=root/'bin/scripts/staff/levels/admin.lua'
shutil.copy2(staff,backup/'admin.lua')
text=staff.read_text()
if 'flag = 0,' not in text:
    raise SystemExit('Unexpected admin flag; no changes made.')
staff.write_text(text.replace('flag = 0,','flag = 2, -- Developer flag enables owner commands in the client',1))
print('Owner client privilege flag corrected. Account permissions unchanged.')
