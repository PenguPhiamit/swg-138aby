"""S6 provenance: every file the two species rely on or that we ship, with its source archive, hash, rights basis and
credit, the way S1 recorded the packages (../provenance.json: packages read in memory, nothing extracted or run).
Reads work/closure.json (written by build_test_archive.py) and checks.json; writes ../provenance.json (s6).
    python -I make_provenance.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S6 = os.path.normpath(os.path.join(HERE, '..'))
SPECIES = os.path.dirname(S6)
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
import species_tables as sp  # noqa: E402

PACKAGE_MEMBERS = set(sp.Package().entries)   # the 117 files inside species.tre of newspecies-original.zip

BASES = {
    'ours': {'rights': 'our own output (tables rebuilt from today\'s stock copies with the species rows re-emitted as data; names from the package, descriptions ours)',
             'credit': 'Fable (this project); rows: Halyn/Phoenix species package (data)'},
    'package-in-mtg023': {'rights': 'Halyn (with Phoenix) "New species for SWGEmu" package file, as carried by MTG patch 023 in the owner\'s client. No licence file in the package; '
                                    'the MTG resource page publishes it for server use (catalogue status P) and asks permission for other uses. The package does not say whether its '
                                    'Nautolan mesh/shader/texture files are Halyn\'s own work or converted from SOE NPC art, so authorship is recorded as unstated. NOT shipped by us: the '
                                    'client already loads it from MTG patch 023; our archive only references the paths.',
                          'credit': 'Halyn and Phoenix (New species for SWGEmu, modthegalaxy.com); hosted by Mod the Galaxy patch 023'},
    'mtg': {'rights': 'Mod the Galaxy patch archive in the owner\'s client (MTG\'s compilation of SOE/LucasArts NGE-era client assets for the pre-CU client); the same basis as every '
                      'other MTG file the galaxy already uses (catalogue status P with credit). Not shipped by us; referenced by path.',
            'credit': 'Mod the Galaxy (compilation); Sony Online Entertainment / LucasArts (original assets)'},
    'stock': {'rights': 'stock client asset of the owner\'s own Star Wars Galaxies installation (SOE/LucasArts). Not shipped by us; referenced by path.',
              'credit': 'Sony Online Entertainment / LucasArts'},
    'MISSING': {'rights': 'not found in our archive or the client load order', 'credit': '-'},
}


def classify(path, source):
    if source == 'local_planets-s6.tre':
        return 'ours'
    if source == 'MISSING':
        return 'MISSING'
    if source.startswith('mtg_patch_023') and path in PACKAGE_MEMBERS:
        return 'package-in-mtg023'
    if source.startswith('mtg_'):
        return 'mtg'
    return 'stock'


def main():
    closure = json.load(open(os.path.join(S6, 'work', 'closure.json'), encoding='utf-8'))
    checks = json.load(open(os.path.join(S6, 'checks.json'), encoding='utf-8'))
    files = {}
    for path, v in sorted(closure['files'].items()):
        base = classify(path, v['source'])
        files[path] = {'source': v['source'], 'bytes': v.get('bytes'), 'sha256': v.get('sha256'), 'basis': base,
                       'species': [s for s in ('nautolan', 'togruta', 'chiss') if s in path] or ['shared'],
                       'shipped_by_us': base == 'ours'}
    shipped = sorted(checks['against_c29']['changed_by_s6'] + checks['against_c29']['new_entries'])
    counts = {}
    for v in files.values():
        counts[v['basis']] = counts.get(v['basis'], 0) + 1
    out = {
        'generated': '2026-10-14', 'task': 'S6 Nautolan + Togruta',
        'rule': 'packages and archives read in memory; nothing extracted to disk, nothing run; nothing written outside outputs/Fable-species/s6',
        'summary': {'closure_files': len(files), 'by_basis': counts, 'shipped_entries': shipped,
                    'rights_unclear': [],   # none: every file is ours, a stock asset, an MTG asset, or a package file the client already loads from MTG patch 023 (flagged below)
                    'missing_stock_gap': [p for p, v in files.items() if v['basis'] == 'MISSING'],
                    'flagged_authorship_unstated': [p for p, v in files.items() if v['basis'] == 'package-in-mtg023' and p.split('/')[0] in ('appearance', 'shader', 'texture')]},
        'bases': BASES,
        'data_used_from_the_package': {
            'newspecies-original.zip': {'sha256': '59b48293026dd8f747e9bc31140e5f088c748ce346719fb5bbc268ba94fb6472', 'species.tre sha256': 'b781cff1d78a1fcd3522a96bfb1135909af1c2d170553e43638e9076c4f772fb',
                                        'rows_and_blocks': 'racial_mods, attribute_limits, customization_data, customization_group_instance, allow_bald, palette_columns rows for nautolan_male / togruta_female; '
                                                           'default_pc_equipment and six profession_defaults PTMP blocks; the two ui_avatardata <Data> blocks; name_* strings; '
                                                           'the 2016 asset_customization_manager map of appearance/nautolan_m.sat (spliced); its racial_mods rows as baseHAM for the race Lua',
                                        'not_used': 'desc_* strings (CC BY-SA Wookieepedia text; ours written instead), its C++ and Lua (reference only), its object_template_crc_string_table'},
            'credit_line_for_CREDITS-and-sources.txt': 'Nautolan and Togruta player species: tables and templates from "New species for SWGEmu" by Halyn (with Phoenix), modthegalaxy.com, '
                                                       'as hosted in Mod the Galaxy patch 023; Nautolan art from the same package; Togruta art from MTG patches 015/016/018 and the stock client; '
                                                       'species descriptions, server code and table merging by this project.'},
        'files': files,
    }
    with open(os.path.join(S6, 'provenance.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print('provenance:', len(files), 'files', counts, 'flagged authorship unstated', len(out['summary']['flagged_authorship_unstated']),
          'missing (stock voice gap)', len(out['summary']['missing_stock_gap']), 'rights unclear', out['summary']['rights_unclear'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
