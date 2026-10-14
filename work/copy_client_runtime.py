from pathlib import Path
import shutil
source=Path('/opt/swg/disc-extracted/SWG')
dest=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client')
for asset in source.rglob('*'):
    if asset.is_file() and asset.suffix.lower() in ('.dll','.m3d','.asi','.flt'):
        target=dest/asset.relative_to(source)
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(asset,target)
            print('Installed runtime:',asset.name)
