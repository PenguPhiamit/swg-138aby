exec(compile(open(__file__.replace('female','client')).read().split('for n in [')[0],__file__,'exec'))
for n in ['appearance/hutt_m.sat','appearance/hutt_f.sat']:
 print(n,re.findall(rb'[ -~]{4,}',get(n)))
for n in ['datatables/mount/mount_appearance.iff','datatables/mount/mount_table.iff','datatables/mount/saddle_hardpoint.iff']:
 try:print(n,len(get(n)))
 except:pass
