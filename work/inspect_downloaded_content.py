from pathlib import Path
import hashlib,json,re,zipfile
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs/Content-catalogue'
DOWNLOADS=Path('C:/Users/Pengw/Downloads')
result=[]
for filename in ['newspecies.zip','zeltros_client.zip','zeltros_server.zip','Borries_Wall_Pack_Vol1.zip',"Abi's Lamp Pack.zip",'BorriesLightMegapack_1_1.zip','multipassenger.zip','Borries_Torch_Pack_1.1.zip','SWG_Borries_Kitchen_Pack_v05.zip','BorriesNabooStructurePack_1_0.zip','BorriesWearableRankPlates_V1.zip','newsnet.zip','betterAstromechs.zip']:
    p=DOWNLOADS/filename
    if not p.exists():continue
    data=p.read_bytes()
    try:
        with zipfile.ZipFile(p) as z:
            files=[n for n in z.namelist() if not n.endswith('/')]
            notices=[]
            for n in files:
                if n.lower().endswith(('.lua','.cpp','.h','.md','.txt')) or any(s in n.lower() for s in ['license','copying','readme','credit']):
                    text=z.read(n).decode('utf-8',errors='replace')
                    terms=[l.strip() for l in text.splitlines() if re.search(r'copyright|proprietary|not for distribution|all rights reserved|licen[cs]e|creative commons|redistribut|credit',l,re.I)]
                    if terms:notices.append(dict(path=n,terms=terms))
            target=OUT/('newspecies-original.zip' if filename=='newspecies.zip' else filename)
            if not target.exists():target.write_bytes(data)
            result.append(dict(name=filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),files=files,notices=notices,source='Halyn MTG species release' if filename=='newspecies.zip' else 'tienvogh MTG Zeltros release' if filename.startswith('zeltros') else 'Original creator MTG resource',executed=False))
    except zipfile.BadZipFile:
        print('Not a complete ZIP yet:',filename)
(OUT/'downloaded-package-evidence.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for r in result:
    unique_terms=sorted({t for n in r['notices'] for t in n['terms'] if not t.startswith('--') and ('repack' in t.lower() or 'redistrib' in t.lower() or 'credit' in t.lower())})
    print(json.dumps(dict(name=r['name'],bytes=r['bytes'],sha256=r['sha256'],file_count=len(r['files']),notice_files=[n for n in r['files'] if any(s in n.lower() for s in ['readme','license','credit','copying'])],distinct_reuse_terms=unique_terms[:8]),indent=2))
