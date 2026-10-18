exec(compile(open(__file__.replace('review-extra','client')).read().split('for n in [')[0],__file__,'exec'))
from swgfmt import trn_iff as iff
import struct
for n in ['object/creature/player/shared_hutt_male.iff','object/creature/player/shared_hutt_female.iff']:
 print(n)
 for _,node in iff.walk(iff.parse(get(n))):
  if node.tag=='XXXX' and any(node.data.startswith(k+b'\0') for k in [b'species',b'speed',b'gender',b'appearanceFilename',b'animationMapFilename']): print(repr(node.data))
import acst
t=acst.read_acst(get('customization/asset_customization_manager.iff'))
for sat in sp.SPECIES['hutt']['sat']:
 print('ACST',sat,acst.lookup(t,sat))
for n in ['datatables/mount/mount_table.iff','datatables/mount/valid_scale_range.iff']:
 try:
  t=st.read_dtii(get(n)); print(n,t['columns'],[row for row in t['rows'] if 'floater' in str(row)])
 except Exception as e:print(e)
