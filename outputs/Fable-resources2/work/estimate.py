"""Offline estimate: of the test galaxy's in-shift galaxy-wide spawns, how many would the backfill put on Hoth, by class.
Pools from resource_manager.lua (dev 1c4c24fb); min/max pools per type from the merged resource_tree.iff; p = E[k] / N
with k uniform in [minpool, maxpool] capped at the 10 zones that existed at creation, N = 11 zones now."""
import sys, os, json, collections
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools'); sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Local-content/local_planets.tre'
t = T.read_dtii(I.open_tre_entry(LP, 'datatables/resource/resource_tree.iff')); ci = {c: i for i, c in enumerate(t['columns'])}
rows = t['rows']
def depth(r): return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
stack, anc = [], {}
for r in rows:
    d = depth(r); stack = [s for s in stack if s[0] < d]; anc[r[1]] = [s[1] for s in stack]; stack.append((d, r[1]))
has_child = {a for chain in anc.values() for a in chain}
leaves = [r[1] for r in rows if r[1] not in has_child]
PLANETS = ('corellia','dantooine','dathomir','endor','lok','naboo','rori','talus','tatooine','yavin4','hoth','ossus','kaas','taanab')
byenum = {r[1]: r for r in rows}
def pools(e): r = byenum[e]; return r[ci['Minimum # Pools']], r[ci['Maximum # Pools']]
def cls3(e): c = anc[e] + [e]; return c[2] if len(c) > 2 else c[-1]
def under(c): return [e for e in leaves if (c in anc[e] or e == c) and e.rsplit('_', 1)[-1] not in PLANETS]
N_OLD, N_NEW = 10, 11
def p_of(e):
    mn, mx = pools(e); ks = [min(k, N_OLD) for k in range(mn, mx + 1)]
    return sum(ks) / len(ks) / N_NEW
def expect(cls, count):
    ls = under(cls); ps = [p_of(e) for e in ls]; p = sum(ps) / len(ps)
    out = collections.Counter()
    c3 = collections.Counter(cls3(e) for e in ls)
    for c, n in c3.items(): out[c] += count * p * n / len(ls)
    return p, out
jtl = 'steel_bicorbantium,steel_arveshian,aluminum_perovskitic,copper_borocarbitic,fiberplast_gravitonic,gas_reactive_organometallic,ore_siliclastic_fermionic,radioactive_polymetric'.split(',')
minimum = [('steel', 1), ('copper', 1), ('aluminum', 1), ('ore_extrusive', 1), ('ore_intrusive', 1), ('ore_carbonate', 1), ('gemstone_crystalline', 1), ('gemstone_armophous', 1), ('radioactive_known', 1), ('fuel_petrochem_solid', 1), ('fuel_petrochem_liquid', 1), ('petrochem_inert_polymer', 2), ('petrochem_inert_lubricating_oil', 2)]
random_w = [('metal', 32), ('ore', 13), ('fuel_petrochem_solid', 6), ('radioactive', 4), ('gemstone', 12), ('gas', 16), ('water', 2), ('fuel_petrochem_liquid', 7), ('petrochem_inert', 8)]; random_size = 27
fixed = [('iron', 14)] + [(e, 1) for e in jtl]
total = collections.Counter(); spawns = collections.Counter(); detail = []
for pool, items in (('minimum', minimum), ('fixed', fixed)):
    for cls, n in items:
        p, out = expect(cls, n); total.update(out); spawns[pool] += n; detail.append((pool, cls, n, round(p, 3), dict({k: round(v, 2) for k, v in out.items()})))
wsum = sum(w for _, w in random_w)
for cls, w in random_w:
    n = random_size * w / wsum; p, out = expect(cls, n); total.update(out); spawns['random'] += n; detail.append(('random', cls, round(n, 2), round(p, 3), {k: round(v, 2) for k, v in out.items()}))
galaxy_wide = sum(spawns.values())
print('in-shift galaxy-wide spawns (minimum %d + random %d + fixed %d) = %d; the 42 native and 10 Hoth-restricted spawns are zone-restricted and excluded' % (spawns['minimum'], spawns['random'], spawns['fixed'], galaxy_wide))
print('expected to land on Hoth by class:', {k: round(v, 1) for k, v in total.items()}, 'total %.1f of %d (%.0f%%)' % (sum(total.values()), galaxy_wide, 100 * sum(total.values()) / galaxy_wide))
for d in detail: print('  ', d)
json.dump({'assumptions': __doc__, 'galaxy_wide_in_shift': galaxy_wide, 'by_pool': dict(spawns), 'expected_on_hoth_by_class': {k: round(v, 2) for k, v in total.items()},
           'expected_total': round(sum(total.values()), 1), 'detail': detail}, open('C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources2/work/estimate.json', 'w'), indent=1)
