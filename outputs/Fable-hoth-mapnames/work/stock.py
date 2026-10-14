import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/owner_content')
import swg_tables as T, swg_client_data as D, trn_iff as I
idx = I.client_index()
def get(name):
    return I.open_tre_entry(os.path.join(I.CLIENT, idx[name]), name)
for n in ('string/en/clientpoi_n.stf', 'string/en/clientpoi_d.stf', 'datatables/clientpoi/clientpoi.iff', 'datatables/clientregion/hoth.iff', 'datatables/clientregion/tatooine.iff', 'string/en/hoth_region_names.stf', 'string/en/tatooine_region_names.stf', 'string/en/region_names.stf'):
    if n not in idx: print(n, 'MISSING'); continue
    d = get(n)
    if n.endswith('.stf'):
        s = T.read_stf(d); rt = T.write_stf(s) == d
        items = T.stf_items(s)
        print(n, '<-', idx[n], len(d), 'B', len(items), 'keys', 'roundtrip', rt, 'next_id', s['next_id'], 'version', s['version'])
        if 'clientpoi' in n:
            tat = [(k, v) for k, v in items if any(x in k for x in ('tusken', 'kenobi', 'ben', 'krayt', 'sarlacc', 'lars'))]
            for k, v in tat[:4]: print('   ', k, '=', v[:110])
        if 'hoth' in n:
            for k, v in items: print('   ', k, '=', v)
    else:
        t = T.read_dtii(d); rt = T.write_dtii(t) == d
        print(n, '<-', idx[n], len(d), 'B', 'roundtrip', rt, 'cols', t['cols'] if 'cols' in t else list(t.keys()), 'rows', len(t['rows']))
        for r in t['rows'][:3]: print('   ', r)
        if 'clientpoi' in n:
            print('    types', t.get('types'))
            for r in t['rows']:
                if r[2] == 'tatooine': print('   ', r)
