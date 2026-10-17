"""Can every item be obtained, and the way it was meant to be? Read-only source map of the Core3 dev tree, compared
with stock SWGEmu (Claude, 17 Oct 2026; owner: "make sure that all the items in the game are obtainable in the way
they were intended". The local model judges the suspects first (local_jobs.py item-check), then Claude checks them).

Inside Debian, as root (reads /opt/swg/Core3-dev and its git history; writes only the outputs below and the stock
copy in /var/tmp/core3-stock):
    python3 -I /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/core3_audit/item_sources.py

For every server item template under object/tangible and object/weapon (world-only folders left out) it lists how a
player gets it (hair styles are not items and are left out):
  drop      a loot item for it is in a loot group that a spawned creature carries (lootGroups, nested groups too)
  scripted  the same, but the group is named by a script or the server code (createLoot, missions, forage, fishing)
  craft     a draft schematic makes it and a skill grants the schematic (skills.iff SCHEMATICS_GRANTED through
            schematic_group.iff), or a loot schematic that drops grants it, or a script names the schematic
  script    a screenplay or manager names the template (quest rewards, recruiters, terminals); world placements
            (spawnSceneObject), inventory checks and hand-in lists (the crafting contractor) don't count
  code      the server code names the template, or a path prefix the code finishes at run time (vendor types, DNA)
  space     a loot group that a space ship carries (lootTable in ship_mobile; open only if the space zones are)
  start     a character creation starting kit (the client's creation/ files)
  test      only the character builder, staff commands, the sandbox test datapads or the bot tools give it
Dead ends are kept apart: a drop only from creatures that nothing spawns, a schematic that nothing grants.
"Spawned" is static: the creature's name appears in a lair template that a spawn list, screenplay or the code names,
or directly in one of those. Static reading only: a source here means there is a path, not that it was tested.

The same map is built for stock SWGEmu (origin/unstable at the commit our history starts from), so each item also
shows which ways of getting it we added or lost. Skill grants come from the client tables (ours included) for both.

Outputs: outputs/tools/core3_audit/item_sources.json and outputs/Documentation-support/item-sources-audit.md.
"""
import collections, glob, json, os, re, subprocess, sys

DEV = '/opt/swg/Core3-dev/MMOCoreORB'
STOCK_REV = '403893d9'   # origin/unstable: the last upstream commit before ours (4357970d, 96f2ed94)
STOCK = '/var/tmp/core3-stock'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, 'item_sources.json')
OUT_MD = os.path.join(HERE, '..', '..', 'Documentation-support', 'item-sources-audit.md')
sys.path.insert(0, os.path.join(HERE, '..', 'owner_content'))

# Folders of world objects, not things a player carries.
NOT_ITEMS = {'bank', 'base', 'camp', 'datapad', 'destructible', 'gravestone', 'hopper', 'hq_destructible', 'inventory',
             'lair', 'loadbeacon', 'location', 'mission', 'planet_map_location', 'poi', 'region', 'shipcontrol', 'sign',
             'spawning', 'terminal', 'test', 'transport', 'ui', 'weather_object', 'creature'}
TEST = re.compile(r'terminal_character_builder|/staff/|screenplays/tests/|sandbox_creatures|sandbox_tools_datapad|'
                  r'Agent[A-Z]|agentgear|BotPop|botpop|CharacterBuilder|/client/')
NOT_A_SOURCE = re.compile(r'spawnSceneObject|spawnChildSceneObject|getContainerObjectByTemplate|hasItemInInventory|'
                          r'hasGeoItem|removeGeoItem|canTurnInDatapad|getTemplate\w*\(\)\s*==|destroyObject')
# Lists of what a player hands in or how a part looks, not ways to get an item.
NOT_SOURCE_FILES = re.compile(r'crafting_contractor|visible_components|village_community_crafting')
QUOTED = re.compile(r'"([A-Za-z0-9_]+)"')
ITEM_LIT = re.compile(r'"(object/(?:tangible|weapon)/[^"]+?\.iff)"')
SCHEM_LIT = re.compile(r'"(object/draft_schematic/[^"]+?\.iff)"')
PREFIX_LIT = re.compile(r'"(object/(?:tangible|weapon)/[^"]*/[^"/]+(?<!\.iff))"')
PLAYER_KINDS = ('drop', 'scripted', 'space', 'craft', 'script', 'code', 'start')


def read(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def luas(root, sub):
    return glob.glob(f'{root}/bin/scripts/{sub}/**/*.lua', recursive=True)


def stock_tree():
    if not os.path.isdir(f'{STOCK}/MMOCoreORB/bin/scripts'):
        os.makedirs(STOCK, exist_ok=True)
        archive = subprocess.Popen(['git', '-c', 'safe.directory=*', '-C', os.path.dirname(DEV), 'archive', STOCK_REV,
                                    'MMOCoreORB/bin/scripts', 'MMOCoreORB/src'], stdout=subprocess.PIPE)
        subprocess.run(['tar', '-x', '-C', STOCK], stdin=archive.stdout, check=True)
        archive.wait()
    return f'{STOCK}/MMOCoreORB'


def grants():
    """draft schematic -> skills that grant it, from the client's tables (ours included)."""
    import swg_client_data as c
    groups = collections.defaultdict(set)
    for r in c.datatable(c.client_file('datatables/crafting/schematic_group.iff')):
        groups[r['GroupId']].add(r['SchematicName'])
    out = collections.defaultdict(set)
    for r in c.datatable(c.client_file('datatables/skill/skills.iff')):
        god = str(r.get('GOD_ONLY')).lower() in ('1', 'true')
        for g in str(r.get('SCHEMATICS_GRANTED') or '').split(','):
            for s in groups.get(g.strip(), ()):
                out[s].add(('test:' if god else '') + r['NAME'])
    return out


def creation_items():
    """template -> starting kits, from the client's creation/ files (PlayerCreationManager gives these items)."""
    import swg_client_data as c
    c.client_file('creation/')   # builds the index
    out = collections.defaultdict(set)
    for name in [n for n in c._index if n.startswith('creation/')]:
        for t in re.findall(rb'object/(?:tangible|weapon)/[^\x00"]+?\.iff', c.client_file(name) or b''):
            out[t.decode('latin-1').replace('/shared_', '/')].add(os.path.basename(name))
    return out


def definitions(root):
    S = f'{root}/bin/scripts'
    d = {'loot': {}, 'groups': {}, 'mobiles': {}, 'lairs': {}, 'schematics': {}, 'loot_schematics': {}, 'items': {},
         'objects': set(), 'ships': {}, 'custom': set()}
    for f in luas(root, 'ship_mobile'):
        t = read(f)
        lt = re.search(r'lootTable\s*=\s*"([^"]+)"', t)
        if lt:
            d['ships'][os.path.basename(f)[:-4]] = lt[1]
    for f in luas(root, 'loot/items'):
        t = read(f)
        n, o = re.search(r'addLootItemTemplate\("([^"]+)"', t), re.search(r'directObjectTemplate\s*=\s*"([^"]+)"', t)
        if n and o:
            d['loot'][n[1]] = o[1]
    for f in luas(root, 'loot/groups'):
        t = read(f)
        n = re.search(r'addLootGroupTemplate\("([^"]+)"', t)
        if n:
            # LootManager looks a name up as a group first, then as an item, whichever key the entry uses
            d['groups'][n[1]] = set(re.findall(r'(?:itemTemplate|groupTemplate)\s*=\s*"([^"]+)"', t))
    for f in luas(root, 'mobile'):
        rel = os.path.relpath(f, S)
        if rel.startswith('mobile/spawn/'):
            continue
        t = read(f)
        if rel.startswith('mobile/lair/'):
            n = re.search(r'addLairTemplate\("([^"]+)"', t)
            if n:
                d['lairs'][n[1]] = set(re.findall(r'\{\s*"([A-Za-z0-9_]+)"\s*,', t))
            continue
        n = re.search(r'addCreatureTemplate\(\s*[A-Za-z0-9_]+\s*,\s*"([^"]+)"', t)
        if n:
            lv = re.search(r'\blevel\s*=\s*(\d+)', t)
            d['mobiles'][n[1]] = (int(lv[1]) if lv else 0, set(re.findall(r'\{\s*group\s*=\s*"([^"]+)"', t)))
    # The server knows each object by the path in its ObjectTemplates:addTemplate line, not by its file path: the
    # 14,000 files under object/custom_content register object/tangible/... paths (the Hoth session, 17 Oct).
    for f in luas(root, 'object'):
        rel = os.path.relpath(f, S)
        if os.path.basename(f) in ('serverobjects.lua', 'objects.lua'):
            continue
        t = read(f)
        custom = rel.startswith('object/custom_content/')
        for path in re.findall(r'ObjectTemplates:addTemplate\(\s*[A-Za-z0-9_]+\s*,\s*"([^"]+)"', t) or [rel[:-4] + '.iff']:
            d['objects'].add(path)
            parts = path.split('/')
            if path.startswith('object/draft_schematic/'):
                tt = re.search(r'targetTemplate\s*=\s*"([^"]+)"', t)
                extra = re.search(r'additionalTemplates\s*=\s*\{([^}]*)\}', t)   # variants the schematic can also make
                if tt:
                    d['schematics'][path] = [x.replace('/shared_', '/') for x in
                                             [tt[1]] + (re.findall(r'"([^"]+\.iff)"', extra[1]) if extra else [])]
            elif parts[1] in ('tangible', 'weapon') and len(parts) > 3 and parts[2] not in NOT_ITEMS | {'hair'}:
                if custom and path in d['items']:
                    continue   # a stock file and a custom copy: keep the stock one
                d['items'][path] = '/'.join(parts[1:3])
                (d['custom'].add if custom else d['custom'].discard)(path)
                if path.startswith('object/tangible/loot/loot_schematic/'):
                    ts = re.search(r'targetDraftSchematic\s*=\s*"([^"]+)"', t)
                    if ts:
                        d['loot_schematics'][path] = ts[1]
    return d


def references(root):
    """Names and templates that scripts and the server code mention, outside the definitions themselves."""
    refs = {'names': set(), 'test_names': set(), 'items': collections.defaultdict(set),
            'schematics': collections.defaultdict(set), 'prefixes': collections.defaultdict(set)}
    files = [f for sub in ('screenplays', 'managers', 'custom_scripts', 'staff', 'utils', 'mobile/spawn')
             for f in luas(root, sub)]
    files.append(f'{root}/bin/scripts/object/tangible/terminal/terminal_character_builder.lua')
    files += [os.path.join(dp, n) for dp, _, ns in os.walk(f'{root}/src') for n in ns if n.endswith(('.cpp', '.h', '.idl'))]
    for f in files:
        if not os.path.exists(f):
            continue
        rel = os.path.relpath(f, root)
        test = bool(TEST.search(rel))
        kind = 'test' if test else ('code' if rel.startswith('src/') else 'script')
        label = rel.replace('bin/scripts/', '').replace('src/server/zone/', '')
        for line in read(f).split('\n'):
            if '"' not in line:
                continue
            (refs['test_names'] if test else refs['names']).update(QUOTED.findall(line))
            if NOT_A_SOURCE.search(line) or NOT_SOURCE_FILES.search(rel):
                continue
            for t in ITEM_LIT.findall(line):
                refs['items'][t.replace('/shared_', '/')].add(f'{kind}:{label}')
            for s in SCHEM_LIT.findall(line):
                refs['schematics'][s.replace('/shared_', '/')].add(f'{kind}:{label}')
            for p in PREFIX_LIT.findall(line):   # a path the code finishes at run time (vendor types, DNA, armour sets)
                refs['prefixes'][p].add(f'{kind}:{label}')
    return refs


def source_map(root, granted, starting):
    d, r = definitions(root), references(root)
    names = r['names']
    lairs_used = {l for l in d['lairs'] if l in names}
    spawned = {m for m in d['mobiles'] if m in names} | {m for l in lairs_used for m in d['lairs'][l]}
    # group -> kind -> creature names (or the group's own name for a scripted group)
    reach = collections.defaultdict(lambda: collections.defaultdict(set))
    for m, (lv, gs) in d['mobiles'].items():
        for g in gs:
            reach[g]['drop' if m in spawned else 'unspawned'].add(f'{m} {lv}')
    for ship, g in d['ships'].items():
        reach[g]['space'].add(f'{ship} 0')
    for g in d['groups']:
        if g in names:
            reach[g]['scripted'].add(g)
        elif g in r['test_names']:
            reach[g]['test'].add(f'group {g}')
    changed = True
    while changed:   # a nested group inherits its parents' ways
        changed = False
        for g, entries in d['groups'].items():
            for s in entries & d['groups'].keys():
                for kind, labels in list(reach[g].items()):
                    before = len(reach[s][kind])
                    reach[s][kind] |= labels
                    changed |= len(reach[s][kind]) != before
    src = collections.defaultdict(lambda: collections.defaultdict(set))
    in_group = collections.defaultdict(set)
    for g, entries in d['groups'].items():
        for i in entries - d['groups'].keys():
            in_group[i].add(g)
    for name, tpl in d['loot'].items():
        if not in_group[name]:
            src[tpl]['orphan'].add(f'loot item {name} is in no group')
        for g in in_group[name]:
            for kind, labels in reach[g].items():
                src[tpl][kind] |= labels
            if not reach[g]:
                src[tpl]['orphan'].add(f'group {g} is used by nothing')
    for tpl, labels in r['items'].items():
        for lab in labels:
            src[tpl][lab.split(':')[0]].add(lab.split(':', 1)[1])
    for tpl in d['items']:
        for p, labels in r['prefixes'].items():
            if tpl.startswith(p):
                for lab in labels:
                    src[tpl][lab.split(':')[0]].add(f'built from "{p}" in {lab.split(":", 1)[1]}')
        for kit in starting.get(tpl, ()):
            src[tpl]['start'].add(kit)
    by_target = collections.defaultdict(set)
    for ls, schem in d['loot_schematics'].items():
        by_target[schem].add(ls)
    for schem, targets in d['schematics'].items():
        ways = set()
        tests = set()
        for skill in granted.get(schem, ()):
            (tests if skill.startswith('test:') else ways).add(f'skill {skill.removeprefix("test:")}')
        for ls in by_target[schem]:
            if any(k in src[ls] for k in ('drop', 'scripted', 'space', 'script', 'code')):
                ways.add(f'loot schematic {os.path.basename(ls)}')
        for lab in r['schematics'].get(schem, ()):
            (tests if lab.startswith('test:') else ways).add(f'schematic named in {lab.split(":", 1)[1]}')
        for tpl in targets:
            src[tpl]['test'] |= tests
            if ways:
                src[tpl]['craft'] |= ways
            else:
                src[tpl]['ungranted'].add(os.path.basename(schem))
    errors = {
        'loot item -> missing object': sorted(f'{n} -> {t}' for n, t in d['loot'].items() if t not in d['objects']),
        'group -> missing entry': sorted(f'{g} -> {i}' for g, es in d['groups'].items() for i in es
                                         if i not in d['loot'] and i not in d['groups']),
        'creature -> missing group': sorted(f'{m} -> {g}' for m, (_, gs) in d['mobiles'].items() for g in gs if g not in d['groups']),
        'schematic -> missing object': sorted(f'{s} -> {t}' for s, ts in d['schematics'].items() for t in ts if t not in d['objects']),
        'lair -> missing creature': sorted(f'{l} -> {m}' for l, ms in d['lairs'].items() for m in ms if m not in d['mobiles']),
    }
    return d['items'], src, errors, d['custom']


def summary(kinds):
    """One line per kind: counts, level range and a few examples."""
    out = {}
    for kind, labels in sorted(kinds.items()):
        labels = sorted(labels)
        if kind in ('drop', 'unspawned', 'space'):
            levels = [int(x.rsplit(' ', 1)[1]) for x in labels if x.rsplit(' ', 1)[-1].isdigit()]
            span = f', level {min(levels)}-{max(levels)}' if levels else ''
            out[kind] = f'{len(labels)} creatures{span}: ' + ', '.join(x.rsplit(" ", 1)[0] for x in labels[:4])
        else:
            out[kind] = f'{len(labels)}: ' + '; '.join(labels[:4])
    return out


def main():
    granted, starting = grants(), creation_items()
    dev_items, dev_src, dev_err, custom = source_map(DEV, granted, starting)
    stock_items, stock_src, stock_err, _ = source_map(stock_tree(), granted, starting)
    items, counts = {}, collections.Counter()
    for tpl, folder in sorted(dev_items.items()):
        dev, stock = dev_src.get(tpl, {}), stock_src.get(tpl, {})
        have = {k for k in PLAYER_KINDS if dev.get(k)}
        had = {k for k in PLAYER_KINDS if stock.get(k)}
        flags = []
        if tpl not in stock_items:
            flags.append('new')
        if not have:
            # an imported template (object/custom_content) that nothing uses is not an item the game offers
            flags.append('test-only' if dev.get('test') else 'imported-unused' if tpl in custom else 'no-source')
        flags += [f'lost-{k}' for k in sorted(had - have)] + [f'gained-{k}' for k in sorted(have - had) if tpl in stock_items]
        counts.update(flags or ['ok'])
        items[tpl] = {'folder': folder, 'custom': tpl in custom, 'flags': flags, 'dev': summary(dev), 'stock': summary(stock) if tpl in stock_items else {}}
    dev_rev = subprocess.run(['git', '-c', 'safe.directory=*', '-C', os.path.dirname(DEV), 'rev-parse', '--short=8', 'HEAD'],
                             capture_output=True, text=True).stdout.strip()
    with open(OUT_JSON, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'dev': dev_rev, 'stock': STOCK_REV, 'counts': counts, 'errors': dev_err,
                   'stock_errors': {k: len(v) for k, v in stock_err.items()}, 'items': items}, f, indent=0)
    folders = collections.defaultdict(collections.Counter)
    for tpl, it in items.items():
        folders[it['folder']].update(it['flags'] or ['ok'])
    md = [f'# Item sources: can every item be obtained? (dev {dev_rev} against stock {STOCK_REV})\n',
          'Written by `tools/core3_audit/item_sources.py` (static reading; see its header for what each way means). '
          'The full map is `tools/core3_audit/item_sources.json`. The local model sorts the flagged items first '
          '(`local_jobs.py item-check`); Claude checks its draft.\n',
          f'{len(items)} item templates. ' + ', '.join(f'{k}: {v}' for k, v in counts.most_common()) + '.\n',
          '## Broken references in the dev tree (stock count in brackets)\n']
    for k, v in dev_err.items():
        md.append(f'- {k}: {len(v)} ({stock_err[k] if isinstance(stock_err[k], int) else len(stock_err[k])})'
                  + (': ' + '; '.join(v[:6]) + (' ...' if len(v) > 6 else '') if v else ''))
    md.append('\n## Flags by folder\n\nImported-unused: templates under object/custom_content that nothing gives out; the local '
              'check leaves them out.\n\n| Folder | Items | ok | no-source | test-only | imported-unused | new | lost | gained |\n'
              '|---|---|---|---|---|---|---|---|---|')
    for folder, c in sorted(folders.items(), key=lambda kv: -sum(kv[1].values())):
        lost = sum(v for k, v in c.items() if k.startswith('lost-'))
        gained = sum(v for k, v in c.items() if k.startswith('gained-'))
        md.append(f'| {folder} | {sum(1 for it in items.values() if it["folder"] == folder)} | {c["ok"]} | {c["no-source"]} | '
                  f'{c["test-only"]} | {c["imported-unused"]} | {c["new"]} | {lost} | {gained} |')
    lost = [t for t, it in items.items() if any(f.startswith('lost-') for f in it['flags'])]
    md.append(f'\n## Items that lost a way of getting them against stock ({len(lost)})\n')
    md += [f'- `{t}`: {", ".join(f for f in items[t]["flags"] if f.startswith("lost-"))}' for t in lost[:80]]
    if len(lost) > 80:
        md.append(f'- ... and {len(lost) - 80} more (item_sources.json)')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')
    print(f'{len(items)} items; ' + ', '.join(f'{k} {v}' for k, v in counts.most_common()))
    print('dev errors: ' + ', '.join(f'{k} {len(v)}' for k, v in dev_err.items()))


if __name__ == '__main__':
    main()
