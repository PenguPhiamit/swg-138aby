import sys
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/owner_content')
import os, swg_tables as T, swg_client_data as D, trn_iff as I
idx = I.client_index()
def get(name):
    return I.open_tre_entry(os.path.join(I.CLIENT, idx[name]), name)
names = dict(T.stf_items(T.read_stf(get('string/en/map_loc_cat_n.stf'))))
rows = D.datatable(get('datatables/player/planet_map_cat.iff'))
cols = list(rows[0].keys()); print('planet_map_cat', cols)
for i, r in enumerate(rows):
    print(i, [r[c] for c in cols], '|', names.get(r[cols[0]], '?'))
print()
rows = D.datatable(get('datatables/clientpoi/clientpoi.iff'))
cols = list(rows[0].keys()); print('clientpoi', len(rows), cols)
for r in rows[:6]: print([r[c] for c in cols])
print('planets', sorted(set(r['planet'] for r in rows) if 'planet' in cols else set(str(r[cols[2]]) for r in rows)))
tat = [r for r in rows if 'tatooine' in str(r).lower()]; print('tatooine rows', len(tat)); [print([r[c] for c in cols]) for r in tat[:8]]
ht = [r for r in rows if 'hoth' in str(r).lower()]; print('hoth rows', len(ht), ht[:3])
print()
for n in ('string/en/map_loc_n.stf', 'string/en/map_loc_type_n.stf'):
    it = dict(T.stf_items(T.read_stf(get(n)))); print(n, len(it), list(it.items())[:6])
# look at the planet map location template
d = get('object/tangible/planet_map_location/shared_map_location_base.iff')
print('shared_map_location_base', len(d), d[:64])
print([n for n in idx if 'planet_map_location' in n or 'map_location' in n][:12])
