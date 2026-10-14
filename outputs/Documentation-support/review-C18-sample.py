"""Read-only 30-object sample; writes evidence beside this script, never stages/applies."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent / 'Fable-backport'
sys.path.insert(0, str(BASE / 'tools'))
import swg_iff
from dormant_analysis import crc_table


def main():
    a = json.loads((BASE / 'work/batch1_objects.json').read_text())['objects']
    b = json.loads((BASE / 'work/batch2_objects.json').read_text())['objects']
    sample = [o for o in a if o['batch'] == '1b']  # all 13 wearables
    sample += [o for o in a if o['batch'] == '1c']  # 3 shared-path repairs
    sample += [next(o for o in a if word in o['server']) for word in (
        'aurebesh_tile_aurek', '/npc_loot/aero', '/cube_loot/', '/cave_driftwood.iff')]
    sample += [o for o in b if o['kind'] == 'new']  # 10 statics/furniture
    assert len(sample) == len({o['server'] for o in sample}) == 30
    merged = crc_table((OUT.parent / 'Local-content/local_planets/misc/object_template_crc_string_table.iff').read_bytes())
    rows = []
    for o in sample:
        batch = '2' if o in b else '1'
        root = BASE / ('staged-batch2' if batch == '2' else 'staged') / 'MMOCoreORB/bin/scripts/object'
        raw = swg_iff.scd.client_file(o['shared'])
        info = swg_iff.resolved(o['shared'])
        files = []
        for rel in o['files']:
            data = (root / rel).read_bytes()
            applied = subprocess.run(['wsl', '-d', 'Debian', '-u', 'swgemu', '--', 'git', '-C',
                '/opt/swg/Core3-dev', 'show', ('5c7ae017' if batch == '2' else '0c44d431') +
                ':MMOCoreORB/bin/scripts/object/' + rel], capture_output=True, check=True).stdout
            files.append(dict(path=rel, sha256=hashlib.sha256(data).hexdigest(), applied_matches=applied == data))
        texts = '\n'.join((root / f).read_text(encoding='latin-1') for f in o['files'])
        registered = o['server'] in re.findall(r'ObjectTemplates:addTemplate\(\s*\w+\s*,\s*"([^"]+)"', texts)
        # Two client-only repairs use an unchanged server file outside their staged-file list.
        existing_server_files = []
        if not registered:
            for candidate in root.rglob('*.lua'):
                body = candidate.read_text(encoding='latin-1')
                if o['server'] in re.findall(r'ObjectTemplates:addTemplate\(\s*\w+\s*,\s*"([^"]+)"', body):
                    existing_server_files.append(str(candidate.relative_to(root)))
            for line in (BASE / 'work/core3_server_templates_files.tsv').read_text().splitlines():
                parts = line.split('\t')
                if len(parts) == 3 and parts[2] == o['server']:
                    existing_server_files.append(parts[0])
            registered = bool(existing_server_files)
        repair_exact = None
        if o['kind'] == 'repair':
            old = (BASE / 'work/core3_orig' / o['files'][0]).read_bytes()
            new = (root / o['files'][0]).read_bytes()
            repair_exact = old.replace(('"' + o['was'] + '"').encode(), ('"' + o['server'] + '"').encode()) == new
        rows.append(dict(server=o['server'], shared=o['shared'], batch=batch, form=raw[8:12].decode() if raw else None,
                         client_sha256=hashlib.sha256(raw).hexdigest() if raw else None,
                         resolved_form=info['form'] if info else None, crc_present=o['shared'] in merged,
                         registered=registered, existing_server_files=existing_server_files,
                         one_string_repair_exact=repair_exact, files=files))
    (OUT / 'C18-sample-evidence.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(dict(objects=len(rows), client_present=sum(bool(r['client_sha256']) for r in rows),
         crc_present=sum(r['crc_present'] for r in rows), registered=sum(r['registered'] for r in rows),
         applied_mismatches=[f for r in rows for f in r['files'] if not f['applied_matches']],
         repair_mismatches=[r['server'] for r in rows if r['one_string_repair_exact'] is False]), indent=2))


if __name__ == '__main__':
    main()
