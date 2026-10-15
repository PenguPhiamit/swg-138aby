"""stage_mtg_merges.stage_mtg_merges(stage_dir, base): give back the MTG rows that stock files hide (Claude, 15 Oct 2026).

The client and the server both load MTG's archives *below* stock, so when a file exists in both, stock's copy wins and
MTG's additions vanish. The owner's BARC speeder (15 Oct) spawned on the server but stayed invisible: the four mount
tables and the monster names come from stock (patch_11_02, patch_13_00), which know nothing of the BARC, while MTG's
copies (mtg_patch_022, mtg_patch_013_configurable_02) carry it. Without a saddle-appearance row the client has no body
to draw for the mount.

Each file here becomes stock + MTG's extra rows: every stock row stays as it is and in order; MTG rows whose key stock
lacks are appended, from the higher-priority MTG copy first (022, then 013). The columns and types are identical in all
copies (checked). The merged files go in local_planets.tre, which the client loads at the top and the server first.
Idempotent.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
from swgfmt import swg_tables as st, trn_iff  # noqa: E402

MTG_COPIES = ['mtg_patch_022.tre', 'mtg_patch_013_configurable_02.tre']   # client priority order (higher first)
TABLES = {   # file -> number of leading columns that make a row's key
    'datatables/mount/logical_saddle_name_map.iff': 1,   # sat_or_skt_name
    'datatables/mount/saddle_appearance_map.iff': 2,     # logical_saddle_name, saddle_capacity
    'datatables/mount/rider_pose_map.iff': 2,            # saddle_appearance_name, seat_index
    'datatables/mount/valid_scale_range.iff': 2,         # appearance_name, saddle_capacity
}
STRINGS = ['string/en/monster_name.stf']


def mtg_copy(name, archive):
    path = os.path.join(trn_iff.CLIENT, archive)
    return trn_iff.open_tre_entry(path, name) if name in trn_iff.list_tre(path) else None


def merge_table(name, keylen, base):
    data = base(name)
    stock = st.read_dtii(data)
    assert st.write_dtii(stock) == data, f'{name}: base does not round-trip'
    rows = [list(r) for r in stock['rows']]
    have = {tuple(r[:keylen]) for r in rows}
    added = []
    for archive in MTG_COPIES:
        copy = mtg_copy(name, archive)
        if copy is None:
            continue
        t = st.read_dtii(copy)
        assert t['columns'] == stock['columns'] and t['types'] == stock['types'], f'{name}: {archive} has other columns'
        for r in t['rows']:
            key = tuple(r[:keylen])
            if key not in have:
                rows.append(list(r))
                have.add(key)
                added.append((archive, key))
    out = st.write_dtii({'version': stock['version'], 'columns': stock['columns'], 'types': stock['types'], 'rows': rows})
    back = st.read_dtii(out)
    assert [list(r) for r in back['rows'][:len(stock['rows'])]] == [list(r) for r in stock['rows']], f'{name}: stock rows changed'
    return out, added


def merge_strings(name, base):
    data = base(name)
    stf = st.read_stf(data)
    assert st.write_stf(stf) == data, f'{name}: base does not round-trip'
    have = dict(st.stf_items(stf))
    added = []
    for archive in MTG_COPIES:
        copy = mtg_copy(name, archive)
        if copy is None:
            continue
        for key, text in st.stf_items(st.read_stf(copy)):
            if key not in have:
                st.stf_add(stf, key, text)
                have[key] = text
                added.append((archive, key))
    out = st.write_stf(stf)
    back = dict(st.stf_items(st.read_stf(out)))
    assert all(back[k] == v for k, v in st.stf_items(st.read_stf(data))), f'{name}: a stock string changed'
    return out, added


def stage_mtg_merges(stage_dir, base):
    report = {}
    for name, keylen in TABLES.items():
        out, added = merge_table(name, keylen, base)
        report[name] = out, added
    for name in STRINGS:
        report[name] = merge_strings(name, base)
    result = {}
    for name, (out, added) in report.items():
        path = os.path.join(stage_dir, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(out)
        result[name] = {'added': len(added), 'from': {a: sum(1 for x, _ in added if x == a) for a in MTG_COPIES},
                        'barc_keys': [k for _, k in added if 'barc' in str(k)], 'sha256': hashlib.sha256(out).hexdigest()}
    return result


if __name__ == '__main__':
    print(__doc__)
