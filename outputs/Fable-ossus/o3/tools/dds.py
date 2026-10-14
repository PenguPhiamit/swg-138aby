"""dds.py: our own DDS reader/writer (Fable, Ossus O3). Standard library only.

A DDS file is the magic 'DDS ', a 124-byte header (DDS_HEADER: size, flags, height, width, pitchOrLinearSize, depth,
mipMapCount, 11 reserved, DDS_PIXELFORMAT (size 32, flags, fourCC, bit count, four masks), caps1..4, reserved) and the
pixel data: every mip level in turn, top level first. read() keeps every header field, so write(read(x)) == x for any
stock file (uncompressed, DXT1, DXT3, DXT5 alike: compressed data is carried as bytes). encode() builds a new
uncompressed A8R8G8B8 file the way the stock UI textures are built (texture/loading/lok/ui_load_lok.dds: flags 0xa1007,
pixel-format flags 0x41, caps 0x401008, pitchOrLinearSize = bytes of the top level), with a box-filtered mip chain when
mips > 1. Pixels are rows top to bottom, each a list of (r, g, b, a) tuples.

    python -I dds.py --selftest      round-trips the four stock files named in SELFTEST and an encoded image
"""
import os
import struct
import sys

MAGIC = b'DDS '
HEADER = '<I I I I I I I 11I I I 4s I I I I I I I I I I'   # size, flags, h, w, pitch, depth, mips, reserved[11], pf..., caps[4], reserved2
FLAGS_BASE = 0x1 | 0x2 | 0x4 | 0x1000            # CAPS | HEIGHT | WIDTH | PIXELFORMAT
FLAG_PITCH, FLAG_MIPS, FLAG_LINEAR = 0x8, 0x20000, 0x80000
PF_ALPHA, PF_FOURCC, PF_RGB = 0x1, 0x4, 0x40
CAPS_COMPLEX, CAPS_TEXTURE, CAPS_MIPMAP = 0x8, 0x1000, 0x400000


def read(data):
    """{'header': {...}, 'data': bytes} with every field of the 124-byte header."""
    if data[:4] != MAGIC:
        raise ValueError('not a DDS file')
    f = struct.unpack_from(HEADER, data, 4)
    h = {'size': f[0], 'flags': f[1], 'height': f[2], 'width': f[3], 'pitch': f[4], 'depth': f[5], 'mips': f[6],
         'reserved': list(f[7:18]), 'pf_size': f[18], 'pf_flags': f[19], 'fourcc': f[20], 'bpp': f[21],
         'masks': list(f[22:26]), 'caps': list(f[26:30]), 'reserved2': f[30]}
    if h['size'] != 124 or h['pf_size'] != 32:
        raise ValueError('unexpected header sizes %d/%d' % (h['size'], h['pf_size']))
    return {'header': h, 'data': data[128:]}


def write(dds):
    h = dds['header']
    hdr = struct.pack(HEADER, h['size'], h['flags'], h['height'], h['width'], h['pitch'], h['depth'], h['mips'],
                      *h['reserved'], h['pf_size'], h['pf_flags'], h['fourcc'], h['bpp'], *h['masks'], *h['caps'], h['reserved2'])
    return MAGIC + hdr + dds['data']


def is_uncompressed(h):
    return not (h['pf_flags'] & PF_FOURCC)


def decode_pixels(dds, level=0):
    """Rows of (r, g, b, a) for an uncompressed 24/32-bit level (masks read from the header)."""
    h = dds['header']
    if not is_uncompressed(h):
        raise ValueError('compressed texture (%r); decode is for uncompressed files' % h['fourcc'])
    bpp = h['bpp'] // 8
    w, hh = h['width'], h['height']
    off = 0
    for _ in range(level):
        off += w * hh * bpp
        w, hh = max(1, w // 2), max(1, hh // 2)
    rm, gm, bm, am = h['masks']

    def chan(v, m):
        if not m:
            return 255
        shift = (m & -m).bit_length() - 1
        bits = bin(m).count('1')
        return ((v & m) >> shift) * 255 // ((1 << bits) - 1)
    rows = []
    d = dds['data']
    for y in range(hh):
        row = []
        for x in range(w):
            p = off + (y * w + x) * bpp
            v = int.from_bytes(d[p:p + bpp], 'little')
            row.append((chan(v, rm), chan(v, gm), chan(v, bm), chan(v, am)))
        rows.append(row)
    return rows


def _box_down(rows):
    h, w = len(rows), len(rows[0])
    nh, nw = max(1, h // 2), max(1, w // 2)
    out = []
    for y in range(nh):
        r = []
        for x in range(nw):
            px = [rows[min(h - 1, 2 * y + dy)][min(w - 1, 2 * x + dx)] for dy in (0, 1) for dx in (0, 1)]
            r.append(tuple(sum(p[i] for p in px) // 4 for i in range(4)))
        out.append(r)
    return out


def encode(rows, mips=1):
    """An uncompressed A8R8G8B8 DDS (bytes) from rows of (r, g, b, a); mips > 1 appends box-filtered levels,
    mips = 0 means the full chain down to 1x1. Stock pattern: ui_load_lok.dds / ui_planet_sel_*.dds headers."""
    h, w = len(rows), len(rows[0])
    if mips == 0:
        mips = max(w, h).bit_length()
    levels, cur = [], rows
    for i in range(mips):
        levels.append(cur)
        if i + 1 < mips:
            cur = _box_down(cur)
    data = bytearray()
    for lv in levels:
        for row in lv:
            for r, g, b, a in row:
                data += struct.pack('<I', (a << 24) | (r << 16) | (g << 8) | b)
    flags = FLAGS_BASE | FLAG_LINEAR | (FLAG_MIPS if mips > 1 else FLAG_MIPS)   # stock sets MIPMAPCOUNT even with 0 mips
    caps1 = CAPS_TEXTURE | CAPS_COMPLEX | CAPS_MIPMAP                          # stock: 0x401008 on ui textures
    hdr = {'size': 124, 'flags': flags, 'height': h, 'width': w, 'pitch': w * h * 4, 'depth': 0,
           'mips': mips if mips > 1 else 0, 'reserved': [0] * 11, 'pf_size': 32, 'pf_flags': PF_RGB | PF_ALPHA,
           'fourcc': b'\0\0\0\0', 'bpp': 32, 'masks': [0xff0000, 0xff00, 0xff, 0xff000000], 'caps': [caps1, 0, 0, 0], 'reserved2': 0}
    return write({'header': hdr, 'data': bytes(data)})


SELFTEST = ['texture/loading/lok/ui_load_lok.dds',        # uncompressed A8R8G8B8, no mips
            'texture/ui_map_hoth.dds',                     # uncompressed R8G8B8 24-bit (MTG), 1 mip
            'texture/ui_planet_sel_tatt.dds',              # DXT1, 9 mips
            'texture/ui_planet_sel_hoth.dds']              # DXT5, 9 mips (MTG)


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'Fable-planet-test', 'tools'))
    import trn_iff
    idx = trn_iff.client_index()
    ok = True
    for n in SELFTEST:
        d = trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, idx[n]), n)
        back = write(read(d))
        h = read(d)['header']
        print('%-45s %8d B  %s  fourcc=%r bpp=%d mips=%d flags=%#x caps=%#x  roundtrip %s' % (
            n, len(d), idx[n], h['fourcc'], h['bpp'], h['mips'], h['flags'], h['caps'][0], back == d))
        ok &= back == d
        if is_uncompressed(h):
            px = decode_pixels(read(d))
            expect = h['width'] * h['height'] * h['bpp'] // 8 * (1 if h['mips'] <= 1 else 1)
            print('    decoded %dx%d, first pixel %s, data bytes %d (top level %d)' % (len(px[0]), len(px), px[0][0], len(d) - 128, expect))
    # encode -> read -> decode gives the pixels back, header fields match the stock pattern
    rows = [[((x * 7) & 255, (y * 3) & 255, (x ^ y) & 255, 255) for x in range(16)] for y in range(8)]
    e = encode(rows, mips=0)
    r = read(e)
    px = decode_pixels(r)
    same = px == rows and r['header']['mips'] == 5 and r['header']['width'] == 16 and len(r['data']) == sum(max(1, 16 >> i) * max(1, 8 >> i) * 4 for i in range(5))
    print('encode/decode 16x8 with a 5-level chain:', same)
    ok &= same
    print('SELFTEST', 'PASSED' if ok else 'FAILED')
    return ok


if __name__ == '__main__':
    sys.exit(0 if ('--selftest' in sys.argv and selftest()) else 1)
