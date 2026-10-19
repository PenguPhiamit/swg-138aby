"""Ossus O13: the ghostfire lightsaber gets a blade, a trail and a hum of its own (Claude, 18 Oct 2026).

Owner, 18 Oct: the ghostfire saber should be "damn near invisible with an opalescent sheen" and leave "LSD trails", and
asked for a custom shader. Read from the client (read only): every stock blade file (appearance/*.lsb) uses
shader/lightsaberblade.sht, a switching shader (SWSH: 4 frames, 1/16 s each) over lightsaberblade_a..d.sht. Each frame
is the stock effect e_h_lightsaberblade.eft, whose pixel program (its HLSL source is in the .psh) does
    rgb = texture.rgb * palette colour + texture.a        (additive blend)
so the texture's alpha is a white-hot core added after the crystal's tint. That is why the ghostfire crystal drew white
however dim its palette entry was. The look therefore needs a texture of its own, not a new effect or pixel program.

This step adds, for one new saber only (no stock file changes, so every other saber is untouched):
  texture/ghostfire_blade_0..7.dds   8 frames, 256x64 A8R8G8B8 with mips: the stock blade's glow shape (frames a..d)
                                     filled with milky pastel opal bands and a few bright flecks that drift along the
                                     blade; the white core is cut to CORE (default 10%) and the glow to GLOW (32%)
  shader/ghostfire_blade_0..7.sht    the stock frame shader (the SSHT inside lightsaberblade_a.sht) on those textures,
                                     without its palette part, so the crystal does not tint it and the texture is the look
  shader/ghostfire_blade.sht         switching shader: 8 frames at 0.1 s, so the sheen loops every 0.8 s
  sound/ghostfire_idle.snd           the stock idle hum with its two volume values 1.0 -> HUM (default 0.25)
  appearance/wp_mle_sword_lightsaber_blade_ghostfire.lsb
                                     the sleek silver one-handed blade file (hilt, light, length) with the shader and hum above
  object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire.iff
                                     the s12 gen4 one-handed saber template with that appearance (the server reads it too)
  texture/sw_ghostfire.dds, shader/sw_ghostfire.sht, appearance/sw_ghostfire.swh
                                     the swing trail: a pastel rainbow ribbon in the stock colour-band trail's shader
                                     layout, in the saber trail's file (sw_light_saber_white.swh) with only the shader changed
  changed  datatables/weapon/swoosh.iff                    + a row: the ghostfire template, sw_ghostfire.swh, UseObjectHue 0
  changed  misc/object_template_crc_string_table.iff       + the ghostfire template's CRC

The server half (the saber's server template, the loot item and the quest giving it) is server/ghostfire-saber-dev.patch.
Every other entry of the base archive stays byte for byte.

    C:/Users/Pengw/miniconda3/python.exe -I build_ghostfire_blade.py [--base PATH] [--out PATH] [--glow F] [--core F] [--hum F]
Default base: ../../../work/ossus-rain/local_planets-ossus-rain.tre (sha256 fbdf58e8..., the O12 rain fix, not installed).
Default out:  ../../../work/ossus-ghostfire-blade/local_planets-ghostfire-blade.tre (+ .sha256, preview PNGs);
checks in ./checks-blade.json.
"""
import argparse
import colorsys
import hashlib
import json
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
from swgfmt import swg_tables  # noqa: E402

BASE_SHA_PREFIX = 'fbdf58e8'

SRC_LSB = 'appearance/wp_mle_sword_lightsaber_blade_sleeksilver.lsb'
SRC_SHARED = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_s12_gen4.iff'
SRC_FRAME_SHT = 'shader/lightsaberblade_a.sht'
SRC_FRAME_DDS = 'texture/lightsaberblade_%s.dds'
STOCK_BLADE_SHT = 'shader/lightsaberblade.sht'
SRC_SWH = 'appearance/sw_light_saber_white.swh'
SRC_TRAIL_SHT = 'shader/sw_gradient_colorbands.sht'
SRC_TRAIL_DDS = 'texture/sw_light_saber_add.dds'
SWOOSH = 'datatables/weapon/swoosh.iff'
CRC = 'misc/object_template_crc_string_table.iff'

SHARED = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire.iff'
LSB = 'appearance/wp_mle_sword_lightsaber_blade_ghostfire.lsb'
BLADE_SHT = 'shader/ghostfire_blade.sht'
FRAME_SHT = 'shader/ghostfire_blade_%d.sht'
FRAME_DDS = 'texture/ghostfire_blade_%d.dds'
SND = 'sound/ghostfire_idle.snd'
TRAIL_SWH = 'appearance/sw_ghostfire.swh'
TRAIL_SHT = 'shader/sw_ghostfire.sht'
TRAIL_DDS = 'texture/sw_ghostfire.dds'

FRAMES, FRAME_SECONDS = 8, 0.1


# ---------------------------------------------------------------- IFF helpers

def find(nodes, pred):
    return [n for _, n in trn_iff.walk(nodes) if pred(n)]


def cstr(b):
    return b[:b.index(b'\0')].decode('latin-1')


# ---------------------------------------------------------------- textures

def c565(c):
    return ((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31


def dxt3_top(d):
    """The top mip of a DXT3 .dds as rows of (r, g, b, a) 0-255."""
    h, w = struct.unpack_from('<II', d, 12)
    assert d[84:88] == b'DXT3', d[84:88]
    px = [[None] * w for _ in range(h)]
    off = 128
    for by in range(h // 4):
        for bx in range(w // 4):
            alpha = struct.unpack_from('<Q', d, off)[0]
            c0, c1, bits = struct.unpack_from('<HHI', d, off + 8)
            off += 16
            p0, p1 = c565(c0), c565(c1)
            pal = [p0, p1, tuple((2 * a + b) // 3 for a, b in zip(p0, p1)), tuple((a + 2 * b) // 3 for a, b in zip(p0, p1))]
            for i in range(16):
                px[by * 4 + i // 4][bx * 4 + i % 4] = pal[(bits >> (2 * i)) & 3] + (((alpha >> (4 * i)) & 15) * 17,)
    return px


def dds_argb(rows):
    """An uncompressed A8R8G8B8 .dds with a full box-filtered mip chain (the stock raw layout: flags a1007, caps 401008)."""
    h, w = len(rows), len(rows[0])
    levels, cur = [rows], rows
    while len(cur) > 1 or len(cur[0]) > 1:
        ch, cw = len(cur), len(cur[0])
        nh, nw = max(1, ch // 2), max(1, cw // 2)
        nxt = []
        for y in range(nh):
            row = []
            for x in range(nw):
                ps = [cur[min(ch - 1, 2 * y + dy)][min(cw - 1, 2 * x + dx)] for dy in (0, 1) for dx in (0, 1)]
                row.append(tuple((sum(p[i] for p in ps) + 2) // 4 for i in range(4)))
            nxt.append(row)
        levels.append(nxt)
        cur = nxt
    head = struct.pack('<4s7I44x', b'DDS ', 124, 0xa1007, h, w, w * 4, 0, len(levels))
    head += struct.pack('<8I', 32, 0x41, 0, 32, 0x00ff0000, 0x0000ff00, 0x000000ff, 0xff000000)
    head += struct.pack('<4I4x', 0x401008, 0, 0, 0)
    assert len(head) == 128
    body = b''.join(bytes(v for p in row for v in (p[2], p[1], p[0], p[3])) for lv in levels for row in lv)
    return head + body, len(levels)


def png(path, rows):
    h, w = len(rows), len(rows[0])
    raw = b''.join(b'\0' + bytes(v for p in r for v in p[:3]) for r in rows)

    def chunk(t, b):
        return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def hash01(*k):
    return int.from_bytes(hashlib.blake2s(repr(k).encode(), digest_size=4).digest(), 'little') / 2 ** 32


def opal_frame(stock, k, glow, core):
    """Frame k of 8: stock glow shape (rgb luminance) times a milky pastel opal field, stock core (alpha) times core."""
    h, w = len(stock), len(stock[0])
    t = k / FRAMES
    rows = []
    for y in range(h):
        v = (y - (h - 1) / 2) / (h / 2)
        row = []
        for x in range(w):
            r0, g0, b0, a0 = stock[y][x]
            shape = (r0 + g0 + b0) / 765.0
            u = x / w
            # hue bands drift along the blade one wavelength per loop; the edges shift hue like a thin film
            hue = (0.62 + 1.4 * u + 0.22 * v * v - t + 0.05 * math.sin(2 * math.pi * (2 * u + t))) % 1.0
            col = [0.35 + 0.65 * c for c in colorsys.hsv_to_rgb(hue, 0.55, 1.0)]
            # opal "fire": soft round sparks, one in about one 8x6 cell in eight, renewed every second frame
            cell = (x // 8, y // 6, (k // 2) % (FRAMES // 2))
            if hash01('fleck', cell) < 0.12:
                fx = (cell[0] + 0.2 + 0.6 * hash01('fx', cell)) * 8
                fy = (cell[1] + 0.2 + 0.6 * hash01('fy', cell)) * 6
                s = math.exp(-((x + 0.5 - fx) / 1.6) ** 2 - ((y + 0.5 - fy) / 1.2) ** 2)
                fire = colorsys.hsv_to_rgb(hash01('hue', cell), 0.8, 1.0)
                col = [c * (1 - 0.5 * s) + 1.2 * f * s for c, f in zip(col, fire)]
            row.append(tuple(min(255, int(round(255 * shape * c * glow))) for c in col)
                       + (min(255, int(round(a0 * core))),))
        rows.append(row)
    return rows


def trail_texture(stock):
    """64x64: the stock saber trail's profile across u (its alpha), in pastel rainbow bands across u, constant along v."""
    h, w = len(stock), len(stock[0])
    prof = [stock[h // 2][x][3] for x in range(w)]
    row = []
    for x in range(w):
        r, g, b = colorsys.hsv_to_rgb((x / w * 1.25) % 1.0, 0.5, 1.0)
        row.append((int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), prof[x]))
    return [list(row) for _ in range(h)]


def preview(frames, bg):
    """Frames side by side over a background, blended the way the effect blends (additive rgb plus the core)."""
    out = []
    for y in range(len(frames[0])):
        line = []
        for f in frames:
            for p in f[y]:
                line.append(tuple(min(255, bg[i] + p[i] + p[3]) for i in range(3)))
            line.append((0, 0, 0))
        out.append(line)
    return out


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=os.path.join(H, 'work', 'ossus-rain', 'local_planets-ossus-rain.tre'))
    ap.add_argument('--out', default=os.path.join(H, 'work', 'ossus-ghostfire-blade', 'local_planets-ghostfire-blade.tre'))
    ap.add_argument('--glow', type=float, default=0.32, help='opal glow strength, 0-1 (stock glow is 1)')
    ap.add_argument('--core', type=float, default=0.10, help='white core strength, 0-1 (stock core is 1)')
    ap.add_argument('--hum', type=float, default=0.25, help='idle hum volume, 0-1 (stock is 1)')
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    if not base_sha.startswith(BASE_SHA_PREFIX):
        print('NOTE: base is %s, not the O12 rain fix %s...' % (base_sha[:8], BASE_SHA_PREFIX))
    base = tre_write.read(base_bytes)[0]

    def src(name):
        data = base.get(name) or trn_iff.client_file(name)
        assert data, 'missing ' + name
        return data

    new_names = [SHARED, LSB, BLADE_SHT, SND, TRAIL_SWH, TRAIL_SHT, TRAIL_DDS] + \
        [FRAME_SHT % k for k in range(FRAMES)] + [FRAME_DDS % k for k in range(FRAMES)]
    clash = [n for n in new_names if n in base or trn_iff.client_index().get(n)]
    assert not clash, 'already exist: %s' % clash
    added = {}

    # the stock blade is a switching shader over four frames; keep its layout, our frame count and time
    stock_switch = trn_iff.parse(src(STOCK_BLADE_SHT))
    dtst = find(stock_switch, lambda n: not n.is_form and n.tag == '0000')
    assert stock_switch[0].form == 'SWSH' and struct.unpack('<if', dtst[0].data) == (4, 0.0625), dtst[0].data
    added[BLADE_SHT] = trn_iff.build([trn_iff.form('SWSH', trn_iff.form(
        '0000', trn_iff.form('DTST', trn_iff.chunk('0000', struct.pack('<if', FRAMES, FRAME_SECONDS))),
        *[trn_iff.chunk('NAME', (FRAME_SHT % k).encode() + b'\0') for k in range(FRAMES)]))])

    # frame shaders: the SSHT inside the stock CSHD frame (effect, material, texture), without the palette (TFAC) part
    cshd = trn_iff.parse(src(SRC_FRAME_SHT))
    assert cshd[0].form == 'CSHD'
    ver = cshd[0].children[0]
    assert [c.form for c in ver.children] == ['SSHT', 'TFAC'], [c.form for c in ver.children]
    ssht = ver.children[0]
    effect = find([ssht], lambda n: not n.is_form and n.tag == 'NAME' and n.data.startswith(b'effect'))
    assert len(effect) == 1 and cstr(effect[0].data) == 'effect\\e_h_lightsaberblade.eft', effect
    tex = find([ssht], lambda n: not n.is_form and n.tag == 'NAME' and n.data.startswith(b'texture/'))
    assert len(tex) == 1 and cstr(tex[0].data) == 'texture/lightsaberblade_a.dds'
    tfns = find([ssht], lambda n: n.is_form and n.form == 'TFNS')[0].children[0].data
    assert tfns == b'NIAM\xff\xff\xff\xff', tfns   # texture factor MAIN = white once the palette part is gone

    stock_frames = [dxt3_top(src(SRC_FRAME_DDS % c)) for c in 'abcd']
    frames = []
    for k in range(FRAMES):
        tex[0].data = (FRAME_DDS % k).encode() + b'\0'
        added[FRAME_SHT % k] = trn_iff.build([ssht])
        rows = opal_frame(stock_frames[k % 4], k, args.glow, args.core)
        frames.append(rows)
        added[FRAME_DDS % k], mips = dds_argb(rows)
    assert mips == 9

    # the hum: the stock idle sound with its volume pair (the only two 1.0 floats) turned down
    lsb = trn_iff.parse(src(SRC_LSB))
    asnd = find(lsb, lambda n: not n.is_form and n.tag == 'ASND')[0]
    snd_name = cstr(asnd.data)
    snd = trn_iff.parse(src(snd_name))
    sd = find(snd, lambda n: not n.is_form and n.tag == '0003')
    assert snd[0].form == 'SD3D' and len(sd) == 1, 'unexpected sound layout'
    body = sd[0].data
    count = struct.unpack_from('<I', body)[0]
    assert count == 1
    tail = body.index(b'\0', 4) + 1
    ones = [i for i in range(tail, len(body) - 3, 4) if body[i:i + 4] == struct.pack('<f', 1.0)]
    assert len(ones) == 2 and ones[1] == ones[0] + 4, ones
    sd[0].data = body[:ones[0]] + struct.pack('<ff', args.hum, args.hum) + body[ones[1] + 4:]
    added[SND] = trn_iff.build(snd)

    # the blade file: sleek silver, with our shader and hum
    shdr = find(lsb, lambda n: not n.is_form and n.tag == 'SHDR')
    assert len(shdr) == 1 and cstr(shdr[0].data) == STOCK_BLADE_SHT
    shdr[0].data = BLADE_SHT.encode() + b'\0'
    asnd.data = SND.encode() + b'\0'
    added[LSB] = trn_iff.build(lsb)

    # the saber template: the s12 gen4 one-handed template with our appearance
    shared = trn_iff.parse(src(SRC_SHARED))
    app = find(shared, lambda n: not n.is_form and n.tag == 'XXXX' and n.data.startswith(b'appearanceFilename\0'))
    assert len(app) == 1
    key = b'appearanceFilename\0\x01'
    assert app[0].data.startswith(key) and cstr(app[0].data[len(key):]) == SRC_LSB
    app[0].data = key + LSB.encode() + b'\0'
    added[SHARED] = trn_iff.build(shared)

    # the trail: the saber trail file, the colour-band trail's shader layout, our rainbow texture
    tsht = trn_iff.parse(src(SRC_TRAIL_SHT))
    ttex = find(tsht, lambda n: not n.is_form and n.tag == 'NAME' and n.data.startswith(b'texture/'))
    assert len(ttex) == 1
    ttex[0].data = TRAIL_DDS.encode() + b'\0'
    added[TRAIL_SHT] = trn_iff.build(tsht)
    trail_rows = trail_texture(dxt3_top(src(SRC_TRAIL_DDS)))
    added[TRAIL_DDS], _ = dds_argb(trail_rows)
    swh = trn_iff.parse(src(SRC_SWH))
    ptex = find(swh, lambda n: not n.is_form and n.tag == '0000' and n.data.startswith(b'shader/'))
    assert len(ptex) == 1 and cstr(ptex[0].data) == 'shader/sw_light_saber_add.sht'
    ptex[0].data = TRAIL_SHT.encode() + ptex[0].data[ptex[0].data.index(b'\0'):]
    added[TRAIL_SWH] = trn_iff.build(swh)

    changed = {}
    old = src(SWOOSH)
    table = swg_tables.read_dtii(old)
    assert swg_tables.write_dtii(table) == old, 'swoosh table does not round-trip'
    assert table['columns'] == ['ObjectTemplateName', 'SwooshName', 'UseObjectHue']
    assert not [r for r in table['rows'] if r[0] == SHARED]
    table['rows'].append([SHARED, TRAIL_SWH, 0])
    changed[SWOOSH] = swg_tables.write_dtii(table)

    old_crc = base[CRC]
    crc = swg_tables.read_cstb(old_crc)
    assert swg_tables.write_cstb(crc['entries'], crc['version']) == old_crc, 'CRC table does not round-trip'
    crc_new = swg_tables.soe_crc(SHARED)
    assert crc_new not in {c for c, _ in crc['entries']}, 'CRC clash'
    changed[CRC] = swg_tables.write_cstb(crc['entries'] + [(crc_new, SHARED)], crc['version'])

    for name, data in added.items():
        if not name.endswith('.dds'):
            assert trn_iff.build(trn_iff.parse(data)) == data, name

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
    in_base_changed = sorted(n for n in changed if n in base)
    new_entries = sorted(n for n in ours if n not in base)

    out_dir = os.path.dirname(args.out)
    png(os.path.join(out_dir, 'preview-blade-dark.png'), preview(frames, (12, 12, 16)))
    png(os.path.join(out_dir, 'preview-blade-day.png'), preview(frames, (150, 160, 170)))
    png(os.path.join(out_dir, 'preview-trail.png'), preview([trail_rows], (12, 12, 16)))

    checks = {'base_sha256': base_sha, 'base_entries': len(base), 'out_sha256': sha, 'out_bytes': len(out),
              'out_entries': len(ours), 'unchanged_entries': len(same), 'changed': in_base_changed, 'added': new_entries,
              'added_sha256': {n: hashlib.sha256(ours[n]).hexdigest() for n in new_entries},
              'settings': {'glow': args.glow, 'core': args.core, 'hum': args.hum, 'frames': FRAMES,
                           'frame_seconds': FRAME_SECONDS},
              'template_crc': '%08x' % crc_new, 'sound_from': snd_name, 'swoosh_rows': len(table['rows']),
              'crc_entries': len(crc['entries']) + 1}
    with open(os.path.join(HERE, 'checks-blade.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: checks[k] for k in ('base_sha256', 'out_sha256', 'out_entries', 'changed', 'settings',
                                             'template_crc')}, indent=1))
    print('added %d entries: %s' % (len(new_entries), ', '.join(new_entries)))
    print('Ghostfire blade step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
