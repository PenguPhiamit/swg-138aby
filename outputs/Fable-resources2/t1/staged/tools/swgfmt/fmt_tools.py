"""fmt_tools: the format helpers tools/hoth/hoth_client_build.py used from Bellum Gero's AGPL tools, in our own code
(Fable B3, 14 Oct 2026). Same call shapes and the same bytes out, so the builder's functions do not change:

    stf_tool.read(path) / write(t, path) / add(t, key, text) / as_dict(t)     string tables; t keeps Bellum's shape
                                                                            {'magic', 'flag', 'next', 'vals': {id: (crc, text)}, 'keys': [(id, key)]}
    dt_tool.read(path) / write(t, path)                                      datatables; t = {'version', 'names', 'types', 'rows'}
    cstb_tool.read(path) -> {name: crc} / write(table, path) / add(table, name)
    tre_pack.pack(src_dir, out_path)                                         our TRE writer (tre_write.py)
    read_tre(path) -> [{'name', 'size', 'offset', 'comp', 'comp_size'}], _inflate(blob, comp, size)
    walk_tres(root) / cfg_priorities(root) / extract_entry(tre, entry, out_root)   the archive walk the Hoth scripts use
The byte work is swg_tables, trn_iff and tre_write beside this file (outputs/tools/swgfmt).
"""
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..'))
from . import swg_tables as st  # noqa: E402
from . import trn_iff  # noqa: E402
from . import tre_write  # noqa: E402


def _read(path):
    with open(path, 'rb') as f:
        return f.read()


def _write(path, data):
    with open(path, 'wb') as f:
        f.write(data)


class stf_tool:
    @staticmethod
    def read(path):
        s = st.read_stf(_read(path))
        return {'magic': 0xABCD, 'flag': s['version'], 'next': s['next_id'],
                'vals': {sid: (crc & 0xFFFFFFFF, text) for sid, crc, text in s['texts']}, 'keys': list(s['keys'])}

    @staticmethod
    def write(t, path):
        texts = [(sid, crc - (1 << 32) if crc >= (1 << 31) else crc, text) for sid, (crc, text) in t['vals'].items()]
        _write(path, st.write_stf({'version': t['flag'], 'next_id': t['next'], 'texts': texts, 'keys': list(t['keys'])}))

    @staticmethod
    def add(t, key, text):
        if any(k == key for _, k in t['keys']):
            raise KeyError('exists: ' + key)
        i = max([t['next']] + [j + 1 for j, _ in t['keys']])     # never reuse an id, even with a stale counter
        t['next'] = i + 1
        t['vals'][i] = (0xFFFFFFFF, text)
        t['keys'].append((i, key))

    @staticmethod
    def as_dict(t):
        return {k: t['vals'][i][1] for i, k in t['keys']}


class dt_tool:
    @staticmethod
    def read(path):
        t = st.read_dtii(_read(path))
        return {'version': t['version'], 'names': list(t['columns']), 'types': list(t['types']), 'rows': [list(r) for r in t['rows']]}

    @staticmethod
    def write(t, path):
        _write(path, st.write_dtii({'version': t['version'], 'columns': t['names'], 'types': t['types'], 'rows': t['rows']}))


class cstb_tool:
    @staticmethod
    def read(path):
        c = st.read_cstb(_read(path))
        return {name: crc for crc, name in c['entries']}

    @staticmethod
    def write(table, path):
        _write(path, st.write_cstb([(crc, name) for name, crc in table.items()], '0000'))

    @staticmethod
    def add(table, name):
        table.setdefault(name, st.soe_crc(name.lower()))


class tre_pack:
    @staticmethod
    def pack(src, out, md5_of='stored'):
        data, names = tre_write.pack_dir(src, out, md5_of=md5_of)
        print('packed %d files -> %s (%d bytes)' % (len(names), out, len(data)))


def read_tre(path):
    return [{'name': name, 'size': size, 'offset': offset, 'comp': comp, 'comp_size': comp_size}
            for name, (offset, size, comp, comp_size) in trn_iff.list_tre(path).items()]


def _inflate(blob, comp, uncompressed_size):
    if comp == 0:
        return blob
    if comp == 2:
        return zlib.decompress(blob, bufsize=max(uncompressed_size, 1))
    raise ValueError('unknown compression type %d' % comp)


# ---------------------------------------------------------------- the archive walk the Hoth scripts use (was tre_inventory)

def cfg_priorities(root):
    """{archive basename (lower): NN} from every searchTree_XX_NN=<file> line of every *.cfg in root, whatever the
    section (the client itself reads [SharedFile] only: client_load_order.py does that; this keeps the older scripts'
    contract)."""
    import re
    pri = {}
    try:
        cfgs = [f for f in os.listdir(root) if f.lower().endswith('.cfg')]
    except OSError:
        return pri
    pat = re.compile(r'^\s*searchTree_\d+_(\d+)\s*=\s*(\S+)', re.I)
    for cfg in cfgs:
        with open(os.path.join(root, cfg), encoding='latin-1') as f:
            for line in f:
                m = pat.match(line)
                if m:
                    pri[os.path.basename(m.group(2)).lower()] = int(m.group(1))
    return pri


def walk_tres(root):
    """Every .tre under root, lowest priority first (a later archive wins), archives the cfg does not list or that sit
    in a subfolder first of all, alphabetical within a rank."""
    found = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith('.tre'):
                found.append(os.path.join(dirpath, fn))
    pri = cfg_priorities(root)
    top = os.path.normcase(os.path.abspath(root))

    def rank(p):
        if os.path.normcase(os.path.dirname(os.path.abspath(p))) != top:
            return -1
        return pri.get(os.path.basename(p).lower(), -1)
    return sorted(found, key=lambda p: (rank(p), os.path.basename(p).lower()))


def extract_entry(tre_path, entry, out_root):
    """Write one archive entry under out_root at its internal path; returns the path written."""
    with open(tre_path, 'rb') as f:
        f.seek(entry['offset'])
        blob = f.read(entry['comp_size'] if entry['comp'] else entry['size'])
    data = _inflate(blob, entry['comp'], entry['size'])
    out_path = os.path.join(out_root, *entry['name'].split('/'))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as o:
        o.write(data)
    return out_path
