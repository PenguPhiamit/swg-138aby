"""Stage the C54 Artisan floater's client schematic and server group table.

Reads the owner's local files only. Never installs or changes a running galaxy.
Default base: the S7 Hutt archive (its review findings remain unresolved).
The complete output archive must later be integrated on BOTH server and client.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

OUTPUTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OUTPUTS / 'Fable-species/s4/tools'))
import species_tables as species
from swgfmt import tre_write, trn_iff as iff

GROUP = 'datatables/crafting/schematic_group.iff'
OLD = 'object/draft_schematic/vehicle/civilian/shared_landspeeder_x34.iff'
SHARED = 'object/draft_schematic/vehicle/civilian/shared_a1_deluxe_floater.iff'
SERVER = SHARED.replace('/shared_', '/')
DEED = 'object/tangible/deed/vehicle_deed/shared_a1_deluxe_floater_deed.iff'
NAMES = 'string/en/pet_deed.stf'


def build(base_entries, fallback):
    def read(name):
        return base_entries[name] if name in base_entries else fallback(name)

    original = read(OLD)
    tree = iff.parse(original)
    assert iff.build(tree) == original, 'X34 client schematic does not round-trip'
    patches = 0
    deed_tree = iff.parse(read(DEED))
    deed_name = next(n.data for _, n in iff.walk(deed_tree)
                     if n.tag == 'XXXX' and n.data.startswith(b'objectName\0'))
    assert deed_name == b'objectName\0\x01\x01pet_deed\0\x01a1_deluxe_floater_deed\0'
    # MTG's deed references a key missing from the resolved pet_deed table.
    # Add our labels while preserving every existing string and its ID.
    name_raw = read(NAMES)
    names = species.st.read_stf(name_raw)
    assert species.st.write_stf(names) == name_raw
    old_names = dict(species.st.stf_items(names))
    wanted_names = {'a1_deluxe_floater_deed': 'A1 Deluxe Floater Deed',
                    'a1_deluxe_floater_schematic': 'A1 Deluxe Floater'}
    for key, value in wanted_names.items():
        if key not in old_names:
            species.st.stf_add(names, key, value)
    names_data = species.st.write_stf(names)
    labels = dict(species.st.stf_items(species.st.read_stf(names_data)))
    assert all(labels[k] == v for k, v in old_names.items())
    assert all(labels[k] for k in wanted_names)
    for _, node in iff.walk(tree):
        if node.tag != 'XXXX':
            continue
        if node.data.startswith(b'craftedSharedTemplate\0'):
            node.data = b'craftedSharedTemplate\0\x01' + DEED.encode() + b'\0'
            patches += 1
        elif node.data.startswith(b'objectName\0'):
            node.data = b'objectName\0\x01\x01pet_deed\0\x01a1_deluxe_floater_schematic\0'
            patches += 1
    assert patches == 2, patches
    schematic = iff.build(tree)
    assert iff.build(iff.parse(schematic)) == schematic
    assert b'shared_landspeeder_x34_deed.iff' not in schematic
    assert DEED.encode() in schematic

    raw = read(GROUP)
    table = species.st.read_dtii(raw)
    assert species.st.write_dtii(table) == raw
    x34 = OLD.replace('/shared_', '/')
    group = next(row[0] for row in table['rows'] if row[1] == x34)
    assert group == 'craftArtisanVehicle', group
    expected = [group, SERVER]
    rows = [row for row in table['rows'] if row[1] == SERVER]
    assert not rows or rows == [expected], rows
    if not rows:
        table['rows'].append(expected)
    group_data = species.st.write_dtii(table)
    assert species.st.read_dtii(group_data)['rows'] == table['rows']
    skills = species.st.read_dtii(read('datatables/skill/skills.iff'))
    master = next(row for row in skills['rows'] if row[0] == 'crafting_artisan_master')
    assert group in master[skills['columns'].index('SCHEMATICS_GRANTED')].split(',')

    result = dict(base_entries)
    result.update({SHARED: schematic, GROUP: group_data, NAMES: names_data})
    # Every other existing entry remains byte-identical, including X34.
    assert all(result[n] == v for n, v in base_entries.items() if n not in (SHARED, GROUP, NAMES))
    assert tre_write.soe_crc(SHARED) != tre_write.soe_crc(OLD)
    return result, {'group': group, 'skill': master[0], 'schematic': SHARED,
                    'shared_crc': hex(tre_write.soe_crc(SHARED)),
                    'x34_shared_crc': hex(tre_write.soe_crc(OLD)),
                    'group_rows': len(table['rows']), 'new_group_rows': int(not rows),
                    'client_display': labels['a1_deluxe_floater_schematic'],
                    'deed_display': labels['a1_deluxe_floater_deed']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=OUTPUTS / 'Fable-species/s7-hutt/local_planets-s7.tre')
    parser.add_argument('--out-dir', type=Path, default=OUTPUTS.parent / 'work/c54-crafting')
    args = parser.parse_args()
    base = args.base.read_bytes()
    entries = tre_write.read(base)[0]
    result, report = build(entries, species.default_base)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stage = args.out_dir / 'stage'
    for name in (SHARED, GROUP, NAMES):
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result[name])
    archive = tre_write.pack(result)
    assert tre_write.read(archive)[0] == result
    out = args.out_dir / 'local_planets-c54.tre'
    out.write_bytes(archive)
    report.update(base_sha256=hashlib.sha256(base).hexdigest(),
                  out_sha256=hashlib.sha256(archive).hexdigest(), entries=len(result),
                  changed=sorted(n for n in entries if result[n] != entries[n]),
                  new=sorted(set(result) - set(entries)),
                  installed=False, species_review_findings_fixed=False)
    (args.out_dir / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
