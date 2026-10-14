import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
import swg_tables as T, trn_iff as I
idx = I.client_index()
for n in sorted(k for k in idx if k.startswith('datatables/clientregion/')):
    t = T.read_dtii(I.open_tre_entry(os.path.join(I.CLIENT, idx[n]), n))
    rows = t['rows']
    # nesting: any row centre inside another row's circle?
    nested = []
    for i, a in enumerate(rows):
        for j, b in enumerate(rows):
            if i != j and ((a[1]-b[1])**2 + (a[2]-b[2])**2) ** 0.5 < b[3] and a[3] < b[3]:
                nested.append((i, j, a[0], a[3], b[0], b[3]))
    print(n, '<-', idx[n], len(rows), 'rows; radii', [r[3] for r in rows][:14], 'nested(small idx, big idx):', nested[:4])
