from pathlib import Path
import concurrent.futures, hashlib, json, sys, time
sys.path.insert(0,str(Path(__file__).parent/'python-deps'))
import gdown

ROOT=Path(__file__).resolve().parents[1]/'outputs/Community-content/MTG-assets'
ROOT.mkdir(parents=True,exist_ok=True)
FILES=[
('mtg_patch_001_appearance_01.tre','1KGSrUfAH6OBODZSRZrchYt67O2Sa59nk'),
('mtg_patch_002_appearance_02.tre','18u1JmIduIfqn0-4WoTxrasFbeIEjOIJ7'),
('mtg_patch_003_appearance_03.tre','1s6Ejz4jhkN9HOQxUHbndygsvE5kL2A8w'),
('mtg_patch_004_appearance_04.tre','1yCt_Gbw-BMmVlQ7LLV0X-hID6Sne2JoU'),
('mtg_patch_005_texture_01.tre','1GH-RmG7S78RQ3khf2nvMHWIcxJyxIHP1'),
('mtg_patch_006_texture_02.tre','1zKA6MmIR-ScdQ33qiZOxo2GC3jM6TCrc'),
('mtg_patch_007_texture_03.tre','1WrwWgSoYwTYzKM09rz07Dt00IuC6rdjt'),
('mtg_patch_008_texture_04.tre','1PZQrUIekbchfbXVXkLdCJBUAKqo3Jffu'),
('mtg_patch_009_Shader_01.tre','1pNlR-QHIyla2PzrPYUkQYLI5qDH6Jkt5'),
('mtg_patch_010_object_01.tre','1X6hIJBB41LsAtFX5x8nXoiMPsassLXNm'),
('mtg_patch_011_files_01.tre','1L8Jk2nKulOTApt0zehbBlOdbuPAZJNUn'),
('mtg_patch_012_configurable_01.tre','1uRndiW_mxpROcznDnyTslfjtnqGj21KB'),
('mtg_patch_013_configurable_02.tre','1jdDfphHGauFnp3IsdF9AEP3kabnLZTsd'),
('mtg_patch_014.tre','1jfpTOGbyb4JPeFvhO8ltne028EzMQXO9'),
('mtg_patch_015.tre','1HizJ8XITig52FkHe2rHs3gPmFSViVSne'),
('mtg_patch_016.tre','1X25Xpc9aMSpqc0ruMXqCwjXwc2roXpiA'),
('mtg_patch_017.tre','1IcKbJy38-7EfjmQCwnHcynakcDGJCD8B'),
('mtg_patch_018.tre','17dcHEzPicHa5J55iVfuLt5YAlaWrZKpp'),
('mtg_patch_019.tre','19iMfHqgth8ywBYRNYu9dUlcjoQB0V6jL'),
('mtg_patch_021.tre','1PFM5IkmPI-26F6hdFUFN-tLhbkQ1D1IG'),
('mtg_patch_022.tre','1GfMPantV4VrORGfzJRW071dSpBNVi3Lc'),
('mtg_patch_023.tre','1JoY1bfRMr-rJpVh6IqhgR736D8JpwnMr'),
('mtg_planets.tre','1irK5g12IBd8-IKcYV0fyVTIYyGsP6i-h')]

def one(entry):
    name,ident=entry
    path=ROOT/name
    try:
        if not path.exists():
            downloaded=gdown.download(id=ident,output=str(path),quiet=True)
            if not downloaded:
                raise RuntimeError('Download was not supplied by the public host.')
        with path.open('rb') as stream:
            header=stream.read(8)
            if header!=b'EERT5000':
                raise RuntimeError('Downloaded file is not a pre-CU-readable TRE archive: '+repr(header))
            stream.seek(0)
            digest=hashlib.file_digest(stream,'sha256').hexdigest()
        print('Collected '+name+' ('+str(path.stat().st_size)+' bytes)',flush=True)
        return {'name':name,'public_drive_id':ident,'bytes':path.stat().st_size,'sha256':digest,'status':'downloaded'}
    except Exception as exc:
        print('Unavailable '+name+': '+str(exc)[:140],flush=True)
        return {'name':name,'public_drive_id':ident,'status':'unavailable','reason':str(exc)[:500]}

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(one,FILES))
(ROOT/'manifest.json').write_text(json.dumps({'publisher':'Mod the Galaxy','source_folder':'https://drive.google.com/drive/folders/1yuJ26kdARCjXxpajgkv6EQaEEIanHD66','files':results},indent=2))
print('Downloaded '+str(sum(x['status']=='downloaded' for x in results))+' of '+str(len(results))+' archives.',flush=True)
