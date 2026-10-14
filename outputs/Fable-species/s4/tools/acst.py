"""customization/asset_customization_manager.iff (FORM ACST): reader, writer, resolver, diff and splice.
Our own code (Fable, 14 Oct 2026); layout from Core3-dev src/templates/customization/AssetCustomizationManagerTemplate.cpp
(the server reads this file too, for creation and image design).

    python -I acst.py roundtrip <file|client:customization/asset_customization_manager.iff>
    python -I acst.py diff <stock> <other>                       # what differs, by appearance
    python -I acst.py splice <stock> <other> <out> appearance/x.sat [...]   # copy those appearances' maps into stock

Tables (chunk order NAME, PNOF, VNOF, DEFV, IRNG, RTYP, UCMP, ULST, UIDX, LLST, LIDX, CIDX; every index 1-based unless
said): NAME = zero-terminated strings addressed by byte offset; PNOF/VNOF = u16 offsets into NAME (palette file names,
variable names); DEFV = u32 default values; IRNG = u32 (min, max) pairs; RTYP = u16, bit 15 set = palette (index into
PNOF) else int range (index into IRNG); UCMP = 3-byte records (VNOF index, RTYP index, DEFV index); ULST = u16 UCMP
indexes (0-based positions); UIDX = 5-byte records (u16 map key, u16 first ULST position, u8 count), sorted by key;
LLST = u16 map keys; LIDX = 5-byte records (u16 map key, u16 first LLST position, u8 count), sorted by key, the maps a
map inherits from; CIDX = 6-byte records (u32 SOE CRC of the appearance file, u16 map key), sorted by CRC.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'Fable-ossus', 'tools'))
from trn_iff import build, chunk, form, load, parse  # noqa: E402
from swg_tables import soe_crc  # noqa: E402

ORDER = ['NAME', 'PNOF', 'VNOF', 'DEFV', 'IRNG', 'RTYP', 'UCMP', 'ULST', 'UIDX', 'LLST', 'LIDX', 'CIDX']


def read_acst(data):
    root = parse(data)[0]
    assert root.form == 'ACST', root.form
    ver = root.children[0]
    ch = {c.tag: c.data for c in ver.children}
    assert [c.tag for c in ver.children] == ORDER, [c.tag for c in ver.children]
    d = {'version': ver.form, 'names': bytearray(ch['NAME'])}
    d['pnof'] = list(struct.unpack('<%dH' % (len(ch['PNOF']) // 2), ch['PNOF']))
    d['vnof'] = list(struct.unpack('<%dH' % (len(ch['VNOF']) // 2), ch['VNOF']))
    d['defv'] = list(struct.unpack('<%dI' % (len(ch['DEFV']) // 4), ch['DEFV']))
    d['irng'] = [struct.unpack_from('<II', ch['IRNG'], i) for i in range(0, len(ch['IRNG']), 8)]
    d['rtyp'] = list(struct.unpack('<%dH' % (len(ch['RTYP']) // 2), ch['RTYP']))
    d['ucmp'] = [tuple(ch['UCMP'][i:i + 3]) for i in range(0, len(ch['UCMP']), 3)]
    d['ulst'] = list(struct.unpack('<%dH' % (len(ch['ULST']) // 2), ch['ULST']))
    d['uidx'] = [struct.unpack_from('<HHB', ch['UIDX'], i) for i in range(0, len(ch['UIDX']), 5)]
    d['llst'] = list(struct.unpack('<%dH' % (len(ch['LLST']) // 2), ch['LLST']))
    d['lidx'] = [struct.unpack_from('<HHB', ch['LIDX'], i) for i in range(0, len(ch['LIDX']), 5)]
    d['cidx'] = [struct.unpack_from('<IH', ch['CIDX'], i) for i in range(0, len(ch['CIDX']), 6)]
    return d


def write_acst(d):
    parts = [
        chunk('NAME', bytes(d['names'])),
        chunk('PNOF', struct.pack('<%dH' % len(d['pnof']), *d['pnof'])),
        chunk('VNOF', struct.pack('<%dH' % len(d['vnof']), *d['vnof'])),
        chunk('DEFV', struct.pack('<%dI' % len(d['defv']), *d['defv'])),
        chunk('IRNG', b''.join(struct.pack('<II', *p) for p in d['irng'])),
        chunk('RTYP', struct.pack('<%dH' % len(d['rtyp']), *d['rtyp'])),
        chunk('UCMP', b''.join(bytes(t) for t in d['ucmp'])),
        chunk('ULST', struct.pack('<%dH' % len(d['ulst']), *d['ulst'])),
        chunk('UIDX', b''.join(struct.pack('<HHB', *r) for r in d['uidx'])),
        chunk('LLST', struct.pack('<%dH' % len(d['llst']), *d['llst'])),
        chunk('LIDX', b''.join(struct.pack('<HHB', *r) for r in d['lidx'])),
        chunk('CIDX', b''.join(struct.pack('<IH', *r) for r in d['cidx'])),
    ]
    return build([form('ACST', form(d['version'], *parts))])


# ---------------------------------------------------------------- resolving a map the way Core3 walks it

def name_at(d, off):
    n = d['names']
    return bytes(n[off:n.index(b'\0', off)]).decode('latin-1')


def _tables(d):
    if '_u' not in d:
        d['_u'] = {k: (s, c) for k, s, c in d['uidx']}
        d['_l'] = {k: (s, c) for k, s, c in d['lidx']}
        d['_c'] = {crc: k for crc, k in d['cidx']}
    return d


def direct_vars(d, key):
    _tables(d)
    out = []
    if key in d['_u']:
        s, c = d['_u'][key]
        for pos in range(s, s + c):
            vi, ri, di = d['ucmp'][d['ulst'][pos] - 1]
            rt = d['rtyp'][ri - 1]
            if rt & 0x8000:
                typ = ('palette', name_at(d, d['pnof'][(rt & 0x7fff) - 1]))
            else:
                typ = ('range',) + tuple(d['irng'][(rt & 0x7fff) - 1])
            out.append((name_at(d, d['vnof'][vi - 1]), typ, d['defv'][di - 1]))
    return tuple(out)


def link_keys(d, key):
    _tables(d)
    if key not in d['_l']:
        return ()
    s, c = d['_l'][key]
    return tuple(d['llst'][pos] for pos in range(s, s + c))


def resolve(d, key, depth=0):
    """The map's own variables and, recursively, the maps it links to (what getCustomizationVariablesFromMap walks)."""
    if depth > 16:
        return ((), ())
    return (direct_vars(d, key), tuple(resolve(d, k, depth + 1) for k in link_keys(d, key)))


def flatten(r, acc=None):
    """Variables in Core3's order of first appearance (a later one with the same name is ignored)."""
    acc = [] if acc is None else acc
    for v in r[0]:
        if all(a[0] != v[0] for a in acc):
            acc.append(v)
    for l in r[1]:
        flatten(l, acc)
    return acc


def lookup(d, appearance):
    _tables(d)
    return d['_c'].get(soe_crc(appearance))


# ---------------------------------------------------------------- diff

def diff(stock, other, names_by_crc=None):
    _tables(stock); _tables(other)
    sc, oc = stock['_c'], other['_c']
    only_other = sorted(set(oc) - set(sc))
    only_stock = sorted(set(sc) - set(oc))
    common = sorted(set(sc) & set(oc))
    differing = [crc for crc in common if flatten(resolve(stock, sc[crc])) != flatten(resolve(other, oc[crc]))]
    nm = names_by_crc or {}
    label = lambda crc: nm.get(crc, '%08x' % crc)  # noqa: E731
    return {'counts': {k: (len(stock[k]), len(other[k])) for k in ('pnof', 'vnof', 'defv', 'irng', 'rtyp', 'ucmp', 'ulst', 'uidx', 'llst', 'lidx', 'cidx')},
            'names_only_in_other': sorted(set(bytes(other['names']).split(b'\0')) - set(bytes(stock['names']).split(b'\0'))),
            'names_only_in_stock': sorted(set(bytes(stock['names']).split(b'\0')) - set(bytes(other['names']).split(b'\0'))),
            'appearances_only_in_other': [label(c) for c in only_other], 'appearances_only_in_stock': [label(c) for c in only_stock],
            'common': len(common), 'common_with_different_variables': [label(c) for c in differing]}


# ---------------------------------------------------------------- splice

def _add_name(d, s):
    b = s.encode('latin-1') + b'\0'
    i = bytes(d['names']).find(b'\0' + b)
    if i >= 0:
        return i + 1
    if bytes(d['names']).startswith(b):
        return 0
    off = len(d['names'])
    d['names'] += b
    return off


def _index_of(lst, value, make=None):
    """1-based index of value in lst, appending it when absent."""
    try:
        return lst.index(value) + 1
    except ValueError:
        lst.append(value)
        return len(lst)


def _struct_index(d):
    out = {}
    for k in set(k for k, _, _ in d['uidx']) | set(k for k, _, _ in d['lidx']):
        out.setdefault(resolve(d, k), []).append(k)
    return out


def appearance_names_by_crc():
    """SOE CRC -> name for every appearance file the client loads (to label CIDX entries)."""
    from trn_iff import client_index
    return {soe_crc(k): k for k in client_index() if k.startswith('appearance/')}


def splice(stock, other, appearances, report=None):
    """Copy the customization maps of the given appearance files from `other` into `stock`, reusing stock maps whose
    resolved structure is identical, creating new maps (keys, UCMP/ULST/UIDX, LLST/LIDX, NAME/PNOF/VNOF/DEFV/IRNG/
    RTYP entries) where not. Returns the new table dict; `report` collects what was done."""
    d = {k: (bytearray(v) if k == 'names' else list(v)) if k != 'version' else v for k, v in stock.items() if not k.startswith('_')}
    _tables(d); _tables(other)
    report = report if report is not None else {}
    existing_struct = _struct_index(d)
    next_key = max([k for _, k in d['cidx']] + [k for k, _, _ in d['uidx']] + [k for k, _, _ in d['lidx']]) + 1
    created = {}

    def ensure_var(v):
        name, typ, default = v
        vi = _index_of(d['vnof'], _add_name(d, name))
        if typ[0] == 'palette':
            pi = _index_of(d['pnof'], _add_name(d, typ[1]))
            ri = _index_of(d['rtyp'], 0x8000 | pi)
        else:
            ii = _index_of(d['irng'], (typ[1], typ[2]))
            ri = _index_of(d['rtyp'], ii)
        di = _index_of(d['defv'], default)
        return _index_of(d['ucmp'], (vi, ri, di))

    def port(key):
        nonlocal next_key
        r = resolve(other, key)
        if r in existing_struct:
            return existing_struct[r][0]
        if key in created:
            return created[key]
        new = next_key
        next_key += 1
        created[key] = new
        dv = direct_vars(other, key)
        if dv:
            start = len(d['ulst'])
            for v in dv:
                d['ulst'].append(ensure_var(v))
            d['uidx'].append((new, start, len(dv)))
        lk = link_keys(other, key)
        if lk:
            ported = [port(k) for k in lk]
            start = len(d['llst'])
            d['llst'].extend(ported)
            d['lidx'].append((new, start, len(ported)))
        existing_struct.setdefault(r, []).append(new)
        return new

    for app in appearances:
        crc = soe_crc(app)
        if crc in d['_c']:
            report[app] = {'status': 'already in stock', 'key': d['_c'][crc]}
            continue
        if crc not in other['_c']:
            report[app] = {'status': 'not in the other table either'}
            continue
        new_key = port(other['_c'][crc])
        d['cidx'].append((crc, new_key))
        d['_c'][crc] = new_key
        report[app] = {'status': 'spliced', 'key': new_key, 'variables': [v[0] for v in flatten(resolve(other, other['_c'][crc]))]}
    d['uidx'].sort(key=lambda r: r[0])
    d['lidx'].sort(key=lambda r: r[0])
    d['cidx'].sort(key=lambda r: r[0])
    for k in ('_u', '_l', '_c'):
        d.pop(k, None)
    report['_new_keys'] = len(created)
    return d


def verify_splice(stock, other, spliced, appearances):
    """Every stock appearance resolves exactly as before; every spliced appearance resolves as in `other`."""
    _tables(stock); _tables(spliced); _tables(other)
    bad = [crc for crc, k in stock['cidx'] if flatten(resolve(stock, k)) != flatten(resolve(spliced, spliced['_c'][crc]))]
    bad_new = [a for a in appearances if soe_crc(a) in other['_c'] and flatten(resolve(other, other['_c'][soe_crc(a)])) != flatten(resolve(spliced, spliced['_c'][soe_crc(a)]))]
    sorted_ok = [c for c, _ in spliced['cidx']] == sorted(c for c, _ in spliced['cidx']) and [k for k, _, _ in spliced['uidx']] == sorted(k for k, _, _ in spliced['uidx']) and [k for k, _, _ in spliced['lidx']] == sorted(k for k, _, _ in spliced['lidx'])
    limits_ok = max([k for _, k in spliced['cidx']]) < 65536 and len(spliced['ulst']) < 65536 and len(spliced['llst']) < 65536 and len(spliced['ucmp']) < 65536 and len(spliced['vnof']) <= 255 and len(spliced['rtyp']) <= 255 and len(spliced['defv']) <= 255
    return {'stock_appearances_unchanged': not bad, 'changed_stock_appearances': len(bad), 'spliced_appearances_match_source': not bad_new,
            'tables_sorted': sorted_ok, 'index_limits_ok (u16 keys/positions, u8 UCMP fields)': limits_ok}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == 'roundtrip':
        for spec in argv[1:]:
            data = load(spec)
            back = write_acst(read_acst(data))
            print('IDENTICAL' if back == data else 'DIFFERENT', len(data), spec)
        return 0
    if argv[0] == 'diff':
        s, o = read_acst(load(argv[1])), read_acst(load(argv[2]))
        r = diff(s, o, appearance_names_by_crc())
        for k, v in r.items():
            print(k, (v if not isinstance(v, list) else (len(v), v[:12])))
        return 0
    if argv[0] == 'splice':
        s, o = read_acst(load(argv[1])), read_acst(load(argv[2]))
        rep = {}
        n = splice(s, o, argv[4:], rep)
        data = write_acst(n)
        with open(argv[3], 'wb') as f:
            f.write(data)
        print(rep)
        print(verify_splice(read_acst(load(argv[1])), o, read_acst(data), argv[4:]))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
