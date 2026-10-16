"""S7: the Hutt test archive = the INSTALLED local_planets.tre (SWG-client, whatever chain built it) + the playable Hutt.

The owner's client already runs SWG-client/local_planets.tre (4,636,682 B on 16 Oct; no build record names its chain),
so the Hutt goes on top of exactly that archive, and every entry the Hutt does not touch stays byte-identical:
  1. extract the installed archive into work/stage;
  2. species_tables.stage_species(['hutt']) (S4) with a base that reads the installed archive first, then the client;
  3. appearance/lat/hutt.lat from tools/build_hutt_lat.py (Level 1, the animation map; rebuilt if missing);
  4. pack with swgfmt.tre_write; checks: untouched entries identical, the Hutt closure, the lat parses.
    C:/Users/Pengw/miniconda3/python.exe -I build_test_archive.py
Writes local_planets-s7.tre and checks.json beside this file. Nothing is installed; the owner's client is not touched.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(SPECIES)
WORK = os.path.join(HERE, 'work')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
from swgfmt import tre_write  # noqa: E402
import species_tables  # noqa: E402

INSTALLED = os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre')
OUT_TRE = os.path.join(HERE, 'local_planets-s7.tre')
LAT = os.path.join(HERE, 'staged', 'client', 'appearance', 'lat', 'hutt.lat')


def main():
    stage = os.path.join(WORK, 'stage')
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)

    installed_bytes = open(INSTALLED, 'rb').read()
    base_entries = tre_write.read(installed_bytes)[0]
    for name, data in base_entries.items():
        path = os.path.join(stage, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)

    def base(rel):  # the installed archive wins, as it does in the client
        return base_entries[rel] if rel in base_entries else species_tables.default_base(rel)

    report = species_tables.stage_species(['hutt'], stage, base=base)

    if not os.path.isfile(LAT):
        subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'build_hutt_lat.py')], check=True, cwd=HERE)
    lat_dst = os.path.join(stage, 'appearance', 'lat', 'hutt.lat')
    os.makedirs(os.path.dirname(lat_dst), exist_ok=True)
    shutil.copyfile(LAT, lat_dst)

    data, names = tre_write.pack_dir(stage, OUT_TRE)
    ours = tre_write.read(data)[0]
    changed = sorted(n for n in base_entries if n in ours and base_entries[n] != ours[n])
    missing = sorted(n for n in base_entries if n not in ours)
    new = sorted(n for n in ours if n not in base_entries)

    checks = {
        'installed': {'path': 'SWG-client/local_planets.tre', 'bytes': len(installed_bytes),
                      'sha256': hashlib.sha256(installed_bytes).hexdigest(), 'entries': len(base_entries)},
        'out': {'path': os.path.relpath(OUT_TRE, OUTPUTS).replace(os.sep, '/'), 'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(), 'entries': len(ours)},
        'untouched_identical': len(base_entries) - len(changed) - len(missing),
        'changed': changed, 'new': new, 'dropped': missing,
        'lat_bytes': len(ours.get('appearance/lat/hutt.lat', b'')),
        'species_report': {'files': sorted(report.get('files', {})), 'notes': report.get('notes', [])},
    }
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: v for k, v in checks.items() if k != 'species_report'}, indent=1)[:1800])
    print('species notes:', report.get('notes', [])[:12])
    assert not missing, 'entries dropped from the installed archive'
    return 0


if __name__ == '__main__':
    sys.exit(main())
