import sys, os, collections
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools'); sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Local-content/local_planets.tre'
t = T.read_dtii(I.open_tre_entry(LP, 'datatables/resource/resource_tree.iff')); ci = {c: i for i, c in enumerate(t['columns'])}
rows = t['rows']
def depth(r): return max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
# build ancestry: for each row, the chain of enums of its ancestors (positional hierarchy)
stack = []; anc = {}
for r in rows:
    d = depth(r)
    stack = [s for s in stack if s[0] < d]
    anc[r[1]] = [s[1] for s in stack]
    stack.append((d, r[1]))
leaves = {r[1]: r for r in rows if not any(a for a in anc.values() if r[1] in a)}
def pools(enum): r = next(x for x in rows if x[1] == enum); return r[ci['Minimum # Pools']], r[ci['Maximum # Pools']]
def class2(enum): return (anc[enum] + [enum])[2] if len(anc[enum]) >= 2 else enum   # CLASS 3 level: mineral/chemical/gas/water/energy...
def leaves_under(cls): return [e for e in leaves if cls in anc[e] or e == cls]
PLANETS = ('corellia','dantooine','dathomir','endor','lok','naboo','rori','talus','tatooine','yavin4','hoth','ossus')
def restricted(e): return e.rsplit('_', 1)[-1] in PLANETS
print('tree rows', len(rows), 'leaves', len(leaves))
for cls in ['steel','copper','aluminum','ore_extrusive','ore_intrusive','ore_carbonate','gemstone_crystalline','gemstone_armophous','radioactive_known','fuel_petrochem_solid','fuel_petrochem_liquid','petrochem_inert_polymer','petrochem_inert_lubricating_oil','metal','ore','fuel_petrochem_solid','radioactive','gemstone','gas','water','petrochem_inert','iron']:
    ls = [e for e in leaves_under(cls) if not restricted(e)]
    ps = [pools(e) for e in ls]
    if not ps: print(cls, 'NO LEAVES'); continue
    mn = sum(p[0] for p in ps) / len(ps); mx = sum(p[1] for p in ps) / len(ps)
    c2 = collections.Counter(class2(e) for e in ls)
    print('%-32s leaves %3d  min/max pools avg %.1f/%.1f  (range %s..%s)  class3 %s' % (cls, len(ls), mn, mx, min(p[0] for p in ps), max(p[1] for p in ps), dict(c2)))
jtl = 'steel_bicorbantium,steel_arveshian,aluminum_perovskitic,copper_borocarbitic,fiberplast_gravitonic,gas_reactive_organometallic,ore_siliclastic_fermionic,radioactive_polymetric'.split(',')
print('JTL rows:', [(e, pools(e), class2(e), e in leaves) for e in jtl if any(x[1] == e for x in rows)])
print('CLASS 3 names:', sorted(set(class2(e) for e in leaves if not restricted(e))))
print('class2 col names sample:', [(r[1], [r[ci['CLASS %d' % i]] for i in range(1, 5)]) for r in rows[:6]])
