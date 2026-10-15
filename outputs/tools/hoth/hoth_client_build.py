"""Hoth step 2: build our copies of the client files that list planets, with Hoth added, and pack local_planets.tre.

    python -I tools/hoth/hoth_client_build.py

Input: the stock copies in Documentation-support/hoth/client-base/ (hoth_client_files.py extract; each one passed an
exact read/write round trip). Output:
    outputs/Local-content/local_planets/<internal paths>   the changed files (staging)
    outputs/Local-content/local_planets.tre                the archive; it must load ABOVE the stock archives
                                                             (client: a higher searchTree number; server: first in TreFiles)
The archive is then read back and every file compared with the staging copy.

What is added (only Hoth; everything else is byte-for-byte stock):
    string/en/planet_n.stf                    hoth = "Hoth"
    misc/planet_crc_string_table.iff          hoth
    datatables/travel/travel.iff              a hoth column and row: Corellia <-> Hoth (like Yavin IV), Hoth -> Hoth
    datatables/player/waypoint_planets.iff    hoth -> ui_planet_sel_hoth.apt (MTG ships the model)
    ui/ui_ticketpurchase.inc                  Endor's blocks cloned for Hoth: galaxy-map label, button, 3D planet,
                                              map page (ui_map_hoth from MTG), data source, code-data entry. No route
                                              line yet (decorative; needs a look in the real client)
    ui/ui_planet_map.inc                      Endor's planetary-map page cloned for Hoth
Format tools are ours: outputs/tools/swgfmt (swg_tables, ui_inc, tre_write behind fmt_tools).
"""
import filecmp, os, shutil, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BASE = os.path.join(H, 'outputs', 'Documentation-support', 'hoth', 'client-base')
STAGE = os.path.join(H, 'outputs', 'Local-content', 'local_planets')
TRE = os.path.join(H, 'outputs', 'Local-content', 'local_planets.tre')
sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))
from swgfmt.fmt_tools import stf_tool, dt_tool, cstb_tool, tre_pack, read_tre, _inflate  # noqa: E402  (ours: swg_tables, trn_iff, tre_write)
from swgfmt import hoth_ui  # noqa: E402  (ours: ui_inc)

# Fares: row = departure, column = arrival (credits). Same pattern as Yavin IV: reached from Corellia only.
FARES_TO_HOTH = {'corellia': 3000}
FARES_FROM_HOTH = {'corellia': 1750, 'hoth': 100}
# Provisional galaxy-map spot (free space, right of the map); replace with the C14 grid-square fit.
GALAXY_SPOT = (425, 225)


def src(path):
    return os.path.join(BASE, *path.split('/'))


def dst(path):
    out = os.path.join(STAGE, *path.split('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return out


def strings():
    t = stf_tool.read(src('string/en/planet_n.stf'))
    stf_tool.add(t, 'hoth', 'Hoth')
    stf_tool.write(t, dst('string/en/planet_n.stf'))


def crc_table():
    t = cstb_tool.read(src('misc/planet_crc_string_table.iff'))
    cstb_tool.add(t, 'hoth')
    cstb_tool.write(t, dst('misc/planet_crc_string_table.iff'))


def travel():
    t = dt_tool.read(src('datatables/travel/travel.iff'))
    t['names'].append('hoth')
    t['types'].append(t['types'][-1])
    for row in t['rows']:
        row.append(FARES_TO_HOTH.get(row[0], 0))
    planets = t['names'][1:]
    t['rows'].append(['hoth'] + [FARES_FROM_HOTH.get(p, 0) for p in planets])
    dt_tool.write(t, dst('datatables/travel/travel.iff'))


def waypoints():
    t = dt_tool.read(src('datatables/player/waypoint_planets.iff'))
    at = next(i for i, r in enumerate(t['rows']) if r[0] == 'yavin4') + 1
    t['rows'].insert(at, ['hoth', 'ui_planet_sel_hoth.apt'])
    dt_tool.write(t, dst('datatables/player/waypoint_planets.iff'))


def ui_includes():
    """Endor's blocks cloned for Hoth in both UI includes (Fable's ui_inc through hoth_ui): the stock bytes outside
    the inserted blocks stay as they are, the bare carriage returns in the OnShow/OnHide scripts included."""
    return hoth_ui.stage_hoth_ui(STAGE, base=lambda path: open(src(path), 'rb').read(), spot=GALAXY_SPOT)


def archive_file(archive, path):
    """Bytes of one file from one client archive (not the load-order winner)."""
    tre = os.path.join(H, 'outputs', 'SWG-client', archive)
    for entry in read_tre(tre):
        if entry['name'].lower() == path:
            with open(tre, 'rb') as stream:
                stream.seek(entry['offset'])
                blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
            return _inflate(blob, entry['comp'], entry['size'])
    raise KeyError(f'{path} not in {archive}')


# The client names every object the server sends by looking its CRC up in misc/object_template_crc_string_table.iff.
# The winning copy is stock patch_14_00's; MTG's larger tables (mtg_patch_022/023) list MTG's new objects but load
# below stock, so without this merge the client can't name any MTG object (found 14 Oct with the Hoth loot slice).
OBJECT_CRC_SOURCES = ['patch_14_00.tre', 'mtg_patch_022.tre', 'mtg_patch_023.tre']


def object_crc_table():
    path = 'misc/object_template_crc_string_table.iff'
    merged, report = {}, []
    for archive in OBJECT_CRC_SOURCES:
        raw = archive_file(archive, path)
        if archive == OBJECT_CRC_SOURCES[0] and not os.path.exists(src(path)):
            os.makedirs(os.path.dirname(src(path)), exist_ok=True)
            open(src(path), 'wb').write(raw)  # the stock copy, beside the other client-base files
        tmp = dst(path) + '.' + archive
        open(tmp, 'wb').write(raw)
        table = cstb_tool.read(tmp)
        cstb_tool.write(table, tmp + '.rt')  # the writer must reproduce a stock table exactly
        round_trip = open(tmp + '.rt', 'rb').read() == raw
        os.remove(tmp); os.remove(tmp + '.rt')
        new = {k: v for k, v in table.items() if k not in merged}
        merged.update(new)
        report.append(f'{archive}: {len(table)} entries, {len(new)} new, round trip {"exact" if round_trip else "DIFFERS"}')
    by_crc = {}
    for name, crc in merged.items():
        by_crc.setdefault(crc, []).append(name)
    clashes = {hex(c): n for c, n in by_crc.items() if len(n) > 1}
    report.append(f'merged: {len(merged)} entries; CRC clashes: {clashes or "none"}')
    cstb_tool.write(merged, dst(path))
    return report


def leaf_counts(rows):
    """For each row: how many leaf rows (resource types) sit under it, from the CLASS 1-8 columns (2..9)."""
    depth = [next(j for j in range(2, 10) if r[j] != '') for r in rows]
    counts = [0] * len(rows)
    for i in range(len(rows)):
        is_leaf = i + 1 == len(rows) or depth[i + 1] <= depth[i]
        if is_leaf:
            counts[i] += 1
            d = depth[i]
            for k in range(i - 1, -1, -1):  # every ancestor
                if depth[k] < d:
                    counts[k] += 1
                    d = depth[k]
    return counts


# MTG's four Hoth gem leaves are named <class>_hoth_<n>, so endswith('_hoth') missed them (Fable R3, 14 Oct 2026). Core3
# restricts a type by the '_hoth' substring (ResourceTree::setZoneRestriction), so the names are kept; their text is
# retyped (MTG: "Hothian Type 1 Crystal Amorphous Gem"), spelt as the stock class text ("Amorphous Gemstone").
HOTH_GEMS = {'armophous_hoth_1': 'Hothian Type 1 Amorphous Gemstone', 'armophous_hoth_2': 'Hothian Type 2 Amorphous Gemstone',
             'crystalline_hoth_1': 'Hothian Type 1 Crystalline Gemstone', 'crystalline_hoth_2': 'Hothian Type 2 Crystalline Gemstone'}


def resource_tree():
    """Hoth resources: stock's resource tree plus MTG's 50 *_hoth rows (mtg_planets.tre has them, but stock
    patch_14_00 shadows it). Core3 reads the rows in order (hierarchy from the CLASS columns; the container and
    random-name columns carry forward), so stock rows keep their values and order and each Hoth row goes where MTG
    put it, beside its siblings. MTG's other additions (Dromund Kaas, JTL space) stay out: no zone restricts them."""
    path = 'datatables/resource/resource_tree.iff'
    tables, report = {}, []
    for archive in ('patch_14_00.tre', 'mtg_planets.tre'):
        raw = archive_file(archive, path)
        tmp = dst(path) + '.' + archive
        open(tmp, 'wb').write(raw)
        tables[archive] = dt_tool.read(tmp)
        dt_tool.write(tables[archive], tmp + '.rt')
        report.append(f'{archive}: {len(tables[archive]["rows"])} rows, round trip '
                      f'{"exact" if open(tmp + ".rt", "rb").read() == raw else "DIFFERS"}')
        os.remove(tmp); os.remove(tmp + '.rt')
        if archive == 'patch_14_00.tre' and not os.path.exists(src(path)):
            os.makedirs(os.path.dirname(src(path)), exist_ok=True)
            open(src(path), 'wb').write(raw)
    stock, mtg = tables['patch_14_00.tre'], tables['mtg_planets.tre']
    assert stock['names'] == mtg['names'] and stock['types'] == mtg['types']
    by_enum = {r[1]: r for r in stock['rows']}
    rows = []
    for r in mtg['rows']:
        if r[1] in by_enum:
            rows.append(list(by_enum[r[1]]))
        elif r[1].endswith('_hoth') or r[1] in HOTH_GEMS:
            row = list(r)
            if r[1] in HOTH_GEMS:
                row[next(j for j in range(2, 10) if r[j] != '')] = HOTH_GEMS[r[1]]
            rows.append(row)
    assert [r[1] for r in rows if r[1] in by_enum] == [r[1] for r in stock['rows']], 'stock order changed'
    # MTG's Hoth set lacks the two native energies Core3's native pool asks every planet for. Clone Endor's rows as
    # Hoth's, at the end of their class (so the carried-forward container and name class stay right). MTG's
    # resource_names.stf, which wins in the client, already names both ("Hoth Solar/Wind Renewable Energy").
    # The three site-limited energies too (R3): stock has no class row for them, only the per-planet leaves, so a new
    # leaf goes after the last leaf of its kind.
    for base, label in (('energy_renewable_unlimited_solar', 'Hoth Solar Renewable Energy'),
                        ('energy_renewable_unlimited_wind', 'Hoth Wind Renewable Energy'),
                        ('energy_renewable_site_limited_geothermal', 'Hoth Geothermal Renewable Energy'),
                        ('energy_renewable_site_limited_tidal', 'Hoth Tidal Renewable Energy'),
                        ('energy_renewable_site_limited_hydron3', 'Hoth Hydron-3 Renewable Energy')):
        if any(r[1] == base + '_hoth' for r in rows):
            continue
        depth = [next(j for j in range(2, 10) if r[j] != '') for r in rows]
        p = next((i for i, r in enumerate(rows) if r[1] == base), None)
        if p is None:   # no class row (the site-limited energies): after the last leaf named <base>_<planet>
            end = max(i for i, r in enumerate(rows) if r[1].startswith(base + '_')) + 1
        else:
            end = next((i for i in range(p + 1, len(rows)) if depth[i] <= depth[p]), len(rows))
        clone = list(next(r for r in rows if r[1] == base + '_endor'))
        clone[1] = base + '_hoth'
        col = depth[next(i for i, r in enumerate(rows) if r[1] == base + '_endor')]
        clone[col] = label
        rows.insert(end, clone)
        report.append(f'added {clone[1]} (cloned from {base}_endor) at row {end + 1}')
    # Maximum/Minimum # types (columns 10, 11): check what stock means by them before recomputing
    stock_leaves = leaf_counts(stock['rows'])
    agree = sum(1 for r, n in zip(stock['rows'], stock_leaves) if r[10] == n)
    report.append(f'stock "Maximum # types" equals the leaf count on {agree} of {len(stock_leaves)} rows')
    new_leaves = leaf_counts(rows)
    old = {r[1]: n for r, n in zip(stock['rows'], stock_leaves)}
    for r, n in zip(rows, new_leaves):
        if r[1] in old and n != old[r[1]]:  # an ancestor of Hoth rows: raise both counts by the Hoth leaves added
            r[10] += n - old[r[1]]
            r[11] += n - old[r[1]]
    for i, r in enumerate(rows):
        r[0] = i + 1
    hoth = [r[1] for r in rows if r[1].endswith('_hoth')]
    report.append(f'merged: {len(rows)} rows ({len(hoth)} Hoth)')
    out = dict(stock)
    out['rows'] = rows
    dt_tool.write(out, dst(path))
    back = dt_tool.read(dst(path))
    report.append(f'read back: {len(back["rows"])} rows, same as written: {back["rows"] == rows}')
    return report


sys.path.insert(0, os.path.join(H, 'outputs', 'tools', 'owner_content'))
import swg_client_data  # noqa: E402  (ours: the client's load order and the archive that wins for each file)


OWN_ARCHIVE = os.path.basename(TRE).lower()
_stock_index = None


def winning(path):
    """(archive name, bytes) of the copy of a file that wins in the client's load order, leaving out our own
    local_planets.tre: once the client loads it, its copy is this script's previous output (C4f-F2)."""
    global _stock_index
    if _stock_index is None:
        _stock_index = {}
        trees, _, _ = swg_client_data.clo.load_order()
        for _, name in reversed(trees):  # lowest first, so higher priorities overwrite
            archive = os.path.basename(name)
            full = os.path.join(H, 'outputs', 'SWG-client', archive)
            if archive.lower() != OWN_ARCHIVE and os.path.exists(full):
                for entry in read_tre(full):
                    _stock_index[entry['name'].lower()] = archive
    archive = _stock_index[path]
    return archive, archive_file(archive, path)


# Botanist feasibility test (owner, 14 Oct: Botanist first; new professions enter at IV like every real elite).
# Only the profession root and the Novice box, shaped like Bio-Engineer's: does the client's skill browser show it,
# can a trainer teach it, does it survive a relog? Everything else about Botanist waits for that answer.
BOTANIST = {
    'root': {'NAME': 'outdoors_botanist', 'PARENT': 'outdoors', 'GRAPH_TYPE': 4, 'IS_PROFESSION': 1, 'SEARCHABLE': 1},
    'novice': {'NAME': 'outdoors_botanist_novice', 'PARENT': 'outdoors_botanist', 'GRAPH_TYPE': 4, 'IS_TITLE': 1,
               'MONEY_REQUIRED': 5000, 'POINTS_REQUIRED': 6, 'SKILLS_REQUIRED': 'outdoors_scout_harvest_04',
               'XP_TYPE': 'resource_harvesting_organic', 'XP_COST': 10000, 'XP_CAP': 40000,
               'SKILL_MODS': 'foraging=10', 'SEARCHABLE': 1},
}
BOTANIST_STRINGS = {
    'string/en/skl_n.stf': {'outdoors_botanist': 'Botanist', 'outdoors_botanist_novice': 'Novice Botanist'},
    'string/en/skl_d.stf': {
        'outdoors_botanist': 'Botanists study the plant life of the galaxy: what grows where, what it is good for, and how '
                             'to keep it alive. Experienced Scouts who have mastered Hunting can begin the trade.',
        'outdoors_botanist_novice': 'Novice Botanists learn to identify useful plants in the wild and gather them with '
                                    'more care than a Scout.'},
    'string/en/skl_t.stf': {'outdoors_botanist_novice': 'Novice Botanist'},
    'string/en/skill_teacher.stf': {'trainer_botanist': 'Most people walk straight past the best thing on the planet. '
                                                        'It is usually green, and it is usually underfoot.'},
    'string/en/mob/creature_names.stf': {'trainer_botanist': 'a Botanist trainer'},
}


def botanist():
    report = []
    archive, raw = winning('datatables/skill/skills.iff')
    path = 'datatables/skill/skills.iff'
    tmp = dst(path) + '.stock'
    open(tmp, 'wb').write(raw)
    t = dt_tool.read(tmp)
    dt_tool.write(t, tmp + '.rt')
    report.append(f'skills.iff from {archive}: {len(t["rows"])} rows, round trip '
                  f'{"exact" if open(tmp + ".rt", "rb").read() == raw else "DIFFERS"}')
    os.remove(tmp); os.remove(tmp + '.rt')
    if not os.path.exists(src(path)):
        os.makedirs(os.path.dirname(src(path)), exist_ok=True)
        open(src(path), 'wb').write(raw)
    names = [r[0] for r in t['rows']]
    assert 'outdoors_botanist' not in names
    def blank(typ):  # dt_tool's own type rule: i, b, h, e(num), z are ints; f floats; the rest strings
        c = typ[0].lower()
        return 0 if c in 'ibhez' else 0.0 if c == 'f' else ''

    def row(values):
        return [values.get(col, blank(typ)) for col, typ in zip(t['names'], t['types'])]

    # the stock Novice row must agree with what we fill in by default (counts and the ENDER column)
    bio = t['rows'][names.index('outdoors_bio_engineer_novice')]
    assert all(bio[i] == blank(ty) or col in BOTANIST['novice'] or col in ('NAME', 'PARENT', 'COMMANDS', 'SCHEMATICS_GRANTED')
               for i, (col, ty) in enumerate(zip(t['names'], t['types']))), 'Bio-Engineer Novice has a column we leave blank'

    # after Bio-Engineer's block, so each parent row comes before its children
    at = max(i for i, n in enumerate(names) if n.startswith('outdoors_bio_engineer')) + 1
    t['rows'][at:at] = [row(BOTANIST['root']), row(BOTANIST['novice'])]
    dt_tool.write(t, dst(path))
    back = dt_tool.read(dst(path))
    report.append(f'skills.iff: Botanist root + Novice inserted at rows {at + 1}-{at + 2}; read back '
                  f'{"same" if back["rows"] == t["rows"] else "DIFFERS"}')
    for stf, entries in BOTANIST_STRINGS.items():
        archive, raw = winning(stf)
        tmp = dst(stf) + '.stock'
        open(tmp, 'wb').write(raw)
        table = stf_tool.read(tmp)
        stf_tool.write(table, tmp + '.rt')
        exact = open(tmp + '.rt', 'rb').read() == raw
        os.remove(tmp); os.remove(tmp + '.rt')
        if not os.path.exists(src(stf)):
            os.makedirs(os.path.dirname(src(stf)), exist_ok=True)
            open(src(stf), 'wb').write(raw)
        for key, text in entries.items():
            assert key not in stf_tool.as_dict(table), (stf, key)
            stf_tool.add(table, key, text)
        stf_tool.write(table, dst(stf))
        report.append(f'{stf} from {archive}: round trip {"exact" if exact else "DIFFERS"}; added {", ".join(entries)}')
    return report


# Hoth quest chain (Fable batch C, dev 92d99dba): a new string table, not a change to a stock one. Fable's TSV has the
# target path on its first line and one key<TAB>text per line; the server reads the same table through TreFiles.
QUEST_STRINGS = os.path.join(H, 'outputs', 'Fable-hoth-batchC', 'strings.tsv')


def quest_strings():
    lines = [l.rstrip('\r\n') for l in open(QUEST_STRINGS, encoding='utf-8')]
    path = lines[0].split()[1]
    assert path.startswith('string/en/') and path.endswith('.stf') and not os.path.exists(src(path)), path
    stock = stf_tool.read(src('string/en/planet_n.stf'))  # header fields of a stock table
    t = {'magic': stock['magic'], 'flag': stock['flag'], 'next': 1, 'vals': {}, 'keys': []}
    entries = dict(l.split('\t', 1) for l in lines if l and not l.startswith('#'))
    for key, text in entries.items():
        stf_tool.add(t, key, text)
    stf_tool.write(t, dst(path))
    back = stf_tool.as_dict(stf_tool.read(dst(path)))
    return [f'{path}: new table, {len(back)} strings, read back {"same" if back == entries else "DIFFERS"}']


# Hoth map markers and place names (Fable's batch B3, outputs/Fable-hoth-mapnames): no C++, the client's own tables.
# region names (string/en/hoth_region_names.stf), place labels (datatables/clientregion/hoth.iff), the "Points of
# Interest" map list (datatables/clientpoi/clientpoi.iff + clientpoi_n/_d.stf). Fable's function takes a base reader;
# ours never returns our own archive's copy (C4f-F2).
sys.path.insert(0, os.path.join(H, 'outputs', 'Fable-hoth-mapnames', 'tools'))
import hoth_names  # noqa: E402  (Fable's)


def stock_copy(path):
    try:
        return winning(path)[1]
    except KeyError:
        return None


def map_names():
    report = hoth_names.stage_hoth_names(STAGE, base=stock_copy)
    return [f'{rel}: {info["bytes"]} bytes' for rel, info in report['files'].items()] + report.get('notes', [])


def check_ui_newlines(path):
    """The stock .inc files use CRLF; hoth_ui keeps every stock byte, so only make sure the stock copy is pure CRLF."""
    raw = open(src(path), 'rb').read()
    return raw.count(b'\r\n') == raw.count(b'\n')


def main():
    # Build into fresh copies beside the old output and publish them only when every check has passed, so a failed
    # run leaves the last good staging folder and archive in place (C4f-F2).
    global STAGE
    final_stage, tre_new = STAGE, TRE + '.new'
    STAGE = final_stage + '.new'
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)  # a failed earlier run's leftovers
    for path in ('ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc'):
        assert check_ui_newlines(path), f'{path}: stock copy is not pure CRLF; review the writer first'
    strings(); crc_table(); travel(); waypoints(); ui_includes()
    for line in object_crc_table():
        print('object CRC table:', line)
    for line in resource_tree():
        print('resource tree:', line)
    for line in botanist():
        print('botanist:', line)
    for line in quest_strings():
        print('quest strings:', line)
    for line in map_names():
        print('map names:', line)
    tre_pack.pack(STAGE, tre_new)
    staged = {os.path.relpath(os.path.join(d, f), STAGE).replace(os.sep, '/'): os.path.join(d, f)
              for d, _, fs in os.walk(STAGE) for f in fs}
    ok = True
    for entry in read_tre(tre_new):
        with open(tre_new, 'rb') as stream:
            stream.seek(entry['offset'])
            blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
        same = _inflate(blob, entry['comp'], entry['size']) == open(staged[entry['name']], 'rb').read()
        ok &= same
        stock = os.path.getsize(src(entry['name'])) if os.path.exists(src(entry['name'])) else 'none, a new file'
        print(f'{"OK " if same else "BAD"} {entry["name"]} ({entry["size"]} bytes; stock {stock})')
    print('archive verified' if ok else 'ARCHIVE MISMATCH')
    if not ok:
        print(f'kept the old {TRE} and {final_stage}; the failed build is in {tre_new} and {STAGE}')
        return 1
    if os.path.isdir(final_stage):
        shutil.rmtree(final_stage)
    os.rename(STAGE, final_stage)
    os.replace(tre_new, TRE)
    STAGE = final_stage
    print('published', TRE)
    # The changed files read back with the same tools, as a last check.
    print('planet_n hoth =', stf_tool.as_dict(stf_tool.read(dst('string/en/planet_n.stf'))).get('hoth'))
    print('crc hoth =', hex(cstb_tool.read(dst('misc/planet_crc_string_table.iff'))['hoth']))
    t = dt_tool.read(dst('datatables/travel/travel.iff'))
    print('travel columns', t['names'][-3:], 'hoth row', t['rows'][-1], 'corellia->hoth', t['rows'][0][-1])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
