"""Probe a TRE archive streamed on stdin (used for the disc's version-6 archives, which live inside WSL). Read-only;
nothing is written. Tries the version-5 index layout (36-byte header, 24-byte records, zlib blocks) and reports
whether it parses, how many entries it finds, and which names match the given substrings.

    MSYS_NO_PATHCONV=1 wsl -d Debian -u swgemu -- cat /opt/swg/disc-extracted/.../patch_sku3_24_shared_00.tre \
        | python -I tre_v6_probe.py jeditemple must_
"""
import struct
import sys
import zlib


def main(argv):
    data = sys.stdin.buffer.read()
    magic, version = data[:4], data[4:8]
    print(f'{len(data)} bytes, magic {magic!r}, version {version!r}')
    if magic != b'EERT':
        return 1
    count, info_off, info_comp, info_size_c, name_comp, name_size_c, name_size_u = struct.unpack_from('<7I', data, 8)
    print(f'header: records {count}, index at {info_off}, index comp {info_comp} size {info_size_c}, names comp {name_comp} '
          f'size {name_size_c}/{name_size_u}')
    try:
        info = data[info_off:info_off + info_size_c]
        if info_comp == 2:
            info = zlib.decompress(info)
        names = data[info_off + info_size_c:info_off + info_size_c + name_size_c]
        if name_comp == 2:
            names = zlib.decompress(names)
        print(f'index block {len(info)} bytes = {len(info) / max(count, 1):.1f} bytes per record; name block {len(names)} bytes')
        rec = 24 if len(info) == count * 24 else (len(info) // count if count else 0)
        entries = []
        for i in range(count):
            crc, size, offset, comp, comp_size, name_off = struct.unpack_from('<IIIIII', info, i * rec)
            end = names.index(b'\0', name_off)
            entries.append((names[name_off:end].decode('latin-1'), size, offset, comp))
        print(f'parsed {len(entries)} entries with {rec}-byte records; first: {entries[:3]}')
        for needle in argv:
            hits = [e[0] for e in entries if needle in e[0]]
            print(f'  "{needle}": {len(hits)} hits, e.g. {hits[:8]}')
        # sanity: decompress the first small compressed entry
        for name, size, offset, comp in entries:
            if comp == 2 and size < 20000:
                blob = data[offset:offset + size * 4]
                out = zlib.decompressobj().decompress(blob)
                print(f'  sample entry {name}: {len(out)} of {size} bytes inflate OK')
                break
    except Exception as ex:
        print('v5-style parse FAILED:', type(ex).__name__, str(ex)[:200])
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
