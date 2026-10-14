"""hoth_names.stage_hoth_names(stage_dir, base=None): the client files that put Hoth's named places on the planetary map
and in the client's location label, built from the winning stock/MTG copies plus the rows of ../sites.tsv and the keys of
../../Fable-hoth-batchB/names.tsv (Fable batch B3, 14 Oct 2026; outputs/Fable-hoth-mapnames/README.md).

    from hoth_names import stage_hoth_names
    report = stage_hoth_names('stage_dir')              # base = the client's winning copies (trn_iff.client_index)
    report = stage_hoth_names('stage_dir', base=fn)     # base(name) -> bytes of your current (merged) copy, or None
    report = stage_hoth_names('stage_dir', include_held=True)   # also the sites marked "held" in sites.tsv

Files written under stage_dir (client paths; every base file is round-tripped byte-exact before it is changed):
  string/en/hoth_region_names.stf      MTG's copy (world_spawner, hothstarport) + every names.tsv key + the sites.tsv keys
  datatables/clientregion/hoth.iff     MTG's row (the outpost) + one row per site with region != 0: the client's location label
  datatables/clientpoi/clientpoi.iff   the stock table (220 rows) + one Hoth row per site with marker = 1: the planetary
                                       map's Points of Interest (the client's own layer; stock Tatooine's Fort Tusken etc.)
  string/en/clientpoi_n.stf            stock + "hoth_<key>" names for the marker rows
  string/en/clientpoi_d.stf            stock + "hoth_<key>" descriptions (our own text, sites.tsv)
Also: snippets/hoth_regions_named.lua (the server-side NAMEDREGION rows, same sites) when snippet_path is given.
Idempotent: keys and rows already present in the base are kept and counted as existing, never duplicated.

Run:  python -I hoth_names.py <stage_dir> [--held] [--large-first]     writes the files and prints the report
      python -I hoth_names.py --verify <stage_dir>                      re-reads a staged set and checks it
"""
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OUT)
if os.path.join(OUTPUTS, 'tools') not in sys.path:
    sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

SITES_TSV = os.path.join(OUT, 'sites.tsv')
NAMES_TSV = os.path.join(OUTPUTS, 'Fable-hoth-batchB', 'names.tsv')
SNIPPET = os.path.join(OUT, 'snippets', 'hoth_regions_named.lua')

REGION_STF = 'string/en/hoth_region_names.stf'
REGION_TABLE = 'datatables/clientregion/hoth.iff'
POI_TABLE = 'datatables/clientpoi/clientpoi.iff'
POI_N = 'string/en/clientpoi_n.stf'
POI_D = 'string/en/clientpoi_d.stf'
FILES = (REGION_STF, REGION_TABLE, POI_TABLE, POI_N, POI_D)
PLANET = 'hoth'
PREFIX = 'hoth_'          # clientpoi keys are one flat namespace (forttusken, kenobishouse ...): ours are hoth_<key>


def default_base(name):
    """The copy the live client loads (stock beats MTG), or None when no archive has the file."""
    idx = trn_iff.client_index()
    arc = idx.get(name.lower())
    if arc is None:
        return None
    return trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), name)


def read_sites(path=SITES_TSV, include_held=False):
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    sites = []
    for r in rows:
        if r['status'] not in ('on', 'held'):
            raise ValueError('sites.tsv: status must be on/held: ' + r['key'])
        if r['status'] == 'held' and not include_held:
            continue
        s = dict(r)
        s['x'], s['y'], s['radius'] = float(r['x']), float(r['y']), float(r['radius'])
        s['marker'] = r['marker'] == '1'
        s['region'] = r['region']            # '1' = snippet row + client label, 'existing' = label only, '0' = none
        s['marker_x'] = float(r['marker_x']) if r['marker_x'] else s['x']
        s['marker_y'] = float(r['marker_y']) if r['marker_y'] else s['y']
        sites.append(s)
    keys = [s['key'] for s in sites]
    if len(set(keys)) != len(keys):
        raise ValueError('sites.tsv: duplicate key')
    return sites


def read_names(path=NAMES_TSV):
    """names.tsv rows for string/en/hoth_region_names.stf: {key: english}."""
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    out = {}
    for r in rows:
        if r['stf'] != REGION_STF:
            continue
        out[r['key']] = r['english']
    return out


def _stf_merge(data, pairs, rel):
    """Round-trip the base string file, add the missing keys. Returns (bytes, info)."""
    stf = st.read_stf(data)
    if st.write_stf(stf) != data:
        raise AssertionError(rel + ': base copy does not round-trip')
    have = dict(st.stf_items(stf))
    ids = {sid for sid, _ in stf['keys']}
    if stf['next_id'] <= max(ids, default=0):      # a stale counter would reuse an id (Bellum hit this on frn_n)
        stf['next_id'] = max(ids) + 1
    added, existing, differ = [], [], []
    for key, text in pairs:
        if key in have:
            existing.append(key)
            if have[key] != text:
                differ.append(key)
            continue
        st.stf_add(stf, key, text)
        added.append(key)
    out = st.write_stf(stf)
    back = st.read_stf(out)
    assert dict(st.stf_items(back)) == {**have, **dict(pairs)} or differ, rel + ': re-read mismatch'
    info = {'base_bytes': len(data), 'base_roundtrip': True, 'base_keys': len(have), 'added': added,
            'existing': existing, 'existing_text_differs': differ, 'keys': len(back['keys']), 'next_id': back['next_id']}
    return out, info


def _dtii_merge(data, new_rows, key_cols, rel):
    """Round-trip the base datatable, append rows whose key columns are not present. Returns (bytes, info)."""
    t = st.read_dtii(data)
    if st.write_dtii(t) != data:
        raise AssertionError(rel + ': base copy does not round-trip')
    have = {tuple(r[c] for c in key_cols) for r in t['rows']}
    added, existing = [], []
    for r in new_rows:
        if len(r) != len(t['columns']):
            raise ValueError(rel + ': row width %d, table has %d columns' % (len(r), len(t['columns'])))
        k = tuple(r[c] for c in key_cols)
        if k in have:
            existing.append(r[0])
            continue
        t['rows'].append(list(r))
        have.add(k)
        added.append(r[0])
    return t, {'base_bytes': len(data), 'base_roundtrip': True, 'base_rows': len(t['rows']) - len(added),
               'columns': t['columns'], 'types': t['types'], 'added': added, 'existing': existing}


def region_rows(sites):
    return [['@hoth_region_names:' + s['key'], s['x'], s['y'], s['radius']] for s in sites if s['region'] != '0']


def poi_rows(sites):
    return [['@clientpoi_n:' + PREFIX + s['key'], '@clientpoi_d:' + PREFIX + s['key'], PLANET, '',
             s['marker_x'], 0.0, s['marker_y']] for s in sites if s['marker']]


def region_snippet(sites):
    """The hoth_regions.lua rows (NAMEDREGION circles) for the sites with region = 1; the ice-caves umbrella is a
    replace patch on the existing no-build row (patches.tsv), so it is not repeated here."""
    lines = [
        '\t-- Named places (Fable batch B3, 14 Oct 2026; outputs/Fable-hoth-mapnames/README.md): server-side names for the',
        "\t-- sites the client labels (datatables/clientregion/hoth.iff) and marks on the planetary map (clientpoi.iff), both",
        '\t-- in local_planets.tre. NAMEDREGION only: no spawning and no build rule. Circles are the label radii; the keys are',
        '\t-- string/en/hoth_region_names.stf. Generated by tools/hoth_names.py from sites.tsv.',
    ]
    for s in sites:
        if s['region'] != '1':
            continue
        lines.append('\t{"@hoth_region_names:%s", %d, %d, {CIRCLE, %d}, NAMEDREGION},' % (s['key'], s['x'], s['y'], s['radius']))
    return '\n'.join(lines) + '\n'


def stage_hoth_names(stage_dir, base=None, include_held=False, large_first=False, sites_path=SITES_TSV,
                     names_path=NAMES_TSV, snippet_path=None):
    base = base or default_base
    sites = read_sites(sites_path, include_held)
    names = read_names(names_path)
    for s in sites:                       # a site named in both files must agree
        if s['key'] in names and names[s['key']] != s['name']:
            raise ValueError('sites.tsv and names.tsv disagree on ' + s['key'])
    report = {'sites': [s['key'] for s in sites], 'files': {}, 'notes': []}

    def out(rel, data, info):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        info.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        report['files'][rel] = info

    # 1. region names: MTG's two keys + names.tsv + any site key names.tsv lacks (the two wampa flanks)
    data = base(REGION_STF)
    if data is None:
        raise FileNotFoundError(REGION_STF + ' has no base copy')
    pairs = list(names.items()) + [(s['key'], s['name']) for s in sites if s['key'] not in names]
    stf, info = _stf_merge(data, pairs, REGION_STF)
    out(REGION_STF, stf, info)

    # 2. client region labels: MTG's outpost row + ours, small circles first (nested labels; see README)
    data = base(REGION_TABLE)
    if data is None:
        raise FileNotFoundError(REGION_TABLE + ' has no base copy')
    t, info = _dtii_merge(data, region_rows(sites), [0], REGION_TABLE)
    t['rows'].sort(key=lambda r: r[3], reverse=large_first)
    info['order'] = 'largest radius first' if large_first else 'smallest radius first'
    info['rows'] = [list(r) for r in t['rows']]
    out(REGION_TABLE, st.write_dtii(t), info)

    # 3. planetary-map markers: stock clientpoi + one Hoth row per marker site
    data = base(POI_TABLE)
    if data is None:
        raise FileNotFoundError(POI_TABLE + ' has no base copy')
    t, info = _dtii_merge(data, poi_rows(sites), [0, 2], POI_TABLE)
    info['hoth_rows'] = [list(r) for r in t['rows'] if r[2] == PLANET]
    out(POI_TABLE, st.write_dtii(t), info)

    # 4. their names and descriptions
    marker_sites = [s for s in sites if s['marker']]
    for rel, col in ((POI_N, 'name'), (POI_D, 'description')):
        data = base(rel)
        if data is None:
            raise FileNotFoundError(rel + ' has no base copy')
        stf, info = _stf_merge(data, [(PREFIX + s['key'], s[col]) for s in marker_sites], rel)
        out(rel, stf, info)

    # 5. the server rows
    if snippet_path:
        text = region_snippet(sites)
        os.makedirs(os.path.dirname(snippet_path), exist_ok=True)
        with open(snippet_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        report['snippet'] = {'path': snippet_path, 'rows': text.count('NAMEDREGION},')}
    report['notes'].append('every base file round-tripped byte-exact before it was changed')
    return report


def verify(stage_dir, include_held=False):
    """Re-read a staged set: parse, round trip, the keys the tables point at exist, no duplicate keys."""
    sites = read_sites(SITES_TSV, include_held)
    res = {}

    def load(rel):
        with open(os.path.join(stage_dir, rel.replace('/', os.sep)), 'rb') as f:
            return f.read()
    rn = dict(st.stf_items(st.read_stf(load(REGION_STF))))
    pn = dict(st.stf_items(st.read_stf(load(POI_N))))
    pd = dict(st.stf_items(st.read_stf(load(POI_D))))
    for rel in FILES:
        d = load(rel)
        if rel.endswith('.stf'):
            s = st.read_stf(d)
            keys = [k for _, k in s['keys']]
            res[rel] = {'roundtrip': st.write_stf(s) == d, 'keys': len(keys), 'duplicate_keys': len(keys) - len(set(keys)),
                        'ids_unique': len({i for i, _ in s['keys']}) == len(keys)}
        else:
            t = st.read_dtii(d)
            res[rel] = {'roundtrip': st.write_dtii(t) == d, 'rows': len(t['rows'])}
    reg = st.read_dtii(load(REGION_TABLE))['rows']
    res[REGION_TABLE]['names_resolve'] = all(r[0].startswith('@hoth_region_names:') and r[0].split(':', 1)[1] in rn for r in reg)
    poi = [r for r in st.read_dtii(load(POI_TABLE))['rows'] if r[2] == PLANET]
    res[POI_TABLE]['hoth_rows'] = len(poi)
    res[POI_TABLE]['names_resolve'] = all(r[0].split(':', 1)[1] in pn and r[1].split(':', 1)[1] in pd for r in poi)
    want_markers = {PREFIX + s['key'] for s in sites if s['marker']}
    res[POI_TABLE]['sites_present'] = want_markers <= {r[0].split(':', 1)[1] for r in poi}
    want_labels = {s['key'] for s in sites if s['region'] != '0'}
    res[REGION_TABLE]['sites_present'] = want_labels <= {r[0].split(':', 1)[1] for r in reg}
    res['ok'] = all(v.get('roundtrip', True) and v.get('names_resolve', True) and v.get('sites_present', True)
                    and v.get('duplicate_keys', 0) == 0 and v.get('ids_unique', True) for v in res.values() if isinstance(v, dict))
    return res


def main(argv):
    if argv and argv[0] == '--verify':
        res = verify(argv[1], '--held' in argv)
        print(json.dumps(res, indent=1))
        return 0 if res['ok'] else 1
    if not argv:
        print(__doc__)
        return 2
    rep = stage_hoth_names(argv[0], include_held='--held' in argv, large_first='--large-first' in argv,
                           snippet_path=SNIPPET if '--no-snippet' not in argv else None)
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
