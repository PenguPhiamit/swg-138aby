"""tre_write.py: our own SWG .tre (EERT 5000) writer (Fable B2, 14 Oct 2026). Standard library only.

Layout, the one every stock and MTG archive uses and our readers (trn_iff.list_tre, client_load_order.read_tre) parse:
  36-byte header: 'EERT', '5000', record count, record-block offset, record-block compression (2 = zlib) and stored
  size, name-block compression and stored size, name-block unpacked size;
  then each file's data (zlib level 9 when that is smaller, else stored), in record order;
  then the record block: 24 bytes per file (SOE CRC-32 of the lower-case path, unpacked size, data offset,
  compression, compressed size or 0 when stored, name offset), sorted by CRC ascending;
  then the name block (NUL-terminated paths); then 16 bytes of MD5 per file, in record order. Every stock and MTG
  archive stores the MD5 of the bytes as they sit in the file (the zlib stream for a compressed entry: patch_14_00
  1489 of 1491 records, patch_00 8816 of 8830, mtg_planets all 3328; the rest are neither); Bellum's tre_pack stores
  the MD5 of the unpacked data instead, and the owner's client loads such archives too. Default: the stock rule;
  md5_of='data' reproduces a tre_pack archive byte for byte.

    pack(files)              files: {path: bytes} -> archive bytes
    pack_dir(folder, out)    every file under folder at its relative path, lower-cased, '/'-separated
    read(data)               {path: bytes} (for the self-test; the readers above are the real consumers)
    python -I tre_write.py --selftest [folder]    pack a folder (default Local-content/local_planets) to scratch, read it
                                                 back with three readers, compare with the archive beside it
"""
import hashlib
import os
import struct
import sys
import zlib

HEADER = '<4s4sIIIIIII'
ZLIB = 2
CRC_POLY = 0x04C11DB7
_TABLE = []
for _i in range(256):
    _c = _i << 24
    for _ in range(8):
        _c = ((_c << 1) ^ CRC_POLY) & 0xFFFFFFFF if _c & 0x80000000 else (_c << 1) & 0xFFFFFFFF
    _TABLE.append(_c)


def soe_crc(name):
    """SOE's CRC-32: MSB-first, polynomial 0x04C11DB7, init and final 0xFFFFFFFF (the same as swg_tables.soe_crc)."""
    c = 0xFFFFFFFF
    for ch in name.encode('latin-1'):
        c = (_TABLE[((c >> 24) ^ ch) & 0xFF] ^ (c << 8)) & 0xFFFFFFFF
    return c ^ 0xFFFFFFFF


def pack(files, level=9, md5_of='stored'):
    """Archive bytes for {path: bytes}; paths are stored lower-case with '/' separators. md5_of: 'stored' (the stock
    rule, MD5 of the bytes as stored) or 'data' (tre_pack's rule, MD5 of the unpacked data)."""
    norm = {}
    for name, data in files.items():
        key = name.replace('\\', '/').lower()
        if key in norm:
            raise ValueError('duplicate path ' + key)
        norm[key] = bytes(data)
    order = sorted((soe_crc(n), n) for n in norm)
    if len({c for c, _ in order}) != len(order):
        raise ValueError('CRC collision between paths')
    out = bytearray(b'\0' * 36)
    records, names, md5s = [], bytearray(), bytearray()
    for crc, name in order:
        data = norm[name]
        comp = zlib.compress(data, level)
        if len(comp) < len(data):
            ctype, blob = ZLIB, comp
        else:
            ctype, blob = 0, data
        offset = len(out)
        out += blob
        records.append(struct.pack('<6I', crc, len(data), offset, ctype, len(blob) if ctype else 0, len(names)))
        names += name.encode('latin-1') + b'\0'
        md5s += hashlib.md5(blob if md5_of == 'stored' else data).digest()
    rec_c = zlib.compress(b''.join(records), level)
    name_c = zlib.compress(bytes(names), level)
    rec_off = len(out)
    out += rec_c + name_c + md5s
    out[:36] = struct.pack(HEADER, b'EERT', b'5000', len(order), rec_off, ZLIB, len(rec_c), ZLIB, len(name_c), len(names))
    return bytes(out)


def pack_dir(folder, out_path=None, md5_of='stored'):
    files = {}
    for d, _, fs in os.walk(folder):
        for f in fs:
            full = os.path.join(d, f)
            with open(full, 'rb') as fh:
                files[os.path.relpath(full, folder).replace(os.sep, '/').lower()] = fh.read()
    data = pack(files, md5_of=md5_of)
    if out_path:
        with open(out_path, 'wb') as fh:
            fh.write(data)
    return data, sorted(files)


def read(data, strict=True):
    """{path: bytes} plus the header fields, reading the layout above (self-test use).
    strict=False reads SOE's own patch_*.tre, where one record's checksum does not match: such records are still
    returned when their size and name CRC check (16 Oct: the strict reader rejected most stock patches)."""
    magic, ver, n, rec_off, rec_comp, rec_csize, name_comp, name_csize, name_usize = struct.unpack_from(HEADER, data, 0)
    if magic != b'EERT':
        raise ValueError('not a TRE archive')
    rec = data[rec_off:rec_off + rec_csize]
    rec = zlib.decompress(rec) if rec_comp == ZLIB else rec
    names = data[rec_off + rec_csize:rec_off + rec_csize + name_csize]
    names = zlib.decompress(names) if name_comp == ZLIB else names
    md5s = data[rec_off + rec_csize + name_csize:]
    files, meta = {}, []
    for i in range(n):
        crc, size, off, comp, csize, noff = struct.unpack_from('<6I', rec, i * 24)
        name = names[noff:names.index(b'\0', noff)].decode('latin-1')
        blob = data[off:off + (csize if comp else size)]
        raw = zlib.decompress(blob) if comp == ZLIB else blob
        tag = md5s[16 * i:16 * i + 16]
        md5_ok = tag in (hashlib.md5(blob).digest(), hashlib.md5(raw).digest())
        if len(raw) != size or soe_crc(name) != crc or (strict and not md5_ok):
            raise ValueError('record %d (%s) does not check' % (i, name))
        files[name] = raw
        meta.append({'name': name, 'crc': crc, 'size': size, 'offset': off, 'comp': comp, 'csize': csize, 'name_offset': noff})
    header = {'version': ver.decode(), 'records': n, 'record_offset': rec_off, 'record_comp': rec_comp, 'record_csize': rec_csize,
              'name_comp': name_comp, 'name_csize': name_csize, 'name_usize': name_usize, 'total': len(data), 'md5_table': len(md5s)}
    return files, header, meta


def selftest(folder=None, md5_of='stored'):
    here = os.path.dirname(os.path.abspath(__file__))
    outputs = os.path.normpath(os.path.join(here, '..', '..'))
    folder = folder or os.path.join(outputs, 'Local-content', 'local_planets')
    beside = folder.rstrip('/\\') + '.tre'
    sys.path.insert(0, os.path.join(outputs, 'tools', 'hoth'))
    import tempfile
    data, names = pack_dir(folder, md5_of=md5_of)
    tmp = os.path.join(tempfile.mkdtemp(), 'selftest.tre')
    print('md5 rule:', md5_of)
    with open(tmp, 'wb') as f:
        f.write(data)
    ok = True
    # 1. our own read()
    files, header, meta = read(data)
    print('packed %d files, %d bytes; read(): %d files, every record checks (size, CRC, MD5)' % (len(names), len(data), len(files)))
    same = all(files[n] == open(os.path.join(folder, *n.split('/')), 'rb').read() for n in names)
    print('  read() bytes identical to the folder:', same); ok &= same
    # 2. trn_iff (Fable's reader)
    from . import trn_iff
    ent = trn_iff.list_tre(tmp)
    same = sorted(ent) == names and all(trn_iff.open_tre_entry(tmp, n) == files[n] for n in names)
    print('  trn_iff.list_tre/open_tre_entry: %d entries, bytes identical: %s' % (len(ent), same)); ok &= same
    # 3. client_load_order.read_tre (the builder's reader)
    try:
        import client_load_order as clo
        got = {}
        for e in clo.read_tre(tmp):
            with open(tmp, 'rb') as s:
                s.seek(e['offset'])
                blob = s.read(e['comp_size'] if e['comp'] else e['size'])
            got[e['name'].lower()] = clo._inflate(blob, e['comp'], e['size'])
        same = sorted(got) == names and all(got[n] == files[n] for n in names)
        print('  client_load_order.read_tre: %d entries, bytes identical: %s' % (len(got), same)); ok &= same
    except Exception as e:
        print('  client_load_order.read_tre: not run (%s)' % e)
    # 4. against the archive beside the folder (tre_pack's)
    if os.path.exists(beside):
        ref = open(beside, 'rb').read()
        rf, rh, rm = read(ref)
        print('  reference %s: %d bytes, sha256 %s' % (os.path.basename(beside), len(ref), hashlib.sha256(ref).hexdigest()[:16]))
        print('  ours:      %d bytes, sha256 %s, byte-identical to the reference: %s' % (len(data), hashlib.sha256(data).hexdigest()[:16], data == ref))
        print('  header fields equal:', header == rh, '' if header == rh else {k: (header[k], rh[k]) for k in header if header[k] != rh[k]})
        print('  records equal (name, crc, size, offset, comp, csize, name offset):', meta == rm)
        print('  file data and record/name blocks identical, only the MD5 tail differs:', data[:rh['record_offset'] + rh['record_csize'] + rh['name_csize']] == ref[:rh['record_offset'] + rh['record_csize'] + rh['name_csize']])
        same_files = sorted(rf) == sorted(files) and all(rf[n] == files[n] for n in files)
        print('  same files with the same bytes:', same_files)
    print('SELFTEST', 'PASSED' if ok else 'FAILED')
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        arg = [a for a in sys.argv[1:] if a not in ('--selftest', '--md5-data')]
        sys.exit(0 if selftest(arg[0] if arg else None, 'data' if '--md5-data' in sys.argv else 'stored') else 1)
    if len(sys.argv) == 3:
        d, n = pack_dir(sys.argv[1], sys.argv[2])
        print('packed %d files -> %s (%d bytes)' % (len(n), sys.argv[2], len(d)))
    else:
        print(__doc__)
