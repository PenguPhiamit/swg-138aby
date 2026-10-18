exec(compile(open(__file__.replace('client2','client')).read().split('for n in [')[0],__file__,'exec'))
t=st.read_dtii(get('datatables/crafting/schematic_group.iff'))
print('group columns',t['columns'])
groups=[]
for row in t['rows']:
 if 'landspeeder_x34' in str(row) or 'speeder_bike' in str(row): print('SPEEDERS',row); groups.extend(str(c) for c in row)
t=st.read_dtii(get('datatables/skill/skills.iff'))
for row in t['rows']:
 if row[0].startswith('crafting_artisan'): print(row[0], 'grants',row[t['columns'].index('SCHEMATICS_GRANTED')])
for n in ['hutt_male','hutt_female','chiss_male']: print(n,hex(tre_write.soe_crc('object/creature/player/shared_'+n+'.iff')))
for n in ['datatables/creation/racial_mods.iff','datatables/creation/attribute_limits.iff']:
 t=st.read_dtii(get(n));print(n,[row for row in t['rows'] if row[0] in ('human_male','wookiee_male')])
for n in sp.PTMP_TABLES[:3]:
 raw=get(n); print(n,'HUTT bytes',[(m.start(),raw[max(0,m.start()-25):m.start()+100]) for m in re.finditer(b'hutt',raw,re.I)])
