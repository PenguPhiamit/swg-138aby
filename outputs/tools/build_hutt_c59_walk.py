"""Retime the player Hutt's walk and run (C59, owner's 16 Oct test: "janky while moving ... looks good while prone").

The client plays a locomotion animation faster or slower so that the speed stored in its LOCT chunk matches the
character's real speed (the human walk and run are authored to the player's 1.549 and 5.376 m/s). The stock Hutt
walk and run were made for slow NPCs: LOCT 0.508 and 0.865 m/s, so a player Hutt plays them about 3x and 6x too
fast. Prone works because the crawl (0.381 m/s) meets prone speed (0.25 x 1.549 = 0.387 m/s) at about 1x.

This adds two copies of the stock files whose LOCT keys and average speed are scaled to the player speeds
(appearance/animation/hutt_loc_walk_player.ans, hutt_loc_run_player.ans; the bone channels are untouched) and points
hutt.lat's loop_standing and loop_combat_standing at them. A Hutt has no feet, so playing the cycle at its
authored rate while the body covers more ground does not show as sliding.

Reads the owner's local files only. Never installs or changes a running galaxy.
Default base: the Nal Hutta + floater archive installed on 16 Oct (503401b4...).
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

BASE_SHA = '503401b49a0c'
LAT = 'appearance/lat/hutt.lat'
# stock file -> (new file, player speed in m/s from object/creature/player/base/shared_base_player.iff `speed`)
RETIME = {
    'appearance/animation/hutt_loc_walk.ans': ('appearance/animation/hutt_loc_walk_player.ans', 1.549),
    'appearance/animation/hutt_loc_run.ans': ('appearance/animation/hutt_loc_run_player.ans', 5.376),
}
LOOPS = ('loop_standing', 'loop_combat_standing')   # the sp_* special-attack entries keep the stock run


def loct(data):
    """(tree, LOCT node, average speed, [(frame, x, y, z)]) of a CKAT 0001."""
    tree = iff.parse(data)
    assert iff.build(tree) == data, 'CKAT does not round-trip'
    assert tree[0].form == 'CKAT' and tree[0].children[0].form == '0001'
    node = next(c for c in tree[0].children[0].children if c.tag == 'LOCT')
    avg, n = struct.unpack_from('<fH', node.data)
    assert len(node.data) == 6 + 14 * n
    keys = [struct.unpack_from('<H3f', node.data, 6 + 14 * k) for k in range(n)]
    return tree, node, avg, keys


def retimed(data, speed, rate):
    """The animation with its locomotion speed set so the client plays it at `rate` x at `speed` m/s."""
    tree, node, avg, keys = loct(data)
    k = speed / rate / avg
    node.data = struct.pack('<fH', avg * k, len(keys)) + b''.join(
        struct.pack('<H3f', f, x * k, y * k, z * k) for f, x, y, z in keys)
    out = iff.build(tree)
    assert len(out) == len(data)
    # Only the LOCT chunk differs.
    old, new = iff.parse(data)[0].children[0].children, iff.parse(out)[0].children[0].children
    assert [c.tag for c in old] == [c.tag for c in new]
    assert all(iff.build([a]) == iff.build([b]) for a, b in zip(old, new) if a.tag != 'LOCT')
    _, _, avg2, keys2 = loct(out)
    assert abs(avg2 * rate - speed) < 1e-3
    return out, {'stock_speed': round(avg, 4), 'new_speed': round(avg2, 4), 'scale': round(k, 4),
                 'stock_playback_x': round(speed / avg, 2), 'new_playback_x': round(speed / avg2, 2)}


def relink(lat_data):
    """hutt.lat with each stock locomotion file replaced by its retimed copy in LOOPS only."""
    ash, count, anims, root = lat.read_lat(lat_data)
    swap = {(old + '\0').encode(): (new + '\0').encode() for old, (new, _) in RETIME.items()}
    changed = []
    for a in anims:
        name = lat.anim_name(a)
        if name not in LOOPS:
            continue
        for _, node in iff.walk([a]):
            if node.tag == 'INFO' and node.data in swap:
                node.data = swap[node.data]
                changed.append((name, node.data[:-1].decode()))
    out = iff.build([root])
    ash2, count2, anims2, _ = lat.read_lat(out)
    assert (ash2, count2, len(anims2)) == (ash, count, len(anims))
    names = {old: new for old, (new, _) in RETIME.items()}
    before = {lat.anim_name(a): lat.ans_paths(a) for a in lat.read_lat(lat_data)[2]}
    after = {lat.anim_name(a): lat.ans_paths(a) for a in anims2}
    for name in before:
        want = [names.get(p, p) if name in LOOPS else p for p in before[name]]
        assert after[name] == want, name
    return out, sorted(changed)


def build(entries, stock, run_rate):
    result = dict(entries)
    report = {'files': {}}
    for old, (new, speed) in RETIME.items():
        assert new not in entries and iff.client_file(new) is None   # a new name, nothing overwritten
        rate = run_rate if 'run' in new else 1.0
        data, info = retimed(stock[old], speed, rate)
        result[new] = data
        info.update(stock_file=old, player_speed=speed, sha256=hashlib.sha256(data).hexdigest())
        report['files'][new] = info
    result[LAT], changed = relink(entries[LAT])
    assert len(changed) == 4, changed
    assert all(result[n] == v for n, v in entries.items() if n != LAT)
    report.update(run_rate=run_rate, relinked=changed, lat_sha256=hashlib.sha256(result[LAT]).hexdigest())
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS.parent / 'work/nal-hutta/local_planets-nalhutta-floater.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/c59-hutt-walk')
    parser.add_argument('--run-rate', type=float, default=1.0,
                        help='playback rate of the run cycle at full run speed (1.0 = as authored; 1.5 = livelier)')
    parser.add_argument('--any-base', action='store_true',
                        help='accept a base other than 503401b4 (a later Hutt archive whose hutt.lat still names the stock walk and run)')
    args = parser.parse_args()
    base = args.base.read_bytes()
    base_sha = hashlib.sha256(base).hexdigest()
    assert args.any_base or base_sha.startswith(BASE_SHA), 'base is not the installed Nal Hutta + floater archive: ' + base_sha
    entries = tre_write.read(base)[0]
    stock = {}
    for old in RETIME:
        assert old not in entries      # stock data_animation_00 / patch copies; the archive has none
        stock[old] = iff.client_file(old)
        assert stock[old], old
    result, report = build(entries, stock, args.run_rate)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stage = args.out_dir / 'stage'
    for name in [LAT] + [new for new, _ in RETIME.values()]:
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result[name])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-c59-walk.tre'
    out.write_bytes(archive)
    report.update(base_sha256=base_sha, out_sha256=hashlib.sha256(archive).hexdigest(), entries=len(result),
                  unchanged=sum(result[n] == entries[n] for n in entries),
                  changed=sorted(n for n in entries if result[n] != entries[n]),
                  new=sorted(set(result) - set(entries)), installed=False)
    (args.out_dir / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
