"""Vong look test, step 4, the client half: our Vong armour as new wearables = any base archive + the clone chain
(Claude, 17 Oct 2026). Nothing is installed.

The owner's mix (17 Oct, "Mix: bone + s02 collar"): the stock bone s01 arms, legs, boots and gloves and the stock
marauder s02 chest, each cloned under a same-length new name so nothing a player already wears changes:

  object/tangible/wearables/armor/bone/shared_armor_bone_s01_<p>.iff        -> .../armor/vong/shared_armor_vong_s01_<p>.iff
  object/tangible/wearables/armor/marauder/shared_armor_marauder_s02_chest_plate.iff
                                                                            -> .../armor/vongcrab/shared_armor_vongcrab_s02_chest_plate.iff
  appearance/<name>_{m,f}.sat, mesh/<name>_{m,f}.lmg, mesh/<name>_{m,f}_l0-3.mgn   (both genders, all four LODs)
  shader/armor_vong_*.sht, shader/armor_vongcrab_chest_s02_*.sht            (each with our colour texture as MAIN)
  texture/armor_vong_*.dds, texture/armor_vongcrab_chest_s02*.dds           (ours: staged by convert_vonduu.py)
  misc/object_template_crc_string_table.iff                                 (+ 8 rows)

Every file except the rebound shaders differs from its stock source only in the renamed letters (same length, so no
IFF size changes; each swap's count is asserted, and the differing bytes are counted). Kept stock and referenced by
name: the meshes' geometry and skeleton weights, the normal maps (_n), the lookup textures, the effects, and the
marauder chest's chainmail shader. Our colour textures have alpha 0 (the shaders' hue mask), so hue = colour 0.
Shaders whose colour 0 (the PAL tagged MAIN) is not palette/white.pal get it rebound to palette/white.pal, default
index 0, as the ice rancor's builder rebinds its palette: the bone leggings' waist strip (wr_metal 0) and the four
marauder chest shaders (wr_metal 61, an olive brown; wr_cloth_general 120). Every other base entry comes through
byte for byte.

    C:/Users/Pengw/miniconda3/python.exe -I build_vong_client.py [--base PATH] [--out PATH]
Default base: ../../../work/nal-hutta-life/local_planets-nalhutta-life.tre (sha256 b01e9f44..., the installed archive).
Default out:  ../../../work/vong-look/local_planets-vong-look.tre (+ .sha256); checks in ../checks-client.json.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VONG = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(VONG)
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'swgfmt'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'nal-hutta-life', 'local_planets-nalhutta-life.tre')
DEFAULT_BASE_SHA_PREFIX = 'b01e9f44'
DEFAULT_OUT = os.path.join(H, 'work', 'vong-look', 'local_planets-vong-look.tre')
TEXTURE_DIR = os.path.join(VONG, 'staged', 'client', 'texture')
CRC_TABLE = 'misc/object_template_crc_string_table.iff'
WHITE = b'palette/white.pal'

BONE = ['bicep_l', 'bicep_r', 'bracer_l', 'bracer_r', 'boots', 'gloves', 'leggings']
# (stock object template, stock appearance stem, new object template, new appearance stem)
PIECES = [('object/tangible/wearables/armor/bone/shared_armor_bone_s01_%s.iff' % p, 'armor_bone_s01_' + p,
           'object/tangible/wearables/armor/vong/shared_armor_vong_s01_%s.iff' % p, 'armor_vong_s01_' + p) for p in BONE]
PIECES.append(('object/tangible/wearables/armor/marauder/shared_armor_marauder_s02_chest_plate.iff',
               'armor_marauder_s02_chest_plate',
               'object/tangible/wearables/armor/vongcrab/shared_armor_vongcrab_s02_chest_plate.iff',
               'armor_vongcrab_s02_chest_plate'))
KEEP_SHADERS = {'shader/armor_marauder_chain_s02_apb15.sht'}   # the chainmail cut-out keeps its stock texture


def shader_plan():
    """stock shader -> (new shader, stock MAIN texture, new MAIN texture, rebind colour 0 to white)."""
    plan = {}
    for part in ('bicep', 'bracer', 'boots', 'gloves', 'leggings'):
        for sm in ('', '_sm'):
            plan['shader/armor_bone_%s_hcsb21%s.sht' % (part, sm)] = (
                'shader/armor_vong_%s_hcsb21%s.sht' % (part, sm),
                'texture/armor_bone_%s%s.dds' % (part, sm), 'texture/armor_vong_%s%s.dds' % (part, sm), False)
    plan['shader/armor_bone_leggings_waist_hcsb21.sht'] = (
        'shader/armor_vong_leggings_waist_hcsb21.sht', 'texture/armor_bone_leggings.dds',
        'texture/armor_vong_leggings.dds', True)
    for kind in ('hcsb21', 'hue_hc8'):
        for sm in ('', '_sm'):
            plan['shader/armor_marauder_chest_s02_%s%s.sht' % (kind, sm)] = (
                'shader/armor_vongcrab_chest_s02_%s%s.sht' % (kind, sm),
                'texture/armor_marauder_chest_s02%s.dds' % sm, 'texture/armor_vongcrab_chest_s02%s.dds' % sm, True)
    for old, (new, t_old, t_new, _) in plan.items():
        assert len(old) == len(new) and len(t_old) == len(t_new), (old, new)
    return plan


SHADERS = shader_plan()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def source(base, rel):
    if rel in base:
        return base[rel], 'base'
    data = trn_iff.client_file(rel)
    assert data is not None, rel
    return data, trn_iff.client_index()[rel]


def swaps(data, pairs):
    """Same-length swaps, each with its exact expected count; returns (new data, differing bytes expected)."""
    expected = 0
    for old, new, count in pairs:
        assert len(old) == len(new), (old, new)
        assert data.count(old) == count, (old, data.count(old), count)
        data = data.replace(old, new)
        expected += count * sum(a != b for a, b in zip(old, new))
    return data, expected


def differing(a, b):
    assert len(a) == len(b)
    return sum(x != y for x, y in zip(a, b))


def rebind_white(data):
    """Point the PAL tagged MAIN (colour 0 of the hue lerp) at palette/white.pal, default index 0."""
    nodes = trn_iff.parse(data)
    assert trn_iff.build(nodes) == data, 'shader does not round-trip'
    pals = [n for _, n in trn_iff.walk(nodes) if not n.is_form and n.tag == 'PAL ']
    main = [p for p in pals if re.match(rb'index_color_\d\x00\x01NIAM', p.data)]
    assert len(main) == 1, [p.data for p in pals]
    p = main[0]
    head = p.data[:p.data.index(b'NIAM') + 4]
    old_palette = p.data[len(head):p.data.index(b'\x00', len(head))]
    old_default = struct.unpack('<i', p.data[-4:])[0]
    assert len(p.data) == len(head) + len(old_palette) + 1 + 4, p.data
    p.data = head + WHITE + b'\x00' + struct.pack('<i', 0)
    out = trn_iff.build(nodes)
    assert trn_iff.build(trn_iff.parse(out)) == out
    return out, {'variable': head[:head.index(b'\x00')].decode(), 'from': old_palette.decode(), 'from_default': old_default,
                 'to': WHITE.decode(), 'to_default': 0}


def build_chain(base, report):
    files, swap_only = {}, {}
    for obj_old, stem_old, obj_new, stem_new in PIECES:
        assert len(obj_old) == len(obj_new) and len(stem_old) == len(stem_new)
        data, _ = source(base, obj_old)
        sat_f_old, sat_f_new = ('appearance/%s_f.sat' % stem_old).encode(), ('appearance/%s_f.sat' % stem_new).encode()
        files[obj_new], exp = swaps(data, [(sat_f_old, sat_f_new, 1)])
        swap_only[obj_new] = (data, exp)
        for g in ('m', 'f'):
            sat_old, sat_new = 'appearance/%s_%s.sat' % (stem_old, g), 'appearance/%s_%s.sat' % (stem_new, g)
            lmg_old, lmg_new = 'appearance/mesh/%s_%s.lmg' % (stem_old, g), 'appearance/mesh/%s_%s.lmg' % (stem_new, g)
            data, _ = source(base, sat_old)
            files[sat_new], exp = swaps(data, [(lmg_old.encode(), lmg_new.encode(), 1)])
            swap_only[sat_new] = (data, exp)
            data, _ = source(base, lmg_old)
            prefix_old = ('appearance/mesh/%s_%s_l' % (stem_old, g)).encode()
            prefix_new = ('appearance/mesh/%s_%s_l' % (stem_new, g)).encode()
            files[lmg_new], exp = swaps(data, [(prefix_old, prefix_new, 4)])
            swap_only[lmg_new] = (data, exp)
            for lod in range(4):
                mgn_old = 'appearance/mesh/%s_%s_l%d.mgn' % (stem_old, g, lod)
                mgn_new = 'appearance/mesh/%s_%s_l%d.mgn' % (stem_new, g, lod)
                data, _ = source(base, mgn_old)
                used = sorted(set(m.decode() for m in re.findall(rb'shader/[a-z0-9_]+\.sht', data)))
                assert set(used) <= set(SHADERS) | KEEP_SHADERS, (mgn_old, used)
                pairs = [(s.encode(), SHADERS[s][0].encode(), data.count(s.encode())) for s in used if s in SHADERS]
                files[mgn_new], exp = swaps(data, pairs)
                swap_only[mgn_new] = (data, exp)
                leftover = sorted(set(m.decode() for m in re.findall(rb'shader/[a-z0-9_]+\.sht', files[mgn_new])))
                assert set(leftover) - {SHADERS[s][0] for s in SHADERS} <= KEEP_SHADERS, (mgn_new, leftover)
    report['rebound'] = {}
    for old, (new, t_old, t_new, rebind) in SHADERS.items():
        data, _ = source(base, old)
        out, exp = swaps(data, [(t_old.encode(), t_new.encode(), 1)])
        if rebind:
            out, report['rebound'][new] = rebind_white(out)
        else:
            swap_only[new] = (data, exp)
        files[new] = out
    for rel, (old, exp) in swap_only.items():
        assert differing(old, files[rel]) == exp, (rel, differing(old, files[rel]), exp)
        assert trn_iff.build(trn_iff.parse(files[rel])) == files[rel], rel
    report['swap_only_files'] = len(swap_only)
    report['rebound_files'] = len(report['rebound'])
    return files


def add_textures(report):
    files = {}
    names = sorted({t_new for _, t_old, t_new, _ in SHADERS.values()})
    for rel in names:
        b = open(os.path.join(TEXTURE_DIR, rel.split('/')[-1]), 'rb').read()
        h, w = struct.unpack_from('<II', b, 12)
        stock = trn_iff.client_file(SHADERS_BY_TEXTURE[rel])
        sh, sw = struct.unpack_from('<II', stock, 12)
        assert b[:4] == b'DDS ' and b[84:88] == b'DXT5' and (w, h) == (sw, sh), (rel, w, h, sw, sh)
        assert struct.unpack_from('<I', b, 28)[0] == struct.unpack_from('<I', stock, 28)[0], rel
        files[rel] = b
    report['textures'] = {rel: {'bytes': len(b), 'sha256': sha(b)} for rel, b in files.items()}
    return files


SHADERS_BY_TEXTURE = {t_new: t_old for _, t_old, t_new, _ in SHADERS.values()}


def add_crc_rows(base, report):
    data, src = source(base, CRC_TABLE)
    t = st.read_cstb(data)
    assert st.write_cstb(t['entries'], t['version']) == data, 'CRC table does not round-trip'
    names = {n for _, n in t['entries']}
    crcs = {c for c, _ in t['entries']}
    assert st.soe_crc(PIECES[0][0]) in crcs, 'soe_crc does not match the table'
    rows = []
    for _, _, obj_new, _ in PIECES:
        c = st.soe_crc(obj_new)
        assert obj_new not in names and c not in crcs, obj_new
        rows.append((c, obj_new))
    out = st.write_cstb(t['entries'] + rows, t['version'])
    assert st.read_cstb(out)['entries'] == sorted(t['entries'] + rows)
    report['crc_table'] = {'from': src, 'rows': len(t['entries']) + len(rows), 'added': rows}
    return {CRC_TABLE: out}


REF = re.compile(rb'(?:appearance|shader|texture|effect|palette)[/\\][a-z0-9_/\\]+\.(?:sat|lmg|mgn|skt|sht|dds|eft|pal)')


def closure(files, base):
    """Every path our new files name must resolve in the new archive, the base or the client."""
    idx = trn_iff.client_index()
    missing = {}
    for rel, data in files.items():
        if rel == CRC_TABLE or rel.endswith('.dds'):
            continue
        for m in REF.findall(data):
            ref = m.decode().replace('\\', '/')
            if ref not in files and ref not in base and ref not in idx:
                missing.setdefault(rel, []).append(ref)
    return missing


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
    report = {}
    new_files = {}
    new_files.update(build_chain(base, report))
    new_files.update(add_textures(report))
    new_files.update(add_crc_rows(base, report))
    clash = sorted(n for n in new_files if n in base and n != CRC_TABLE)
    assert not clash, clash
    missing = closure(new_files, base)
    assert not missing, missing

    files = dict(base)
    files.update(new_files)
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
    assert not dropped and changed == [CRC_TABLE] and set(new) == set(new_files) - {CRC_TABLE}, (dropped, changed)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed),
        'changed': changed, 'new': new, 'report': report,
    }
    with open(os.path.join(VONG, 'checks-client.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1, default=list)
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed')}, indent=1))
    print('new entries: %d (%d swap-only clones, %d rebound shaders, %d textures, %d CRC rows)' % (
        len(new), report['swap_only_files'], report['rebound_files'], len(report['textures']),
        len(report['crc_table']['added'])))
    print('Vong look client step: PASS (1 changed, %d new, every other entry byte-identical)' % len(new))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
