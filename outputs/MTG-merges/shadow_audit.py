"""shadow_audit.py: every file where a stock archive shadows an MTG copy, classified (15 Oct 2026). Read-only.

    python -I shadow_audit.py            # writes shadow-audit.json next to this file (a few minutes, one process per core)

The client and the server load MTG's 23 archives (mtg_*.tre) below the stock ones, so for a file in both the stock copy
wins. For each such file this compares the winning stock copy (the one trn_iff.client_index() picks, which is also the
merge step's base) with the highest-priority MTG copy (client order from swgemu_live.cfg, which the test galaxy's
server list repeats) and classifies it:

  same              byte-identical
  same_content      not byte-identical, but the same rows / keys and texts / CRC entries (order or ids differ)
  mtg_superset      MTG adds rows or keys; every stock row or string is in MTG's copy unchanged (or, if MTG lacks some
                    stock rows, it changes none of the ones it has)
  mtg_subset        MTG only lacks some of stock's rows or keys (nothing to give back)
  mtg_changes       MTG edits stock rows or strings (same key, other values)
  different_format  columns, types or table version differ (or a table that does not parse)
  binary            not a datatable, string file or CRC string table, and not byte-identical

Tables are compared on a key: the fewest leading columns on which the stock rows and MTG's rows are each unique (the
whole row when a table repeats rows). Lower-priority MTG copies are compared too for files with additions, and every
file the existing chain already stages (local_planets-fauna.tre) is compared against that staged copy, because the
merge step builds on it. Each file also gets what Core3 reads it for (server_reads, from the upstream source), a topic,
and a decision: merged (it is in stage_mtg_merges' lists), nothing to merge, skipped, or for Claude with the reason.

shadow-audit.json: counts, decisions, the merge step's lists, a record for every file that is not byte-identical
(files), and the names of the byte-identical ones (same_files).
"""
import collections
import hashlib
import json
import os
import struct
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
for p in (os.path.join(OUTPUTS, 'tools'), os.path.join(OUTPUTS, 'tools', 'hoth')):
    if p not in sys.path:
        sys.path.insert(0, p)
from swgfmt import swg_tables as st, trn_iff  # noqa: E402
import client_load_order as clo  # noqa: E402

CHAIN_TRE = os.path.join(OUTPUTS, 'Local-model-ossus-fauna', 'local_planets-fauna.tre')   # the chain before the MTG merges
OUT_JSON = os.path.join(HERE, 'shadow-audit.json')
SAMPLES = 6

# What Core3 reads from the archives (upstream clone h/work/Core3, branch unstable 403893d9, read 15 Oct 2026; the live
# sandbox branch is built on it). Exact paths found as string literals in MMOCoreORB/src (tests and the client excluded).
SERVER_FILES = {
    'abstract/slot/slot_definition/slot_definitions.iff': 'equipment slots (TemplateManager)',
    'chat/mood_types.iff': 'chat moods (ChatManager)',
    'chat/spatial_chat_types.iff': 'spatial chat types (ChatManager)',
    'creation/default_pc_equipment.iff': 'new-character equipment (PlayerCreationManager)',
    'creation/default_pc_hairstyles.iff': 'new-character hair (PlayerCreationManager)',
    'creation/profession_defaults.iff': 'starting professions (PlayerCreationManager)',
    'customization/asset_customization_manager.iff': 'customization variables (TemplateManager)',
    'customization/customization_id_manager.iff': 'customization ids (TemplateManager)',
    'datatables/badge/badge_map.iff': 'badges (BadgeList)',
    'datatables/chat/social_types.iff': 'socials (ChatManager)',
    'datatables/clientpoi/clientpoi.iff': 'planet points of interest (PlanetManager)',
    'datatables/command/command_tables_shared.iff': 'commands (CommandConfigManager)',
    'datatables/command/command_tables_shared_ground.iff': 'ground commands (CommandConfigManager)',
    'datatables/command/command_tables_shared_space.iff': 'space commands (CommandConfigManager)',
    'datatables/crafting/component.iff': 'crafting components (ComponentMap)',
    'datatables/crafting/schematic_group.iff': 'schematic groups (SchematicMap)',
    'datatables/creation/attribute_limits.iff': 'character creation attribute limits (PlayerCreationManager)',
    'datatables/creation/profession_mods.iff': 'character creation profession mods (PlayerCreationManager)',
    'datatables/creation/racial_mods.iff': 'character creation species mods (PlayerCreationManager)',
    'datatables/creation/starting_locations.iff': 'starting locations (PlayerManager)',
    'datatables/customization/allow_bald.iff': 'bald allowed per species (TemplateManager)',
    'datatables/customization/customization_data.iff': 'Image Designer customizations (ImageDesignManager)',
    'datatables/customization/hair_assets_skill_mods.iff': 'hair styles per Image Designer skill (TemplateManager)',
    'datatables/customization/palette_columns.iff': 'palette columns (TemplateManager)',
    'datatables/faction/rank.iff': 'faction ranks (FactionManager)',
    'datatables/include/state.iff': 'creature states (CreatureState)',
    'datatables/mount/valid_scale_range.iff': 'which creatures a Creature Handler can train as mounts, by appearance and '
                                              'scale (PetManager::isValidMountScale)',
    'datatables/movement/movement_human.iff': 'postures and movement (CreaturePosture, Lua templates)',
    'datatables/performance/perform_effect.iff': 'entertainer effects (PerformanceManager)',
    'datatables/performance/performance.iff': 'entertainer songs and dances (PerformanceManager)',
    'datatables/player/planet_map_cat.iff': 'planet map categories (TemplateManager)',
    'datatables/player/quests.iff': 'quests (PlayerManager)',
    'datatables/resource/resource_tree.iff': 'resource classes (ResourceTree)',
    'datatables/skill/skills.iff': 'skills and professions (SkillManager)',
    'datatables/skill/xp_limits.iff': 'experience caps (SkillManager)',
    'datatables/space/countermeasures.iff': 'ship countermeasures (ShipManager)',
    'datatables/space/hyperspace/hyperspace_locations.iff': 'hyperspace points (ShipManager)',
    'datatables/space/missiles.iff': 'ship missiles (ShipManager)',
    'datatables/space/ship_chassis.iff': 'ship chassis (ShipManager)',
    'datatables/space/ship_components.iff': 'ship components (ShipManager)',
    'datatables/space/ship_turret.iff': 'ship turrets (ShipManager)',
    'datatables/space/ship_weapon_components.iff': 'ship weapons (ShipManager)',
    'datatables/space_command/droid_program_size.iff': 'droid programs (SkillManager)',
    'datatables/travel/travel.iff': 'travel fares (PlanetManager)',
    'datatables/xp/species.iff': 'species experience (PlayerManager)',
    'misc/quest_crc_string_table.iff': 'quest CRCs (PlayerManager)',
    'string/en/mood_types.stf': 'mood names (ChatManager)',
}
SERVER_PREFIXES = {
    'string/en/': 'every string/en file goes into the server strings database (StringIdManager::populateDatabase, run '
                  'only when that database is new, truncated, or reloaded with Core3.TreManager.ReloadStrings / reloadstrings)',
    'datatables/questtask/': 'quest tasks (PlayerManager, datatables/questtask/<quest>.iff)',
    'creation/profession_defaults_': 'per-profession starting items and attributes (PlayerCreationManager, paths listed '
                                     'in creation/profession_defaults.iff)',
    'datatables/space/nebula/': 'nebulas per zone (SpaceManager)',
    'datatables/space/ship_chassis_': 'per-chassis data (ShipChassisData)',
    'object/': 'client object templates, read when a Lua template names them (TemplateManager::addTemplate)',
}
SERVER_EXT = {'.flr': 'floor meshes (TemplateManager::getFloorMesh)', '.pob': 'portal layouts (getPortalLayout)',
              '.ilf': 'interior layouts (getInteriorLayout)', '.sfp': 'structure footprints (loadStructureFootprint)',
              '.apt': 'appearances for collision (getAppearanceTemplate)', '.msh': 'meshes for collision (getAppearanceTemplate)',
              '.cmp': 'component appearances for collision (getAppearanceTemplate)', '.lod': 'LOD appearances for collision (getAppearanceTemplate)',
              '.pal': 'palettes (getPaletteTemplate)', '.trn': 'terrain', '.ws': 'world snapshots'}


def server_reads(name):
    if name in SERVER_FILES:
        return SERVER_FILES[name]
    for p, what in SERVER_PREFIXES.items():
        if name.startswith(p):
            return what
    if name.startswith('abstract/slot/'):
        return 'slot descriptors and arrangements (TemplateManager)'
    return SERVER_EXT.get(os.path.splitext(name)[1])


TOPICS = [   # (substring of the path, topic); first match wins
    ('datatables/mount/', 'mounts'), ('vehicle', 'vehicles'), ('speeder', 'vehicles'), ('mount', 'mounts'),
    ('monster_name', 'creature names'), ('creature_names', 'creature names'), ('npc_name', 'NPC names'),
    ('datatables/buff', 'buffs'), ('buff', 'buffs'), ('datatables/appearance', 'appearance tables'),
    ('datatables/skill', 'skills'), ('skl_', 'skills'), ('datatables/expertise', 'expertise (NGE)'), ('expertise', 'expertise (NGE)'),
    ('datatables/loot', 'loot'), ('loot', 'loot'), ('datatables/crafting', 'crafting'), ('craft', 'crafting'),
    ('datatables/customization', 'customization'), ('customization', 'customization'),
    ('datatables/command', 'commands'), ('cmd_', 'commands'), ('datatables/space', 'space'), ('space', 'space'), ('ship', 'space'),
    ('collection', 'collections (NGE)'), ('quest', 'quests'), ('datatables/item', 'items'), ('obj_n', 'item names'),
    ('obj_d', 'item descriptions'), ('obj_attr', 'item attributes'), ('item', 'items'), ('weapon', 'weapons'),
    ('armor', 'armor'), ('wearable', 'wearables'), ('clothing', 'wearables'), ('hair', 'customization'),
    ('species', 'species'), ('creation', 'character creation'), ('badge', 'badges'), ('travel', 'travel'),
    ('planet', 'planets'), ('terrain', 'terrain'), ('snapshot', 'snapshots'), ('ui/', 'UI'), ('ui_', 'UI'),
    ('music', 'music'), ('performance', 'entertainer'), ('dance', 'entertainer'), ('pet', 'pets'),
    ('faction', 'factions'), ('gcw', 'factions'), ('resource', 'resources'), ('string/en/', 'strings'), ('datatables/', 'datatables'),
]


def topic(name):
    for sub, t in TOPICS:
        if sub in name:
            return t
    return name.split('/')[0]


# Additive files the merge step leaves out, and why (decided 15 Oct 2026 from the rows themselves; see shadow-audit.md)
SKIP_REASONS = {
    'datatables/clientpoi/clientpoi.iff': 'for Claude: server reads it (PlanetManager POIs); MTG adds its own Hoth POIs '
                                          '(hothechobase, hothstarport ...) beside ours, plus Mandalore and Taanab',
    'datatables/creation/attribute_limits.iff': 'for Claude: server reads it (character creation); MTG adds 16 species, '
                                                'bith and aqualish twice with different values; species workstream',
    'datatables/customization/allow_bald.iff': 'for Claude: server reads it; MTG species (hutt, nautolan, togruta, aqualish); '
                                               'species workstream',
    'datatables/player/waypoint_planets.iff': 'for Claude: adds taanab, nalhutta, kashyyyk, kaas to the waypoint planet list; '
                                              'which planets exist is the owner\'s call',
    'datatables/resource/resource_tree.iff': 'for Claude: server reads it (resource classes); additive against stock but '
                                             'conflicts with the chain\'s staged copy (Ossus rows, raised type counts)',
    'misc/object_template_crc_string_table.iff': 'nothing left: the Hoth build already merges patch_14_00 + mtg_patch_022 + '
                                                 'mtg_patch_023, and no MTG copy has a name the staged table lacks',
}


def decision(name, rec, merged):
    if name in merged:
        return 'merged'
    c = rec['class']
    if c in ('same', 'same_content', 'mtg_subset'):
        return 'nothing to merge'
    if name.startswith('string/') and not name.startswith('string/en/'):
        return 'skipped: not English (the English client and the server read string/en only)'
    if name in SKIP_REASONS:
        return SKIP_REASONS[name]
    if c == 'binary':
        return 'skipped: binary'
    if c == 'different_format':
        return 'for Claude: different format'
    if c == 'mtg_changes':
        return 'for Claude: MTG edits stock rows or strings'
    return 'for Claude: not reviewed'


# ---------------------------------------------------------------- comparisons

def kind_of(name, data):
    if name.endswith('.stf'):
        return 'stf'
    if len(data) >= 12 and data[:4] == b'FORM':
        f = data[8:12]
        if f == b'DTII':
            return 'dtii'
        if f == b'CSTB':
            return 'cstb'
        return 'iff:' + f.decode('latin-1', 'replace').strip()
    return 'other'


def _norm(row):
    return tuple(('f', struct.pack('<f', c)) if isinstance(c, float) else c for c in row)


def _short(row, n=8):
    return [round(c, 4) if isinstance(c, float) else (c[:60] if isinstance(c, str) else c) for c in row[:n]]


def table_key(stock_rows, mtg_rows, ncols):
    """Fewest leading columns on which both row lists are unique, or None (a list repeats a whole row)."""
    for k in range(1, ncols + 1):
        if len({r[:k] for r in stock_rows}) == len(stock_rows) and len({r[:k] for r in mtg_rows}) == len(mtg_rows):
            return k
    return None


def compare_dtii(a, b):
    """a: base copy (stock or staged), b: MTG copy. Returns a record."""
    try:
        ta, tb = st.read_dtii(a), st.read_dtii(b)
    except Exception as e:  # noqa: BLE001
        return {'class': 'different_format', 'reason': f'does not parse: {e}'[:200]}
    rec = {'columns': len(ta['columns']), 'stock_rows': len(ta['rows']), 'mtg_rows': len(tb['rows'])}
    if ta['version'] != tb['version'] or ta['columns'] != tb['columns'] or ta['types'] != tb['types']:
        rec.update({'class': 'different_format', 'version': [ta['version'], tb['version']],
                    'columns_only_stock': [c for c in ta['columns'] if c not in tb['columns']],
                    'columns_only_mtg': [c for c in tb['columns'] if c not in ta['columns']],
                    'types_differ': [c for c, x, y in zip(ta['columns'], ta['types'], tb['types']) if x != y]
                    if ta['columns'] == tb['columns'] else None,
                    'same_columns_other_order': sorted(ta['columns']) == sorted(tb['columns']) and ta['columns'] != tb['columns']})
        return rec
    ra, rb = [_norm(r) for r in ta['rows']], [_norm(r) for r in tb['rows']]
    ncols = len(ta['columns'])
    k = table_key(ra, rb, ncols)
    rec['key_columns'] = k
    rec['key_names'] = ta['columns'][:k] if k else 'whole row (rows repeat)'
    sa, sb = collections.Counter(ra), collections.Counter(rb)
    added_full = [r for r in rb if r not in sa]
    missing_full = [r for r in ra if r not in sb]
    if k:
        ma, mb = {r[:k]: i for i, r in enumerate(ra)}, {r[:k]: i for i, r in enumerate(rb)}
        edited = [key for key in ma if key in mb and ra[ma[key]] != rb[mb[key]]]
        added = [key for key in mb if key not in ma]
        missing = [key for key in ma if key not in mb]
        rec['edited_samples'] = [{'stock': _short(ta['rows'][ma[key]]), 'mtg': _short(tb['rows'][mb[key]])} for key in edited[:SAMPLES]]
        rec['added_samples'] = [_short(tb['rows'][mb[key]]) for key in added[:SAMPLES]]
    else:
        edited = None if (added_full and missing_full) else []
        added, missing = added_full, missing_full
        rec['added_samples'] = [_short(list(tb['rows'][rb.index(r)])) for r in added[:SAMPLES]]
    rec.update({'added': len(added), 'edited': None if edited is None else len(edited), 'stock_absent_in_mtg': len(missing)})
    if not added and not missing and not edited:
        rec['class'] = 'same_content'
        rec['order_differs'] = ra != rb
    elif edited is None or edited:
        rec['class'] = 'mtg_changes'
    elif added:
        rec['class'] = 'mtg_superset'
    else:
        rec['class'] = 'mtg_subset'
    return rec


def compare_stf(a, b):
    try:
        sa, sb = st.read_stf(a), st.read_stf(b)
    except Exception as e:  # noqa: BLE001
        return {'class': 'different_format', 'reason': f'does not parse: {e}'[:200]}
    ia, ib = st.stf_items(sa), st.stf_items(sb)
    da, db = dict(ia), dict(ib)
    rec = {'stock_keys': len(da), 'mtg_keys': len(db), 'stock_duplicate_keys': len(ia) - len(da),
           'mtg_duplicate_keys': len(ib) - len(db)}
    if sa['version'] != sb['version']:
        rec.update({'class': 'different_format', 'version': [sa['version'], sb['version']]})
        return rec
    added = [k for k in db if k not in da]
    edited = [k for k in da if k in db and da[k] != db[k]]
    missing = [k for k in da if k not in db]
    rec.update({'added': len(added), 'edited': len(edited), 'stock_absent_in_mtg': len(missing),
                'added_samples': [[k, db[k][:80]] for k in added[:SAMPLES]],
                'edited_samples': [{'key': k, 'stock': da[k][:100], 'mtg': db[k][:100]} for k in edited[:SAMPLES]],
                'edited_whitespace_or_case_only': sum(1 for k in edited if da[k].strip().lower() == db[k].strip().lower())})
    rec['class'] = ('mtg_changes' if edited else 'mtg_superset' if added else 'mtg_subset' if missing else 'same_content')
    return rec


def compare_cstb(a, b):
    try:
        ca, cb = st.read_cstb(a), st.read_cstb(b)
    except Exception as e:  # noqa: BLE001
        return {'class': 'different_format', 'reason': f'does not parse: {e}'[:200]}
    na, nb = {n: c for c, n in ca['entries']}, {n: c for c, n in cb['entries']}
    crc_a = {c: n for c, n in ca['entries']}
    rec = {'stock_entries': len(na), 'mtg_entries': len(nb)}
    if ca['version'] != cb['version']:
        rec.update({'class': 'different_format', 'version': [ca['version'], cb['version']]})
        return rec
    added = [n for n in nb if n not in na]
    edited = [n for n in na if n in nb and na[n] != nb[n]]
    missing = [n for n in na if n not in nb]
    collisions = [n for n in added if nb[n] in crc_a]
    bad_crc = [n for n in added if st.soe_crc(n) != nb[n]]
    rec.update({'added': len(added), 'edited': len(edited), 'stock_absent_in_mtg': len(missing),
                'crc_collisions_with_stock': collisions[:SAMPLES], 'added_with_wrong_crc': bad_crc[:SAMPLES],
                'added_samples': added[:SAMPLES]})
    rec['class'] = ('mtg_changes' if edited or collisions else 'mtg_superset' if added else 'mtg_subset' if missing else 'same_content')
    return rec


def compare(name, a, b):
    if a == b:
        return {'class': 'same'}
    ka, kb = kind_of(name, a), kind_of(name, b)
    if ka != kb:
        return {'class': 'different_format' if {ka, kb} & {'dtii', 'stf', 'cstb'} else 'binary', 'kinds': [ka, kb]}
    if ka == 'dtii':
        return compare_dtii(a, b)
    if ka == 'stf':
        return compare_stf(a, b)
    if ka == 'cstb':
        return compare_cstb(a, b)
    return {'class': 'binary', 'kind': ka}


# ---------------------------------------------------------------- the worker

def entry(archive, name):
    return trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, archive), name)


def work(job):
    name, stock_arc, stock_size, mtg_copies, chain = job   # mtg_copies: [(archive, size)], highest priority first
    top_arc, top_size = mtg_copies[0]
    rec = {'stock': stock_arc, 'mtg': top_arc, 'mtg_copies': [a for a, _ in mtg_copies]}
    tabular = name.endswith(('.stf', '.iff'))
    if stock_size != top_size and not tabular:
        rec.update({'class': 'binary', 'sizes': [stock_size, top_size]})
        return name, rec
    a, b = entry(stock_arc, name), entry(top_arc, name)
    rec.update(compare(name, a, b))
    if rec['class'] == 'binary':
        rec['sizes'] = [len(a), len(b)]
    if rec['class'] in ('same', 'binary'):
        return name, rec
    if rec.get('added') and len(mtg_copies) > 1:   # what the lower MTG copies would add (the merge step reads them all)
        rec['lower_copies'] = {}
        for arc, _ in mtg_copies[1:]:
            c = entry(arc, name)
            sub = compare(name, a, c)
            rec['lower_copies'][arc] = {k: sub.get(k) for k in ('class', 'added', 'edited', 'stock_absent_in_mtg', 'added_samples')}
    if chain is not None:   # the chain already stages this file: the merge step would build on the staged copy
        sub = compare(name, chain, b)
        rec['vs_chain_staged'] = {k: sub.get(k) for k in ('class', 'added', 'edited', 'stock_absent_in_mtg', 'columns_only_stock',
                                                           'columns_only_mtg', 'key_columns', 'added_samples')}
    return name, rec


# ---------------------------------------------------------------- main

def main():
    trees, _, _ = clo.load_order()
    prio = {n: p for p, n in trees}
    order = [n for _, n in trees]                     # highest priority first, config order within a priority
    stock = [n for n in order if not n.lower().startswith('mtg_')]
    mtg = [n for n in order if n.lower().startswith('mtg_')]
    idx = trn_iff.client_index()
    s_files, m_files = collections.defaultdict(list), collections.defaultdict(list)
    for n in stock:
        for e, v in trn_iff.list_tre(os.path.join(trn_iff.CLIENT, n)).items():
            s_files[e].append((n, v[1]))
    for n in mtg:
        for e, v in trn_iff.list_tre(os.path.join(trn_iff.CLIENT, n)).items():
            m_files[e].append((n, v[1]))
    chain_names = set(trn_iff.list_tre(CHAIN_TRE))
    both = sorted(set(s_files) & set(m_files))
    jobs, tie_rule = [], []
    for name in both:
        win = idx[name]
        assert not win.lower().startswith('mtg_'), name
        size = dict(s_files[name])[win]
        server_first = s_files[name][0][0]   # Core3 keeps the first archive in TreFiles that has the file
        if server_first != win:
            tie_rule.append((name, win, server_first))
        chain = trn_iff.open_tre_entry(CHAIN_TRE, name) if name in chain_names else None
        jobs.append((name, win, size, m_files[name], chain))
    print(f'{len(stock)} stock and {len(mtg)} MTG archives; {len(s_files)} stock files, {len(m_files)} MTG files, '
          f'{len(both)} in both', flush=True)
    files = {}
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 1)) as pool:
        for i, (name, rec) in enumerate(pool.map(work, jobs, chunksize=200)):
            files[name] = rec
            if i % 10000 == 0:
                print(f'  {i}/{len(jobs)}', flush=True)
    # same-priority stock archives: client_index lets the later one win, Core3 the earlier one; show where it matters
    ties = []
    for name, cwin, swin in tie_rule:
        same = entry(cwin, name) == entry(swin, name)
        if not same:
            ties.append({'file': name, 'client_index_winner': cwin, 'server_winner': swin, 'class': files[name]['class']})
    sys.path.insert(0, HERE)
    import stage_mtg_merges as smm  # noqa: E402  (what the merge step takes)
    merged = set(smm.merged_files())
    for name, rec in files.items():
        rec['topic'] = topic(name)
        rec['server_reads'] = server_reads(name)
        rec['chain_stages_it'] = name in chain_names
        rec['decision'] = decision(name, rec, merged)
    counts = collections.Counter(r['class'] for r in files.values())
    decisions = collections.Counter(r['decision'] for r in files.values())
    by_kind = collections.defaultdict(collections.Counter)
    for name, r in files.items():
        by_kind[r['class']][os.path.splitext(name)[1] or '(none)'] += 1
    mtg_only = sorted(set(m_files) - set(s_files))
    out = {
        'built': '2026-10-15', 'tool': 'MTG-merges/shadow_audit.py',
        'stock_archives': stock, 'mtg_archives_priority_order': mtg,
        'client_priorities': {n: prio[n] for n in order},
        'stock_files': len(s_files), 'mtg_files': len(m_files), 'in_both': len(both), 'mtg_only': len(mtg_only),
        'stock_only': len(set(s_files) - set(m_files)),
        'counts': dict(counts.most_common()),
        'counts_by_extension': {c: dict(v.most_common()) for c, v in by_kind.items()},
        'decisions': dict(decisions.most_common()),
        'merge_step': {'MTG_COPIES': smm.MTG_COPIES, 'TABLES': smm.TABLES, 'STRINGS': smm.STRINGS, 'CRC_TABLES': smm.CRC_TABLES},
        'server_reads_not_same': {n: files[n]['server_reads'] for n in both
                                  if files[n]['class'] != 'same' and files[n]['server_reads'] and not n.startswith('string/')},
        'same_priority_winner_differs': ties,
        'files': {n: files[n] for n in both if files[n]['class'] != 'same'},
        'same_files': [n for n in both if files[n]['class'] == 'same'],
    }
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=None, separators=(',', ':'), default=list)
    print(json.dumps(out['counts'], indent=1))
    print(json.dumps(out['decisions'], indent=1))
    print(f'same-priority winner differs in content for {len(ties)} files; wrote {OUT_JSON} '
          f'({os.path.getsize(OUT_JSON) / 1e6:.1f} MB, sha256 {hashlib.sha256(open(OUT_JSON, "rb").read()).hexdigest()[:12]})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
