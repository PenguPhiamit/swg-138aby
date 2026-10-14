from pathlib import Path
import hashlib,json,re,zipfile
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs/Community-content'
OUT.mkdir(exist_ok=True)
MTG=BASE/'work/research/mod-the-galaxy'
paths=['MMOCoreORB/bin/scripts/object/custom_content','MMOCoreORB/bin/scripts/mobile/custom_content','MMOCoreORB/bin/scripts/screenplays/custom_screenplays']
files=[]
with zipfile.ZipFile(OUT/'MTG-published-content.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for folder in paths:
        for path in sorted((MTG/folder).rglob('*')):
            if path.is_file():
                relative=path.relative_to(MTG).as_posix()
                archive.write(path,relative)
                files.append(relative)
    for name in ['COPYING','README.md']:
        archive.write(MTG/name,name)
    # The shared-template include list is necessary before loading server definitions.
    allobjects=(MTG/'MMOCoreORB/bin/scripts/object/allobjects.lua').read_text()
    shared=[line for line in allobjects.splitlines() if 'includeFile("custom_content/' in line]
    archive.writestr('mtg-shared-template-includes.lua','\n'.join(shared)+'\n')
excluded=[];srfiles=0
SR=BASE/'work/research/sentinels-republic'
with zipfile.ZipFile(OUT/'SR-public-scripts-reference.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in (SR/'MMOCoreORB/bin/scripts').rglob('*.lua'):
        content=path.read_text(errors='replace')
        if re.search(r'proprietary|not for distribution',content,re.I):
            excluded.append(path.relative_to(SR).as_posix());continue
        archive.write(path,path.relative_to(SR).as_posix());srfiles+=1
    archive.write(SR/'COPYING','COPYING')
    archive.write(SR/'README.md','README.md')
credits='''COMMUNITY CONTENT - SOURCE AND CREDIT RECORD

Mod the Galaxy: https://github.com/ModTheGalaxy/mtgserver
Revision: 54deb619e83c2c5e353f6a825a829d56201704f0 (update-wip)
Published reuse statement: https://github.com/ModTheGalaxy/mtgserver/wiki
Credit Mod the Galaxy and the original contributors. Preserve all file notices.
Contributors and tools credited by the project/community include Lasko, Timbab,
Sytner, and the SWGEmu team. File-specific authorship should be traced through
the repository history before publishing a modified package or public website.
Original Star Wars Galaxies game assets belong to their respective rights holders;
the local installation started from the user's Complete Online Adventures disc.

Sentinel's Republic public scripts: https://github.com/swgsremu/sentinelsrepublic-server
Revision: 5df918b48f9fe011e93738c539311778906e189f
This archive is a reference collection, not an installed server replacement.
Files carrying proprietary/not-for-distribution notices are excluded from the
reusable archive. The original research checkout remains unchanged.

Sunrunner II original scripts/art and unverified Empire in Flames packages were
not collected as reusable bundles. They require an available release or permission.
No permission request was sent to another team during this task.
'''
(OUT/'CREDITS-and-sources.txt').write_text(credits)
manifest={'mtg_revision':'54deb619e83c2c5e353f6a825a829d56201704f0','mtg_published_files':len(files),'sr_reference_lua_files':srfiles,'sr_excluded_notice_files':excluded,'archives':{}}
for name in ['MTG-published-content.zip','SR-public-scripts-reference.zip']:
    path=OUT/name
    with path.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
    manifest['archives'][name]={'bytes':path.stat().st_size,'sha256':sha}
(OUT/'collection-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
