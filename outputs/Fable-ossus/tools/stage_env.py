"""O1c: the environment, loading and client-region tables for Ossus, copy-and-edit from Dantooine with Tatooine's
second sun. Our own code (Fable, 14 Oct 2026). Stock art is referenced by path only.

    python -I stage_env.py     # writes staged/client/terrain/environment/ossus.iff, datatables/{environment,clientregion,
                               #   loading}/ossus.iff, string/en/ossus_region_names.stf, string/en/loading/ossus{,_n}.stf,
                               #   out/env-report.json

Sources (read from the owner's client archives through Fable-planet-test/tools/trn_iff.py, never copied out):
  terrain/environment/dantooine.iff (FORM ENVM: NSKY, STAR, SUN, MOON, SMOO, CELS...) + the SSUN chunk of
  terrain/environment/tatooine.iff (its second sun); datatables/environment/dantooine.iff (25 columns, 5 weather rows
  per environment family); datatables/clientregion/dantooine.iff (Name, X, Z, Radius); datatables/loading/dantooine.iff
  (StringId, Picture, Title). Family names must match the EFAM names in terrain/ossus.trn (ossus_terrain.py ENVS).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '..', 'Fable-planet-test', 'tools'))
import swg_tables as st  # noqa: E402
from trn_iff import build, client_file, parse  # noqa: E402
import ossus_terrain as ot  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'client')
OUT = os.path.join(ROOT, 'out')

# our environment families (terrain/ossus.trn) <- the Dantooine family whose rows (sky, clouds, fog, sounds, music) we copy
FAMILY_SOURCE = {'ossus_plains': 'main_base', 'ossus_forest': 'second_stepes', 'ossus_mountains': 'stepes',
                 'ossus_benchland': 'jedi_temple', 'ossus_canyon': 'dantari1', 'ossus_knossa': 'outpost'}

# client regions (the names the client shows on the planetary map / overhead), story-neutral geography
REGIONS = [
    ('knossa', 'Knossa', ot.PAD['cx'], ot.PAD['cy'], 300.0),
    ('academy_benchland', 'the Academy Benchland', ot.BENCH['cx'], ot.BENCH['cy'], 1300.0),
    ('imhar_canyon', 'Imhar Canyon', 5150.0, 100.0, 1400.0),
    ('eocho_mountains', 'the Eocho Mountains', 0.0, -6600.0, 3200.0),
    ('adega_lake', 'Adega Lake', ot.LAKE['cx'], ot.LAKE['cy'], 700.0),
    ('ossus', 'Ossus', 0.0, 0.0, 9000.0),
]

# loading screen rows: our own text; the pictures are stock generic tiles referenced by path (no Ossus art yet)
LOADING = [
    ('ossus', 'Ossus', 'loading/generic/generic_swg',
     'Ossus, in the Adega system, was a centre of Jedi learning for thousands of years before the Great Sith War '
     'scarred it. Forest, benchland and canyon country around the old Knossa landing field.'),
    ('knossa', 'Knossa', 'loading/generic/generic_swg',
     'Knossa, the landing field in the south of the settled plains, below the Eocho Mountains.'),
    ('academy_benchland', 'The Academy Benchland', 'loading/generic/generic_swg',
     'A raised meadow north of Knossa where the Jedi once built. A road climbs to it from the landing field.'),
    ('imhar_canyon', 'Imhar Canyon', 'loading/generic/generic_swg',
     'A winding canyon in the east, its floor a few metres above the lakes that fill the low ground.'),
]


def write(rel, data):
    path = os.path.join(STAGED, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def main():
    rep = {'files': {}}
    # 1. the sky file: Dantooine's ENVM with Tatooine's SSUN (second sun) inserted after SUN
    dant = client_file('terrain/environment/dantooine.iff')
    tato = client_file('terrain/environment/tatooine.iff')
    assert build(parse(dant)) == dant and build(parse(tato)) == tato
    tree = parse(dant)
    envm = tree[0].children[0]
    ssun = [c for c in parse(tato)[0].children[0].children if c.tag == 'SSUN'][0]
    kids = []
    for c in envm.children:
        kids.append(c)
        if c.tag == 'SUN ':
            kids.append(ssun)
    envm.children = kids
    data = build(tree)
    back = parse(data)[0].children[0]
    rep['files']['terrain/environment/ossus.iff'] = {
        'stock_round_trips': True, 'chunks': [c.tag for c in back.children], 'bytes': len(data),
        'ssun_bytes_identical_to_tatooine': [c.data for c in back.children if c.tag == 'SSUN'][0] == ssun.data,
        'rest_identical_to_dantooine': [c.data for c in back.children if c.tag != 'SSUN'] == [c.data for c in parse(dant)[0].children[0].children]}
    write('terrain/environment/ossus.iff', data)

    # 2. datatables/environment/ossus.iff: 5 weather rows per family, copied from the chosen Dantooine family
    src = st.read_dtii(client_file('datatables/environment/dantooine.iff'))
    name_col = src['columns'].index('Environment Family Name')
    rows = []
    for ours, theirs in FAMILY_SOURCE.items():
        for r in src['rows']:
            if r[name_col] == theirs:
                rows.append([ours] + r[1:])
    table = {'version': src['version'], 'columns': src['columns'], 'types': src['types'], 'rows': rows}
    data = st.write_dtii(table)
    back = st.read_dtii(data)
    trn_families = ['ossus_' + n for n in ot.ENVS]
    rep['files']['datatables/environment/ossus.iff'] = {
        'rows': len(back['rows']), 'families': sorted(set(r[0] for r in back['rows'])), 'weather_rows_per_family': 5,
        'families_match_terrain': sorted(set(r[0] for r in back['rows'])) == sorted(trn_families),
        'columns': len(back['columns']), 'source_families': FAMILY_SOURCE,
        'referenced_files_exist': None}
    # every file a row names (sky gradient, cloud shaders, colour ramps, env maps, sounds, music) must exist in the client
    from trn_iff import client_index
    idx = client_index()
    missing = set()
    for r in back['rows']:
        for t, cell in zip(back['types'], r):
            if t == 's' and cell and '/' in cell and cell.lower() not in idx:
                missing.add(cell)
    rep['files']['datatables/environment/ossus.iff']['referenced_files_exist'] = not missing
    rep['files']['datatables/environment/ossus.iff']['missing'] = sorted(missing)
    write('datatables/environment/ossus.iff', data)

    # 3. client regions + their names
    src = st.read_dtii(client_file('datatables/clientregion/dantooine.iff'))
    rows = [['@ossus_region_names:' + key, float(x), float(y), float(r)] for key, _, x, y, r in REGIONS]
    data = st.write_dtii({'version': src['version'], 'columns': src['columns'], 'types': src['types'], 'rows': rows})
    write('datatables/clientregion/ossus.iff', data)
    names = st.stf_new()
    for key, text, *_ in REGIONS:
        st.stf_add(names, key, text)
    ndata = st.write_stf(names)
    write('string/en/ossus_region_names.stf', ndata)
    rep['files']['datatables/clientregion/ossus.iff'] = {'rows': st.read_dtii(data)['rows'], 'columns': src['columns'],
                                                         'names_file': 'string/en/ossus_region_names.stf', 'names': st.stf_items(st.read_stf(ndata))}

    # 4. loading screens: table + the two string files it points at
    src = st.read_dtii(client_file('datatables/loading/dantooine.iff'))
    rows = [['@loading/ossus:' + key, pic, '@loading/ossus_n:' + key] for key, _, pic, _ in LOADING]
    data = st.write_dtii({'version': src['version'], 'columns': src['columns'], 'types': src['types'], 'rows': rows})
    write('datatables/loading/ossus.iff', data)
    texts, titles = st.stf_new(), st.stf_new()
    for key, title, _, text in LOADING:
        st.stf_add(texts, key, text)
        st.stf_add(titles, key, title)
    write('string/en/loading/ossus.stf', st.write_stf(texts))
    write('string/en/loading/ossus_n.stf', st.write_stf(titles))
    pics = sorted(set(pic for _, _, pic, _ in LOADING))
    rep['files']['datatables/loading/ossus.iff'] = {'rows': st.read_dtii(data)['rows'], 'pictures_exist_in_client': all(('texture/' + p + '.dds').lower() in idx for p in pics),
                                                    'pictures': pics, 'strings': ['string/en/loading/ossus.stf', 'string/en/loading/ossus_n.stf']}
    for rel in ('string/en/ossus_region_names.stf', 'string/en/loading/ossus.stf', 'string/en/loading/ossus_n.stf'):
        with open(os.path.join(STAGED, rel.replace('/', os.sep)), 'rb') as f:
            d = f.read()
        rep['files'][rel] = {'round_trip': st.write_stf(st.read_stf(d)) == d, 'entries': len(st.read_stf(d)['keys'])}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'env-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    for k, v in rep['files'].items():
        print(k, json.dumps(v)[:260])
    ok = (rep['files']['terrain/environment/ossus.iff']['ssun_bytes_identical_to_tatooine'] and rep['files']['terrain/environment/ossus.iff']['rest_identical_to_dantooine']
          and rep['files']['datatables/environment/ossus.iff']['families_match_terrain'] and rep['files']['datatables/environment/ossus.iff']['referenced_files_exist']
          and rep['files']['datatables/loading/ossus.iff']['pictures_exist_in_client'])
    print('env:', 'PASS' if ok else 'CHECK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
