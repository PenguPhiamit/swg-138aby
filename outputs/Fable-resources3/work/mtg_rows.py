import sys, os, json
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools')
from swgfmt import trn_iff as I, swg_tables as T
idx = I.client_index()
def get(n, arc=None): return I.open_tre_entry(os.path.join(I.CLIENT, arc or idx[n]), n)
mtg = T.read_dtii(get('datatables/resource/resource_tree.iff', 'mtg_planets.tre')); stock = T.read_dtii(get('datatables/resource/resource_tree.iff'))
ci = {c: i for i, c in enumerate(mtg['columns'])}
def depth(r): return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
def show(t, enums):
    rows = t['rows']; by = {r[1]: (k, r) for k, r in enumerate(rows)}
    for e in enums:
        if e not in by: print('  MISSING', e); continue
        k, r = by[e]; d = depth(r)
        attrs = [(r[ci['Attribute %d' % i]], r[ci['Att %d min' % i]], r[ci['Att %d max' % i]]) for i in range(1, 12) if r[ci['Attribute %d' % i]]]
        print('  %4d %-40s depth %d text %-34s pools %s/%s types %s/%s prev %-34s container %s rnd %s' % (k, e, d, r[ci['CLASS %d' % d]], r[ci['Minimum # Pools']], r[ci['Maximum # Pools']], r[ci['Minimum # types']], r[ci['Maximum # types']], rows[k-1][1], r[ci['Resource Container Type']].split('/')[-1], r[ci['Random Name Class']]))
        print('        attrs', attrs)
stock_enums = {r[1] for r in stock['rows']}
extra = [r[1] for r in mtg['rows'] if r[1] not in stock_enums]
print('MTG extras', len(extra)); print([e for e in extra if not e.endswith(('_hoth', '_kaas'))])
print('== the 4 gems + 3 energies (MTG)'); show(mtg, ['armophous_hoth_1', 'armophous_hoth_2', 'crystalline_hoth_1', 'crystalline_hoth_2', 'energy_renewable_site_limited_geothermal_hoth', 'energy_renewable_site_limited_tidal_hoth', 'energy_renewable_site_limited_hydron3_hoth'])
print('== stock parents / siblings'); show(stock, ['gemstone_armophous', 'gemstone_armophous_type1', 'gemstone_crystalline', 'gemstone_crystalline_type1', 'energy_renewable_site_limited_geothermal', 'energy_renewable_site_limited_geothermal_endor', 'energy_renewable_site_limited_tidal_endor', 'energy_renewable_site_limited_hydron3_endor', 'energy_renewable_unlimited_wind_endor'])
print('== MTG hoth inorganics vs stock parents (attribute rule)'); show(mtg, ['steel_hoth', 'iron_hoth', 'copper_hoth', 'ore_extrusive_hoth', 'gas_reactive_hoth', 'radioactive_hoth', 'petrochem_fuel_liquid_hoth']); show(stock, ['steel', 'steel_duralloy', 'iron', 'iron_kammris', 'copper', 'ore_extrusive', 'ore_extrusive_vintrium', 'gas_reactive', 'gas_reactive_tolium', 'radioactive', 'radioactive_type7', 'petrochem_fuel_liquid', 'petrochem_fuel_liquid_type7'])
