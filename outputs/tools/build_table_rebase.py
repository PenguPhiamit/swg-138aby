"""Table rebase (17 Oct, speeders reported invisible and uncallable on run 27): bring our four mount tables up to MTG 022.

local_planets.tre outranks every stock and MTG archive, so its copies of datatables/mount/* are the ones the client
reads. This adds any row whose key is missing from ours, from mtg_patch_022, and checks ours is a key superset of
MTG 022 and of the stock winner (patch_11_02). Where both have a key with different values, ours stays.
Result on b01e9f44 (17 Oct): nothing missing, the output is byte-identical to the base. MTG 022's extra rows are
second rows for keys ours already has (swamp speeder, hoverlifter, AT-RT camo poses; a nerf saddle; a bantha scale).
The customization tables are not touched: MTG's copies sit below the stock archives, so the client has never read
their extra rows, and ours already hold every stock row (Documentation-support/table-rebase-17oct.md).

Reads the owner's local files only; never installs. Every other entry stays byte-identical.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

OUTPUTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OUTPUTS / 'tools'))
sys.path.insert(0, str(OUTPUTS / 'Fable-species/s4/tools'))
from swgfmt import tre_write, trn_iff as iff
import species_tables as species

BASE_SHA = 'b01e9f44aeba'
MTG = OUTPUTS / 'SWG-client' / 'mtg_patch_022.tre'
STOCK = OUTPUTS / 'SWG-client' / 'patch_11_02.tre'
# table -> number of leading columns that form the key
TABLES = {'datatables/mount/logical_saddle_name_map.iff': 1,
          'datatables/mount/saddle_appearance_map.iff': 2,
          'datatables/mount/rider_pose_map.iff': 2,
          'datatables/mount/valid_scale_range.iff': 2}


def rebase(ours_raw, mtg_raw, stock_raw, nkey):
    ours, mtg, stock = (species.st.read_dtii(r) for r in (ours_raw, mtg_raw, stock_raw))
    assert species.st.write_dtii(ours) == ours_raw
    assert ours['columns'] == mtg['columns'] == stock['columns']
    key = lambda r: tuple(str(v) for v in r[:nkey])
    have = {key(r) for r in ours['rows']}
    added = []
    for r in mtg['rows']:
        if key(r) not in have:
            ours['rows'].append(list(r))
            have.add(key(r))
            added.append([str(v) for v in r])
    out = species.st.write_dtii(ours)
    rows = species.st.read_dtii(out)['rows']
    keys = {key(r) for r in rows}
    assert all(key(r) in keys for r in mtg['rows']), 'not a key superset of MTG 022'
    assert all(key(r) in keys for r in stock['rows']), 'not a key superset of the stock winner'
    old = [tuple(map(str, r)) for r in species.st.read_dtii(ours_raw)['rows']]
    assert [tuple(map(str, r)) for r in rows[:len(old)]] == old, 'an existing row changed'
    kept = [[str(v) for v in r] for r in mtg['rows']
            if key(r) in {key(o) for o in species.st.read_dtii(ours_raw)['rows']}
            and tuple(map(str, r)) not in old]
    return out, {'rows': [len(old), len(rows)], 'mtg_rows': len(mtg['rows']), 'stock_rows': len(stock['rows']),
                 'added_from_mtg': added, 'mtg_differs_ours_kept': kept}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS.parent / 'work/nal-hutta-life/local_planets-nalhutta-life.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/table-rebase')
    parser.add_argument('--any-base', action='store_true', help='accept a base other than b01e9f44')
    args = parser.parse_args()
    base = args.base.read_bytes()
    base_sha = hashlib.sha256(base).hexdigest()
    assert args.any_base or base_sha.startswith(BASE_SHA), 'base is not b01e9f44: ' + base_sha
    entries = tre_write.read(base)[0]
    result, report = dict(entries), {}
    for name, nkey in TABLES.items():
        result[name], report[name] = rebase(entries[name], iff.open_tre_entry(str(MTG), name),
                                            iff.open_tre_entry(str(STOCK), name), nkey)
    assert all(result[n] == v for n, v in entries.items() if n not in TABLES)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        path = args.out_dir / 'stage' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result[name])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-table-rebase.tre'
    out.write_bytes(archive)
    summary = {'base_sha256': base_sha, 'out_sha256': hashlib.sha256(archive).hexdigest(), 'entries': len(result),
               'changed': sorted(n for n in entries if result[n] != entries[n]), 'tables': report, 'installed': False}
    (args.out_dir / 'checks.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
