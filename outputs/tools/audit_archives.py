"""Read-only C11 checkout audit. Hash tracked materialized files; never run repository code."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
CATALOGUE=ROOT/'Content-catalogue'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    doc=json.loads((CATALOGUE/'archive-downloads.json').read_text(encoding='utf-8'))
    results=[]
    for item in doc['items']:
        if item.get('status')!='downloaded':continue
        folder=(PROJECT/item['local_path']).resolve()
        research=(PROJECT/'work/research').resolve()
        if not folder.is_relative_to(research):raise ValueError('checkout outside research directory')
        prefix=['git','-c','safe.directory='+folder.as_posix(),'-C',str(folder)]
        def git(*args):return subprocess.check_output(prefix+list(args))
        revision=git('rev-parse','HEAD').decode().strip()
        files=[x.decode('utf-8') for x in git('ls-files','-z').split(b'\0') if x]
        taken=[];absent=[];symlinks=[]
        for rel in sorted(files):
            path=folder/rel
            if path.is_symlink():symlinks.append(rel);continue
            if not path.is_file():absent.append(rel);continue
            if not path.resolve().is_relative_to(folder):raise ValueError('tracked path escaped checkout')
            taken.append({'path':rel,'bytes':path.stat().st_size,'sha256':digest(path)})
        licences=[r for r in taken if Path(r['path']).name.lower().startswith(('license','licence','copying','notice'))]
        output=CATALOGUE/(item['id']+'-checkout-sha256.json')
        output.write_text(json.dumps({'id':item['id'],'revision':revision,'files':taken,'absent_tracked_paths':absent,'symlinks_not_followed':symlinks},indent=1)+'\n',encoding='utf-8')
        results.append({'id':item['id'],'local_path':item['local_path'],'recorded_revision':item['revision_or_version'],'actual_revision':revision,'revision_matches':revision==item['revision_or_version'],'materialized_files':len(taken),'materialized_bytes':sum(r['bytes'] for r in taken),'absent_tracked_count':len(absent),'symlinks_not_followed':symlinks,'licence_files':licences,'manifest_path':str(output.relative_to(ROOT)),'manifest_sha256':digest(output),'tracked_changes':git('diff','--name-only').decode().splitlines(),'staged_changes':git('diff','--cached','--name-only').decode().splitlines(),'recorded_license_verified':item.get('license_verified',False)})
        print(item['id'], 'pin='+str(results[-1]['revision_matches']),len(taken),'files;',len(absent),'sparse/absent;',len(licences),'licence/notice files',flush=True)
    (CATALOGUE/'archive-checkout-audit.json').write_text(json.dumps({'scope':'Local pinned source bytes only; no repo code executed, no install or import permission inferred','items':results},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()

