"""Floater v2: take the Hutt's skin weights off `root`, so the whole body sinks with the riding pose.

The owner's 10:35 PM test of v1 (hutt_mnt_ride_floater.ans): "the floater was fixed with just a little bit of
clipping remaining ... spikes of his model poking up when in the cockpit". The client pins the rider's root bone
to the floater's `player` hardpoint, so v1 lowers root's children (belly, tail01, spine) instead of root. Vertices
skinned partly to `root` (197 of 1,350 on LOD 0: chest, neck and chin) stay up while their neighbours sink
0.70 m, and the skin stretches into spikes.

This moves each vertex's `root` share onto the nearest child of root that the mesh names (belly, spine or tail01,
by bind-pose distance), merging it with any weight the vertex already has on that bone. Outside the riding pose those vertices now
follow that child fully instead of partly: belly only bobs up and down (at most 0.15 m, never rotates, in all 127
stock Hutt animations); spine and tail01 sway (README section 6).
The two LOD 0 Hutt meshes (hutt_m_l0.mgn, hutt_f_l0.mgn, stock data_skeletal_mesh_00) are overridden in the
archive; NPC Hutts share them.

Reads the owner's local files only. Never installs or changes a running galaxy.
Default base: 9ce108a0 (v1 floater -> Nal Hutta -> C59 walk), installed on client and server at 10:05 PM.
Every other entry stays byte-identical. Integrate on BOTH server and client.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

OUTPUTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OUTPUTS / 'tools'))
from swgfmt import tre_write, trn_iff as iff
import build_hutt_c54_floater as v1

BASE_SHA = '9ce108a03b02'
# LOD 0 only: LODs 1-3 name no belly or spine (only tail01, which sways), so they keep their weights (README 6).
MESHES = ['appearance/mesh/hutt_%s_l0.mgn' % g for g in 'mf']
SKT = 'appearance/skeleton/hutt.skt'
TARGETS = ('belly', 'spine', 'tail01')


def bind_positions():
    """{bone: model-space bind position} of root and TARGETS, from hutt.skt LOD 0 (their bind rotations are identity)."""
    tree = iff.parse(iff.client_file(SKT))
    sktm = next(n for _, n in iff.walk(tree) if n.form == '0002')
    kids = {c.tag: c.data for c in sktm.children}
    names = [s.decode() for s in kids['NAME'].split(b'\0')[:-1]]
    parent = struct.unpack('<%di' % len(names), kids['PRNT'])
    bones = [names.index(n) for n in ('root',) + TARGETS]
    assert parent[bones[0]] == -1 and all(parent[i] == bones[0] for i in bones[1:])
    for tag in ('RPRE', 'RPST', 'BPRO'):
        rots = struct.unpack('<%df' % (4 * len(names)), kids[tag])
        assert all(rots[4 * i:4 * i + 4] == (1.0, 0.0, 0.0, 0.0) for i in bones), tag + ' not identity'
    bptr = {names[i]: struct.unpack_from('<3f', kids['BPTR'], 12 * i) for i in bones}
    pos = {t: tuple(a + b for a, b in zip(bptr['root'], bptr[t])) for t in TARGETS}
    pos['root'] = bptr['root']
    return pos


def reweight(data, pivots):
    """The mesh with every `root` weight moved to the nearest of TARGETS that the mesh names."""
    tree = iff.parse(data)
    assert iff.build(tree) == data, 'MGN does not round-trip'
    f = tree[0].children[0]
    assert tree[0].form == 'SKMG' and f.form == '0004'
    kids = {c.tag: c for c in f.children if not c.is_form}
    info = list(struct.unpack('<11I', kids['INFO'].data))
    names = [s.decode() for s in kids['XFNM'].data.split(b'\0')[:-1]]
    pos = [struct.unpack_from('<3f', kids['POSN'].data, 12 * i) for i in range(len(kids['POSN'].data) // 12)]
    heads = struct.unpack('<%dI' % len(pos), kids['TWHD'].data)
    raw = kids['TWDT'].data
    assert info[3] == len(names) and info[4] == len(pos) and info[5] == len(raw) // 8 == sum(heads)
    root = names.index('root')
    cands = [(names.index(t), pivots[t]) for t in TARGETS if t in names]
    assert len(cands) == len(TARGETS), 'mesh lacks one of ' + ', '.join(TARGETS)
    new_heads, new_w, moved, o = [], [], {}, 0
    for v, h in enumerate(heads):
        ws = [list(struct.unpack_from('<If', raw, 8 * (o + k))) for k in range(h)]
        o += h
        total = sum(w for _, w in ws)
        r = [w for b, w in ws if b == root]
        if r:
            tgt = min(cands, key=lambda c: sum((a - b) ** 2 for a, b in zip(pos[v], c[1])))[0]
            ws = [e for e in ws if e[0] != root]
            hit = next((e for e in ws if e[0] == tgt), None)
            if hit:
                hit[1] += r[0]
            else:
                ws.append([tgt, r[0]])
            moved[names[tgt]] = moved.get(names[tgt], 0) + 1
            assert abs(sum(w for _, w in ws) - total) < 1e-5
        new_heads.append(len(ws))
        new_w.extend(ws)
    assert o == len(raw) // 8
    kids['TWHD'].data = struct.pack('<%dI' % len(new_heads), *new_heads)
    kids['TWDT'].data = b''.join(struct.pack('<If', b, w) for b, w in new_w)
    info[5] = len(new_w)
    kids['INFO'].data = struct.pack('<11I', *info)
    out = iff.build(tree)
    check = iff.parse(out)[0].children[0]
    twdt = next(c.data for c in check.children if c.tag == 'TWDT')
    assert all(struct.unpack_from('<I', twdt, 8 * i)[0] != root for i in range(len(twdt) // 8))
    # Positions, normals, triangles, shaders and blend targets are untouched.
    same = [c.tag or c.form for c in f.children if c.tag not in ('INFO', 'TWHD', 'TWDT')]
    assert [c.data for c in check.children if c.tag in same and not c.is_form] == \
           [c.data for c in iff.parse(data)[0].children[0].children if c.tag in same and not c.is_form]
    return out, {'root_vertices': sum(moved.values()), 'moved_to': moved, 'weights': [len(raw) // 8, len(new_w)]}


def build(entries):
    # v1 must already be in the base: the riding .ans, and hutt.lat naming it for the six riding entries.
    assert v1.RIDE in entries
    _, _, anims, _ = v1.lat.read_lat(entries[v1.LAT])
    riding = sorted(v1.lat.anim_name(a) for a in anims if v1.RIDE in v1.lat.ans_paths(a))
    assert len(riding) == 6, riding
    pivots = bind_positions()
    result, report = dict(entries), {}
    for name in MESHES:
        assert name not in entries, name + ' already overridden in the base'
        result[name], report[name] = reweight(iff.client_file(name), pivots)
    assert all(result[n] == v for n, v in entries.items())
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS.parent / 'work/c59-walk-on-0e4fe92d/local_planets-c59-walk.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/c54-floater-v2')
    parser.add_argument('--any-base', action='store_true',
                        help='accept a base other than 9ce108a0 (a later archive that still carries floater v1)')
    args = parser.parse_args()
    base = args.base.read_bytes()
    base_sha = hashlib.sha256(base).hexdigest()
    assert args.any_base or base_sha.startswith(BASE_SHA), 'base is not the installed 9ce108a0 archive: ' + base_sha
    entries = tre_write.read(base)[0]
    result, meshes = build(entries)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in MESHES:
        path = args.out_dir / 'stage' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result[name])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-c54-floater-v2.tre'
    out.write_bytes(archive)
    report = {'base_sha256': base_sha, 'out_sha256': hashlib.sha256(archive).hexdigest(), 'entries': len(result),
              'changed': sorted(n for n in entries if result[n] != entries[n]),
              'new': sorted(set(result) - set(entries)), 'meshes': meshes,
              'mesh_sha256': {n: hashlib.sha256(result[n]).hexdigest() for n in MESHES}, 'installed': False}
    (args.out_dir / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('base_sha256', 'out_sha256', 'entries', 'changed', 'new')}, indent=2))
    for n in MESHES:
        print(n, meshes[n])


if __name__ == '__main__':
    main()
