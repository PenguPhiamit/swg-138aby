from pathlib import Path
import collections, hashlib, json, re, struct, zipfile, zlib

BASE = Path(__file__).resolve().parents[1]
LIB = BASE / 'outputs/Community-content'
OUT = BASE / 'outputs/Content-catalogue'
OUT.mkdir(exist_ok=True)
REV = '54deb619e83c2c5e353f6a825a829d56201704f0'
source_base = f'https://github.com/ModTheGalaxy/mtgserver/blob/{REV}/'
files = []
with zipfile.ZipFile(LIB/'MTG-published-content.zip') as archive:
    for name in archive.namelist():
        if not name.endswith('.lua'):
            continue
        data = archive.read(name)
        body = data.decode('utf-8', errors='replace')
        registrations = re.findall(r'ObjectTemplates:addTemplate\([^\n]*?,\s*"([^"]+)"\)', body)
        mobiles = re.findall(r'CreatureTemplates:addCreatureTemplate\([^\n]*?,\s*"([^"]+)"\)', body)
        relative = name.split('bin/scripts/',1)[-1]
        if relative.startswith('object/custom_content/'):
            category = 'object/' + relative.split('/')[2]
        elif relative.startswith('mobile/custom_content/'):
            category = 'mobile/' + relative.split('/')[2]
        else:
            category = '/'.join(relative.split('/')[:2])
        notices = [line.strip()[:250] for line in body[:5000].splitlines() if re.search(r'copyright|proprietary|not for distribution|licen[cs]e|author:|created by|written by',line,re.I)]
        files.append(dict(path=name,category=category,templates=registrations,mobile_templates=mobiles,
                          sha256=hashlib.sha256(data).hexdigest(),notices=notices,source=source_base+name,
                          reuse='MTG published contributor-use statement; preserve notices and credit; underlying game assets are separate',
                          tested=False))

assets = collections.defaultdict(list)
special = []
total_entries = 0
for path in sorted((LIB/'MTG-assets').glob('*.tre')):
    with path.open('rb') as stream:
        magic,version,count,offset,ftype,fsize,ntype,nsize,usize = struct.unpack('<4s4s7I',stream.read(36))
        if magic != b'EERT' or version != b'5000':
            raise RuntimeError(f'Unsupported archive {path.name}: {magic} {version}')
        stream.seek(offset)
        records=stream.read(fsize if ftype==2 else count*24)
        if ftype==2: records=zlib.decompress(records)
        names=stream.read(nsize if ntype==2 else usize)
        if ntype==2: names=zlib.decompress(names)
        for i in range(count):
            record=struct.unpack_from('<6I',records,i*24)
            start=record[5]; end=names.find(b'\0',start)
            name=names[start:end].decode('latin1')
            total_entries+=1
            if name.startswith(('terrain/','snapshot/','object/creature/player/','object/creature/','datatables/creation/','datatables/player/','datatables/travel/')):
                assets[name].append(path.name)
            if name.startswith(('datatables/creation/','datatables/player/','datatables/travel/')) or (name.startswith('datatables/') and any(x in name for x in ['species','race','planet'])):
                pos=stream.tell(); stream.seek(record[2])
                payload=stream.read(record[4] if record[3]==2 else record[1]); stream.seek(pos)
                if record[3]==2: payload=zlib.decompress(payload)
                strings=[x.decode('latin1') for x in re.findall(rb'[ -~]{4,}',payload)]
                special.append(dict(path=name,archive=path.name,strings=strings))

counts=dict(sorted(collections.Counter(x['category'] for x in files).items()))
result=dict(researched='2026-10-13',revision=REV,scope='Every Lua file in the collected MTG published-content bundle; relevant names from all 23 downloaded MTG archive indexes. Source availability is not runtime validation or a legal guarantee.',
            files=files,category_counts=counts,archive_entry_records=total_entries,
            relevant_assets=[dict(path=k,archives=v) for k,v in sorted(assets.items())],
            datatable_string_evidence=special)
(OUT/'MTG-file-inventory.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
summary=dict(lua_files=len(files),unique_registered_object_paths=len({v for f in files for v in f['templates']}),
             category_counts=counts,terrain_files=[k for k in sorted(assets) if k.startswith('terrain/') and k.endswith('.trn')],
             snapshot_files=[k for k in sorted(assets) if k.startswith('snapshot/')],
             player_object_files=[k for k in sorted(assets) if k.startswith('object/creature/player/')],
             notable_datatables=[dict(path=x['path'],archive=x['archive']) for x in special],
             detected_notice_files=[dict(path=x['path'],notices=x['notices']) for x in files if x['notices']])
(OUT/'MTG-inventory-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k != 'detected_notice_files'},indent=2))
