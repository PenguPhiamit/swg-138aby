exec(compile(open(__file__.replace('iff','client')).read().split('for n in [')[0],__file__,'exec'))
for n in ['object/draft_schematic/vehicle/civilian/shared_landspeeder_x34.iff','object/mobile/vehicle/shared_a1_deluxe_floater.iff','object/intangible/vehicle/shared_a1_deluxe_floater_pcd.iff','object/tangible/deed/vehicle_deed/shared_a1_deluxe_floater_deed.iff']:
 print(n)
 for path,node in sp.acst.walk(sp.parse(get(n))) if hasattr(sp.acst,'walk') else []: print(path,node)
 print(re.findall(rb'[ -~]{3,}',get(n)))
