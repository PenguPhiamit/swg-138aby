"""Tier table for the README from work/dormant_analysis.json: counts per tier and category, with examples.
Run: python -I tools/report_tiers.py  -> work/tiers.md (printed too)
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', 'work')
rows = json.load(open(os.path.join(W, 'dormant_analysis.json'), encoding='utf-8'))


def cat(p):
    parts = p.split('/')
    return '/'.join(parts[:3]) if len(parts) > 3 else '/'.join(parts[:2])


lines = ['| Tier | Category | Objects | Reason / pre-CU note | Examples |', '|---|---|---|---|---|']
for tier in 'ABCD':
    sub = [r for r in rows if r['tier'] == tier]
    groups = collections.defaultdict(list)
    for r in sub:
        groups[cat(r['shared'])].append(r)
    for c, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        reasons = collections.Counter((r['reason'], r['precu_note']) for r in rs).most_common(1)[0][0]
        ex = ', '.join(sorted({r['shared'].split('/')[-1][7:-4] for r in rs})[:3])
        lines.append(f'| {tier} | `{c}` | {len(rs)} | {reasons[0]}{" (" + reasons[1] + ")" if reasons[1] else ""} | {ex} |')
totals = collections.Counter(r['tier'] for r in rows)
lines.append('')
lines.append('Totals: ' + ', '.join(f'{t}: {totals[t]}' for t in 'ABCD') + f'; all: {len(rows)}')
text = '\n'.join(lines) + '\n'
with open(os.path.join(W, 'tiers.md'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print(text)
