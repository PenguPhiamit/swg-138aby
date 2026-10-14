"""Tier the truly dormant client objects (client shared template, no server template registered anywhere in
Core3-dev, custom_content included) and record what each one needs. Read-only everywhere except work/.

Inputs (all produced earlier in this folder, or by the catalogue tools):
  ../Content-catalogue/dormant-client-objects.json   the 13,627 listed objects
  work/core3_server_templates.tsv / core3_client_templates.tsv   every addTemplate/addClientTemplate path in Core3-dev
  work/bellum_index.json                             Bellum Gero registrations by path
  work/disc_index.json                               owner's SOE disc archives by file name
  work/crc_table_winner.txt                          the CRC string table the client loads (patch_14_00.tre)
  ../tools/hoth/data/hoth_loot_inventory.json        Claude's Hoth loot set (excluded from batches)

Run: python -I tools/dormant_analysis.py   ->  work/dormant_analysis.json, work/dormant_listing.txt
"""
import collections, json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, HERE)
import swg_iff  # noqa: E402
from swg_iff import scd  # noqa: E402
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
import client_load_order as clo  # noqa: E402

W = os.path.join(ROOT, 'work')


def load_tsv(name):
    out = {}
    with open(os.path.join(W, name), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) == 2:
                out.setdefault(parts[1], []).append(parts[0])
    return out


def crc_table(data):
    chunks = {}
    (_, kind, a, b), = list(scd.iff_chunks(data))[:1]
    (_, ver, a, b) = next(scd.iff_chunks(data, a, b))
    for tag, _, s, e in scd.iff_chunks(data, a, b):
        chunks[tag] = (s, e)
    n = struct.unpack_from('<I', data, chunks['DATA'][0])[0]
    crcs = struct.unpack_from('<%dI' % n, data, chunks['CRCT'][0])
    offs = struct.unpack_from('<%dI' % n, data, chunks['STRT'][0])
    s = chunks['STNG'][0]
    return {data[s + o:data.index(b'\0', s + o)].decode('latin-1'): c for o, c in zip(offs, crcs)}


def read_from(archive, name):
    p = os.path.join(clo.CLIENT, archive)
    for e in clo.read_tre(p):
        if e['name'].lower() == name:
            with open(p, 'rb') as f:
                f.seek(e['offset'])
                blob = f.read(e['comp_size'] if e['comp'] else e['size'])
            return clo._inflate(blob, e['comp'], e['size'])


def server_of(shared):
    h, t = shared.rsplit('/', 1)
    return h + '/' + t[len('shared_'):]


# ---- tier rules -------------------------------------------------------------------------------------------
# Each rule: (regex on the shared path, tier, reason, pre-CU note). First match wins. Checked after the
# form-type rules in tier_of().
RULES = [
    (r'/test/|shared_test_|_test\.iff|/temp_|shared_temp', 'D', 'test or temporary object', ''),
    (r'^object/ship/|^object/tangible/ship/|^object/intangible/ship/|^object/draft_schematic/space/|/space_mining/|/shipcontrol/',
     'D', 'space (JTL) object; space is deferred', 'JTL'),
    (r'^object/tangible/cybernetic/', 'C', 'cybernetics are an NGE system Core3 lacks', 'NGE'),
    (r'^object/mobile/hologram/', 'C', 'hologram NPC (NGE storyteller/heroic holograms)', 'NGE'),
    (r'^object/mobile/beast_master/|/beast/', 'C', 'beast master system (NGE)', 'NGE'),
    (r'^object/mobile/skeleton/', 'D', 'skeleton mobiles are client animation rigs, not spawnable NPCs', ''),
    (r'^object/mobile/vendor/', 'B', 'vendor NPC body for a new species: needs the species in Races/vendor lists', 'species'),
    (r'^object/creature/player/', 'B', 'playable species: needs Races.h, character creation and appearance work (owner: no hybrids until all regular species are in)', 'species'),
    (r'^object/player_quest/', 'C', 'NGE player quest (journal) object', 'NGE'),
    (r'^object/tangible/loot/collectible/|/collection/', 'C', 'collections UI (NGE)', 'NGE'),
    (r'^object/tangible/loot/loot_schematic/', 'B', 'loot schematic: needs the draft schematic it grants and the crafted object', 'crafting'),
    (r'^object/tangible/loot/npc_loot/', 'A', 'junk/NPC loot item: server template only, then a loot-group entry', ''),
    (r'^object/tangible/loot/creature_loot/', 'A', 'creature loot item: server template only, then a loot-group entry', ''),
    (r'^object/tangible/loot/.*(painting|statue|rug|plant|trophy|hologram|diorama|banner|poster|chair|table|lamp|bed|couch|cabinet|shelf|desk)',
     'A', 'decor loot item: server template only', ''),
    (r'^object/tangible/loot/', 'A', 'loot item: server template only, then a loot-group entry', ''),
    (r'^object/draft_schematic/armor/', 'B', 'armor schematic: needs the crafted armor object, its stats and a profession hook', 'crafting'),
    (r'^object/draft_schematic/weapon/', 'B', 'weapon schematic: needs the crafted weapon, stats and a profession hook', 'crafting'),
    (r'^object/draft_schematic/bio_engineer/', 'B', 'bio-engineer schematic: needs the bio component object and profession hook', 'crafting'),
    (r'^object/draft_schematic/', 'B', 'draft schematic: needs the crafted object and a profession hook', 'crafting'),
    (r'^object/tangible/wearables/', 'A', 'wearable: server template only (check per-species meshes in the client .sat)', 'wearable'),
    (r'^object/tangible/component/', 'B', 'crafting component: needs the schematic that makes it and the one that uses it', 'crafting'),
    (r'^object/weapon/', 'B', 'weapon: needs damage/speed stats and a source (schematic or loot)', 'stats'),
    (r'^object/tangible/medicine/', 'B', 'medicine: needs effect values and a schematic/loot source', 'stats'),
    (r'^object/tangible/food/', 'B', 'food: needs effect values and a schematic/loot source', 'stats'),
    (r'^object/building/player/', 'B', 'player structure: needs the deed, the building template and the client portal layout', 'housing'),
    (r'^object/building/|^object/static/structure/|^object/installation/', 'B', 'building/installation: placed by snapshot or deed; needs the world work that uses it', 'world'),
    (r'^object/tangible/deed/', 'B', 'deed: needs the object chain it creates', 'chain'),
    (r'^object/tangible/terminal/', 'C', 'terminal: needs the game system it fronts', ''),
    (r'^object/tangible/inventory/|^object/tangible/base/|^object/weapon/base/', 'D', 'base/inventory container variant', ''),
    (r'^object/tangible/dungeon/', 'C', 'dungeon prop: part of an instance that is not ported', ''),
    (r'^object/tangible/theme_park/|^object/tangible/location/|^object/tangible/ground_spawning/|^object/tangible/travel/',
     'C', 'quest/system prop with no owning system ported', ''),
    (r'^object/resource_container/', 'A', 'resource container variant: server template only (check the resource type exists pre-CU)', 'resources'),
    (r'^object/tangible/furniture/', 'A', 'decor: server template only', ''),
    (r'^object/tangible/item/', 'A', 'item: server template only', ''),
    (r'^object/static/', 'A', 'static prop: server template only; usable by world building', ''),
]


def tier_of(path, info):
    form = info['form'] if info else None
    for rx, tier, reason, note in RULES:
        if re.search(rx, path):
            return tier, reason, note
    if form in ('STOT', 'SSOT'):
        return 'A', 'tangible/static object: server template only', ''
    return 'D', 'unsorted', ''


def main():
    listed = json.load(open(os.path.join(OUTPUTS, 'Content-catalogue', 'dormant-client-objects.json'), encoding='utf-8'))
    server = load_tsv('core3_server_templates.tsv')
    client = load_tsv('core3_client_templates.tsv')
    bellum = json.load(open(os.path.join(W, 'bellum_index.json'), encoding='utf-8'))
    disc = json.load(open(os.path.join(W, 'disc_index.json'), encoding='utf-8'))['files']
    stock = set(l.strip() for l in open(os.path.join(W, 'crc_table_winner.txt'), encoding='utf-8'))
    mtg_tables = {}
    for a in ('mtg_patch_023.tre', 'mtg_patch_022.tre', 'mtg_patch_021.tre', 'mtg_patch_019.tre'):
        mtg_tables[a] = crc_table(read_from(a, 'misc/object_template_crc_string_table.iff'))
    hoth = json.load(open(os.path.join(OUTPUTS, 'tools', 'hoth', 'data', 'hoth_loot_inventory.json'), encoding='utf-8'))
    hoth_templates = set(hoth['templates'])

    scd._build_index()
    rows = []
    for o in listed['objects']:
        shared = o['object']
        srv = server_of(shared)
        if srv in server:
            continue  # already registered in Core3-dev (any folder)
        info = swg_iff.resolved(shared)
        win = scd._index.get(shared.lower())
        tier, reason, note = tier_of(shared, info)
        in_hoth = srv in hoth_templates
        rows.append({
            'shared': shared, 'server': srv, 'origin': o['origin'], 'archives': o['archives'],
            'winning_archive': os.path.basename(win[0]) if win else None,
            'form': info['form'] if info else None,
            'template_class': swg_iff.TYPE_NAMES.get(info['form']) if info else None,
            'base': info['chain'][1] if info and len(info['chain']) > 1 else None,
            'gameObjectType': info['gameObjectType'] if info else None,
            'objectName': info['objectName'] if info else None,
            'appearance': info['appearanceFilename'] if info else None,
            'clientDataFile': info['clientDataFile'] if info else None,
            'core3_client_template': client.get(shared, []),
            'bellum_server': [b['file'] for b in bellum['server'].get(srv, [])],
            'bellum_client': [b['file'] for b in bellum['client'].get(shared, [])],
            'disc_archives': disc.get(shared.lower(), []),
            'in_stock_crc_table': shared in stock,
            'in_mtg_crc_tables': [a for a, t in mtg_tables.items() if shared in t],
            'hoth_loot_set': in_hoth,
            'tier': tier, 'reason': reason, 'precu_note': note,
        })
    rows.sort(key=lambda r: (r['tier'], r['shared']))
    with open(os.path.join(W, 'dormant_analysis.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rows, f, indent=1)

    def cat(p):
        parts = p.split('/')
        return '/'.join(parts[:3]) if len(parts) > 3 else '/'.join(parts[:2])

    lines = [f'truly dormant: {len(rows)} (listed {len(listed["objects"])}, already registered {len(listed["objects"]) - len(rows)})', '']
    for tier in 'ABCD':
        sub = [r for r in rows if r['tier'] == tier]
        lines.append(f'== tier {tier}: {len(sub)}')
        for c, n in sorted(collections.Counter(cat(r['shared']) for r in sub).items(), key=lambda kv: -kv[1]):
            lines.append(f'   {n:5d} {c}')
        lines.append('')
    lines.append('== per object (tier | form | gameObjectType | base | objectName | disc | mtg tables | bellum | hoth | path)')
    for r in rows:
        on = f'{r["objectName"][0]}:{r["objectName"][1]}' if r['objectName'] else '-'
        lines.append(f'{r["tier"]} {r["form"] or "?":4s} {hex(r["gameObjectType"]) if r["gameObjectType"] is not None else "-":7s} '
                     f'{(r["base"] or "-").split("/")[-1]:40s} {on:60s} disc={len(r["disc_archives"])} '
                     f'mtg={len(r["in_mtg_crc_tables"])} bellum={"y" if r["bellum_server"] else "-"} '
                     f'{"HOTH " if r["hoth_loot_set"] else ""}{r["shared"]}')
    with open(os.path.join(W, 'dormant_listing.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:60]))
    print('->', os.path.join(W, 'dormant_analysis.json'))


if __name__ == '__main__':
    main()
