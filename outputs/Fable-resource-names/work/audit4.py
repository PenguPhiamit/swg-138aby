import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Local-content/local_planets.tre'
t = T.read_dtii(I.open_tre_entry(LP, 'datatables/resource/resource_tree.iff'))
ci = {c: i for i, c in enumerate(t['columns'])}
def depth(r):
    return max(i for i in range(1, 9) if r[ci['CLASS %d' % i]]) if any(r[ci['CLASS %d' % i]] for i in range(1, 9)) else 0
rows = t['rows']
for i, r in enumerate(rows):
    e = r[1]
    if e in ('wheat_wild_hoth', 'petrochem_fuel_liquid_hoth', 'steel_hoth', 'ore_extrusive_hoth', 'gas_reactive_hoth', 'radioactive_hoth', 'energy_renewable_unlimited_wind_hoth', 'wheat_wild_tatooine', 'steel_smelted', 'ore_extrusive_type1', 'petrochem_fuel_liquid_type1', 'gas_reactive_type1', 'radioactive_type1', 'fiberplast_tatooine'):
        print('%4d %-38s depth %d class %-28s prev %-36s maxtypes %s mintypes %s container %s rndname %s' % (i, e, depth(r), r[ci['CLASS %d' % depth(r)]], rows[i-1][1], r[ci['Maximum # types']], r[ci['Minimum # types']], r[ci['Resource Container Type']], r[ci['Random Name Class']]))
