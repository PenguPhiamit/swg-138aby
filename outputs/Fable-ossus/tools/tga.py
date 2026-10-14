"""8-bit greyscale TGA (image type 3, uncompressed, bottom-left origin) writer and reader for terrain bitmaps.
Our own code (Fable, 14 Oct 2026). Core3's TargaBitmap ignores the descriptor byte and the client honours it, so
the file is written with the TGA default (origin bottom-left, descriptor 0): file row 0 is the SOUTH edge of the
layer's boundary rectangle and column 0 its WEST edge, which is also how Core3's FilterBitmap samples it
(Fable-planet-test/tools/trn_read.py: load_tga_grey + bitmap_filter).
"""
import struct


def write_tga_grey(path, width, height, rows_south_to_north):
    """rows_south_to_north: height rows of width ints 0..255, the first row being the southern edge."""
    assert len(rows_south_to_north) == height and all(len(r) == width for r in rows_south_to_north)
    header = struct.pack('<BBBHHBHHHHBB', 0, 0, 3, 0, 0, 0, 0, 0, width, height, 8, 0)
    with open(path, 'wb') as f:
        f.write(header)
        for r in rows_south_to_north:
            f.write(bytes(r))


def read_tga_grey(data):
    """Plain reader (file order): (width, height, rows_south_to_north)."""
    idlen, cmaptype, datatype = data[0], data[1], data[2]
    width, height, bpp, desc = struct.unpack_from('<HHBB', data, 12)
    assert datatype == 3 and bpp == 8 and desc & 0x20 == 0
    pos = 18 + idlen
    rows = [list(data[pos + r * width: pos + (r + 1) * width]) for r in range(height)]
    return width, height, rows
