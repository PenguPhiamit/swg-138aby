exec(compile(open(__file__.replace('leaf','client')).read().split('for n in [')[0],__file__,'exec'))
from swgfmt import trn_iff as iff
for n in ['object/draft_schematic/vehicle/civilian/shared_landspeeder_x34.iff','object/mobile/vehicle/shared_a1_deluxe_floater.iff']:
 for path,node in iff.walk(iff.parse(get(n))):
  if node.tag=='XXXX' and (b'objectName' in node.data or b'craftedSharedTemplate' in node.data): print(n,path,repr(node.data))
