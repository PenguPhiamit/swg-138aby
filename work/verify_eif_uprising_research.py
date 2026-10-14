from pathlib import Path
import hashlib,json,re,zipfile

BASE=Path(__file__).resolve().parents[1]
CAT=BASE/'outputs/Content-catalogue'
OUT=CAT/'EiF-Uprising'
audit=json.loads((OUT/'eif-source-audit.json').read_text())
active=json.loads((CAT/'active-content-catalogue.json').read_text())
assert len(audit['species'])==37
assert audit['unique_species_options']==47 and audit['species_header_entries']==66
assert len(active['rows'])==len({r['id'] for r in active['rows']})==102
assert sum(r['kind']=='Species' for r in active['rows'])==40
assert all(not r['runtime_validated'] for r in active['rows'])
assert not any(r['kind'] in ['SR gameplay','Excluded file'] for r in active['rows'])
assert not any('swgsremu' in s or 'sentinelsrepublic' in s.lower() for r in active['rows'] for s in r['sources'])
assert all(m['registered_in_serverobjects'] and m['declared_shared_template'] and m['in_eif_starsider01'] for r in audit['species'] for m in r['models'])
assert not any(f['restrictive_notice'] for f in audit['inspected_files'])
for package in audit['new_packages']+[audit['species_reference_bundle']]:
    path=OUT/package['name']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==package['sha256']
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
with zipfile.ZipFile(OUT/audit['species_reference_bundle']['name']) as z:
    assert len(z.namelist())==audit['species_reference_bundle']['files']
    assert 'LGPL-2.1.txt' in z.namelist() and 'MMOCoreORB/COPYING' in z.namelist()
    assert not any('sentinel' in n.lower() for n in z.namelist())
    original_files={f['path']:f for f in audit['inspected_files']}
    for name in z.namelist():
        if name in original_files:assert hashlib.sha256(z.read(name)).hexdigest()==original_files[name]['sha256']
for report in [OUT/'EiF-and-Uprising-research.md',CAT/'SWG-active-content-catalogue.md']:
    for target in re.findall(r'\]\(<([^>]+)>\)',report.read_text(encoding='utf-8')):
        assert Path(target).exists(),target
archive=OUT/'EiF-starsider01-reference.tre'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==audit['inspected_client_archive']['sha256']
manifest_path=BASE/'outputs/Community-content/collection-manifest.json'
manifest=json.loads(manifest_path.read_text())
manifest['active_scope_update_2026_10_13']=dict(excluded_projects=['Sentinels Republic'],
    inactive_historical_archives=['SR-public-scripts-reference.zip'],active_catalogue=str(CAT/'active-content-catalogue.json'),
    eif_uprising_report=str(OUT/'EiF-and-Uprising-research.md'),historical_counts_preserved=True)
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
result=dict(active_entries=102,legacy_eif_additions=37,later_eif_options_unverified=3,
            inspected_source_files=len(audit['inspected_files']),original_source_files_in_bundle=audit['species_reference_bundle']['files']-2,
            all_legacy_species_registered_and_matching_client_templates=True,
            sr_excluded_from_active_plan=True,source_notices_and_zip_integrity_checked=True,local_report_links_verified=True,
            client_archive_hash_verified=True,server_changes=False,gameplay_tested=False,
            external_messages_sent=False,payments_arranged=False)
(OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
