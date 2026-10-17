"""PL-05 Hoth leftovers, the client half = any base archive + what the owner's Hoth answers need on the client
(Claude, 17 Oct 2026). Nothing is installed.

  terrain/hoth.trn                     the mynock den's terrain layer (Fable batch B2: MTG's hoth.trn + one flatten disc
                                       and a cave-mouth exclusion at -2000, -4800; owner, 15 Oct: the ice-cave option
                                       "with the added flatten layer"). Fable's staged file, checked by hash against
                                       the client's MTG copy it was made from.
  string/en/hoth_region_names.stf,     map names for the two dens (the "held" rows of Fable-hoth-mapnames/sites.tsv:
  datatables/clientregion/hoth.iff,    Mynock Den, Glacial Rancor Grounds) through Fable's own hoth_names tool, on
  datatables/clientpoi/clientpoi.iff,  the base's copies; every key and row already there is kept
  string/en/clientpoi_n.stf, _d.stf
  datatables/badge/badge_map.iff,      badge 141 bdg_thm_park_hoth_salvage for Quartermaster Vell's chain (a theme-park
  string/en/badge_n.stf, badge_d.stf   content badge, like the stock bdg_thm_park_* rows); stops if 141 or the key is used
  object/mobile/shared_rancor_ice.iff  the glacial rancor's pale blue body: the stock rancor_hue meshes and texture,
  appearance/rancor_ice.sat, mesh/...  its four shaders bound to the Chiss skin palette (palette/npc_chiss_skin.pal,
  shader/rancor_ice_*.sht              stock) instead of palette/creature_rancor.pal; default index 5
  misc/object_template_crc_string_table.iff  + the new object template's CRC row

Every other entry of the base comes through byte for byte (checked).

    C:/Users/Pengw/miniconda3/python.exe -I build_hoth_leftovers.py [--base PATH] [--out PATH]
Default base: ../../work/chain-1016/local_planets-chain-1016.tre (installed 16 Oct, sha256 df1d538e...).
Default out:  ../../work/hoth-leftovers/local_planets-hoth-leftovers.tre (+ .sha256); checks in ./checks-client.json.
"""
import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'swgfmt'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-hoth-mapnames', 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
import hoth_names  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'chain-1016', 'local_planets-chain-1016.tre')
DEFAULT_BASE_SHA_PREFIX = 'df1d538e'
DEFAULT_OUT = os.path.join(H, 'work', 'hoth-leftovers', 'local_planets-hoth-leftovers.tre')

# --- the mynock den's terrain (Fable batch B2)
TRN = 'terrain/hoth.trn'
TRN_SOURCE_SHA = '51ede670150650c604dcacf676c96080e92a5859bc4347b681ea69698d1896e2'  # MTG's, mtg_patch_022.tre
TRN_STAGED = os.path.join(OUTPUTS, 'Fable-hoth-batchB', 'staged', 'client', 'terrain', 'hoth.trn')
TRN_STAGED_SHA = 'ef2c1ee2be8475373f5c2314158f24428802f28b8c31a52f1a6f5325cb515209'

# --- the quest badge (the shape of the stock theme-park badges, e.g. 105 bdg_thm_park_jabba_badge)
BADGE_MAP = 'datatables/badge/badge_map.iff'
BADGE_N, BADGE_D = 'string/en/badge_n.stf', 'string/en/badge_d.stf'
BADGE = [141, 'bdg_thm_park_hoth_salvage', 'NONE', 2, 1, 'content']
BADGE_NAME = "Vell's Salvage Crew"
BADGE_DESC = "...ran all three of Quartermaster Vell's salvage jobs on Hoth and came back to collect the pay."

# --- the pale blue rancor
PALETTE_OLD, PALETTE_NEW = b'palette/creature_rancor.pal', b'palette/npc_chiss_skin.pal'
HUE_DEFAULT = 5  # RGB (0, 128, 182): the lightest of the Chiss palette's 8 entries; the server sets hue 5 as well
OBJECT_OLD, OBJECT_NEW = 'object/mobile/shared_rancor_hue.iff', 'object/mobile/shared_rancor_ice.iff'
SAT_OLD, SAT_NEW = 'appearance/rancor_hue.sat', 'appearance/rancor_ice.sat'
LMG_OLD, LMG_NEW = 'appearance/mesh/rancor_hue.lmg', 'appearance/mesh/rancor_ice.lmg'
MGN = ['appearance/mesh/rancor_hue_l%d.mgn' % i for i in range(5)]
SHT = ['shader/rancor_hue_hcsb21.sht', 'shader/rancor_hue_hcb13.sht', 'shader/rancor_hue_hc8.sht',
       'shader/rancor_hue_lod_hc8.sht']
CRC_TABLE = 'misc/object_template_crc_string_table.iff'

NAME_FILES = set(hoth_names.FILES)
CHAIN_NEW = {OBJECT_NEW, SAT_NEW, LMG_NEW} | {m.replace('rancor_hue', 'rancor_ice') for m in MGN} | \
    {s.replace('rancor_hue', 'rancor_ice') for s in SHT}
TOUCHED = {TRN, BADGE_MAP, BADGE_N, BADGE_D, CRC_TABLE} | NAME_FILES | CHAIN_NEW


def sha(b):
    return hashlib.sha256(b).hexdigest()


def source(base, rel):
    if rel in base:
        return base[rel], 'base'
    data = trn_iff.client_file(rel)
    assert data is not None, rel
    return data, trn_iff.client_index()[rel]


def swap(data, old, new, count):
    """Same-length string swap inside an IFF (no chunk sizes change); the result must still parse."""
    assert len(old) == len(new), (old, new)
    assert data.count(old) == count, (old, data.count(old), count)
    out = data.replace(old, new)
    assert trn_iff.build(trn_iff.parse(out)) == out
    return out


def ice_shader(data):
    """Rebind the shader's index_color_1 from the rancor palette to the Chiss skin palette, default index 5."""
    nodes = trn_iff.parse(data)
    assert trn_iff.build(nodes) == data, 'shader does not round-trip'
    pals = [n for _, n in trn_iff.walk(nodes) if not n.is_form and n.tag == 'PAL ']
    assert len(pals) == 1, len(pals)
    p = pals[0]
    head = b'index_color_1\x00\x01NIAM'  # variable name, private flag, texture tag MAIN (little-endian)
    prefix = head + PALETTE_OLD + b'\x00'
    assert p.data.startswith(prefix) and len(p.data) == len(prefix) + 4, p.data
    old_default = struct.unpack('<i', p.data[-4:])[0]   # stock defaults differ per shader (23, 1, ...)
    p.data = head + PALETTE_NEW + b'\x00' + struct.pack('<i', HUE_DEFAULT)
    out = trn_iff.build(nodes)
    assert out.count(b'creature_rancor') == 0 and out.count(PALETTE_NEW) == 1
    return out, old_default


def palette_entries(data):
    count = struct.unpack_from('<H', data, 22)[0]
    return [tuple(data[24 + 4 * i:27 + 4 * i]) for i in range(count)]


def build_chain(base, report):
    files = {}
    for rel in [OBJECT_OLD, SAT_OLD, LMG_OLD] + MGN + SHT:
        assert rel.replace('rancor_hue', 'rancor_ice') not in base, rel
    pal = palette_entries(trn_iff.client_file(PALETTE_NEW.decode()))
    assert len(pal) == 8 and HUE_DEFAULT < len(pal)
    report['chiss_palette'] = {'entries': pal, 'default': HUE_DEFAULT, 'rgb': pal[HUE_DEFAULT]}
    report['shader_old_defaults'] = {}
    for s in SHT:
        data, _ = source(base, s)
        files[s.replace('rancor_hue', 'rancor_ice')], report['shader_old_defaults'][s] = ice_shader(data)
    for m in MGN:
        data, _ = source(base, m)
        files[m.replace('rancor_hue', 'rancor_ice')] = out = swap(data, b'shader/rancor_hue_', b'shader/rancor_ice_', 1)
        assert b'rancor_hue' not in out, m
    data, _ = source(base, LMG_OLD)
    files[LMG_NEW] = swap(data, b'appearance/mesh/rancor_hue_l', b'appearance/mesh/rancor_ice_l', 5)
    data, _ = source(base, SAT_OLD)
    files[SAT_NEW] = swap(data, LMG_OLD.encode(), LMG_NEW.encode(), 1)
    data, _ = source(base, OBJECT_OLD)
    files[OBJECT_NEW] = swap(data, SAT_OLD.encode(), SAT_NEW.encode(), 1)
    for rel, data in files.items():
        assert b'rancor_hue' not in data or rel.startswith('shader/'), rel   # shaders keep texture/rancor_hue*.dds
    # the CRC table: every row kept, one row added
    data, src = source(base, CRC_TABLE)
    t = st.read_cstb(data)
    assert st.write_cstb(t['entries'], t['version']) == data, 'CRC table does not round-trip'
    crc = st.soe_crc(OBJECT_NEW)
    assert OBJECT_NEW not in {n for _, n in t['entries']} and crc not in {c for c, _ in t['entries']}
    assert st.soe_crc(OBJECT_OLD) in {c for c, _ in t['entries']}, 'soe_crc does not match the table'
    files[CRC_TABLE] = st.write_cstb(t['entries'] + [(crc, OBJECT_NEW)], t['version'])
    assert st.read_cstb(files[CRC_TABLE])['entries'] == sorted(t['entries'] + [(crc, OBJECT_NEW)])
    report['crc_table'] = {'from': src, 'rows': len(t['entries']) + 1, 'added': [crc, OBJECT_NEW]}
    report['chain'] = sorted(CHAIN_NEW)
    return files


def merge_badge_map(data):
    t = st.read_dtii(data)
    assert st.write_dtii(t) == data, 'badge_map.iff: source does not round-trip'
    assert t['columns'] == ['INDEX', 'KEY', 'MUSIC', 'CATEGORY', 'SHOW', 'TYPE'], t['columns']
    assert BADGE[0] not in {r[0] for r in t['rows']}, 'badge index %d already used' % BADGE[0]
    assert BADGE[1] not in {r[1] for r in t['rows']}, 'badge key already used'
    assert BADGE[0] == max(r[0] for r in t['rows']) + 1, 'badge index is not the next free one'
    assert BADGE[0] < 160, 'Core3 keeps 5 x 32 badge bits'
    assert (BADGE[3], BADGE[5]) in {(r[3], r[5]) for r in t['rows']}, 'no stock row has this category and type'
    rows = t['rows'] + [list(BADGE)]
    out = st.write_dtii({'version': t['version'], 'columns': t['columns'], 'types': t['types'], 'rows': rows})
    assert st.read_dtii(out)['rows'][:-1] == t['rows']
    return out, {'rows': len(rows), 'added': BADGE}


def merge_stf(data, key, text):
    s = st.read_stf(data)
    assert st.write_stf(s) == data, 'stf does not round-trip'
    have = dict(st.stf_items(s))
    assert key not in have, key
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    st.stf_add(s, key, text)
    out = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(out))) == {**have, key: text}
    return out, {'keys': len(have) + 1, key: text}


def build_names(base, report):
    """Fable's hoth_names tool with the held sites, on the base's own copies; check that only the two dens are new."""
    for rel in NAME_FILES:
        assert rel in base, rel + ' is not in the base (the installed archive has all five)'
    with tempfile.TemporaryDirectory() as tmp:
        rep = hoth_names.stage_hoth_names(tmp, base=lambda rel: base.get(rel), include_held=True)
        files = {rel: open(os.path.join(tmp, rel.replace('/', os.sep)), 'rb').read() for rel in NAME_FILES}
    new_keys = {'mynock_den', 'rancor_grounds'}
    for rel in (hoth_names.REGION_STF, hoth_names.POI_N, hoth_names.POI_D):
        before = dict(st.stf_items(st.read_stf(base[rel])))
        after = dict(st.stf_items(st.read_stf(files[rel])))
        added = set(after) - set(before)
        want = new_keys if rel == hoth_names.REGION_STF else {hoth_names.PREFIX + k for k in new_keys}
        # hoth_region_names.stf already has both keys (Fable's names.tsv went in with the map names); the clientpoi
        # files get them now. Either way: both present afterwards, nothing else added or changed.
        assert added <= want <= set(after) and all(after[k] == v for k, v in before.items()), (rel, added)
        report[rel] = {'added': {k: after[k] for k in sorted(added)}, 'unchanged': files[rel] == base[rel]}
        if not added:
            assert files[rel] == base[rel], rel
            del files[rel]
    for rel, key in ((hoth_names.REGION_TABLE, lambda r: r[0]), (hoth_names.POI_TABLE, lambda r: (r[0], r[2]))):
        before = st.read_dtii(base[rel])['rows']
        after = st.read_dtii(files[rel])['rows']
        assert all(r in after for r in before), rel + ': a base row changed or went missing'
        added = [r for r in after if r not in before]
        assert len(added) == 2 and len(after) == len(before) + 2, (rel, added)
        report[rel] = {'rows': len(after), 'added': added}
    report['names_tool_sites'] = rep['sites']
    return files


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the installed archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    files = dict(base)
    report = {}

    # 1. terrain
    assert TRN not in base, 'the base already carries a hoth.trn: rebuild the den layer on that copy instead'
    assert sha(trn_iff.client_file(TRN)) == TRN_SOURCE_SHA, "the client's hoth.trn is not the one Fable patched"
    trn = open(TRN_STAGED, 'rb').read()
    assert sha(trn) == TRN_STAGED_SHA, 'Fable-hoth-batchB/staged/client/terrain/hoth.trn changed'
    assert trn_iff.build(trn_iff.parse(trn)) == trn
    files[TRN] = trn
    report[TRN] = {'from': 'Fable-hoth-batchB/staged/client/terrain/hoth.trn', 'sha256': TRN_STAGED_SHA,
                   'source_sha256': TRN_SOURCE_SHA}

    # 2. map names for the dens
    files.update(build_names(base, report))

    # 3. the badge
    data, src = source(base, BADGE_MAP)
    files[BADGE_MAP], report['badge_map'] = merge_badge_map(data)
    report['badge_map']['from'] = src
    for rel, text in ((BADGE_N, BADGE_NAME), (BADGE_D, BADGE_DESC)):
        data, src = source(base, rel)
        files[rel], report[rel] = merge_stf(data, BADGE[1], text)
        report[rel]['from'] = src

    # 4. the pale blue rancor
    files.update(build_chain(base, report))

    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))

    ours = tre_write.read(out)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    dropped = sorted(n for n in base if n not in ours)
    new = sorted(n for n in ours if n not in base)
    assert all(ours[n] == files[n] for n in files)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped),
        'changed': changed, 'new': new, 'dropped': dropped, 'report': report,
    }
    with open(os.path.join(HERE, 'checks-client.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1, default=list)
    assert not dropped, dropped
    unchanged_names = {rel for rel in NAME_FILES if rel not in files or files[rel] == base[rel]}
    assert set(changed) | set(new) == TOUCHED - unchanged_names, sorted((set(changed) | set(new)) ^ TOUCHED)
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new')}, indent=1))
    print('Hoth leftovers client step: PASS (%d changed, %d new, every other entry byte-identical)' % (len(changed), len(new)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
