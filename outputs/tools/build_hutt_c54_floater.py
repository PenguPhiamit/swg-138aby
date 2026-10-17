"""Stage a lower riding pose for the player Hutt on the A1 Deluxe Floater (16 Oct floater test).

The rider's root bone sits on the floater's `player` hardpoint (y 1.474 m). The Hutt's root is 0.573 m above
its base and its mesh is 1.8 m tall, so the head ends ~2.7 m up, through the canopy (apex 2.34 m).
This adds appearance/animation/hutt_mnt_ride_floater.ans: the Hutt standing idle with the three children of
`root` (belly, tail01, spine) moved down by DROP metres, so the whole body sinks under a root that stays on the
hardpoint. hutt.lat's non-combat riding entries then name it instead of the idle. Only the Hutt changes.

Reads the owner's local files only. Never installs or changes a running galaxy.
Default base: the C54 archive installed on client and server on 16 Oct (6ff21312...).
The output archive must be integrated on BOTH server and client, like C54.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

OUTPUTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OUTPUTS / 'tools'))
sys.path.insert(0, str(OUTPUTS / 'Fable-species/s7-hutt/tools'))
from swgfmt import tre_write, trn_iff as iff
import build_hutt_lat as lat

BASE_SHA = '6ff2131229b3'
IDLE = 'appearance/animation/hutt_idl_stand_breathe.ans'
RIDE = 'appearance/animation/hutt_mnt_ride_floater.ans'
LAT = 'appearance/lat/hutt.lat'
DROP = 0.70                       # metres; README "the change" gives the arithmetic
ROOT_CHILDREN = ('belly', 'tail01', 'spine')   # hutt.skt body LOD: PRNT == 0


def ckat(data):
    """(tree, INFO counts, {bone: (rot flag, rot idx, mask, x, y, z)}, STRN node, [CHNL nodes]) of a CKAT 0001."""
    tree = iff.parse(data)
    assert iff.build(tree) == data, 'CKAT does not round-trip'
    assert tree[0].form == 'CKAT' and tree[0].children[0].form == '0001'
    top = tree[0].children[0].children
    info = struct.unpack('<fHHHHHH', top[0].data)
    xfrm = next(c for c in top if c.form == 'XFRM')
    bones = {}
    for x in xfrm.children:
        i = x.data.index(b'\0')
        bones[x.data[:i].decode()] = struct.unpack_from('<BHBHHH', x.data, i + 1)
    strn = next(c for c in top if c.tag == 'STRN')
    chnl = next(c for c in top if c.form == 'ATRN').children
    assert len(strn.data) == 4 * info[6] and len(chnl) == info[5]
    return tree, info, bones, strn, chnl


def lowered(idle, drop):
    """The idle with every translation of root's children moved down by drop (y only)."""
    tree, info, bones, strn, chnl = ckat(idle)
    static = list(struct.unpack('<%df' % info[6], strn.data))
    # Each bone owns its translation slots; check none of the edited ones is shared.
    used = [(m & bit, idx) for (_, _, m, *xyz) in bones.values() for bit, idx in zip((8, 16, 32), xyz)]
    edited = []
    for name in ROOT_CHILDREN:
        _, _, mask, _, y, _ = bones[name]
        slot = (mask & 16, y)
        assert used.count(slot) == 1, (name, slot)
        if mask & 16:
            node = chnl[y]
            n = struct.unpack_from('<H', node.data)[0]
            keys = [struct.unpack_from('<Hf', node.data, 2 + 6 * k) for k in range(n)]
            node.data = struct.pack('<H', n) + b''.join(struct.pack('<Hf', f, v - drop) for f, v in keys)
            edited.append((name, 'channel', y, n))
        else:
            static[y] -= drop
            edited.append((name, 'static', y, round(static[y], 4)))
    strn.data = struct.pack('<%df' % len(static), *static)
    out = iff.build(tree)
    assert len(out) == len(idle)
    # The new file differs from the idle only in those y values.
    _, info2, bones2, strn2, chnl2 = ckat(out)
    assert info2 == info and bones2 == bones
    return out, edited


def relink(lat_data):
    """hutt.lat with IDLE replaced by RIDE in every non-combat riding entry."""
    ash, count, anims, root = lat.read_lat(lat_data)
    changed = []
    for a in anims:
        name = lat.anim_name(a)
        if not name.endswith('riding') or '_combat_' in name:
            continue
        for _, node in iff.walk([a]):
            if node.tag == 'INFO' and node.data == (IDLE + '\0').encode():
                node.data = (RIDE + '\0').encode()
                changed.append(name)
    out = iff.build([root])
    ash2, count2, anims2, _ = lat.read_lat(out)
    assert (ash2, count2, len(anims2)) == (ash, count, len(anims))
    before = {lat.anim_name(a): lat.ans_paths(a) for a in lat.read_lat(lat_data)[2]}
    after = {lat.anim_name(a): lat.ans_paths(a) for a in anims2}
    for name in before:
        want = [RIDE if (name in changed and p == IDLE) else p for p in before[name]]
        assert after[name] == want, name
    return out, sorted(changed)


def build(entries, idle, drop):
    assert RIDE not in entries and iff.client_file(RIDE) is None   # a new name, nothing overwritten
    ride, edited = lowered(idle, drop)
    lat_data, changed = relink(entries[LAT])
    assert changed == sorted(['loop_riding', 'loop_pistol_riding', 'loop_rifle_riding', 'loop_polearm_riding',
                              'loop_sword_1h_riding', 'loop_sword_2h_riding']), changed
    result = dict(entries)
    result.update({RIDE: ride, LAT: lat_data})
    assert all(result[n] == v for n, v in entries.items() if n != LAT)
    return result, {'drop_m': drop, 'ride_ans': RIDE, 'edited_bones': edited, 'relinked': changed,
                    'ride_sha256': hashlib.sha256(ride).hexdigest(),
                    'lat_sha256': hashlib.sha256(lat_data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS.parent / 'work/c54-crafting/local_planets-c54.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/c54-floater')
    parser.add_argument('--drop', type=float, default=DROP)
    args = parser.parse_args()
    base = args.base.read_bytes()
    base_sha = hashlib.sha256(base).hexdigest()
    assert base_sha.startswith(BASE_SHA), 'base is not the installed C54 archive: ' + base_sha
    entries = tre_write.read(base)[0]
    idle = iff.client_file(IDLE)       # stock data_animation_00; the archive has no copy
    assert IDLE not in entries and idle
    result, report = build(entries, idle, args.drop)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stage = args.out_dir / 'stage'
    for name in (RIDE, LAT):
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result[name])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-c54-floater.tre'
    out.write_bytes(archive)
    report.update(base_sha256=base_sha, out_sha256=hashlib.sha256(archive).hexdigest(), entries=len(result),
                  changed=sorted(n for n in entries if result[n] != entries[n]),
                  new=sorted(set(result) - set(entries)), installed=False)
    (args.out_dir / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
