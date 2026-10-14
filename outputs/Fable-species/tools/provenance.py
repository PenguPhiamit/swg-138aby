"""S1: provenance of the downloaded species packages (source, bytes, sha256, members, licence/readme findings,
contributors, decision), written to ../provenance.json. Read-only: zip members are listed and read in memory as text
or bytes, nothing is extracted or run. Our own code (Fable, 14 Oct 2026).

    python -I provenance.py
"""
import collections
import hashlib
import json
import os
import struct
import sys
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
from trn_iff import CLIENT, list_tre  # noqa: E402

CAT = os.path.join(OUTPUTS, 'Content-catalogue')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def tre_index_from_bytes(data):
    magic, ver, count, info_off, info_comp, info_csize, name_comp, name_csize, name_usize = struct.unpack_from('<4s4s7I', data, 0)
    info = data[info_off:info_off + info_csize]
    info = zlib.decompress(info) if info_comp == 2 else info
    names = data[info_off + info_csize:info_off + info_csize + name_csize]
    names = zlib.decompress(names) if name_comp == 2 else names
    out = []
    for i in range(count):
        crc, size, off, comp, csize, noff = struct.unpack_from('<IIIIII', info, i * 24)
        end = names.index(b'\0', noff)
        out.append((names[noff:end].decode('latin-1'), size))
    return magic.decode() + ver.decode(), out


def zip_record(path):
    zf = zipfile.ZipFile(path)
    members = zf.infolist()
    ext = collections.Counter((m.filename.rsplit('.', 1)[-1].lower() if '.' in m.filename.split('/')[-1] else 'dir') for m in members)
    docs = [m.filename for m in members if m.filename.lower().split('/')[-1].startswith(('readme', 'license', 'licence', 'copying', 'credits', 'notes'))]
    rec = {'bytes': os.path.getsize(path), 'sha256': sha(path), 'members': len(members), 'by_extension': dict(ext), 'readme_or_licence_members': docs}
    heads = {}
    for m in members:
        if m.filename.endswith(('.lua', '.cpp', '.h')):
            t = zf.read(m.filename).decode('utf-8', 'replace')
            first = ' '.join(l.strip() for l in t.splitlines()[:3])
            heads[first[:90]] = heads.get(first[:90], 0) + 1
    rec['source_file_headers'] = heads
    return zf, rec


def main():
    p = {'generated': '2026-10-14', 'rule': 'packages read as text or bytes in memory; nothing extracted to disk, nothing run', 'packages': {}}
    # 1. the original public species package
    path = os.path.join(CAT, 'newspecies-original.zip')
    zf, rec = zip_record(path)
    tre = zf.read('species.tre')
    ver, entries = tre_index_from_bytes(tre)
    rec.update({
        'what': 'Halyn (with Phoenix) "New species for SWGEmu" (Core3 beta 0.5 era, 2016): 48 Core3 source files under species/ (3 C++, 45 Lua) and species.tre (117 client files)',
        'source': ['https://modthegalaxy.com/index.php?resources/new-species-for-swgemu.36/', 'https://modthegalaxy.com/index.php?threads/new-species-for-swgemu-core3-beta-0-5.629/'],
        'version': 'beta 0.5 (the MTG thread title); no version file inside the zip',
        'contributors': ['Halyn (author)', 'Phoenix (per the catalogue)', 'SWGEmu Core3 (the server files are Core3 files with their LGPL file headers; Core3 itself is AGPL-3.0)'],
        'licence_findings': ['no readme or licence file in the zip', 'every Lua/C++ member carries the SWGEmu Core3 file header (LGPL text, "See file COPYING")',
                             'catalogue status P (Published for server use); the resource page asks permission for uses outside the species-mod purpose (Content-catalogue research)'],
        'species_tre': {'version': ver, 'entries': len(entries), 'sha256': hashlib.sha256(tre).hexdigest(), 'bytes': len(tre),
                        'by_top_dir': dict(collections.Counter(n.split('/')[0] for n, _ in entries)),
                        'species_with_custom_art': {'gotal': sum(1 for n, _ in entries if 'gotal' in n), 'nautolan': sum(1 for n, _ in entries if 'nautolan' in n)},
                        'player_templates': sorted(n.split('/')[-1] for n, _ in entries if n.startswith('object/creature/player/'))},
        'cpp_members': {n: hashlib.sha256(zf.read(n)).hexdigest() for n in zf.namelist() if n.endswith(('.cpp', '.h'))},
        'species_added': ['aqualish (m/f)', 'bith (m/f)', 'chiss (m/f)', 'devaronian (m)', 'gotal (m)', 'gran (m)', 'hutt (m/f)', 'ishi_tib (m)', 'nautolan (m)', 'nightsister (f)',
                          'nikto (m)', 'quarren (m)', 'smc (f)', 'talz (m)', 'togruta (f)', 'weequay (m)'],
        'defects_seen': ['racial_mods.iff lists aqualish and bith twice', 'TemplateSpecies gives aqualish/bith/gotal/talz the species id 0 (human)',
                         'no skills.iff rows for species_<new> (only skl_n/skl_d names, and none for hutt)', 'player_species.stf descriptions are Wookieepedia text (CC BY-SA)',
                         'default_pc_hairstyles names hair_human_female_s33, which the client and Core3-dev lack', 'its client tables are 2016 copies of older stock patches (column types differ from today\'s)'],
        'decision': {'client art gotal/nautolan (MTG patch 023 carries it)': 'usable with credit (Halyn/Phoenix; MTG as host)',
                     '20 player client templates (MTG patch 023)': 'usable; already in the merged CRC table',
                     'rows of the creation/customization tables': 'usable as data, re-emitted on today\'s stock schema',
                     'player_species.stf descriptions': 'excluded (CC BY-SA text); names usable; we write our own descriptions',
                     'server Lua': 'reference; re-written in Core3-dev\'s shape (s3/)',
                     'C++ (Races.h, PlayerCreationManager.cpp, ImageDesignManager.cpp)': 'reference only; 2016 Core3, dev differs; the Races.h array pattern is the model',
                     'misc/object_template_crc_string_table.iff in species.tre': 'excluded; the merged table in local_planets.tre already holds the entries'}})
    p['packages']['newspecies-original.zip'] = rec
    # 2. the two "zeltros" zips: a planet, not the Zeltron species
    for name, what in (('zeltros_client.zip', 'Zeltros planet (tienvogh): terrain, snapshot, buildings, regions; CC-BY-NC per the catalogue'),
                       ('zeltros_server.zip', 'Zeltros planet server Lua (buildings, flora, furniture)')):
        zf2, rec2 = zip_record(os.path.join(CAT, name))
        rec2.update({'what': what, 'source': ['https://modthegalaxy.com/index.php?resources/zeltros-planet.135/'],
                     'decision': 'excluded from the species track: this is the Zeltros PLANET package, not a Zeltron species package (none was downloaded); catalogue planet-018, status C'})
        p['packages'][name] = rec2
    # 3. EiF references (F51)
    eif = os.path.join(CAT, 'EiF-Uprising')
    zf3, rec3 = zip_record(os.path.join(eif, 'EiF-2017-species-source-reference.zip'))
    rec3.update({'what': 'Empire in Flames 2017 public source snapshot, species Lua and licence texts only (reference)',
                 'zeltron_members': [n for n in zf3.namelist() if 'zeltron' in n.lower()],
                 'decision': 'held: source reference only; EiF client art (starsider01) terms unresolved (feature F51); no import'})
    p['packages']['EiF-2017-species-source-reference.zip'] = rec3
    tre_path = os.path.join(eif, 'EiF-starsider01-reference.tre')
    if os.path.exists(tre_path):
        ents = list_tre(tre_path)
        p['packages']['EiF-starsider01-reference.tre'] = {'bytes': os.path.getsize(tre_path), 'sha256': sha(tre_path), 'entries': len(ents),
                                                           'zeltron_entries': sorted(k for k in ents if 'zeltron' in k),
                                                           'decision': 'held: EiF client art, rights not established (F51); read as reference only'}
    # 4. MTG patch 023 in the owner's client (host of the package's client files)
    mtg = os.path.join(CLIENT, 'mtg_patch_023.tre')
    if os.path.exists(mtg):
        ents = list_tre(mtg)
        pkg_names = set(n.lower() for n, _ in entries)
        p['packages']['mtg_patch_023.tre (owner client)'] = {'bytes': os.path.getsize(mtg), 'sha256': sha(mtg), 'entries': len(ents),
                                                              'package_files_it_carries': sum(1 for n in pkg_names if n in ents),
                                                              'decision': 'usable in place (MTG, catalogue status P with credit); it is how the client already has the species files'}
    with open(os.path.join(ROOT, 'provenance.json'), 'w', encoding='utf-8') as f:
        json.dump(p, f, indent=1)
    for k, v in p['packages'].items():
        print(k, v.get('sha256', '')[:16], v.get('members', v.get('entries')), 'members/entries;', str(v.get('decision'))[:90])
    return 0


if __name__ == '__main__':
    sys.exit(main())
