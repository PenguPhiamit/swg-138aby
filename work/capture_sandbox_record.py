from pathlib import Path
import hashlib,json,re,subprocess,zipfile
BASE=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
OUT=BASE/'outputs';ROOT=Path('/opt/swg/Core3/MMOCoreORB')
validation=json.loads((OUT/'SWG-sandbox-validation.json').read_text())
logs=(BASE/'work/sandbox-startup.log').read_text(errors='replace')
validation['warning_line_count']=sum('WARNING' in line for line in logs.splitlines())
validation['referenced_warning_paths']=sorted({value for value in re.findall(r'(?:WARNING - |could not open lua derv: |AppearanceTemplate not found:)([^\s]+)',logs) if '/' in value})
validation['asset_hash_checks']=[]
assets=json.loads((OUT/'Community-content/MTG-assets/manifest.json').read_text())
for entry in assets['files']:
    result={'name':entry['name']}
    for label,folder in [('server',Path('/opt/swg/tre')),('client',OUT/'SWG-client')]:
        with (folder/entry['name']).open('rb') as stream:
            result[label+'_matches_download']=hashlib.file_digest(stream,'sha256').hexdigest()==entry['sha256']
    validation['asset_hash_checks'].append(result)
if not all(x['server_matches_download'] and x['client_matches_download'] for x in validation['asset_hash_checks']):raise RuntimeError('An installed asset copy failed its checksum.')
validation['all_23_installed_assets_match_download']=True
(OUT/'SWG-sandbox-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
support=OUT/'Documentation-support';support.mkdir(exist_ok=True)
(support/'sandbox-startup.log').write_text(logs)
settings=json.loads((OUT/'SWG-sandbox-settings.json').read_text())
with zipfile.ZipFile(OUT/'Community-content/Local-sandbox-changes.zip','w',zipfile.ZIP_DEFLATED) as archive:
    added=set()
    for rel in settings['changed_files']+['bin/scripts/object/allobjects.lua','bin/scripts/object/serverobjects.lua','bin/scripts/mobile/serverobjects.lua','bin/scripts/mobile/conversations.lua','bin/scripts/screenplays/screenplays.lua','bin/scripts/object/tangible/terminal/terminal_character_builder.lua','bin/scripts/object/sandbox/mtg_catalog.lua','bin/scripts/screenplays/custom_screenplays/the_tutorial/the_tutorial_0001_the_beginning.lua']:
        if rel=='bin/conf/config-local.lua' or rel in added:continue
        archive.write(ROOT/rel,rel);added.add(rel)
    local=(ROOT/'bin/conf/config-local.lua').read_text()
    archive.writestr('sandbox-profile.lua',local.split('-- Local sandbox profile, applied October 13, 2026.',1)[1])
    archive.write(OUT/'Community-content/CREDITS-and-sources.txt','CREDITS-and-sources.txt')
    archive.write('/opt/swg/Core3/COPYING','COPYING')
patch=subprocess.check_output(['runuser','-u','swgemu','--','git','-C','/opt/swg/Core3','diff','--binary','--','.',':(exclude)MMOCoreORB/bin/scripts/managers/resource_manager_spawns.lua'],text=True)
(support/'tracked-source-changes.patch').write_text(patch)
(support/'record-index.json').write_text(json.dumps({'source_patch':'tracked-source-changes.patch','startup_log':'sandbox-startup.log','reproducible_source_package':'../Community-content/Local-sandbox-changes.zip','private_configuration_included':False,'note':'The standalone profile contains only the new public sandbox and content settings; database credentials are omitted.'},indent=2)+'\n')
print('All 23 server/client asset copies match their downloaded hashes. Warning inventory and reproducible source package saved.',flush=True)
