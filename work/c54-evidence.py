import importlib.util,contextlib,io,tempfile
exec(compile(open(__file__.replace('evidence','client')).read().split('for n in [')[0],__file__,'exec'))
report={}
checks=json.loads((r/'Fable-species/s7-hutt/checks.json').read_text())
old=(r/'SWG-client/local_planets.tre.bak-20261016').read_bytes()
before=tre_write.read(old)[0]
assert hashlib.sha256(old).hexdigest()==checks['installed']['sha256']
report['s7_archive']={'sha256':hashlib.sha256((r/'Fable-species/s7-hutt/local_planets-s7.tre').read_bytes()).hexdigest(),'changed':sorted(n for n in before if entries.get(n)!=before[n]),'new':sorted(set(entries)-set(before)),'unchanged':sum(entries.get(n)==v for n,v in before.items()),'dropped':sorted(set(before)-set(entries))}
assert report['s7_archive']['unchanged']==164 and not report['s7_archive']['dropped']
assert entries['appearance/lat/hutt.lat']==(r/'Fable-species/s7-hutt/staged/client/appearance/lat/hutt.lat').read_bytes()
report['shared_species']={}
from swgfmt import trn_iff as iff
for gender in ('male','female'):
 n=f'object/creature/player/shared_hutt_{gender}.iff'
 leaf=next(x.data for _,x in iff.walk(iff.parse(get(n))) if x.tag=='XXXX' and x.data.startswith(b'species\0'))
 value=int.from_bytes(leaf[-4:],'little');assert value==4
 report['shared_species'][gender]=value
report['s7_racial_mods']=[row for row in st.read_dtii(get('datatables/creation/racial_mods.iff'))['rows'] if row[0]=='hutt_male'][0]
report['s7_racial_total']=sum(report['s7_racial_mods'][2:]);assert report['s7_racial_total']==1600
# Exercise the actual builder entry point against a disposable fake archive. Both an
# invalid cached LAT and an unrelated changed base entry are accepted by its only gate.
spec=importlib.util.spec_from_file_location('c54_s7_builder',r/'Fable-species/s7-hutt/build_test_archive.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'installed.tre').write_bytes(tre_write.pack({'keep.bin':b'original'}));(t/'hutt.lat').write_bytes(b'not an IFF')
 mod.INSTALLED=str(t/'installed.tre');mod.WORK=str(t/'work');mod.OUT_TRE=str(t/'out.tre');mod.LAT=str(t/'hutt.lat');mod.HERE=str(t)
 original_stage=mod.species_tables.stage_species
 def fake_stage(species,stage,base):
  (Path(stage)/'keep.bin').write_bytes(b'corrupted unrelated file')
  return {'files':{},'notes':[]}
 mod.species_tables.stage_species=fake_stage
 try:
  with contextlib.redirect_stdout(io.StringIO()): code=mod.main()
 finally:mod.species_tables.stage_species=original_stage
 accepted=tre_write.read((t/'out.tre').read_bytes())[0]
 assert code==0 and accepted['appearance/lat/hutt.lat']==b'not an IFF' and accepted['keep.bin']!=b'original'
 report['builder_counterexample']={'exit':code,'invalid_cached_lat_accepted':True,'unrelated_file_change_accepted':True,'input_was_disposable':True}
# C54 generation is deterministic and idempotent on its own output.
spec=importlib.util.spec_from_file_location('c54_crafting',r/'tools/build_hutt_c54_crafting.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
out,a=mod.build(entries,sp.default_base);out2,b=mod.build(out,sp.default_base)
assert out2==out and b['new_group_rows']==0
assert out['object/draft_schematic/vehicle/civilian/shared_a1_deluxe_floater.iff']!=get('object/draft_schematic/vehicle/civilian/shared_landspeeder_x34.iff')
report['c54_crafting']={'idempotent':True,'preserves_untouched_base_entries':all(out[n]==v for n,v in entries.items() if n!=mod.NAMES),'only_changed_base_entry':mod.NAMES,**a}
dest=r/'Documentation-support/hutt-c54-checks.json'
dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
