"""Ossus look pass (O9): an orange-gold atmosphere, as in the Legends picture of Ossus from space (Claude, 17 Oct 2026).

Ossus's sky and light come from datatables/environment/ossus.iff, which since O1c names Dantooine's sky gradient
(texture/grad_sky_dantooine.dds, 256x32 RGB) and lighting colour ramp (terrain/colorramp/dantooine_global0.tga,
256x8: the light, ambient, fog and sky colours across the day). This step makes our own warm versions of both from
Dantooine's (each pixel pulled toward gold at the same brightness, so night stays night) and points every Ossus row
at them. The four bad-weather rows of each family (no sky gradient: overcast) keep their overcast and get a
lightly warmed copy of their own ramp (Naboo's naboo_global1.tga). Terrain shape, shaders, flora and every other entry
stay byte for byte.
  new      texture/grad_sky_ossus.dds              Dantooine's gradient, gold pull SKY_PULL
  new      terrain/colorramp/ossus_global0.tga     Dantooine's ramp, gold pull per row RAMP_PULL (clear weather)
  new      terrain/colorramp/ossus_overcast0.tga   Naboo's naboo_global1 ramp, gold pull OVERCAST_PULL (weather 1-4)
  changed  datatables/environment/ossus.iff        clear rows: columns 2 (sky) and 9 (ramp); weather rows: column 9

    C:/Users/Pengw/miniconda3/python.exe -I build_ossus_look.py [--base PATH] [--out PATH] [--sky K] [--ramp K]
Default base: ../../../work/nal-hutta-life/local_planets-nalhutta-life.tre (installed, sha256 b01e9f44...).
Default out:  ../../../work/ossus-look/local_planets-ossus-look.tre (+ .sha256); checks and before/after colours in
./checks-look.json, and ../../../work/ossus-look/preview-*.png (before and after).
"""
import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'nal-hutta-life', 'local_planets-nalhutta-life.tre')
DEFAULT_BASE_SHA_PREFIX = 'b01e9f44'
WORK = os.path.join(H, 'work', 'ossus-look')
DEFAULT_OUT = os.path.join(WORK, 'local_planets-ossus-look.tre')
ENV = 'datatables/environment/ossus.iff'
SKY_SRC, SKY_NEW = 'texture/grad_sky_dantooine.dds', 'texture/grad_sky_ossus.dds'
RAMP_SRC, RAMP_NEW = 'terrain/colorramp/dantooine_global0.tga', 'terrain/colorramp/ossus_global0.tga'
OVC_SRC, OVC_NEW = 'terrain/colorramp/naboo_global1.tga', 'terrain/colorramp/ossus_overcast0.tga'
OVERCAST_PULL = 0.20
GOLD = (255, 168, 72)        # the orange-gold of the Legends picture's limb, as a hue; brightness comes from each pixel
SKY_PULL = 0.55
# rows 0-7 of the ramp; the lit rows get a lighter pull so the ground keeps its greens
RAMP_PULL = [0.30, 0.25, 0.25, 0.30, 0.35, 0.50, 0.35, 0.45]
SKY_COL, RAMP_COL = 2, 9


def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def warm(rgb, k):
    r, g, b = rgb
    L = lum(r, g, b)
    if L <= 0:
        return rgb
    s = L / lum(*GOLD)
    t = [c * s for c in GOLD]
    return tuple(max(0, min(255, int(round((1 - k) * c + k * tc)))) for c, tc in zip(rgb, t))


def dds_pixels(data):
    h = struct.unpack('<31I', data[4:128])
    height, width, flags, bits = h[2], h[3], h[19], h[21]
    masks = h[22:25]
    assert data[:4] == b'DDS ' and flags == 0x40 and bits == 24 and masks == (0xff0000, 0xff00, 0xff), (flags, bits, masks)
    body = data[128:]
    assert len(body) == width * height * 3, len(body)
    return width, height, [(body[i + 2], body[i + 1], body[i]) for i in range(0, len(body), 3)]


def dds_write(src, pixels):
    return src[:128] + b''.join(bytes((b, g, r)) for r, g, b in pixels)


def tga_pixels(data):
    idlen, cmap, kind = data[0], data[1], data[2]
    w, h = struct.unpack('<HH', data[12:16])
    bpp = data[16]
    assert cmap == 0 and kind == 2 and bpp == 32, (cmap, kind, bpp)
    off = 18 + idlen
    body = data[off:off + w * h * 4]
    return w, h, off, [tuple(body[i:i + 4]) for i in range(0, len(body), 4)]   # BGRA


def warm_ramp(src, pulls):
    """(bytes, w, h, rows before, rows after) for a 256x8 BGRA colour ramp, each stored row pulled by its own amount."""
    w, h, off, px = tga_pixels(src)
    before = [[(p[2], p[1], p[0]) for p in px[y * w:(y + 1) * w]] for y in range(h)]
    after = [[warm(p, pulls[y]) for p in row] for y, row in enumerate(before)]
    body = b''.join(bytes((b, g, r, px[y * w + x][3])) for y, row in enumerate(after) for x, (r, g, b) in enumerate(row))
    out = src[:off] + body + src[off + w * h * 4:]
    assert len(out) == len(src)
    return out, w, h, before, after


def sample(rows, w, cols=(0, 32, 64, 96, 128, 160, 192, 224)):
    return [['%02x%02x%02x' % px for px in (row[c] for c in cols)] for row in rows]


def png(path, w, h, pixels, scale=1):
    """A plain RGB PNG (our own writer: zlib + crc32), each pixel drawn scale x scale."""
    import zlib

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''
    for y in range(h):
        line = b'\x00' + b''.join(bytes(pixels[y * w + x]) * scale for x in range(w))
        raw += line * scale
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 2, 0, 0, 0)) +
                chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--sky', type=float, default=SKY_PULL)
    ap.add_argument('--ramp', type=float, default=None, help='one pull for every ramp row instead of RAMP_PULL')
    args = ap.parse_args(argv)
    ramp_pull = [args.ramp] * 8 if args.ramp is not None else RAMP_PULL
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the installed b01e9f44: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    assert SKY_NEW not in base and RAMP_NEW not in base and OVC_NEW not in base

    env = st.read_dtii(base[ENV])
    assert st.write_dtii(env) == base[ENV], 'environment table does not round-trip'
    before_cols = sorted(set((r[SKY_COL], r[RAMP_COL]) for r in env['rows']))

    # the sky gradient
    sky_src = trn_iff.client_file(SKY_SRC)
    w, h, px = dds_pixels(sky_src)
    sky_px = [warm(p, args.sky) for p in px]
    sky = dds_write(sky_src, sky_px)
    assert dds_pixels(sky)[2] == sky_px

    ramp, rw, rh, rows_before, rows_after = warm_ramp(trn_iff.client_file(RAMP_SRC), ramp_pull)
    ovc, _, _, ovc_before, ovc_after = warm_ramp(trn_iff.client_file(OVC_SRC), [OVERCAST_PULL] * 8)

    rows = [list(r) for r in env['rows']]
    for r in rows:
        if r[SKY_COL] == SKY_SRC and r[RAMP_COL] == RAMP_SRC:
            r[SKY_COL], r[RAMP_COL] = SKY_NEW, RAMP_NEW
        else:
            assert r[SKY_COL] == '' and r[RAMP_COL] == OVC_SRC, r
            r[RAMP_COL] = OVC_NEW
    env_out = st.write_dtii({'version': env['version'], 'columns': env['columns'], 'types': env['types'], 'rows': rows})
    back = st.read_dtii(env_out)['rows']
    assert all(b[:SKY_COL] + b[SKY_COL + 1:RAMP_COL] + b[RAMP_COL + 1:] == o[:SKY_COL] + o[SKY_COL + 1:RAMP_COL] + o[RAMP_COL + 1:]
               for b, o in zip(back, env['rows'])), 'other columns moved'

    files = dict(base)
    files[ENV], files[SKY_NEW], files[RAMP_NEW], files[OVC_NEW] = env_out, sky, ramp, ovc
    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))

    os.makedirs(WORK, exist_ok=True)
    png(os.path.join(WORK, 'preview-sky-before.png'), w, h, px, 2)
    png(os.path.join(WORK, 'preview-sky-after.png'), w, h, sky_px, 2)
    png(os.path.join(WORK, 'preview-ramp-before.png'), rw, rh, [p for row in rows_before for p in row], 4)
    png(os.path.join(WORK, 'preview-ramp-after.png'), rw, rh, [p for row in rows_after for p in row], 4)
    png(os.path.join(WORK, 'preview-overcast-before.png'), rw, rh, [p for row in ovc_before for p in row], 4)
    png(os.path.join(WORK, 'preview-overcast-after.png'), rw, rh, [p for row in ovc_after for p in row], 4)

    ours = tre_write.read(out)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    new = sorted(n for n in ours if n not in base)
    dropped = sorted(n for n in base if n not in ours)
    sky_rows = [sky_px[y * w:(y + 1) * w] for y in range(h)]
    sky_rows_before = [px[y * w:(y + 1) * w] for y in range(h)]
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'sha256': base_sha, 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha, 'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped), 'changed': changed, 'new': new, 'dropped': dropped,
        'environment_before': before_cols, 'environment_after': sorted(set((r[SKY_COL], r[RAMP_COL]) for r in back)),
        'gold': GOLD, 'sky_pull': args.sky, 'ramp_pull': ramp_pull, 'overcast_pull': OVERCAST_PULL,
        'overcast_rows_before_at_8_times': sample(ovc_before, rw), 'overcast_rows_after_at_8_times': sample(ovc_after, rw),
        'ramp_rows_before_at_8_times': sample(rows_before, rw), 'ramp_rows_after_at_8_times': sample(rows_after, rw),
        'sky_top_middle_bottom_before': sample([sky_rows_before[0], sky_rows_before[h // 2], sky_rows_before[-1]], w),
        'sky_top_middle_bottom_after': sample([sky_rows[0], sky_rows[h // 2], sky_rows[-1]], w),
    }
    with open(os.path.join(HERE, 'checks-look.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped and changed == [ENV] and new == sorted([SKY_NEW, RAMP_NEW, OVC_NEW]), (changed, new, dropped)
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new', 'environment_before', 'environment_after')}, indent=1))
    print('Ossus look step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
