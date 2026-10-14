from pathlib import Path
import hashlib,json,os,pwd,re,shutil,subprocess,zipfile

BASE=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
ROOT=Path('/opt/swg/Core3/MMOCoreORB')
OUT=BASE/'outputs'
LIB=OUT/'Community-content'
manifest=json.loads((LIB/'MTG-assets/manifest.json').read_text())
if any(x['status']!='downloaded' for x in manifest['files']):raise RuntimeError('MTG asset set incomplete.')
if subprocess.run(['pgrep','-x','core3'],stdout=subprocess.DEVNULL).returncode==0:raise RuntimeError('Install only while galaxy is stopped.')
uid=pwd.getpwnam('swgemu').pw_uid;gid=pwd.getpwnam('swgemu').pw_gid
with zipfile.ZipFile(LIB/'MTG-published-content.zip') as archive:
    for name in archive.namelist():
        if not name.startswith('MMOCoreORB/bin/scripts/'):
            continue
        target=ROOT/Path(name).relative_to('MMOCoreORB')
        if not target.resolve().is_relative_to((ROOT/'bin/scripts').resolve()):raise RuntimeError('Unexpected package path.')
        if target.exists():raise RuntimeError('Content target already exists: '+str(target))
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(archive.read(name));os.chown(target,uid,gid)
    includes=archive.read('mtg-shared-template-includes.lua').decode()

def append(rel,text):
    path=ROOT/rel
    content=path.read_text()
    if text.strip() in content:raise RuntimeError('Content loader already present: '+rel)
    path.write_text(content+'\n-- Mod the Galaxy published content. See Community-content/CREDITS-and-sources.txt.\n'+text+'\n')

append('bin/scripts/object/allobjects.lua',includes)
append('bin/scripts/object/serverobjects.lua','includeFile("custom_content/serverobjects.lua")')
append('bin/scripts/mobile/serverobjects.lua','includeFile("custom_content/serverobjects.lua")')
append('bin/scripts/mobile/conversations.lua','includeFile("custom_content/conversations.lua")')

quest=ROOT/'bin/scripts/screenplays/custom_screenplays/the_tutorial/the_tutorial_0001_the_beginning.lua'
text=quest.read_text()
text=text.replace('1, -10.5, -0.9, 24.3, 179, 1082883','1, 3565, 5, -4795, 180, 0')
text=text.replace('1, -8.4, -0.9, 22.9, -103, 1082883','1, 3568, 5, -4795, 180, 0')
text=text.replace('self:setMoodString(pHan, "npc_sitting_chair")','if pHan ~= nil then self:setMoodString(pHan, "npc_standing_drinking") end')
text=text.replace('self:setMoodString(pChewie, "npc_sitting_chair")','if pChewie ~= nil then self:setMoodString(pChewie, "npc_standing_drinking") end')
quest.write_text('-- Adapted from the published MTG tutorial; NPC positions moved outdoors for this sandbox.\n'+text)
append('bin/scripts/screenplays/screenplays.lua','includeFile("custom_screenplays/screenplays.lua")')

# Inventory objects and draft schematics can be selected from nested builder menus.
items={}
for path in (ROOT/'bin/scripts/object/custom_content').rglob('*.lua'):
    content=path.read_text(errors='replace')
    for item in re.findall(r'ObjectTemplates:addTemplate\([^\n]*?,\s*"([^"]+)"\)',content):
        if not item.startswith(('object/tangible/','object/weapon/','object/draft_schematic/')):continue
        parts=item.removeprefix('object/').removesuffix('.iff').split('/')
        node=items
        for part in parts[:-1]:node=node.setdefault(part,{})
        node[parts[-1]]=item
def quoted(s):return json.dumps(s,ensure_ascii=True)
def menu(tree):
    result=[]
    for name,value in sorted(tree.items()):
        result.append(quoted(name.replace('_',' ').title()))
        result.append(menu(value) if isinstance(value,dict) else quoted(value))
    return '{'+',\n'.join(result)+'}'
catalog=ROOT/'bin/scripts/object/sandbox/mtg_catalog.lua'
catalog.parent.mkdir(exist_ok=True)
catalog.write_text('-- Published Mod the Galaxy objects, grouped for local sandbox access.\nlocal mtgMenu = '+menu(items)+'\ntable.insert(object_tangible_terminal_terminal_character_builder.itemList, 1, mtgMenu)\ntable.insert(object_tangible_terminal_terminal_character_builder.itemList, 1, "MTG Content Library")\n')
os.chown(catalog,uid,gid)
terminal=ROOT/'bin/scripts/object/tangible/terminal/terminal_character_builder.lua'
content=terminal.read_text()
needle='ObjectTemplates:addTemplate(object_tangible_terminal_terminal_character_builder,'
if content.count(needle)!=1:raise RuntimeError('Unexpected character builder definition.')
terminal.write_text(content.replace(needle,'includeFile("sandbox/mtg_catalog.lua")\n\n'+needle))

names=[entry['name'] for entry in manifest['files']]
ordered=['mtg_patch_023.tre','mtg_patch_022.tre','mtg_planets.tre','mtg_patch_021.tre']+[name for name in reversed(names) if name not in {'mtg_patch_023.tre','mtg_patch_022.tre','mtg_planets.tre','mtg_patch_021.tre'}]
for name in names:
    source=LIB/'MTG-assets'/name
    for dest in (Path('/opt/swg/tre')/name, OUT/'SWG-client'/name):
        if dest.exists():raise RuntimeError('Asset destination exists: '+str(dest))
        shutil.copy2(source,dest)
        if dest.stat().st_size!=source.stat().st_size:raise RuntimeError('Asset copy incomplete.')
        if str(dest).startswith('/opt/'):
            os.chown(dest,uid,gid)
    print('Installed matching archive '+name,flush=True)
config=ROOT/'bin/conf/config-local.lua'
content=config.read_text()+'\n-- MTG additions use lower priority than the original pre-CU files.\n'
for name in ordered:content+='table.insert(Core3.TreFiles, '+quoted(name)+')\n'
config.write_text(content);config.chmod(0o600)
live=OUT/'SWG-client/swgemu_live.cfg'
content=live.read_text()
content=re.sub(r'(maxSearchPriority\s*=\s*)(\d+)',lambda m:m[1]+str(int(m[2])+24),content)
content=re.sub(r'(searchTree_\d+_)(\d+)',lambda m:m[1]+str(int(m[2])+24),content)
content+='\n; MTG additional assets below the pre-CU archive priorities.\n'
for priority,name in zip(range(23,0,-1),ordered):content+='\tsearchTree_00_'+str(priority)+'='+name+'\n'
live.write_text(content)

# Check syntax without executing the content in a separate interpreter.
lua_files=list((ROOT/'bin/scripts/object/custom_content').rglob('*.lua'))+list((ROOT/'bin/scripts/mobile/custom_content').rglob('*.lua'))+list((ROOT/'bin/scripts/screenplays/custom_screenplays').rglob('*.lua'))+[catalog]
syntax_errors=[]
for path in lua_files:
    # Several reference/tutorial files may not be runtime entry points. Report any syntax issue.
    result=subprocess.run(['luac5.3','-p',str(path)],capture_output=True,text=True)
    if result.returncode:syntax_errors.append({'file':str(path.relative_to(ROOT)), 'error':result.stderr.strip()})
if syntax_errors:
    (OUT/'Community-content/lua-syntax-errors.json').write_text(json.dumps(syntax_errors,indent=2))
    raise RuntimeError('Published content contains '+str(len(syntax_errors))+' Lua syntax errors; repair before starting.')
for folder in (ROOT/'bin/scripts/object/custom_content',ROOT/'bin/scripts/mobile/custom_content',ROOT/'bin/scripts/screenplays/custom_screenplays',catalog.parent):
    for path in folder.rglob('*'):
        os.chown(path,uid,gid)
    os.chown(folder,uid,gid)
record={'asset_archives_installed':len(names),'asset_load_order':'Original pre-CU first, MTG fallback second, on both server and client','lua_files_syntax_checked':len(lua_files),'inventory_catalog_entries':sum(1 for line in catalog.read_text().splitlines() if '"object/' in line),'example_quest':'MTG The Beginning; Han and Chewbacca at 3565/-4795 and 3568/-4795 Tatooine, outside','new_planets_enabled':False,'source':'54deb619e83c2c5e353f6a825a829d56201704f0','runtime_test_pending':True}
(OUT/'SWG-community-install.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
