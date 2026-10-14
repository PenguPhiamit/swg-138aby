from pathlib import Path
import collections, hashlib, json, re, shutil, struct, zipfile, zlib

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'work/research/eif-public'
OUT=BASE/'outputs/Content-catalogue/EiF-Uprising'
OUT.mkdir(parents=True,exist_ok=True)
REV='35bdbed4bba3015d592c928ecf30fb0e40e336c6'
SOURCE=f'https://gitlab.com/Empire-In-Flames/EiF-Public/-/blob/{REV}/'
racepath='MMOCoreORB/src/server/zone/objects/player/Races.h'
body=(ROOT/racepath).read_text(encoding='utf-8')
block=re.search(r'const static char\* Species\[\] = \{(.*?)\};',body,re.S).group(1)
species=re.findall(r'"([a-z_]+)"',block)
stock={'human','trandoshan','twilek','bothan','zabrak','rodian','moncal','wookiee','sullustan','ithorian'}
names={'smc':'Singing Mountain Clan Witch','ishi_tib':'Ishi Tib','kel_dor':'Kel Dor','chadra_fan':'Chadra-Fan','droid':'Droid (NK3 label in source; not verified IG-100)','moncal':'Mon Calamari','twilek':"Twi'lek"}
mtg=json.loads((BASE/'outputs/Content-catalogue/MTG-file-inventory.json').read_text())
assets={a['path']:a['archives'] for a in mtg['relevant_assets']}
playerroot=ROOT/'MMOCoreORB/bin/scripts/object/creature/player'
serverobjects=(playerroot/'serverobjects.lua').read_text()
clientobjects=(playerroot/'objects.lua').read_text()
rows=[]
for key in dict.fromkeys(species):
    if key in stock:continue
    models=[]
    for gender in ['male','female']:
        p=playerroot/f'{key}_{gender}.lua'
        if not p.exists():continue
        text=p.read_text()
        shared=f'object/creature/player/shared_{key}_{gender}.iff'
        models.append(dict(gender=gender,path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                          registered_in_serverobjects=f'creature/player/{key}_{gender}.lua' in serverobjects,
                          declared_shared_template=shared in clientobjects,
                          local_mtg_archives=assets.get(shared,[]),shared_template=shared,
                          starting_skills=re.findall(r'"(species_[^"]+)"',text),
                          notice='LGPL-2-or-later file header' if 'GNU Lesser' in text else 'See individual source'))
    rows.append(dict(key=key,name=names.get(key,key.title()),models=models,
                     source=SOURCE+racepath,code_available=True,client_package_complete=False,runtime_validated=False,
                     reuse='Published AGPL repository; player Lua retains LGPL file headers. Separate client-art terms unresolved beyond explicitly released packages.'))
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '.git' in p.parts:continue
    if p.suffix not in ['.lua','.cpp','.h'] and p.name not in ['COPYING','README']:continue
    rel=p.relative_to(ROOT).as_posix()
    raw=p.read_bytes();text=raw.decode('utf-8',errors='replace')
    notices=[l.strip() for l in text[:7000].splitlines() if re.search(r'copyright|proprietary|not for distribution|licen[cs]e',l,re.I)]
    files.append(dict(path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source=SOURCE+rel,
                      restrictive_notice=bool(re.search(r'proprietary|not for distribution',text,re.I)),notices=notices))
assert not any(f['restrictive_notice'] for f in files)
packages=[]
for name,url,author in [
    ('halyns_datapad.zip','https://modthegalaxy.com/index.php?resources/halyns-datapad.41/','Halyn / EiF'),
    ('unstable_lightsaber_blade.zip','https://modthegalaxy.com/index.php?resources/unstable-lightsaber-blades.118/','Halyn (shaders), Auri (textures) / EiF')]:
    p=Path('C:/Users/Pengw/Downloads')/name
    if not p.exists():continue
    raw=p.read_bytes()
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        members=[n for n in z.namelist() if not n.endswith('/')]
        notices=[]
        for n in members:
            if n.lower().endswith(('.lua','.txt','.md')) or re.search('license|copying|readme',n,re.I):
                text=z.read(n).decode('utf-8',errors='replace')
                notices.append(dict(path=n,text=text))
    shutil.copyfile(p,OUT/name)
    packages.append(dict(name=name,source=url,author=author,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),files=members,notices=notices,executed=False))
manifest=json.loads((BASE/'work/research/eif-patch-manifest.json').read_text(encoding='utf-8-sig'))
patches=[p for p in manifest['required'] if p['name'].endswith('.tre')]
result=dict(researched='2026-10-13',repository='https://gitlab.com/Empire-In-Flames/EiF-Public',revision=REV,revision_date='2017-08-09',
            species_header_entries=len(species),unique_species_options=len(set(species)),additional_options=len(rows),species=rows,
            inspected_files=files,new_packages=packages,
            missing_custom_entry_point='MMOCoreORB/bin/custom_scripts/screenplays/screenplays.lua',
            patch_repository='https://gitlab.com/EiF-Public/patch-files',patch_revision='5f97c7983d2ab950255113f9ae96447b3526f454',
            patch_date='2025-10-19',manifest_patch_count=len(patches),manifest_patch_bytes=sum(p['size'] for p in patches),
            manifest_scope='Client files for playing EiF. No blanket asset reuse license found in root README or file index. starsider45.tre exists in repository index but is absent from this manifest.',
            server_changes=False)
archivepath=BASE/'work/research/eif-starsider01.tre'
if archivepath.exists():
    raw=archivepath.read_bytes()
    expected=next(p for p in patches if p['name']=='starsider01.tre')
    assert len(raw)==expected['size'] and hashlib.md5(raw).hexdigest().lower()==expected['md5'].lower()
    magic,version,count,offset,ftype,fsize,ntype,nsize,usize=struct.unpack('<4s4s7I',raw[:36])
    assert (magic,version)==(b'EERT',b'5000')
    records_len=fsize if ftype==2 else count*24
    records=raw[offset:offset+records_len]
    if ftype==2:records=zlib.decompress(records)
    names=raw[offset+records_len:offset+records_len+(nsize if ntype==2 else usize)]
    if ntype==2:names=zlib.decompress(names)
    entries=[];tables=[]
    for i in range(count):
        record=struct.unpack_from('<6I',records,i*24)
        start=record[5];end=names.find(b'\0',start);name=names[start:end].decode('latin1')
        entries.append(dict(path=name,bytes=record[1]))
        if name.startswith(('datatables/creation/','datatables/player/')) or name=='object/creature/player/shared_droid_male.iff':
            data=raw[record[2]:record[2]+(record[4] if record[3]==2 else record[1])]
            if record[3]==2:data=zlib.decompress(data)
            tables.append(dict(path=name,strings=[s.decode('latin1') for s in re.findall(rb'[ -~]{4,}',data)]))
    entrynames={e['path'] for e in entries}
    for row in rows:
        for model in row['models']:model['in_eif_starsider01']=model['shared_template'] in entrynames
    result['inspected_client_archive']=dict(name='starsider01.tre',path=str(archivepath),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
        md5=hashlib.md5(raw).hexdigest(),matches_pinned_manifest=True,entry_count=count,
        all_player_templates_found=sum(all(m['in_eif_starsider01'] for m in r['models']) for r in rows),
        source='https://gitlab.com/EiF-Public/patch-files/-/blob/5f97c7983d2ab950255113f9ae96447b3526f454/assets/starsider01.tre',
        installed=False,reuse='Publicly downloadable EiF player patch; separate asset reuse permission not established.')
    (OUT/'EiF-starsider01-index.json').write_text(json.dumps(dict(archive=result['inspected_client_archive'],entries=entries,datatable_string_evidence=tables),indent=2),encoding='utf-8')
(OUT/'eif-source-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
shutil.copyfile(ROOT/'MMOCoreORB/COPYING',OUT/'EiF-public-COPYING.txt')
shutil.copyfile(BASE/'work/research/eif-patch-manifest.json',OUT/'EiF-public-patch-manifest.json')
print(json.dumps(dict(unique_species_options=result['unique_species_options'],additional_options=len(rows),
                     header_entries=len(species),names=[r['name'] for r in rows],
                     with_mtg_player_assets=sum(all(m['local_mtg_archives'] for m in r['models']) for r in rows),
                     inspected_files=len(files),packages=[p['name'] for p in packages],patch_count=len(patches),patch_bytes=result['manifest_patch_bytes'],
                     client_archive=result.get('inspected_client_archive')),indent=2))
