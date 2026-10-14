import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
for n in ('datatables/clientregion/hoth.iff', 'datatables/clientregion/tatooine.iff', 'datatables/clientpoi/clientpoi.iff'):
    t = T.read_dtii(I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n))
    print(n, t['version'], t['columns'], t['types'])
# stock clientpoi: duplicate name refs? ids of clientpoi_d
s = T.read_stf(I.open_tre_entry(os.path.join(I.CLIENT, idx['string/en/clientpoi_d.stf']), 'string/en/clientpoi_d.stf'))
ids = sorted(sid for sid, _ in s['keys']); print('clientpoi_d ids', ids[0], ids[-1], len(ids), 'next', s['next_id'])
s = T.read_stf(I.open_tre_entry(os.path.join(I.CLIENT, idx['string/en/hoth_region_names.stf']), 'string/en/hoth_region_names.stf'))
print('hoth_region_names', s)
