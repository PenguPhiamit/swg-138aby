"""stage_s6.stage_s6(stage_dir, base): the client files for Nautolan (male) and Togruta (female), on top of any chain
(Fable species S6, 14 Oct 2026). Our own code; builds on s4/tools/species_tables.stage_species and s4/tools/acst.

1. species_tables.stage_species(['nautolan', 'togruta'], ...) with acst_other = the package's 2016 ACST plus the Togruta map
   (tools/acst_togruta.py): rows, PTMP blocks, the two <Data> blocks, names (ours: descriptions), species skills, and the
   ACST splice of appearance/nautolan_m.sat (from the 2016 table) and appearance/togruta_f.sat (our map).
2. palette_columns.iff: the package's rows for the two skin palettes (npc_skin_nautolan, npc_togruta: 4 columns, 36 of 64
   entries at creation, as the package set them), which stage_species's name filter does not catch (they do not start
   with npc_<species>_), re-emitted on the base schema.
3. default_pc_hairstyles.iff: a NAME-only PTMP block per species, the way stock declares its hairless species (Mon
   Calamari, Wookiee): the package has no hair block for either, both have head-tails, allow_bald is 1.
Every base copy round-trips before it is changed; every output re-reads; the report says what was added and whether the
two appearances resolve to the intended customization variables.
"""
import copy
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
import species_tables  # noqa: E402
import acst  # noqa: E402
import acst_togruta  # noqa: E402
import swg_tables as st  # noqa: E402
from trn_iff import build, parse  # noqa: E402

NEW = ['nautolan', 'togruta']
TEMPLATES = {'nautolan': 'object/creature/player/shared_nautolan_male.iff', 'togruta': 'object/creature/player/shared_togruta_female.iff'}
PALETTES = ['npc_skin_nautolan', 'npc_togruta']
ACST_REL = 'customization/asset_customization_manager.iff'


def ui_block(species):
    """The SpeciesSelection <Data .../> block in the stock shape (attribute order and camera values of the stock blocks)."""
    tpl = TEMPLATES[species]
    lines = ["<Data", "appearancefemale='%s'" % tpl, "appearancemale='%s'" % tpl, "cameraoffsetmaxy='1.6'", "cameraoffsetmaxz='1'", "cameraoffsety='0.9'",
             "cameraoffsetz='5'", "description='@player_species:desc_%s'" % species, "displayname='@player_species:name_%s'" % species,
             "localdescription='[@player_species:desc_%s]'" % species, "localdisplayname='[@player_species:name_%s]'" % species,
             "LocalText='[@player_species:name_%s]'" % species, "Name='%s'" % species, "skill='species_%s'" % species, "Text='@player_species:name_%s'" % species]
    return lines[0] + '\r\n' + ''.join('\t\t\t\t' + l + '\r\n' for l in lines[1:]) + '\t\t\t/>'


def stage_s6(stage_dir, base):
    pkg = species_tables.Package()
    other2, tog_key = acst_togruta.with_togruta(pkg.file(ACST_REL))
    rep = species_tables.stage_species(NEW, stage_dir, base=base, acst_other=other2)
    s6 = {'togruta_map_key_in_other': tog_key}

    def cur(rel):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        return open(path, 'rb').read() if os.path.exists(path) else base(rel)

    def out(rel, data, info):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        info.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        rep['files'][rel] = info

    # 2. palette_columns rows for the two skin palettes
    rel = 'datatables/customization/palette_columns.iff'
    cur_bytes = cur(rel)
    tb = st.read_dtii(cur_bytes)
    assert st.write_dtii(tb) == cur_bytes, rel + ' does not round-trip'
    tp = st.read_dtii(pkg.file(rel))
    assert tp['columns'] == tb['columns'], rel + ' columns differ'
    have = {r[0] for r in tb['rows']}
    added = [list(r) for r in tp['rows'] if r[0] in PALETTES and r[0] not in have]
    if added:
        new = {'version': tb['version'], 'columns': tb['columns'], 'types': tb['types'], 'rows': tb['rows'] + added}
        data = st.write_dtii(new)
        assert st.read_dtii(data)['rows'] == new['rows']
        before = rep['files'].get(rel, {}).get('rows_added', 0)
        out(rel, data, {'rows_before': len(tb['rows']) - before, 'rows_added': before + len(added), 'types_from_base': True, 'palettes': [r[0] for r in added]})
    s6['palette_rows_added'] = [r[0] for r in added]

    # 3. NAME-only hair blocks
    rel = 'creation/default_pc_hairstyles.iff'
    cur_bytes = cur(rel)
    tree = parse(cur_bytes)
    assert build(tree) == cur_bytes, rel + ' does not round-trip'
    ver = tree[0].children[0]
    model = next(c for c in ver.children if len(c.children) == 1 and not c.children[0].is_form and c.children[0].tag == 'NAME'
                 and c.children[0].data.startswith(b'object/creature/player/shared_moncal_male.iff'))
    added_blocks = []
    for s in NEW:
        name = TEMPLATES[s].encode('latin-1')
        if any(name in build([c]) for c in ver.children):
            continue
        node = copy.deepcopy(model)
        node.children[0].data = name + b'\0'
        ver.children.append(node)
        added_blocks.append(s)
    if added_blocks:
        data = build(tree)
        back = parse(data)[0].children[0]
        assert len(back.children) == len(ver.children) and all(TEMPLATES[s].encode('latin-1') in build([back.children[-len(added_blocks) + i]]) for i, s in enumerate(added_blocks))
        out(rel, data, {'blocks_before': len(ver.children) - len(added_blocks), 'blocks_added': len(added_blocks), 'shape': 'NAME-only PTMP, as the stock Mon Calamari / Wookiee blocks'})
    s6['hair_blocks_added'] = added_blocks

    # 4. ui_avatardata.inc: our own <Data> block per species in the full stock shape (the package has none for Togruta and
    #    its Nautolan block lacks displayname/localdisplayname); replaces the package's block when one is there
    rel = 'ui/ui_avatardata.inc'
    text = cur(rel).decode('latin-1')
    i = text.find("Name='SpeciesSelection'")
    j = text.find('</DataSource>', i)
    assert i > 0 and j > i
    replaced, inserted = [], []
    for s in NEW:
        blk = ui_block(s)
        k = text.find("Name='%s'" % s, i, j)
        if k >= 0:
            a = text.rfind('<Data', 0, k)
            b = text.find('/>', k) + 2
            if text[a:b] != blk:
                text = text[:a] + blk + text[b:]
                replaced.append(s)
            j = text.find('</DataSource>', i)
        else:
            line_start = text.rfind('\n', 0, j) + 1
            text = text[:line_start] + '\t\t\t' + blk + '\r\n' + text[line_start:]
            inserted.append(s)
            j = text.find('</DataSource>', i)
    if replaced or inserted:
        prev = rep['files'].get(rel, {})
        out(rel, text.encode('latin-1'), {'blocks_added': prev.get('blocks_added', 0) + len(inserted), 'blocks_rewritten_in_stock_shape': replaced,
                                           'shape': '15 attributes as the stock zabrak block (appearancemale = appearancefemale for a single-gender species, as the package does)'})
    rep['notes'] = [n for n in rep.get('notes', []) if not ('no block' in n and any(s in n for s in inserted))]
    s6['ui_blocks'] = {'inserted': inserted, 'rewritten': replaced}

    # checks on the staged ACST
    acst_bytes = cur(ACST_REL)
    tog = acst_togruta.resolved(acst_bytes)
    naut = acst_togruta.resolved(acst_bytes, 'appearance/nautolan_m.sat')
    naut2016 = acst_togruta.resolved(pkg.file(ACST_REL), 'appearance/nautolan_m.sat')
    s6['togruta_resolves_to_design'] = tog == list(acst_togruta.TOGRUTA_VARS)
    s6['nautolan_resolves_as_2016'] = naut is not None and naut == naut2016
    s6['togruta_variables'] = [v[0] for v in (tog or [])]
    s6['nautolan_variables'] = [v[0] for v in (naut or [])]
    acst_info = rep['files'].get(ACST_REL, {})
    s6['acst_verification'] = acst_info.get('verification')
    # the creation UI lists both
    ui = cur('ui/ui_avatardata.inc').decode('latin-1')
    sel = ui[ui.find("Name='SpeciesSelection'"):ui.find('</DataSource>', ui.find("Name='SpeciesSelection'"))]
    s6['species_in_ui'] = re.findall(r"Name='([a-z_]+)'", sel)
    rep['s6'] = s6
    rep['ok'] = (s6['togruta_resolves_to_design'] and s6['nautolan_resolves_as_2016'] and all(s in s6['species_in_ui'] for s in NEW)
                 and bool(acst_info.get('verification', {}).get('stock_appearances_unchanged')) and not [n for n in rep.get('notes', []) if 'no block' in n])
    return rep


if __name__ == '__main__':
    print(__doc__)
