import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
def get(n): return I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n)
names = dict(T.stf_items(T.read_stf(get('string/en/resource/resource_names.stf'))))
print('generic class names:', {k: names.get(k) for k in ['steel', 'iron', 'aluminum', 'copper', 'ore_extrusive', 'ore_intrusive', 'gas_reactive', 'petrochem_fuel_liquid', 'petrochem_fuel_solid', 'radioactive', 'wheat_wild', 'fiberplast', 'water_vapor', 'energy_renewable_unlimited_wind', 'resource', 'metal', 'ore', 'mineral', 'chemical', 'gas', 'petrochem_fuel', 'gas_reactive_unknown']})
sv = dict(T.stf_items(T.read_stf(get('string/en/mission/survey/survey_resource_names.stf')))); print('survey_resource_names', idx['string/en/mission/survey/survey_resource_names.stf'], len(sv), list(sv.items())[:5])
mt = T.read_dtii(get('datatables/resource/resource_tree.iff'))
# stock rows per planet suffix for 'hoth'-style naming example (MTG)
print('MTG hoth names sample:', [(k, names[k]) for k in ['meat_wild_hoth', 'fiberplast_hoth', 'water_vapor_hoth', 'energy_renewable_unlimited_wind_hoth'] if k in names])
# stock: do any inorganic per-planet rows exist?
stock = T.read_dtii(get('datatables/resource/resource_tree.iff'))
inorg = [r[1] for r in stock['rows'] if any(r[1].startswith(p) for p in ('steel', 'iron', 'aluminum', 'copper', 'ore_', 'gas_', 'petrochem', 'radioactive'))]
print('stock inorganic enums', len(inorg), inorg[:60])
# stock planet-specific: which classes carry a planet suffix (should be 45 organics+water+fiberplast+energy)
print('names total', len(names))
