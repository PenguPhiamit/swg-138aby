exec(compile(open(__file__.replace('strings','client')).read().split('for n in [')[0],__file__,'exec'))
for n in ['string/en/pet_deed.stf','string/en/monster_name.stf','string/en/monster_detail.stf']:
 print(n,[(k,v) for k,v in st.stf_items(st.read_stf(get(n))) if 'floater' in k])
