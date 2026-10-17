"""PL-06: Nal Hutta's own resources, the client and server half (Claude, 17 Oct 2026).

Why Nal Hutta has nothing to survey: resource_manager.lua's activeZones never named hutta (the first look left it out
because no type was restricted to it), so the spawner gave it no galaxy-wide spawn and logged
"backfillZones: hutta is not in activeZones, ignored". Adding it to activeZones (the Lua patch) fixes the minerals,
gas and chemicals, but water, flora, creature and energy resources are planet types: each planet has its own leaves
in resource_tree.iff (water_vapor_rori, meat_herbivore_rori ...), restricted by the "_<planet>" in the name
(ResourceTree::setZoneRestriction). Nal Hutta has none, so this step adds them. Darklight's Nal Hutta was made from
Rori's terrain, so Rori's planet rows are cloned with the planet word swapped, exactly as Ossus cloned Dantooine's
(Fable-ossus/o4/tools/stage_ossus.py merge_resource_tree: every ancestor's Maximum/Minimum # types raised by the
leaves added under it). The server reads the same file from local_planets.tre (it is first in Core3.TreFiles).

    C:/Users/Pengw/miniconda3/python.exe -I build_nal_hutta_life.py
Base: ../work/chain-1017/local_planets-chain-1017.tre (sha256 f0191ab5..., the archive on client and server since
run 25). Writes ../work/nal-hutta-life/local_planets-nalhutta-life.tre, its .sha256, and checks.json beside this file.
Every other entry stays byte-identical (checked). Nothing is installed.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S7 = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(os.path.dirname(S7))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o4', 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
import stage_ossus  # noqa: E402

BASE = os.path.join(H, 'work', 'chain-1017', 'local_planets-chain-1017.tre')
BASE_SHA_PREFIX = 'f0191ab5'
WORK = os.path.join(H, 'work', 'nal-hutta-life')
OUT_TRE = os.path.join(WORK, 'local_planets-nalhutta-life.tre')
TREE = 'datatables/resource/resource_tree.iff'


def merge_tree(data):
    # stage_ossus's merge, pointed at Rori -> Nal Hutta. RES_PLANETS names every planet word a leaf can end in.
    stage_ossus.PLANET = 'hutta'
    stage_ossus.RES_SOURCE = 'rori'
    stage_ossus.RES_ADJ = {'rori': 'Rori', 'hutta': 'Nal Hutta'}
    stage_ossus.RES_PLANETS = stage_ossus.RES_PLANETS + ('ossus', 'hutta')
    return stage_ossus.merge_resource_tree(data)


def main():
    base_bytes = open(BASE, 'rb').read()
    base_sha = hashlib.sha256(base_bytes).hexdigest()
    assert base_sha.startswith(BASE_SHA_PREFIX), 'base is not the f0191ab5 archive: ' + base_sha
    base = tre_write.read(base_bytes)[0]
    old = st.read_dtii(base[TREE])
    assert not any(r[1].endswith('_hutta') for r in old['rows']), 'the tree already has hutta rows'

    files = dict(base)
    files[TREE], info = merge_tree(base[TREE])
    new = st.read_dtii(files[TREE])
    rori = [r[1] for r in old['rows'] if r[1].endswith('_rori')]
    hutta = [r[1] for r in new['rows'] if r[1].endswith('_hutta')]
    names = {r[1]: next(c for c in r[2:10] if c) for r in new['rows'] if r[1].endswith('_hutta')}
    assert sorted(h[:-len('hutta')] for h in hutta) == sorted(r[:-len('rori')] for r in rori), 'not a one-to-one clone'
    assert all('Rori' not in n for n in names.values()), [n for n in names.values() if 'Rori' in n]

    data = tre_write.pack(files)
    os.makedirs(WORK, exist_ok=True)
    with open(OUT_TRE, 'wb') as f:
        f.write(data)
    sha = hashlib.sha256(data).hexdigest()
    with open(OUT_TRE + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (sha, os.path.basename(OUT_TRE)))

    ours = tre_write.read(data)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    dropped = sorted(n for n in base if n not in ours)
    added = sorted(n for n in ours if n not in base)
    others_kept = all(r[1] in {x[1] for x in new['rows']} for r in old['rows'])
    checks = {
        'base': {'path': os.path.relpath(BASE, H).replace(os.sep, '/'), 'bytes': len(base_bytes), 'sha256': base_sha,
                 'entries': len(base)},
        'out': {'path': os.path.relpath(OUT_TRE, H).replace(os.sep, '/'), 'bytes': len(data), 'sha256': sha,
                'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped),
        'changed': changed, 'new': added, 'dropped': dropped,
        'tree': {'rows_before': len(old['rows']), 'rows_after': len(new['rows']), 'rori_leaves': len(rori),
                 'hutta_rows': len(hutta), 'every_old_row_kept': others_kept, 'merge': info,
                 'hutta_names': names},
    }
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped and not added and changed == [TREE], (changed, added, dropped)
    assert others_kept
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed')}, indent=1))
    print('hutta rows:', len(hutta), 'e.g.', list(names.items())[:4])
    print('Nal Hutta resources step: PASS (resource_tree.iff only, every other entry byte-identical)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
