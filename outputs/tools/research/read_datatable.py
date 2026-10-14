"""Read a client datatable (IFF DTII) straight out of the TRE archives, read-only.

Inside Debian (as swgemu):
  python3 read_datatable.py datatables/skill/skills.iff [--find text] [--cols NAME,COMMANDS] [--tre /opt/swg/tre]

--find prints the rows where any cell contains the text (any case). Without it, prints the column names.
When several archives hold the file, the copy from the archive that sorts last is used (patch archives
like mtg_patch_* and hotfix_* override the base data), and the others are listed.
"""
from pathlib import Path
import struct, sys, zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))


def tre_entries(path):
    with path.open('rb') as f:
        magic, version, count, offset, ftype, fsize, ntype, nsize, usize = struct.unpack('<4s4s7I', f.read(36))
        if magic != b'EERT' or version != b'5000':
            return
        f.seek(offset)
        records = f.read(fsize if ftype == 2 else count * 24)
        if ftype == 2:
            records = zlib.decompress(records)
        names = f.read(nsize if ntype == 2 else usize)
        if ntype == 2:
            names = zlib.decompress(names)
    for i in range(count):
        record = struct.unpack_from('<6I', records, i * 24)
        start = record[5]
        yield names[start:names.find(b'\0', start)].decode('latin1'), record


def read_file(archive, record):
    with archive.open('rb') as f:
        f.seek(record[2])
        data = f.read(record[4] if record[3] == 2 else record[1])
    return zlib.decompress(data) if record[3] == 2 else data


def chunks(data, start=0, end=None):
    """(tag, payload, form_type) for each IFF chunk; FORM chunks give their 4-byte type and inner payload."""
    end = len(data) if end is None else end
    i = start
    while i + 8 <= end:
        tag = data[i:i + 4].decode('latin1')
        size = struct.unpack('>I', data[i + 4:i + 8])[0]
        body = data[i + 8:i + 8 + size]
        if tag == 'FORM':
            yield tag, body[4:], body[:4].decode('latin1')
        else:
            yield tag, body, None
        i += 8 + size


def parse_dtii(data):
    (tag, body, kind), = list(chunks(data))[:1]
    assert tag == 'FORM' and kind == 'DTII', (tag, kind)
    inner = next(c for c in chunks(body) if c[0] == 'FORM')[1]  # FORM 0001
    columns, types, rows = [], [], []
    for tag, payload, _ in chunks(inner):
        if tag == 'COLS':
            count = struct.unpack('<I', payload[:4])[0]
            columns = [c.decode('latin1') for c in payload[4:].split(b'\0')[:count]]
        elif tag == 'TYPE':
            types = [t.decode('latin1') for t in payload.split(b'\0')[:len(columns)]]
        elif tag == 'ROWS':
            count = struct.unpack('<I', payload[:4])[0]
            i = 4
            for _ in range(count):
                row = []
                for t in types:
                    code = t[:1].lower()
                    if code in ('s', 'p', 'c'):  # strings (and string-like)
                        end = payload.index(b'\0', i)
                        row.append(payload[i:end].decode('latin1'))
                        i = end + 1
                    elif code == 'f':
                        row.append(round(struct.unpack('<f', payload[i:i + 4])[0], 4))
                        i += 4
                    else:  # i, b, h, e, z: 32-bit integers
                        row.append(struct.unpack('<i', payload[i:i + 4])[0])
                        i += 4
                rows.append(row)
    return columns, types, rows


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    target = args[0]
    tre = Path(args[args.index('--tre') + 1]) if '--tre' in args else Path('/opt/swg/tre')
    find = args[args.index('--find') + 1].lower() if '--find' in args else None
    wanted = args[args.index('--cols') + 1].split(',') if '--cols' in args else None
    found = []
    for archive in sorted(tre.glob('*.tre')):
        for name, record in tre_entries(archive) or []:
            if name == target:
                found.append((archive, record))
    if not found:
        raise SystemExit(f'{target} is not in {tre}')
    archive, record = found[-1]
    print(f'{target}: using {archive.name}' + (f' (also in {", ".join(a.name for a, _ in found[:-1])})' if len(found) > 1 else ''))
    columns, types, rows = parse_dtii(read_file(archive, record))
    if not find:
        print(f'{len(rows)} rows; columns: ' + ', '.join(f'{c}:{t}' for c, t in zip(columns, types)))
        return
    show = [columns.index(c) for c in wanted] if wanted else range(len(columns))
    for row in rows:
        if any(find in str(cell).lower() for cell in row):
            print(' | '.join(f'{columns[k]}={row[k]}' for k in show))


if __name__ == '__main__':
    main()
