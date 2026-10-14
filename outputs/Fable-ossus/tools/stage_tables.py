"""O1b: register Ossus in the four client tables, built on the stock copies in Documentation-support/hoth/client-base
with our own writers (swg_tables.py). Our own code (Fable, 14 Oct 2026).

    python -I stage_tables.py          # writes staged/client/{misc,datatables,string}/..., out/tables-report.json

Each output is checked three ways: the stock copy round-trips byte for byte through the same writer; the staged
file re-reads to the stock content plus exactly the Ossus entries; and it also re-reads through Claude's independent
reader (outputs/tools/owner_content/swg_client_data.py). The galaxy-map spot and the Corellia fare are placeholders
(owner questions), recorded in placeholders.json and in the report.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, HERE)
import swg_tables as st  # noqa: E402

BASE = os.path.join(OUTPUTS, 'Documentation-support', 'hoth', 'client-base')
STAGED = os.path.join(ROOT, 'staged', 'client')
OUT = os.path.join(ROOT, 'out')
PLANET = 'ossus'
PLACEHOLDERS = {
    'corellia_to_ossus_fare': {'value': 3000, 'status': 'PLACEHOLDER (owner decision)',
                               'note': 'the Yavin IV / Hoth pattern: Corellia -> Ossus 3000, Ossus -> Corellia 1750, Ossus -> Ossus 100'},
    'ossus_to_corellia_fare': {'value': 1750, 'status': 'PLACEHOLDER (owner decision)'},
    'galaxy_map_spot': {'value': None, 'status': 'PLACEHOLDER (owner decision)',
                        'note': 'not in these four tables: the ticket UI (ui/ui_ticketpurchase.inc) places the button; Hoth sits at the '
                                'provisional (425, 225) and the affine fit of the stock map was rejected (Documentation-support/hoth/'
                                'galaxy-map-calibration.md). Lore grid for Ossus: Adega system, Outer Rim, near Yavin (R-6 vs P-6).'},
    'planet_model': {'value': 'ui_planet_sel_dant.apt', 'status': 'PLACEHOLDER (stock Dantooine model referenced in place) until '
                                                                   'appearance/ui_planet_sel_ossus.apt exists (map-art step)'},
}


def read(rel):
    with open(os.path.join(BASE, rel), 'rb') as f:
        return f.read()


def write(rel, data):
    path = os.path.join(STAGED, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def independent_reader():
    sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'owner_content'))
    import swg_client_data  # noqa: E402
    return swg_client_data


def main():
    rep = {'base': BASE, 'files': {}, 'placeholders': PLACEHOLDERS}
    scd = independent_reader()

    # 1. planet CRC table
    rel = 'misc/planet_crc_string_table.iff'
    stock = read(rel)
    table = st.read_cstb(stock)
    assert st.write_cstb(table['entries'], table['version']) == stock
    entries = table['entries'] + [(st.soe_crc(PLANET), PLANET)]
    data = st.write_cstb(entries, table['version'])
    back = st.read_cstb(data)
    names = [n for _, n in back['entries']]
    rep['files'][rel] = {'stock_round_trip': True, 'stock_entries': len(table['entries']), 'staged_entries': len(back['entries']),
                         'ossus_crc': '%08x' % st.soe_crc(PLANET), 'crc_order_ascending': [c for c, _ in back['entries']] == sorted(c for c, _ in back['entries']),
                         'stock_names_kept': sorted(n for _, n in table['entries']) == sorted(n for n in names if n != PLANET),
                         'crc_check_on_stock_names': all(st.soe_crc(n) == c for c, n in table['entries'])}
    write(rel, data)

    # 2. travel.iff: a column and a row for Ossus; only Corellia <-> Ossus fares (placeholders) and Ossus -> Ossus 100
    rel = 'datatables/travel/travel.iff'
    stock = read(rel)
    t = st.read_dtii(stock)
    assert st.write_dtii(t) == stock
    cols = t['columns'] + [PLANET]
    types = t['types'] + [t['types'][-1]]
    rows = []
    for r in t['rows']:
        fare = PLACEHOLDERS['corellia_to_ossus_fare']['value'] if r[0] == 'corellia' else 0
        rows.append(r + [fare])
    ossus_row = [PLANET] + [0] * (len(cols) - 1)
    ossus_row[cols.index('corellia')] = PLACEHOLDERS['ossus_to_corellia_fare']['value']
    ossus_row[cols.index(PLANET)] = 100
    rows.append(ossus_row)
    data = st.write_dtii({'version': t['version'], 'columns': cols, 'types': types, 'rows': rows})
    back = st.read_dtii(data)
    ind = scd.datatable(data)
    rep['files'][rel] = {'stock_round_trip': True, 'columns': back['columns'], 'rows': len(back['rows']),
                         'stock_cells_unchanged': all(br[:len(t['columns'])] == sr for br, sr in zip(back['rows'], t['rows'])),
                         'ossus_row': dict(zip(back['columns'], back['rows'][-1])),
                         'corellia_row_ossus_fare': dict(zip(back['columns'], back['rows'][0]))[PLANET],
                         'independent_reader_agrees': [dict(zip(cols, r)) for r in rows] == ind}
    write(rel, data)

    # 3. planet_n.stf: the planet's display name
    rel = 'string/en/planet_n.stf'
    stock = read(rel)
    s = st.read_stf(stock)
    assert st.write_stf(s) == stock
    st.stf_add(s, PLANET, 'Ossus')
    data = st.write_stf(s)
    back = st.read_stf(data)
    items = dict(st.stf_items(back))
    ind = scd.string_file(data)
    rep['files'][rel] = {'stock_round_trip': True, 'entries': len(back['keys']), 'ossus': items.get(PLANET), 'next_id': back['next_id'],
                         'stock_entries_kept': all(items.get(k) == v for k, v in st.stf_items(st.read_stf(stock))),
                         'independent_reader_agrees': ind.get(PLANET) == 'Ossus' and len(ind) == len(items)}
    write(rel, data)

    # 4. waypoint_planets.iff: name + the planet model the galaxy map draws
    rel = 'datatables/player/waypoint_planets.iff'
    stock = read(rel)
    t = st.read_dtii(stock)
    assert st.write_dtii(t) == stock
    rows = t['rows'] + [[PLANET, PLACEHOLDERS['planet_model']['value']]]
    data = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    back = st.read_dtii(data)
    ind = scd.datatable(data)
    rep['files'][rel] = {'stock_round_trip': True, 'rows': len(back['rows']), 'ossus_row': back['rows'][-1],
                         'stock_rows_unchanged': back['rows'][:-1] == t['rows'],
                         'independent_reader_agrees': [dict(zip(t['columns'], r)) for r in rows] == ind}
    write(rel, data)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'tables-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    with open(os.path.join(ROOT, 'placeholders.json'), 'w', encoding='utf-8') as f:
        json.dump(PLACEHOLDERS, f, indent=1)
    for rel, r in rep['files'].items():
        print(rel, json.dumps(r)[:300])
    ok = all(all(v is True for k, v in r.items() if k.endswith(('round_trip', 'unchanged', 'kept', 'agrees', 'ascending', 'names'))) for r in rep['files'].values())
    print('tables:', 'PASS' if ok else 'CHECK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
