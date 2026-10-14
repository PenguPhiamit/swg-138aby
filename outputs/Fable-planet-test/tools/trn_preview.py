"""Render a .trn's server-side heightfield as a greyscale PNG (standard library only). Our own code (Fable, 14 Oct 2026).

    python -I trn_preview.py <spec> <out.png> [--res 256] [--water] [--gamma 0.5]

Heights come from trn_read.HeightEvaluator (the Core3 port). Black = lowest, white = highest (gamma 0.5 by default,
so low ground is not crushed by a few peaks); with --water, cells under the global water table are drawn mid-grey.
North is up (world +y), west is left (world -x).
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trn_iff import load  # noqa: E402
import trn_read  # noqa: E402


def write_png(path, width, height, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    spec, out = argv[0], argv[1]
    res = int(argv[argv.index('--res') + 1]) if '--res' in argv else 256
    gamma = float(argv[argv.index('--gamma') + 1]) if '--gamma' in argv else 0.5  # lifts low ground so hills show
    show_water = '--water' in argv
    trn = trn_read.read_trn(load(spec))
    ev = trn_read.HeightEvaluator(trn, trn_read.client_bitmap_loader)
    half = trn['header']['size'] / 2
    step = trn['header']['size'] / res
    grid = []
    for j in range(res):
        y = half - (j + 0.5) * step  # top row = north
        grid.append([ev.height(-half + (i + 0.5) * step, y) for i in range(res)])
    lo = min(min(r) for r in grid)
    hi = max(max(r) for r in grid)
    water = trn['header']['global_water_height'] if trn['header']['use_global_water_table'] else None
    rows = []
    for r in grid:
        row = []
        for h in r:
            if show_water and water is not None and h < water:
                row.append(96)
            else:
                row.append(int(255 * ((h - lo) / (hi - lo)) ** gamma) if hi > lo else 0)
        rows.append(row)
    write_png(out, res, res, rows)
    print(f'{out}: {res}x{res}, heights {lo:.1f}..{hi:.1f} m' + (f', water at {water:.1f} m' if water is not None else ''))
    for w in sorted(set(ev.warnings)):
        print('warning:', w)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
