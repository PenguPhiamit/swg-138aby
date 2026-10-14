"""species_tables.stage_species(species, stage_dir, base=None): write every client file a playable species needs,
built from the current stock copies with exact round trips, from the Halyn/Phoenix species package's rows and
blocks (read in memory from Content-catalogue/newspecies-original.zip; never extracted or run) and our own text.
Our own code (Fable, 14 Oct 2026). For Claude's archive builder (hoth_client_build.py).

    from species_tables import stage_species
    report = stage_species(['chiss'], 'stage_dir')            # base = the stock copies in the owner's client
    report = stage_species(['chiss'], 'stage_dir', base=fn)   # base(name) -> bytes of your current (merged) copy

Files written under stage_dir (only those that changed): ui/ui_avatardata.inc, string/en/player_species.stf,
datatables/creation/racial_mods.iff, datatables/creation/attribute_limits.iff, datatables/customization/
{customization_data,customization_group_instance,hair_assets_skill_mods,palette_columns,allow_bald}.iff,
creation/default_pc_hairstyles.iff, creation/default_pc_equipment.iff, creation/profession_defaults_*.iff,
datatables/skill/skills.iff, string/en/skl_n.stf, string/en/skl_d.stf, customization/asset_customization_manager.iff
(only when a species' appearance is missing from the base table). Every base copy must round-trip through the writer
before it is changed (assert), every output re-reads, and the report says what was added.
"""
import hashlib
import json
import os
import re
import struct
import sys
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'tools'))
import acst  # noqa: E402
import swg_tables as st  # noqa: E402
from trn_iff import build, client_file, parse  # noqa: E402

PACKAGE = os.path.join(OUTPUTS, 'Content-catalogue', 'newspecies-original.zip')
IFF_RE = re.compile(rb'[A-Za-z0-9_/\.]+\.iff')

# appearance files per species (from the package's player templates), display names, and our own descriptions
SPECIES = {
    'aqualish': {'genders': ('male', 'female'), 'name': 'Aqualish', 'sat': ['appearance/aqualish_m_01.sat', 'appearance/aqualish_f_01.sat']},
    'bith': {'genders': ('male', 'female'), 'name': 'Bith', 'sat': ['appearance/bith_m.sat', 'appearance/bith_f.sat']},
    'chiss': {'genders': ('male', 'female'), 'name': 'Chiss', 'sat': ['appearance/chiss_m.sat', 'appearance/chiss_f.sat']},
    'devaronian': {'genders': ('male',), 'name': 'Devaronian', 'sat': ['appearance/devaronian_m.sat']},
    'gotal': {'genders': ('male',), 'name': 'Gotal', 'sat': ['appearance/gotal_m.sat']},
    'gran': {'genders': ('male',), 'name': 'Gran', 'sat': ['appearance/gran_m.sat']},
    'hutt': {'genders': ('male', 'female'), 'name': 'Hutt', 'sat': ['appearance/hutt_m.sat', 'appearance/hutt_f.sat']},
    'ishi_tib': {'genders': ('male',), 'name': 'Ishi Tib', 'sat': ['appearance/ishi_tib_m.sat']},
    'nautolan': {'genders': ('male',), 'name': 'Nautolan', 'sat': ['appearance/nautolan_m.sat']},
    'nightsister': {'genders': ('female',), 'name': 'Nightsister', 'sat': ['appearance/nightsister_f.sat']},
    'nikto': {'genders': ('male',), 'name': 'Nikto', 'sat': ['appearance/nikto_m.sat']},
    'quarren': {'genders': ('male',), 'name': 'Quarren', 'sat': ['appearance/quarren_m.sat']},
    'smc': {'genders': ('female',), 'name': 'Singing Mountain Clan Witch', 'sat': ['appearance/sing_mt_clan_f.sat']},
    'talz': {'genders': ('male',), 'name': 'Talz', 'sat': ['appearance/talz_m.sat']},
    'togruta': {'genders': ('female',), 'name': 'Togruta', 'sat': ['appearance/togruta_f.sat']},
    'weequay': {'genders': ('male',), 'name': 'Weequay', 'sat': ['appearance/weequay_m.sat']},
}
# our own in-game descriptions (story-neutral, one or two sentences; the package's are Wookieepedia text and are not used)
DESCRIPTIONS = {
    'aqualish': 'A tusked, hard-headed people from Ando, quick to anger and quicker to take work on the fringes of the galaxy.',
    'bith': 'A large-eyed, domed-headed people from Clak\'dor VII, famed for their ear for music and their patience with intricate work.',
    'chiss': 'A near-human people of the Unknown Regions, blue-skinned and red-eyed, disciplined and reserved; few are seen this far into the galaxy.',
    'devaronian': 'A horned, restless people from Devaron; the males are wanderers by nature and turn up wherever ships land.',
    'gotal': 'A people of Antar 4 whose head cones sense the moods and energies around them; they make patient hunters and trackers.',
    'gran': 'A three-eyed, peaceable people from Kinyen, used to living close together and uneasy on their own.',
    'hutt': 'The slug-like clan lords of Nal Hutta, long-lived and heavy, who treat every bargain as a contest they mean to win.',
    'ishi_tib': 'A green, beaked people from Tibrin, tidy planners who keep their gills wet and their accounts straight.',
    'nautolan': 'An amphibious people from Glee Anselm with head-tails that taste the air; calm in water and hard to rattle on land.',
    'nightsister': 'A witch of the Dathomir covens who turned from the clan ways, feared for the spells she can bring to bear.',
    'nikto': 'A hardy, scaled people long bound to Hutt service, found wherever the Hutts need muscle.',
    'quarren': 'A tentacle-faced people from the depths of Mon Cala, practical and blunt, and never far from a deal.',
    'smc': 'A witch of Dathomir\'s Singing Mountain Clan, trained in the clan\'s spells and sworn to its laws.',
    'talz': 'A tall, white-furred people from Alzoc III, strong and gentle until pushed, and never truly warm away from the snow.',
    'togruta': 'A people of Shili with montrals and head-tails that sense the space around them; hunters who prefer company to solitude.',
    'weequay': 'A leather-skinned people from Sriluur, close-mouthed outside their own clans and often found as guards and mercenaries.',
}
ATTRS = ['health', 'strength', 'constitution', 'action', 'quickness', 'stamina', 'mind', 'focus', 'willpower']
CUSTOMIZATION_TABLES = ['datatables/customization/customization_data.iff', 'datatables/customization/customization_group_instance.iff',
                        'datatables/customization/hair_assets_skill_mods.iff', 'datatables/customization/palette_columns.iff',
                        'datatables/customization/allow_bald.iff']
PTMP_TABLES = ['creation/default_pc_hairstyles.iff', 'creation/default_pc_equipment.iff'] + \
    ['creation/profession_defaults_%s.iff' % p for p in ('combat_brawler', 'combat_marksman', 'crafting_artisan', 'jedi', 'outdoors_scout', 'science_medic', 'social_entertainer')]


# ---------------------------------------------------------------- the package, read in memory

class Package:
    def __init__(self, path=PACKAGE):
        self.zf = zipfile.ZipFile(path)
        data = self.zf.read('species.tre')
        magic, ver, count, info_off, info_comp, info_csize, name_comp, name_csize, name_usize = struct.unpack_from('<4s4s7I', data, 0)
        info = data[info_off:info_off + info_csize]
        info = zlib.decompress(info) if info_comp == 2 else info
        names = data[info_off + info_csize:info_off + info_csize + name_csize]
        names = zlib.decompress(names) if name_comp == 2 else names
        self.entries = {}
        for i in range(count):
            crc, size, off, comp, csize, noff = struct.unpack_from('<IIIIII', info, i * 24)
            end = names.index(b'\0', noff)
            self.entries[names[noff:end].decode('latin-1')] = (off, size, comp, csize)
        self.data = data

    def file(self, name):
        off, size, comp, csize = self.entries[name]
        blob = self.data[off:off + (csize if comp else size)]
        return zlib.decompress(blob) if comp == 2 else blob


def _mentions(cell, species):
    """A string cell that names the species (template names, species_gender, npc_<species>_ palettes)."""
    if not isinstance(cell, str):
        return False
    c = cell.lower()
    return bool(re.search(r'(^|[/_])%s_(male|female)\b' % re.escape(species), c) or re.search(r'shared_%s_(male|female)\.iff' % re.escape(species), c)
                or c.startswith('npc_%s_' % species))


def default_base(name):
    return client_file(name)


def stage_species(species, stage_dir, base=None, package_path=PACKAGE, acst_other=None):
    base = base or default_base
    pkg = Package(package_path)
    species = [s.lower() for s in species]
    for s in species:
        if s not in SPECIES:
            raise ValueError('unknown species ' + s)
    report = {'species': species, 'files': {}, 'notes': []}

    def out(rel, data, info):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        info.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        report['files'][rel] = info

    # 1. DTII tables: rows naming the species, re-emitted on the base schema
    for rel in ['datatables/creation/racial_mods.iff', 'datatables/creation/attribute_limits.iff'] + CUSTOMIZATION_TABLES:
        base_bytes = base(rel)
        tb = st.read_dtii(base_bytes)
        assert st.write_dtii(tb) == base_bytes, 'base does not round-trip: ' + rel
        tp = st.read_dtii(pkg.file(rel))
        assert tp['columns'] == tb['columns'], rel + ' columns differ'
        have = set(tuple(r) for r in tb['rows'])
        added, seen = [], set()
        for r in tp['rows']:
            if any(_mentions(c, s) for c in r for s in species) and tuple(r) not in have and tuple(r) not in seen:
                added.append(list(r))
                seen.add(tuple(r))
        if rel.endswith('hair_assets_skill_mods.iff'):
            # drop hair the client lacks (the package names hair_human_female_s33, which stock never shipped)
            from trn_iff import client_index
            idx = client_index()
            kept = [r for r in added if r[0].lower() in idx]
            dropped = len(added) - len(kept)
            added = kept
            if dropped:
                report['notes'].append('%s: dropped %d row(s) whose hair object the client lacks' % (rel, dropped))
        if not added:
            report['files'][rel] = {'unchanged': True, 'rows_added': 0}
            continue
        new = {'version': tb['version'], 'columns': tb['columns'], 'types': tb['types'], 'rows': tb['rows'] + added}
        data = st.write_dtii(new)
        assert st.read_dtii(data)['rows'] == new['rows']
        out(rel, data, {'rows_before': len(tb['rows']), 'rows_added': len(added), 'types_from_base': True})

    # 2. PTMP tables: append the species' PTMP forms from the package to the base form's children
    for rel in PTMP_TABLES:
        base_bytes = base(rel)
        tree = parse(base_bytes)
        assert build(tree) == base_bytes, 'base does not round-trip: ' + rel
        ver = tree[0].children[0]
        present = set(m.group(0) for c in ver.children for m in IFF_RE.finditer(build([c])) if b'object/creature/player/' in m.group(0))
        pk = parse(pkg.file(rel))[0].children[0]
        added = []
        wanted = re.compile(rb'shared_(' + b'|'.join(re.escape(s).encode() for s in species) + rb')_(male|female)\.iff')
        for c in pk.children:
            raw = build([c])
            names = set(m.group(0) for m in IFF_RE.finditer(raw) if b'object/creature/player/' in m.group(0))
            if any(wanted.search(n) for n in names) and not (names & present):
                if rel.endswith('default_pc_hairstyles.iff'):
                    c = _drop_missing_hair(c, report, rel)
                added.append(c)
        if not added:
            report['files'][rel] = {'unchanged': True, 'blocks_added': 0}
            continue
        ver.children.extend(added)
        data = build(tree)
        assert len(parse(data)[0].children[0].children) == len(ver.children)
        out(rel, data, {'blocks_before': len(ver.children) - len(added), 'blocks_added': len(added)})

    # 3. ui_avatardata.inc: the species' <Data .../> blocks before </DataSource> of SpeciesSelection
    rel = 'ui/ui_avatardata.inc'
    base_text = base(rel).decode('latin-1')
    pk_text = pkg.file(rel).decode('latin-1')
    i = base_text.find("Name='SpeciesSelection'")
    j = base_text.find('</DataSource>', i)
    line_start = base_text.rfind('\n', 0, j) + 1
    blocks = []
    for s in species:
        if "Name='%s'" % s in base_text:
            continue
        k = pk_text.find("Name='%s'" % s)
        if k < 0:
            report['notes'].append('ui_avatardata.inc: the package has no block for ' + s)
            continue
        a = pk_text.rfind('<Data', 0, k)
        b = pk_text.find('/>', k) + 2
        block = pk_text[a:b].replace('\r\n', '\n').replace('\n', '\r\n')
        blocks.append('\t\t\t' + block + '\r\n')
    if blocks:
        new_text = base_text[:line_start] + ''.join(blocks) + base_text[line_start:]
        out(rel, new_text.encode('latin-1'), {'blocks_added': len(blocks)})
    else:
        report['files'][rel] = {'unchanged': True, 'blocks_added': 0}

    # 4. strings: player_species.stf (name from the package, description ours), skl_n/skl_d for the species skill
    rel = 'string/en/player_species.stf'
    base_bytes = base(rel)
    sf = st.read_stf(base_bytes)
    assert st.write_stf(sf) == base_bytes
    keys = dict(st.stf_items(sf))
    pk_keys = dict(st.stf_items(st.read_stf(pkg.file(rel))))
    mods_table = st.read_dtii(pkg.file('datatables/creation/racial_mods.iff'))
    n_added = 0
    for s in species:
        if 'name_' + s not in keys:
            st.stf_add(sf, 'name_' + s, pk_keys.get('name_' + s, SPECIES[s]['name']))
            n_added += 1
        if 'desc_' + s not in keys:
            row = next((r for r in mods_table['rows'] if r[0] == s + '_male' or r[1] == s + '_female'), None)
            mods = row[2:11] if row else [100] * 9
            attr = 'ATTRIBUTES\n\n' + '\n'.join('\\>024%s: \\>128+%d\\>000' % (a.capitalize(), v) for a, v in zip(ATTRS, mods))
            st.stf_add(sf, 'desc_' + s, DESCRIPTIONS[s] + '\r\n\r\n' + attr)
            n_added += 1
    if n_added:
        out(rel, st.write_stf(sf), {'keys_added': n_added})
    else:
        report['files'][rel] = {'unchanged': True, 'keys_added': 0}
    for rel, text in (('string/en/skl_n.stf', '%s Species'), ('string/en/skl_d.stf', 'The innate abilities of the %s.')):
        base_bytes = base(rel)
        sf = st.read_stf(base_bytes)
        assert st.write_stf(sf) == base_bytes
        keys = dict(st.stf_items(sf))
        n_added = 0
        for s in species:
            if 'species_' + s not in keys:
                st.stf_add(sf, 'species_' + s, text % SPECIES[s]['name'])
                n_added += 1
        if n_added:
            out(rel, st.write_stf(sf), {'keys_added': n_added})
        else:
            report['files'][rel] = {'unchanged': True, 'keys_added': 0}

    # 5. skills.iff: species_<s> cloned from species_human (SPECIES_REQUIRED = s)
    rel = 'datatables/skill/skills.iff'
    base_bytes = base(rel)
    tb = st.read_dtii(base_bytes)
    assert st.write_dtii(tb) == base_bytes
    names = set(r[0] for r in tb['rows'])
    human = next(r for r in tb['rows'] if r[0] == 'species_human')
    col = tb['columns'].index('SPECIES_REQUIRED')
    added = []
    for s in species:
        if 'species_' + s not in names:
            row = list(human)
            row[0] = 'species_' + s
            row[col] = s
            added.append(row)
    if added:
        # keep the species rows together: insert after the last species_* row
        last = max(i for i, r in enumerate(tb['rows']) if r[0].startswith('species_'))
        rows = tb['rows'][:last + 1] + added + tb['rows'][last + 1:]
        data = st.write_dtii({'version': tb['version'], 'columns': tb['columns'], 'types': tb['types'], 'rows': rows})
        out(rel, data, {'rows_added': len(added), 'cloned_from': 'species_human'})
    else:
        report['files'][rel] = {'unchanged': True, 'rows_added': 0}

    # 6. asset_customization_manager.iff: splice only the appearances the base lacks
    rel = 'customization/asset_customization_manager.iff'
    base_bytes = base(rel)
    tb = acst.read_acst(base_bytes)
    assert acst.write_acst(tb) == base_bytes
    other = acst.read_acst(acst_other) if acst_other else acst.read_acst(pkg.file(rel))
    wanted = [a for s in species for a in SPECIES[s]['sat']]
    missing = [a for a in wanted if acst.lookup(tb, a) is None]
    if missing:
        rep = {}
        spliced = acst.splice(tb, other, missing, rep)
        data = acst.write_acst(spliced)
        ver = acst.verify_splice(acst.read_acst(base_bytes), other, acst.read_acst(data), missing)
        assert ver['stock_appearances_unchanged'] and ver['spliced_appearances_match_source'] and ver['tables_sorted'], ver
        out(rel, data, {'appearances_spliced': {a: rep[a] for a in missing}, 'verification': ver})
    else:
        report['files'][rel] = {'unchanged': True, 'appearances_already_in_base': wanted}
    report['summary'] = {'files_written': sum(1 for v in report['files'].values() if not v.get('unchanged')),
                         'files_unchanged': sum(1 for v in report['files'].values() if v.get('unchanged'))}
    return report


def _drop_missing_hair(ptmp_node, report, rel):
    """Rebuild a HAIR PTMP form without hair objects the client lacks (ITMS is a run of zero-terminated names)."""
    from trn_iff import Node, client_index  # noqa: F401
    idx = client_index()
    for c in ptmp_node.children:
        if not c.is_form and c.tag == 'ITMS':
            items = [s for s in c.data.split(b'\0') if s]
            kept = [s for s in items if s.decode('latin-1').lower() in idx]
            if len(kept) != len(items):
                report['notes'].append('%s: dropped %d hair(s) the client lacks: %s' % (rel, len(items) - len(kept), [s.decode() for s in items if s not in kept]))
                c.data = b''.join(s + b'\0' for s in kept)
    return ptmp_node


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    rep = stage_species(argv[1:], argv[0])
    print(json.dumps(rep, indent=1)[:4000])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
