"""Fetch explicit owner-authorized CC0 packages; never extract or execute them.

Official source HTML is retained as licence evidence. ZIP members and licences
are recorded through zipfile reads only. Hard transfer/expanded-size limits.
"""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3] / 'outputs/Farming-assets'
CAP = 3_000_000_000
PACKAGES = [
    ('interface-textures', 'rubberduck',
     'https://opengameart.org/content/sci-fi-interface-textures',
     'https://opengameart.org/sites/default/files/sci-fi-interface-textures.zip'),
    *[(f'interface-source-{i}', 'rubberduck',
       'https://opengameart.org/content/sci-fi-interface-textures',
       f'https://opengameart.org/sites/default/files/interface_{i}_source.zip') for i in range(1, 5)],
    ('kenney-space-station', 'Kenney', 'https://kenney.nl/assets/space-station-kit',
     'https://kenney.nl/media/pages/assets/space-station-kit/6475288f2e-1712749919/kenney_space-station-kit.zip'),
    ('industrial-pbr', 'a52; rubberduck; Yughues (some textures)',
     'https://opengameart.org/content/pbr-industrial-asset-pack',
     'https://opengameart.org/sites/default/files/oga_industrial_a52_version_0.zip'),
    ('industrial-pbr-baked', 'a52; rubberduck; Yughues (some textures)',
     'https://opengameart.org/content/pbr-industrial-asset-pack',
     'https://opengameart.org/sites/default/files/oga_industrial_a52_version_baked_models_0.zip'),
    ('industrial-tanks', 'rubberduck',
     'https://opengameart.org/content/industrial-extension-pack-1-tanks',
     'https://opengameart.org/sites/default/files/Industrial_pack_1_tanks.zip'),
    ('industrial-pipes', 'rubberduck',
     'https://opengameart.org/content/3d-lod-pipe-construction-set',
     'https://opengameart.org/sites/default/files/3d-LOD-pipe-construction-set.zip'),
    ('brick-planters', 'tiko479',
     'https://opengameart.org/content/brick-planters-low-poly-style',
     'https://opengameart.org/sites/default/files/brick_planters.zip'),
    ('industrial-original', 'rubberduck; Yughues (some textures)',
     'https://opengameart.org/content/high-quality-industrial-asset-pack',
     'https://opengameart.org/sites/default/files/OGA_industrial.zip'),
    ('kenney-food', 'Kenney', 'https://kenney.nl/assets/food-kit',
     'https://kenney.nl/media/pages/assets/food-kit/83086fa91c-1719418518/kenney_food-kit.zip'),
    ('kenney-nature', 'Kenney', 'https://kenney.nl/assets/nature-kit',
     'https://kenney.nl/media/pages/assets/nature-kit/37ac38a37b-1677698939/kenney_nature-kit.zip'),
]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={
        'User-Agent': 'SWG-local-asset-audit/1.0'}), timeout=30)


def run():
    ROOT.mkdir(parents=True, exist_ok=True)
    receipts = []
    used = sum(p.stat().st_size for p in ROOT.rglob('*.zip'))
    for slug, authors, source, url in PACKAGES:
        folder = ROOT / slug
        folder.mkdir(exist_ok=True)
        cached = folder / 'receipt.json'
        if cached.exists() and (folder / 'original.zip').exists():
            previous = json.loads(cached.read_text(encoding='utf-8'))
            if previous.get('status', '').startswith('downloaded'):
                with (folder / 'original.zip').open('rb') as saved:
                    if hashlib.file_digest(saved, 'sha256').hexdigest() == previous.get('sha256'):
                        receipts.append({k: v for k, v in previous.items() if k != 'files'})
                        continue
        record = dict(slug=slug, authors=authors, source=source, download=url,
                      retrieved_utc=datetime.now(timezone.utc).isoformat(), imported=False)
        try:
            with get(source) as reply:
                page = reply.read(2_000_001)
            if len(page) > 2_000_000 or b'CC0' not in page:
                raise ValueError('source licence evidence missing or oversized')
            (folder / 'source.html').write_bytes(page)
            target = folder / 'original.zip'
            if not target.exists():
                with get(url) as reply:
                    size = reply.headers.get('Content-Length')
                    record['announced_bytes'] = int(size) if size else None
                    # Fail closed when no pre-transfer size is available.
                    if not size or int(size) <= 0 or used + int(size) > CAP:
                        raise ValueError('missing size or batch cap exceeded')
                    partial = target.with_suffix('.partial')
                    actual = 0
                    with partial.open('wb') as out:
                        while chunk := reply.read(1024 * 1024):
                            actual += len(chunk)
                            if used + actual > CAP or actual > int(size):
                                raise ValueError('transfer exceeded declared size or cap')
                            out.write(chunk)
                    if actual != int(size):
                        raise ValueError('incomplete transfer')
                    partial.replace(target)
                    used += actual
            record['bytes'] = target.stat().st_size
            with target.open('rb') as saved:
                record['sha256'] = hashlib.file_digest(saved, 'sha256').hexdigest()
            with zipfile.ZipFile(target) as archive:
                files = archive.infolist()
                if len(files) > 100_000 or sum(f.file_size for f in files) > 10_000_000_000:
                    raise ValueError('expanded inventory limit exceeded')
                record['files'] = [dict(name=f.filename, bytes=f.file_size, crc32=f.CRC) for f in files]
                licences = []
                for i, member in enumerate(files):
                    if any(s in Path(member.filename).name.lower() for s in ('license', 'licence', 'readme', 'credit')):
                        if member.file_size <= 200_000:
                            saved = f'notice-{i}.txt'
                            (folder / saved).write_bytes(archive.read(member))
                            licences.append(dict(member=member.filename, saved=saved))
                record['notices'] = licences
            record['status'] = 'downloaded; retained original; import not approved'
            record['license'] = 'CC0 per retained official source; inspect notices before import'
        except Exception as error:
            record['status'] = 'held'
            record['reason'] = str(error)
        (folder / 'receipt.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
        receipts.append({k: v for k, v in record.items() if k != 'files'})
        print(slug, record['status'], record.get('bytes', 0), flush=True)
    (ROOT / 'receipts.json').write_text(json.dumps(receipts, indent=2), encoding='utf-8')


if __name__ == '__main__':
    run()
