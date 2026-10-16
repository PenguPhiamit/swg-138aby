"""S7: the Hutt test archive = the INSTALLED local_planets.tre (SWG-client, whatever chain built it) + the playable Hutt.

The owner's client already runs SWG-client/local_planets.tre (4,636,682 B on 16 Oct; no build record names its chain),
so the Hutt goes on top of exactly that archive, and every entry the Hutt does not touch stays byte-identical:
  1. extract the installed archive into work/stage;
  2. species_tables.stage_species(['hutt']) (S4) with a base that reads the installed archive first, then the client;
  3. appearance/lat/hutt.lat from tools/build_hutt_lat.py (Level 1, the animation map; rebuilt if missing);
  4. pack with swgfmt.tre_write; checks: untouched entries identical, the Hutt closure, the lat parses.
    C:/Users/Pengw/miniconda3/python.exe -I build_test_archive.py
Writes local_planets-s7.tre and checks.json beside this file. Nothing is installed; the owner's client is not touched.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(SPECIES)
WORK = os.path.join(HERE, 'work')
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
import species_tables  # noqa: E402

# The owner's archive before any Hutt build (backed up when S7 was first installed, 16 Oct 05:51).
INSTALLED = os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre.bak-20261016')
OUT_TRE = os.path.join(HERE, 'local_planets-s7.tre')
LAT = os.path.join(HERE, 'staged', 'client', 'appearance', 'lat', 'hutt.lat')

# README section 5.2: Health, Strength, Constitution, Action, Quickness, Stamina, Mind, Focus, Willpower (900 points).
RACIAL_MODS = [100, 150, 300, 0, 0, 50, 0, 0, 300]
# Limits as the stock non-human rows derive them: min = 300 + mod; max = min + (700, 200, 100, 700, 150, 100, 700, 200,
# 200); total = the minimums + 1,800 (checked against the Trandoshan and Wookiee rows).
RANGES = [700, 200, 100, 700, 150, 100, 700, 200, 200]
ATTRIBUTE_LIMITS = [v for m, r in zip(RACIAL_MODS, RANGES) for v in (300 + m, 300 + m + r)] + [sum(300 + m for m in RACIAL_MODS) + 1800]
DESCRIPTION = ("Slow to move and quick to count, the Hutts of Nal Hutta have run the Rim's markets for longer than the Republic "
               "has had a Senate. A Hutt is immense, long-lived and hard to kill, resists mind tricks that bend lesser beings, "
               "and treats every conversation as a negotiation already won. Krayt's Empire tolerated the kajidics for their "
               "ships and their silence; its fall left them the richest power still standing. Hutts wear only Hutt-made gear "
               "and travel by repulsor platform.\r\n\r\nATTRIBUTES\n\n" + "\n".join(
                   "\\>024%s: \\>128+%d\\>000" % (n, v) for n, v in zip(
                       ['Health', 'Strength', 'Constitution', 'Action', 'Quickness', 'Stamina', 'Mind', 'Focus', 'Willpower'],
                       RACIAL_MODS)))
SKILL_NAME, SKILL_DESC = 'Hutt Special Features', 'Hutt Abilities'
HUTT_PALETTE = ['npc_species_hutts', 8, 32]  # set_hutt_creation: 32 colours, 8 columns at creation
CREATION_TABLES = ['creation/default_pc_equipment.iff', 'creation/default_pc_hairstyles.iff'] + [
    'creation/profession_defaults_%s.iff' % p for p in (
    'combat_brawler', 'combat_marksman', 'crafting_artisan', 'outdoors_scout', 'science_medic', 'social_entertainer')]
ALLOWED_CHANGES = {'datatables/creation/attribute_limits.iff', 'datatables/creation/racial_mods.iff',
                   'datatables/customization/allow_bald.iff', 'datatables/customization/customization_data.iff',
                   'datatables/customization/customization_group_instance.iff', 'datatables/skill/skills.iff',
                   'string/en/skl_d.stf', 'string/en/skl_n.stf', 'string/en/player_species.stf', 'ui/ui_avatardata.inc',
                   'datatables/customization/palette_columns.iff'} | set(CREATION_TABLES)


def _set_row(stage, rel, values):
    path = os.path.join(stage, rel.replace('/', os.sep))
    table = st.read_dtii(open(path, 'rb').read())
    rows = [r for r in table['rows'] if r[0] == 'hutt_male']
    assert len(rows) == 1, rel
    rows[0][2:] = values
    open(path, 'wb').write(st.write_dtii(table))


def _set_text(stage, rel, key, text):
    path = os.path.join(stage, rel.replace('/', os.sep))
    stf = st.read_stf(open(path, 'rb').read())
    sids = [sid for sid, k in stf['keys'] if k == key]
    if sids:
        stf['texts'] = [(sid, crc, text if sid == sids[0] else old) for sid, crc, old in stf['texts']]
    else:
        st.stf_add(stf, key, text)
    open(path, 'wb').write(st.write_stf(stf))


def set_hutt_facts(stage):
    _set_row(stage, 'datatables/creation/racial_mods.iff', RACIAL_MODS)
    _set_row(stage, 'datatables/creation/attribute_limits.iff', ATTRIBUTE_LIMITS)
    _set_text(stage, 'string/en/player_species.stf', 'desc_hutt', DESCRIPTION)
    _set_text(stage, 'string/en/skl_n.stf', 'species_hutt', SKILL_NAME)
    _set_text(stage, 'string/en/skl_d.stf', 'species_hutt', SKILL_DESC)


# The owner's client crashed creating a Hutt (16 Oct 4:12 PM, integer divide by zero on the customization screen):
# 1. the Hutt skin colour (index_color_1 in shader/hutt_*_hue_*.sht) is palette/npc_species_hutts.pal (32 colours), which
#    had no palette_columns row, so the creation colour grid had 0 columns. The Chiss needed the same (npc_chiss_skin).
# 2. no Hutt block in default_pc_equipment, default_pc_hairstyles or the six profession_defaults, so the client dressed
#    the Hutt in the first block's human-male clothes (pants_s05_m in the crash log) and would offer human hair. Hutts
#    get NAME-only blocks, exactly like the stock Wookiee ones.
def _player(name):
    return b'object/creature/player/shared_%s.iff\x00' % name.encode()


def set_hutt_creation(stage):
    from swgfmt import trn_iff as iff
    path = os.path.join(stage, 'datatables', 'customization', 'palette_columns.iff')
    table = st.read_dtii(open(path, 'rb').read())
    rows = [r for r in table['rows'] if r[0] == HUTT_PALETTE[0]]
    if not rows:
        like = next(r for r in table['rows'] if r[0] == 'npc_chiss_skin')
        table['rows'].append(HUTT_PALETTE + like[3:])
        open(path, 'wb').write(st.write_dtii(table))
    for rel in CREATION_TABLES:
        path = os.path.join(stage, rel.replace('/', os.sep))
        root = iff.parse(open(path, 'rb').read())
        body = root[0].children[0]
        names = [c.children[0].data for c in body.children if c.is_form and c.form == 'PTMP']
        for gender in ('male', 'female'):
            if _player('hutt_' + gender) in names:
                continue
            wookiee = names.index(_player('wookiee_' + gender))
            blocks = [c for c in body.children if c.is_form and c.form == 'PTMP']
            assert len(blocks[wookiee].children) == 1, rel  # the stock Wookiee block is its NAME alone
            at = body.children.index(blocks[wookiee]) + 1
            body.children.insert(at, iff.form('PTMP', iff.chunk('NAME', _player('hutt_' + gender))))
            names = [c.children[0].data for c in body.children if c.is_form and c.form == 'PTMP']
        open(path, 'wb').write(iff.build(root))


def main():
    stage = os.path.join(WORK, 'stage')
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)

    installed_bytes = open(INSTALLED, 'rb').read()
    base_entries = tre_write.read(installed_bytes)[0]
    for name, data in base_entries.items():
        path = os.path.join(stage, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)

    def base(rel):  # the installed archive wins, as it does in the client
        return base_entries[rel] if rel in base_entries else species_tables.default_base(rel)

    report = species_tables.stage_species(['hutt'], stage, base=base)

    # The S7 profile (GPT's C54 F2/F3): the generic stager copies the package's Wookiee-like row and keeps the
    # imported description, so the approved values are set here explicitly.
    set_hutt_facts(stage)
    set_hutt_creation(stage)

    # Always rebuild and check the Level 1 animation table (C54 F6: a cached table was copied unchecked).
    lat_tool = os.path.join(HERE, 'tools', 'build_hutt_lat.py')
    subprocess.run([sys.executable, '-I', lat_tool], check=True, cwd=HERE)
    subprocess.run([sys.executable, '-I', lat_tool, '--check'], check=True, cwd=HERE)
    lat_dst = os.path.join(stage, 'appearance', 'lat', 'hutt.lat')
    os.makedirs(os.path.dirname(lat_dst), exist_ok=True)
    shutil.copyfile(LAT, lat_dst)

    data, names = tre_write.pack_dir(stage, OUT_TRE)
    ours = tre_write.read(data)[0]
    changed = sorted(n for n in base_entries if n in ours and base_entries[n] != ours[n])
    missing = sorted(n for n in base_entries if n not in ours)
    new = sorted(n for n in ours if n not in base_entries)

    checks = {
        'installed': {'path': 'SWG-client/local_planets.tre', 'bytes': len(installed_bytes),
                      'sha256': hashlib.sha256(installed_bytes).hexdigest(), 'entries': len(base_entries)},
        'out': {'path': os.path.relpath(OUT_TRE, OUTPUTS).replace(os.sep, '/'), 'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(), 'entries': len(ours)},
        'untouched_identical': len(base_entries) - len(changed) - len(missing),
        'changed': changed, 'new': new, 'dropped': missing,
        'lat_bytes': len(ours.get('appearance/lat/hutt.lat', b'')),
        'species_report': {'files': sorted(report.get('files', {})), 'notes': report.get('notes', [])},
    }
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps({k: v for k, v in checks.items() if k != 'species_report'}, indent=1)[:1800])
    print('species notes:', report.get('notes', [])[:12])
    assert not missing, 'entries dropped from the installed archive'
    assert set(changed) <= ALLOWED_CHANGES, 'unexpected changes: %s' % sorted(set(changed) - ALLOWED_CHANGES)
    assert set(new) <= {'appearance/lat/hutt.lat'}, 'unexpected new entries: %s' % new
    rm = [r for r in st.read_dtii(ours['datatables/creation/racial_mods.iff'])['rows'] if r[0] == 'hutt_male']
    al = [r for r in st.read_dtii(ours['datatables/creation/attribute_limits.iff'])['rows'] if r[0] == 'hutt_male']
    assert rm == [['hutt_male', 'hutt_female'] + RACIAL_MODS], rm
    assert al == [['hutt_male', 'hutt_female'] + ATTRIBUTE_LIMITS], al
    pc = [r for r in st.read_dtii(ours['datatables/customization/palette_columns.iff'])['rows'] if r[0] == HUTT_PALETTE[0]]
    assert len(pc) == 1 and pc[0][:3] == HUTT_PALETTE, pc
    for rel in CREATION_TABLES:
        for gender in ('male', 'female'):
            assert ours[rel].count(_player('hutt_' + gender)) == 1, (rel, gender)
    print('S7 facts verified in the packed archive: racial mods, limits, the skin palette row, empty clothing blocks; '
          'allowed changes only')
    return 0


if __name__ == '__main__':
    sys.exit(main())
