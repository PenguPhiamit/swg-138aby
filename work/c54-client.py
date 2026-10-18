import sys,json,re,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1]/'outputs'
sys.path[:0]=[str(r/'tools'),str(r/'Fable-species/s4/tools')]
from swgfmt import tre_write
import species_tables as sp
st=sp.st
entries=tre_write.read((r/'Fable-species/s7-hutt/local_planets-s7.tre').read_bytes())[0]
def get(n): return entries[n] if n in entries else sp.default_base(n)
for n in ['datatables/creation/racial_mods.iff','datatables/creation/attribute_limits.iff','datatables/skill/skills.iff']:
 t=st.read_dtii(get(n)); print(n,t['columns'])
 for row in t['rows']:
  if any('hutt' in str(c).lower() for c in row) or (n.endswith('skills.iff') and row[0].startswith('crafting_artisan') and 'vehicle' in str(row)): print(row)
for n in ['string/en/player_species.stf','string/en/skl_n.stf','string/en/skl_d.stf']:
 print(n,[(k,v) for k,v in st.stf_items(st.read_stf(get(n))) if 'hutt' in k])
print('UI',re.findall(r'<Data\b[^>]*Name=\'hutt\'[^>]*/>',get('ui/ui_avatardata.inc').decode('latin1')))
for n in sp.PTMP_TABLES:
 tree=sp.parse(get(n))[0].children[0]
 print(n,[(c.form,sp.build([c]).decode('latin1')) for c in tree.children if b'hutt' in sp.build([c])])
from trn_iff import client_index
idx=client_index()
print('FLOATER client paths',[(n,str(v)[:240]) for n,v in idx.items() if 'a1_deluxe_floater' in n])
for n in ['datatables/mount/mount_appearance_map.iff','datatables/mount/rider_pose_map.iff','datatables/mount/saddle_appearance_map.iff','datatables/mount/saddle_hardpoint_map.iff']:
 try:
  t=st.read_dtii(get(n)); print(n,t['columns'],[row for row in t['rows'] if 'floater' in str(row)])
 except Exception as e: print(n,str(e))
