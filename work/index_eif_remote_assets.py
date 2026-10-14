"""Read only public TRE headers/indexes via bounded HTTP range requests."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,struct,urllib.parse,urllib.request,zlib

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs/Content-catalogue/EiF-Uprising'
REV='5f97c7983d2ab950255113f9ae96447b3526f454'
manifest=json.loads((BASE/'work/research/eif-patch-manifest.json').read_text(encoding='utf-8-sig'))
patches=[p['name'] for p in manifest['required'] if p['name'].endswith('.tre')]+['starsider45.tre']
def read_range(url,start,length):
    if length>12_000_000:raise ValueError('Unexpectedly large index')
    request=urllib.request.Request(url,headers={'Range':f'bytes={start}-{start+length-1}','User-Agent':'SWG-local-content-research/1.0'})
    with urllib.request.urlopen(request,timeout=25) as response:
        if response.status!=206:raise ValueError(f'Range not honored: {response.status}')
        raw=response.read(length+1)
        if len(raw)!=length:raise ValueError(f'Wrong length: {len(raw)} vs {length}')
        return raw,response.headers.get('Content-Range','')
def index(name):
    url='https://gitlab.com/api/v4/projects/EiF-Public%2Fpatch-files/repository/files/'+urllib.parse.quote('assets/'+name,safe='')+'/raw?ref='+REV
    raw,content_range=read_range(url,0,36)
    magic,version,count,offset,ftype,fsize,ntype,nsize,usize=struct.unpack('<4s4s7I',raw)
    if (magic,version)!=(b'EERT',b'5000'):raise ValueError('Unsupported archive header')
    records_len=fsize if ftype==2 else count*24
    names_len=nsize if ntype==2 else usize
    payload,_=read_range(url,offset,records_len+names_len)
    records=payload[:records_len]; names=payload[records_len:]
    if ftype==2:records=zlib.decompress(records)
    if ntype==2:names=zlib.decompress(names)
    entries=[]
    for i in range(count):
        record=struct.unpack_from('<6I',records,i*24)
        start=record[5];end=names.find(b'\0',start)
        entries.append(dict(path=names[start:end].decode('latin1'),bytes=record[1]))
    return dict(name=name,revision=REV,url=url,in_manifest=name!='starsider45.tre',entry_count=count,
                total_archive_bytes=int(content_range.split('/')[-1]),index_bytes_read=36+len(payload),
                index_sha256=hashlib.sha256(raw+payload).hexdigest(),entries=entries,asset_payloads_downloaded=False)
results=[];errors=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    jobs={pool.submit(index,name):name for name in patches}
    for job in as_completed(jobs):
        name=jobs[job]
        try:
            data=job.result();results.append(data)
            print(f"Indexed {name}: {data['entry_count']} paths; {data['index_bytes_read']} bytes read",flush=True)
        except Exception as ex:
            errors.append(dict(name=name,error=str(ex)));print(f'Could not index {name}: {ex}',flush=True)
results.sort(key=lambda r:r['name'])
audit=json.loads((OUT/'eif-source-audit.json').read_text())
by_path={}
for archive in results:
    for item in archive['entries']:by_path.setdefault(item['path'],[]).append(archive['name'])
evidence=[]
for species in audit['species']:
    evidence.append(dict(key=species['key'],name=species['name'],models=[dict(shared_template=m['shared_template'],archives=by_path.get(m['shared_template'],[])) for m in species['models']]))
result=dict(researched='2026-10-13',repository='https://gitlab.com/EiF-Public/patch-files',revision=REV,
            scope='Public archive index names only; no asset payloads extracted or installed. Index presence does not establish reuse permission, correct dependencies, client load priority or gameplay.',
            archives=results,errors=errors,species_evidence=evidence,
            terrains=sorted(k for k in by_path if k.startswith('terrain/') and k.endswith('.trn')),
            snapshots=sorted(k for k in by_path if k.startswith('snapshot/')),
            bytes_read=sum(r['index_bytes_read'] for r in results),server_changes=False)
(OUT/'EiF-public-asset-index.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(archives=len(results),errors=errors,bytes_read=result['bytes_read'],
                     species_all_templates_found=sum(all(m['archives'] for m in s['models']) for s in evidence),
                     terrains=result['terrains']),indent=2),flush=True)
