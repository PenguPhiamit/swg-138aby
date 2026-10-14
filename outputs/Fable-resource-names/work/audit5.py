import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
# which client files mention resource_names (ui includes, scripts, tables)
users = []
for n in idx:
    if n.startswith('ui/') or n.endswith('.inc') or n.endswith('.lua') or n.endswith('.txt') or n.startswith('datatables/resource'):
        d = get(n)
        if d and b'resource_names' in d: users.append(n)
print('client files mentioning resource_names:', users[:20])
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Local-content/local_planets.tre'
t = T.read_dtii(I.open_tre_entry(LP, 'datatables/resource/resource_tree.iff')); ci = {c: i for i, c in enumerate(t['columns'])}
names = dict(T.stf_items(T.read_stf(get('string/en/resource/resource_names.stf'))))
def depth(r): return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
print('\nhoth rows: ENUM | tree display name | stf name')
for r in t['rows']:
    if r[1].endswith('_hoth'):
        print('  %-40s %-32s %s' % (r[1], r[ci['CLASS %d' % depth(r)]], names.get(r[1], '-')))
# stock rows where tree display name != stf name
diff = [(r[1], r[ci['CLASS %d' % depth(r)]], names.get(r[1])) for r in t['rows'] if not r[1].endswith('_hoth') and names.get(r[1]) and names.get(r[1]) != r[ci['CLASS %d' % depth(r)]]]
print('\nstock rows where the tree text differs from the stf:', len(diff)); [print('  ', d) for d in diff[:12]]
nost = [(r[1], r[ci['CLASS %d' % depth(r)]]) for r in t['rows'] if not names.get(r[1])]
print('\nrows with no stf name:', nost)
