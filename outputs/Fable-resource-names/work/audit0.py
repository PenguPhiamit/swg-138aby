import sys, os, collections
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
N = 'string/en/resource/resource_names.stf'; TR = 'datatables/resource/resource_tree.iff'
print('winning names:', idx[N], ' winning tree:', idx[TR])
names = dict(T.stf_items(T.read_stf(I.open_tre_entry(os.path.join(I.CLIENT, idx[N]), N))))
print('names keys', len(names))
LP = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Local-content/local_planets.tre'
merged = T.read_dtii(I.open_tre_entry(LP, TR)); stock = T.read_dtii(I.open_tre_entry(os.path.join(I.CLIENT, idx[TR]), TR))
print('merged rows', len(merged['rows']), 'stock rows', len(stock['rows']), 'cols', merged['columns'])
enums = [r[1] for r in merged['rows']]
missing = [e for e in enums if not names.get(e)]
print('merged rows with no name:', len(missing)); print(missing)
smiss = [r[1] for r in stock['rows'] if not names.get(r[1])]; print('stock rows with no name:', len(smiss), smiss[:20])
# stock per-planet naming examples
for suf in ('_tatooine', '_dantooine', '_yavin4', '_lok', '_corellia', '_naboo', '_dathomir', '_endor', '_rori', '_talus'):
    ex = [(r[1], names.get(r[1])) for r in stock['rows'] if r[1].endswith(suf)]
    print(suf, len(ex), ex[:3], '... wind/solar:', [n for k, n in ex if 'energy' in k])
# which classes exist per planet in stock (the planet-leaf classes)
per = collections.defaultdict(set)
for r in stock['rows']:
    e = r[1]
    for p in ('tatooine', 'dantooine', 'yavin4', 'lok', 'corellia', 'naboo', 'dathomir', 'endor', 'rori', 'talus'):
        if e.endswith('_' + p): per[p].add(e[:-len(p) - 1])
print('stock planet-leaf classes per planet:', {p: len(v) for p, v in per.items()})
allc = set.union(*per.values()); print(sorted(allc))
# MTG's tree: other planets' rows and names
mt = [a for a in sorted(set(idx.values())) if a.startswith('mtg')]
for arc in ('mtg_planets.tre', 'mtg_patch_022.tre', 'mtg_patch_019.tre'):
    d = I.open_tre_entry(os.path.join(I.CLIENT, arc), TR)
    if d:
        t = T.read_dtii(d); ens = [r[1] for r in t['rows']]
        extra = [e for e in ens if e not in set(r[1] for r in stock['rows'])]
        print(arc, 'tree rows', len(ens), 'beyond stock', len(extra), 'unnamed among them', [e for e in extra if not names.get(e)][:40])
