"""The BARC rider fix, client only (Claude, 15 Oct 2026):

    python -I build_barc_ride_archive.py

With the merged mount tables (1315dbb4) the owner's BARC spawned and showed its Enter radial, but Enter did nothing.
The client's male animation table, appearance/lat/all_m.lat, comes from stock (patch_11_02) and has no rider pose
"vehicle_barc_speeder" (rider_pose_map.iff names it for the BARC). MTG's copy (mtg_patch_022) maps it to
all_b_mnt_ride_barc_speeder.ans, an MTG-only file, plus 184 other new names (mount poses for MTG's vehicles). The female
table all_f.lat is MTG-only and already has it. MTG's all_m.lat holds every stock name except one pistol tumble
animation and three duplicate saddle aliases (one a typo, saddle_body2_narrrow) whose proper names it keeps.

This packs the installed archive unchanged plus MTG's all_m.lat as local_planets-barcride.tre and checks that every
other entry is byte-identical. Core3 does not read .lat files, so the server keeps its copy until the next restart.
The full shadow-audit build (build_mtg_merges_archive.py) should take all_m.lat the same way.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Local-model-ossus-fauna'))
from swgfmt import trn_iff  # noqa: E402
import build_fauna_archive as fauna  # noqa: E402
tre = fauna.names.lore.tre_write

INSTALLED = os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre')
INSTALLED_SHA = '1315dbb4c9f39250bfb7030441483090c2b3bd9c6ef006795bc9ad244c7b74aa'
LAT, LAT_FROM = 'appearance/lat/all_m.lat', 'mtg_patch_022.tre'


def main():
    raw = open(INSTALLED, 'rb').read()
    assert hashlib.sha256(raw).hexdigest() == INSTALLED_SHA, 'the installed archive is not 1315dbb4'
    have = tre.read(raw)[0]
    assert LAT not in have
    lat = trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, LAT_FROM), LAT)
    assert b'vehicle_barc_speeder' in lat and b'all_b_mnt_ride_barc_speeder.ans' in lat
    assert 'appearance/animation/all_b_mnt_ride_barc_speeder.ans' in trn_iff.client_index()
    stage = os.path.join(HERE, 'work', 'barcride')
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    for name, data in list(have.items()) + [(LAT, lat)]:
        path = os.path.join(stage, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
    out = os.path.join(HERE, 'local_planets-barcride.tre')
    data, _ = tre.pack_dir(stage, out)
    ours = tre.read(data)[0]
    other_same = all(ours.get(n) == d for n, d in have.items())
    result = {'built': '2026-10-15', 'archive': os.path.basename(out), 'sha256': hashlib.sha256(data).hexdigest(),
              'bytes': len(data), 'entries': len(ours), 'base': INSTALLED_SHA, 'added': LAT, 'added_from': LAT_FROM,
              'added_sha256': hashlib.sha256(lat).hexdigest(), 'other_entries_identical': other_same,
              'ok': other_same and set(ours) == set(have) | {LAT} and ours[LAT] == lat}
    with open(os.path.join(HERE, 'checks-barcride.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=1)
    print(json.dumps(result, indent=1))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
