"""Vehicle fix (17 Oct, run 29: "light bendning barc has no model i can see its name so its there").

A vehicle's visible body is its saddle appearance (logical_saddle_name_map -> saddle_appearance_map); the
pv_*.sat named by the object template is an 8-vertex dummy. Every shader of the Light Bending BARC's body
(lb_barc_combined_*_2d10.sht) uses effect\\2d_distort.eft, MTG's screen-distortion "cloak" effect, which no other
vehicle uses and which draws nothing visible in this pre-CU client. This points the Light Bending BARC's
logical saddle at the regular Clone BARC body (lookup/clone_barc_speeder: clone_barc_speeder.apt,
clientdata/vehicle/barc_speeder.iff, rider pose vehicle_barc_speeder), so it draws and rides as a BARC.
Name, deed, PCD and server templates stay as they are. Report: Documentation-support/vehicles-render-17oct.md.

Reads the owner's local files only; never installs. Every other entry stays byte-identical.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

OUTPUTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OUTPUTS / 'tools'))
sys.path.insert(0, str(OUTPUTS / 'Fable-species/s4/tools'))
from swgfmt import tre_write, trn_iff as iff
import species_tables as species

BASE_SHA = 'beb06d28'
LSN = 'datatables/mount/logical_saddle_name_map.iff'
SAM = 'datatables/mount/saddle_appearance_map.iff'
RPM = 'datatables/mount/rider_pose_map.iff'
VSR = 'datatables/mount/valid_scale_range.iff'
REPOINT = {'appearance/light_bending_barc_speeder.sat': ('lookup/barc_speeder_light_bend', 'lookup/clone_barc_speeder')}


def build(entries):
    raw = entries[LSN]
    table = species.st.read_dtii(raw)
    assert species.st.write_dtii(table) == raw
    sam = {r[0]: r for r in species.st.read_dtii(entries[SAM])['rows']}
    poses = {r[0] for r in species.st.read_dtii(entries[RPM])['rows']}
    scales = {r[0] for r in species.st.read_dtii(entries[VSR])['rows']}
    changed = []
    for row in table['rows']:
        if row[0] in REPOINT:
            old, new = REPOINT[row[0]]
            assert row[1] == old, row
            assert new in sam and sam[new][2] in poses and iff.client_file(sam[new][2]), new
            assert row[0] in scales, row[0]
            row[1] = new
            changed.append([row[0], old, new, sam[new][2], sam[new][3]])
    assert len(changed) == len(REPOINT), changed
    out = species.st.write_dtii(table)
    before = species.st.read_dtii(raw)['rows']
    after = species.st.read_dtii(out)['rows']
    assert len(before) == len(after)
    assert sum(1 for a, b in zip(before, after) if a != b) == len(REPOINT)
    result = dict(entries)
    result[LSN] = out
    assert all(result[n] == v for n, v in entries.items() if n != LSN)
    return result, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS.parent / 'work/ossus-cave-mouths/local_planets-cave-mouths.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/vehicle-fixes')
    parser.add_argument('--any-base', action='store_true', help='accept a base other than beb06d28')
    args = parser.parse_args()
    base = args.base.read_bytes()
    base_sha = hashlib.sha256(base).hexdigest()
    assert args.any_base or base_sha.startswith(BASE_SHA), 'base is not beb06d28: ' + base_sha
    entries = tre_write.read(base)[0]
    result, changed = build(entries)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stage = args.out_dir / 'stage' / LSN
    stage.parent.mkdir(parents=True, exist_ok=True)
    stage.write_bytes(result[LSN])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-vehicle-fixes.tre'
    out.write_bytes(archive)
    report = {'base_sha256': base_sha, 'out_sha256': hashlib.sha256(archive).hexdigest(), 'entries': len(result),
              'changed': [LSN], 'repointed': changed, 'installed': False}
    (args.out_dir / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
