"""Read SWG client data the way Core3 does: files from the archives the client loads, datatables and string files.
Read-only; nothing is extracted to disk.

    python -I tools/owner_content/swg_client_data.py datatables/skill/skills.iff [row-filter]
    python -I tools/owner_content/swg_client_data.py string/en/skl_n.stf [key-filter]

Formats follow Core3-dev: src/templates/datatables/DataTableIff.cpp (FORM DTII > FORM 0001 > COLS, TYPE, ROWS; 's'
cells are zero-terminated strings, 'f' floats, every other type a 32-bit integer) and src/templates/string/StringFile.cpp
(0xABCD header, a byte, next id, count, then id/crc/UTF-16 text records and id/ASCII key records).
"""
import os, struct, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hoth'))
import client_load_order as clo  # noqa: E402  (also brings Bellum's read_tre and _inflate)

_index = None


def _build_index():
    global _index
    _index = {}
    trees, _, _ = clo.load_order()
    for priority, name in reversed(trees):  # lowest first, so higher priorities overwrite
        path = os.path.join(clo.CLIENT, name)
        if os.path.exists(path):
            for entry in clo.read_tre(path):
                _index[entry['name'].lower()] = (path, entry)


def client_file(name):
    """Bytes of a client file from the archive that wins in the client's load order, or None."""
    if _index is None:
        _build_index()
    hit = _index.get(name.lower())
    if not hit:
        return None
    path, entry = hit
    with open(path, 'rb') as f:
        f.seek(entry['offset'])
        blob = f.read(entry['comp_size'] if entry['comp'] else entry['size'])
    return clo._inflate(blob, entry['comp'], entry['size'])


def iff_chunks(data, start=0, end=None):
    """Yield (tag, form_type_or_None, body_start, body_end) for the IFF items between start and end."""
    end = len(data) if end is None else end
    i = start
    while i + 8 <= end:
        tag = data[i:i + 4].decode('ascii', 'replace')
        size = struct.unpack_from('>I', data, i + 4)[0]
        if tag == 'FORM':
            yield tag, data[i + 8:i + 12].decode('ascii', 'replace'), i + 12, i + 8 + size
        else:
            yield tag, None, i + 8, i + 8 + size
        i += 8 + size


def _cstring(data, i):
    j = data.index(b'\0', i)
    return data[i:j].decode('latin-1'), j + 1


def datatable(data):
    """List of row dicts {column: value} from a DTII datatable."""
    (_, kind, a, b), = list(iff_chunks(data))[:1]
    assert kind == 'DTII', kind
    (_, version, a, b) = next(iff_chunks(data, a, b))
    cols, types, rows = [], [], []
    for tag, _, s, e in iff_chunks(data, a, b):
        if tag == 'COLS':
            n, i = struct.unpack_from('<I', data, s)[0], s + 4
            for _ in range(n):
                c, i = _cstring(data, i)
                cols.append(c)
        elif tag == 'TYPE':
            i = s
            for _ in cols:
                t, i = _cstring(data, i)
                types.append(t[:1])
        elif tag == 'ROWS':
            n, i = struct.unpack_from('<I', data, s)[0], s + 4
            for _ in range(n):
                row = {}
                for c, t in zip(cols, types):
                    if t == 's':
                        row[c], i = _cstring(data, i)
                    elif t == 'f':
                        row[c], i = struct.unpack_from('<f', data, i)[0], i + 4
                    else:
                        row[c], i = struct.unpack_from('<i', data, i)[0], i + 4
                rows.append(row)
    return rows


def string_file(data):
    """Dict {key: text} from a .stf string file."""
    magic = struct.unpack_from('<I', data, 0)[0]
    assert magic & 0xFFFF == 0xABCD, hex(magic)
    count = struct.unpack_from('<I', data, 9)[0]
    i, text = 13, {}
    for _ in range(count):
        num, _crc, n = struct.unpack_from('<III', data, i)
        text[num] = data[i + 12:i + 12 + 2 * n].decode('utf-16-le', 'replace')
        i += 12 + 2 * n
    out = {}
    for _ in range(count):
        num, n = struct.unpack_from('<II', data, i)
        out[data[i + 8:i + 8 + n].decode('latin-1')] = text.get(num, '')
        i += 8 + n
    return out


def main(argv):
    name, needle = argv[0], (argv[1].lower() if len(argv) > 1 else '')
    data = client_file(name)
    if data is None:
        print(f'{name}: not in any archive the client loads')
        return 1
    if name.endswith('.stf'):
        for k, v in string_file(data).items():
            if needle in k.lower() or needle in v.lower():
                print(f'{k}\t{v}')
    else:
        rows = datatable(data)
        print(f'{len(rows)} rows; columns: {", ".join(rows[0]) if rows else "-"}')
        for r in rows:
            if needle and needle not in str(r).lower():
                continue
            print({k: v for k, v in r.items() if v not in ('', 0)})
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
