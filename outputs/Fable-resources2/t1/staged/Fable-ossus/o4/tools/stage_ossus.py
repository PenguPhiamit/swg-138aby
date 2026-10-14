"""stage_ossus.stage_ossus(stage_dir, base): every Ossus client file in one call (Fable O4c, 14 Oct 2026).

    from stage_ossus import stage_ossus
    report = stage_ossus(stage_dir, base)          # base(name) -> bytes of the copy to build on, or None

base must return the copy that is already staged (Hoth's) when there is one, else the client's winning copy; the
shared files are then merged on top of it, every existing entry kept, Ossus added once (a second call changes nothing):
  misc/planet_crc_string_table.iff      + ossus (CRC f270b502)
  datatables/travel/travel.iff          + column and row; Corellia -> Ossus 3000, Ossus -> Corellia 1750, Ossus -> Ossus 100 (placeholders)
  string/en/planet_n.stf                + ossus "Ossus"
  datatables/player/waypoint_planets.iff + row ossus / ui_planet_sel_ossus.apt (after hoth, else yavin4)
  ui/ui_ticketpurchase.inc, ui/ui_planet_map.inc   Endor's blocks cloned for Ossus after Hoth's (ui_inc.py); galaxy-map spot placeholder
  datatables/resource/resource_tree.iff + the 45 Ossus rows (dantooine's planet rows cloned, O2c), ancestors' type counts raised
The Ossus-only files are copied from the earlier batches' staged output: O1 terrain and environment, O1c clientregion,
loading strings, O2a snapshot, O3 art (map, globe chain, loading tile and table).

    python -I stage_ossus.py <stage_dir> [--staging DIR]     DIR = the current staging folder (default Local-content/local_planets)
    python -I stage_ossus.py --selftest                       scratch copy of the staging folder: Hoth kept, Ossus added, idempotent
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
O4 = os.path.dirname(HERE)
OSSUS = os.path.dirname(O4)
OUTPUTS = os.path.dirname(OSSUS)
if os.path.join(OUTPUTS, 'tools') not in sys.path:
    sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
from swgfmt import ui_inc  # noqa: E402

PLANET, NAME = 'ossus', 'Ossus'
STAGING = os.path.join(OUTPUTS, 'Local-content', 'local_planets')
STOCK_BASE = os.path.join(OUTPUTS, 'Documentation-support', 'hoth', 'client-base')
PLACEHOLDERS = {
    'corellia_to_ossus_fare': {'value': 3000, 'status': 'PLACEHOLDER (owner question 10)'},
    'ossus_to_corellia_fare': {'value': 1750, 'status': 'PLACEHOLDER (owner question 10)'},
    'galaxy_map_spot': {'value': (425, 290), 'status': 'PLACEHOLDER (owner question 10): below Hoth\'s provisional (425, 225) on the 498x481 map; '
                                                       'the button is 61x59, the label sits +8,-4 and the 3D planet +4,+4 from it'},
}
TRAVEL_SELF = 100
SOURCES = {   # Ossus-only files: (batch folder under Fable-ossus, client path)
    'staged/client': ['terrain/ossus.trn', 'terrain/ossus_academy.tga', 'terrain/ossus_canyon.tga', 'terrain/ossus_mesa.tga',
                      'terrain/environment/ossus.iff', 'datatables/environment/ossus.iff', 'datatables/clientregion/ossus.iff',
                      'string/en/ossus_region_names.stf', 'string/en/loading/ossus.stf', 'string/en/loading/ossus_n.stf'],
    'o2/staged/client': ['snapshot/ossus.ws'],
    'o3/staged/client': ['texture/ui_map_ossus.dds', 'texture/ui_planet_sel_ossus.dds', 'appearance/ui_planet_sel_ossus.apt',
                         'appearance/mesh/ui_planet_sel_ossus.msh', 'shader/ui_planet_sel_ossus.sht',
                         'texture/loading/ossus/ui_load_ossus.dds', 'datatables/loading/ossus.iff'],
}
SHARED = ['misc/planet_crc_string_table.iff', 'datatables/travel/travel.iff', 'string/en/planet_n.stf',
          'datatables/player/waypoint_planets.iff', 'ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc', 'datatables/resource/resource_tree.iff']
RES_SOURCE, RES_ADJ = 'dantooine', {'dantooine': 'Dantooine', 'ossus': 'Ossus'}
RES_PLANETS = ('corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4', 'hoth', 'kaas', 'taanab', PLANET)


def winning(name):
    idx = trn_iff.client_index()
    arc = idx.get(name.lower())
    return None if arc is None else trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), name)


def staging_base(folder):
    """base(name): the file from the staging folder when it is there, else the client's winning copy."""
    def base(name):
        p = os.path.join(folder, name.replace('/', os.sep))
        if os.path.exists(p):
            with open(p, 'rb') as f:
                return f.read()
        return winning(name)
    return base


# ---------------------------------------------------------------- the shared files

def merge_crc_table(data):
    t = st.read_cstb(data)
    assert st.write_cstb(t['entries'], t['version']) == data, 'planet CRC table: base does not round-trip'
    names = [n for _, n in t['entries']]
    if PLANET in names:
        return data, {'action': 'present', 'entries': len(names)}
    out = st.write_cstb(t['entries'] + [(st.soe_crc(PLANET), PLANET)], t['version'])
    back = st.read_cstb(out)
    assert sorted(n for _, n in back['entries'] if n != PLANET) == sorted(names)
    return out, {'action': 'added', 'entries': len(back['entries']), 'crc': '%08x' % st.soe_crc(PLANET), 'kept': names}


def merge_travel(data):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'travel.iff: base does not round-trip'
    cols = list(t['columns'])
    if PLANET in cols:
        return data, {'action': 'present', 'columns': cols}
    cols.append(PLANET)
    types = t['types'] + [t['types'][-1]]
    rows = [r + [PLACEHOLDERS['corellia_to_ossus_fare']['value'] if r[0] == 'corellia' else 0] for r in t['rows']]
    row = [PLANET] + [0] * (len(cols) - 1)
    row[cols.index('corellia')] = PLACEHOLDERS['ossus_to_corellia_fare']['value']
    row[cols.index(PLANET)] = TRAVEL_SELF
    rows.append(row)
    out = st.write_dtii({'version': t['version'], 'columns': cols, 'types': types, 'rows': rows})
    back = st.read_dtii(out)
    assert all(br[:len(t['columns'])] == sr for br, sr in zip(back['rows'], t['rows']))
    return out, {'action': 'added', 'columns': cols, 'rows': len(rows), 'ossus_row': dict(zip(cols, row)), 'kept_rows': [r[0] for r in t['rows']]}


def merge_planet_names(data):
    s = st.read_stf(data)
    assert st.write_stf(s) == data, 'planet_n.stf: base does not round-trip'
    have = dict(st.stf_items(s))
    if PLANET in have:
        return data, {'action': 'present', 'keys': len(have)}
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    st.stf_add(s, PLANET, NAME)
    out = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(out))) == {**have, PLANET: NAME}
    return out, {'action': 'added', 'keys': len(have) + 1, 'kept': sorted(have)}


def merge_waypoint_planets(data, model='ui_planet_sel_ossus.apt'):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'waypoint_planets.iff: base does not round-trip'
    names = [r[0] for r in t['rows']]
    if PLANET in names:
        r = t['rows'][names.index(PLANET)]
        if r[1] == model:
            return data, {'action': 'present', 'rows': names}
        r[1] = model                       # an earlier placeholder model: point it at ours
        out = st.write_dtii(t)
        return out, {'action': 'model updated', 'rows': names, 'model': model}
    at = (names.index('hoth') if 'hoth' in names else names.index('yavin4')) + 1
    rows = t['rows'][:at] + [[PLANET, model]] + t['rows'][at:]
    out = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    assert [r for r in st.read_dtii(out)['rows'] if r[0] != PLANET] == t['rows']
    return out, {'action': 'added', 'rows': [r[0] for r in rows], 'model': model, 'after': rows[at - 1][0]}


def merge_resource_tree(data):
    """The 45 Ossus planet rows: each dantooine planet row cloned right after itself with the planet word swapped,
    every ancestor's Maximum/Minimum # types raised by the leaves under it (O2c's rule, Claude's Hoth merge the same)."""
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'resource_tree.iff: base does not round-trip'
    cols = t['columns']
    ci = {c: i for i, c in enumerate(cols)}
    if any(r[1].endswith('_' + PLANET) for r in t['rows']):
        return data, {'action': 'present', 'rows': len(t['rows'])}

    def depth_of(r):
        filled = [k for k in range(8) if r[2 + k]]
        return filled[0] + 1 if filled else 0

    def is_leaf(r):
        return r[1].rsplit('_', 1)[-1] in RES_PLANETS
    out_rows, added = [], []
    for r in t['rows']:
        out_rows.append(list(r))
        if r[1].endswith('_' + RES_SOURCE):
            c = list(r)
            c[1] = r[1][:-len(RES_SOURCE)] + PLANET
            nc = 2 + depth_of(r) - 1
            c[nc] = RES_ADJ[PLANET] + r[nc][len(RES_ADJ[RES_SOURCE]):] if r[nc].startswith(RES_ADJ[RES_SOURCE] + ' ') else r[nc].replace(RES_ADJ[RES_SOURCE], RES_ADJ[PLANET])
            out_rows.append(c)
            added.append((c[1], c[nc]))
    bumped, stack = {}, []
    for idx, r in enumerate(out_rows):
        d = depth_of(r)
        if is_leaf(r):
            if r[1].endswith('_' + PLANET):
                for a in stack:
                    bumped[a] = bumped.get(a, 0) + 1
            continue
        stack = [a for a in stack if depth_of(out_rows[a]) < d]
        stack.append(idx)
    for idx, n in bumped.items():
        out_rows[idx][ci['Maximum # types']] += n
        out_rows[idx][ci['Minimum # types']] += n
    for k, r in enumerate(out_rows):
        r[0] = k + 1
    out = st.write_dtii({'version': t['version'], 'columns': cols, 'types': t['types'], 'rows': out_rows})
    back = st.read_dtii(out)
    kept = [r for r in back['rows'] if not r[1].endswith('_' + PLANET)]
    assert len(kept) == len(t['rows']) and [r[1] for r in kept] == [r[1] for r in t['rows']]
    mx, mn = ci['Maximum # types'], ci['Minimum # types']
    for k, (o, b) in enumerate(zip(kept, t['rows'])):        # every other cell of every kept row is unchanged
        assert o[2:mx] == b[2:mx] and o[mn + 1:] == b[mn + 1:], o[1]
    return out, {'action': 'added', 'rows': len(back['rows']), 'added': len(added), 'first': added[:3], 'ancestors_bumped': len(bumped)}


def merge_ui(ticket, planet_map):
    spot = PLACEHOLDERS['galaxy_map_spot']['value']
    t_out, p_out, rep = ui_inc.add_planet(ticket, planet_map, NAME, PLANET, 'ui_planet_sel_ossus.apt', 'ui_map_ossus', spot,
                                          after='Hoth' if 'buttonHoth' in ticket.decode('latin-1') else None)
    rep['bytes_kept'] = ui_inc.lines_kept(ticket, t_out) and ui_inc.lines_kept(planet_map, p_out)
    rep['crlf'] = {'ticket': (t_out.count(b'\r\n'), t_out.count(b'\n')), 'planet_map': (p_out.count(b'\r\n'), p_out.count(b'\n'))}
    rep['bare_cr_unchanged'] = (t_out.count(b'\r\r\n') == ticket.count(b'\r\r\n')) and (p_out.count(b'\r\r\n') == planet_map.count(b'\r\r\n'))
    rep['planets'] = ui_inc.planets_in(t_out)
    return t_out, p_out, rep


# ---------------------------------------------------------------- the whole planet

def stage_ossus(stage_dir, base, include_resources=True):
    report = {'planet': PLANET, 'placeholders': PLACEHOLDERS, 'shared': {}, 'copied': {}, 'notes': []}

    def out(rel, data, info):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        info.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        return info

    def need(rel):
        d = base(rel)
        if d is None:
            raise FileNotFoundError(rel + ': no base copy')
        return d
    rel = 'misc/planet_crc_string_table.iff'
    d, info = merge_crc_table(need(rel)); report['shared'][rel] = out(rel, d, info)
    rel = 'datatables/travel/travel.iff'
    d, info = merge_travel(need(rel)); report['shared'][rel] = out(rel, d, info)
    rel = 'string/en/planet_n.stf'
    d, info = merge_planet_names(need(rel)); report['shared'][rel] = out(rel, d, info)
    rel = 'datatables/player/waypoint_planets.iff'
    d, info = merge_waypoint_planets(need(rel)); report['shared'][rel] = out(rel, d, info)
    t, p, info = merge_ui(need('ui/ui_ticketpurchase.inc'), need('ui/ui_planet_map.inc'))
    report['shared']['ui/ui_ticketpurchase.inc'] = out('ui/ui_ticketpurchase.inc', t, {'ui': info})
    report['shared']['ui/ui_planet_map.inc'] = out('ui/ui_planet_map.inc', p, {'planet_map_lines_added': info.get('planet_map_lines_added')})
    if include_resources:
        rel = 'datatables/resource/resource_tree.iff'
        d, info = merge_resource_tree(need(rel)); report['shared'][rel] = out(rel, d, info)
        report['notes'].append('the server reads the same resource_tree.iff (TreFiles) and needs ossus in resource_manager.lua activeZones (O2c)')
    for folder, rels in SOURCES.items():
        for rel in rels:
            src = os.path.join(OSSUS, folder.replace('/', os.sep), rel.replace('/', os.sep))
            with open(src, 'rb') as f:
                data = f.read()
            prev = base(rel)
            report['copied'][rel] = out(rel, data, {'from': 'Fable-ossus/' + folder, 'replaced_different_copy': prev is not None and prev != data})
    report['notes'].append('galaxy-map spot and the two fares are placeholders (owner question 10)')
    return report


def verify(stage_dir, base):
    """Every base entry kept, Ossus present, in each shared file; the UI files only grew by inserted lines."""
    res = {}

    def load(rel):
        with open(os.path.join(stage_dir, rel.replace('/', os.sep)), 'rb') as f:
            return f.read()
    b = base('misc/planet_crc_string_table.iff'); o = load('misc/planet_crc_string_table.iff')
    bn = {n for _, n in st.read_cstb(b)['entries']}; on = {n for _, n in st.read_cstb(o)['entries']}
    res['planet_crc'] = {'base_kept': bn <= on, 'ossus': PLANET in on, 'hoth_present': 'hoth' in on, 'ascending': [c for c, _ in st.read_cstb(o)['entries']] == sorted(c for c, _ in st.read_cstb(o)['entries'])}
    bt = st.read_dtii(base('datatables/travel/travel.iff')); ot = st.read_dtii(load('datatables/travel/travel.iff'))
    bc = bt['columns']
    res['travel'] = {'base_columns_kept': ot['columns'][:len(bc)] == bc, 'base_cells_kept': all(orow[:len(bc)] == brow for orow, brow in zip(ot['rows'], bt['rows'])),
                     'ossus_column': PLANET in ot['columns'], 'ossus_row': any(r[0] == PLANET for r in ot['rows']), 'hoth_present': 'hoth' in ot['columns'] and any(r[0] == 'hoth' for r in ot['rows'])}
    bs = dict(st.stf_items(st.read_stf(base('string/en/planet_n.stf')))); os_ = dict(st.stf_items(st.read_stf(load('string/en/planet_n.stf'))))
    res['planet_n'] = {'base_kept': all(os_.get(k) == v for k, v in bs.items()), 'ossus': os_.get(PLANET), 'hoth_present': os_.get('hoth')}
    bw = st.read_dtii(base('datatables/player/waypoint_planets.iff'))['rows']; ow = st.read_dtii(load('datatables/player/waypoint_planets.iff'))['rows']
    res['waypoint_planets'] = {'base_rows_kept': [r for r in ow if r[0] != PLANET] == [r for r in bw if r[0] != PLANET], 'ossus': next((r[1] for r in ow if r[0] == PLANET), None), 'hoth_present': any(r[0] == 'hoth' for r in ow)}
    for rel in ('ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc'):
        bb, oo = base(rel), load(rel)
        txt = oo.decode('latin-1')
        res[rel] = {'base_lines_kept': ui_inc.lines_kept(bb, oo), 'crlf_only': oo.count(b'\r\n') == oo.count(b'\n'), 'bare_cr_kept': oo.count(b'\r\r\n') == bb.count(b'\r\r\n'),
                    'ossus_mentions': txt.count('Ossus') + txt.count('ossus'), 'hoth_mentions': txt.count('Hoth') + txt.count('hoth'),
                    'base_hoth_mentions': bb.decode('latin-1').count('Hoth') + bb.decode('latin-1').count('hoth')}
    res['ui/ui_ticketpurchase.inc']['planets'] = ui_inc.planets_in(load('ui/ui_ticketpurchase.inc'))
    if os.path.exists(os.path.join(stage_dir, 'datatables', 'resource', 'resource_tree.iff')):
        br = st.read_dtii(base('datatables/resource/resource_tree.iff'))['rows']; orr = st.read_dtii(load('datatables/resource/resource_tree.iff'))['rows']
        res['resource_tree'] = {'base_enums_kept': [r[1] for r in orr if not r[1].endswith('_' + PLANET)] == [r[1] for r in br],
                                'ossus_rows': sum(1 for r in orr if r[1].endswith('_' + PLANET)), 'hoth_rows': sum(1 for r in orr if r[1].endswith('_hoth'))}
    res['copied_present'] = all(os.path.exists(os.path.join(stage_dir, rel.replace('/', os.sep))) for rels in SOURCES.values() for rel in rels)
    res['ok'] = all(all(v for k, v in d.items() if isinstance(v, bool) and not k.startswith('hoth')) for d in res.values() if isinstance(d, dict)) and res['copied_present']
    res['hoth_kept'] = all(d.get('hoth_present') for d in res.values() if isinstance(d, dict) and 'hoth_present' in d)
    return res


def selftest():
    ok = True
    for label, folder in (('current staging (Hoth present)', STAGING), ('stock only (no Hoth)', STOCK_BASE)):
        scratch = tempfile.mkdtemp()
        shutil.copytree(folder, scratch, dirs_exist_ok=True)
        base = staging_base(scratch)
        out1 = tempfile.mkdtemp()
        rep = stage_ossus(out1, base)
        ver = verify(out1, base)
        out2 = tempfile.mkdtemp()
        rep2 = stage_ossus(out2, staging_base(out1))      # second pass on the result: every shared file 'present', bytes identical
        same = all(rep2['shared'][r]['sha256'] == rep['shared'][r]['sha256'] for r in rep['shared'])
        present = all(rep2['shared'][r].get('action', 'present') == 'present' or r.startswith('ui/') for r in rep2['shared'])
        ui2 = rep2['shared']['ui/ui_ticketpurchase.inc']['ui'].get('ticket') == 'already present'
        print('== %s: verify ok %s (hoth kept %s); second pass identical %s, shared files present %s, ui present %s' % (label, ver['ok'], ver['hoth_kept'], same, present, ui2))
        print('   planets in the ticket UI:', ver['ui/ui_ticketpurchase.inc']['planets'])
        print('   travel columns:', st.read_dtii(open(os.path.join(out1, 'datatables', 'travel', 'travel.iff'), 'rb').read())['columns'])
        print('   waypoint rows:', [r[0] for r in st.read_dtii(open(os.path.join(out1, 'datatables', 'player', 'waypoint_planets.iff'), 'rb').read())['rows']])
        bad = {k: v for k, v in ver.items() if isinstance(v, dict) and not all(x for x in v.values() if isinstance(x, bool))}
        if bad:
            print('   FAILED checks:', json.dumps(bad, indent=1))
        ok &= ver['ok'] and same and present and ui2
        for d in (scratch, out1, out2):
            shutil.rmtree(d)
    print('SELFTEST', 'PASSED' if ok else 'FAILED')
    return ok


def main(argv):
    if '--selftest' in argv:
        return 0 if selftest() else 1
    if not argv:
        print(__doc__)
        return 2
    folder = argv[argv.index('--staging') + 1] if '--staging' in argv else STAGING
    base = staging_base(folder)
    rep = stage_ossus(argv[0], base)
    rep['verify'] = verify(argv[0], base)
    print(json.dumps(rep, indent=1, default=str))
    return 0 if rep['verify']['ok'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
