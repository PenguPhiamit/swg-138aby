from pathlib import Path
import hashlib, urllib.request, shutil
source = Path('/opt/swg/disc-extracted/SWG')
dest = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/SWG-client')
dest.mkdir(parents=True, exist_ok=True)
for asset in source.rglob('*'):
    if asset.is_file() and asset.suffix.lower() in ('.dll', '.m3d', '.asi', '.flt'):
        target = dest / asset.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists(): shutil.copy2(asset, target)
base = 'https://www.launchpad2.net/SWGEmu/'
manifest = Path('/opt/swg/client-required.txt').read_text()
for row in manifest.splitlines():
    if not row.strip(): continue
    name, size, digest = row.split(';')[:3]
    target = dest / name
    target.parent.mkdir(parents=True, exist_ok=True)
    def valid(p):
        if not p.is_file() or p.stat().st_size != int(size): return False
        with p.open('rb') as f: return hashlib.file_digest(f, 'md5').hexdigest().lower() == digest.strip().lower()
    if valid(target): continue
    if valid(source / name):
        shutil.copy2(source / name, target)
        print('Copied', name, flush=True)
    else:
        urllib.request.urlretrieve(base + name, target)
        if not valid(target): raise RuntimeError('Checksum mismatch: ' + name)
        print('Patched', name, flush=True)
for name in ['swgemu.cfg','swgemu_live.cfg','swgemu_login.cfg','swgemu_preload.cfg','swgemu_machineoptions.iff','options.cfg']:
    urllib.request.urlretrieve(base + name, dest / name)
print('Client files verified; configuration pending.', flush=True)
