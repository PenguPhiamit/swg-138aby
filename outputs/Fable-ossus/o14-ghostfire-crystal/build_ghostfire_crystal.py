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
Default base: ../../../work/ossus-ghostfire-blade/local_planets-ghostfire-blade.tre (c8a61080: lsd2 + the O12 rain byte + O13;
the installed archive now has O14 and the light whip on top, so it can't be the base).
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
GHOST_GLOW, GHOST_CORE, BANDS = 0.14, 0.02, 1.6   # must match the .hlsl
OPAL_BASE, OPAL_SWING = 0.75, 0.25


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
                f.write(stock_file(inc))
        src = os.path.join(tmp, 'blade.hlsl')
        with open(src, 'wb') as f:
            f.write(source)
        out = os.path.join(tmp, 'blade.pexe')
        subprocess.run([fxc, '/nologo', '/T', 'ps_2_0', '/E', 'main', '/I', tmp, '/Fo', out, src],
                       check=True, capture_output=True)
        code = open(out, 'rb').read()
        dis = subprocess.run([fxc, '/nologo', '/dumpbin', out], check=True, capture_output=True, text=True).stdout
    return code, dis


_stock_index = None


def stock_file(name):
    """A client file as the archives under ours give it. trn_iff.client_file reads the live client, whose
    local_planets.tre is now an O14 build (b9fbc48a, 8:07 PM), so it would hand back our own pixel program and
    customization table instead of the stock ones."""
    global _stock_index
    if _stock_index is None:
        trn_iff.client_index()  # puts client_load_order on the path
        import client_load_order as clo
        trees, _, _ = clo.load_order()
        order = [n for _, n in sorted(trees, key=lambda t: t[0])]
        mtg = sorted(n for n in os.listdir(trn_iff.CLIENT) if n.lower().startswith('mtg_') and n.lower().endswith('.tre'))
        _stock_index = {}
        for arc in mtg + order:
            path = os.path.join(trn_iff.CLIENT, arc)
            if arc.lower() != 'local_planets.tre' and os.path.exists(path):
                for entry in trn_iff.list_tre(path):
                    _stock_index[entry] = arc
    arc = _stock_index.get(name.lower())
    return trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), name) if arc else None


def read_pal(data):
    i = data.index(b'data') + 8
    ver, count = struct.unpack_from('<HH', data, i)
    return i, ver, [list(data[i + 4 + 4 * k:i + 8 + 4 * k]) for k in range(count)]


def ghost_entry(k):
    # green 4k, but entry 40 at 0x1e rather than 0x20: a grey (g = r = b) never reads as ghostfire to the trail program,
    # so a white crystal's trail can't pass for one even if a trail darkens its colour as it fades
    return [0x20, min(4 * k, 0x1E), 0x20, 0]


# Owner, 7:50 PM, on 2 s / full alpha / the doubled effect / 8 bars: "trails are too vibrant" (a big fan of full-strength
# bars around the Jedi). Back to the single additive effect, half alpha, 1.2 s and 6 copies per trail.
# Owner, 8:15 PM, on that: "the trails are too faint now" and "we dont see enough of all the colors". Full alpha again on
# the single effect (half the 7:50 strength), and every band at full strength in its own hue (OIL below).
STROBE_SECONDS = 1.2
STROBE_BARS = 6
TRAIL_ALPHA = 1.0
TRAIL_EFFECT = 'effect/e_particle_emisadd.eft'   # the colour-band trail's single effect (the 2x one was too loud)
SHARED_B = 'object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire_b.iff'
TRAIL_B_SWH = 'appearance/sw_ghostfire_b.swh'
TRAIL_B_SHT = 'shader/sw_ghostfire_b.sht'
TRAIL_B_DDS = 'texture/sw_ghostfire_b.dds'
ACM = 'customization/asset_customization_manager.iff'
# A trail that draws only for the ghostfire crystal, for any saber's trail row with UseObjectHue 1 (first the light whip:
# owner, ~8:45 PM, "the ghostfire crystal also has no trails on the whip hilt"). Its pixel program reads the crystal's
# palette colour from the vertex colour and draws the strobe texture's oil-slick bars for ghostfire, nothing otherwise.
GTRAIL_SOURCE = os.path.join(HERE, 'ghostfire_trail_ps20.hlsl')
GTRAIL_PSH = 'pixel_program/ghostfire_trail_ps20.psh'
GTRAIL_EFT = 'effect/ghostfire_trail.eft'
GTRAIL_SHT = 'shader/sw_ghostfire_trail.sht'
GTRAIL_SWH = 'appearance/sw_ghostfire_trail.swh'
# Any hilt (owner, ~8:5x PM: "yes, it was supposed to be tied to the crystal, go in any hilt"): the trail all 169 saber
# rows share, with a program that keeps the stock trail for every other crystal and draws the strobe bars for ghostfire.
GSABER_SOURCE = os.path.join(HERE, 'ghostfire_saber_trail_ps20.hlsl')
GSABER_PSH = 'pixel_program/ghostfire_saber_trail_ps20.psh'
GSABER_EFT = 'effect/ghostfire_saber_trail.eft'
GSABER_SHT = 'shader/sw_light_saber_ghostfire.sht'
GSABER_DDS = 'texture/sw_light_saber_ghostfire.dds'
STOCK_SABER_SHT = 'shader/sw_light_saber_add.sht'
WHIP_LSB = 'appearance/wp_mle_lightwhip_blade.lsb'   # the main session's light whip blade (Lightwhip/), same gap


# Owner, 18 Oct evening: "maybe mix some darker colors in too for a more gasoline purple fumed kinda thing, and the
# color is mostly for the trails". An oil slick or heat-tinted (fumed) metal: thin-film colours, mostly deep violet,
# indigo, petrol blue, teal and magenta, one bronze glint, on dark. Additive light can't darken, so "darker" means
# deep hues and every other band at about half strength.
# Owner, later: "add some cyan and a brighter green" (both at full strength, so they land on even, undimmed bands).
# Owner, 8:15 PM: "we dont see enough of all the colors". The capture showed pale green streaks: the half-strength bands
# and the 20% smoky-violet mix washed the violets out, and green and cyan, far brighter to the eye, won on the grass. Now
# no dimmed bands and no grey: ten hues in thin-film order (an oil slick's sequence), half of them purples and blues at
# full strength, with green, cyan, gold and teal held a little lower so they don't drown the rest. The first six are
# the strobe bars and the first eight the tip ribbons, so each spans the whole range.
OIL = [(0.62, 0.20, 1.00), (0.18, 0.38, 1.00), (0.00, 0.78, 0.85), (0.28, 0.85, 0.30), (0.90, 0.68, 0.12),
       (1.00, 0.18, 0.80), (0.55, 0.12, 1.00), (0.00, 0.72, 0.66), (1.00, 0.40, 0.35), (0.38, 0.28, 1.00)]
# violet, blue, cyan, green, gold, magenta, purple, teal, rose, indigo


def oil(i, u):
    """Band i's colour, drifting towards the next band's from hilt (u=0) to tip (u=1), like a thin film."""
    a, b = OIL[i % len(OIL)], OIL[(i + 1) % len(OIL)]
    return [x + (y - x) * u for x, y in zip(a, b)]


def strobe_lit(y, h, bars, duty):
    """Row y's bar index and how lit it is (soft bars along v, the trail's time axis)."""
    v = (y + 0.5) / h * bars
    i, f = int(v), v - int(v)
    d = abs(f - 0.5) * 2                     # 0 at a bar's centre, 1 at the gap's centre
    edge = 1 - duty
    return i, 1.0 if d <= edge - 0.15 else 0.0 if d >= edge + 0.15 else (edge + 0.15 - d) / 0.3


def saber_trail_texture(stock_rows, bars, duty):
    """64x64 for the shared saber trail: the stock trail texture's alpha texel for texel (the stock look for every other
    crystal), and the strobe bars' oil-slick colours (times how lit each row is) in the colour channels for ghostfire."""
    h, w = len(stock_rows), len(stock_rows[0])
    rows = []
    for y in range(h):
        i, lit = strobe_lit(y, h, bars, duty)
        rows.append([tuple(int(round(c * lit * 255)) for c in oil(i, x / (w - 1))) + (stock_rows[y][x][3],)
                     for x in range(w)])
    return rows


def strobe_texture(profile, bars, duty):
    """64x64: the stock saber trail's profile across u (hilt to tip) times soft bars along v (the trail's time axis),
    each bar its own oil-slick colour, so each bar can read as one copy of the blade."""
    h, w = 64, len(profile)
    rows = []
    for y in range(h):
        i, lit = strobe_lit(y, h, bars, duty)
        row = []
        for x, p in enumerate(profile):
            r, g, b = oil(i, x / (w - 1))
            row.append((int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), int(round(p * lit))))
        rows.append(row)
    return rows


def diag_texture(profile):
    """64x64 diagnostic: white for v < 8%, then hues red -> yellow -> green -> cyan -> blue -> violet along v; the stock
    trail profile across u."""
    rows = []
    for y in range(64):
        v = (y + 0.5) / 64
        if v < 0.08:
            r = g = b = 1.0
        else:
            r, g, b = colorsys.hsv_to_rgb((v - 0.08) / 0.92 * 0.8, 1.0, 1.0)
        rows.append([(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), p) for p in profile])
    return rows


def shader_model(diffuse, tf):
    """The .hlsl's ghostfire branch in Python, for the previews and the stock-path check."""
    r, g, b, a = [v / 255.0 for v in diffuse]
    brightest = max(tf)
    ghost = min(1.0, max(0.0, (0.17 - brightest) * 100.0))
    return ghost


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=os.path.join(H, 'work', 'ossus-ghostfire-blade', 'local_planets-ghostfire-blade.tre'))
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
    stock = base.get(PSH) or stock_file(PSH)
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
    old_ribbon_rgba = {}
    for k, name in enumerate(RIBBONS):
        rn = trn_iff.parse(base[name])
        v = rn[0].children[0]
        assert rn[0].form == 'SWSH' and v.form == '0001'
        d = [c for c in v.children if not c.is_form][-1]
        dur, = struct.unpack_from('<f', d.data, 16)
        rate, samples = struct.unpack_from('<fI', d.data, 48)
        assert abs(dur - 0.1) < 1e-6 and rate == 30.0 and samples == 20, (name, dur, rate, samples)
        old_ribbon_rgba[name] = [round(x, 3) for x in struct.unpack_from('<4f', d.data, 0)]
        d.data = struct.pack('<4f', *oil(k, 0.0), TRAIL_ALPHA) + struct.pack('<f', args.trail) + d.data[20:52] + struct.pack('<I', 60) + d.data[56:]
        changed[name] = trn_iff.build(rn)

    # strobe trail test (owner: "Strobe trail, test first"): the saber trail is the surface the blade sweeps between its
    # trail hardpoints; bright bars with gaps along the trail's time axis should leave copies of the whole blade.
    # A (the Ghostfire Lightsaber): the saber trail layout (0000), 1.5 s, 8 pastel bars per texture.
    # B (a second test saber): the same, in the 0001 layout with 8 samples a second and one bar per texture, in case the
    # texture repeats per sample segment rather than once along the trail. Whichever shows copies tells us the mapping.
    added = {}
    profile = [p[3] for p in o13.dxt3_top(stock_file(o13.SRC_TRAIL_DDS))[32]]
    changed[o13.TRAIL_DDS], _ = o13.dds_argb(strobe_texture(profile, STROBE_BARS, 0.45))
    swh = trn_iff.parse(base[o13.TRAIL_SWH])
    assert swh[0].children[0].form == '0000'
    data = [c for c in swh[0].children[0].children if not c.is_form][-1]
    assert abs(struct.unpack_from('<f', data.data, 16)[0] - 0.06) < 1e-6
    assert struct.unpack_from('<4f', data.data, 0) == (1.0, 1.0, 1.0, 0.5)
    data.data = struct.pack('<4f', 1.0, 1.0, 1.0, TRAIL_ALPHA) + struct.pack('<f', STROBE_SECONDS) + data.data[20:]
    changed[o13.TRAIL_SWH] = trn_iff.build(swh)
    a_data = data.data
    sht = trn_iff.parse(base[o13.TRAIL_SHT])
    eft = [x for _, x in trn_iff.walk(sht) if not x.is_form and x.tag == 'NAME' and x.data.startswith(b'effect')]
    assert len(eft) == 1 and o13.cstr(eft[0].data) == 'effect/e_particle_emisadd.eft', eft
    if TRAIL_EFFECT != 'effect/e_particle_emisadd.eft':
        eft[0].data = TRAIL_EFFECT.encode() + b'\0'
        assert stock_file(TRAIL_EFFECT), TRAIL_EFFECT
        changed[o13.TRAIL_SHT] = trn_iff.build(sht)

    # the ghostfire-only trail: its own pixel program (ps_2_0) in a copy of the single additive particle effect (only the
    # shader-model-2 implementation changes; the older ones stay a_modulate), on the strobe bars, in the saber trail file
    gnodes = trn_iff.parse(stock)
    gver = gnodes[0].children[0]
    gsource = open(GTRAIL_SOURCE, 'rb').read().replace(b'\r\n', b'\n')
    gcode, gdis = compile_ps20(gsource)
    for want in ('ps_2_0', 'alphaFadeOpacityHolder c7', 'diffuseMap             s0'):
        assert want in gdis, 'trail program lacks %r' % want
    gslots = int(gdis.split('approximately ')[1].split(' instruction')[0])
    assert gslots <= 64, gslots
    gver.children[0].data = gsource + (b'\0' if stock_src.endswith(b'\0') else b'')
    gver.children[1].data = gcode
    added[GTRAIL_PSH] = trn_iff.build(gnodes)
    geft = trn_iff.parse(stock_file('effect/e_particle_emisadd.eft'))
    ppsh = [x for _, x in trn_iff.walk(geft) if not x.is_form and x.data == b'\x01pixel_program/a_modulate.psh\0']
    assert len(ppsh) == 2, len(ppsh)
    ppsh[0].data = b'\x01' + GTRAIL_PSH.encode() + b'\0'
    added[GTRAIL_EFT] = trn_iff.build(geft)
    gsht = trn_iff.parse(base[o13.TRAIL_SHT])
    gname = [x for _, x in trn_iff.walk(gsht) if not x.is_form and x.tag == 'NAME' and x.data.startswith(b'effect')]
    assert len(gname) == 1
    gname[0].data = GTRAIL_EFT.encode() + b'\0'
    added[GTRAIL_SHT] = trn_iff.build(gsht)
    gswh = trn_iff.parse(changed[o13.TRAIL_SWH])
    gptex = [x for _, x in trn_iff.walk(gswh) if not x.is_form and x.tag == '0000' and x.data.startswith(b'shader/')]
    assert len(gptex) == 1 and o13.cstr(gptex[0].data) == o13.TRAIL_SHT
    gptex[0].data = GTRAIL_SHT.encode() + gptex[0].data[gptex[0].data.index(b'\0'):]
    added[GTRAIL_SWH] = trn_iff.build(gswh)
    for name in (GTRAIL_PSH, GTRAIL_EFT, GTRAIL_SHT, GTRAIL_SWH):
        assert trn_iff.build(trn_iff.parse(added[name])) == added[name]

    # any hilt: the shared saber trail (sw_light_saber_white.swh, UseObjectHue 1 on all 169 saber rows) gets its own
    # program in a copy of its doubled additive effect, our texture (stock alpha, strobe colours), 1.2 s and alpha 1.
    # The program draws the stock trail over the newest 5% (0.06 s) for every other crystal, the bars for ghostfire.
    snodes = trn_iff.parse(stock)
    sver = snodes[0].children[0]
    ssource = open(GSABER_SOURCE, 'rb').read().replace(b'\r\n', b'\n')
    scode, sdis = compile_ps20(ssource)
    for want in ('ps_2_0', 'alphaFadeOpacityHolder c7', 'diffuseMap             s0'):
        assert want in sdis, 'saber trail program lacks %r' % want
    sslots = int(sdis.split('approximately ')[1].split(' instruction')[0])
    assert sslots <= 64, sslots
    sver.children[0].data = ssource + (b'\0' if stock_src.endswith(b'\0') else b'')
    sver.children[1].data = scode
    added[GSABER_PSH] = trn_iff.build(snodes)
    seft = trn_iff.parse(stock_file('effect/e_particle_emisadd_2x.eft'))
    sppsh = [x for _, x in trn_iff.walk(seft) if not x.is_form and x.data == b'\x01pixel_program/a_modulate2x.psh\0']
    assert len(sppsh) == 2, len(sppsh)
    sppsh[0].data = b'\x01' + GSABER_PSH.encode() + b'\0'
    added[GSABER_EFT] = trn_iff.build(seft)
    ssht = trn_iff.parse(stock_file(STOCK_SABER_SHT))
    sname = {o13.cstr(x.data): x for _, x in trn_iff.walk(ssht) if not x.is_form and x.tag == 'NAME'}
    assert sorted(sname) == ['effect/e_particle_emisadd_2x.eft', 'texture/sw_light_saber_add.dds'], sorted(sname)
    sname['effect/e_particle_emisadd_2x.eft'].data = GSABER_EFT.encode() + b'\0'
    sname['texture/sw_light_saber_add.dds'].data = GSABER_DDS.encode() + b'\0'
    added[GSABER_SHT] = trn_iff.build(ssht)
    stock_rows = o13.dxt3_top(stock_file(o13.SRC_TRAIL_DDS))
    added[GSABER_DDS], _ = o13.dds_argb(saber_trail_texture(stock_rows, STROBE_BARS, 0.45))
    sswh = trn_iff.parse(stock_file(o13.SRC_SWH))
    sptex = [x for _, x in trn_iff.walk(sswh) if not x.is_form and x.tag == '0000' and x.data.startswith(b'shader/')]
    assert len(sptex) == 1 and o13.cstr(sptex[0].data) == STOCK_SABER_SHT
    sptex[0].data = GSABER_SHT.encode() + sptex[0].data[sptex[0].data.index(b'\0'):]
    sdat = [c for c in sswh[0].children[0].children if not c.is_form][-1]
    assert sswh[0].children[0].form == '0000'
    assert struct.unpack_from('<5f', sdat.data, 0)[3:] == (0.5, struct.unpack_from('<f', struct.pack('<f', 0.06))[0])
    sdat.data = struct.pack('<5f', 1.0, 1.0, 1.0, 1.0, STROBE_SECONDS) + sdat.data[20:]
    added[o13.SRC_SWH] = trn_iff.build(sswh)
    for name in (GSABER_PSH, GSABER_EFT, GSABER_SHT, o13.SRC_SWH):
        assert trn_iff.build(trn_iff.parse(added[name])) == added[name]

    # B is now a one-look diagnostic for the any-hilt trail (owner, ~8:15 PM: "being able to swap is important"): the
    # stock saber trail file itself (sw_light_saber_white.swh, the one every crafted saber shares) with only its shader,
    # colour (full) and life (1.2 s) changed, and a texture that is white for the first 8% of v, then a rainbow along
    # the rest. A capture shows whether v runs once along the trail or repeats per sample, and which end is the newest.
    added[TRAIL_B_DDS], _ = o13.dds_argb(diag_texture(profile))
    tname = [x for _, x in trn_iff.walk(sht) if not x.is_form and x.tag == 'NAME' and x.data.startswith(b'texture/')]
    assert len(tname) == 1
    tname[0].data = TRAIL_B_DDS.encode() + b'\0'
    added[TRAIL_B_SHT] = trn_iff.build(sht)
    swh_b = trn_iff.parse(stock_file(o13.SRC_SWH))
    ptex = [x for _, x in trn_iff.walk(swh_b) if not x.is_form and x.tag == '0000' and x.data.startswith(b'shader/')][0]
    assert o13.cstr(ptex.data) == 'shader/sw_light_saber_add.sht'
    ptex.data = TRAIL_B_SHT.encode() + ptex.data[ptex.data.index(b'\0'):]
    bdat = [c for c in swh_b[0].children[0].children if not c.is_form][-1]
    assert struct.unpack_from('<5f', bdat.data, 0)[3:] == (0.5, struct.unpack_from('<f', struct.pack('<f', 0.06))[0])
    bdat.data = struct.pack('<5f', 1.0, 1.0, 1.0, 1.0, STROBE_SECONDS) + bdat.data[20:]
    added[TRAIL_B_SWH] = trn_iff.build(swh_b)
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

    # Owner, 7:50 PM, with the ghostfire crystal in: "there is a red saber in there somehow". The client only applies a
    # customization variable to an appearance that its asset customization table lists (CIDX: appearance path CRC ->
    # asset key; the key's links lead to /private/index_color_blade on palette/wp_lightsaber.pal, default 0). Stock
    # blades are listed; our new blade file was not (nor the light whip's), so the crystal's colour was dropped and the
    # default, palette 0 (red), drew. Both get a row pointing at the sleek silver blade's key. The server never uses this
    # table for the blade colour (only image design, goggles and Lua), so this is client data only.
    acm_stock = stock_file(ACM)
    acm = trn_iff.parse(acm_stock)
    assert trn_iff.build(acm) == acm_stock and acm[0].form == 'ACST' and acm[0].children[0].form == '0000'
    acm_chunks = {c.tag: c for c in acm[0].children[0].children}
    cidx = acm_chunks['CIDX']
    rows = {struct.unpack_from('<I', cidx.data, i)[0]: struct.unpack_from('<H', cidx.data, i + 4)[0]
            for i in range(0, len(cidx.data), 6)}
    assert len(rows) * 6 == len(cidx.data) and list(rows) == sorted(rows)
    donor_key = rows[o13.swg_tables.soe_crc(o13.SRC_LSB)]
    assert donor_key == 18199, donor_key
    acm_rows = {}
    for path in (o13.LSB, WHIP_LSB):
        crc_l = o13.swg_tables.soe_crc(path)
        assert crc_l not in rows, path
        rows[crc_l] = donor_key
        acm_rows[path] = '%08x' % crc_l
    cidx.data = b''.join(struct.pack('<IH', c, rows[c]) for c in sorted(rows))
    added[ACM] = trn_iff.build(acm)
    gen5 = trn_iff.parse(stock_file('appearance/wp_mle_2h_sword_lightsaber_blade_gen5.lsb'))
    lght = [x for _, x in trn_iff.walk(gen5) if x.is_form and x.form == 'LGHT'][0]
    colr = [c for c in lght.children if not c.is_form and c.tag == 'COLR']
    assert len(colr) == 1 and colr[0].data == bytes.fromhex('202020ff')
    colr[0].data = b'\0\0\0\0'
    ver.children.insert(2, lght)
    changed[o13.LSB] = trn_iff.build(lsb)

    table = o13.swg_tables.read_dtii(base[o13.SWOOSH])
    assert [r for r in table['rows'] if r[0] == o13.SHARED] and not [r for r in table['rows'] if r[0] == SHARED_B]
    # the Ghostfire Lightsaber is an ordinary hilt now (owner: "being able to swap is important"): the shared trail
    a_row = [r for r in table['rows'] if r[0] == o13.SHARED]
    assert len(a_row) == 1 and a_row[0][1:] == [o13.TRAIL_SWH, 0], a_row
    a_row[0][1:] = [o13.SRC_SWH, 1]
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
    tex = o13.dxt3_top(stock_file('texture/lightsaberblade_a.dds'))
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
            [[tuple(c * p[3] // 255 for c in p[:3]) for p in row] for row in strobe_texture(profile, STROBE_BARS, 0.45)])
    o13.png(os.path.join(out_dir, 'preview-strobe-b.png'),
            [[tuple(c * p[3] // 255 for c in p[:3]) for p in row] for row in diag_texture(profile)])

    checks = {'base_sha256': base_sha, 'base_entries': len(base), 'out_sha256': sha, 'out_bytes': len(out),
              'out_entries': len(ours), 'unchanged_entries': len(same), 'changed': sorted(changed),
              'added': sorted(added), 'acm_rows': acm_rows, 'acm_donor_key': donor_key, 'strobe': {'seconds': STROBE_SECONDS, 'a_bars': STROBE_BARS, 'alpha': TRAIL_ALPHA, 'effect': TRAIL_EFFECT, 'b_diagnostic': 'stock saber trail layout, white for v < 0.08 then a rainbow along v, full colour, same life as A',
                                                  'template_b_crc': '%08x' % crc_b},
              'changed_sha256': {n: hashlib.sha256(ours[n]).hexdigest() for n in sorted(changed)},
              'shader': {'fxc': os.path.basename(os.path.dirname(os.path.dirname(fxc_path()))), 'slots': slots,
                         'code_sha256': hashlib.sha256(code).hexdigest(), 'glow': GHOST_GLOW, 'core': GHOST_CORE,
                         'bands': BANDS},
              'palette_32_40': ['%02x%02x%02x' % tuple(ents[GHOST_FIRST + k][:3]) for k in range(GHOST_COUNT)],
              'stock_crystal_brightest': {k: round(max(ents[k][:3]) / 255.0, 3) for k in used},
              'ghostfire_trail': {'files': [GTRAIL_SWH, GTRAIL_SHT, GTRAIL_EFT, GTRAIL_PSH], 'slots': gslots,
                                  'code_sha256': hashlib.sha256(gcode).hexdigest(), 'texture': o13.TRAIL_DDS,
                                  'seconds': STROBE_SECONDS, 'alpha': TRAIL_ALPHA},
              'saber_trail': {'swh': o13.SRC_SWH, 'files': [GSABER_SHT, GSABER_EFT, GSABER_PSH, GSABER_DDS],
                              'slots': sslots, 'code_sha256': hashlib.sha256(scode).hexdigest(),
                              'seconds': STROBE_SECONDS, 'stock_share': 0.05, 'ghostfire_lightsaber_row': [o13.SRC_SWH, 1]},
              'ribbon_trail_seconds': args.trail, 'ribbon_samples': 60, 'ribbon_rgba_was': old_ribbon_rgba,
              'ribbon_rgba': {n: [round(x, 3) for x in oil(k, 0.0)] + [TRAIL_ALPHA] for k, n in enumerate(RIBBONS)}}
    with open(os.path.join(HERE, 'checks-crystal.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: checks[k] for k in ('base_sha256', 'out_sha256', 'out_entries', 'changed', 'shader')}, indent=1))
    print('Ghostfire crystal step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
