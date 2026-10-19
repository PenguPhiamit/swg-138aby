"""Light whip step 1 (L1, Claude, 18 Oct 2026): the client half of the stiff whip. It is also what a player without the
graphics hook will see once the bending whip exists. Design: ../Documentation-support/lightwhip-design.md.

Owner, 18 Oct ~7:05 PM: "build step 1 of the light whip: the whip hilt template, the long thin blade with its own
shaders and trail, and the server saber template with loot and schematic. Built, not installed."

Read from the client (read only): a blade file (.lsb) is one hilt appearance, one straight blade (LGTH 1.2, WDTH 0.15 on
the leather hilt) and the idle hum. The swing trail is the surface swept between the hilt's hardpoints tr1s (0.126) and
tr1e (1.125), so a longer blade also needs those hardpoints moved out, or the trail would cover only the first metre.

This step adds, for the whip only (no stock file changes except the tables and string files below):
  appearance/wp_mle_lightwhip.apt, appearance/lod/wp_mle_lightwhip.lod, appearance/mesh/wp_mle_lightwhip_l0..2.msh
        the leather-grip one-handed hilt, with tr1e at LENGTH - 0.075 and whp1 at 0.625 x LENGTH (stock proportions)
  appearance/wp_mle_lightwhip_blade.lsb
        that hilt with a long, thin blade (LENGTH, WIDTH) and the whip's own blade shader; stock hum, open and close
  shader/lightwhipblade.sht, shader/lightwhipblade_a..d.sht
        the stock switching blade shader and its four frames (stock textures, crystal tint kept) on the whip's effect
  effect/e_h_lightwhipblade.eft
        the stock blade effect, with its ps_2_0 pass on the whip's pixel program (ps_1_1 and fixed-function stay stock)
  pixel_program/e_h_lightwhipblade_ps20.psh
        e_h_lightwhipblade_ps20.hlsl next to this script: the O14 blade program (ghostfire included) with the white core
        at 75%; its own instructions give it its own id for the O15 hook
  the trail (owner, 8:26 PM: "the trail; none without a specific crystal"; 8:45 PM: "the ghostfire crystal also has no
        trails on the whip hilt"). Default --trail ghostfire: the whip's swoosh row points at O14's ghostfire-only trail,
        appearance/sw_ghostfire_trail.swh (its program draws the strobe bars for palette entries 32-40 and nothing for any
        other crystal, on the ps_2_0 path). --trail none: appearance/sw_lightwhip.swh, the stock saber trail on a fully
        transparent texture (shader/sw_lightwhip_none.sht, texture/sw_lightwhip_none.dds). --trail S: sw_lightwhip.swh as
        the stock trail lasting S seconds
  object/weapon/melee/sword/crafted_saber/shared_sword_lightwhip.iff
        the s5 gen4 one-handed saber template with the whip blade and its own name and description
  object/draft_schematic/weapon/lightsaber/shared_lightsaber_lightwhip.iff
        the gen4 one-handed saber schematic, crafting the whip
  object/tangible/loot/loot_schematic/shared_lightwhip_schematic.iff
        a loot schematic (a handheld viewscreen, like the Geonosian schematics) with its own name and description
  changed  datatables/weapon/swoosh.iff                        + the whip's trail row (UseObjectHue 1)
  changed  misc/object_template_crc_string_table.iff           + the three new templates' CRCs
  changed  string/en/weapon_name.stf, weapon_detail.stf          + sword_lightwhip
  changed  string/en/craft_weapon_ingredients_n.stf, _d.stf      + lightwhip_schematic

The server half (saber template, schematic, loot schematic, loot items and group) is server/lightwhip-dev.patch.
Every other entry of the base archive stays byte for byte.

    C:/Users/Pengw/miniconda3/python.exe -I build_lightwhip.py [--base PATH] [--out PATH] [--length M] [--width M] [--trail S]
Default base: ../../work/ossus-ghostfire-crystal/local_planets-ghostfire-crystal.tre (O14, sha256 a0cca018..., built,
not installed). Default out: ../../work/lightwhip/local_planets-lightwhip.tre (+ .sha256); checks in ./checks-lightwhip.json.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o14-ghostfire-crystal'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o15-mirage'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
from swgfmt import swg_tables  # noqa: E402
import build_ghostfire_crystal as o14  # noqa: E402  (fxc compile with the client's include files)
import blade_ids  # noqa: E402  (the O15 hook's pixel program id; read only)

BASE_SHA_PREFIX = 'a0cca018'

SRC_LSB = 'appearance/wp_mle_sword_lightsaber_blade_leather.lsb'
SRC_APT = 'appearance/wp_mle_sword_lightsaber_leather.apt'
SRC_LOD = 'appearance/lod/wp_mle_sword_lightsaber_leather.lod'
SRC_MSH = 'mesh/wp_mle_sword_lightsaber_leather_l%d.msh'      # as the LOD names them (under appearance/)
SRC_SHARED = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_s5_gen4.iff'
SRC_DS = 'object/draft_schematic/weapon/lightsaber/shared_lightsaber_one_hand_gen4.iff'
SRC_LS = 'object/tangible/loot/loot_schematic/shared_geonosian_sonic_blaster_schematic.iff'
STOCK_BLADE_SHT = 'shader/lightsaberblade.sht'
STOCK_FRAME_SHT = 'shader/lightsaberblade_%s.sht'
STOCK_EFT = 'effect/e_h_lightsaberblade.eft'
STOCK_PSH = 'pixel_program/e_h_lightsaberblade_ps20.psh'
STOCK_SWH = 'appearance/sw_light_saber_white.swh'
STOCK_TRAIL_SHT = 'shader/sw_light_saber_add.sht'
SWOOSH = 'datatables/weapon/swoosh.iff'
CRC = 'misc/object_template_crc_string_table.iff'

APT = 'appearance/wp_mle_lightwhip.apt'
LOD = 'appearance/lod/wp_mle_lightwhip.lod'
MSH = 'mesh/wp_mle_lightwhip_l%d.msh'
LSB = 'appearance/wp_mle_lightwhip_blade.lsb'
BLADE_SHT = 'shader/lightwhipblade.sht'
FRAME_SHT = 'shader/lightwhipblade_%s.sht'
EFT = 'effect/e_h_lightwhipblade.eft'
PSH = 'pixel_program/e_h_lightwhipblade_ps20.psh'
SWH = 'appearance/sw_lightwhip.swh'
NONE_SHT = 'shader/sw_lightwhip_none.sht'
NONE_DDS = 'texture/sw_lightwhip_none.dds'
SHARED = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightwhip.iff'
DS = 'object/draft_schematic/weapon/lightsaber/shared_lightsaber_lightwhip.iff'
LS = 'object/tangible/loot/loot_schematic/shared_lightwhip_schematic.iff'
SOURCE = os.path.join(HERE, 'e_h_lightwhipblade_ps20.hlsl')

STOCK_LENGTH, STOCK_TR1E, STOCK_WHP1, STOCK_TR1S = 1.2, 1.125, 0.75, 0.1258

# Our own words (Wookieepedia Legends, "Lightwhip", read 18 Oct 2026; its text is not copied).
STRINGS = {
    'string/en/weapon_name.stf': {'sword_lightwhip': 'Lightwhip'},
    'string/en/weapon_detail.stf': {'sword_lightwhip': (
        'A rare cousin of the lightsaber. Several small crystals feed a long, flexible strand of energy instead of a '
        'rigid blade, giving the wielder a reach few duelists know how to answer. It is hard to master, poor at '
        'blocking, and weaker against heavy armor than a true blade.')},
    'string/en/craft_weapon_ingredients_n.stf': {'lightwhip_schematic': 'Lightwhip Schematic'},
    'string/en/craft_weapon_ingredients_d.stf': {'lightwhip_schematic': (
        'Notes on building a lightwhip, kept by the witches of Dathomir. A Jedi who has mastered lightsaber '
        'construction can learn to make one from them.')},
}


def find(nodes, pred):
    return [n for _, n in trn_iff.walk(nodes) if pred(n)]


def cstr(b):
    return b[:b.index(b'\0')].decode('latin-1')


def chunks(nodes, tag):
    return find(nodes, lambda n: not n.is_form and n.tag == tag)


def set_prop(nodes, key, new, old=None):
    """Set the one template property chunk (XXXX: key, NUL, value) named key; check its old value when given."""
    hits = find(nodes, lambda n: not n.is_form and n.tag == 'XXXX' and n.data.startswith(key + b'\0'))
    assert len(hits) == 1, (key, len(hits))
    if old is not None:
        assert hits[0].data[len(key) + 1:] == old, (key, hits[0].data)
    hits[0].data = key + b'\0' + new


def string_id(table, key):
    return b'\x01\x01' + table.encode() + b'\0\x01' + key.encode() + b'\0'


def move_hardpoints(nodes, length):
    """tr1e to length - 0.075 and whp1 to 0.625 x length (the stock proportions); tr1s stays. Returns the new points."""
    want = {'tr1e': (STOCK_TR1E, length - (STOCK_LENGTH - STOCK_TR1E)),
            'whp1': (STOCK_WHP1, STOCK_WHP1 * length / STOCK_LENGTH),
            'tr1s': (STOCK_TR1S, STOCK_TR1S)}
    forms = find(nodes, lambda n: n.is_form and n.form == 'HPTS')
    assert len(forms) == 1, len(forms)
    seen = {}
    for hp in forms[0].children:
        assert hp.tag == 'HPNT' and len(hp.data) >= 49
        name = cstr(hp.data[48:])
        m = list(struct.unpack_from('<12f', hp.data))
        old, new = want[name]
        assert abs(m[7] - old) < 1e-4 and m[3] == 0.0 and m[11] == 0.0, (name, m)
        m[7] = new
        hp.data = struct.pack('<12f', *m) + hp.data[48:]
        seen[name] = round(new, 4)
    assert sorted(seen) == sorted(want), seen
    return seen


_stock_index = None


def stock_index():
    """{lower name: archive}: the client's archives in trn_iff.client_index's order, without local_planets.tre. The
    installed local_planets.tre may already hold the whip, and every older entry of it is in the base anyway."""
    global _stock_index
    if _stock_index is None:
        sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
        import client_load_order as clo  # noqa: E402
        trees, _, _ = clo.load_order()
        order = [n for _, n in sorted(trees, key=lambda t: t[0])]
        mtg = sorted(n for n in os.listdir(trn_iff.CLIENT) if n.lower().startswith('mtg_') and n.lower().endswith('.tre'))
        _stock_index = {}
        for n in mtg + order:
            path = os.path.join(trn_iff.CLIENT, n)
            if n.lower() != 'local_planets.tre' and os.path.exists(path):
                for entry in trn_iff.list_tre(path):
                    _stock_index[entry] = n
    return _stock_index


def stock_file(name):
    archive = stock_index().get(name.lower())
    return trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, archive), name) if archive else None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=os.path.join(H, 'work', 'ossus-ghostfire-crystal', 'local_planets-ghostfire-crystal.tre'))
    ap.add_argument('--out', default=os.path.join(H, 'work', 'lightwhip', 'local_planets-lightwhip.tre'))
    ap.add_argument('--length', type=float, default=4.5,
                    help='blade length in metres (stock saber 1.2; owner, 8:26 PM: "a little shorter" than the first 2.5; '
                         'then 9:10 PM, with the bend: "a good bit longer", "4-5", so it can coil at the feet)')
    ap.add_argument('--width', type=float, default=0.09, help='blade glow width in metres (stock saber 0.15)')
    ap.add_argument('--trail', default='ghostfire',
                    help='ghostfire (default): O14\'s ghostfire-only trail; none: no visible trail; or seconds: the stock '
                         'saber trail lasting that long (stock 0.06)')
    args = ap.parse_args(argv)
    if args.trail not in ('ghostfire', 'none'):
        args.trail = float(args.trail)
        assert 0.03 <= args.trail <= 3.0, args.trail
    assert 1.2 <= args.length <= 6.0 and 0.02 <= args.width <= 0.3
    base_bytes = open(args.base, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    if not base_sha.startswith(BASE_SHA_PREFIX):
        print('NOTE: base is %s, not O14 %s...' % (base_sha[:8], BASE_SHA_PREFIX))
    base = tre_write.read(base_bytes)[0]

    def src(name):
        data = base.get(name) or stock_file(name)
        assert data, 'missing ' + name
        return data

    msh_names = ['appearance/' + MSH % k for k in range(3)]
    new_names = [APT, LOD, LSB, BLADE_SHT, EFT, PSH, SWH, SHARED, DS, LS, NONE_SHT, NONE_DDS] + msh_names + \
        [FRAME_SHT % c for c in 'abcd']
    clash = [n for n in new_names if n in base or stock_index().get(n)]
    assert not clash, 'already exist: %s' % clash
    added, changed = {}, {}

    # ---- the hilt: the leather one-handed hilt with its trail and mid-blade hardpoints moved out
    apt = trn_iff.parse(src(SRC_APT))
    name = chunks(apt, 'NAME')
    assert len(name) == 1 and cstr(name[0].data) == SRC_LOD
    name[0].data = LOD.encode() + b'\0'
    added[APT] = trn_iff.build(apt)

    lod = trn_iff.parse(src(SRC_LOD))
    chld = chunks(lod, 'CHLD')
    assert sorted(cstr(c.data[4:]) for c in chld) == sorted(SRC_MSH % k for k in range(3)), [c.data for c in chld]
    for c in chld:
        level = int(cstr(c.data[4:])[-5])
        c.data = c.data[:4] + (MSH % level).encode() + b'\0'
    hardpoints = move_hardpoints(lod, args.length)
    added[LOD] = trn_iff.build(lod)
    for k in range(3):
        msh = trn_iff.parse(src('appearance/' + SRC_MSH % k))
        assert msh[0].form == 'MESH'
        assert move_hardpoints(msh, args.length) == hardpoints
        added['appearance/' + MSH % k] = trn_iff.build(msh)

    # ---- the blade: switching shader > 4 frame shaders (stock textures and crystal tint) > our effect > our program
    switch = trn_iff.parse(src(STOCK_BLADE_SHT))
    assert switch[0].form == 'SWSH'
    frame_names = chunks(switch, 'NAME')
    assert [cstr(n.data) for n in frame_names] == [STOCK_FRAME_SHT % c for c in 'abcd']
    for n, c in zip(frame_names, 'abcd'):
        n.data = (FRAME_SHT % c).encode() + b'\0'
    added[BLADE_SHT] = trn_iff.build(switch)

    for c in 'abcd':
        frame = trn_iff.parse(src(STOCK_FRAME_SHT % c))
        assert frame[0].form == 'CSHD'
        assert [x.form for x in frame[0].children[0].children] == ['SSHT', 'TFAC'], 'frame layout'
        eff = [n for n in chunks(frame, 'NAME') if n.data.startswith(b'effect')]
        assert len(eff) == 1 and cstr(eff[0].data) == 'effect\\e_h_lightsaberblade.eft', eff
        eff[0].data = EFT.replace('/', '\\').encode() + b'\0'
        added[FRAME_SHT % c] = trn_iff.build(frame)

    eft = trn_iff.parse(src(STOCK_EFT))
    assert eft[0].form == 'EFCT'
    ps20 = b'\x01' + STOCK_PSH.encode() + b'\0'
    hits = [n for n in find(eft, lambda n: n.is_form and n.form == 'PPSH')
            for d in chunks([n], 'DATA') if d.data == ps20]
    assert len(hits) == 1, len(hits)
    for d in chunks(hits, 'DATA'):
        if d.data == ps20:
            d.data = b'\x01' + PSH.encode() + b'\0'
    assert sum(1 for d in chunks(eft, 'DATA') if d.data == b'\x01' + PSH.encode() + b'\0') == 1
    added[EFT] = trn_iff.build(eft)

    psh = trn_iff.parse(src(STOCK_PSH))          # the O14 program in the base: PSHP > 0000 > PSRC, PEXE
    ver = psh[0].children[0]
    assert psh[0].form == 'PSHP' and ver.form == '0000' and [c.tag for c in ver.children] == ['PSRC', 'PEXE']
    o14_code = ver.children[1].data
    stock_src = ver.children[0].data
    source = open(SOURCE, 'rb').read().replace(b'\r\n', b'\n')
    code, dis = o14.compile_ps20(source)
    for want in ('ps_2_0', 'textureFactor          c3', 'alphaFadeOpacityHolder c7', 'diffuseMap             s0'):
        assert want in dis, 'compiled shader lacks %r' % want
    slots = int(dis.split('approximately ')[1].split(' instruction')[0])
    assert slots <= 64, slots
    ver.children[0].data = source + (b'\0' if stock_src.endswith(b'\0') else b'')
    ver.children[1].data = code
    added[PSH] = trn_iff.build(psh)
    ids = {'stock': '%08x' % blade_ids.shader_id(blade_ids.pexe(stock_file(STOCK_PSH))),
           'o14': '%08x' % blade_ids.shader_id(o14_code), 'whip': '%08x' % blade_ids.shader_id(code)}
    assert len(set(ids.values())) == 3, ids

    lsb = trn_iff.parse(src(SRC_LSB))
    (base_name,) = chunks(lsb, 'BASE')
    assert cstr(base_name.data) == SRC_APT
    base_name.data = APT.encode() + b'\0'
    (shdr,) = chunks(lsb, 'SHDR')
    assert cstr(shdr.data) == STOCK_BLADE_SHT
    shdr.data = BLADE_SHT.encode() + b'\0'
    (lgth,), (wdth,) = chunks(lsb, 'LGTH'), chunks(lsb, 'WDTH')
    assert abs(struct.unpack('<f', lgth.data)[0] - STOCK_LENGTH) < 1e-6
    assert abs(struct.unpack('<f', wdth.data)[0] - 0.15) < 1e-6
    lgth.data, wdth.data = struct.pack('<f', args.length), struct.pack('<f', args.width)
    added[LSB] = trn_iff.build(lsb)

    # ---- the trail: O14's ghostfire-only trail (default), none (the stock trail on a transparent texture), or the stock
    # trail, longer lived
    swh = trn_iff.parse(stock_file(STOCK_SWH))   # the client's own: O14 overrides this file since a0cca018
    assert swh[0].form == 'SWSH' and swh[0].children[0].form == '0000'
    data = [c for c in swh[0].children[0].children if not c.is_form][-1]
    assert abs(struct.unpack_from('<f', data.data, 16)[0] - 0.06) < 1e-6
    if args.trail == 'ghostfire':
        assert o14.GTRAIL_SWH in base and o14.GTRAIL_SHT in base, 'the base lacks O14\'s ghostfire-only trail'
        trail_row = o14.GTRAIL_SWH
    elif args.trail != 'none':
        data.data = data.data[:16] + struct.pack('<f', args.trail) + data.data[20:]
    else:
        ptex = [x for x in chunks(swh, '0000') if x.data.startswith(b'shader/')]
        assert len(ptex) == 1 and cstr(ptex[0].data) == STOCK_TRAIL_SHT, ptex
        ptex[0].data = NONE_SHT.encode() + ptex[0].data[ptex[0].data.index(b'\0'):]
        sht = trn_iff.parse(stock_file(STOCK_TRAIL_SHT))
        tex = [n for n in chunks(sht, 'NAME') if n.data.startswith(b'texture/')]
        assert len(tex) == 1, tex
        tex[0].data = NONE_DDS.encode() + b'\0'
        added[NONE_SHT] = trn_iff.build(sht)
        added[NONE_DDS], _ = o14.o13.dds_argb([[(0, 0, 0, 0)] * 4 for _ in range(4)])
    if args.trail != 'ghostfire':
        added[SWH] = trn_iff.build(swh)
        trail_row = SWH

    # ---- the templates
    shared = trn_iff.parse(src(SRC_SHARED))
    set_prop(shared, b'appearanceFilename', b'\x01' + LSB.encode() + b'\0', b'\x01' + SRC_LSB.encode() + b'\0')
    set_prop(shared, b'objectName', string_id('weapon_name', 'sword_lightwhip'),
             string_id('weapon_name', 'sword_lightsaber_type5'))
    set_prop(shared, b'detailedDescription', string_id('weapon_detail', 'sword_lightwhip'),
             string_id('weapon_detail', 'sword_lightsaber_gen4'))
    added[SHARED] = trn_iff.build(shared)

    ds = trn_iff.parse(src(SRC_DS))
    set_prop(ds, b'craftedSharedTemplate', b'\x01' + SHARED.encode() + b'\0',
             b'\x01object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_gen4.iff\0')
    added[DS] = trn_iff.build(ds)

    ls = trn_iff.parse(src(SRC_LS))
    set_prop(ls, b'objectName', string_id('craft_weapon_ingredients_n', 'lightwhip_schematic'),
             string_id('craft_weapon_ingredients_n', 'geonosian_sonic_blaster_schematic'))
    set_prop(ls, b'detailedDescription', string_id('craft_weapon_ingredients_d', 'lightwhip_schematic'),
             string_id('craft_weapon_ingredients_d', 'geonosian_sonic_blaster_schematic'))
    added[LS] = trn_iff.build(ls)

    # ---- the tables and strings
    old = src(SWOOSH)
    table = swg_tables.read_dtii(old)
    assert swg_tables.write_dtii(table) == old, 'swoosh table does not round-trip'
    assert [r for r in table['rows'] if r[0] == SRC_SHARED] == [[SRC_SHARED, STOCK_SWH, 1]]
    assert not [r for r in table['rows'] if r[0] == SHARED]
    table['rows'].append([SHARED, trail_row, 1])
    changed[SWOOSH] = swg_tables.write_dtii(table)

    old_crc = src(CRC)
    crc = swg_tables.read_cstb(old_crc)
    assert swg_tables.write_cstb(crc['entries'], crc['version']) == old_crc, 'CRC table does not round-trip'
    have = {c for c, _ in crc['entries']}
    crcs = {n: swg_tables.soe_crc(n) for n in (SHARED, DS, LS)}
    assert not have & set(crcs.values()) and len(set(crcs.values())) == 3, 'CRC clash'
    changed[CRC] = swg_tables.write_cstb(crc['entries'] + [(c, n) for n, c in crcs.items()], crc['version'])

    for path, wanted in STRINGS.items():
        raw = src(path)
        stf = swg_tables.read_stf(raw)
        assert swg_tables.write_stf(stf) == raw, path + ' does not round-trip'
        before = dict(swg_tables.stf_items(stf))
        for key, text in wanted.items():
            assert key not in before, (path, key)
            swg_tables.stf_add(stf, key, text)
        changed[path] = swg_tables.write_stf(stf)
        after = dict(swg_tables.stf_items(swg_tables.read_stf(changed[path])))
        assert all(after[k] == v for k, v in before.items()) and all(after[k] == v for k, v in wanted.items())

    for n, d in added.items():
        assert n.endswith('.dds') or trn_iff.build(trn_iff.parse(d)) == d, n

    files = dict(base)
    files.update(added)
    files.update(changed)
    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    sha = hashlib.sha256(out).hexdigest()
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (sha, os.path.basename(args.out)))

    ours = tre_write.read(out)[0]
    same = [n for n in base if n not in changed]
    assert all(ours[n] == base[n] for n in same), 'a base entry changed'
    assert all(ours[n] == added[n] for n in added) and all(ours[n] == changed[n] for n in changed)
    assert sorted(ours) == sorted(set(base) | set(added) | set(changed)), 'entry list'
    new_entries = sorted(n for n in ours if n not in base)

    checks = {'base_sha256': base_sha, 'base_entries': len(base), 'out_sha256': sha, 'out_bytes': len(out),
              'out_entries': len(ours), 'unchanged_entries': len(same),
              'changed': sorted(n for n in changed if n in base), 'added': new_entries,
              'added_sha256': {n: hashlib.sha256(ours[n]).hexdigest() for n in new_entries},
              'settings': {'length': args.length, 'width': args.width, 'trail': args.trail, 'trail_row': trail_row},
              'hardpoints_y': hardpoints, 'template_crcs': {n: '%08x' % c for n, c in crcs.items()},
              'pixel_program_ids': ids, 'shader_slots': slots,
              'shader_code_sha256': hashlib.sha256(code).hexdigest(), 'swoosh_rows': len(table['rows']),
              'crc_entries': len(crc['entries']) + 3, 'strings': STRINGS}
    with open(os.path.join(HERE, 'checks-lightwhip.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: checks[k] for k in ('base_sha256', 'out_sha256', 'out_entries', 'changed', 'settings',
                                             'hardpoints_y', 'pixel_program_ids', 'shader_slots')}, indent=1))
    print('added %d entries: %s' % (len(new_entries), ', '.join(new_entries)))
    print('Light whip step 1: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
