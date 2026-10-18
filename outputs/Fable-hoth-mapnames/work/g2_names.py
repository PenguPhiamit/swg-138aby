import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
n = 'string/en/resource/resource_names.stf'; print('winning', idx[n])
missing = ['petrochem_fuel_liquid_hoth', 'petrochem_fuel_solid_hoth', 'radioactive_hoth', 'steel_hoth', 'iron_hoth', 'aluminum_hoth', 'copper_hoth', 'ore_extrusive_hoth', 'ore_intrusive_hoth', 'gas_reactive_hoth', 'wheat_wild_hoth']
for arc in sorted(set(os.listdir(I.CLIENT))):
    if not arc.lower().endswith('.tre'): continue
    d = I.open_tre_entry(os.path.join(I.CLIENT, arc), n)
    if d is None: continue
    items = dict(T.stf_items(T.read_stf(d)))
    have = [k for k in missing if items.get(k)]
    print(' ', arc, len(items), 'keys; names for the 11 unnamed hoth keys:', len(have), [items[k] for k in have][:3])
