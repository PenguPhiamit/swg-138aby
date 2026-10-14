import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
st = T.read_dtii(get('datatables/resource/resource_tree.iff')); ci = {c: i for i, c in enumerate(st['columns'])}
def depth(r): return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
disp = {r[1]: r[ci['CLASS %d' % depth(r)]] for r in st['rows']}
cls = ['wheat_wild', 'petrochem_fuel_liquid', 'petrochem_fuel_solid', 'radioactive', 'steel', 'iron', 'aluminum', 'copper', 'ore_extrusive', 'ore_intrusive', 'gas_reactive']
print('generic class display text (stock tree):', {c: disp.get(c) for c in cls})
print('known/unknown children:', {c: [k for k in disp if k.startswith(c + '_') and not k[len(c)+1:].startswith('type')][:4] for c in cls})
planets = ['corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4']
adj = {}
for p in planets:
    n = disp['fiberplast_' + p]; adj[p] = n.replace(' Fiberplast', '')
print('adjectives from fiberplast_<planet>:', adj)
print('examples:', {k: disp[k] for k in ['fiberplast_tatooine', 'water_vapor_dantooine', 'energy_renewable_unlimited_wind_yavin4', 'wheat_wild_tatooine', 'wheat_wild_dantooine', 'meat_wild_rori']})
# MTG's own rows: kaas and taanab display text (not merged by us; reference for the pattern MTG used)
for arc in ('mtg_planets.tre', 'mtg_patch_022.tre'):
    t = T.read_dtii(get('datatables/resource/resource_tree.iff', arc)); d2 = {r[1]: r[ci['CLASS %d' % depth(r)]] for r in t['rows']}
    print(arc, {k: d2[k] for k in d2 if k.endswith('_kaas') or k.endswith('_taanab')} and [ (k, d2[k]) for k in d2 if k in ('meat_wild_kaas', 'steel_kaas', 'meat_wild_taanab', 'fiberplast_taanab', 'steel_taanab')])
# the server's copy of the tree: which archive does the server read? (TreFiles) -> cannot read config; note only
