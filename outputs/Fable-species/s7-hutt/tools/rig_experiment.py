"""Hutt rig experiment (owner, 16 Oct 5:40 PM: "give the Hutt the human bone names and hand points, then I'll test once").

The created Hutt cannot be controlled by the pre-CU client (Documentation-support/hutt-c54.md, last section). Every playable
species uses a body skeleton with the human bone names (all_b.skt or ithorian.skt), both hand points and a face skeleton
attached at "head"; hutt.skt has none of that. This adds, to a copy of the C54 archive, for the test client only:
  1. appearance/skeleton/hutt.skt: every all_b bone the Hutt lacks (names compared case-insensitively, as the client
     does: hum_m.sat attaches its face at "head" while all_b names it "Head"), as zero-length bones under the matching
     Hutt bone, so the mesh and the animations are unchanged; hold_l mirrors hold_r onto the left wrist;
  2. appearance/hutt_m.sat / hutt_f.sat: the human face skeleton (hum_m_face / hum_f_face) attached at "head" with
     hum_m_face.lat, exactly as hum_m.sat and hum_f.sat do.
NPC Hutts use the same files; the extra bones carry no vertices. Not installed by this script.
    C:/Users/Pengw/miniconda3/python.exe -I rig_experiment.py
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import tre_write, trn_iff as iff  # noqa: E402

CLIENT = os.path.join(OUTPUTS, 'SWG-client')
BASE = os.path.join(os.path.dirname(OUTPUTS), 'work', 'c54-crafting', 'local_planets-c54.tre')
OUT = os.path.join(os.path.dirname(OUTPUTS), 'work', 'c54-crafting', 'local_planets-c54-rig.tre')
SKT, SAT_M, SAT_F = 'appearance/skeleton/hutt.skt', 'appearance/hutt_m.sat', 'appearance/hutt_f.sat'

ALL_B = ['root', 'lThigh', 'lShin', 'lAnkle', 'lToe', 'rThigh', 'rShin', 'rAnkle', 'rToe', 'spine1', 'spine2', 'spine3',
         'neck', 'Head', 'lClav', 'lArm', 'lForeArm', 'lUlna', 'lWrist', 'lThumb01', 'lThumb02', 'lIndex01', 'lIndex02',
         'lRing01', 'lRing02', 'hold_l', 'rClav', 'rArm', 'rForeArm', 'rUlna', 'rWrist', 'rThumb01', 'rThumb02',
         'rIndex01', 'rIndex02', 'rRing01', 'rRing02', 'hold_r']


def parent_for(name):
    """The Hutt bones to hang a missing human bone under, best first."""
    low = name.lower()
    if low[1:] in ('thigh', 'shin', 'ankle', 'toe'):
        return ['root']
    if low.startswith('spine') or low == 'neck':
        return ['spine']
    if low == 'hold_l':
        return ['l_wrist']
    side = 'l_' if low[0] == 'l' else 'r_'
    part = low[1:]
    if part == 'clav':
        return [side + 'clavicle']
    if part == 'arm':
        return [side + 'arm']
    if part == 'forearm':
        return [side + 'forearm']
    if part == 'ulna':
        return [side + 'ulna', side + 'forearm']
    return [side + 'wrist']


def edit_sktm(form):
    kids = {c.tag: c for c in form.children}
    n = struct.unpack('<i', kids['INFO'].data)[0]
    names = [x.decode('latin-1') for x in kids['NAME'].data.split(b'\0')[:n]]
    prnt = list(struct.unpack('<%di' % n, kids['PRNT'].data))
    quats = {t: [list(struct.unpack_from('<4f', kids[t].data, 16 * i)) for i in range(n)] for t in ('RPRE', 'RPST', 'BPRO')}
    bptr = [list(struct.unpack_from('<3f', kids['BPTR'].data, 12 * i)) for i in range(n)]
    jror = list(struct.unpack('<%dI' % n, kids['JROR'].data))
    have = {x.lower(): i for i, x in enumerate(names)}
    added = []
    for bone in ALL_B:
        if bone.lower() in have:
            continue
        parent = next(have[p] for p in parent_for(bone) if p in have)
        ident = [1.0, 0.0, 0.0, 0.0]
        q = {t: list(ident) for t in quats}
        t = [0.0, 0.0, 0.0]
        if bone == 'hold_l' and 'hold_r' in have:   # mirror the right hand point across the body's YZ plane
            r = have['hold_r']
            q = {k: [v[r][0], v[r][1], -v[r][2], -v[r][3]] for k, v in quats.items()}
            t = [-bptr[r][0], bptr[r][1], bptr[r][2]]
        names.append(bone)
        prnt.append(parent)
        for k in quats:
            quats[k].append(q[k])
        bptr.append(t)
        jror.append(0)
        have[bone.lower()] = len(names) - 1
        added.append(bone)
    m = len(names)
    kids['INFO'].data = struct.pack('<i', m)
    kids['NAME'].data = b''.join(x.encode('latin-1') + b'\0' for x in names)
    kids['PRNT'].data = struct.pack('<%di' % m, *prnt)
    for k in quats:
        kids[k].data = b''.join(struct.pack('<4f', *v) for v in quats[k])
    kids['BPTR'].data = b''.join(struct.pack('<3f', *v) for v in bptr)
    kids['JROR'].data = struct.pack('<%dI' % m, *jror)
    assert all(p < i for i, p in enumerate(prnt) if i), 'a parent after its child'
    return n, m, added


def edit_skeleton(data):
    root = iff.parse(data)
    report = []
    for _, node in iff.walk(root):
        if node.is_form and node.form == 'SKTM':
            report.append(edit_sktm(node.children[0]))
    return iff.build(root), report


def edit_sat(data, face_skt):
    root = iff.parse(data)
    body = root[0].children[0]
    kids = {c.tag: c for c in body.children}
    assert kids['SKTI'].data == b'appearance/skeleton/hutt.skt\0\0', kids['SKTI'].data
    meshes = kids['INFO'].data[0]
    kids['INFO'].data = bytes([meshes]) + struct.pack('<ii', 2, 1)
    kids['SKTI'].data = b'appearance/skeleton/hutt.skt\0\0' + face_skt + b'\0head\0'
    kids['LATX'].data = (struct.pack('<H', 2) + b'appearance/skeleton/hutt.skt\0appearance/lat/hutt.lat\0'
                         + face_skt + b'\0appearance/lat/hum_m_face.lat\0')
    return iff.build(root)


def client_file(name):
    for tre in ('mtg_patch_002_appearance_02.tre', 'mtg_patch_001_appearance_01.tre'):
        entries = tre_write.read(open(os.path.join(CLIENT, tre), 'rb').read())[0]
        if name in entries:
            return entries[name]
    raise KeyError(name)


def main():
    base = tre_write.read(open(BASE, 'rb').read())[0]
    for name in (SKT, SAT_M, SAT_F):
        assert name not in base, name + ' already in the base archive'
    skt, report = edit_skeleton(client_file(SKT))
    for before, after, added in report:
        print('LOD: %d -> %d bones, added %s' % (before, after, ','.join(added)))
    out = dict(base)
    out[SKT] = skt
    out[SAT_M] = edit_sat(client_file(SAT_M), b'appearance/skeleton/hum_m_face.skt')
    out[SAT_F] = edit_sat(client_file(SAT_F), b'appearance/skeleton/hum_f_face.skt')
    data = tre_write.pack(out)
    assert tre_write.read(data)[0] == out
    for name in (SKT, SAT_M, SAT_F):
        assert iff.build(iff.parse(out[name])) == out[name]
    open(OUT, 'wb').write(data)
    print(OUT, len(out), 'entries', hashlib.sha256(data).hexdigest()[:8])


if __name__ == '__main__':
    main()
