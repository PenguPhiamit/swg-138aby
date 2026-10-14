import sys
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/owner_content')
import swg_tables as T, swg_client_data as D, trn_iff as I
idx = I.client_index()
print('entries matching planet_map / poi / map_loc / hoth_region_names:')
for name in sorted(idx):
    n = name.lower()
    if n.startswith('datatables/') and ('map' in n or 'poi' in n) or 'map_loc' in n or 'hoth_region_names' in n or n.startswith('string/en/poi'):
        print('  ', name, '<-', idx[name])
def get(name):
    a = idx[name]; a = a[0] if isinstance(a, (list, tuple)) else a
    r = I.open_tre_entry(a, name)
    return r[1] if isinstance(r, tuple) else r
names = T.stf_items(get('string/en/map_loc_cat_n.stf'))
rows = D.datatable(get('datatables/player/planet_map_cat.iff'))
cols = list(rows[0].keys()); print(cols)
for i, r in enumerate(rows):
    print(i, [r[c] for c in cols], '|', names.get(r[cols[0]], '?'))
