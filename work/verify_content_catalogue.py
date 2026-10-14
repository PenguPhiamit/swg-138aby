from pathlib import Path
import collections,hashlib,json,urllib.parse,zipfile

base=Path(__file__).resolve().parents[1]
out=base/'outputs/Content-catalogue'
data=json.loads((out/'content-catalogue.json').read_text(encoding='utf-8'))
inventory=json.loads((out/'MTG-file-inventory.json').read_text(encoding='utf-8'))
rows=data['rows']
assert len(rows)==len({r['id'] for r in rows})
assert all(r['sources'] and all(urllib.parse.urlsplit(u).scheme=='https' for u in r['sources']) for r in rows)
for kind,key in [('Planet','ground_worlds'),('Station','stations'),('Species','additional_species')]:
    assert sum(r['kind']==kind for r in rows)==data['counts'][key]
species=[r for r in rows if r['kind']=='Species' and 'genders' in r]
assert len(species)==16
assert all(e['archives'] for r in species for e in r['local_asset_evidence'])
worlds=[r for r in rows if r['kind']=='Planet' and r.get('local_asset_evidence')]
assert len(worlds)==11
assert all(len(r['local_asset_evidence'])==2 for r in worlds)
assert len(inventory['files'])==16734
assert not any('proprietary' in ' '.join(f['notices']).lower() or 'not for distribution' in ' '.join(f['notices']).lower() for f in inventory['files'])
assert len([r for r in rows if r['status']=='X'])==2
assert not any(r['runtime_validated'] for r in rows)
packages=json.loads((out/'downloaded-package-evidence.json').read_text(encoding='utf-8'))
assert len(packages)==13
for package in packages:
    filename='newspecies-original.zip' if package['name']=='newspecies.zip' else package['name']
    path=out/filename
    raw=path.read_bytes()
    assert len(raw)==package['bytes']
    assert hashlib.sha256(raw).hexdigest()==package['sha256']
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
    assert not package['executed']
counts=collections.Counter(r['status_label'] for r in rows)
result=dict(catalogue_entries=len(rows),worlds_with_terrain_and_snapshot=len(worlds),
            additional_species_with_player_template_evidence=len(species),mtg_lua_files=len(inventory['files']),
            downloaded_packages=len(packages),status_counts=dict(counts),checks='Identifiers, counts, evidence references, source URL schemes, restrictive-notice scan, runtime-status labels, downloaded ZIP integrity and SHA-256 hashes verified. This does not validate third-party download availability or gameplay.',
            server_changes=False)
(out/'catalogue-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
