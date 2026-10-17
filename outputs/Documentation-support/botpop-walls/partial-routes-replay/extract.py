# Read-only: carve RecastNavMesh blobs (MSET header + tiles) out of a copy of navareas.db (Berkeley DB btree, overflow pages)
import struct, sys, os, collections
path, outdir = sys.argv[1], sys.argv[2]
f = open(path, 'rb'); data = f.read()
pagesize = struct.unpack_from('<I', data, 20)[0]
print('pagesize', pagesize)
n = len(data) // pagesize
pages = {}
heads = []
for p in range(n):
    off = p * pagesize
    pgno, prev, nxt, entries, hf, level, typ = struct.unpack_from('<IIIHHBB', data, off + 8)
    if typ == 7:
        pages[p] = (prev, nxt, hf)
        if prev == 0: heads.append(p)
print('overflow pages', len(pages), 'chains', len(heads))
os.makedirs(outdir, exist_ok=True)
found = 0
names = collections.Counter()
for h in heads:
    buf = bytearray(); p = h; seen = 0
    while p and p in pages and seen < 1000000:
        prev, nxt, ln = pages[p]
        off = p * pagesize + 32
        buf += data[off:off + ln]; p = nxt; seen += 1
    i = buf.find(b'TESM')
    if i < 0: continue
    # name string just before: Core3 String = u16 length + bytes, then bool(1)
    j = i - 1  # bool
    name = None
    for L in range(3, 120):
        s = j - L
        if s - 2 >= 0 and struct.unpack_from('<H', buf, s - 2)[0] == L:
            name = buf[s:j].decode('latin1'); break
    magic, ver, ntiles = struct.unpack_from('<iii', buf, i)
    names[name] += 1
    fn = os.path.join(outdir, '%s.%d.mset' % (name, names[name]))
    open(fn, 'wb').write(buf[i:])
    found += 1
print('meshes', found)
for k, v in sorted(names.items()): print(k, v)
