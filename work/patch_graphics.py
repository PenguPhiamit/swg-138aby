from pathlib import Path
import urllib.request, shutil
dest=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client')
backup=Path('/opt/swg/runtime-backup')
backup.mkdir(exist_ok=True)
for name in ['gl05_r.dll','gl06_r.dll','gl07_r.dll']:
    shutil.copy2(dest/name,backup/name)
    urllib.request.urlretrieve('https://www.launchpad2.net/SWGEmu/'+name,dest/name)
    print('Patched',name,(dest/name).stat().st_size)
