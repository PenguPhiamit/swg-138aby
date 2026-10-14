"""C22 read-only review probes: pinned source, cave floor geometry, camps, isolated archive checks.
Run from Windows: python -I outputs/Documentation-support/review-C22/check_c22.py
No builds, server changes, bot commands, downloads, or production archive writes.
Uses the project's existing IFF/TRE/terrain readers; derives floor triangles from Core3's
CellProperty.cpp and FloorMesh.cpp (de1b679a). Game bytes stay local and are not copied here.
"""
import sys,re,json,struct,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'outputs/Fable-hoth-caves/tools'))
import ws_read
from trn_iff import parse,load,walk,Reader,build
nodes,_=ws_read.read_ws(load('tre:mtg_planets.tre:snapshot/hoth.ws'))
byid={n['id']:n for n in nodes}
import subprocess, tempfile, contextlib, io, types

def show(commit, path):
    return subprocess.check_output(['wsl','-d','Debian','-u','swgemu','--','git','-C',
                                    '/opt/swg/Core3-dev','show',commit+':'+path])

cave_source=show('c5f1ae06','MMOCoreORB/bin/scripts/screenplays/caves/hoth_ice_caves.lua')
rows=[]
for ln,line in enumerate(cave_source.decode().splitlines(),1):
 if 'spawnMobile(' not in line:continue
 args=json.loads('['+line.split('(',1)[1].rsplit(')',1)[0]+']')
 rows.append(dict(line=ln,template=args[1],x=args[3],z=args[4],y=args[5],cell=args[7]))
def find(root,name):return [n for _,n in walk(root) if n.form==name or n.tag==name]
cache={};results=[];inputs={}
for row in rows:
 cell=byid[row['cell']]; cave=byid[cell['parent']]
 obj=cave['template']; data=load('client:'+obj)
 pob=re.search(rb'appearance/[^\x00]+\.pob',data).group().decode()
 if pob not in cache:
  blob=load('client:'+pob); tree=parse(blob);assert build(tree)==blob
  inputs[pob]=hashlib.sha256(blob).hexdigest()
  cells=find(tree,'CELS')[0].children
  parsed=[]
  for c in cells:
   d=c.children[0].children[0];assert d.tag=='DATA'
   r=Reader(d.data);portals=r.i32();r.u8();name=r.cstr();mesh=r.cstr();has=r.u8();floor=r.cstr() if has else None
   parsed.append((name,floor))
  cache[pob]=parsed
 name,floor=cache[pob][cell['cell_index']]
 if not floor:raise RuntimeError((row,cell,name))
 if floor not in cache:
  fb=load('client:'+floor); ft=parse(fb);assert build(ft)==fb
  inputs[floor]=hashlib.sha256(fb).hexdigest()
  v=find(ft,'VERT')[0].data;t=find(ft,'TRIS')[0].data;ver=ft[0].children[0].form
  if ver=='0006':
   nv=struct.unpack_from('<I',v)[0];nt=struct.unpack_from('<I',t)[0];v=v[4:];t=t[4:]
  else:nv=len(v)//12;nt=len(t)//60
  assert len(v)==nv*12 and len(t)==nt*60
  vs=list(struct.iter_unpack('<fff',v));ts=[struct.unpack_from('<iii',t,i*60) for i in range(nt)]
  assert all(0<=k<nv for tri in ts for k in tri)
  cache[floor]=(vs,ts)
 vs,ts=cache[floor];heights=[]
 for tri in ts:
  a,b,c=[vs[k] for k in tri]
  ax,az,ay=a;bx,bz,by=b;cx,cz,cy=c
  den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-8:continue
  u=((by-cy)*(row['x']-cx)+(cx-bx)*(row['y']-cy))/den
  v=((cy-ay)*(row['x']-cx)+(ax-cx)*(row['y']-cy))/den
  w=1-u-v
  if min(u,v,w)>=-1e-5:heights.append(u*az+v*bz+w*cz)
 dz=min((abs(z-row['z']) for z in heights),default=None)
 results.append(dict(row,building=cave['id'],cell_index=cell['cell_index'],cell_name=name,floor=floor,heights=heights,nearest_height_delta=dz))
out=dict(rows=len(rows),distinct_cells=len({r['cell'] for r in rows}),no_triangle=[r for r in results if not r['heights']],over_1m=[r for r in results if r['nearest_height_delta'] is not None and r['nearest_height_delta']>1],max_delta=max(r['nearest_height_delta'] or 0 for r in results),inputs=inputs,results=results)
# Keep only derived measurements and input hashes, never game asset bytes.
summary={k:v for k,v in out.items() if k != 'results'}
summary['cave_script_sha256']=hashlib.sha256(cave_source).hexdigest()

camp_source=show('de1b679a','MMOCoreORB/bin/scripts/screenplays/poi/hoth_camps.lua').decode()
sys.path.insert(0,str(H/'outputs/Fable-hoth-batchA/tools'))
import hoth_survey
terrain=hoth_survey.evaluator()
positions=[]
for ln,line in enumerate(camp_source.splitlines(),1):
    if 'spawnMobile(' not in line and 'spawnSceneObject(' not in line: continue
    args=json.loads('['+line.split('(',1)[1].rsplit(')',1)[0]+']')
    mob='spawnMobile(' in line
    x,z,y=args[3:6] if mob else args[2:5]
    assert abs(x)<7640 and abs(y)<7640
    positions.append(dict(line=ln,mobile=mob,x=x,y=y,z=z,ground=terrain.height(x,y)))
summary['camps']=dict(mobiles=sum(p['mobile'] for p in positions),props=sum(not p['mobile'] for p in positions),
                      maximum_ground_delta=max(abs(p['z']-p['ground']) for p in positions),
                      off_map=0,
                      degrees_passed_to_scene_heading=[p['line'] for p in positions if not p['mobile'] and
                         abs(json.loads('['+camp_source.splitlines()[p['line']-1].split('(',1)[1].rsplit(')',1)[0]+']')[-1])>6.2832])

# Read a narrow set of registrations in one WSL invocation; every source read uses git show.
remote = """import subprocess,json
root='/opt/swg/Core3-dev'
names=subprocess.check_output(['git','-C',root,'ls-tree','-r','--name-only','de1b679a','MMOCoreORB/bin/scripts/mobile']).decode().splitlines()
selected=[p for p in names if '/hoth/' in p or p.endswith(('/junk_dealer.lua','/imperial_recruiter.lua','/rebel_recruiter.lua')) or (p.endswith('serverobjects.lua') and ('/lair/' in p or p.endswith('/mobile/serverobjects.lua') or p.endswith('/mobile/spawn/serverobjects.lua')))]
print(json.dumps({p:subprocess.check_output(['git','-C',root,'show','de1b679a:'+p]).decode() for p in selected}))
"""
content=json.loads(subprocess.check_output(['wsl','-d','Debian','-u','swgemu','--','python3','-'],input=remote.encode()))
mobile_names=set();lair_names=set();group_names=set()
for path,text in content.items():
    mobile_names.update(re.findall(r'addCreatureTemplate\([^,]+,\s*"([^"]+)"',text))
    lair_names.update(re.findall(r'addLairTemplate\("([^"]+)"',text))
    group_names.update(re.findall(r'addSpawnGroup\("([^"]+)"',text))
used_mobiles={row['template'] for row in rows}
used_mobiles.update(json.loads('['+line.split('(',1)[1].rsplit(')',1)[0]+']')[1]
                    for line in camp_source.splitlines() if 'spawnMobile(' in line)
used_lairs=set()
for path,text in content.items():
    if '/spawn/hoth/' in path:
        used_lairs.update(re.findall(r'lairTemplateName\s*=\s*"([^"]+)"',text))
    if '/lair/' in path and '/hoth/' in path:
        mobile_section=text.split('mobiles =',1)[1].split('spawnLimit',1)[0]
        used_mobiles.update(re.findall(r'"(hoth_[^"]+)"',mobile_section))
assert not used_mobiles-mobile_names and not used_lairs-lair_names
for path in content:
    if '/lair/' in path and '/hoth/' in path:
        rel=path.split('/mobile/',1)[1]
        assert any('includeFile("'+rel+'")' in text for p,text in content.items() if p.endswith('serverobjects.lua')),rel
regions=show('69eb77fe','MMOCoreORB/bin/scripts/managers/planet/hoth_regions.lua').decode()
areas=[]
for line in regions.splitlines():
    m=re.search(r'\{"(hoth_[^"]+)", ([-\d]+), ([-\d]+), \{CIRCLE, (\d+)\}, SPAWNAREA, \{"([^"]+)"\}, (\d+)\}',line)
    if m:
        name,x,y,r,group,limit=m.groups();x,y,r,limit=map(int,[x,y,r,limit])
        assert group in group_names
        assert abs(x)+r<7640 and abs(y)+r<7640
        assert (x*x+(y+2000)**2)**.5-r>300
        assert ((x+400)**2+(y-2600)**2)**.5-r>450
        areas.append(dict(name=name,x=x,y=y,radius=r,group=group,limit=limit))
assert len(areas)==8
pairs=[]
for i,a in enumerate(areas):
    for b in areas[i+1:]:
        distance=((a['x']-b['x'])**2+(a['y']-b['y'])**2)**.5
        if distance<a['radius']+b['radius']:
            pairs.append(dict(a=a['name'],b=b['name'],overlap_along_centres=round(a['radius']+b['radius']-distance,2)))
summary['registrations']=dict(distinct_used_mobiles=len(used_mobiles),distinct_used_lairs=len(used_lairs),missing=[],area_groups=6)
summary['regions']=dict(areas=areas,area_limit=sum(a['limit'] for a in areas),overlapping_pairs=pairs,
                       clears_map_edges_and_outpost_300m_and_caves_450m=True,
                       area_flags='SPAWNAREA only; world spawns also eligible')
# Compare actual appearance chains; plain rancor has a static shader, hue variant has the palette.
chains={}
for kind in ['','_hue']:
    paths=['object/mobile/shared_rancor'+kind+'.iff','appearance/rancor'+kind+'.sat',
           'appearance/mesh/rancor'+kind+'.lmg','appearance/mesh/rancor'+kind+'_l0.mgn',
           'shader/rancor_asb13.sht' if not kind else 'shader/rancor_hue_hcsb21.sht']
    blobs=[load('client:'+path) for path in paths]
    assert all(paths[i+1].encode() in blobs[i] for i in range(len(paths)-1))
    chains[kind or 'plain']=dict(paths=paths,sha256=[hashlib.sha256(b).hexdigest() for b in blobs],
                                  has_rancor_palette=b'palette/creature_rancor.pal' in blobs[-1],
                                  shader_form=parse(blobs[-1])[0].form)
assert not chains['plain']['has_rancor_palette'] and chains['_hue']['has_rancor_palette']
summary['rancor_appearance']=chains
assert not summary['no_triangle'] and not summary['over_1m']
assert summary['camps']['maximum_ground_delta']<.051

# Pin the reviewed builder, redirect every build write into a private temporary directory.
builder_source=subprocess.check_output(['git','show','f0b192e:outputs/tools/hoth/hoth_client_build.py'])
mod=types.ModuleType('c22_pinned_builder')
mod.__file__=str(H/'outputs/tools/hoth/hoth_client_build.py')
exec(compile(builder_source,mod.__file__,'exec'),mod.__dict__)
order=mod.swg_client_data.clo.load_order
try:
    trees,other,top=order()
    mod.swg_client_data.clo.load_order=lambda: ([(999,'local_planets.tre'),*trees],other,top)
    mod._stock_index=None
    selected=mod.winning('datatables/skill/skills.iff')[0]
    assert selected.lower()!='local_planets.tre'
finally:
    mod.swg_client_data.clo.load_order=order
protected=Path(mod.STAGE)
paths=['datatables/skill/skills.iff',*mod.BOTANIST_STRINGS]
before={p:hashlib.sha256((protected/p).read_bytes()).hexdigest() for p in paths}
with tempfile.TemporaryDirectory(prefix='c22-') as td:
    scratch=Path(td).resolve()
    mod.STAGE=str(scratch/'stage');mod.BASE=str(scratch/'base')
    for p in paths:
        target=Path(mod.src(p));target.parent.mkdir(parents=True,exist_ok=True)
        _,blob=mod.winning(p);target.write_bytes(blob)
    mod.botanist()
    first={p:hashlib.sha256(Path(mod.dst(p)).read_bytes()).hexdigest() for p in paths}
    mod.botanist()
    second={p:hashlib.sha256(Path(mod.dst(p)).read_bytes()).hexdigest() for p in paths}
    assert first==second==before
    # Exercise main's actual failure/publication branch with deliberately mismatched synthetic bytes.
    for fn in ['strings','crc_table','travel','waypoints','ticket_ui','planet_map_ui']:
        setattr(mod,fn,lambda: None)
    for fn in ['object_crc_table','resource_tree','botanist']:
        setattr(mod,fn,lambda: [])
    mod.check_ui_newlines=lambda p: True
    final=scratch/'publish-stage';final.mkdir();(final/'sentinel').write_bytes(b'old stage')
    tre=scratch/'publish.tre';tre.write_bytes(b'old archive')
    mod.STAGE=str(final);mod.TRE=str(tre)
    def fake_pack(stage,out):
        p=Path(stage);p.mkdir();(p/'fixture').write_bytes(b'expected')
        Path(out).write_bytes(b'bad')
    old_pack=mod.tre_pack.pack
    try:
        mod.tre_pack.pack=fake_pack
        mod.read_tre=lambda _: [dict(name='fixture',offset=0,comp_size=0,comp=0,size=3)]
        mod._inflate=lambda blob,*_: blob
        src=Path(mod.src('fixture'));src.write_bytes(b'expected')
        with contextlib.redirect_stdout(io.StringIO()): result=mod.main()
        assert result==1 and tre.read_bytes()==b'old archive' and (final/'sentinel').read_bytes()==b'old stage'
    finally: mod.tre_pack.pack=old_pack
assert before=={p:hashlib.sha256((protected/p).read_bytes()).hexdigest() for p in paths}
summary['archive_fix']=dict(commit='f0b192e',source_sha256=hashlib.sha256(builder_source).hexdigest(),
    skill_source_with_own_archive_first=selected,two_botanist_outputs_identical=True,
    matches_installed_botanist_staging=True,protected_staging_unchanged=True,
    synthetic_verification_failure_preserves_prior_stage_and_archive=True,
    full_archive_pack_or_publish=False)
(HERE/'offline-results.json').write_bytes((json.dumps(summary,indent=2)+'\n').replace('\n','\r\n').encode())
print(json.dumps({k:v for k,v in summary.items() if k!='inputs'},indent=2))
