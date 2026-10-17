"""PL-03: Nal Hutta's first look, the client half = the newest Hutt archive + the Nal Hutta entries (Claude, 16 Oct 2026).

Darklight's planet (terrain/hutta.trn in mtg_planets.tre, snapshot/hutta.ws and terrain/environment/hutta.iff in
mtg_patch_022.tre, datatables/clientregion/hutta.iff with the one Bilbousa row) is already on the client; the planet CRC
table already lists hutta. What the client still lacks, and this step adds on top of the base archive:
  string/en/hutta_region_names.stf      new: bilbousa "Bilbousa" (the key MTG's clientregion row points at)
  string/en/planet_n.stf                + hutta "Nal Hutta"
  datatables/travel/travel.iff          + column and row; Tatooine -> Nal Hutta 3000, Nal Hutta -> Tatooine 1750,
                                          Nal Hutta -> Nal Hutta 100 (the Corellia/Ossus pattern; placeholders)
  datatables/player/waypoint_planets.iff + hutta / ui_planet_sel_rori.apt (MTG ships ui_planet_sel_nalhutta.dds but no .apt)
  ui/ui_ticketpurchase.inc, ui/ui_planet_map.inc   Endor's blocks cloned for Nal Hutta after Ossus's (swgfmt/ui_inc.py);
                                          globe = the Rori placeholder, planetary map = MTG's texture/ui_map_nalhutta.dds
  datatables/loading/hutta.iff, string/en/loading/hutta.stf, hutta_n.stf   new: three loading screens, our own text,
                                          the stock generic tile (as Ossus had before its own art)
Every other entry of the base stays byte-identical (checked). Nothing is installed.

    C:/Users/Pengw/miniconda3/python.exe -I build_nal_hutta.py [--base PATH]
Default base: ../work/nal-hutta/base-6ff21312.tre (a copy of the installed Hutt archive, sha256 6ff21312...). If the
floater candidate lands first, pass it as --base: this step touches none of the floater's files.
Writes ../work/nal-hutta/local_planets-nalhutta.tre, its .sha256, and checks.json beside this file.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S7 = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(os.path.dirname(S7))
H = os.path.dirname(OUTPUTS)
WORK = os.path.join(H, 'work', 'nal-hutta')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
from swgfmt import ui_inc  # noqa: E402

PLANET, NAME = 'hutta', 'Nal Hutta'
DEFAULT_BASE = os.path.join(WORK, 'base-6ff21312.tre')
BASE_SHA_PREFIX = '6ff21312'
OUT_TRE = os.path.join(WORK, 'local_planets-nalhutta.tre')
GLOBE = 'ui_planet_sel_rori.apt'        # placeholder: no appearance/ui_planet_sel_nalhutta.apt in any client archive
MAP_TEXTURE = 'ui_map_nalhutta'         # MTG 022's planetary map image (texture/ui_map_nalhutta.dds)
PLACEHOLDERS = {
    'tatooine_to_hutta_fare': 3000, 'hutta_to_tatooine_fare': 1750, 'hutta_to_hutta_fare': 100,
    # below Ossus's provisional (425, 290) on the 498x481 galaxy map (button 61x59); lore: Y'Toub system, Hutt Space
    'galaxy_map_spot': (425, 355),
    'globe': GLOBE,
}
REGION_NAMES = [('bilbousa', 'Bilbousa')]
LOADING_PICTURE = 'loading/generic/generic_swg'
LOADING = [   # key, title, text (ours)
    ('hutta', 'Nal Hutta',
     'Nal Hutta, in the Y\'Toub system, is the throne world of the Hutt kajidics. Centuries of industry and neglect have '
     'left it a warm, stinking swamp under a yellow haze, with Nar Shaddaa hanging in its sky.'),
    ('bilbousa', 'Bilbousa',
     'The capital squats on a shelf of firm ground above the brown water. Every kajidic of note keeps a tower here, and '
     'every visitor pays someone for the privilege of leaving.'),
    ('swamps', 'The Hutta Lowlands',
     'Beyond the city the land sinks into brown, warm water and rotting reeds. Little that lives out there is friendly, '
     'and none of it is clean.'),
]
CHANGED = {'string/en/planet_n.stf', 'datatables/travel/travel.iff', 'datatables/player/waypoint_planets.iff',
           'ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc'}
NEW = {'string/en/hutta_region_names.stf', 'datatables/loading/hutta.iff', 'string/en/loading/hutta.stf',
       'string/en/loading/hutta_n.stf'}


def merge_travel(data):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'travel.iff: base does not round-trip'
    cols = list(t['columns'])
    assert PLANET not in cols, 'travel.iff already has hutta'
    cols.append(PLANET)
    types = t['types'] + [t['types'][-1]]
    rows = [r + [PLACEHOLDERS['tatooine_to_hutta_fare'] if r[0] == 'tatooine' else 0] for r in t['rows']]
    row = [PLANET] + [0] * (len(cols) - 1)
    row[cols.index('tatooine')] = PLACEHOLDERS['hutta_to_tatooine_fare']
    row[cols.index(PLANET)] = PLACEHOLDERS['hutta_to_hutta_fare']
    rows.append(row)
    out = st.write_dtii({'version': t['version'], 'columns': cols, 'types': types, 'rows': rows})
    back = st.read_dtii(out)
    assert all(br[:len(t['columns'])] == sr for br, sr in zip(back['rows'], t['rows']))
    return out, {'columns': cols, 'hutta_row': {c: v for c, v in zip(cols, row) if v},
                 'into_hutta': {r[0]: r[-1] for r in back['rows'] if r[-1]}}


def merge_planet_names(data):
    s = st.read_stf(data)
    assert st.write_stf(s) == data, 'planet_n.stf: base does not round-trip'
    have = dict(st.stf_items(s))
    assert PLANET not in have, 'planet_n.stf already has hutta'
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    st.stf_add(s, PLANET, NAME)
    out = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(out))) == {**have, PLANET: NAME}
    return out, {'hutta': NAME, 'keys': len(have) + 1}


def merge_waypoint_planets(data):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'waypoint_planets.iff: base does not round-trip'
    names = [r[0] for r in t['rows']]
    assert PLANET not in names, 'waypoint_planets.iff already has hutta'
    at = names.index('ossus' if 'ossus' in names else 'yavin4') + 1
    rows = t['rows'][:at] + [[PLANET, GLOBE]] + t['rows'][at:]
    out = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    assert [r for r in st.read_dtii(out)['rows'] if r[0] != PLANET] == t['rows']
    return out, {'rows': [r[0] for r in rows], 'globe': GLOBE}


def merge_ui(ticket, planet_map):
    after = 'Ossus' if b'buttonOssus' in ticket else None
    t_out, p_out, rep = ui_inc.add_planet(ticket, planet_map, 'Hutta', PLANET, GLOBE, MAP_TEXTURE,
                                          PLACEHOLDERS['galaxy_map_spot'], after=after)
    # the element names stay 'Hutta' (key 'hutta'); only the label the player reads says the planet's name
    for old, new in ((b"LocalText='Hutta'", b"LocalText='%s'" % NAME.encode()), (b'>Hutta</Text>', b'>%s</Text>' % NAME.encode())):
        assert t_out.count(old) == 1, old
        t_out = t_out.replace(old, new)
    rep['after'] = after
    rep['bytes_kept'] = ui_inc.lines_kept(ticket, t_out) and ui_inc.lines_kept(planet_map, p_out)
    rep['bare_cr_unchanged'] = (t_out.count(b'\r\r\n') == ticket.count(b'\r\r\n') and
                                p_out.count(b'\r\r\n') == planet_map.count(b'\r\r\n'))
    rep['planets'] = ui_inc.planets_in(t_out)
    return t_out, p_out, rep


def new_files():
    out = {}
    names = st.stf_new()
    for key, text in REGION_NAMES:
        st.stf_add(names, key, text)
    out['string/en/hutta_region_names.stf'] = st.write_stf(names)
    src = st.read_dtii(trn_iff.client_file('datatables/loading/dantooine.iff'))
    rows = [['@loading/hutta:' + key, LOADING_PICTURE, '@loading/hutta_n:' + key] for key, _, _ in LOADING]
    out['datatables/loading/hutta.iff'] = st.write_dtii({'version': src['version'], 'columns': src['columns'],
                                                         'types': src['types'], 'rows': rows})
    texts, titles = st.stf_new(), st.stf_new()
    for key, title, text in LOADING:
        st.stf_add(texts, key, text)
        st.stf_add(titles, key, title)
    out['string/en/loading/hutta.stf'] = st.write_stf(texts)
    out['string/en/loading/hutta_n.stf'] = st.write_stf(titles)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    if args.base == DEFAULT_BASE:
        assert base_sha.startswith(BASE_SHA_PREFIX), 'default base is not the 6ff21312 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]

    # what the client already has (MTG): checked, not changed
    idx = trn_iff.client_index()
    region = st.read_dtii(trn_iff.client_file('datatables/clientregion/hutta.iff'))
    crc = st.read_cstb(base['misc/planet_crc_string_table.iff'])
    have = {
        'terrain/hutta.trn': idx.get('terrain/hutta.trn'), 'snapshot/hutta.ws': idx.get('snapshot/hutta.ws'),
        'terrain/environment/hutta.iff': idx.get('terrain/environment/hutta.iff'),
        'terrain/environment/nalhutta.iff': idx.get('terrain/environment/nalhutta.iff'),
        'datatables/environment/hutta.iff': idx.get('datatables/environment/hutta.iff'),
        'texture/ui_map_nalhutta.dds': idx.get('texture/ui_map_nalhutta.dds'),
        'texture/ui_planet_sel_nalhutta.dds': idx.get('texture/ui_planet_sel_nalhutta.dds'),
        'appearance/ui_planet_sel_nalhutta.apt': idx.get('appearance/ui_planet_sel_nalhutta.apt'),
        'appearance/' + GLOBE: idx.get('appearance/' + GLOBE),
        'texture/' + LOADING_PICTURE + '.dds': idx.get('texture/' + LOADING_PICTURE + '.dds'),
        'clientregion_rows': region['rows'],
        'planet_crc_has': sorted(n for _, n in crc['entries'] if 'hutta' in n),
        'hutta_strings_in_client': sorted(n for n in idx if n.startswith('string/') and 'hutta' in n),
    }
    assert have['terrain/hutta.trn'] and have['snapshot/hutta.ws'] and have['texture/ui_map_nalhutta.dds']
    assert have['appearance/' + GLOBE] and have['texture/' + LOADING_PICTURE + '.dds']
    assert 'hutta' in have['planet_crc_has']
    assert [r[0] for r in region['rows']] == ['@hutta_region_names:bilbousa'], region['rows']

    files = dict(base)
    report = {}
    files['datatables/travel/travel.iff'], report['travel'] = merge_travel(base['datatables/travel/travel.iff'])
    files['string/en/planet_n.stf'], report['planet_n'] = merge_planet_names(base['string/en/planet_n.stf'])
    files['datatables/player/waypoint_planets.iff'], report['waypoint_planets'] = merge_waypoint_planets(
        base['datatables/player/waypoint_planets.iff'])
    files['ui/ui_ticketpurchase.inc'], files['ui/ui_planet_map.inc'], report['ui'] = merge_ui(
        base['ui/ui_ticketpurchase.inc'], base['ui/ui_planet_map.inc'])
    for rel, data in new_files().items():
        assert rel not in base, rel
        files[rel] = data

    data = tre_write.pack(files)
    os.makedirs(WORK, exist_ok=True)
    with open(OUT_TRE, 'wb') as f:
        f.write(data)
    sha = hashlib.sha256(data).hexdigest()
    with open(OUT_TRE + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (sha, os.path.basename(OUT_TRE)))

    ours = tre_write.read(data)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    dropped = sorted(n for n in base if n not in ours)
    new = sorted(n for n in ours if n not in base)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(OUT_TRE, H).replace(os.sep, '/'), 'bytes': len(data), 'sha256': sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped),
        'changed': changed, 'new': new, 'dropped': dropped,
        'client_already_has': have, 'placeholders': PLACEHOLDERS, 'report': report,
        'new_texts': {rel: st.stf_items(st.read_stf(ours[rel])) for rel in sorted(NEW) if rel.endswith('.stf')},
        'loading_rows': st.read_dtii(ours['datatables/loading/hutta.iff'])['rows'],
    }
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped, dropped
    assert set(changed) == CHANGED, changed
    assert set(new) == NEW, new
    assert report['ui']['bytes_kept'] and report['ui']['bare_cr_unchanged'], report['ui']
    assert 'Hutta' in report['ui']['planets'], report['ui']['planets']
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new')}, indent=1))
    print('travel into hutta:', report['travel']['into_hutta'], 'from hutta:', report['travel']['hutta_row'])
    print('ticket planets:', report['ui']['planets'])
    print('Nal Hutta client step: PASS (allowed changes only, every other entry byte-identical)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
