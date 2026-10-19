"""Ossus O14: the ghostfire crystal gives any saber the near-invisible opal blade, and the ribbon trails linger
(Claude, 18 Oct 2026).

Owner, 18 Oct ~6:10 PM: "can we make a new Crystal entry with the new shader and make all sabers compatible with the new
crystal type? also the blade needs to be dimmer and the trails more prominent (and slow like LSD ...)".

The crystal only sets a palette entry, and every stock blade draws with the same pixel program, e_h_lightsaberblade_ps20.psh
(patch_11_02): rgb = texture.rgb * palette colour + texture.a (white core). This step replaces that program with
e_h_lightsaberblade_ps20.hlsl next to this script: the stock maths for every crystal colour the server gives (entries 0-11
and 31, brightest channel 0.65 or more: the ghostfire weight is exactly 0), and for the ghostfire entries 32-40 (every
channel 0.157 or less) the core almost goes and the glow becomes dim milky opal bands. Compiled here with the Windows
SDK's fxc.exe for ps_2_0, the stock target (fxc rebuilds the stock source to the same 8 instructions on the same registers).

  changed  pixel_program/e_h_lightsaberblade_ps20.psh     our source and its compiled code (PSRC + PEXE)
  changed  palette/wp_lightsaber.pal                       entries 32-40 = (0x20, 4k, 0x20) for 32 + k: still dark, and the
                                                           green channel tells the shader the shimmer step (the server
                                                           steps 33-40 every 150 ms), so the bands drift along the blade
  changed  appearance/ghostfire_ribbon_a..h.swh            the trail behind each ribbon lasts 1.2 s instead of 0.1 s
                                                           (the float after the colour; stock weapons 0.06, contrails
                                                           0.25-0.5, missile smoke 2-4) and keeps up to 60 samples (was 20)

Research behind the trails (owner: "slow like LSD"): Dubois and VanRullen 2011 (PLOS Biology) describe LSD trails as a
series of discrete still afterimages behind a moving object, like a multiple-exposure photograph; PsychonautWiki and
Bluelight reports describe trails that linger and fade slowly, in the object's colours. Here each ribbon is played every
150 ms in the next pastel colour (the server's synced ribbons), so a long-lived trail becomes a run of colour bands
behind the swing.

Older graphics paths (the effect's ps_1_1 and fixed-function versions) are left stock: there the crystal stays a dim tint.

    C:/Users/Pengw/miniconda3/python.exe -I build_ghostfire_crystal.py [--base PATH] [--out PATH] [--trail SECONDS]
Default base: ../../SWG-client/local_planets.tre (installed c8a61080: lsd2 + the O12 rain byte + O13).
Default out:  ../../../work/ossus-ghostfire-crystal/local_planets-ghostfire-crystal.tre (+ .sha256, previews);
checks in ./checks-crystal.json.
"""
import argparse
import colorsys  # noqa: F401  (kept for parity with O13's preview helpers)
import glob
import hashlib
import json
import math
import os
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o13-ghostfire-blade'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402
import build_ghostfire_blade as o13  # noqa: E402  (DXT3 reader, PNG writer)

BASE_SHA_PREFIX = 'c8a61080'
PSH = 'pixel_program/e_h_lightsaberblade_ps20.psh'
PAL = 'palette/wp_lightsaber.pal'
RIBBONS = ['appearance/ghostfire_ribbon_%s.swh' % c for c in 'abcdefgh']
SOURCE = os.path.join(HERE, 'e_h_lightsaberblade_ps20.hlsl')
INCLUDES = ['pixel_program/include/pixel_shader_constants.inc', 'pixel_program/include/functions.inc',
            'shared_program/functions.inc']
GHOST_FIRST, GHOST_COUNT = 32, 9           # entries 32 (idle) and 33-40 (shimmer steps)
GHOST_GLOW, GHOST_CORE, BANDS = 0.08, 0.015, 1.6   # must match the .hlsl
OPAL_BASE, OPAL_SWING = 0.72, 0.28


def fxc_path():
    hits = sorted(glob.glob(r'C:/Program Files (x86)/Windows Kits/10/bin/10.*/x64/fxc.exe'))
    assert hits, 'fxc.exe (Windows SDK) not found'
    return hits[-1]


def compile_ps20(source):
    """Compile with the client's own include files beside it; return (bytecode, disassembly)."""
    fxc = fxc_path()
    with tempfile.TemporaryDirectory() as tmp:
        for inc in INCLUDES:
            path = os.path.join(tmp, inc)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(trn_iff.client_file(inc))
        src = os.path.join(tmp, 'blade.hlsl')
        with open(src, 'wb') as f:
            f.write(source)
        out = os.path.join(tmp, 'blade.pexe')
        subprocess.run([fxc, '/nologo', '/T', 'ps_2_0', '/E', 'main', '/I', tmp, '/Fo', out, src],
                       check=True, capture_output=True)
        code = open(out, 'rb').read()
        dis = subprocess.run([fxc, '/nologo', '/dumpbin', out], check=True, capture_output=True, text=True).stdout
    return code, dis


def read_pal(data):
    i = data.index(b'data') + 8
    ver, count = struct.unpack_from('<HH', data, i)
    return i, ver, [list(data[i + 4 + 4 * k:i + 8 + 4 * k]) for k in range(count)]


def ghost_entry(k):
    return [0x20, 4 * k, 0x20, 0]


STROBE_SECONDS = 2.0
TRAIL_EFFECT = 'effect/e_particle_emisadd_2x.eft'   # the stock saber trail's effect
SHARED_B = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire_b.iff'
TRAIL_B_SWH = 'appearance/sw_ghostfire_b.swh'
TRAIL_B_SHT = 'shader/sw_ghostfire_b.sht'
TRAIL_B_DDS = 'texture/sw_ghostfire_b.dds'


def strobe_texture(profile, bars, duty):
    """64x64: the stock saber trail's profile across u (hilt to tip) times soft bars along v (the trail's time axis),
    each bar its own pastel colour, so each bar can read as one copy of the blade."""
    h, w = 64, len(profile)
    rows = []
    for y in range(h):
        v = (y + 0.5) / h * bars
        i, f = int(v), v - int(v)
        d = abs(f - 0.5) * 2                     # 0 at a bar's centre, 1 at the gap's centre
        edge = 1 - duty
        lit = 1.0 if d <= edge - 0.15 else 0.0 if d >= edge + 0.15 else (edge + 0.15 - d) / 0.3
        r, g, b = colorsys.hsv_to_rgb((i / max(bars, 1) + 0.6) % 1.0, 0.6, 1.0)
        rows.append([(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), int(round(p * lit)))
                     for p in profile])
    return rows


def shader_model(diffuse, tf):
    """The .hlsl's ghostfire branch in Python, for the previews and the stock-path check."""
    r, g, b, a = [v / 255.0 for v in diffuse]
    brightest = max(tf)
    ghost = min(1.0, max(0.0, (0.17 - brightest) * 100.0))
    return ghost


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre'))
    ap.add_argument('--out', default=os.path.join(H, 'work', 'ossus-ghostfire-crystal', 'local_planets-ghostfire-crystal.tre'))
    ap.add_argument('--trail', type=float, default=1.2, help='ribbon trail lifetime in seconds (was 0.1)')
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    if not base_sha.startswith(BASE_SHA_PREFIX):
        print('NOTE: base is %s, not the installed %s...' % (base_sha[:8], BASE_SHA_PREFIX))
    base = tre_write.read(base_bytes)[0]
    changed = {}

    # the pixel program: stock layout (PSHP > 0000 > PSRC, PEXE), our source and code
    stock = base.get(PSH) or trn_iff.client_file(PSH)
    nodes = trn_iff.parse(stock)
    ver = nodes[0].children[0]
    assert nodes[0].form == 'PSHP' and ver.form == '0000' and [c.tag for c in ver.children] == ['PSRC', 'PEXE']
    stock_src = ver.children[0].data
    assert b'diffuseColor.rgb = saturate (diffuseColor.rgb + diffuseColor.a);' in stock_src, 'not the stock source'
    source = open(SOURCE, 'rb').read().replace(b'\r\n', b'\n')
    code, dis = compile_ps20(source)
    for want in ('ps_2_0', 'textureFactor          c3', 'alphaFadeOpacityHolder c7', 'diffuseMap             s0'):
        assert want in dis, 'compiled shader lacks %r' % want
    slots = int(dis.split('approximately ')[1].split(' instruction')[0])
    assert slots <= 64, slots
    ver.children[0].data = source + (b'\0' if stock_src.endswith(b'\0') else b'')
    ver.children[1].data = code
    changed[PSH] = trn_iff.build(nodes)

    # the palette: entries 32-40 dark, green = the shimmer step
    pal = base[PAL]
    at, pver, ents = read_pal(pal)
    assert len(ents) >= GHOST_FIRST + GHOST_COUNT, len(ents)
    used = [k for k in list(range(0, 12)) + [31]]
    assert min(max(ents[k][:3]) for k in used) / 255.0 >= 0.6, 'a crystal colour is too dark for the ghostfire test'
    for k in range(GHOST_COUNT):
        ents[GHOST_FIRST + k] = ghost_entry(k)
    body = struct.pack('<HH', pver, len(ents)) + b''.join(bytes(e) for e in ents)
    new_pal = pal[:at] + body + pal[at + len(body):]
    assert len(new_pal) == len(pal)
    changed[PAL] = new_pal
    ghost_weights = [shader_model((0, 0, 0, 0), [v / 255.0 for v in e[:3]]) for e in ents]
    assert all(ghost_weights[k] == 0.0 for k in used), 'ghostfire weight not 0 for a stock crystal'
    assert all(ghost_weights[GHOST_FIRST + k] == 1.0 for k in range(GHOST_COUNT))

    # the ribbons: trail lifetime (offset 16) and sample count (offset 52 in version 0001)
    for name in RIBBONS:
        rn = trn_iff.parse(base[name])
        v = rn[0].children[0]
        assert rn[0].form == 'SWSH' and v.form == '0001'
        d = [c for c in v.children if not c.is_form][-1]
        dur, = struct.unpack_from('<f', d.data, 16)
        rate, samples = struct.unpack_from('<fI', d.data, 48)
        assert abs(dur - 0.1) < 1e-6 and rate == 30.0 and samples == 20, (name, dur, rate, samples)
        d.data = d.data[:16] + struct.pack('<f', args.trail) + d.data[20:52] + struct.pack('<I', 60) + d.data[56:]
        changed[name] = trn_iff.build(rn)

    # strobe trail test (owner: "Strobe trail, test first"): the saber trail is the surface the blade sweeps between its
    # trail hardpoints; bright bars with gaps along the trail's time axis should leave copies of the whole blade.
    # A (the Ghostfire Lightsaber): the saber trail layout (0000), 1.5 s, 8 pastel bars per texture.
    # B (a second test saber): the same, in the 0001 layout with 8 samples a second and one bar per texture, in case the
    # texture repeats per sample segment rather than once along the trail. Whichever shows copies tells us the mapping.
    added = {}
    profile = [p[3] for p in o13.dxt3_top(trn_iff.client_file(o13.SRC_TRAIL_DDS))[32]]
    changed[o13.TRAIL_DDS], _ = o13.dds_argb(strobe_texture(profile, 8, 0.45))
    swh = trn_iff.parse(base[o13.TRAIL_SWH])
    assert swh[0].children[0].form == '0000'
    data = [c for c in swh[0].children[0].children if not c.is_form][-1]
    assert abs(struct.unpack_from('<f', data.data, 16)[0] - 0.06) < 1e-6
    # owner, 7:15 PM: "the trails are still too faint": full colour alpha (was 0.5) and the stock saber trail's
    # doubled additive effect (emisadd_2x) instead of the colour-band trail's single one
    assert struct.unpack_from('<4f', data.data, 0) == (1.0, 1.0, 1.0, 0.5)
    data.data = struct.pack('<4f', 1.0, 1.0, 1.0, 1.0) + struct.pack('<f', STROBE_SECONDS) + data.data[20:]
    changed[o13.TRAIL_SWH] = trn_iff.build(swh)
    a_data = data.data
    sht = trn_iff.parse(base[o13.TRAIL_SHT])
    eft = [x for _, x in trn_iff.walk(sht) if not x.is_form and x.tag == 'NAME' and x.data.startswith(b'effect')]
    assert len(eft) == 1 and o13.cstr(eft[0].data) == 'effect/e_particle_emisadd.eft', eft
    eft[0].data = TRAIL_EFFECT.encode() + b'\0'
    assert trn_iff.client_file(TRAIL_EFFECT), TRAIL_EFFECT
    changed[o13.TRAIL_SHT] = trn_iff.build(sht)

    added[TRAIL_B_DDS], _ = o13.dds_argb(strobe_texture(profile, 1, 0.3))
    tname = [x for _, x in trn_iff.walk(sht) if not x.is_form and x.tag == 'NAME' and x.data.startswith(b'texture/')]
    assert len(tname) == 1
    tname[0].data = TRAIL_B_DDS.encode() + b'\0'
    added[TRAIL_B_SHT] = trn_iff.build(sht)
    ptex = [x for _, x in trn_iff.walk(swh) if not x.is_form and x.tag == '0000' and x.data.startswith(b'shader/')][0]
    ptex_b = TRAIL_B_SHT.encode() + ptex.data[ptex.data.index(b'\0'):]
    added[TRAIL_B_SWH] = trn_iff.build([trn_iff.form('SWSH', trn_iff.form(
        '0001', trn_iff.form('PTEX', trn_iff.chunk('0000', ptex_b)),
        trn_iff.chunk('0000', a_data + struct.pack('<fII', 8.0, 16, 5))))])
    added[SHARED_B] = base[o13.SHARED]

    # owner, 7:15 PM: "the blade is still too visible", and the capture shows the blade's light lighting the kirruk red
    # (the blade light takes the crystal's colour). The Ghostfire Lightsaber now draws the stock blade, so the crystal
    # decides its look like any saber (the ghostfire crystal gives the dim opal path above), and its blade light is off.
    # The sleek silver blade file has no light section (LGHT); the gen5 files do (BASE, ASND, LGHT, BLAD). In case the
    # engine falls back to a default light in the crystal's colour, ours gets the gen5 one with its colour at 0.
    lsb = trn_iff.parse(base[o13.LSB])
    ver = lsb[0].children[0]
    shdr = [x for _, x in trn_iff.walk(lsb) if not x.is_form and x.tag == 'SHDR']
    assert len(shdr) == 1 and o13.cstr(shdr[0].data) == o13.BLADE_SHT
    assert [c.tag if not c.is_form else c.form for c in ver.children] == ['BASE', 'ASND', 'BLAD']
    shdr[0].data = o13.STOCK_BLADE_SHT.encode() + b'\0'
    gen5 = trn_iff.parse(trn_iff.client_file('appearance/wp_mle_2h_sword_lightsaber_blade_gen5.lsb'))
    lght = [x for _, x in trn_iff.walk(gen5) if x.is_form and x.form == 'LGHT'][0]
    colr = [c for c in lght.children if not c.is_form and c.tag == 'COLR']
    assert len(colr) == 1 and colr[0].data == bytes.fromhex('202020ff')
    colr[0].data = b'\0\0\0\0'
    ver.children.insert(2, lght)
    changed[o13.LSB] = trn_iff.build(lsb)

    table = o13.swg_tables.read_dtii(base[o13.SWOOSH])
    assert [r for r in table['rows'] if r[0] == o13.SHARED] and not [r for r in table['rows'] if r[0] == SHARED_B]
    table['rows'].append([SHARED_B, TRAIL_B_SWH, 0])
    changed[o13.SWOOSH] = o13.swg_tables.write_dtii(table)
    crc = o13.swg_tables.read_cstb(base[o13.CRC])
    crc_b = o13.swg_tables.soe_crc(SHARED_B)
    assert crc_b not in {c for c, _ in crc['entries']}
    changed[o13.CRC] = o13.swg_tables.write_cstb(crc['entries'] + [(crc_b, SHARED_B)], crc['version'])
    for name in (TRAIL_B_SWH, TRAIL_B_SHT):
        assert trn_iff.build(trn_iff.parse(added[name])) == added[name]
    assert not [n for n in added if n in base]

    files = dict(base)
    files.update(changed)
    files.update(added)
    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    sha = hashlib.sha256(out).hexdigest()
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (sha, os.path.basename(args.out)))
    ours = tre_write.read(out)[0]
    assert sorted(ours) == sorted(set(base) | set(changed) | set(added))
    same = [n for n in base if n not in changed]
    assert all(ours[n] == base[n] for n in same) and all(ours[n] == changed[n] for n in changed)
    assert all(ours[n] == added[n] for n in added)

    # previews: the stock blade frame a under each ghostfire step, blended as the game blends it
    tex = o13.dxt3_top(trn_iff.client_file('texture/lightsaberblade_a.dds'))
    frames = []
    for k in range(1, GHOST_COUNT):
        phase = (4 * k / 255.0) * (255.0 / 32.0)
        rows = []
        for y, row in enumerate(tex):
            line = []
            for x, (r, g, b, a) in enumerate(row):
                ang = 2 * math.pi * (x / len(row) * BANDS + phase)
                c, s = math.cos(ang), math.sin(ang)
                opal = [OPAL_BASE + OPAL_SWING * (c * u + s * w) for u, w in ((1, 0), (-0.5, 0.8660254), (-0.5, -0.8660254))]
                glow = (r + g + b) / 765.0
                line.append(tuple(min(255, int(round(255 * (glow * GHOST_GLOW * o + a / 255.0 * GHOST_CORE))))
                                  for o in opal) + (0,))
            rows.append(line)
        frames.append(rows)
    out_dir = os.path.dirname(args.out)
    o13.png(os.path.join(out_dir, 'preview-crystal-dark.png'), o13.preview(frames, (12, 12, 16)))
    o13.png(os.path.join(out_dir, 'preview-crystal-day.png'), o13.preview(frames, (150, 160, 170)))

    o13.png(os.path.join(out_dir, 'preview-strobe-a.png'),
            [[tuple(c * p[3] // 255 for c in p[:3]) for p in row] for row in strobe_texture(profile, 8, 0.45)])
    o13.png(os.path.join(out_dir, 'preview-strobe-b.png'),
            [[tuple(c * p[3] // 255 for c in p[:3]) for p in row] for row in strobe_texture(profile, 1, 0.3)])

    checks = {'base_sha256': base_sha, 'base_entries': len(base), 'out_sha256': sha, 'out_bytes': len(out),
              'out_entries': len(ours), 'unchanged_entries': len(same), 'changed': sorted(changed),
              'added': sorted(added), 'strobe': {'seconds': STROBE_SECONDS, 'a_bars': 8, 'b_bars': 1, 'b_rate': 8.0,
                                                  'b_samples': 16, 'template_b_crc': '%08x' % crc_b},
              'changed_sha256': {n: hashlib.sha256(ours[n]).hexdigest() for n in sorted(changed)},
              'shader': {'fxc': os.path.basename(os.path.dirname(os.path.dirname(fxc_path()))), 'slots': slots,
                         'code_sha256': hashlib.sha256(code).hexdigest(), 'glow': GHOST_GLOW, 'core': GHOST_CORE,
                         'bands': BANDS},
              'palette_32_40': ['%02x%02x%02x' % tuple(ents[GHOST_FIRST + k][:3]) for k in range(GHOST_COUNT)],
              'stock_crystal_brightest': {k: round(max(ents[k][:3]) / 255.0, 3) for k in used},
              'ribbon_trail_seconds': args.trail, 'ribbon_samples': 60}
    with open(os.path.join(HERE, 'checks-crystal.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: checks[k] for k in ('base_sha256', 'out_sha256', 'out_entries', 'changed', 'shader')}, indent=1))
    print('Ghostfire crystal step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
