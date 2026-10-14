import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
want = {'meat_wild_tatooine', 'steel', 'petrochem_fuel_liquid', 'water_vapor', 'wheat_wild_tatooine', 'steel_hoth'}
print('string/en files whose name has "resource":', [n for n in idx if n.startswith('string/en/') and 'resource' in n])
hits = {}
for n in sorted(idx):
    if not (n.startswith('string/en/') and n.endswith('.stf')): continue
    try: items = dict(T.stf_items(T.read_stf(get(n))))
    except Exception as e: continue
    found = {k: items[k] for k in want if k in items}
    if found or any('Tatooinian Wild Meat' in v for v in items.values()):
        hits[n] = (idx[n], found, [k for k, v in items.items() if 'Tatooinian Wild Meat' in v][:3])
for n, h in hits.items(): print(n, h)
# every archive's copy of resource_names.stf (not just the winner)
for arc in sorted(set(idx.values())):
    d = I.open_tre_entry(os.path.join(I.CLIENT, arc), 'string/en/resource/resource_names.stf')
    if d: 
        it = dict(T.stf_items(T.read_stf(d))); print('copy in', arc, len(it), 'keys;', {k: it.get(k) for k in ['meat_wild_tatooine', 'steel', 'petrochem_fuel_liquid', 'water_vapor', 'steel_hoth', 'meat_wild_hoth']})
