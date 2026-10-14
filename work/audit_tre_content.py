from pathlib import Path
import struct,zlib,re,json,collections
workspace=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
root=Path('/opt/swg/Core3/MMOCoreORB')
log=(workspace/'work/current-journal.txt').read_text(errors='replace')
missing=set(re.findall(r'WARNING - ([^\s]+) not found\.',log))
missing.update(re.findall(r'could not open (?:lua )?derv: ([^\s]+)',log))
missing.update(re.findall(r'AppearanceTemplate not found:([^\s]+)',log))
config=(root/'bin/conf/config.lua').read_text()
block=config.split('TreFiles = {',1)[1].split('}',1)[0]
loaded=set(re.findall(r'"([^"]+\.tre)"',block))
probes={'datatables/space/ship_chassis.iff','object/ship/base/shared_ship_base.iff','appearance/pt_light_indoor_glow.prt'}
hits={name:[] for name in sorted(missing|probes)}
stats=[];errors=[]
for group,folder in [('server',Path('/opt/swg/tre')),('original_disc',Path('/opt/swg/disc-extracted/SWG'))]:
    for p in sorted(folder.glob('*.tre')):
        try:
            with p.open('rb') as f:
                header=f.read(36)
                magic,version,count,offset,ftype,fsize,ntype,nsize,usize=struct.unpack('<4s4s7I',header)
                if magic!=b'EERT' or version!=b'5000':
                    raise ValueError(f'unsupported {magic!r} {version!r}')
                f.seek(offset)
                files=f.read(fsize if ftype==2 else count*24)
                if ftype==2:files=zlib.decompress(files)
                names=f.read(nsize if ntype==2 else usize)
                if ntype==2:names=zlib.decompress(names)
                for i in range(count):
                    record=struct.unpack_from('<6I',files,i*24)
                    start=record[5];end=names.find(b'\0',start)
                    name=names[start:end].decode('latin1')
                    if name in hits:
                        loc={'group':group,'archive':p.name,'loaded':group=='server' and p.name in loaded,'bytes':record[1]}
                        resume=f.tell();f.seek(record[2]);payload=f.read(record[4] if record[3]==2 else record[1]);f.seek(resume)
                        if record[3]==2:payload=zlib.decompress(payload)
                        loc['data_header']=repr(payload[:16])
                        hits[name].append(loc)
                stats.append({'group':group,'archive':p.name,'entries':count})
        except Exception as exc: errors.append({'archive':str(p),'error':str(exc)})
result={'missing_assets':{n:hits[n] for n in sorted(missing)},'probes':{n:hits[n] for n in sorted(probes)},'archives_scanned':len(stats),'errors':errors,'loaded_config_archives':len(loaded),'missing_config_archives':sorted(n for n in loaded if not (Path('/opt/swg/tre')/n).exists()),'scan_scope':'Version 0005 indexes; 0006 original disc archives excluded. No game or server files changed.'}
(workspace/'work/content-audit.json').write_text(json.dumps(result,indent=2))
print('Archives scanned:',len(stats),'Unsupported originals:',len(errors),'Unique warning paths:',len(missing),'Missing configured archives:',result['missing_config_archives'])
for name,locations in hits.items():
    print(name, '=>', ', '.join(x['group']+':'+x['archive']+' '+x['data_header'] for x in locations) or 'Not found in decoded archives; newer originals not assessed')
